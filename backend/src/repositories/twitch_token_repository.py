from datetime import datetime

from models.twitch_token_model import TwitchTokens
from services.supabase_service import SupaBase


class TwitchTokenRepository:
    def __init__(self, supabase: SupaBase):
        self.supabase = supabase

    def create_or_update(self, twitch_token_model_data: TwitchTokens):
        data = twitch_token_model_data.model_dump(exclude_none=True)

        if isinstance(data.get("expire_date"), datetime):
            data["expire_date"] = data["expire_date"].isoformat()

        return self.supabase.upsert("TwitchTokens", data, on_conflict="user_id")

    def get_by_user_id(self, user_id):
        row = self.supabase.get_row_by_id("user_id", user_id, "TwichTokens")
        return row
