from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration of the app"""

    # ============= SECRETS =============
    TWITCH_CLIENT_ID: str = "test_twitch_client_id"
    TWITCH_CLIENT_SECRET: str = "test_twitch_secret"

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

    # Youtube
    SCOPES: str = "https://www.googleapis.com/auth/youtube.upload"
    API_SERVICE_NAME: str = "youtube"
    API_VERSION: str = "v3"

    # Edit
    TITLES_TEMPLATE_PATH: str = "data/titles_template.json"
    SRT_DIR_PATH: str = "tmp/srt"
    EDITED_CLIP_FOLDER: str = "data/edited_clips"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """Load once then cached"""
    return Settings()


# Export settings
settings = get_settings()
