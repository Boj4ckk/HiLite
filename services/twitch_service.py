
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import requests
import logging
import os

load_dotenv()
class TwitchApi:
       
    """
    Handles Twitch API interactions for authentication, video fetching, and downloading.
    """

    BASE_URL = os.getenv("BASE_URL")
    logging.basicConfig(filename="app.log",  level=logging.DEBUG,format="%(asctime)s - %(levelname)s - %(message)s",  datefmt="%Y-%m-%d %H:%M:%S")

    def __init__(self, clientId, clientSecret):
        """
        Initialize TwitchApi instance and authenticate.

        :param clientId: Twitch application client ID.
        :param clientSecret: Twitch application client secret.
        """
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.accessToken = self.authenticate()
        self.headers = {
            "Client-Id": self.clientId,
            "Authorization": f"Bearer {self.accessToken}"
        }
    

    def authenticate(self):
        """
        Authenticate and get an app access token.

        :return: Access token as a string.
        """
        
        url = "https://id.twitch.tv/oauth2/token"
        payload = {
            "client_id": self.clientId,
            "client_secret": self.clientSecret,
            "grant_type": "client_credentials"
        }
        response = requests.post(url, data=payload)
        response.raise_for_status()
        token = response.json()["access_token"]
        logging.info("Successfully authenticated with Twitch API.")
        return token
    
    def get_broadcaster_id(self, username):
        """
        Fetch the user ID for a given Twitch username.

        :param username: Twitch username.
        :return: User ID as a string, or None if not found.
        """
        url = f"{self.BASE_URL}/users"
        params = {"login": username}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                return data[0]["id"]
        logging.error(f"Failed to fetch user ID for {username}: {response.text}")
        return None
    
    def get_broadcaster_clips(self, brodcaster_id, filters={"first":50}):
        """
        Fetch videos for a given Twitch user based on filters.

        :param userId: Twitch user ID.
        :param filters: Dictionary of filters (e.g., views, duration, started_at, ended_at).
                       If not provided, defaults to clips from the last 7 days.
        :return: List of video metadata dictionaries.
        """
        url = f"{self.BASE_URL}/clips"
        params = {"broadcaster_id": brodcaster_id}
        
        # Set default time window if no filters provided
        if filters.get("started_at") is None:
            ended_at = datetime.now(timezone.utc)
            started_at = ended_at - timedelta(days=7)
            filters = {

                "started_at": started_at.isoformat(),
                "ended_at": ended_at.isoformat()
            }
        
        params.update(filters)
        response = requests.get(url, headers=self.headers, params=params)
     
        if response.status_code == 200:
            return response.json().get("data", [])
        logging.error(f"Failed to fetch clip for broadcaster {brodcaster_id}: {response.text}")
        return []
    
    def get_game_info(self, game_id):
        """
        Fetch game information from Twitch API using the game ID.

        :param game_id: Twitch game ID.
        :return: Game info dict or None if not found.
        """
        url = f"{self.BASE_URL}/games"
        params = {"id": game_id}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                return data[0]
        logging.error(f"Failed to fetch game info for game_id {game_id}: {response.text}")
        return None
    
    def download_clips(self,broadcaster_id,clip_id,editor_id=""):

        url = f"{self.BASE_URL}/clips/downloads"
        params = {
            "broadcaster_id" : broadcaster_id,
            "editor_id": editor_id,
            "clip_id" : clip_id
        }
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json().get("data", [])
        logging.error(f"Failed to Download clip : {clip_id} for broadcaster {broadcaster_id}: {response.text}")
        return []
    
