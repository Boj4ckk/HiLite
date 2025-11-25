import pytest
from buisness.srt_buisness import SrtBuisness

def test_seconds_to_srt_time_zero():
    result = SrtBuisness.seconds_to_srt_time(0)
    assert result == "00:00:00,000"

def test_seconds_to_srt_time_basic():
    result = SrtBuisness.seconds_to_srt_time(65.5)
    assert result == "00:01:05,500"

def test_seconds_to_srt_time_with_hours():
    result = SrtBuisness.seconds_to_srt_time(3661.250)
    assert result == "01:01:01,250"

def test_seconds_to_srt_time_with_milliseconds():
    result = SrtBuisness.seconds_to_srt_time(1.999)
    assert result == "00:00:01,999"

def test_seconds_to_srt_time_large_value():
    result = SrtBuisness.seconds_to_srt_time(7322.125)
    assert result == "02:02:02,125"

def test_transcription_to_srt_lines_empty_list():
    result = SrtBuisness.transcription_to_srt_lines([])
    assert result == []

def test_transcription_to_srt_lines_single_word():
    class MockWord:
        def __init__(self, text, start, end):
            self.text = text
            self.start = start
            self.end = end
    words = [MockWord("Hello", 0.0, 0.5)]
    result = SrtBuisness.transcription_to_srt_lines(words)
    assert len(result) == 1
    assert "1\n" in result[0]
    assert "00:00:00,000 --> 00:00:00,500\n" in result[0]
    assert "Hello\n" in result[0]

def test_transcription_to_srt_lines_multiple_words():
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
    assert len(result) == 3
    assert "1\n" in result[0]
    assert "00:00:00,000 --> 00:00:00,500\n" in result[0]
    assert "Hello\n" in result[0]
    assert "2\n" in result[1]
    assert "00:00:00,500 --> 00:00:01,000\n" in result[1]
    assert "world\n" in result[1]
    assert "3\n" in result[2]
    assert "00:00:01,000 --> 00:00:01,500\n" in result[2]
    assert "test\n" in result[2]

def test_transcription_to_srt_lines_with_long_timings():
    class MockWord:
        def __init__(self, text, start, end):
            self.text = text
            self.start = start
            self.end = end
    words = [MockWord("Long", 3600.0, 3600.5)]
    result = SrtBuisness.transcription_to_srt_lines(words)
    assert len(result) == 1
    assert "01:00:00,000 --> 01:00:00,500\n" in result[0]
