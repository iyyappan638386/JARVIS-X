import json

from app.backup import create_backup, restore_backup


def test_backup_and_restore(tmp_path, monkeypatch):
    memory_file = tmp_path / "data" / "conversation.json"
    backup_dir = tmp_path / "data" / "backups"

    monkeypatch.setattr("app.backup.MEMORY_FILE", memory_file)
    monkeypatch.setattr("app.backup.BACKUP_DIR", backup_dir)

    original = [
        {"role": "user", "content": "My project is BLACKBOX."},
        {"role": "assistant", "content": "I remember BLACKBOX."},
    ]

    memory_file.parent.mkdir(parents=True, exist_ok=True)
    memory_file.write_text(json.dumps(original), encoding="utf-8")

    backup_path = create_backup()

    memory_file.write_text("[]", encoding="utf-8")
    restored_count = restore_backup(str(backup_path))

    restored = json.loads(memory_file.read_text(encoding="utf-8"))

    assert restored_count == 2
    assert restored == original


def test_restore_rejects_invalid_backup(tmp_path, monkeypatch):
    import pytest

    memory_file = tmp_path / "conversation.json"
    bad_backup = tmp_path / "bad.json"
    bad_backup.write_text('{"invalid": true}', encoding="utf-8")

    monkeypatch.setattr("app.backup.MEMORY_FILE", memory_file)

    with pytest.raises(ValueError):
        restore_backup(str(bad_backup))
