import httpx
from services.twitch_service import TwitchApi
from config.settings import settings
from config.logger_conf import setup_logger

logger = setup_logger()

class EventSubService:

    def __init__(self, twitch_api: TwitchApi):
        self.twitch_api = twitch_api
    
    async def create_eventsub_subscription(
        self,
        broadcaster_id: str,
        event_type: str,
        version: str = "1"
    ):
        """
        Create or retrieve existing EventSub subscription.
        
        :param broadcaster_id: Twitch user ID of the broadcaster
        :param event_type: Type of event (e.g., 'stream.offline')
        :param version: Event version (default: "1")
        :return: Subscription data or None if failed
        """
     
        headers = await self.twitch_api.get_headers()
        
        async with httpx.AsyncClient() as client:
            # Check existing subscriptions
            try:
                list_response = await client.get(
                    settings.TWITCH_EVENTSUB_URL,
                    headers=headers
                )
                list_response.raise_for_status()
                existing_subs = list_response.json()["data"]
            except httpx.HTTPStatusError as e:
                logger.error(f"Failed to list EventSubs: {e}")
                return None
            
            # Check if subscription already exists
            for sub in existing_subs:
                if (sub["type"] == event_type and 
                    sub["condition"].get("broadcaster_user_id") == broadcaster_id and
                    sub["status"] == "enabled"):
                    logger.info(f"EventSub already exists (ID: {sub['id']})")
                    return sub
            
            # Create new subscription
            logger.info(f"Creating EventSub for event: {event_type}")
            
            try:
                response = await client.post(
                    settings.TWITCH_EVENTSUB_URL,
                    headers={**headers, "Content-Type": "application/json"},
                    json={
                        "type": event_type,
                        "version": version,
                        "condition": {
                            "broadcaster_user_id": broadcaster_id
                        },
                        "transport": {
                            "method": "webhook",
                            "callback": f"{settings.BASE_URL}/twitch/webhook",
                            "secret": settings.TWITCH_EVENTSUB_SECRET
                        }
                    }
                )
                
                if response.status_code == 202:
                    subscription = response.json()["data"][0]
                    logger.info(f"Subscription created successfully! (ID: {subscription['id']})")
                    return subscription
                else:
                    logger.error(f"Failed to create EventSub: {response.status_code} - {response.text}")
                    return None
                    
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error creating EventSub: {e}")
                logger.error(f"Response: {e.response.text if hasattr(e, 'response') else 'N/A'}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error creating EventSub: {e}")
                return None