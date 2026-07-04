"""
Phase 1: Interactive Chatbot (SRS section 3.5) — standalone version.

No external API, no API key, no internet connection required at runtime.
NLP is handled entirely by nlp_engine.py using rule-based intent matching.

Run:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000

Then open frontend/index.html in a browser.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

import nlp_engine

app = FastAPI(title="Finance Assistant - Chatbot Service (Standalone)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the frontend from the same service, so deployment is a single URL.
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    intent: str


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = nlp_engine.handle_message(req.message)
    return ChatResponse(reply=result.reply, intent=result.intent)


@app.get("/health")
def health():
    return {"status": "ok"}
