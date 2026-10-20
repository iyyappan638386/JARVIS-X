from app.config import load_settings


def test_default_settings():
    settings = load_settings()

    assert settings.app_name == "JARVIS-X"
    assert settings.app_env == "development"
    assert settings.default_language == "auto"
    assert settings.wake_word == "Hey Jarvis"
    assert settings.llm_provider == "none"
