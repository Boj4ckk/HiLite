from fastapi import HTTPException
from fastapi import APIRouter, Depends

from api.dependencies import get_current_user, get_twitch_service
from config.logger_conf import setup_logger
from services.twitch_service import TwitchApi
from repositories.user_repository import User
from services.eventsub_service import EventSubService

logger = setup_logger()


router = APIRouter(prefix="/app")



@router.post("/eventsub/create")
async def create_eventsub_for_user(
    event_type: str = "stream.offline",
    current_user: dict = Depends(get_current_user),
    twitch_api: TwitchApi  = Depends(get_twitch_service)
):
    db_user: User = current_user["user"]
    user_id = db_user.id
    logger.info(user_id)
    await twitch_api.get_access_token()
    event_subservice = EventSubService(twitch_api)
    subscription = await event_subservice.create_eventsub_subscription(
        user_id,
        event_type
    )

    if subscription:
        return{
            "status": "success",
            "user_id": user_id,
            "subscription_id": subscription["id"],
            "event_type": event_type
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to create EventSub")