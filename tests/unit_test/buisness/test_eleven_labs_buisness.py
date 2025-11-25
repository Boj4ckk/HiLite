import pytest
from unittest.mock import patch, MagicMock, mock_open
from buisness.eleven_labs_buisness import ElevenLabsBuisness

@patch('buisness.eleven_labs_buisness.VideoFileClip')
@patch('buisness.eleven_labs_buisness.tempfile.NamedTemporaryFile')
@patch('builtins.open', new_callable=mock_open, read_data=b'fake_audio_data')
@patch('os.path.exists')
@patch('os.remove')
def test_extract_audio_bytes_success(mock_remove, mock_exists, mock_file, mock_tempfile, mock_video):
    mock_exists.return_value = True
    mock_temp = MagicMock()
    mock_temp.name = 'temp_audio.mp3'
    mock_tempfile.return_value = mock_temp

    mock_audio = MagicMock()
    mock_video_instance = MagicMock()
    mock_video_instance.audio = mock_audio
    mock_video_instance.duration = 10.5
    mock_video.return_value = mock_video_instance

    result = ElevenLabsBuisness.extract_audio_bytes_from_video('fake_video.mp4')
    assert result == b'fake_audio_data'
    mock_video.assert_called_once_with('fake_video.mp4')
    mock_audio.write_audiofile.assert_called_once()
    mock_video_instance.close.assert_called_once()
    mock_audio.close.assert_called_once()

@patch('os.path.exists')
def test_extract_audio_file_not_found(mock_exists):
    mock_exists.return_value = False
    with pytest.raises(FileNotFoundError) as excinfo:
        ElevenLabsBuisness.extract_audio_bytes_from_video('nonexistent.mp4')
    assert "Video file not found" in str(excinfo.value)

@patch('buisness.eleven_labs_buisness.VideoFileClip')
@patch('os.path.exists')
def test_extract_audio_no_audio_track(mock_exists, mock_video):
    mock_exists.return_value = True
    mock_video_instance = MagicMock()
    mock_video_instance.audio = None
    mock_video.return_value = mock_video_instance
    with pytest.raises(ValueError) as excinfo:
        ElevenLabsBuisness.extract_audio_bytes_from_video('video_no_audio.mp4')
    assert "no audio track" in str(excinfo.value)
    mock_video_instance.close.assert_called_once()

@patch('buisness.eleven_labs_buisness.VideoFileClip')
@patch('buisness.eleven_labs_buisness.tempfile.NamedTemporaryFile')
@patch('os.path.exists')
@patch('os.remove')
def test_extract_audio_cleanup_on_error(mock_remove, mock_exists, mock_tempfile, mock_video):
    mock_exists.return_value = True
    mock_temp = MagicMock()
    mock_temp.name = 'temp_audio.mp3'
    mock_tempfile.return_value = mock_temp
    mock_audio = MagicMock()
    mock_audio.write_audiofile.side_effect = Exception("Write error")
    mock_video_instance = MagicMock()
    mock_video_instance.audio = mock_audio
    mock_video.return_value = mock_video_instance
    with pytest.raises(Exception):
        ElevenLabsBuisness.extract_audio_bytes_from_video('video.mp4')
    mock_video_instance.close.assert_called_once()
    mock_audio.close.assert_called_once()

@patch('buisness.eleven_labs_buisness.VideoFileClip')
@patch('buisness.eleven_labs_buisness.tempfile.NamedTemporaryFile')
@patch('builtins.open', new_callable=mock_open, read_data=b'test_audio')
@patch('os.path.exists')
@patch('os.remove')
def test_extract_audio_returns_correct_bytes(mock_remove, mock_exists, mock_file, mock_tempfile, mock_video):
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
    assert isinstance(result, bytes)
    assert result == b'test_audio'
