import logging
import os
import sys

from src.config import LOGS_DIR


class CustomFormatter(logging.Formatter):
    """Custom formatter that removes file extensions from filenames"""
    def format(self, record):
        # Remove file extension from filename
        record.filename = os.path.splitext(record.filename)[0]
        return super().format(record)


def get_logger(service_name: str, log_file: str = "app.log") -> logging.Logger:
    logger = logging.getLogger(service_name)

    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    log_format: str = "[%(asctime)s] [%(name)s] [%(levelname)s] - %(filename)s.%(funcName)s:  %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"

    formatter = CustomFormatter(log_format, datefmt=date_format)

    # Set the file path
    log_file_path: str = os.path.join(LOGS_DIR, log_file)

    # File handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(formatter)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

