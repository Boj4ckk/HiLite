import os
import time

from dotenv import load_dotenv
from services.twitch_service import TwitchApi
from buisness.twitch_buisness import TwitchBuisness
from services.scraping_service import ScrapingService
from buisness.scraping_buisness import ScrapingBuisness


from services.youtube_service import YoutubeService



load_dotenv()

twitch_service = TwitchApi(os.getenv("TWITCH_CLIENT_ID"),os.getenv("TWITCH_CLIENT_SECRET"))
twitch_b = TwitchBuisness()



streamer_id = twitch_service.get_broadcaster_id("Sniper_Biscuit")

clip_response = twitch_service.get_broadcaster_clips(streamer_id, {"first":1})
print(clip_response)

game_id = clip_response[0]["game_id"]
game_info = twitch_service.get_game_info(game_id)
print(game_info)

clip_url = twitch_b.extract_clips_url(clip_response)
print(clip_url)

title = twitch_b.generate_short_title(twitch_service,clip_response[0])

"""
s_s = ScrapingService()
s_b = ScrapingBuisness(s_s)
s_b.dowload_clip(clip_url[0])
"""

load_dotenv()

ys = YoutubeService(os.getenv("CLIENT_SECRET_FILE"),os.getenv("SCOPES"),os.getenv("API_SERVICE_NAME"),os.getenv("API_VERSION"))
ys.upload_video("C:/Users/yazki/OneDrive/Bureau/HiLite/HiLite/data/twitch_clips/20240730_FantasticBreakableLionLitFam-ZzlHJ4he5G7m7cDK_portrait.mp4",title,"LE MEILLEUR STREAMER VALO EN LIVE TOUT LES SOIRS",["#Short",twitch_service.get_game_info(clip_response[0]["game_id"]).get("name")],"public")
