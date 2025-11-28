from dotenv import load_dotenv
from supabase import Client, create_client

from config.logger_conf import setup_logger

load_dotenv()
logger = setup_logger()


class SupaBase:
    def __init__(self, url, key):
        self.url = url
        self.key = key
        self.supabase: Client = create_client(self.url, self.key)

    def insert_into_users(self, username):
        data = {"username": username}
        try:
            logger.info(f"Inserting {username} into users...")
            response = self.supabase.table("Users").insert(data).execute()
            logger.info(f"Inserted user: {username} successfully")
            return response
        except Exception as e:
            logger.error(
                f"Insertion into db failed. Make sure the table is correct.Make sure the data is correct. {e}"
            )

    def get_user(self, user_id):
        logger.info(f"Fetching data for the user_id: {user_id}")
        try:
            response = (
                self.supabase.table("Users")
                .select("*")
                .eq("id", user_id)
                .single()
                .execute()
            )
            logger.info(f"successfully fetch data for the user_id: {user_id}")
            return getattr(response, "data", response)
        except Exception as e:
            logger.error(f"Failed to fetch data for the user {user_id}: {e}")

    def get_network(self, network_id):
        try:
            logger.info(f"Fetching data for the network  :{network_id}")
            response = (
                self.supabase.table("SocialNetwork")
                .select("*")
                .eq("id", network_id)
                .single()
                .execute()
            )
            logger.info(f"successfully fetch data for the network_id :{network_id}")
            return getattr(response, "data", response)
        except Exception as e:
            logger.error(f"Failed to fetch data for the network {network_id}: {e}")

    def get_user_networks_by_network_id(self, user_id, network_id):
        try:
            logger.info(f"Fetching user : {user_id} network : {network_id}")
            response = (
                self.supabase.table("SocialNetwork")
                .select("*")
                .eq("id", network_id)
                .eq("user_id", user_id)
                .single()
                .execute()
            )
            logger.info(f"Fetched user : {user_id} network : {network_id} successfully")
            return getattr(response, "data", response)
        except Exception as e:
            logger.error(
                f"Failed to fetch network : {network_id} for the user {user_id}: {e}"
            )

    def insert_user_network(self, user_id, platform, access_token, refresh_token):
        data = {
            "user_id": user_id,
            "refresh_token": refresh_token,
            "platform": platform,
            "access_token": access_token,
        }
        try:
            logger.info(f"Inserting into user's: {user_id} network.")
            response = self.supabase.table("SocialNetwork").insert(data).execute()
            logger.info(f"Inserted network for the user : {user_id} successfully")
            return getattr(response, "data", response)
        except Exception as e:
            logger.error(f"Failed to insert networks for the user {user_id}: {e}")

    def update_user_network(
        self, network_id, user_id, platform, access_token, refresh_token
    ):
        data = {
            "user_id": user_id,
            "refresh_token": refresh_token,
            "platform": platform,
            "access_token": access_token,
        }
        try:
            logger.info(
                f"Updating network table: {network_id} for the user:  {user_id}"
            )
            response = (
                self.supabase.table("SocialNetwork")
                .update(data)
                .eq("id", network_id)
                .execute()
            )
            logger.info(f"Updated network table: {network_id} successfully")
            return getattr(response, "data", response)
        except Exception as e:
            logger.error(f"Failed to update table network:{network_id}. {e}")
