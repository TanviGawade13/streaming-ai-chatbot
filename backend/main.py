from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from chatbot import Chatbot, DEFAULT_SYSTEM_PROMPT

load_dotenv()

app = FastAPI(title="Neon_bot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict this before deploying
    allow_methods=["*"],
    allow_headers=["*"],
)

bot = Chatbot()
sessions = {}  # session_id -> {"system_prompt", "summary", "messages"}


class ChatRequest(BaseModel):
    session_id: str
    message: str
    system_prompt: Optional[str] = None


def get_session(session_id, system_prompt=None):
    if session_id not in sessions:
        sessions[session_id] = {
            "system_prompt": system_prompt or DEFAULT_SYSTEM_PROMPT,
            "summary": "",
            "messages": [],
        }
    elif system_prompt:
        sessions[session_id]["system_prompt"] = system_prompt
    return sessions[session_id]


@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    session = get_session(req.session_id, req.system_prompt)
    return StreamingResponse(
        bot.stream(session, req.message),
        media_type="text/plain",
    )


@app.get("/session/{session_id}")
def session_info(session_id: str):
    session = sessions.get(session_id)
    if not session:
        return {"exists": False}
    return {
        "exists": True,
        "system_prompt": session["system_prompt"],
        "summary": session["summary"],
        "message_count": len(session["messages"]),
    }


@app.post("/session/{session_id}/reset")
def reset_session(session_id: str):
    sessions.pop(session_id, None)
    return {"reset": True}


# Serve the frontend from the same server (mounted last so API routes win)
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")