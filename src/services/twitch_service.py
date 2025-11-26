import logging
import os
from datetime import datetime, timedelta, timezone

import requests

logger = logging.getLogger("HiLiteLogger")


class TwitchApi:
    """
    Handles Twitch API interactions for authentication, video fetching, and downloading.
    """

    def __init__(self, client_id, client_secret):
        """
        Initialize TwitchApi instance and authenticate.

        :param client_id: Twitch application client ID.
        :param client_secret: Twitch application client secret.
        """
        self.BASE_URL = os.getenv("BASE_URL")
        self.client_id = client_id
        self.client_secret = client_secret
        self.accessToken = self.authenticate()
        self.headers = {
            "Client-Id": self.client_id,
            "Authorization": f"Bearer {self.accessToken}",
        }

    def authenticate(self):
        """
        Authenticate and get an app access token.

        :return: Access token as a string.
        :raises: Exception for authentication failures
        """
        url = "https://id.twitch.tv/oauth2/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        try:
            logger.info("Authenticating with Twitch API...")
            response = requests.post(url, data=payload, timeout=10)
            response.raise_for_status()

            data = response.json()
            if "access_token" not in data:
                logger.error("Access token not found in Twitch API response")
                raise ValueError("Invalid authentication response from Twitch")

            token = data["access_token"]
            logger.info("Successfully authenticated with Twitch API")
            return token

        except requests.exceptions.Timeout:
            logger.error("Twitch authentication timeout")
            raise Exception("Twitch API timeout during authentication")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error during Twitch authentication: {e}")
            raise Exception(f"Failed to connect to Twitch API: {e}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error during Twitch authentication: {e}")
            raise Exception(f"Twitch authentication failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during Twitch authentication: {e}")
            raise

    def get_broadcaster_id(self, username):
        """
        Fetch the user ID for a given Twitch username.

        :param username: Twitch username.
        :return: User ID as a string, or None if not found.
        """
        try:
            url = f"{self.BASE_URL}/users"
            params = {"login": username}
            logger.info(f"Fetching broadcaster ID for username: {username}")

            response = requests.get(
                url, headers=self.headers, params=params, timeout=10
            )
            response.raise_for_status()

            data = response.json().get("data", [])
            if data:
                broadcaster_id = data[0]["id"]
                logger.info(f"Found broadcaster ID: {broadcaster_id} for {username}")
                return broadcaster_id

            logger.warning(f"No user found for username: {username}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch user ID for {username}: {e}")
            return None

    def get_broadcaster_clips(self, brodcaster_id, filters={"first": 50}):
        """
        Fetch videos for a given Twitch user based on filters.

        :param brodcaster_id: Twitch user ID.
        :param filters: Dictionary of filters (e.g., views, duration, started_at, ended_at).
                       If not provided, defaults to clips from the last 7 days.
        :return: List of video metadata dictionaries.
        """
        try:
            url = f"{self.BASE_URL}/clips"
            params = {"broadcaster_id": brodcaster_id}

            # Set default time window if no filters provided
            if filters.get("started_at") is None:
                ended_at = datetime.now(timezone.utc)
                started_at = ended_at - timedelta(days=7)
                filters = {
                    "started_at": started_at.isoformat(),
                    "ended_at": ended_at.isoformat(),
                }

            params.update(filters)
            logger.info(f"Fetching clips for broadcaster {brodcaster_id}")

            response = requests.get(
                url, headers=self.headers, params=params, timeout=10
            )
            response.raise_for_status()

            clips = response.json().get("data", [])
            logger.info(f"Retrieved {len(clips)} clips for broadcaster {brodcaster_id}")
            return clips

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch clips for broadcaster {brodcaster_id}: {e}")
            return []

    def get_game_info(self, game_id):
        """
        Fetch game information from Twitch API using the game ID.

        :param game_id: Twitch game ID.
        :return: Game info dict or None if not found.
        """
        try:
            url = f"{self.BASE_URL}/games"
            params = {"id": game_id}
            logger.info(f"Fetching game info for game_id: {game_id}")

            response = requests.get(
                url, headers=self.headers, params=params, timeout=10
            )
            response.raise_for_status()

            data = response.json().get("data", [])
            if data:
                game_info = data[0]
                logger.info(f"Found game: {game_info.get('name')}")
                return game_info

            logger.warning(f"No game found for game_id: {game_id}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch game info for game_id {game_id}: {e}")
            return None

    def download_clips(self, broadcaster_id, clip_id, editor_id=""):
        url = f"{self.BASE_URL}/clips/downloads"
        params = {
            "broadcaster_id": broadcaster_id,
            "editor_id": editor_id,
            "clip_id": clip_id,
        }
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json().get("data", [])
        logging.error(
            f"Failed to Download clip : {clip_id} for broadcaster {broadcaster_id}: {response.text}"
        )
        return []
