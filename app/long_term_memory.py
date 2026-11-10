import json
from pathlib import Path


class LongTermMemory:
    """Store important facts separately from recent conversation history."""

    def __init__(self, storage_path: str = "data/facts.json") -> None:
        self.path = Path(storage_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._save({})

    def _load(self) -> dict[str, str]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            return {}

    def _save(self, facts: dict[str, str]) -> None:
        self.path.write_text(
            json.dumps(facts, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def remember(self, key: str, value: str) -> None:
        key, value = key.strip(), value.strip()
        if not key or not value:
            raise ValueError("Key and value cannot be empty.")
        facts = self._load()
        facts[key] = value
        self._save(facts)

    def recall(self, key: str) -> str | None:
        return self._load().get(key.strip())

    def get_all(self) -> dict[str, str]:
        return self._load()

    def forget(self, key: str) -> bool:
        facts = self._load()
        if key not in facts:
            return False
        del facts[key]
        self._save(facts)
        return True
