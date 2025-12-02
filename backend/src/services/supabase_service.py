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

    def get_user_from_token(self, token):
        """Return the Supabase user object for a given access token or None on error."""
        if not token:
            logger.info("Token is None")
            return None

        try:
            # try the common call signature: get_user(token)
            user_resp = None
            try:
                user_resp = self.supabase.auth.get_user(token)
            except TypeError:
                # fallback: some client versions expect a dict payload
                try:
                    user_resp = self.supabase.auth.get_user({"access_token": token})
                except Exception:
                    user_resp = None

            if not user_resp:
                logger.error(
                    "get_user_from_token: no response from supabase.auth.get_user"
                )
                return None

            # normalize response: support Pydantic-like object or dict

            user = getattr(user_resp, "user", None)
            if user is None and isinstance(user_resp, dict):
                # some versions return {"user": {...}} or {"data": {...}, "error": ...}
                user = user_resp.get("user") or user_resp.get("data")
                # if data contains keys like 'user' or user object inside, try to extract
                if isinstance(user, dict) and "user" in user:
                    user = user.get("user")

            return user
        except Exception as e:
            logger.error("Error in get_user_from_token: %s", e)
            return None

    def get_row_by_id(self, column, id_value, table):
        try:
            logger.info(f"Geting {table} {column} Where {column} = {id_value}")
            response = (
                self.client.table(table)
                .select("*")
                .eq(column, id_value)
                .single()
                .execute()
            )
            return response
        except Exception:
            logger.error(f"Failed to get {table} {column} where {column} == {id_value}")

    def upsert(self, table_name, data, on_conflict: str = None):
        """
        Create or update table
        Args:
            table_name (str): name of the table
            data (dict) : data to insert or update in table
        """
        response = None
        try:
            logger.info(
                f"Upserting into table {table_name} (on_conflict={on_conflict})"
            )
            table = self.supabase.table(table_name)
            if on_conflict:
                response = table.upsert(data, on_conflict=on_conflict).execute()
            else:
                response = table.upsert(data).execute()

            # log response details for debugging
            try:
                logger.debug("Upsert response: %s", getattr(response, "data", response))
            except Exception:
                logger.debug("Upsert response repr: %r", response)
            logger.info(f"Upsert into table {table_name} successfully.")
        except Exception as e:
            logger.error(f"Failed to upsert into table {table_name}: %s", e)
        return response

    def insert(self, table_name, data):
        try:
            logger.info(f"Inserting into table {table_name}")
            response = self.supabase.table(table_name).insert(data).execute()
            logger.info(f"Successfully inserted into {table_name}")
            return response
        except Exception:
            logger.error(f"Failed to insert into table {table_name}")
