import os
import time

from dotenv import load_dotenv
from routes.tiktok_route import app
from services.twitch_service import TwitchApi
from buisness.twitch_buisness import TwitchBuisness


from services.tiktok_service import TikTokService
from routes.tiktok_route import callback,HTTPS_REDIRECT_URI



load_dotenv()
"""
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
"""
ts = TikTokService(os.getenv("CLIENT_ID"),os.getenv("CLIENT_SECRET"))

if __name__ == "__main__":
    client_id = ts.client_id
    scope = "video.upload"
    state = "123abc"  # random string
    auth_url = f"https://www.tiktok.com/auth/authorize/?client_key={client_id}&scope={scope}&response_type=code&redirect_uri={HTTPS_REDIRECT_URI}&state={state}"
    print(f"Ouvre ce lien dans ton navigateur : {auth_url}")
    app.run(debug=True, port=5000)





print("Hello world")