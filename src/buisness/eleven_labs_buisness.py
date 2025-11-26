import logging
import os
import tempfile

from moviepy.editor import VideoFileClip

logger = logging.getLogger("HiLiteLogger")


class ElevenLabsBuisness:
    @staticmethod
    def extract_audio_bytes_from_video(video_path):
        """
        Extract audio from video file and return as bytes.

        Args:
            video_path: Path to the video file

        Returns:
            bytes: Audio data in MP3 format

        Raises:
            FileNotFoundError: If video file doesn't exist
            ValueError: If video has no audio track
            Exception: For other processing errors
        """
        logger.info(f"Starting audio extraction from: {video_path}")

        # Verify file exists
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            raise FileNotFoundError(f"Video file not found: {video_path}")

        video = None
        tmp = None

        try:
            # Load video
            video = VideoFileClip(video_path)
            logger.info(f"Video loaded successfully, duration: {video.duration}s")

            # Check if video has audio
            if video.audio is None:
                logger.error(f"Video has no audio track: {video_path}")
                raise ValueError(f"Video has no audio track: {video_path}")

            # Create temporary file
            tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            tmp_path = tmp.name
            tmp.close()
            logger.info(f"Created temporary audio file: {tmp_path}")

            # Extract audio
            video.audio.write_audiofile(tmp_path, logger=None)
            logger.info("Audio extraction completed")

            # Read audio bytes
            with open(tmp_path, "rb") as f:
                audio_bytes = f.read()

            logger.info(
                f"Audio bytes read successfully, size: {len(audio_bytes)} bytes"
            )
            return audio_bytes

        except FileNotFoundError:
            raise
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to extract audio from video: {e}")
            raise Exception(f"Failed to extract audio: {e}") from e

        finally:
            # Cleanup resources
            try:
                if video:
                    if video.audio:
                        video.audio.close()
                    video.close()
                    logger.info("Video resources closed")
            except Exception as e:
                logger.warning(f"Error closing video resources: {e}")

            # Remove temporary file
            if tmp:
                try:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                        logger.info("Temporary audio file removed")
                except Exception as e:
                    logger.warning(f"Error removing temporary file: {e}")
