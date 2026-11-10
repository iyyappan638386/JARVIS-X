import json
import re
import urllib.error
import urllib.request

from app.memory import ConversationMemory
from app.long_term_memory import LongTermMemory


class OllamaProvider:
    """Connect JARVIS-X to a locally running Ollama model."""

    def __init__(
        self,
        model: str = "qwen2.5:3b",
        memory: ConversationMemory | None = None,
    ) -> None:
        self.model = model
        self.url = "http://localhost:11434/api/chat"
        self.memory = memory if memory is not None else ConversationMemory()
        self.long_term_memory = LongTermMemory()

    def _remember_explicit_facts(self, message: str) -> None:
        """Extract supported explicit project facts from the user's message."""
        patterns = (
            r"\bmy\s+project\s+name\s+is\s+(.+)",
            r"\bmy\s+project\s+is\s+(.+)",
        )

        for pattern in patterns:
            match = re.search(pattern, message.strip(), re.IGNORECASE)
            if match:
                value = match.group(1).strip().rstrip(" .!?")
                if value:
                    self.long_term_memory.remember("project_name", value)
                return

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
                {
                    "role": "system",
                    "content": "Saved user facts: " + str(self.long_term_memory.get_all()),
                },
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
                raw_response = response.read()
            result = json.loads(raw_response.decode("utf-8"))
            answer = result["message"]["content"]
            if not isinstance(answer, str):
                raise TypeError("Ollama response content must be a string.")
        except urllib.error.URLError as exc:
            raise RuntimeError(
                "Cannot connect to Ollama. Check that Ollama is running."
            ) from exc
        except (json.JSONDecodeError, UnicodeDecodeError, KeyError, TypeError) as exc:
            raise RuntimeError("Ollama returned an invalid response.") from exc

        self._remember_explicit_facts(message)
        self.memory.add_message("user", message)
        self.memory.add_message("assistant", answer)
        return answer
