from dataclasses import dataclass, field
from pathlib import Path
import copy
import json
import os
import tempfile


@dataclass
class ConversationMemory:
    """Store conversation messages and save them to a JSON file."""

    max_messages: int = 20
    storage_path: str = "data/conversation.json"
    messages: list[dict[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.max_messages, bool) or not isinstance(self.max_messages, int):
            raise TypeError("max_messages must be an integer.")
        if self.max_messages < 1:
            raise ValueError("max_messages must be at least 1.")

        path = Path(self.storage_path)
        if path.exists():
            try:
                saved = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(saved, list):
                    self.messages = [
                        item.copy()
                        for item in saved
                        if isinstance(item, dict)
                        and item.get("role") in {"user", "assistant"}
                        and isinstance(item.get("content"), str)
                    ][-self.max_messages:]
            except (json.JSONDecodeError, OSError):
                self.messages = []

    def add_message(self, role: str, content: str) -> None:
        if role not in {"user", "assistant"}:
            raise ValueError("Role must be user or assistant.")
        if not isinstance(content, str):
            raise TypeError("Message content must be a string.")

        self.messages.append({"role": role, "content": content})
        self.messages = self.messages[-self.max_messages:]
        self.save()

    def get_messages(self) -> list[dict[str, str]]:
        return copy.deepcopy(self.messages)

    def save(self) -> None:
        path = Path(self.storage_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                prefix=path.name + ".",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                json.dump(
                    self.messages,
                    temporary_file,
                    indent=2,
                    ensure_ascii=False,
                )
                temporary_file.flush()
                os.fsync(temporary_file.fileno())

            os.replace(temporary_path, path)
        except Exception:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise

    def clear(self) -> None:
        self.messages.clear()
        self.save()
