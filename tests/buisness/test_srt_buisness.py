import unittest
from buisness.srt_buisness import SrtBuisness


class TestSrtBuisness(unittest.TestCase):
    """Unit tests for SrtBuisness class."""

    def test_seconds_to_srt_time_zero(self):
        """Test conversion of 0 seconds."""
        result = SrtBuisness.seconds_to_srt_time(0)
        self.assertEqual(result, "00:00:00,000")

    def test_seconds_to_srt_time_basic(self):
        """Test conversion of basic time values."""
        result = SrtBuisness.seconds_to_srt_time(65.5)
        self.assertEqual(result, "00:01:05,500")

    def test_seconds_to_srt_time_with_hours(self):
        """Test conversion with hours."""
        result = SrtBuisness.seconds_to_srt_time(3661.250)
        self.assertEqual(result, "01:01:01,250")

    def test_seconds_to_srt_time_with_milliseconds(self):
        """Test conversion with precise milliseconds."""
        result = SrtBuisness.seconds_to_srt_time(1.999)
        self.assertEqual(result, "00:00:01,999")

    def test_seconds_to_srt_time_large_value(self):
        """Test conversion of large time value."""
        result = SrtBuisness.seconds_to_srt_time(7322.125)
        self.assertEqual(result, "02:02:02,125")

    def test_transcription_to_srt_lines_empty_list(self):
        """Test with empty word list."""
        result = SrtBuisness.transcription_to_srt_lines([])
        self.assertEqual(result, [])

    def test_transcription_to_srt_lines_single_word(self):
        """Test with single word."""
        class MockWord:
            def __init__(self, text, start, end):
                self.text = text
                self.start = start
                self.end = end

        words = [MockWord("Hello", 0.0, 0.5)]
        result = SrtBuisness.transcription_to_srt_lines(words)
        
        self.assertEqual(len(result), 1)
        self.assertIn("1\n", result[0])
        self.assertIn("00:00:00,000 --> 00:00:00,500\n", result[0])
        self.assertIn("Hello\n", result[0])

    def test_transcription_to_srt_lines_multiple_words(self):
        """Test with multiple words."""
        class MockWord:
            def __init__(self, text, start, end):
                self.text = text
                self.start = start
                self.end = end

        words = [
            MockWord("Hello", 0.0, 0.5),
            MockWord("world", 0.5, 1.0),
            MockWord("test", 1.0, 1.5)
        ]
        result = SrtBuisness.transcription_to_srt_lines(words)
        
        self.assertEqual(len(result), 3)
        
        # Check first line
        self.assertIn("1\n", result[0])
        self.assertIn("00:00:00,000 --> 00:00:00,500\n", result[0])
        self.assertIn("Hello\n", result[0])
        
        # Check second line
        self.assertIn("2\n", result[1])
        self.assertIn("00:00:00,500 --> 00:00:01,000\n", result[1])
        self.assertIn("world\n", result[1])
        
        # Check third line
        self.assertIn("3\n", result[2])
        self.assertIn("00:00:01,000 --> 00:00:01,500\n", result[2])
        self.assertIn("test\n", result[2])

    def test_transcription_to_srt_lines_with_long_timings(self):
        """Test with longer timing values (hours)."""
        class MockWord:
            def __init__(self, text, start, end):
                self.text = text
                self.start = start
                self.end = end

        words = [MockWord("Long", 3600.0, 3600.5)]
        result = SrtBuisness.transcription_to_srt_lines(words)
        
        self.assertEqual(len(result), 1)
        self.assertIn("01:00:00,000 --> 01:00:00,500\n", result[0])


if __name__ == "__main__":
    unittest.main()
