import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
from pathlib import Path
from services.srt_service import SrtService


class TestSrtService(unittest.TestCase):
    """Unit tests for SrtService class with mocked dependencies."""

    @patch.dict(os.environ, {'SRT_DIR_PATH': 'tmp/srt'})
    @patch('services.srt_service.Path')
    def test_init_with_env_var(self, mock_path):
        """Test initialization with SRT_DIR_PATH set."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        
        service = SrtService("output.srt")
        
        self.assertIn("output.srt", service.srt_output_file)
        mock_path_instance.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch.dict(os.environ, {}, clear=True)
    @patch('services.srt_service.Path')
    def test_init_without_env_var_uses_default(self, mock_path):
        """Test initialization uses default when SRT_DIR_PATH not set."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        
        service = SrtService("output.srt")
        
        # Should use default value
        self.assertIn("output.srt", service.srt_output_file)
        mock_path_instance.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch.dict(os.environ, {'SRT_DIR_PATH': 'custom/path'})
    @patch('services.srt_service.Path')
    def test_init_creates_directory(self, mock_path):
        """Test that __init__ creates the SRT directory."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        
        service = SrtService("test.srt")
        
        mock_path_instance.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch.dict(os.environ, {'SRT_DIR_PATH': 'tmp/srt'})
    @patch('services.srt_service.Path')
    @patch('services.srt_service.SrtBuisness.transcription_to_srt_lines')
    @patch('builtins.open', new_callable=mock_open)
    def test_convert_transcription_success(self, mock_file, mock_srt_lines, mock_path):
        """Test successful transcription to SRT conversion."""
        # Setup mocks
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        
        mock_transcription = MagicMock()
        mock_transcription.words = ["word1", "word2", "word3"]
        
        mock_srt_lines.return_value = [
            "1\n00:00:00,000 --> 00:00:00,500\nHello",
            "2\n00:00:00,500 --> 00:00:01,000\nworld"
        ]
        
        # Execute
        service = SrtService("output.srt")
        result = service.convert_transcription_into_srt(mock_transcription)
        
        # Verify
        self.assertIn("output.srt", result)
        mock_srt_lines.assert_called_once_with(["word1", "word2", "word3"])
        mock_file.assert_called_once()
        
        # Verify write calls
        file_handle = mock_file()
        self.assertEqual(file_handle.write.call_count, 2)

    @patch.dict(os.environ, {'SRT_DIR_PATH': 'tmp/srt'})
    @patch('services.srt_service.Path')
    @patch('services.srt_service.SrtBuisness.transcription_to_srt_lines')
    @patch('builtins.open', new_callable=mock_open)
    def test_convert_transcription_empty_words(self, mock_file, mock_srt_lines, mock_path):
        """Test conversion with empty transcription."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        
        mock_transcription = MagicMock()
        mock_transcription.words = []
        
        mock_srt_lines.return_value = []
        
        service = SrtService("empty.srt")
        result = service.convert_transcription_into_srt(mock_transcription)
        
        self.assertIn("empty.srt", result)
        mock_srt_lines.assert_called_once_with([])

    @patch.dict(os.environ, {'SRT_DIR_PATH': 'tmp/srt'})
    @patch('services.srt_service.Path')
    @patch('services.srt_service.SrtBuisness.transcription_to_srt_lines')
    @patch('builtins.open', new_callable=mock_open)
    def test_convert_transcription_write_error(self, mock_file, mock_srt_lines, mock_path):
        """Test error handling when file write fails."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        
        mock_transcription = MagicMock()
        mock_transcription.words = ["word1"]
        
        mock_srt_lines.return_value = ["line1"]
        mock_file.side_effect = IOError("Disk full")
        
        service = SrtService("output.srt")
        
        with self.assertRaises(IOError):
            service.convert_transcription_into_srt(mock_transcription)

    @patch.dict(os.environ, {'SRT_DIR_PATH': 'tmp/srt'})
    @patch('services.srt_service.Path')
    @patch('services.srt_service.SrtBuisness.transcription_to_srt_lines')
    @patch('builtins.open', new_callable=mock_open)
    def test_convert_transcription_encoding_utf8(self, mock_file, mock_srt_lines, mock_path):
        """Test that file is written with UTF-8 encoding."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        
        mock_transcription = MagicMock()
        mock_transcription.words = ["word"]
        mock_srt_lines.return_value = ["line"]
        
        service = SrtService("output.srt")
        service.convert_transcription_into_srt(mock_transcription)
        
        # Verify encoding parameter
        call_args = mock_file.call_args
        self.assertEqual(call_args.kwargs['encoding'], 'utf-8')

    @patch.dict(os.environ, {'SRT_DIR_PATH': 'tmp/srt'})
    @patch('services.srt_service.Path')
    @patch('services.srt_service.SrtBuisness.transcription_to_srt_lines')
    def test_convert_transcription_srt_buisness_error(self, mock_srt_lines, mock_path):
        """Test error handling when SrtBuisness fails."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        
        mock_transcription = MagicMock()
        mock_transcription.words = ["word"]
        
        mock_srt_lines.side_effect = Exception("Processing error")
        
        service = SrtService("output.srt")
        
        with self.assertRaises(Exception) as context:
            service.convert_transcription_into_srt(mock_transcription)
        
        self.assertIn("Processing error", str(context.exception))


if __name__ == "__main__":
    unittest.main()
