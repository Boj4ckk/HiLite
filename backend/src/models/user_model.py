from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    id: str
    username: Optional[str]
    email: Optional[str]
    profile_picture: Optional[str]
