from datetime import datetime
import os

from src.config import REPORTS_DIR, REPORT_FILE_EXTENSION


def ensure_directories() -> None:
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

def save_report_to_file(report_name: str, report_content: str) -> str:
    timestamp: str = datetime.now().strftime("%d-%m-%Y_%H-%M")
    filename: str = f"{report_name}_{timestamp}.{REPORT_FILE_EXTENSION}"
    file_path: str = os.path.join(REPORTS_DIR, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return file_path