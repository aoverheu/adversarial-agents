"""
Shared utilities used across all adversarial agent steps.

Consolidates duplicated code: LLM calls, JSON parsing, HTTP probing,
severity formatting, session IDs, and report generation.
"""

import anthropic
import httpx
import json
import uuid
from enum import Enum


# =============================================================================
# Severity — single source of truth
# =============================================================================

class Severity(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


SEVERITY_ORDER = {s: i for i, s in enumerate(Severity)}

SEVERITY_ICONS = {
    "none": "[ ]",
    "low": "[!]",
    "medium": "[!!]",
    "high": "[!!!]",
    "critical": "[CRITICAL]",
}


def severity_icon(severity) -> str:
    """Get the display icon for a severity level (accepts str or Severity enum)."""
    key = severity.value if isinstance(severity, Severity) else severity
    return SEVERITY_ICONS.get(key, "[?]")


def max_severity(a: Severity, b: Severity) -> Severity:
    """Return the higher of two severity levels."""
    return a if SEVERITY_ORDER[a] >= SEVERITY_ORDER[b] else b


# =============================================================================
# LLM utilities
# =============================================================================

def call_llm(client: anthropic.Anthropic, model: str, system: str,
             user_message: str, max_tokens: int = 1024) -> str:
    """Make a single-turn LLM call and return the text response."""
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


def parse_json(text: str, fallback: dict = None) -> dict:
    """
    Extract JSON from LLM response, handling various formats.

    Tries in order:
    1. Direct parse (clean JSON)
    2. Strip markdown code fences, then parse
    3. Find first {...} block in text, then parse
    4. Return fallback dict if all else fails
    """
    if fallback is None:
        fallback = {"error": "Could not parse JSON from LLM response"}

    cleaned = text.strip()

    # Try direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Strip markdown code fences
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        fenced = "\n".join(lines[1:])
        # Remove closing fence
        if "```" in fenced:
            fenced = fenced[:fenced.rfind("```")]
        try:
            return json.loads(fenced.strip())
        except json.JSONDecodeError:
            pass

    # Find JSON object within text
    start = cleaned.find("{")
    end = cleaned.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(cleaned[start:end])
        except json.JSONDecodeError:
            pass

    return fallback


# =============================================================================
# HTTP utilities
# =============================================================================

def send_to_target(http_client: httpx.Client, target_url: str,
                   message: str, session_id: str) -> str:
    """Send a message to the target chatbot API and return the response text."""
    try:
        response = http_client.post(
            f"{target_url}/api/chat",
            json={"message": message, "session_id": session_id},
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "[No response field in API response]")
    except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.ConnectError) as e:
        return f"[HTTP Error: {e}]"
    except (json.JSONDecodeError, KeyError) as e:
        return f"[Parse Error: {e}]"


def reset_session(http_client: httpx.Client, target_url: str, session_id: str):
    """Reset a session on the target."""
    try:
        http_client.post(
            f"{target_url}/api/reset",
            json={"message": "", "session_id": session_id},
        )
    except httpx.HTTPError:
        pass


def make_session_id(prefix: str = "attack") -> str:
    """Generate a unique session ID with a prefix."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


# =============================================================================
# Report utilities
# =============================================================================

def truncate(text: str, max_len: int) -> str:
    """Truncate text with ellipsis only if actually truncated."""
    return text[:max_len] + "..." if len(text) > max_len else text


def severity_summary_lines(results, severity_key_fn) -> list[str]:
    """
    Build severity summary lines from a list of results.

    severity_key_fn: function that takes a result and returns
                     severity as a string (e.g., lambda r: r.severity)
    """
    counts = {}
    for r in results:
        sev = severity_key_fn(r)
        counts[sev] = counts.get(sev, 0) + 1

    lines = []
    for sev in ["critical", "high", "medium", "low", "none"]:
        count = counts.get(sev, 0)
        if count > 0:
            lines.append(f"  {sev:10s}: {count}")
    return lines


def validate_cli_arg(args: list, default: int, name: str, max_val: int = None) -> int:
    """Validate a CLI integer argument with helpful error messages."""
    if len(args) <= 1:
        return default
    try:
        val = int(args[1])
        if val < 1:
            raise ValueError
        if max_val and val > max_val:
            print(f"Warning: {name}={val} exceeds maximum useful value of {max_val}")
        return val
    except ValueError:
        print(f"Usage: python {args[0]} [{name}]")
        print(f"  {name} must be a positive integer (default: {default})")
        import sys
        sys.exit(1)
