from typing import Optional

from pydantic import BaseModel


class TwitchTokensRequest(BaseModel):
    twitch_access_token: str
    twitch_refresh_token: Optional[str] = None
