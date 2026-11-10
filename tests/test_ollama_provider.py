from unittest.mock import patch

from app.ai.ollama_provider import OllamaProvider


def test_provider_uses_local_ollama_endpoint():
    provider = OllamaProvider()

    assert provider.model == "qwen2.5:3b"
    assert provider.url == "http://localhost:11434/api/chat"


@patch("app.ai.ollama_provider.urllib.request.urlopen")
def test_provider_returns_ai_response(mock_urlopen):
    import json
    from unittest.mock import MagicMock

    fake_response = MagicMock()
    fake_response.read.return_value = json.dumps({
        "message": {"content": "Vanakkam Batman!"}
    }).encode("utf-8")

    mock_urlopen.return_value.__enter__.return_value = fake_response

    provider = OllamaProvider()
    result = provider.generate_response("Vanakkam")

    assert result == "Vanakkam Batman!"
    mock_urlopen.assert_called_once()

def test_project_fact_extraction(tmp_path, monkeypatch):
    import json
    from unittest.mock import MagicMock
    from app.long_term_memory import LongTermMemory
    monkeypatch.setattr("app.ai.ollama_provider.LongTermMemory", lambda: LongTermMemory(str(tmp_path / "facts.json")))
    provider = OllamaProvider()
    response = MagicMock()
    response.__enter__.return_value = response
    response.read.return_value = json.dumps({"message": {"content": "Saved."}}).encode("utf-8")
    with patch("app.ai.ollama_provider.urllib.request.urlopen", return_value=response):
        provider.generate_response("My project is BLACKBOX.")
    assert provider.long_term_memory.recall("project_name") == "BLACKBOX"

def test_project_name_fact_extraction(tmp_path, monkeypatch):
    import json
    from unittest.mock import MagicMock
    from app.long_term_memory import LongTermMemory
    monkeypatch.setattr("app.ai.ollama_provider.LongTermMemory", lambda: LongTermMemory(str(tmp_path / "facts.json")))
    provider = OllamaProvider()
    response = MagicMock()
    response.__enter__.return_value = response
    response.read.return_value = json.dumps({"message": {"content": "Saved."}}).encode("utf-8")
    with patch("app.ai.ollama_provider.urllib.request.urlopen", return_value=response):
        provider.generate_response("My project name is JARVIS-X.")
    assert provider.long_term_memory.recall("project_name") == "JARVIS-X"


def test_provider_handles_connection_error():
    import urllib.error
    import pytest
    provider = OllamaProvider()
    with patch("app.ai.ollama_provider.urllib.request.urlopen", side_effect=urllib.error.URLError("offline")):
        with pytest.raises(RuntimeError, match="Cannot connect to Ollama"):
            provider.generate_response("Hello")

def test_provider_handles_invalid_json():
    import pytest
    from unittest.mock import MagicMock
    provider = OllamaProvider()
    response = MagicMock()
    response.__enter__.return_value = response
    response.read.return_value = b"not valid json"
    with patch("app.ai.ollama_provider.urllib.request.urlopen", return_value=response):
        with pytest.raises(RuntimeError, match="invalid response"):
            provider.generate_response("Hello")

def test_provider_handles_missing_message_content():
    import json
    import pytest
    from unittest.mock import MagicMock
    provider = OllamaProvider()
    response = MagicMock()
    response.__enter__.return_value = response
    response.read.return_value = json.dumps({"message": {}}).encode("utf-8")
    with patch("app.ai.ollama_provider.urllib.request.urlopen", return_value=response):
        with pytest.raises(RuntimeError, match="invalid response"):
            provider.generate_response("Hello")
