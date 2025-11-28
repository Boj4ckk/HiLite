import requests
from dotenv import load_dotenv

from buisness.token_manager import TokenManager
from config.logger_conf import setup_logger
from config.settings import settings
from services.supabase_service import SupaBase
from services.youtube_service import YoutubeService

load_dotenv()
logger = setup_logger()

if __name__ == "__main__":
    url = "https://production.assets.clips.twitchcdn.net/v2/media/ObliqueAwkwardCucumberGingerPower-Ixj1zpAT2FyjJ3An/345f8f79-95c5-4b3c-a0ca-2912eeee1838/video-918.mp4?response-content-disposition=attachment%3B%20filename%3D%2220251122_ObliqueAwkwardCucumberGingerPower-Ixj1zpAT2FyjJ3An_portrait.mp4%22&amp;sig=af862476362f7905e3e46d3d03112b309ab22992&amp;token=%7B%22authorization%22%3A%7B%22forbidden%22%3Afalse%2C%22reason%22%3A%22%22%7D%2C%22clip_uri%22%3A%22https%3A%2F%2Fproduction.assets.clips.twitchcdn.net%2Fv2%2Fmedia%2FObliqueAwkwardCucumberGingerPower-Ixj1zpAT2FyjJ3An%2F345f8f79-95c5-4b3c-a0ca-2912eeee1838%2Fvideo-918.mp4%22%2C%22clip_slug%22%3A%22ObliqueAwkwardCucumberGingerPower-Ixj1zpAT2FyjJ3An%22%2C%22device_id%22%3A%22eb08ba79833b9b60%22%2C%22expires%22%3A1764406709%2C%22user_id%22%3A%22479115469%22%2C%22version%22%3A3%7D"
    r = requests.get(url)
    path = "video.mp4"
    with open("video.mp4", "wb") as f:
        f.write(r.content)
    supabase_service = SupaBase(settings.SUPABASE_URL, settings.SUPABASE_API_KEY)
    token_manager = TokenManager(supabase_service)
    youtube_service = YoutubeService(settings.CLIENT_SECRET_FILE)

    tokens = token_manager.get_tokens(1, 2)

    yt_client = youtube_service.get_client(
        tokens["access_token"], tokens["refresh_token"]
    )[0]
    youtube_service.upload_video(yt_client, "video.mp4", "tt", "t", "t", "private")
