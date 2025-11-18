
import os
from dotenv import load_dotenv
import google_auth_oauthlib.flow
import googleapiclient.discovery
import logging
from googleapiclient.http import MediaFileUpload

load_dotenv()
logger = logging.getLogger("HiLiteLogger")

class YoutubeService:
    """
    Service class for accessing the YouTube Data API using OAuth2 authentication.
    Handles authentication, API client initialization, and provides methods for search and channel data retrieval.
    """

    def __init__(self, client_secret,scopes,api_service_name,api_version):
        """
        Initialize the YouTube API client using OAuth2 credentials.
        Loads configuration from environment variables:
            - CLIENT_SECRET_FILE: Path to the OAuth2 client secrets file.
            - SCOPES: Comma-separated list of OAuth2 scopes.
            - API_SERVICE_NAME: Name of the YouTube API service.
            - API_VERSION: Version of the YouTube API.
        Raises:
            ValueError: If any required environment variable is missing.
            Exception: If authentication or client initialization fails.
        """

        self.client_secret = client_secret
        self.scopes = scopes
        self.api_service_name = api_service_name
        self.api_version = api_version


        try:
            # Start OAuth2 flow and build the YouTube API client
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                self.client_secret,
                self.scopes.split(","),
            )
            credentials = flow.run_local_server(port=8080)
            self.youtube_client = googleapiclient.discovery.build(
                self.api_service_name,
                self.api_version,
                credentials=credentials
            )
            logger.info("YouTube service initialized successfully.")
        except Exception as e:
            # Log initialization errors
            logger.error(f"Error while initializing YouTube service: {e}")
    

    def upload_video(self, file, title, description, tags, status):
        media = MediaFileUpload(file, chunksize=-1, resumable=True, mimetype="video/mp4")
        request = self.youtube_client.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                },
                "status": {
                    "privacyStatus": status  # "public", "private", "unlisted"
                }
            },
            media_body=media
        )
        response = request.execute()
        logger.info(f"Video uploaded successfully. Video ID: {response['id']}")
        return response["id"]