# Neon_bot

A chatbot web app with a FastAPI backend and a plain HTML/CSS/JavaScript frontend. It talks to the `openai/gpt-oss-20b` model hosted on Groq, streams replies word by word, lets you set a custom system prompt, and summarizes older messages to keep long conversations manageable.

## Features

- **Streaming replies:** Answers appear token by token as the model generates them.
- **Custom system prompt:** Change how the bot behaves from the Settings panel.
- **Conversation memory:** Each browser keeps its own session, so refreshing the page keeps the chat.
- **Automatic summarization:** Once a conversation passes 12 messages, older messages are condensed into a summary and only the 6 most recent are kept word-for-word.
- **New chat:** Reset the conversation at any time.
- **Single server:** The FastAPI backend also serves the frontend, so you run one command.

## Tech Stack

- **Backend:** Python, FastAPI, Uvicorn
- **LLM provider:** Groq (via the OpenAI-compatible API using the `openai` library)
- **Model:** `openai/gpt-oss-20b`
- **Frontend:** HTML, CSS, JavaScript (no framework)
- **Config:** python-dotenv

## Project Structure

```
neon-chatbot/
├── backend/
│   ├── main.py            # FastAPI routes, sessions, static file serving
│   ├── chatbot.py         # LLM calls, streaming, summarization
│   ├── requirements.txt   # Python dependencies
│   └── .env               # Your secret API key (not committed)
└── frontend/
    ├── index.html         # Page structure
    ├── style.css          # Styling
    └── script.js          # Sending messages, reading the stream
```

## Prerequisites

- Python 3.9 or newer
- A Groq API key from [console.groq.com](https://console.groq.com)

## Setup

1. Clone or download the project and move into it:

   ```bash
   cd neon-chatbot
   ```

2. Create the environment file inside `backend/`:

   ```bash
   # backend/.env
   GROQ_API_KEY=your_groq_key_here
   ```

3. Install the dependencies:
   ```bash
   cd backend
   python -m pip install -r requirements.txt
   ```

## Running the App

From the `backend` folder, start the server:

```bash
uvicorn main:app --reload
```

Then open **http://127.0.0.1:8000** in your browser.

The interactive API documentation is available at **http://127.0.0.1:8000/docs**.

## API Endpoints

| Method | Endpoint                      | Description                                               |
| ------ | ----------------------------- | --------------------------------------------------------- |
| POST   | `/chat/stream`                | Send a message and receive a streamed reply               |
| GET    | `/session/{session_id}`       | Get a session's system prompt, summary, and message count |
| POST   | `/session/{session_id}/reset` | Delete a session and its history                          |

### Example request

```json
{
  "session_id": "abc123",
  "message": "Hi, who are you?",
  "system_prompt": null
}
```

## How It Works

1. The browser sends your message to `/chat/stream` along with a session ID.
2. The backend finds or creates that session's history.
3. `chatbot.py` builds the request: system prompt, then any summary of older messages, then recent messages.
4. Groq returns tokens, which are passed straight to the browser as they arrive.
5. When history grows past 12 messages, the older part is summarized and removed from the history.

## Configuration

Adjustable values live at the top of `backend/chatbot.py`:

| Constant                | Default              | Meaning                                       |
| ----------------------- | -------------------- | --------------------------------------------- |
| `MODEL`                 | `openai/gpt-oss-20b` | The Groq model to use                         |
| `DEFAULT_SYSTEM_PROMPT` | Neon_bot intro       | Used when no custom prompt is set             |
| `KEEP_RECENT`           | `6`                  | Messages kept word-for-word after summarizing |
| `SUMMARIZE_AFTER`       | `12`                 | Message count that triggers summarization     |

## Known Limitations

- **In-memory sessions:** Conversations are stored in a Python dictionary and are lost when the server restarts.
- **Summary delay:** The summary is generated after a reply finishes, so the reply that triggers it takes slightly longer.
- **Open CORS:** `allow_origins=["*"]` is suitable for local development only. Restrict it before deploying.
- **No authentication:** Anyone who can reach the server can use it and send requests on your API key's quota.

## Future Scope

- Store sessions in MongoDB so history survives restarts
- Run summarization in a background task
- Restrict CORS and add authentication
- Add a React frontend
- Add tool use and agentic workflows

## License

MIT License.
