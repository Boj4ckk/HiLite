

import hashlib
import hmac
from http.client import HTTPException
from config.settings import settings


def verify_signature(raw_body,headers):
    """
    Verify if the webhook is from Twitch.

    Args:
        - raw_body : body response as bytes.
        - headers  : header response.
    
    """

    message_id = headers.get('twitch-eventsub-message-id')
    timestamp = headers.get('twitch-eventsub-message-timestamp')
    signature = headers.get('twitch-eventsub-message-signature')

    if not all([message_id,timestamp,signature]):
        raise HTTPException(status_code=400,detail="Missing headers")
    
    # Construct HMAC message
    secret = settings.TWITCH_EVENTSUB_SECRET.encode('utf-8')
    hmac_message = message_id.encode() + timestamp.encode() + raw_body
    expected_signature = 'sha256=' + hmac.new( # exemple : Twitch-Eventsub-Message-Signature: sha256=<hex> 
        secret,
        hmac_message,
        hashlib.sha256 #
    ).hexdigest() #hexa convertion

    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(status_code=403,detail="Invalid signature")