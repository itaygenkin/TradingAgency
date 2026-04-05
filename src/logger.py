import logging
import sys
from src.config import LOG_FILE


def setup_logger() -> logging.Logger:
    """
    Configures the central logger for the application.
    Outputs to both a file and the console.
    """
    logger = logging.getLogger("TradingAgent")
    logger.setLevel(logging.INFO)

    # Format for our logs: Timestamp - Name - Level - Message
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Handler 1: Writing to a file
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)

    # Handler 2: Printing to console (STDOUT)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

logger = setup_logger()

