import unittest
from unittest.mock import MagicMock, patch, mock_open
import json
import os
from buisness.twitch_buisness import TwitchBuisness


class TestTwitchBuisness(unittest.TestCase):
    """Unit tests for TwitchBuisness class."""

    def test_extract_clips_ids_empty(self):
        """Test extracting clip IDs from empty list."""
        result = TwitchBuisness.extract_clips_ids([])
        self.assertEqual(result, [])

    def test_extract_clips_ids_single(self):
        """Test extracting clip IDs from single clip."""
        clips = [{"id": "clip123", "title": "Test Clip"}]
        result = TwitchBuisness.extract_clips_ids(clips)
        self.assertEqual(result, ["clip123"])

    def test_extract_clips_ids_multiple(self):
        """Test extracting clip IDs from multiple clips."""
        clips = [
            {"id": "clip1", "title": "Clip 1"},
            {"id": "clip2", "title": "Clip 2"},
            {"id": "clip3", "title": "Clip 3"}
        ]
        result = TwitchBuisness.extract_clips_ids(clips)
        self.assertEqual(result, ["clip1", "clip2", "clip3"])

    def test_extract_clips_url_empty(self):
        """Test extracting clip URLs from empty list."""
        result = TwitchBuisness.extract_clips_url([])
        self.assertEqual(result, [])

    def test_extract_clips_url_single(self):
        """Test extracting clip URLs from single clip."""
        clips = [{"url": "https://clips.twitch.tv/clip1", "id": "clip1"}]
        result = TwitchBuisness.extract_clips_url(clips)
        self.assertEqual(result, ["https://clips.twitch.tv/clip1"])

    def test_extract_clips_url_multiple(self):
        """Test extracting clip URLs from multiple clips."""
        clips = [
            {"url": "https://clips.twitch.tv/clip1"},
            {"url": "https://clips.twitch.tv/clip2"},
            {"url": "https://clips.twitch.tv/clip3"}
        ]
        result = TwitchBuisness.extract_clips_url(clips)
        self.assertEqual(result, [
            "https://clips.twitch.tv/clip1",
            "https://clips.twitch.tv/clip2",
            "https://clips.twitch.tv/clip3"
        ])

    @patch.dict(os.environ, {'TITLES_TEMPLATE_PATH': ''})
    def test_generate_short_title_no_env_var(self):
        """Test generate_short_title when env var is not set."""
        mock_service = MagicMock()
        clip = {"broadcaster_name": "TestStreamer", "title": "Epic Play", "game_id": "123"}
        
        result = TwitchBuisness.generate_short_title(mock_service, clip)
        self.assertIsNone(result)

    @patch.dict(os.environ, {'TITLES_TEMPLATE_PATH': 'nonexistent.json'})
    @patch('os.path.exists')
    def test_generate_short_title_file_not_found(self, mock_exists):
        """Test generate_short_title when template file doesn't exist."""
        mock_exists.return_value = False
        mock_service = MagicMock()
        clip = {"broadcaster_name": "TestStreamer", "title": "Epic Play", "game_id": "123"}
        
        result = TwitchBuisness.generate_short_title(mock_service, clip)
        self.assertIsNone(result)

    @patch.dict(os.environ, {'TITLES_TEMPLATE_PATH': 'templates.json'})
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    def test_generate_short_title_invalid_json(self, mock_file, mock_exists):
        """Test generate_short_title with invalid JSON file."""
        mock_exists.return_value = True
        mock_service = MagicMock()
        clip = {"broadcaster_name": "TestStreamer", "title": "Epic Play", "game_id": "123"}
        
        result = TwitchBuisness.generate_short_title(mock_service, clip)
        self.assertIsNone(result)

    @patch.dict(os.environ, {'TITLES_TEMPLATE_PATH': 'templates.json'})
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"templates": []}')
    def test_generate_short_title_empty_templates(self, mock_file, mock_exists):
        """Test generate_short_title with empty templates list."""
        mock_exists.return_value = True
        mock_service = MagicMock()
        clip = {"broadcaster_name": "TestStreamer", "title": "Epic Play", "game_id": "123"}
        
        result = TwitchBuisness.generate_short_title(mock_service, clip)
        self.assertIsNone(result)

    @patch.dict(os.environ, {'TITLES_TEMPLATE_PATH': 'templates.json'})
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('random.choice')
    def test_generate_short_title_success(self, mock_random, mock_file, mock_exists):
        """Test successful title generation."""
        mock_exists.return_value = True
        
        # Mock file content
        template_data = {
            "templates": [
                "{broadcaster_name} | {game} - {clip_title}"
            ]
        }
        mock_file.return_value.read.return_value = json.dumps(template_data)
        mock_random.return_value = "{broadcaster_name} | {game} - {clip_title}"
        
        # Mock service
        mock_service = MagicMock()
        mock_service.get_game_info.return_value = {"name": "League of Legends"}
        
        clip = {
            "broadcaster_name": "TestStreamer",
            "title": "Epic Play",
            "game_id": "123"
        }
        
        result = TwitchBuisness.generate_short_title(mock_service, clip)
        
        self.assertIsNotNone(result)
        self.assertIn("TestStreamer", result)
        self.assertIn("League of Legends", result)
        self.assertIn("Epic Play", result)

    @patch.dict(os.environ, {'TITLES_TEMPLATE_PATH': 'templates.json'})
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('random.choice')
    def test_generate_short_title_game_not_found(self, mock_random, mock_file, mock_exists):
        """Test title generation when game info is not found."""
        mock_exists.return_value = True
        
        template_data = {
            "templates": [
                "{broadcaster_name} - {clip_title}"
            ]
        }
        mock_file.return_value.read.return_value = json.dumps(template_data)
        mock_random.return_value = "{broadcaster_name} - {clip_title}"
        
        # Mock service returns None for game info
        mock_service = MagicMock()
        mock_service.get_game_info.return_value = None
        
        clip = {
            "broadcaster_name": "TestStreamer",
            "title": "Epic Play",
            "game_id": "999"
        }
        
        result = TwitchBuisness.generate_short_title(mock_service, clip)
        
        self.assertIsNotNone(result)
        self.assertIn("TestStreamer", result)
        self.assertIn("Epic Play", result)


if __name__ == "__main__":
    unittest.main()
