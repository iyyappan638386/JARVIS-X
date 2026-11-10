from dataclasses import dataclass, field
from pathlib import Path
import json


@dataclass
class ConversationMemory:
    """Store conversation messages and save them to a JSON file."""
    max_messages: int = 20
    storage_path: str = "data/conversation.json"
    messages: list[dict[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        path = Path(self.storage_path)
        if path.exists():
            try:
                saved = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(saved, list):
                    self.messages = [
                        item for item in saved
                        if isinstance(item, dict)
                        and item.get("role") in {"user", "assistant"}
                        and isinstance(item.get("content"), str)
                    ][-self.max_messages:]
            except (json.JSONDecodeError, OSError):
                self.messages = []

    def add_message(self, role: str, content: str) -> None:
        if role not in {"user", "assistant"}:
            raise ValueError("Role must be user or assistant.")

        self.messages.append({"role": role, "content": content})
        self.messages = self.messages[-self.max_messages:]
        self.save()

    def get_messages(self) -> list[dict[str, str]]:
        return list(self.messages)

    def save(self) -> None:
        path = Path(self.storage_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.messages, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def clear(self) -> None:
        self.messages.clear()
        self.save()
