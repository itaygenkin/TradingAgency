from datetime import datetime
import os
from typing import Any

from src.config import REPORTS_DIR, REPORT_FILE_EXTENSION
from src.models.result import Result


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

def clean_report(report: str) -> str:
    end_of_report = report.find("DATA_START")
    if end_of_report > 0:
        return report[:end_of_report]

    return report


def zip_prediction_and_actual_market_data(pending_predictions: dict[str, Any], actual_market_data: list[Result]) -> list[tuple[Any, Any]]:
    """
    Zips pending predictions with actual market data where the actual data is successful
    and a corresponding prediction exists.
    """
    zipped_data = []
    for actual_data in actual_market_data:
        if actual_data.is_success():
            ticker = actual_data.value.ticker
            prediction = pending_predictions.get(ticker)
            if prediction:
                zipped_data.append((prediction, actual_data.value))

    return zipped_data
