import pytest
from unittest.mock import patch, MagicMock
from services.eleven_labs_service import ElevenLabsService


def test_init_success():
    with patch("services.eleven_labs_service.ElevenLabs") as mock_client:
        service = ElevenLabsService("fake_api_key")
        assert service.api_key == "fake_api_key"
        mock_client.assert_called_once_with(api_key="fake_api_key")


def test_init_no_api_key():
    with pytest.raises(ValueError) as excinfo:
        ElevenLabsService(None)
    assert "ElevenLabs API key is required" in str(excinfo.value)


def test_speech_to_text_success():
    with patch(
        "services.eleven_labs_service.ElevenLabsBuisness.extract_audio_bytes_from_video",
        return_value=b"audio",
    ):
        mock_client = MagicMock()
        mock_transcription = MagicMock()
        mock_transcription.words = ["word1", "word2"]
        mock_client.speech_to_text.convert.return_value = mock_transcription
        with patch("services.eleven_labs_service.ElevenLabs", return_value=mock_client):
            service = ElevenLabsService("key")
            result = service.speech_to_text("video.mp4", "en")
            assert result.words == ["word1", "word2"]


def test_speech_to_text_file_not_found():
    with patch(
        "services.eleven_labs_service.ElevenLabsBuisness.extract_audio_bytes_from_video",
        side_effect=FileNotFoundError("not found"),
    ):
        with patch("services.eleven_labs_service.ElevenLabs", return_value=MagicMock()):
            service = ElevenLabsService("key")
            with pytest.raises(FileNotFoundError):
                service.speech_to_text("video.mp4", "en")
