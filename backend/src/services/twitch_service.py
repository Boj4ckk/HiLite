import logging
from datetime import datetime, timedelta, timezone

import httpx
import requests

from config.settings import settings

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
        self.BASE_URL = settings.BASE_URL
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = settings.TWITCH_SCOPES
    
        # Token management
        self._access_token = None
        self._token_expiry = None



    async def get_access_token(self) -> str:
        """
        Get valid access token, refreshing if necessary.
        
        :return: Valid access token
        """
        if self._access_token is None or datetime.now() >= self._token_expiry:
            await self._refresh_token()
        return self._access_token
    


    async def _refresh_token(self):
        """
        Authenticate and get a new app access token.
        """
        url = settings.TWITCH_TOKEN_URI
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        try:
            logger.info("Authenticating with Twitch API...")
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=payload, timeout=10)
                response.raise_for_status()

                data = response.json()
                if "access_token" not in data:
                    logger.error("Access token not found in Twitch API response")
                    raise ValueError("Invalid authentication response from Twitch")

                self._access_token = data["access_token"]
                # Token expires in ~60 days, but we refresh 1 hour before
                expires_in = data.get("expires_in", 5184000)  # Default 60 days
                self._token_expiry = datetime.now() + timedelta(seconds=expires_in - 3600)
                
                logger.info("Successfully authenticated with Twitch API")

        except httpx.TimeoutException:
            logger.error("Twitch authentication timeout")
            raise Exception("Twitch API timeout during authentication")
        except httpx.ConnectError as e:
            logger.error(f"Connection error during Twitch authentication: {e}")
            raise Exception(f"Failed to connect to Twitch API: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during Twitch authentication: {e}")
            raise Exception(f"Twitch authentication failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during Twitch authentication: {e}")
            raise
    
    async def get_headers(self):
        """Get headers with valid access token."""
        token = await self.get_access_token()
        return {
            "Client-Id": self.client_id,
            "Authorization": f"Bearer {token}",
        }

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

            response =  requests.get(
                url, headers={
                "Client-Id": self.client_id, "Authorization": f"Bearer {self._access_token}",}, params=params, timeout=10
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
                url, headers={
            "Client-Id": self.client_id,
            "Authorization": f"Bearer {self._access_token}",}, params=params, timeout=10
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
