import logging
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload

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
        self.scopes = scopes or os.getenv("SCOPES")
        self.api_service_name = api_service_name or os.getenv("API_SERVICE_NAME")
        self.api_version = api_version or os.getenv("API_VERSION")

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

        self.client_secret = client_secret
        self.port = port

        try:
            logger.info("Initializing YouTube service...")
            # Start OAuth2 flow and build the YouTube API client
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                self.client_secret,
                self.scopes.split(","),
            )

            # Try to run local server, retry with different port if occupied
            try:
                credentials = flow.run_local_server(port=self.port)
            except OSError as e:
                if (
                    "Address already in use" in str(e)
                    or "WinError 10048" in str(e)
                    or "WinError 10013" in str(e)
                ):
                    logger.warning(
                        f"Port {self.port} is occupied, trying port {self.port + 1}"
                    )
                    credentials = flow.run_local_server(port=self.port + 1)
                else:
                    raise

            self.youtube_client = googleapiclient.discovery.build(
                self.api_service_name, self.api_version, credentials=credentials
            )
            logger.info("YouTube service initialized successfully")

        except FileNotFoundError:
            raise
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error while initializing YouTube service: {e}")
            raise Exception(f"Failed to initialize YouTube service: {e}") from e

    def upload_video(self, file, title, description, tags, status):
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
            logger.info(f"Starting upload of video: {file}")
            logger.info(f"Title: {title}, Status: {status}")

            media = MediaFileUpload(
                file, chunksize=-1, resumable=True, mimetype="video/mp4"
            )
            request = self.youtube_client.videos().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": title,
                        "description": description,
                        "tags": tags,
                    },
                    "status": {"privacyStatus": status},
                },
                media_body=media,
            )

            response = request.execute()

            if "id" not in response:
                logger.error("Video ID not found in upload response")
                raise ValueError("Invalid upload response from YouTube")

            video_id = response["id"]
            logger.info(f"Video uploaded successfully. Video ID: {video_id}")
            return video_id

        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to upload video: {e}")
            raise Exception(f"YouTube upload failed: {e}") from e
