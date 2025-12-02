from fastapi import APIRouter, Depends

from api.dependencies import get_current_user, get_user_repository
from config.logger_conf import setup_logger
from models.twitch_token_model import TwitchTokensRequest
from models.user_model import User
from repositories.user_repository import UserRepository

logger = setup_logger()


router = APIRouter(prefix="/auth")


@router.get("/me")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"user": current_user}


@router.post("/twitch/tokens")
async def save_twitch_tokens(
    tokens: TwitchTokensRequest,
    user_respository: UserRepository = Depends(get_user_repository),
):
    access_token = tokens.twitch_access_token
    refresh_token = tokens.twitch_refresh_token

    user_respository.insert_twitch_tokens(access_token, refresh_token)
