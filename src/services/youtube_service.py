import logging
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from config.path_config import BASE_DIR

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
        

        # Token file path
        token_path = os.getenv("YT_TOKEN_PATH")
        if not token_path:
            raise ValueError("YT_TOKEN_PATH environment variable not set")

        self.token = os.path.join(BASE_DIR,token_path)

        token_dir = os.path.dirname(self.token) #dir of the file
        os.makedirs(token_dir, exist_ok=True)
        logger.info(f"Token will be saved to {self.token}")


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
            # Start OAuth2 flow get credentials and build the YouTube API client
            credentials = self._get_credentials()

            # Create youtube client
            self.youtube_client = googleapiclient.discovery.build(
                self.api_service_name, 
                self.api_version, 
                credentials=credentials
            )
            logger.info("YouTube service initialized successfully")

        except FileNotFoundError:
            raise
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error while initializing YouTube service: {e}")
            raise Exception(f"Failed to initialize YouTube service: {e}") from e


    def _get_credentials(self):
        """
        Get valid credentials, refreshing or requesting new auth if needed.
        
        Returns:
            Credentials: Valid OAuth2 credentials with refresh token
            
        Raises:
            Exception: If authentication fails
        """
        credentials = None

        # Load existing credentials if available
        if os.path.exists(self.token):
            try:
                credentials = Credentials.from_authorized_user_file(
                    self.token,
                    self.scopes.split(",")
                )
                logger.info("Loaded existing credntials from token file")
            except Exception as e:
                logger.warning(f"Failed to load credentials: {e}")
        
        # Refresh if token is expired but refresh token is available
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                logger.info("Token expired, refreshing...")
                credentials.refresh(Request()) # Refresh token

                # Save refreshed token
                with open(self.token, "w") as f:
                    f.write(credentials.to_json())
                logger.info("Token refreshed successfully")

                return credentials
            except Exception as e:
                logger.error(f"Failed to refresh token: {e}")
                credentials = None
        
        # Need fisrt/new auth
        if not credentials or not credentials.valid:
            logger.info("Starting OAuth2 flow for new credentials...")

            try:
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    self.client_secret,
                    self.scopes.split(","),
                )
                flow.oauth2session.redirect_uri = f"http://localhost:/{self.port}/"

                auth_url, _ = flow.authorization_url(
                    access_type="offline",
                    prompt="consent",
                    include_granted_scopes="true"
                )

                logger.info("Opening brower for authorization")

                # Starting local server
                try:
                    credentials = flow.run_local_server(
                        port=self.port,
                        open_browser=True
                    )
                except OSError as e:
                    if(
                        "Adress already is use" in str(e)
                        or "WinError 10048" in (e)
                        or "WinErro 10013 in" in (e)
                    ):
                        logger.warning(
                            f"Port {self.port} is occupied, tryping port {self.port + 1}"
                        )
                        credentials = flow.run_local_server(
                            port=self.port + 1,
                            open_browser=True
                        )
                    else:
                        raise
                
                if not credentials.refresh_token:
                    logger.warning(
                        "       No refresh_token received! This can happen if:\n"
                        "   1. User already authorized this app before\n"
                        "   2. Previous token still exists\n"
                        "   Solution: Revoke access at https://myaccount.google.com/permissions\n"
                        "   Then delete token.json and try again."
                    )
                else:
                    logger.info("Refresh token obtained successfully")
                
                with open(self.token, "w") as f:
                    f.write(credentials.to_json())
                logger.info(f"Credentials saved to {self.token}")
            except Exception as e:
                logger.error(f"OAuth flow failed: {e}")
        return credentials
        







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
