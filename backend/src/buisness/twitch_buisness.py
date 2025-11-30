import json
import logging
import os
import random
from pathlib import Path

from config.settings import settings
from services.twitch_service import TwitchApi


class TwitchBuisness:
    @staticmethod
    def extract_clips_ids(clips_obj):
        clips_ids = []
        for clip in clips_obj:
            clips_ids.append(clip["id"])
        return clips_ids

    @staticmethod
    def extract_clips_url(clip_obj):
        clips_url = []

        for clip in clip_obj:
            clips_url.append(clip["url"])
        return clips_url

    @staticmethod
    def generate_short_title(twitch_service: TwitchApi, clip):
        """
        Generate a short title for a clip using a random template.
        Fills template with broadcaster name, game name, and clip title.
        Logs each step in English.
        """
        logger = logging.getLogger("HiLiteLogger")

        titles_template_path_env = settings.TITLES_TEMPLATE_PATH
        if not titles_template_path_env:
            logger.error("TITLES_TEMPLATE_PATH environment variable is not set")
            return None

        titles_template_path = str(Path(titles_template_path_env))

        # Check if file exists
        if not os.path.exists(titles_template_path):
            logger.error(f"Title templates file not found: {titles_template_path}")
            return None

        # Load title templates from file
        logger.info(f"Loading title templates from {titles_template_path}")
        try:
            with open(titles_template_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validate JSON structure
            if not isinstance(data, dict) or "templates" not in data:
                logger.error(
                    "Invalid title templates file structure: missing 'templates' key"
                )
                return None

            title_templates = data["templates"]
            if not isinstance(title_templates, list) or len(title_templates) == 0:
                logger.error("Title templates list is empty or invalid")
                return None

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse title templates JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to load title templates: {e}")
            return None

        # Choose a random template
        random_title_template = random.choice(title_templates)
        logger.info(f"Selected random title template: {random_title_template}")

        broadcaster_name = clip.get("broadcaster_name", "")
        clip_title = clip.get("title", "")

        # Get game info and extract game name
        game_info = twitch_service.get_game_info(clip.get("game_id"))
        if game_info:
            game_name = game_info.get("name", "")
            logger.info(f"Fetched game name: {game_name}")
        else:
            game_name = ""
            logger.warning(f"Game info not found for game_id: {clip.get('game_id')}")

        # Format the title
        try:
            title = random_title_template.format(
                broadcaster_name=broadcaster_name, game=game_name, clip_title=clip_title
            )
            logger.info(f"Generated short title: {title}")
            return title
        except Exception as e:
            logger.error(f"Failed to format title: {e}")
            return None
