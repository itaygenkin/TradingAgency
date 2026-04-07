import os

from src.logger import get_logger
from src.validator import run_validation_pipeline

logger = get_logger("ValidationMain")

def get_latest_report() -> str:
    """
    helper to find and read the most recent report file
    """
    reports_dir: str = "data/reports"
    files = [os.path.join(reports_dir, f) for f in os.listdir(reports_dir) if f.endswith(".md")]
    latest_file = max(files, key=os.path.getctime)

    with open(latest_file, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    try:
        report_content: str = get_latest_report()
        run_validation_pipeline(report_content)
    except Exception as e:
        logger.error(f"validation failed: {e}")




