import json
import os
import tempfile
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
        except (json.JSONDecodeError, OSError):
            return {}

        if not isinstance(data, dict):
            return {}

        return {
            key: value
            for key, value in data.items()
            if isinstance(key, str) and isinstance(value, str)
        }

    def _save(self, facts: dict[str, str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=self.path.name + ".",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                json.dump(
                    facts,
                    temporary_file,
                    indent=2,
                    ensure_ascii=False,
                )
                temporary_file.flush()
                os.fsync(temporary_file.fileno())

            os.replace(temporary_path, self.path)
        except Exception:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise

    def remember(self, key: str, value: str) -> None:
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError("Key and value must be strings.")

        key, value = key.strip(), value.strip()
        if not key or not value:
            raise ValueError("Key and value cannot be empty.")

        facts = self._load()
        facts[key] = value
        self._save(facts)

    def recall(self, key: str) -> str | None:
        if not isinstance(key, str):
            raise TypeError("Key must be a string.")
        return self._load().get(key.strip())

    def get_all(self) -> dict[str, str]:
        return self._load()

    def forget(self, key: str) -> bool:
        if not isinstance(key, str):
            raise TypeError("Key must be a string.")

        key = key.strip()
        facts = self._load()
        if key not in facts:
            return False

        del facts[key]
        self._save(facts)
        return True
