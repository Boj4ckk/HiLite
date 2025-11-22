import csv
import json
import logging
import csv
import json
import logging
import os
from pathlib import Path
import time

from dotenv import load_dotenv
from tqdm import tqdm
from services.twitch_service import TwitchApi
from buisness.twitch_buisness import TwitchBuisness
from services.scraping_service import ScrapingService
from buisness.scraping_buisness import ScrapingBuisness


from services.youtube_service import YoutubeService
from services.eleven_labs_service import ElevenLabsService
from services.srt_service import SrtService
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import pysrt

from buisness.subtitlesBuisness import SubtitlesBuisness


from services.eleven_labs_service import ElevenLabsService
from services.srt_service import SrtService
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import pysrt

from buisness.subtitlesBuisness import SubtitlesBuisness





load_dotenv()
logger = logging.getLogger("HiLiteLogger")

def load_blacklist():
    """Load all blacklisted clip IDs from CSV."""
    csv_path = os.getenv("TWITCH_CLIP_BLACKLIST_PATH")
    
    # Create file with header if it doesn't exist
    if not os.path.exists(csv_path):
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["clip_id", "url"])
        return set()
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["clip_id"] for row in reader}

def add_to_blacklist(clip_id, clip_url):
    """Add a clip to the blacklist."""
    csv_path = os.getenv("TWITCH_CLIP_BLACKLIST_PATH")
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([clip_id, clip_url])
    logger.info(f"Clip {clip_id} added to blacklist")

def find_new_clip(clips):
    """Find the first clip not in blacklist."""
    blacklist = load_blacklist()
    
    for clip in clips:
        clip_id = clip.get("id")
        if clip_id not in blacklist:
            logger.info(f"Found new clip: {clip_id}")
            return clip
    
    logger.warning("No new clips found - all clips are in blacklist")
    return None



def fetch_clips(broadcaster_name):
    """Fetch clips and return the first one not in blacklist."""
    # Init twitch service
    twitch_service = TwitchApi(os.getenv("TWITCH_CLIENT_ID"), os.getenv("TWITCH_CLIENT_SECRET"))

    # Fetch broadcaster clips (50 by default)
    broadcaster_id = twitch_service.get_broadcaster_id(broadcaster_name)
    print(f"\nFetching clips for {broadcaster_name}...\n")
    
    all_clips = twitch_service.get_broadcaster_clips(broadcaster_id)
    print(f"Retrieved {len(all_clips)} clips from Twitch API")
    
    # Find first non-blacklisted clip
    new_clip = find_new_clip(all_clips)
    
    if new_clip is None:
        print("No new clips available - all clips are already processed")
        return None
    
    # Add to blacklist
    clip_id = str(new_clip.get("id"))
    clip_url = str(new_clip.get("url"))
    add_to_blacklist(clip_id, clip_url)
    
    print(f"Selected new clip: {clip_id}")
    return new_clip

def clean_clip_folder():
    """Remove all files from clip folder before downloading new clip."""
    clip_folder = Path(os.getenv("TWITCH_CLIP_FOLDER_PATH"))
    for file in clip_folder.glob("*.mp4"):
        try:
            file.unlink()
            logger.info(f"Removed old file: {file.name}")
        except PermissionError:
            logger.warning(f"Could not delete {file.name} - file in use. Waiting...")
            time.sleep(2)
            try:
                file.unlink()
                logger.info(f"Removed old file: {file.name} (after retry)")
            except Exception as e:
                logger.error(f"Failed to delete {file.name}: {e}")
    logger.info("Clip folder cleaned")

def download_clip(clip_obj):
    """Download a single clip after cleaning the folder."""
    # Clean folder first to ensure only one video exists
    clean_clip_folder()
    
    scraping_service = ScrapingService()
    clip_url = clip_obj.get("url")
    print(f"\rDownloading clip...", end="", flush=True)
    scraping_service.download_clip(clip_url)
    scraping_service.close()
    print(" Done!")
    logger.info(f"Clip downloaded: {clip_url}")
    


        

def post_single_video_on_youtube(video_path, title, description, tags=None, status="public"):
    """Upload a video to YouTube."""
    if tags is None:
        tags = ["gaming", "twitch", "clips"]
    
    youtube_service = YoutubeService(
        os.getenv("CLIENT_SECRET_FILE"),
        os.getenv("SCOPES"),
        os.getenv("API_SERVICE_NAME"),
        os.getenv("API_VERSION")
    )
    
    video_id = youtube_service.upload_video(
        video_path,
        title,
        description,
        tags,
        status
    )
    
    logger.info(f"Video uploaded to YouTube. Video ID: {video_id}")
    return video_id







def get_clip_video_path():
    """Get the path of the single video file in clip folder."""
    clip_folder = Path(os.getenv("TWITCH_CLIP_FOLDER_PATH"))
    video_files = list(clip_folder.glob("*.mp4"))
    
    if len(video_files) == 0:
        raise FileNotFoundError("No video file found in clip folder")
    elif len(video_files) > 1:
        raise RuntimeError(f"Multiple videos found in folder: {len(video_files)}. Expected only 1.")
    
    return str(video_files[0])

