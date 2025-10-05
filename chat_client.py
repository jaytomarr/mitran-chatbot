import os
from typing import Dict, List, Optional, Iterable

from google import genai
from google.genai import types

from config import (
    MODEL_NAME,
    GOOGLE_SEARCH_TOOL_ENABLED,
    SESSION_MAX_TURNS,
    SYSTEM_PROMPT_PATH,
    GEMINI_API_KEY_ENV,
)


def _read_system_prompt() -> str:
    try:
        with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


class ChatClient:
    def __init__(self) -> None:
        api_key = os.environ.get(GEMINI_API_KEY_ENV)
        if not api_key:
            raise RuntimeError(f"Missing {GEMINI_API_KEY_ENV} environment variable")

        self.client = genai.Client(api_key=api_key)
        self.model = MODEL_NAME
        self.system_instruction_text = _read_system_prompt()
        self.histories: Dict[str, List[types.Content]] = {}

        self.tools: Optional[List[types.Tool]] = None
        if GOOGLE_SEARCH_TOOL_ENABLED:
            self.tools = [types.Tool(googleSearch=types.GoogleSearch())]

        self.generate_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
            safety_settings=[
                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_ONLY_HIGH"),
                types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_ONLY_HIGH"),
                types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_ONLY_HIGH"),
                types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"),
            ],
            tools=self.tools,
            system_instruction=[types.Part.from_text(text=self.system_instruction_text)] if self.system_instruction_text else None,
        )

    def _get_history(self, session_id: str) -> List[types.Content]:
        return self.histories.setdefault(session_id, [])

    def _trim_history(self, history: List[types.Content]) -> List[types.Content]:
        if SESSION_MAX_TURNS <= 0:
            return history
        # Each turn corresponds to user+model pair; keep last N*2 entries
        keep = max(1, SESSION_MAX_TURNS) * 2
        return history[-keep:]

    def add_user_message(self, session_id: str, text: str) -> None:
        history = self._get_history(session_id)
        history.append(types.Content(role="user", parts=[types.Part.from_text(text=text)]))
        self.histories[session_id] = self._trim_history(history)

    def add_model_message(self, session_id: str, text: str) -> None:
        history = self._get_history(session_id)
        history.append(types.Content(role="model", parts=[types.Part.from_text(text=text)]))
        self.histories[session_id] = self._trim_history(history)

    def generate(self, session_id: str, user_text: str) -> str:
        self.add_user_message(session_id, user_text)
        contents = list(self._get_history(session_id))

        response_text_parts: List[str] = []
        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=self.generate_config,
        ):
            if chunk.text:
                response_text_parts.append(chunk.text)

        full_text = "".join(response_text_parts)
        if full_text:
            self.add_model_message(session_id, full_text)
        return full_text

    def stream(self, session_id: str, user_text: str) -> Iterable[str]:
        self.add_user_message(session_id, user_text)
        contents = list(self._get_history(session_id))

        parts: List[str] = []
        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=self.generate_config,
        ):
            if chunk.text:
                parts.append(chunk.text)
                yield chunk.text
        full_text = "".join(parts)
        if full_text:
            self.add_model_message(session_id, full_text)


