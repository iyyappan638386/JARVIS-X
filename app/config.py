import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "JARVIS-X"
    app_env: str = "development"
    log_level: str = "INFO"
    default_language: str = "auto"
    wake_word: str = "Hey Jarvis"
    llm_provider: str = "ollama"
    ollama_model: str = "qwen2.5:3b"
    memory_limit: int = 20


def load_settings() -> Settings:
    try:
        memory_limit = int(os.getenv("MEMORY_LIMIT", "20"))
    except ValueError:
        memory_limit = 20

    return Settings(
        app_name=os.getenv("APP_NAME", "JARVIS-X"),
        app_env=os.getenv("APP_ENV", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        default_language=os.getenv("DEFAULT_LANGUAGE", "auto"),
        wake_word=os.getenv("WAKE_WORD", "Hey Jarvis"),
        llm_provider=os.getenv("LLM_PROVIDER", "ollama"),
        ollama_model=os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
        memory_limit=max(1, memory_limit),
    )
