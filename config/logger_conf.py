

import logging
import logging.handlers


def setup_logger():
    logger = logging.getLogger("HiLiteLogger")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        "app.log", maxBytes=5*1024*1024, backupCount=3
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    return logger