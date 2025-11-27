import os

import requests
from dotenv import load_dotenv

from config.logger_conf import setup_logger
from config.settings import settings
from services.youtube_service import YoutubeService

load_dotenv()
logger = setup_logger()

if __name__ == "__main__":
    url = "https://production.assets.clips.twitchcdn.net/v2/media/SpikyDistinctLeopardLeeroyJenkins-N9xG6ymSy02rpRwD/4e74654c-d39a-4640-b205-77103da8efa9/video-918.mp4?response-content-disposition=attachment%3B%20filename%3D%2220251123_SpikyDistinctLeopardLeeroyJenkins-N9xG6ymSy02rpRwD_portrait.mp4%22&sig=deacec7aa67c50d41596934af793952e1eb087e4&token=%7B%22authorization%22%3A%7B%22forbidden%22%3Afalse%2C%22reason%22%3A%22%22%7D%2C%22clip_uri%22%3A%22https%3A%2F%2Fproduction.assets.clips.twitchcdn.net%2Fv2%2Fmedia%2FSpikyDistinctLeopardLeeroyJenkins-N9xG6ymSy02rpRwD%2F61f41444-b018-4164-bde3-ba8d24dc06a1%2Fvideo-1080.mp4%22%2C%22clip_slug%22%3A%22SpikyDistinctLeopardLeeroyJenkins-N9xG6ymSy02rpRwD%22%2C%22device_id%22%3A%225f4WQzo4sGUnTkn6kIJUC33n7s0xcmRm%22%2C%22expires%22%3A1764355841%2C%22user_id%22%3A%22%22%2C%22version%22%3A3%7D"

    output_file = os.path.join("data", "clip_twitch.mp4")

    logger.info("Téléchargement en cours...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(output_file, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    logger.info(f"Téléchargement terminé :{output_file}")

    ys = YoutubeService(settings.CLIENT_SECRET_FILE)
    ys.upload_video(output_file)
