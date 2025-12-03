from fastapi import Depends, Header, HTTPException

from buisness.db.twitch_token_business import TwitchTokensBusiness
from buisness.db.user_business import UserBusiness
from config.logger_conf import setup_logger
from config.settings import settings
from repositories.twitch_token_repository import TwitchTokenRepository
from repositories.user_repository import UserRepository
from services.supabase_service import SupaBase
from services.twitch_service import TwitchApi

logger = setup_logger()


# ======= SERVICES ==================
def get_supabase_service() -> SupaBase:
    supabase = SupaBase(settings.SUPABASE_URL, settings.SUPABASE_API_KEY)
    return supabase


def get_twitch_service() -> TwitchApi:
    twitch_api = TwitchApi(settings.TWITCH_CLIENT_ID, settings.TWITCH_CLIENT_SECRET)
    return twitch_api


# ========== REPOSITORIES ================
def get_user_repository(
    supabase: SupaBase = Depends(get_supabase_service),
) -> UserRepository:
    user_repository = UserRepository(supabase)
    return user_repository


def get_twitch_token_repository(
    supabase: SupaBase = Depends(get_supabase_service),
) -> TwitchTokenRepository:
    twitch_token_repository = TwitchTokenRepository(supabase)
    return twitch_token_repository


# ========= BUSINESS ==============
def get_user_business(
    supabase: SupaBase = Depends(get_supabase_service),
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserBusiness:
    user_buisness = UserBusiness(supabase, user_repository)
    return user_buisness


async def get_current_user(
    authorization: str = Header(None),
    user_business: UserBusiness = Depends(get_user_business),
):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing auth header")

    token = authorization.replace("Bearer ", "").strip()
    db_user = user_business.sync_user(token)
    return db_user


def get_twitch_token_business(
    supabase: SupaBase = Depends(get_supabase_service),
    twitch_token_repository: TwitchTokenRepository = Depends(
        get_twitch_token_repository
    ),
) -> TwitchTokensBusiness:
    twitch_token_business = TwitchTokensBusiness(supabase, twitch_token_repository)
    return twitch_token_business
