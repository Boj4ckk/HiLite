from config.logger_conf import setup_logger
from services.supabase_service import SupaBase

logger = setup_logger()


class TokenManager:
    def __init__(self, supabase_service: SupaBase):
        self.supabase = supabase_service

    def save_tokens(self, user_id, platform, access_token, refresh):
        if not access_token:
            raise ValueError("Access Token needed")

        user = self.supabase.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        return self.supabase.insert_user_network(
            user_id, platform, access_token, refresh
        )

    def get_tokens(self, user_id, network_id):
        try:
            user = self.supabase.get_user(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            response = self.supabase.get_user_networks_by_network_id(
                user_id, network_id
            )

            tokens = {
                "access_token": response["access_token"],
                "refresh_token": response["refresh_token"],
            }

            if not tokens["access_token"]:
                raise ValueError(f"No access token found for network {network_id}")
            return tokens

        except Exception as e:
            logger.error(f"Failed to get tokens for network {network_id}: {e}")

    def update_token(
        self, network_id, user_id, access_token, platform, refresh_token=None
    ):
        try:
            user = self.supabase.get_user(user_id)
            network = self.supabase.get_network(network_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            if not network:
                raise ValueError(f"Network {network_id} not found")
            self.supabase.update_user_network(
                network_id, user_id, platform, access_token, refresh_token
            )

        except Exception as e:
            logger.error(f"Failed to update tokens for network {network_id}: {e}")
