import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import tempfile
from buisness.eleven_labs_buisness import ElevenLabsBuisness


class TestElevenLabsBuisness(unittest.TestCase):
    """Unit tests for ElevenLabsBuisness class."""

    @patch('buisness.eleven_labs_buisness.VideoFileClip')
    @patch('buisness.eleven_labs_buisness.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_audio_data')
    @patch('os.path.exists')
    @patch('os.remove')
    def test_extract_audio_bytes_success(self, mock_remove, mock_exists, mock_file, mock_tempfile, mock_video):
        """Test successful audio extraction from video."""
        # Setup mocks
        mock_exists.return_value = True
        mock_temp = MagicMock()
        mock_temp.name = 'temp_audio.mp3'
        mock_tempfile.return_value = mock_temp
        
        mock_audio = MagicMock()
        mock_video_instance = MagicMock()
        mock_video_instance.audio = mock_audio
        mock_video_instance.duration = 10.5
        mock_video.return_value = mock_video_instance
        
        # Execute
        result = ElevenLabsBuisness.extract_audio_bytes_from_video('fake_video.mp4')
        
        # Verify
        self.assertEqual(result, b'fake_audio_data')
        mock_video.assert_called_once_with('fake_video.mp4')
        mock_audio.write_audiofile.assert_called_once()
        mock_video_instance.close.assert_called_once()
        mock_audio.close.assert_called_once()

    @patch('os.path.exists')
    def test_extract_audio_file_not_found(self, mock_exists):
        """Test error when video file doesn't exist."""
        mock_exists.return_value = False
        
        with self.assertRaises(FileNotFoundError) as context:
            ElevenLabsBuisness.extract_audio_bytes_from_video('nonexistent.mp4')
        
        self.assertIn("Video file not found", str(context.exception))

    @patch('buisness.eleven_labs_buisness.VideoFileClip')
    @patch('os.path.exists')
    def test_extract_audio_no_audio_track(self, mock_exists, mock_video):
        """Test error when video has no audio track."""
        mock_exists.return_value = True
        
        # Setup mock video with no audio
        mock_video_instance = MagicMock()
        mock_video_instance.audio = None
        mock_video.return_value = mock_video_instance
        
        with self.assertRaises(ValueError) as context:
            ElevenLabsBuisness.extract_audio_bytes_from_video('video_no_audio.mp4')
        
        self.assertIn("no audio track", str(context.exception))
        mock_video_instance.close.assert_called_once()

    @patch('buisness.eleven_labs_buisness.VideoFileClip')
    @patch('buisness.eleven_labs_buisness.tempfile.NamedTemporaryFile')
    @patch('os.path.exists')
    @patch('os.remove')
    def test_extract_audio_cleanup_on_error(self, mock_remove, mock_exists, mock_tempfile, mock_video):
        """Test that temporary files are cleaned up even on error."""
        mock_exists.return_value = True
        
        # Setup mocks
        mock_temp = MagicMock()
        mock_temp.name = 'temp_audio.mp3'
        mock_tempfile.return_value = mock_temp
        
        mock_audio = MagicMock()
        # Simulate error during audio writing
        mock_audio.write_audiofile.side_effect = Exception("Write error")
        
        mock_video_instance = MagicMock()
        mock_video_instance.audio = mock_audio
        mock_video.return_value = mock_video_instance
        
        # Execute and verify exception
        with self.assertRaises(Exception):
            ElevenLabsBuisness.extract_audio_bytes_from_video('video.mp4')
        
        # Verify cleanup was attempted
        mock_video_instance.close.assert_called_once()
        mock_audio.close.assert_called_once()

    @patch('buisness.eleven_labs_buisness.VideoFileClip')
    @patch('buisness.eleven_labs_buisness.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data=b'test_audio')
    @patch('os.path.exists')
    @patch('os.remove')
    def test_extract_audio_returns_correct_bytes(self, mock_remove, mock_exists, mock_file, mock_tempfile, mock_video):
        """Test that extracted audio bytes match expected data."""
        mock_exists.return_value = True
        
        mock_temp = MagicMock()
        mock_temp.name = 'temp_audio.mp3'
        mock_tempfile.return_value = mock_temp
        
        mock_audio = MagicMock()
        mock_video_instance = MagicMock()
        mock_video_instance.audio = mock_audio
        mock_video_instance.duration = 5.0
        mock_video.return_value = mock_video_instance
        
        result = ElevenLabsBuisness.extract_audio_bytes_from_video('video.mp4')
        
        self.assertIsInstance(result, bytes)
        self.assertEqual(result, b'test_audio')


if __name__ == "__main__":
    unittest.main()
