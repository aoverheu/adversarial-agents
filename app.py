"""
HelpBot Web App
===============
FastAPI server that serves the chat frontend and exposes the agent as an API.
"""

from dotenv import load_dotenv
load_dotenv()

import anthropic
from collections import OrderedDict
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from agent import Agent, HELPBOT_SYSTEM_PROMPT

app = FastAPI(title="HelpBot - TechNova Support")
templates = Jinja2Templates(directory="templates")

# Shared Anthropic client — one connection pool for all sessions
_shared_client = anthropic.Anthropic()

MAX_SESSIONS = 100  # Evict oldest sessions when this limit is reached


class SessionStore:
    """LRU-bounded session store to prevent unbounded memory growth."""

    def __init__(self, max_size: int = MAX_SESSIONS):
        self._store: OrderedDict[str, Agent] = OrderedDict()
        self._max_size = max_size

    def get(self, session_id: str) -> Agent:
        if session_id in self._store:
            self._store.move_to_end(session_id)
            return self._store[session_id]
        # Evict oldest if at capacity
        while len(self._store) >= self._max_size:
            self._store.popitem(last=False)
        agent = Agent(
            name="HelpBot",
            system_prompt=HELPBOT_SYSTEM_PROMPT,
            _client=_shared_client,
        )
        self._store[session_id] = agent
        return agent

    def reset(self, session_id: str):
        if session_id in self._store:
            self._store[session_id].reset()


sessions = SessionStore()


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """The API endpoint our adversarial agent will attack later."""
    agent = sessions.get(req.session_id)
    try:
        response = agent.run(req.message)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Agent error: {type(e).__name__}: {str(e)}"},
        )
    return ChatResponse(response=response, session_id=req.session_id)


@app.post("/api/reset")
async def reset(req: ChatRequest):
    """Reset a session's conversation history."""
    sessions.reset(req.session_id)
    return {"status": "reset", "session_id": req.session_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8877)
