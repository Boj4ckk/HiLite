import os
import time

from dotenv import load_dotenv
from services.twitch_service import TwitchApi
from buisness.twitch_buisness import TwitchBuisness
from services.scraping_service import ScrapingService
from buisness.scraping_buisness import ScrapingBuisness


from services.youtube_service import YoutubeService

from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import pysrt

load_dotenv()
"""


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


s_s = ScrapingService()
s_b = ScrapingBuisness(s_s)
s_b.dowload_clip(clip_url[0])


load_dotenv()

ys = YoutubeService(os.getenv("CLIENT_SECRET_FILE"),os.getenv("SCOPES"),os.getenv("API_SERVICE_NAME"),os.getenv("API_VERSION"))
ys.upload_video("C:/Users/yazki/OneDrive/Bureau/HiLite/HiLite/data/twitch_clips/20240730_FantasticBreakableLionLitFam-ZzlHJ4he5G7m7cDK_portrait.mp4",title,"LE MEILLEUR STREAMER VALO EN LIVE TOUT LES SOIRS",["#Short",twitch_service.get_game_info(clip_response[0]["game_id"]).get("name")],"public")
"""

from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import pysrt
import os
import shutil

# --- Configuration ---
video_path = "video.mp4"
srt_path = "video.srt"
output_path = "video_tiktok_capcut.mp4"
font_path = "arialbd.ttf"  # Changez pour Anton si vous l'avez
font_size = 120
text_color = (255, 255, 255, 255)  # blanc
stroke_color = (0, 0, 0, 255)      # contour noir
stroke_width = 6
position_y_ratio = 0.80          # 85% de la hauteur pour rester légèrement au-dessus du bas
temp_dir = "tmp_words"

# --- Préparer le dossier temporaire ---
os.makedirs(temp_dir, exist_ok=True)

# --- Charger vidéo et sous-titres ---
video = VideoFileClip(video_path)
subs = pysrt.open(srt_path)

clips = [video]

# --- Générer un clip par mot ---
for sub_idx, sub in enumerate(subs):
    start = sub.start.hours*3600 + sub.start.minutes*60 + sub.start.seconds + sub.start.milliseconds/1000
    end = sub.end.hours*3600 + sub.end.minutes*60 + sub.end.seconds + sub.end.milliseconds/1000
    duration = end - start

    words = sub.text.split()
    word_duration = duration / len(words)

    for i, word in enumerate(words):
        word_start = start + i * word_duration
        word_end = word_start + word_duration

        # --- Créer image du mot avec PIL ---
        img = Image.new("RGBA", (1280, 130), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(font_path, font_size)

        # largeur/hauteur avec textbbox
        bbox = draw.textbbox((0, 0), word, font=font, stroke_width=stroke_width)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        # dessiner texte centré
        draw.text(((1280-w)/2, 0), word, font=font, fill=text_color, stroke_width=stroke_width, stroke_fill=stroke_color)

        # --- Sauvegarder image temporaire ---
        img_path = os.path.join(temp_dir, f"sub{sub_idx}_word{i}.png")
        img.save(img_path)

        # --- Créer ImageClip avec effet fade-in / pop ---
        pos_y = int(video.h * position_y_ratio)  # calcul fixe
        txt_clip = ImageClip(img_path).set_start(word_start).set_end(word_end).set_position(
            ("center", pos_y)
        )
        txt_clip = txt_clip.fadein(0.1) # fade-in/out rapide
        clips.append(txt_clip)

# --- Composer vidéo finale ---
final = CompositeVideoClip(clips)
final.write_videofile(output_path, codec="libx264", fps=video.fps)

# --- Nettoyer dossier temporaire ---
shutil.rmtree(temp_dir)
