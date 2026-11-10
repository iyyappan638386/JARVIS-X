import pytest

from app.ai.provider import LLMProvider


def test_provider_requires_response_implementation():
    with pytest.raises(TypeError):
        LLMProvider()
