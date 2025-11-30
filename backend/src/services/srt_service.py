import logging
from pathlib import Path

from buisness.srt_buisness import SrtBuisness
from config.settings import settings

logger = logging.getLogger("HiLiteLogger")


class SrtService:
    def __init__(self, srt_output_file):
        """
        Initialize SRT service with output file path.

        Args:
            srt_output_file: Filename for the SRT file (not full path)

        Raises:
            ValueError: If SRT_DIR_PATH is not set
        """
        srt_dir = settings.SRT_DIR_PATH
        if not srt_dir:
            # Use default value if not set
            srt_dir = "tmp/srt"
            logger.warning(f"SRT_DIR_PATH not set, using default: {srt_dir}")

        # Create directory if it doesn't exist
        Path(srt_dir).mkdir(parents=True, exist_ok=True)

        self.srt_output_file = str(Path(srt_dir) / srt_output_file)
        logger.info(f"SrtService initialized with output file: {self.srt_output_file}")

    def convert_transcription_into_srt(self, transcription):
        try:
            logger.info("Starting transcription to SRT conversion")
            words = transcription.words
            logger.info(f"Processing {len(words)} words from transcription")

            lines = SrtBuisness.transcription_to_srt_lines(words)
            logger.info(f"Generated {len(lines)} SRT lines")

            with open(self.srt_output_file, "w", encoding="utf-8") as f:
                for line in lines:
                    f.write(line + "\n")

            logger.info(f"Successfully wrote SRT file: {self.srt_output_file}")
            return self.srt_output_file
        except Exception as e:
            logger.error(f"Failed to convert transcription to SRT: {e}")
            raise
