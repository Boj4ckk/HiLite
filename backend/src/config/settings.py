from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration of the app"""

    # ============= SECRETS =============
    TWITCH_CLIENT_ID: str = "test_twitch_client_id"
    TWITCH_CLIENT_SECRET: str = "test_twitch_secret"
    TWITCH_EVENTSUB_SECRET: str = (
        "c5b83f91d1d8e910ac8698abfae45d2388a6dfef2b2f3d0dce8cb85a3edfb0a1"
    )

    CLIENT_ID: str = "test_youtube_client_id"
    CLIENT_SECRET_FILE: str = "tests/fixtures/client_secret.json"
    YT_TOKEN_PATH: str = "tests/fixtures/youtube_token.json"

    ELEVENLABS_API_KEY: str = "test_elevenlabs_key"

    SUPABASE_API_KEY: str = "test_supabase_key"
    SUPABASE_URL: str = "test_password"
    # ============= Buisness Conf =============
    # Twitch
    BASE_URL: str = "https://api.twitch.tv/helix"
    TWITCH_CLIP_FOLDER_PATH: str = "data/twitch_clips"
    TWITCH_CLIP_BLACKLIST_PATH: str = "data/clip_blacklist.csv"

    TWITCH_OAUTH2_VALIDATE: str = "https://id.twitch.tv/oauth2/validate"
    TWITCH_OAUTH2_URL: str = "https://id.twitch.tv/oauth2/authorize"
    TWITCH_TOKEN_URI: str = "https://id.twitch.tv/oauth2/token"
    TWITCH_SCOPES: str = "user:read:email+clips:edit"
    TWITCH_CALLBACK_URL: str = "http://localhost:8000/auth/callback/twitch"

    TWITCH_EVENTSUB_URL: str = "https://api.twitch.tv/helix/eventsub/subscriptions"

    # Youtube
    SCOPES: str = "https://www.googleapis.com/auth/youtube.upload"
    API_SERVICE_NAME: str = "youtube"
    API_VERSION: str = "v3"

    YOUTUBE_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    YOUTUBE_SERVER_PORT: str = "8081"
    YOUTUBE_REDIRECT_URI: str = f"http://localhost:{YOUTUBE_SERVER_PORT}/"

    # Edit
    TITLES_TEMPLATE_PATH: str = "data/titles_template.json"
    SRT_DIR_PATH: str = "tmp/srt"
    EDITED_CLIP_FOLDER: str = "data/edited_clips"

    # CORS
    BACKEND_URL: str = "http://localhost:8000"

    CORS_ALLOWED_ORIGINS: str = "https://hilite-frontend.onrender.com"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """Load once then cached"""
    return Settings()


# Export settings
settings = get_settings()
