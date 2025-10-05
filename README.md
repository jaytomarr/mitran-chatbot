# Simple Chatbot (Gemini)

Minimal scaffold to use your Google AI Studio model for a chatbot with:
- ChatClient (Python) with session memory ON and Google Search tool enabled
- FastAPI endpoint: POST /chat
- Streamlit test UI

## Setup
1. Python 3.10+
2. Install deps:
   
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment:
   - Copy `env.example` to `.env` and fill values
   - Required: `GEMINI_API_KEY`

## Run Streamlit (local test)
```bash
streamlit run app.py
```

## Run API
```bash
uvicorn api:app --reload --port 8000
```

POST /chat body:
```json
{
  "session_id": "abc123",
  "message": "Hello",
  "stream": false
}
```

Response:
```json
{ "text": "..." }
```

## Files
- `chat_client.py` core client with memory and search tool
- `api.py` FastAPI endpoint
- `app.py` Streamlit chat UI
- `prompts/system.txt` system instructions
- `config.py` env-driven config
- `requirements.txt` dependencies


