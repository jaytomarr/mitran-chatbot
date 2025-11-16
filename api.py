from typing import Optional
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from chat_client import ChatClient


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = ChatClient()


class ChatRequest(BaseModel):
    session_id: str
    message: str
    stream: Optional[bool] = False

class SendRequest(BaseModel):
    session_id: str
    text: str

class StreamRequest(BaseModel):
    session_id: str
    text: str


@app.post("/v1/sessions")
async def create_session():
    sid = str(uuid.uuid4())
    client._get_history(sid)
    return {"session_id": sid}

@app.post("/v1/chat/send")
async def chat_send(req: SendRequest):
    text = client.generate(req.session_id, req.text)
    return {"text": text}

@app.post("/v1/chat/stream")
async def chat_stream_post(req: StreamRequest):
    def iter_sse():
        for piece in client.stream(req.session_id, req.text):
            yield f"data: {piece}\n\n"
    return StreamingResponse(iter_sse(), media_type="text/event-stream")

@app.get("/v1/chat/stream")
async def chat_stream_get(session_id: str, text: str):
    def iter_sse():
        for piece in client.stream(session_id, text):
            yield f"data: {piece}\n\n"
    return StreamingResponse(iter_sse(), media_type="text/event-stream")

@app.get("/v1/chat/history")
async def chat_history(session_id: str):
    items = client._get_history(session_id)
    messages = []
    for c in items:
        t = ""
        for p in getattr(c, "parts", []):
            if hasattr(p, "text") and p.text:
                t += p.text
        role = "user" if getattr(c, "role", "") == "user" else "assistant"
        messages.append({"role": role, "text": t})
    return {"messages": messages}

@app.post("/chat")
async def chat(req: ChatRequest):
    text = client.generate(req.session_id, req.message)
    return {"text": text}


@app.get("/health")
async def health():
    return {"status": "ok"}


