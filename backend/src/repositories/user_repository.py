from models.user_model import User
from services.supabase_service import SupaBase


class UserRepository:
    def __init__(self, supabase: SupaBase):
        self.supabase = supabase

    def create_or_update(self, user: User):
        data = user.model_dump()
        # Use on_conflict to ensure update happens when row with same id exists.
        # Note: verify the table name matches your Supabase table (e.g. "users" vs "User").
        return self.supabase.upsert("User", data, on_conflict="id")
