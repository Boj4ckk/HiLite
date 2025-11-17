import os
import time

from dotenv import load_dotenv
from services.twitch_service import TwitchApi
from buisness.twitch_buisness import TwitchBuisness
from services.scraping_service import ScrapingService
from buisness.scraping_buisness import ScrapingBuisness



load_dotenv()
twitch_service = TwitchApi(os.getenv("CLIENT_ID"),os.getenv("CLIENT_SECRET"))

twitch_b = TwitchBuisness()



streamer_id = twitch_service.get_broadcaster_id("Sniper_Biscuit")
print(streamer_id)
clip_response = twitch_service.get_broadcaster_clips(streamer_id, {"first":1})
print(clip_response)
clip_url = twitch_b.extract_clips_url(clip_response)
print(clip_url)



s_s = ScrapingService()
s_b = ScrapingBuisness(s_s)
s_b.dowload_clip(clip_url[0])





