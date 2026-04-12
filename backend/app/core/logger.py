"""
Global Error Handling
One centralized error handler.
"""

import logging
import os


def setup_logger():

    if not os.path.exists("logs"):
        os.makedirs("logs")

    logger = logging.getLogger("smart_farming")
    logger.setLevel(logging.INFO)

    if not logger.handlers:

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        file_handler = logging.FileHandler("logs/app.log")
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
