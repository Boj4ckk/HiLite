import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
from buisness.subtitles_buisness import SubtitlesBuisness


class TestSubtitlesBuisness(unittest.TestCase):
    """Unit tests for SubtitlesBuisness class."""

    def test_get_word_timings_basic(self):
        """Test word timing calculation for basic subtitle."""
        # Create mock subtitle
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
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], "Hello")
        self.assertEqual(result[1][0], "world")
        self.assertAlmostEqual(result[0][1], 1.0)  # Start time
        self.assertAlmostEqual(result[0][2], 1.5)  # End time
        self.assertAlmostEqual(result[1][1], 1.5)  # Start time
        self.assertAlmostEqual(result[1][2], 2.0)  # End time

    def test_get_word_timings_empty_text(self):
        """Test word timing with empty subtitle text."""
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
        
        self.assertEqual(result, [])

    def test_get_word_timings_single_word(self):
        """Test word timing with single word."""
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
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "Test")
        self.assertAlmostEqual(result[0][1], 0.5)
        self.assertAlmostEqual(result[0][2], 1.5)

    def test_get_word_timings_with_milliseconds(self):
        """Test word timing calculation with milliseconds."""
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
        
        self.assertEqual(len(result), 2)
        self.assertAlmostEqual(result[0][1], 0.25)
        self.assertAlmostEqual(result[0][2], 0.5)
        self.assertAlmostEqual(result[1][1], 0.5)
        self.assertAlmostEqual(result[1][2], 0.75)

    @patch('os.path.exists')
    def test_generate_word_image_font_not_found(self, mock_exists):
        """Test error when font file doesn't exist."""
        mock_exists.return_value = False
        
        with self.assertRaises(FileNotFoundError) as context:
            SubtitlesBuisness.generate_word_image(
                "Test",
                "nonexistent_font.ttf",
                60,
                (255, 255, 255, 255),
                (0, 0, 0, 255),
                3
            )
        
        self.assertIn("Font file not found", str(context.exception))

    def test_generate_word_image_empty_word(self):
        """Test that empty word returns None."""
        result = SubtitlesBuisness.generate_word_image(
            "",
            "font.ttf",
            60,
            (255, 255, 255, 255),
            (0, 0, 0, 255),
            3
        )
        
        self.assertIsNone(result)

    def test_generate_word_image_whitespace_only(self):
        """Test that whitespace-only word returns None."""
        result = SubtitlesBuisness.generate_word_image(
            "   ",
            "font.ttf",
            60,
            (255, 255, 255, 255),
            (0, 0, 0, 255),
            3
        )
        
        self.assertIsNone(result)

    @patch('os.path.exists')
    @patch('buisness.subtitles_buisness.Image')
    @patch('buisness.subtitles_buisness.ImageDraw')
    @patch('buisness.subtitles_buisness.ImageFont')
    def test_generate_word_image_success(self, mock_font, mock_draw, mock_image, mock_exists):
        """Test successful word image generation."""
        mock_exists.return_value = True
        
        # Setup mocks
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
        
        self.assertEqual(result, "test_word.png")
        mock_img_instance.save.assert_called_once_with("test_word.png")

    @patch('os.makedirs')
    @patch('buisness.subtitles_buisness.SubtitlesBuisness.get_word_timings_from_subtitle')
    @patch('buisness.subtitles_buisness.SubtitlesBuisness.generate_word_image')
    def test_generate_subtitle_images_empty_subs(self, mock_gen_img, mock_get_timings, mock_makedirs):
        """Test generate_subtitle_images with empty subtitle list."""
        result = SubtitlesBuisness.generate_subtitle_images(
            [],
            "font.ttf",
            60,
            (255, 255, 255, 255),
            (0, 0, 0, 255),
            3,
            "temp_dir"
        )
        
        self.assertEqual(result, [])
        mock_makedirs.assert_called_once_with("temp_dir", exist_ok=True)

    @patch('os.makedirs')
    @patch('buisness.subtitles_buisness.SubtitlesBuisness.get_word_timings_from_subtitle')
    @patch('buisness.subtitles_buisness.SubtitlesBuisness.generate_word_image')
    def test_generate_subtitle_images_success(self, mock_gen_img, mock_get_timings, mock_makedirs):
        """Test successful subtitle image generation."""
        # Mock word timings
        mock_get_timings.return_value = [
            ("Hello", 0.0, 0.5),
            ("world", 0.5, 1.0)
        ]
        
        # Mock image generation
        mock_gen_img.side_effect = ["img1.png", "img2.png"]
        
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
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("img1.png", 0.0, 0.5))
        self.assertEqual(result[1], ("img2.png", 0.5, 1.0))

    @patch('os.path.exists')
    def test_create_subtitled_video_video_not_found(self, mock_exists):
        """Test error when video file doesn't exist."""
        mock_exists.return_value = False
        
        with self.assertRaises(FileNotFoundError) as context:
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
        
        self.assertIn("Video file not found", str(context.exception))

    @patch('os.path.exists')
    def test_create_subtitled_video_srt_not_found(self, mock_exists):
        """Test error when SRT file doesn't exist."""
        def exists_side_effect(path):
            if "video" in path:
                return True
            return False
        
        mock_exists.side_effect = exists_side_effect
        
        with self.assertRaises(FileNotFoundError) as context:
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
        
        self.assertIn("SRT file not found", str(context.exception))


if __name__ == "__main__":
    unittest.main()
