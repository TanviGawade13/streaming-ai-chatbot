const chat = document.getElementById("chat");
const form = document.getElementById("inputForm");
const input = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const settingsBtn = document.getElementById("settingsBtn");
const settings = document.getElementById("settings");
const systemPrompt = document.getElementById("systemPrompt");
const newChatBtn = document.getElementById("newChatBtn");

// Same origin as the backend, so a relative URL works
const API_BASE = "";

// Keep one session id per browser, so refreshing keeps the conversation
let sessionId = localStorage.getItem("neon_session_id");
if (!sessionId) {
  sessionId = crypto.randomUUID();
  localStorage.setItem("neon_session_id", sessionId);
}

function addMessage(text, role) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}

settingsBtn.addEventListener("click", () => {
  settings.classList.toggle("hidden");
});

newChatBtn.addEventListener("click", async () => {
  await fetch(`${API_BASE}/session/${sessionId}/reset`, { method: "POST" });
  sessionId = crypto.randomUUID();
  localStorage.setItem("neon_session_id", sessionId);
  chat.innerHTML = "";
  addMessage("New chat started. How can I help?", "bot");
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const message = input.value.trim();
  if (!message) return;

  addMessage(message, "user");
  input.value = "";
  sendBtn.disabled = true;

  const botBubble = addMessage("", "bot");

  try {
    const response = await fetch(`${API_BASE}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        message: message,
        system_prompt: systemPrompt.value.trim() || null,
      }),
    });

    if (!response.ok) {
      throw new Error(`Server error ${response.status}`);
    }

    // Read the streamed body chunk by chunk and append it to the bubble
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      botBubble.textContent += decoder.decode(value, { stream: true });
      chat.scrollTop = chat.scrollHeight;
    }
  } catch (error) {
    botBubble.classList.add("error");
    botBubble.textContent = "Something went wrong: " + error.message;
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
});
