from config.logger_conf import setup_logger
from models.user_model import User
from repositories.user_repository import UserRepository
from services.supabase_service import SupaBase

logger = setup_logger()


class UserBusiness:
    def __init__(self, supabase: SupaBase, user_repository: UserRepository):
        self.supabase = supabase
        self.user_repository = user_repository

    def sync_user(self, token):
        user = self.supabase.get_user_from_token(token)
        if not user:
            logger.info("sync_user: no user returned from supabase for token")
            return None

        # Normalize user and metadata for dict or object shapes
        if isinstance(user, dict):
            user_id = user.get("id")
            metadata = user.get("user_metadata") or {}
        else:
            user_id = getattr(user, "id", None)
            metadata = getattr(user, "user_metadata", {}) or {}

        def _meta_get(key):
            if isinstance(metadata, dict):
                return metadata.get(key)
            return getattr(metadata, key, None)

        user_data = {
            "id": user_id,
            "username": _meta_get("nickname"),
            "email": _meta_get("email"),
            "profile_picture": _meta_get("picture"),
        }

        # Build User model (repository expects a User model with model_dump)
        try:
            user_model = User(**user_data)
        except Exception as e:
            logger.error("Failed to construct User model: %s", e)
            return None

        try:
            self.user_repository.create_or_update(user_model)
        except Exception as e:
            logger.error("Failed to upsert user: %s", e)
            return None

        return user_model
