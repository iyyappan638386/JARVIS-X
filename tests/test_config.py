import pytest
from app.config import load_settings

def test_default_settings(monkeypatch):
    for key in ("APP_NAME", "APP_ENV", "LOG_LEVEL", "DEFAULT_LANGUAGE", "WAKE_WORD", "LLM_PROVIDER", "OLLAMA_MODEL", "MEMORY_LIMIT"):
        monkeypatch.delenv(key, raising=False)
    settings = load_settings()
    assert settings.app_name == "JARVIS-X"
    assert settings.app_env == "development"
    assert settings.log_level == "INFO"
    assert settings.default_language == "auto"
    assert settings.wake_word == "Hey Jarvis"
    assert settings.llm_provider == "ollama"
    assert settings.ollama_model == "qwen2.5:3b"
    assert settings.memory_limit == 20

def test_environment_settings(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Test-JARVIS")
    monkeypatch.setenv("APP_ENV", "testing")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DEFAULT_LANGUAGE", "en")
    monkeypatch.setenv("WAKE_WORD", "Hello Jarvis")
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")
    monkeypatch.setenv("MEMORY_LIMIT", "30")
    settings = load_settings()
    assert settings.app_name == "Test-JARVIS"
    assert settings.app_env == "testing"
    assert settings.log_level == "DEBUG"
    assert settings.default_language == "en"
    assert settings.wake_word == "Hello Jarvis"
    assert settings.ollama_model == "test-model"
    assert settings.memory_limit == 30

def test_invalid_memory_limit_uses_default(monkeypatch):
    monkeypatch.setenv("MEMORY_LIMIT", "invalid")
    assert load_settings().memory_limit == 20

def test_memory_limit_minimum_is_one(monkeypatch):
    monkeypatch.setenv("MEMORY_LIMIT", "0")
    assert load_settings().memory_limit == 1
