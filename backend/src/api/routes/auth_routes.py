from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import (
    get_current_user,
    get_twitch_service,
    get_twitch_token_business,
    get_user_business,
)
from buisness.db.twitch_token_business import TwitchTokensBusiness
from buisness.db.user_business import UserBusiness
from config.logger_conf import setup_logger
from models.dto.dto_twitch_token_model import TwitchTokensRequest
from models.user_model import User
from services.twitch_service import TwitchApi

logger = setup_logger()


router = APIRouter(prefix="/auth")


@router.post("/me")
async def sync_user(
    tokens: TwitchTokensRequest,
    twitch_token_business: TwitchTokensBusiness = Depends(get_twitch_token_business),
    user_business: UserBusiness = Depends(get_user_business),
    current_user: User = Depends(get_current_user),
    twitch_api: TwitchApi = Depends(get_twitch_service),
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Unable to sync user")

    if tokens is not None:
        ok = twitch_token_business.asign_access_token(
            twitch_api,
            tokens,
            current_user,
        )
        if not ok:
            raise HTTPException(status_code=400, detail="Invalid Twitch tokens")

    return {
        "status": "ok",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "profile_picture": current_user.profile_picture,
        },
    }
