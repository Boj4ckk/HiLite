import pytest
from unittest.mock import MagicMock, patch, mock_open
from buisness.subtitles_buisness import SubtitlesBuisness

def test_get_word_timings_basic():
    mock_sub = MagicMock()
    mock_sub.start.hours = 0
    mock_sub.start.minutes = 0
    mock_sub.start.seconds = 1
    mock_sub.start.milliseconds = 0
    mock_sub.end.hours = 0
    mock_sub.end.minutes = 0
    mock_sub.end.seconds = 2
    mock_sub.end.milliseconds = 0
    mock_sub.text = "Hello world"
    result = SubtitlesBuisness.get_word_timings_from_subtitle(mock_sub)
    assert len(result) == 2
    assert result[0][0] == "Hello"
    assert result[1][0] == "world"
    assert pytest.approx(result[0][1], 0.01) == 1.0
    assert pytest.approx(result[0][2], 0.01) == 1.5
    assert pytest.approx(result[1][1], 0.01) == 1.5
    assert pytest.approx(result[1][2], 0.01) == 2.0

def test_get_word_timings_empty_text():
    mock_sub = MagicMock()
    mock_sub.start.hours = 0
    mock_sub.start.minutes = 0
    mock_sub.start.seconds = 0
    mock_sub.start.milliseconds = 0
    mock_sub.end.hours = 0
    mock_sub.end.minutes = 0
    mock_sub.end.seconds = 1
    mock_sub.end.milliseconds = 0
    mock_sub.text = ""
    result = SubtitlesBuisness.get_word_timings_from_subtitle(mock_sub)
    assert result == []

def test_get_word_timings_single_word():
    mock_sub = MagicMock()
    mock_sub.start.hours = 0
    mock_sub.start.minutes = 0
    mock_sub.start.seconds = 0
    mock_sub.start.milliseconds = 500
    mock_sub.end.hours = 0
    mock_sub.end.minutes = 0
    mock_sub.end.seconds = 1
    mock_sub.end.milliseconds = 500
    mock_sub.text = "Test"
    result = SubtitlesBuisness.get_word_timings_from_subtitle(mock_sub)
    assert len(result) == 1
    assert result[0][0] == "Test"
    assert pytest.approx(result[0][1], 0.01) == 0.5
    assert pytest.approx(result[0][2], 0.01) == 1.5

def test_get_word_timings_with_milliseconds():
    mock_sub = MagicMock()
    mock_sub.start.hours = 0
    mock_sub.start.minutes = 0
    mock_sub.start.seconds = 0
    mock_sub.start.milliseconds = 250
    mock_sub.end.hours = 0
    mock_sub.end.minutes = 0
    mock_sub.end.seconds = 0
    mock_sub.end.milliseconds = 750
    mock_sub.text = "Quick test"
    result = SubtitlesBuisness.get_word_timings_from_subtitle(mock_sub)
    assert len(result) == 2
    assert pytest.approx(result[0][1], 0.01) == 0.25
    assert pytest.approx(result[0][2], 0.01) == 0.5
    assert pytest.approx(result[1][1], 0.01) == 0.5
    assert pytest.approx(result[1][2], 0.01) == 0.75

@patch('os.path.exists')
def test_generate_word_image_font_not_found(mock_exists):
    mock_exists.return_value = False
    with pytest.raises(FileNotFoundError) as excinfo:
        SubtitlesBuisness.generate_word_image(
            "Test",
            "nonexistent_font.ttf",
            60,
            (255, 255, 255, 255),
            (0, 0, 0, 255),
            3
        )
    assert "Font file not found" in str(excinfo.value)

def test_generate_word_image_empty_word():
    result = SubtitlesBuisness.generate_word_image(
        "",
        "font.ttf",
        60,
        (255, 255, 255, 255),
        (0, 0, 0, 255),
        3
    )
    assert result is None

def test_generate_word_image_whitespace_only():
    result = SubtitlesBuisness.generate_word_image(
        "   ",
        "font.ttf",
        60,
        (255, 255, 255, 255),
        (0, 0, 0, 255),
        3
    )
    assert result is None

