import json
import pytest
from app.long_term_memory import LongTermMemory

def test_remember_and_recall(tmp_path):
    memory = LongTermMemory(str(tmp_path / "facts.json"))
    memory.remember("project", "BLACKBOX")
    assert memory.recall("project") == "BLACKBOX"

def test_key_normalization(tmp_path):
    memory = LongTermMemory(str(tmp_path / "facts.json"))
    memory.remember(" project ", " BLACKBOX ")
    assert memory.recall(" project ") == "BLACKBOX"

def test_forget_normalizes_key(tmp_path):
    memory = LongTermMemory(str(tmp_path / "facts.json"))
    memory.remember("project", "BLACKBOX")
    assert memory.forget(" project ") is True
    assert memory.recall("project") is None

def test_facts_persist_across_instances(tmp_path):
    path = str(tmp_path / "facts.json")
    first = LongTermMemory(path)
    first.remember("project", "BLACKBOX")
    second = LongTermMemory(path)
    assert second.recall("project") == "BLACKBOX"

def test_empty_key_or_value_is_rejected(tmp_path):
    memory = LongTermMemory(str(tmp_path / "facts.json"))
    with pytest.raises(ValueError):
        memory.remember(" ", "BLACKBOX")
    with pytest.raises(ValueError):
        memory.remember("project", " ")

def test_non_string_key_or_value_is_rejected(tmp_path):
    memory = LongTermMemory(str(tmp_path / "facts.json"))
    with pytest.raises(TypeError):
        memory.remember(None, "BLACKBOX")
    with pytest.raises(TypeError):
        memory.remember("project", None)

def test_corrupted_json_returns_empty_facts(tmp_path):
    path = tmp_path / "facts.json"
    path.write_text("{invalid json", encoding="utf-8")
    memory = LongTermMemory(str(path))
    assert memory.get_all() == {}
