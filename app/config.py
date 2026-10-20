import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "JARVIS-X"
    app_env: str = "development"
    log_level: str = "INFO"
    default_language: str = "auto"
    wake_word: str = "Hey Jarvis"
    llm_provider: str = "none"


def load_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "JARVIS-X"),
        app_env=os.getenv("APP_ENV", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        default_language=os.getenv("DEFAULT_LANGUAGE", "auto"),
        wake_word=os.getenv("WAKE_WORD", "Hey Jarvis"),
        llm_provider=os.getenv("LLM_PROVIDER", "none"),
    )