def subtitle_video(subtitle_font="C:/Windows/Fonts/arial.ttf", font_size=110):
    """Add subtitles to the single video in clip folder."""
    # Get the video path
    video_path = get_clip_video_path()
    logger.info(f"Processing video: {video_path}")
    
    # Output to edited_clips folder instead of same folder
    edited_folder = Path(os.getenv("EDITED_CLIP_FOLDER"))
    edited_folder.mkdir(parents=True, exist_ok=True)
    
    video_filename = Path(video_path).stem
    video_output_path = str(edited_folder / f"{video_filename}_subtitled.mp4")
    
    # Generate transcription
    elevenlabs_service = ElevenLabsService(os.getenv("ELEVEN_LABS_API_KEY"))
    print("Generating transcription...")
    transcription = elevenlabs_service.speach_to_text(video_path, "fr")

    # Setup srt service - use only filename, not full path
    video_filename = Path(video_path).stem  # Get filename without extension
    srt_output_file = f"{video_filename}.srt"
    srt_service = SrtService(srt_output_file)

    # Convert transcription to srt and save it
    print("Creating SRT file...")
    srt_service.convert_transcription_into_srt(transcription) 
    srt_path = srt_service.srt_output_file

    # Create subtitled video
    print("Adding subtitles to video...")
    subtitle_buisness = SubtitlesBuisness()
    subtitle_buisness.create_subtitled_video(
        video_path,
        srt_path,
        video_output_path,
        subtitle_font,
        font_size,
        (255, 255, 255, 255),
        (0, 0, 0, 255),
        6,
        0.80,
    )
    
    logger.info(f"Subtitled video created: {video_output_path}")
    
    # Clean up: wait a bit to ensure files are released
    time.sleep(1)
    
    return video_output_path


def process_single_clip(broadcaster_name):
    """Complete pipeline: fetch -> download -> subtitle -> upload for one clip."""
    print("\n" + "="*50)
    print("Starting clip processing pipeline")
    print("="*50)
    
    # Step 1: Fetch new clip
    clip = fetch_clips(broadcaster_name)
    if clip is None:
        print("No new clips available. Skipping.")
        return False
    
    print(f"Processing clip: {clip.get('url')}")
    
    try:
        # Step 2: Download clip (with folder cleaning)
        print("\n[1/4] Downloading clip...")
        download_clip(clip)
        
        # Step 3: Add subtitles
        print("\n[2/4] Adding subtitles...")
        subtitled_video = subtitle_video()
        
        # Step 4: Generate title and description
        print("\n[3/4] Preparing YouTube upload...")
        
        # Generate title using template
        twitch_service = TwitchApi(os.getenv("TWITCH_CLIENT_ID"), os.getenv("TWITCH_CLIENT_SECRET"))
        twitch_business = TwitchBuisness()
        youtube_title = twitch_business.generate_short_title(twitch_service, clip)
        
        if youtube_title is None:
            # Fallback title if template generation fails
            youtube_title = f"{clip.get('title', 'Clip')} | {clip.get('broadcaster_name', broadcaster_name)}"
        
        broadcaster = clip.get("broadcaster_name", broadcaster_name)
        game_id = clip.get("game_id")
        game_info = twitch_service.get_game_info(game_id) if game_id else None
        game = game_info.get("name", "Gaming") if game_info else "Gaming"
        
        # Create YouTube description
        youtube_description = f"""
                Clip de {broadcaster} en stream!
            Game: {game}

            #twitch #gaming #{game.replace(' ', '')} #{broadcaster.replace(' ', '')}
                    #short""".strip()
        
        # Step 5: Upload to YouTube
        print("\n[4/4] Uploading to YouTube...")
        video_id = post_single_video_on_youtube(
            subtitled_video,
            youtube_title,
            youtube_description,
            tags=[game, broadcaster, "twitch", "clips","short"],
            status="public"
        )
        
        print(f"\n Video uploaded successfully!")
        print(f"YouTube URL: https://www.youtube.com/watch?v={video_id}")
        
        print("\n" + "="*50)
        print("Pipeline completed successfully!")
        print("="*50 + "\n")
        return True
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        print(f"\n Error during processing: {e}")
        return False

if __name__ == "__main__":
    nb_clips = 3
    broadcaster_name = "Sniper_Biscuit"
    
    successful = 0
    failed = 0
    
    for i in range(nb_clips):
        print(f"\n\n{'='*60}")
        print(f"PROCESSING CLIP {i+1}/{nb_clips}")
        print(f"{'='*60}\n")
        
        result = process_single_clip(broadcaster_name)
        
        if result:
            successful += 1
        else:
            failed += 1
            print("Moving to next clip...")
        
        # Small delay between clips
        if i < nb_clips - 1:
            time.sleep(2)
    
    print(f"\n\n{'='*60}")
    print(f"FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"Successful: {successful}/{nb_clips}")
    print(f"Failed: {failed}/{nb_clips}")
    print(f"{'='*60}\n")    
   


