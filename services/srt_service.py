from pathlib import Path
from elevenlabs import types

from buisness.srt_buisness import SrtBuisness
import os
import logging

logger = logging.getLogger("HiLiteLogger")

class SrtService:
    def __init__(self, srt_output_file):
        self.srt_output_file = str(Path(os.getenv("SRT_DIR_PATH")) / srt_output_file)
        self.srt_buisness = SrtBuisness()
        logger.info(f"SrtService initialized with output file: {self.srt_output_file}")

    def convert_transcription_into_srt(self, transcription):
        try:
            logger.info("Starting transcription to SRT conversion")
            words = transcription.words
            logger.info(f"Processing {len(words)} words from transcription")
            
            lines = self.srt_buisness.transcription_to_srt_lines(words)
            logger.info(f"Generated {len(lines)} SRT lines")
            
            with open(self.srt_output_file, "w", encoding="utf-8") as f:
                for line in lines:
                    f.write(line + "\n")
            
            logger.info(f"Successfully wrote SRT file: {self.srt_output_file}")
            return self.srt_output_file
        except Exception as e:
            logger.error(f"Failed to convert transcription to SRT: {e}")
            raise


                

        

