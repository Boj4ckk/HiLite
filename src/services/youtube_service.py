import logging
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

from config.settings import settings

logger = logging.getLogger("HiLiteLogger")


class YoutubeService:
    """
    Service class for accessing the YouTube Data API using OAuth2 authentication.
    Handles authentication, API client initialization, and provides methods for search and channel data retrieval.
    """

    def __init__(
        self,
        client_secret,
        scopes=None,
        api_service_name=None,
        api_version=None,
        port=8081,
    ):
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
        # Load from env if not provided
        self.scopes = scopes or settings.SCOPES
        self.api_service_name = api_service_name or settings.API_SERVICE_NAME
        self.api_version = api_version or settings.API_VERSION
        self.client_secret = client_secret
        self.port = settings.YOUTUBE_SERVER_PORT

        # Validate required parameters
        if not client_secret:
            raise ValueError("client_secret is required")
        if not self.scopes:
            raise ValueError("SCOPES environment variable is not set")
        if not self.api_service_name:
            raise ValueError("API_SERVICE_NAME environment variable is not set")
        if not self.api_version:
            raise ValueError("API_VERSION environment variable is not set")
        if not os.path.exists(client_secret):
            raise FileNotFoundError(f"Client secret file not found: {client_secret}")

        logger.info("Youtube service configuration loaded")

    def get_client(
        self, access_token, refresh_token=None
    ):  # return list youtube client , credentials
        """
        Create an authenticated YouTube client using the provided tokens.
        Automatically refreshes the token if it is expired.

        Args:
        access_token: OAuth2 access token
        refresh_token: Refresh token (optional)

        Returns:
        tuple: (youtube_client, credentials)
        - youtube_client: Authenticated YouTube API client
        - credentials: Credentials object (possibly refreshed)

        Raises:
        Exception: If creating the client fails
        """

        try:
            credentials = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri=settings.YOUTUBE_TOKEN_URI,
                client_id=settings.CLIENT_ID,
                client_secret=self.client_secret,
                scopes=self.scopes.split(","),
            )

            # Refresh if expired and refresh available
            if credentials.expired and credentials.refresh_token:
                logger.info("Token expired, refreshing...")
                credentials.refresh(Request())
                logger.info("Token refreshed successfully")

            youtube_client = googleapiclient.discovery.build(
                self.api_service_name, self.api_version, credentials=credentials
            )

            return youtube_client, credentials

        except Exception as e:
            logger.error(f"Failed to create YouTube client: {e}")
            raise

    def authentificate_new_user(self):
        try:
            logger.info("Starting Oauth2 flow for new user...")

            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                self.client_secret,
                self.scopes.split(","),
            )
            flow.oauth2session.redirect_uri = settings.YOUTUBE_REDIRECT_URI
            auth_url, _ = flow.authorization_url(
                access_type="offline", prompt="consent", include_granted_scopes="true"
            )

            try:
                credentials = flow.run_local_server(port=self.port, open_browser=True)
            except OSError as e:
                if (
                    "Address already in use" in str(e)
                    or "WinError 10048" in str(e)
                    or "WinError 10013" in str(e)
                ):
                    logger.warning(f"Port {self.port} occupied, trying {self.port + 1}")
                    credentials = flow.run_local_server(
                        port=self.port + 1, open_browser=True
                    )
                else:
                    raise

            if not credentials.refresh_token:
                logger.error(
                    "No refresh_token received! This can happen if:\n"
                    "   1. User already authorized this app before\n"
                    "   2. Previous token still exists\n"
                    "   Solution: Revoke access at https://myaccount.google.com/permissions"
                )
                raise ValueError("No refresh token received from Google OAuth")

            logger.info("Authentication successful, tokens received")

            return {
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
            }

        except Exception as e:
            logger.error(f"OAuth flow failed: {e}")
            raise

    def upload_video(self, youtube_client, file, title, description, tags, pusblish_at):
        """
        Upload a video to YouTube.

        Args:
            file: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            status: Privacy status ('public', 'private', 'unlisted')

        Returns:
            str: Video ID of uploaded video

        Raises:
            FileNotFoundError: If video file doesn't exist
            Exception: For upload errors
        """
        if not os.path.exists(file):
            raise FileNotFoundError(f"Video file not found: {file}")

        try:
            logger.info(f"Sheduling the upload of video: {file}")

            media = MediaFileUpload(
                file, chunksize=-1, resumable=True, mimetype="video/mp4"
            )
            # The youtube client resource should expose `videos().insert(...)`
            # when created with `googleapiclient.discovery.build(...)`.
            try:
                videos_resource = youtube_client.videos()
            except Exception:
                raise TypeError(
                    "youtube_client does not appear to be a valid YouTube resource"
                )

            request = videos_resource.insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": title,
                        "description": description,
                        "tags": tags,
                    },
                    "status": {"privacyStatus": "private", "publishAt": pusblish_at},
                },
                media_body=media,
            )

            response = request.execute()

            if "id" not in response:
                logger.error("Video ID not found in upload response")
                raise ValueError("Invalid upload response from YouTube")

            video_id = response["id"]
            logger.info(f"Video: {video_id} will be uploaded at {pusblish_at}. ")
            return video_id

        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to shedule the upload: {e}")
            raise Exception(f"YouTube shedule upload failed: {e}") from e
