import os
from datetime import datetime
from typing import Any

from src.logger import get_logger
from src.agent import MarketAnalysisAgent
from src.config import REPORTS_DIR, WATCHLIST, REPORT_FILE_PREFIX
from src.tools import get_premarket_data

logger = get_logger("market_analyzer")

def ensure_directories() -> None:
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

def save_report_to_file(report_content: str) -> str:
    timestamp: str = datetime.now().strftime("%d-%m-%Y_%H-%M")
    filename: str = f"{REPORT_FILE_PREFIX}_{timestamp}.txt"
    file_path: str = os.path.join(REPORTS_DIR, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return file_path

def run_agent_pipeline() -> None:
    """
    Executes the full agent workflow: Fetch -> Analyze -> Save.
    :return:
    """
    logger.info("Starting pipeline execution...")

    ensure_directories()

    # Step 1: Fetching data using our tool
    logger.info(f"Step 1: Fetching pre-market data for {len(WATCHLIST)} stocks...")
    raw_market_data: dict[str, Any] = get_premarket_data(WATCHLIST)

    # Step 2: Passing data to the Gemini Agent
    logger.info(f"Step 2: Sending data to Gemini for analysis...")
    analyst = MarketAnalysisAgent()
    analyzed_report = analyst.analyze_market_data(raw_market_data)

    # Step 3: Saving the output to a file
    logger.info(f"Step 3: Saving report to disk...")
    path: str = save_report_to_file(analyzed_report)

    logger.info(f"Pipeline Completed Successfully")
    logger.info(f"Report saved to: {path}")

if __name__ == "__main__":
    try:
        run_agent_pipeline()
    except Exception as e:
        logger.error(f"An error occurred during the pipeline execution: {str(e)}", exc_info=True)


