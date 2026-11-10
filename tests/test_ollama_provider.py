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