@patch('os.path.exists')
@patch('buisness.subtitles_buisness.Image')
@patch('buisness.subtitles_buisness.ImageDraw')
@patch('buisness.subtitles_buisness.ImageFont')
def test_generate_word_image_success(mock_font, mock_draw, mock_image, mock_exists):
    mock_exists.return_value = True
    mock_img_instance = MagicMock()
    mock_image.new.return_value = mock_img_instance
    mock_draw_instance = MagicMock()
    mock_draw.Draw.return_value = mock_draw_instance
    mock_draw_instance.textbbox.return_value = (0, 0, 100, 50)
    mock_font_instance = MagicMock()
    mock_font.truetype.return_value = mock_font_instance
    result = SubtitlesBuisness.generate_word_image(
        "Test",
        "valid_font.ttf",
        60,
        (255, 255, 255, 255),
        (0, 0, 0, 255),
        3,
        img_path="test_word.png"
    )
    assert result == "test_word.png"
    mock_img_instance.save.assert_called_once_with("test_word.png")

@patch('os.makedirs')
@patch('buisness.subtitles_buisness.SubtitlesBuisness.get_word_timings_from_subtitle')
@patch('buisness.subtitles_buisness.SubtitlesBuisness.generate_word_image')
def test_generate_subtitle_images_empty_subs(mock_gen_img, mock_get_timings, mock_makedirs):
    result = SubtitlesBuisness.generate_subtitle_images(
        [],
        "font.ttf",
        60,
        (255, 255, 255, 255),
        (0, 0, 0, 255),
        3,
        "temp_dir"
    )
    assert result == []
    mock_makedirs.assert_called_once_with("temp_dir", exist_ok=True)

@patch('os.makedirs')
@patch('buisness.subtitles_buisness.SubtitlesBuisness.get_word_timings_from_subtitle')
@patch('buisness.subtitles_buisness.SubtitlesBuisness.generate_word_image')
def test_generate_subtitle_images_success(mock_gen_img, mock_get_timings, mock_makedirs):
    mock_get_timings.return_value = [
        ("Hello", 0.0, 0.5),
        ("world", 0.5, 1.0)
    ]
    mock_gen_img.side_effect = [
        "temp_dir\\sub0_word0.png",
        "temp_dir\\sub0_word1.png"
    ]
    mock_subs = [MagicMock()]
    result = SubtitlesBuisness.generate_subtitle_images(
        mock_subs,
        "font.ttf",
        60,
        (255, 255, 255, 255),
        (0, 0, 0, 255),
        3,
        "temp_dir"
    )
    assert len(result) == 2
    assert result[0] == ("temp_dir\\sub0_word0.png", 0.0, 0.5)
    assert result[1] == ("temp_dir\\sub0_word1.png", 0.5, 1.0)

@patch('os.path.exists')
def test_create_subtitled_video_video_not_found(mock_exists):
    mock_exists.return_value = False
    with pytest.raises(FileNotFoundError) as excinfo:
        SubtitlesBuisness.create_subtitled_video(
            "nonexistent.mp4",
            "subs.srt",
            "output.mp4",
            "font.ttf",
            60,
            (255, 255, 255, 255),
            (0, 0, 0, 255),
            3
        )
    assert "Video file not found" in str(excinfo.value)

@patch('os.path.exists')
def test_create_subtitled_video_srt_not_found(mock_exists):
    def exists_side_effect(path):
        if "video" in path:
            return True
        return False
    mock_exists.side_effect = exists_side_effect
    with pytest.raises(FileNotFoundError) as excinfo:
        SubtitlesBuisness.create_subtitled_video(
            "video.mp4",
            "nonexistent.srt",
            "output.mp4",
            "font.ttf",
            60,
            (255, 255, 255, 255),
            (0, 0, 0, 255),
            3
        )
    assert "SRT file not found" in str(excinfo.value)
