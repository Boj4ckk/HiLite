import unittest
from unittest.mock import MagicMock, patch
import os
from datetime import datetime, timezone, timedelta
import requests
from services.twitch_service import TwitchApi


class TestTwitchApi(unittest.TestCase):
    """Unit tests for TwitchApi class with mocked requests."""

    @patch.dict(os.environ, {'BASE_URL': 'https://api.twitch.tv/helix'})
    @patch('services.twitch_service.requests.post')
    def test_authenticate_success(self, mock_post):
        """Test successful authentication."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "test_token_123"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        api = TwitchApi("client_id", "client_secret")
        
        self.assertEqual(api.accessToken, "test_token_123")
        self.assertEqual(api.headers["Authorization"], "Bearer test_token_123")
        mock_post.assert_called_once()

    @patch.dict(os.environ, {'BASE_URL': 'https://api.twitch.tv/helix'})
    @patch('services.twitch_service.requests.post')
    def test_authenticate_timeout(self, mock_post):
        """Test authentication with timeout error."""
        mock_post.side_effect = requests.exceptions.Timeout()
        
        with self.assertRaises(Exception) as context:
            TwitchApi("client_id", "client_secret")
        
        self.assertIn("timeout", str(context.exception).lower())

    @patch.dict(os.environ, {'BASE_URL': 'https://api.twitch.tv/helix'})
    @patch('services.twitch_service.requests.post')
    def test_authenticate_connection_error(self, mock_post):
        """Test authentication with connection error."""
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        with self.assertRaises(Exception) as context:
            TwitchApi("client_id", "client_secret")
        
        self.assertIn("connect", str(context.exception).lower())

    @patch.dict(os.environ, {'BASE_URL': 'https://api.twitch.tv/helix'})
    @patch('services.twitch_service.requests.post')
    def test_authenticate_http_error(self, mock_post):
        """Test authentication with HTTP error."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
        mock_post.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            TwitchApi("client_id", "client_secret")
        
        self.assertIn("authentication failed", str(context.exception).lower())

    @patch.dict(os.environ, {'BASE_URL': 'https://api.twitch.tv/helix'})
    @patch('services.twitch_service.requests.post')
    def test_authenticate_missing_token(self, mock_post):
        """Test authentication when response doesn't contain access token."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "invalid_credentials"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        with self.assertRaises(ValueError) as context:
            TwitchApi("client_id", "client_secret")
        
        self.assertIn("authentication response", str(context.exception).lower())

    @patch.dict(os.environ, {'BASE_URL': 'https://api.twitch.tv/helix'})
    @patch('services.twitch_service.requests.post')
    @patch('services.twitch_service.requests.get')
    def test_get_broadcaster_id_success(self, mock_get, mock_post):
        """Test successful broadcaster ID retrieval."""
        # Mock authentication
        mock_auth_response = MagicMock()
        mock_auth_response.json.return_value = {"access_token": "test_token"}
        mock_auth_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_auth_response
        
        # Mock get_broadcaster_id
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = {"data": [{"id": "12345", "login": "testuser"}]}
        mock_get_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_get_response
        
        api = TwitchApi("client_id", "client_secret")
        result = api.get_broadcaster_id("testuser")
        
        self.assertEqual(result, "12345")
        mock_get.assert_called_once()

    @patch.dict(os.environ, {'BASE_URL': 'https://api.twitch.tv/helix'})
    @patch('services.twitch_service.requests.post')
    @patch('services.twitch_service.requests.get')
    def test_get_broadcaster_id_not_found(self, mock_get, mock_post):
        """Test broadcaster ID when user not found."""
        mock_auth_response = MagicMock()
        mock_auth_response.json.return_value = {"access_token": "test_token"}
        mock_auth_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_auth_response
        
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = {"data": []}
        mock_get_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_get_response
        
        api = TwitchApi("client_id", "client_secret")
        result = api.get_broadcaster_id("nonexistent_user")
        
        self.assertIsNone(result)

    @patch.dict(os.environ, {'BASE_URL': 'https://api.twitch.tv/helix'})
    @patch('services.twitch_service.requests.post')
    @patch('services.twitch_service.requests.get')
    def test_get_broadcaster_id_request_error(self, mock_get, mock_post):
        """Test broadcaster ID with request error."""
        mock_auth_response = MagicMock()
        mock_auth_response.json.return_value = {"access_token": "test_token"}
        mock_auth_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_auth_response
        
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        api = TwitchApi("client_id", "client_secret")
        result = api.get_broadcaster_id("testuser")
        
        self.assertIsNone(result)

    @patch.dict(os.environ, {'BASE_URL': 'https://api.twitch.tv/helix'})
    @patch('services.twitch_service.requests.post')
    @patch('services.twitch_service.requests.get')
    def test_get_broadcaster_clips_with_defaults(self, mock_get, mock_post):
        """Test getting clips with default time window."""
        mock_auth_response = MagicMock()
        mock_auth_response.json.return_value = {"access_token": "test_token"}
        mock_auth_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_auth_response
        
        mock_clips_response = MagicMock()
        mock_clips_response.json.return_value = {
            "data": [
                {"id": "clip1", "title": "Clip 1"},
                {"id": "clip2", "title": "Clip 2"}
            ]
        }
        mock_clips_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_clips_response
        
        api = TwitchApi("client_id", "client_secret")
        result = api.get_broadcaster_clips("broadcaster123")
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "clip1")

    @patch.dict(os.environ, {'BASE_URL': 'https://api.twitch.tv/helix'})
    @patch('services.twitch_service.requests.post')
    @patch('services.twitch_service.requests.get')
    def test_get_broadcaster_clips_with_custom_filters(self, mock_get, mock_post):
        """Test getting clips with custom filters."""
        mock_auth_response = MagicMock()
        mock_auth_response.json.return_value = {"access_token": "test_token"}
        mock_auth_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_auth_response
        
        mock_clips_response = MagicMock()
        mock_clips_response.json.return_value = {"data": []}
        mock_clips_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_clips_response
        
        api = TwitchApi("client_id", "client_secret")
        custom_filters = {
            "started_at": "2025-01-01T00:00:00Z",
            "ended_at": "2025-01-02T00:00:00Z",
            "first": 10
        }
        result = api.get_broadcaster_clips("broadcaster123", filters=custom_filters)
        
        self.assertEqual(result, [])
        # Verify filters were passed
        call_args = mock_get.call_args
        self.assertIn("started_at", call_args.kwargs['params'])

    @patch.dict(os.environ, {'BASE_URL': 'https://api.twitch.tv/helix'})
    @patch('services.twitch_service.requests.post')
    @patch('services.twitch_service.requests.get')
    def test_get_broadcaster_clips_request_error(self, mock_get, mock_post):
        """Test getting clips with request error."""
        mock_auth_response = MagicMock()
        mock_auth_response.json.return_value = {"access_token": "test_token"}
        mock_auth_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_auth_response
        
        mock_get.side_effect = requests.exceptions.RequestException("API error")
        
        api = TwitchApi("client_id", "client_secret")
        result = api.get_broadcaster_clips("broadcaster123")
        
        self.assertEqual(result, [])

    @patch.dict(os.environ, {'BASE_URL': 'https://api.twitch.tv/helix'})
    @patch('services.twitch_service.requests.post')
    @patch('services.twitch_service.requests.get')
    def test_get_game_info_success(self, mock_get, mock_post):
        """Test successful game info retrieval."""
        mock_auth_response = MagicMock()
        mock_auth_response.json.return_value = {"access_token": "test_token"}
        mock_auth_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_auth_response
        
        mock_game_response = MagicMock()
        mock_game_response.json.return_value = {
            "data": [{"id": "123", "name": "League of Legends"}]
        }
        mock_game_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_game_response
        
        api = TwitchApi("client_id", "client_secret")
        result = api.get_game_info("123")
        
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "League of Legends")

    @patch.dict(os.environ, {'BASE_URL': 'https://api.twitch.tv/helix'})
    @patch('services.twitch_service.requests.post')
    @patch('services.twitch_service.requests.get')
    def test_get_game_info_not_found(self, mock_get, mock_post):
        """Test game info when game not found."""
        mock_auth_response = MagicMock()
        mock_auth_response.json.return_value = {"access_token": "test_token"}
        mock_auth_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_auth_response
        
        mock_game_response = MagicMock()
        mock_game_response.json.return_value = {"data": []}
        mock_game_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_game_response
        
        api = TwitchApi("client_id", "client_secret")
        result = api.get_game_info("999999")
        
        self.assertIsNone(result)

    @patch.dict(os.environ, {'BASE_URL': 'https://api.twitch.tv/helix'})
    @patch('services.twitch_service.requests.post')
    @patch('services.twitch_service.requests.get')
    def test_get_game_info_request_error(self, mock_get, mock_post):
        """Test game info with request error."""
        mock_auth_response = MagicMock()
        mock_auth_response.json.return_value = {"access_token": "test_token"}
        mock_auth_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_auth_response
        
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        api = TwitchApi("client_id", "client_secret")
        result = api.get_game_info("123")
        
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
