import pytest
from unittest.mock import patch, MagicMock
from services.srt_service import SRTService

def test_parse_srt_success():
    srt_content = "1\n00:00:01,000 --> 00:00:02,000\nHello world\n"
    result = SRTService.parse_srt(srt_content)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]['text'] == 'Hello world'

def test_parse_srt_empty():
    result = SRTService.parse_srt("")
    assert result == []

def test_parse_srt_invalid_format():
    srt_content = "Invalid SRT"
    result = SRTService.parse_srt(srt_content)
    assert result == []

@patch('services.srt_service.SRTService.parse_srt')
def test_save_srt_file_success(mock_parse):
    mock_parse.return_value = [{'text': 'Hello world'}]
    with patch('builtins.open', new_callable=MagicMock) as mock_open:
        SRTService.save_srt_file('file.srt', 'content')
        mock_open.assert_called_once_with('file.srt', 'w', encoding='utf-8')

@patch('builtins.open', new_callable=MagicMock)
def test_save_srt_file_failure(mock_open):
    mock_open.side_effect = IOError('Failed to open file')
    with pytest.raises(IOError):
        SRTService.save_srt_file('file.srt', 'content')
