import json
import urllib.request
import urllib.error
from app.memory import ConversationMemory
from app.long_term_memory import LongTermMemory


class OllamaProvider:
    """Connect JARVIS-X to a locally running Ollama model."""

    def __init__(self, model: str = "qwen2.5:3b", memory: ConversationMemory | None = None) -> None:
        self.model = model
        self.url = "http://localhost:11434/api/chat"
        self.memory = memory or ConversationMemory()
        self.long_term_memory = LongTermMemory()

    def generate_response(self, message: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are JARVIS-X, a helpful personal AI assistant. "
                          "Use saved facts when relevant, and do not invent personal facts. "
                        "Call the user Batman. Understand English, Tamil, "
                        "and Tanglish. Reply naturally in the language "
                        "the user uses. Keep answers clear and beginner-friendly."
                    ),
                },
                {"role": "system", "content": "Saved user facts: " + str(self.long_term_memory.get_all())},
                  *self.memory.get_messages(),
                {"role": "user", "content": message},
            ],
            "stream": False,
        }

        request = urllib.request.Request(
            self.url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))
                answer = result["message"]["content"]

                # Save explicit personal facts stated by the user.
                import re
                patterns = [
                    (
                        r"my project name is\s+(.+)",
                        "project_name",
                    ),
                ]
                for pattern, key in patterns:
                    match = re.search(pattern, message.strip(), re.IGNORECASE)
                    if match:
                        value = match.group(1).strip().rstrip(".!?")
                        if value:
                            self.long_term_memory.remember(key, value)

                self.memory.add_message("user", message)
                self.memory.add_message("assistant", answer)
                return answer
        except urllib.error.URLError as exc:
            raise RuntimeError(
                "Cannot connect to Ollama. Check that Ollama is running."
            ) from exc
