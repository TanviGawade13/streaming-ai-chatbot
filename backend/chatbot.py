import os
from openai import OpenAI

MODEL = "openai/gpt-oss-20b"
DEFAULT_SYSTEM_PROMPT = (
    "You are Neon_bot, a helpful assistant. "
    "Introduce yourself in your first message. Give short and helpful answers."
)

KEEP_RECENT = 6       # messages kept word-for-word after summarizing
SUMMARIZE_AFTER = 12  # summarize older messages once history grows past this


class Chatbot:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )

    def build_messages(self, session):
        """Assemble what we send to the LLM: system prompt, summary, recent messages."""
        messages = [{"role": "system", "content": session["system_prompt"]}]
        if session["summary"]:
            messages.append({
                "role": "system",
                "content": "Summary of the earlier conversation:\n" + session["summary"],
            })
        messages.extend(session["messages"])
        return messages

    def stream(self, session, user_text):
        """Yield the reply token by token, then save it to history."""
        session["messages"].append({"role": "user", "content": user_text})

        full_reply = ""
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=self.build_messages(session),
            stream=True,
        )

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                full_reply += token
                yield token

        session["messages"].append({"role": "assistant", "content": full_reply})
        self.maybe_summarize(session)

    def maybe_summarize(self, session):
        """When history gets long, fold the oldest messages into a summary."""
        messages = session["messages"]
        if len(messages) <= SUMMARIZE_AFTER:
            return

        old = messages[:-KEEP_RECENT]
        recent = messages[-KEEP_RECENT:]

        transcript = "\n".join(f"{m['role']}: {m['content']}" for m in old)
        previous = f"Previous summary:\n{session['summary']}\n\n" if session["summary"] else ""

        response = self.client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system",
                 "content": "Summarize this conversation concisely. Keep key facts, names, and decisions."},
                {"role": "user", "content": previous + transcript},
            ],
        )

        session["summary"] = response.choices[0].message.content
        session["messages"] = recent