import os
import time

from dotenv import load_dotenv
from services.twitch_service import TwitchApi
from buisness.twitch_buisness import TwitchBuisness
from services.scraping_service import ScrapingService
from buisness.scraping_buisness import ScrapingBuisness


from services.youtube_service import YoutubeService
from services.eleven_labs_service import ElevenLabsService
from services.srt_service import SrtService


load_dotenv()
"""
twitch_service = TwitchApi(os.getenv("TWITCH_CLIENT_ID"),os.getenv("TWITCH_CLIENT_SECRET"))
twitch_b = TwitchBuisness()



streamer_id = twitch_service.get_broadcaster_id("Sniper_Biscuit")

clip_response = twitch_service.get_broadcaster_clips(streamer_id, {"first":2 })
print(clip_response)

game_id = clip_response[1]["game_id"]
game_info = twitch_service.get_game_info(game_id)
print(game_info)

clip_url = twitch_b.extract_clips_url(clip_response)
print(clip_url)

title = twitch_b.generate_short_title(twitch_service,clip_response[1])


s_s = ScrapingService()
s_b = ScrapingBuisness(s_s)
s_b.dowload_clip(clip_url[1])



"""




e_s = ElevenLabsService(os.getenv("ELEVENLABS_API_KEY"))
transcription = e_s.speach_to_text(
    video_path="20251116_BrightCourageousDaikonDuDudu-p6rmYSPtl4BEDKO4_portrait.mp4",
    model_id="scribe_v1",
    tag_audio_events=True,
    language_code="fr",
    diarize=True,
)
srt_service = SrtService(transcription)

print(srt_service.convert_transcription_into_srt("video.srt"))

