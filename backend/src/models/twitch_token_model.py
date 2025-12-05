from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TwitchTokens(BaseModel):
    id: Optional[str] = None
    access_token: str
    refresh_token: Optional[str] = None
    expire_date: datetime
    user_id: str
