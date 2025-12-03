from datetime import datetime, timedelta

from config.logger_conf import setup_logger
from models.dto.dto_twitch_token_model import TwitchTokensRequest
from models.twitch_token_model import TwitchTokens
from models.user_model import User
from repositories.twitch_token_repository import TwitchTokenRepository
from services.supabase_service import SupaBase
from services.twitch_service import TwitchApi

logger = setup_logger()


class TwitchTokensBusiness:
    def __init__(
        self, supabase: SupaBase, twitch_token_repository: TwitchTokenRepository
    ):
        self.supabase = supabase
        self.twitch_token_repository = twitch_token_repository

    def asign_access_token(
        self,
        twitch_api: TwitchApi,
        twitch_tokens_request: TwitchTokensRequest,
        current_user: User,
    ):
        access_token = twitch_tokens_request.twitch_access_token
        refresh_token = twitch_tokens_request.twitch_refresh_token
        user_id = current_user.id

        is_token_valid_response = twitch_api.is_token_valid(access_token)
        valid = is_token_valid_response["valid"]
        expires_in = is_token_valid_response["expires_in"]

        # Case where user don't have token yet (first conn)
        if not valid:
            logger.error(
                f"Invalid twitch access token for user : {current_user.username} "
            )
            return False

        now = datetime.utcnow()
        expire_date = now + timedelta(seconds=expires_in)

        data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expire_date": expire_date,
            "user_id": user_id,
        }

        twitch_token_data = TwitchTokens(**data)
        response = self.twitch_token_repository.create_or_update(twitch_token_data)
        return response


def get_valid_access_token(self, twitch_api: TwitchApi, user_id: str) -> str | None:
    row = self.twitch_token_repository.get_by_user_id(user_id)
    if not row:
        logger.error("No Twitch tokens found for user %s", user_id)
        return None

    access_token = row.get("access_token")
    refresh_token = row.get("refresh_token")
    expires_date = row.get("expire_date")

    now = datetime.utcnow()

    if expires_date and expires_date > now:
        return access_token

    if not refresh_token:
        logger.error("No refresh_token stored for user %s", user_id)
        return None

    response = twitch_api.refresh_access_token(refresh_token)
    data = response.json()

    new_access_token = data.get("access_token")
    new_refresh_token = data.get("refresh_token") or refresh_token

    if not new_access_token:
        logger.error("No access_token in Twitch refresh response for user %s", user_id)
        return None

    is_token_valid_response = twitch_api.is_token_valid(new_access_token)
    if not is_token_valid_response.get("valid"):
        logger.info("The refreshed token is not valid for user %s", user_id)
        return None

    expires_in = is_token_valid_response.get("expires_in")
    expire_date = now + timedelta(seconds=expires_in)

    updated = {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "expire_date": expire_date,
        "user_id": user_id,
    }
    twitch_token_data = TwitchTokens(**updated)
    self.twitch_token_repository.create_or_update(twitch_token_data)

    return new_access_token
