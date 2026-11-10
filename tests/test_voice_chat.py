import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock
from app.voice_chat import transcribe_offline

@pytest.mark.parametrize(("language", "expected"), [
    ("auto", None),
    ("en", "en"),
    ("ta", "ta"),
])
def test_transcribe_offline_language_selection(language, expected):
    audio = MagicMock()
    audio.get_wav_data.return_value = b"fake wav data"

    model = MagicMock()
    model.transcribe.return_value = (
        [SimpleNamespace(text="Hello", no_speech_prob=0.01)],
        SimpleNamespace(language=expected),
    )

    result = transcribe_offline(audio, model, language)

    assert result == "Hello"
    assert model.transcribe.call_args.kwargs["language"] == expected
