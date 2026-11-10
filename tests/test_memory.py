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


def test_memory_persists_across_instances(tmp_path):
    path = tmp_path / "persistent_memory.json"
    memory = ConversationMemory(storage_path=str(path))
    memory.add_message("user", "வணக்கம்")

    restored = ConversationMemory(storage_path=str(path))

    assert restored.get_messages() == [
        {"role": "user", "content": "வணக்கம்"}
    ]


def test_get_messages_returns_independent_data(tmp_path):
    memory = ConversationMemory(storage_path=str(tmp_path / "copy_memory.json"))
    memory.add_message("user", "Original")

    returned = memory.get_messages()
    returned[0]["content"] = "Changed"

    assert memory.get_messages()[0]["content"] == "Original"


def test_zero_max_messages_is_rejected(tmp_path):
    import pytest

    with pytest.raises(ValueError):
        ConversationMemory(
            max_messages=0,
            storage_path=str(tmp_path / "zero_memory.json"),
        )


def test_negative_max_messages_is_rejected(tmp_path):
    import pytest

    with pytest.raises(ValueError):
        ConversationMemory(
            max_messages=-1,
            storage_path=str(tmp_path / "negative_memory.json"),
        )


def test_non_string_content_is_rejected(tmp_path):
    import pytest

    memory = ConversationMemory(storage_path=str(tmp_path / "invalid_content.json"))

    with pytest.raises(TypeError):
        memory.add_message("user", None)
