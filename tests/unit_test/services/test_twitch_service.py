import pytest
from unittest.mock import patch, MagicMock
from services.twitch_service import TwitchService

def test_get_stream_info_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'data': [{'id': '123', 'title': 'Test Stream'}]}
    with patch('services.twitch_service.requests.get', return_value=mock_response):
        result = TwitchService.get_stream_info('channel', 'token')
        assert result == {'id': '123', 'title': 'Test Stream'}

def test_get_stream_info_not_found():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'data': []}
    with patch('services.twitch_service.requests.get', return_value=mock_response):
        with pytest.raises(ValueError) as excinfo:
            TwitchService.get_stream_info('channel', 'token')
        assert 'Stream not found' in str(excinfo.value)

def test_get_stream_info_api_error():
    mock_response = MagicMock()
    mock_response.status_code = 500
    with patch('services.twitch_service.requests.get', return_value=mock_response):
        with pytest.raises(Exception) as excinfo:
            TwitchService.get_stream_info('channel', 'token')
        assert 'API request failed' in str(excinfo.value)

@patch('services.twitch_service.TwitchService.get_stream_info')
def test_get_stream_title_integration(mock_get_info):
    mock_get_info.return_value = {'id': '123', 'title': 'Test Stream'}
    result = TwitchService.get_stream_title('channel', 'token')
    assert result == 'Test Stream'
    mock_get_info.assert_called_once_with('channel', 'token')
