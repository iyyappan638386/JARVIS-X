import json
from pathlib import Path
from datetime import datetime

from app.memory import ConversationMemory

MEMORY_FILE = Path("data/conversation.json")
BACKUP_DIR = Path("data/backups")


def create_backup() -> Path:
    if not MEMORY_FILE.exists():
        raise FileNotFoundError("No saved conversation found to back up.")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"conversation_{timestamp}.json"
    backup_file.write_text(
        MEMORY_FILE.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    return backup_file


def restore_backup(backup_file: str) -> int:
    source = Path(backup_file)

    if not source.is_file():
        raise FileNotFoundError("Backup file was not found.")

    messages = json.loads(source.read_text(encoding="utf-8"))

    if not isinstance(messages, list):
        raise ValueError("Backup format is invalid.")

    for item in messages:
        if (
            not isinstance(item, dict)
            or item.get("role") not in {"user", "assistant"}
            or not isinstance(item.get("content"), str)
        ):
            raise ValueError("Backup contains an invalid message.")

    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(
        json.dumps(messages, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return len(messages)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS-X memory backup tool")
    parser.add_argument("action", choices=["backup", "restore", "list"])
    parser.add_argument("file", nargs="?")
    args = parser.parse_args()

    if args.action == "backup":
        print(f"Backup created: {create_backup()}")

    elif args.action == "restore":
        if not args.file:
            parser.error("Provide a backup file path to restore.")
        count = restore_backup(args.file)
        print(f"Restored {count} messages.")

    else:
        files = sorted(BACKUP_DIR.glob("conversation_*.json")) if BACKUP_DIR.exists() else []
        if not files:
            print("No backups found.")
        else:
            for file in files:
                print(file)


if __name__ == "__main__":
    main()
