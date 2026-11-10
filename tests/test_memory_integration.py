from unittest.mock import patch, MagicMock
import json

from app.ai.ollama_provider import OllamaProvider
from app.memory import ConversationMemory


def test_provider_remembers_conversation(tmp_path):
    memory = ConversationMemory(
        storage_path=str(tmp_path / "integration_memory.json")
    )
    provider = OllamaProvider(memory=memory)

    def fake_response(*args, **kwargs):
        response = MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = json.dumps({
            "message": {"content": "Your project is BLACKBOX."}
        }).encode("utf-8")
        return response

    with patch(
        "app.ai.ollama_provider.urllib.request.urlopen",
        side_effect=fake_response,
    ) as mock_urlopen:
        provider.generate_response("My project is BLACKBOX.")

        provider.generate_response("Do you remember my project?")

        second_request = mock_urlopen.call_args.args[0]
        second_payload = json.loads(second_request.data.decode("utf-8"))

        assert any(
            item.get("content") == "My project is BLACKBOX."
            for item in second_payload["messages"]
        )

    assert len(memory.get_messages()) == 4
