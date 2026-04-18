"""
Core logging module.

Key Point:
Configures and provides a centralized logging system for the application.

Responsibilities:
- Configure logging format and level
- Output logs to console and file
- Ensure consistent logging across all modules

Architecture Role:
- System-level utility for monitoring and debugging
- Provides a unified logging interface across all layers

Layer Interaction:
- Used by: Core modules, Services, Error Handler, Routes
- Communicates with: File system (logs directory)

Data Flow:
Application starts
        ↓
Logger initialized via setup_logger()
        ↓
Log handlers configured (console + file)
        ↓
Modules log events using shared logger
        ↓
Logs written to console and log file

"""

#app.core.logger.py

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
