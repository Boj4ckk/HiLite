from elevenlabs.client import ElevenLabs
from buisness.eleven_labs_buisness import ElevenLabsBuisness
import logging

logger = logging.getLogger("HiLiteLogger")

class ElevenLabsService:

    def __init__(self, api_key):
        """
        Initialize ElevenLabs service with API key.
        
        Args:
            api_key: ElevenLabs API key
            
        Raises:
            ValueError: If api_key is None or empty
        """
        if not api_key:
            raise ValueError("ElevenLabs API key is required")
        
        self.api_key = api_key
        try:
            self.eleven_labs_client = ElevenLabs(api_key=self.api_key)
            logger.info("ElevenLabs service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ElevenLabs client: {e}")
            raise
    

    def speech_to_text(self, video_path, language_code, model_id="scribe_v1", tag_audio_events=True, diarize=True):
        """
        Convert video speech to text using ElevenLabs API.
        
        Args:
            video_path: Path to video file
            language_code: Language code (e.g., 'fr', 'en')
            model_id: Transcription model to use
            tag_audio_events: Whether to tag audio events (laugh, applause, etc.)
            diarize: Whether to annotate who is speaking
            
        Returns:
            Transcription object from ElevenLabs
            
        Raises:
            FileNotFoundError: If video file doesn't exist
            ValueError: If video has no audio
            Exception: For API errors or processing failures
        """
        logger.info(f"Starting speech-to-text for video: {video_path}, language: {language_code}")
        
        try:
            # Extract audio from video
            audio_data = ElevenLabsBuisness.extract_audio_bytes_from_video(video_path)
            logger.info(f"Audio extracted successfully, size: {len(audio_data)} bytes")
            
            # Call ElevenLabs API
            logger.info("Sending audio to ElevenLabs API for transcription...")
            transcription = self.eleven_labs_client.speech_to_text.convert(
                file=audio_data,
                model_id=model_id,
                tag_audio_events=tag_audio_events,
                language_code=language_code,
                diarize=diarize
            )
            
            logger.info(f"Transcription completed successfully, words count: {len(transcription.words)}")
            return transcription
            
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Video processing error: {e}")
            raise
        except Exception as e:
            logger.error(f"ElevenLabs API error during transcription: {e}")
            raise Exception(f"Failed to transcribe audio: {e}") from e


    
