from PIL import Image, ImageDraw, ImageFont
import os
import shutil
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
import pysrt
import logging

logger = logging.getLogger("HiLiteLogger")
class SubtitlesBuisness:

    @staticmethod
    def generate_word_image(word, font_path, font_size, text_color, stroke_color, stroke_width, width=1280, height=130, img_path="word.png"):
        """Generate an image for a single word with specified styling."""
        # Skip empty words
        if not word or not word.strip():
            logger.warning("Skipping empty word for image generation")
            return None
        
        # Verify font exists
        if not os.path.exists(font_path):
            logger.error(f"Font file not found: {font_path}")
            raise FileNotFoundError(f"Font file not found: {font_path}")
        
        try:
            img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(font_path, font_size)
            bbox = draw.textbbox((0, 0), word, font=font, stroke_width=stroke_width)
            w = bbox[2] - bbox[0]
            draw.text(((width-w)/2, 0), word, font=font, fill=text_color, stroke_width=stroke_width, stroke_fill=stroke_color)
            img.save(img_path)
            return os.path.normpath(img_path)
        except OSError as e:
            logger.error(f"Failed to load font {font_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to generate word image for '{word}': {e}")
            raise

    @staticmethod
    def get_word_timings_from_subtitle(sub):
        """Calculate timing for each word in a subtitle."""
        start = sub.start.hours*3600 + sub.start.minutes*60 + sub.start.seconds + sub.start.milliseconds/1000
        end = sub.end.hours*3600 + sub.end.minutes*60 + sub.end.seconds + sub.end.milliseconds/1000
        duration = end - start
        words = sub.text.split()
        
        # Skip empty subtitles
        if len(words) == 0:
            return []
        
        word_duration = duration / len(words)
        return [(word, start + i*word_duration, start + (i+1)*word_duration) for i, word in enumerate(words)]

    @staticmethod
    def generate_subtitle_images(subs, font_path, font_size, text_color, stroke_color, stroke_width, temp_dir):
        """Generate all word images for subtitles and return list of (img_path, start, end)."""
        logger.info(f"Starting image generation for {len(subs)} subtitles")
        os.makedirs(temp_dir, exist_ok=True)
        img_infos = []
        
        for sub_idx, sub in enumerate(subs):
            word_timings = SubtitlesBuisness.get_word_timings_from_subtitle(sub)
            for i, (word, word_start, word_end) in enumerate(word_timings):
                img_path = os.path.join(temp_dir, f"sub{sub_idx}_word{i}.png")
                try:
                    generated_path = SubtitlesBuisness.generate_word_image(
                        word, font_path, font_size, text_color, stroke_color, stroke_width, 1280, 130, img_path
                    )
                    # Only add if image was successfully generated
                    if generated_path:
                            img_infos.append((os.path.normpath(img_path), word_start, word_end))
                except Exception as e:
                    logger.warning(f"Skipping word '{word}' due to error: {e}")
                    continue
        
        logger.info(f"Generated {len(img_infos)} word images in {temp_dir}")
        return img_infos

    @staticmethod
    def create_subtitled_video(
        video_path,
        srt_path,
        output_path,
        font_path,
        font_size,
        text_color,
        stroke_color,
        stroke_width,
        position_y_ratio=0.80,
        temp_dir="tmp/subtitles_temp"
    ):
        """
        Create a video with animated word-by-word subtitles.
        Handles image generation, video composition, and cleanup.
        """
        try:
            logger.info(f"Starting subtitle video creation for {video_path}")
            
            # Verify input files exist
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            if not os.path.exists(srt_path):
                raise FileNotFoundError(f"SRT file not found: {srt_path}")
            
            # Load video and subtitles
            video = VideoFileClip(video_path)
            subs = pysrt.open(srt_path)
            logger.info(f"Loaded video and {len(subs)} subtitles")
            
            # Generate all word images
            img_infos = SubtitlesBuisness.generate_subtitle_images(
                subs, font_path, font_size, text_color, stroke_color, stroke_width, temp_dir
            )
            logger.info(f"Generated {len(img_infos)} word images")
            
            # Create video clips
            clips = [video]
            pos_y = int(video.h * position_y_ratio)
            
            for img_path, word_start, word_end in img_infos:
                txt_clip = ImageClip(img_path).set_start(word_start).set_end(word_end).set_position(
                    ("center", pos_y)
                )
                txt_clip = txt_clip.fadein(0.1)
                clips.append(txt_clip)
            
            logger.info(f"Created {len(clips)} video clips")
            
            # Compose and write final video
            final = CompositeVideoClip(clips)
            final.write_videofile(output_path, codec="libx264", fps=video.fps)
            logger.info(f"Successfully created subtitled video: {output_path}")
            
            # Clean up temporary files
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to create subtitled video: {e}")
            # Clean up on error
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            raise

        return output_path