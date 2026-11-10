from app.memory import ConversationMemory


def test_add_and_retrieve_messages(tmp_path):
    memory = ConversationMemory(storage_path=str(tmp_path / "test_memory.json"))
    memory.add_message("user", "Hello Jarvis")
    memory.add_message("assistant", "Hello Batman")

    assert len(memory.get_messages()) == 2
    assert memory.get_messages()[0]["content"] == "Hello Jarvis"


def test_memory_keeps_only_recent_messages(tmp_path):
    memory = ConversationMemory(
        max_messages=2,
        storage_path=str(tmp_path / "recent_memory.json"),
    )
    memory.add_message("user", "Message 1")
    memory.add_message("assistant", "Message 2")
    memory.add_message("user", "Message 3")

    messages = memory.get_messages()
    assert len(messages) == 2
    assert messages[0]["content"] == "Message 2"
    assert messages[1]["content"] == "Message 3"


def test_clear_memory(tmp_path):
    memory = ConversationMemory(storage_path=str(tmp_path / "clear_memory.json"))
    memory.add_message("user", "Hello")
    memory.clear()

    assert memory.get_messages() == []


def test_invalid_role_is_rejected(tmp_path):
    import pytest

    memory = ConversationMemory(storage_path=str(tmp_path / "invalid_memory.json"))

    with pytest.raises(ValueError):
        memory.add_message("system", "Invalid message")
