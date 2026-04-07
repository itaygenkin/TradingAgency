import time
from typing import Any

from src.logger import get_logger
from src.agent import MarketAnalysisAgent
from src.config import WATCHLIST, REPORT_FILE_PREFIX
from src.tools import get_premarket_data, get_stock_news
from src.utils import ensure_directories, save_report_to_file

logger = get_logger("main_pipeline")


def run_agent_pipeline() -> None:
    """
    Executes the full agent workflow: Fetch -> Analyze -> Save.
    :return:
    """
    logger.info("Initializing Agent Pipeline with 'Eyes' (Web Search)")

    ensure_directories()

    logger.info(f"step 1: fetching pre-market data for {len(WATCHLIST)} stocks")
    market_prices: dict[str, Any] = get_premarket_data(WATCHLIST)

    logger.info(f"step 2: sending data to Gemini for analysis")
    news_context: dict[str, str] = {}
    for ticker in WATCHLIST:
        news_context[ticker] = get_stock_news(ticker)
        time.sleep(0.3)

    logger.info(f"step 3: sending data to Gemini for analysis")
    analyst = MarketAnalysisAgent()
    final_report_content = analyst.analyze_market_data(market_prices, news_context)

    logger.info(f"step 3: saving report to disk...")
    path: str = save_report_to_file(report_name=REPORT_FILE_PREFIX, report_content=final_report_content)

    logger.info(f"report saved to: {path}")
    logger.info(f"pipeline Completed Successfully")

if __name__ == "__main__":
    try:
        run_agent_pipeline()
    except Exception as e:
        logger.error(f"An error occurred during the pipeline execution: {str(e)}", exc_info=True)


