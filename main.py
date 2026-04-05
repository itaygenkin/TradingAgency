import os
import time
from datetime import datetime
from typing import Any

from src.logger import get_logger
from src.agent import MarketAnalysisAgent
from src.config import REPORTS_DIR, WATCHLIST, REPORT_FILE_PREFIX, REPORT_FILE_EXTENSION
from src.tools import get_premarket_data, get_stock_news

logger = get_logger("main_pipeline")

def ensure_directories() -> None:
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

def save_report_to_file(report_content: str) -> str:
    timestamp: str = datetime.now().strftime("%d-%m-%Y_%H-%M")
    filename: str = f"{REPORT_FILE_PREFIX}_{timestamp}.{REPORT_FILE_EXTENSION}"
    file_path: str = os.path.join(REPORTS_DIR, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return file_path

def run_agent_pipeline() -> None:
    """
    Executes the full agent workflow: Fetch -> Analyze -> Save.
    :return:
    """
    logger.info("Initializing Agent Pipeline with 'Eyes' (Web Search)")

    ensure_directories()

    # Step 1: getting prices
    logger.info(f"step 1: fetching pre-market data for {len(WATCHLIST)} stocks")
    market_prices: dict[str, Any] = get_premarket_data(WATCHLIST)

    # Step 2: Passing data to the Gemini Agent
    logger.info(f"step 2: sending data to Gemini for analysis...")
    news_context: dict[str, str] = {}
    for ticker in WATCHLIST:
        news_context[ticker] = get_stock_news(ticker)
        time.sleep(0.3)

    # step 3: analysis
    logger.info(f"step 3: sending data to Gemini for analysis")
    analyst = MarketAnalysisAgent()
    final_report = analyst.analyze_market_data(market_prices, news_context)

    # step 4: saving the output to a file
    logger.info(f"step 3: saving report to disk...")
    path: str = save_report_to_file(final_report)

    logger.info(f"Report saved to: {path}")
    logger.info(f"Pipeline Completed Successfully")

if __name__ == "__main__":
    try:
        run_agent_pipeline()
    except Exception as e:
        logger.error(f"An error occurred during the pipeline execution: {str(e)}", exc_info=True)


