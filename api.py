from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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


@app.post("/chat")
async def chat(req: ChatRequest):
    if req.stream:
        # For simplicity, non-streaming JSON response. Streaming can be added later if needed.
        text = client.generate(req.session_id, req.message)
        return {"text": text}
    text = client.generate(req.session_id, req.message)
    return {"text": text}


@app.get("/health")
async def health():
    return {"status": "ok"}


