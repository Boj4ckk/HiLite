import unittest
from unittest.mock import MagicMock, patch
from services.eleven_labs_service import ElevenLabsService


class TestElevenLabsService(unittest.TestCase):
    """Unit tests for ElevenLabsService class with mocked dependencies."""

    def test_init_with_valid_api_key(self):
        """Test successful initialization with valid API key."""
        with patch('services.eleven_labs_service.ElevenLabs') as mock_elevenlabs:
            service = ElevenLabsService("valid_api_key_123")
            
            self.assertEqual(service.api_key, "valid_api_key_123")
            mock_elevenlabs.assert_called_once_with(api_key="valid_api_key_123")

    def test_init_with_empty_api_key(self):
        """Test initialization fails with empty API key."""
        with self.assertRaises(ValueError) as context:
            ElevenLabsService("")
        
        self.assertIn("API key is required", str(context.exception))

    def test_init_with_none_api_key(self):
        """Test initialization fails with None API key."""
        with self.assertRaises(ValueError) as context:
            ElevenLabsService(None)
        
        self.assertIn("API key is required", str(context.exception))

    @patch('services.eleven_labs_service.ElevenLabs')
    def test_init_client_creation_failure(self, mock_elevenlabs):
        """Test initialization fails when ElevenLabs client creation fails."""
        mock_elevenlabs.side_effect = Exception("API initialization failed")
        
        with self.assertRaises(Exception) as context:
            ElevenLabsService("valid_key")
        
        self.assertIn("API initialization failed", str(context.exception))

    @patch('services.eleven_labs_service.ElevenLabsBuisness.extract_audio_bytes_from_video')
    @patch('services.eleven_labs_service.ElevenLabs')
    def test_speech_to_text_success(self, mock_elevenlabs, mock_extract_audio):
        """Test successful speech-to-text conversion."""
        # Setup mocks
        mock_extract_audio.return_value = b"fake_audio_data"
        
        mock_transcription = MagicMock()
        mock_transcription.words = ["Hello", "world"]
        
        mock_client = MagicMock()
        mock_client.speech_to_text.convert.return_value = mock_transcription
        mock_elevenlabs.return_value = mock_client
        
        # Execute
        service = ElevenLabsService("test_key")
        result = service.speech_to_text("video.mp4", "en")
        
        # Verify
        self.assertEqual(result, mock_transcription)
        mock_extract_audio.assert_called_once_with("video.mp4")
        mock_client.speech_to_text.convert.assert_called_once()
        
        # Check call arguments
        call_args = mock_client.speech_to_text.convert.call_args
        self.assertEqual(call_args.kwargs['file'], b"fake_audio_data")
        self.assertEqual(call_args.kwargs['language_code'], "en")
        self.assertEqual(call_args.kwargs['model_id'], "scribe_v1")

    @patch('services.eleven_labs_service.ElevenLabsBuisness.extract_audio_bytes_from_video')
    @patch('services.eleven_labs_service.ElevenLabs')
    def test_speech_to_text_file_not_found(self, mock_elevenlabs, mock_extract_audio):
        """Test speech_to_text with file not found error."""
        mock_extract_audio.side_effect = FileNotFoundError("Video file not found")
        mock_elevenlabs.return_value = MagicMock()
        
        service = ElevenLabsService("test_key")
        
        with self.assertRaises(FileNotFoundError):
            service.speech_to_text("nonexistent.mp4", "fr")

    @patch('services.eleven_labs_service.ElevenLabsBuisness.extract_audio_bytes_from_video')
    @patch('services.eleven_labs_service.ElevenLabs')
    def test_speech_to_text_no_audio_track(self, mock_elevenlabs, mock_extract_audio):
        """Test speech_to_text with no audio track error."""
        mock_extract_audio.side_effect = ValueError("Video has no audio track")
        mock_elevenlabs.return_value = MagicMock()
        
        service = ElevenLabsService("test_key")
        
        with self.assertRaises(ValueError):
            service.speech_to_text("video_no_audio.mp4", "fr")

    @patch('services.eleven_labs_service.ElevenLabsBuisness.extract_audio_bytes_from_video')
    @patch('services.eleven_labs_service.ElevenLabs')
    def test_speech_to_text_api_error(self, mock_elevenlabs, mock_extract_audio):
        """Test speech_to_text with API error."""
        mock_extract_audio.return_value = b"audio_data"
        
        mock_client = MagicMock()
        mock_client.speech_to_text.convert.side_effect = Exception("API rate limit exceeded")
        mock_elevenlabs.return_value = mock_client
        
        service = ElevenLabsService("test_key")
        
        with self.assertRaises(Exception) as context:
            service.speech_to_text("video.mp4", "en")
        
        self.assertIn("Failed to transcribe audio", str(context.exception))

    @patch('services.eleven_labs_service.ElevenLabsBuisness.extract_audio_bytes_from_video')
    @patch('services.eleven_labs_service.ElevenLabs')
    def test_speech_to_text_custom_parameters(self, mock_elevenlabs, mock_extract_audio):
        """Test speech_to_text with custom parameters."""
        mock_extract_audio.return_value = b"audio_data"
        
        mock_transcription = MagicMock()
        mock_client = MagicMock()
        mock_client.speech_to_text.convert.return_value = mock_transcription
        mock_elevenlabs.return_value = mock_client
        
        service = ElevenLabsService("test_key")
        result = service.speech_to_text(
            "video.mp4",
            "fr",
            model_id="custom_model",
            tag_audio_events=False,
            diarize=False
        )
        
        # Verify custom parameters
        call_args = mock_client.speech_to_text.convert.call_args
        self.assertEqual(call_args.kwargs['model_id'], "custom_model")
        self.assertEqual(call_args.kwargs['tag_audio_events'], False)
        self.assertEqual(call_args.kwargs['diarize'], False)
        self.assertEqual(call_args.kwargs['language_code'], "fr")


if __name__ == "__main__":
    unittest.main()
