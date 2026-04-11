from typing import Any

from src.logger import get_logger
from src.llm_engine import MarketAnalysisAgent
from src.config import WATCHLIST, REPORT_FILE_PREFIX
from src.market_provider import MarketProvider
from src.repository import MarketRepository
from src.utils import ensure_directories, save_report_to_file

logger = get_logger("day_analysis")


def run_day_analysis() -> None:
    logger.info("starting day analysis pipeline")
    ensure_directories()
    if not MarketProvider.is_market_open_today():
        return

    db = MarketRepository()
    agent = MarketAnalysisAgent()

    logger.info(f"step 1: fetching pre-market data and stock news for {len(WATCHLIST)} stocks")
    market_data: dict[str, Any] = MarketProvider.get_premarket_data(WATCHLIST)
    news_data: dict[str, Any] = MarketProvider.get_stock_news_for_watchlist(WATCHLIST)

    logger.info("step 2: sending data to agent for analysis and creating report")
    report = agent.analyze_market_data(market_data, news_data)

    logger.info("step 3: saving report to file")
    report_path: str = save_report_to_file(report_name=REPORT_FILE_PREFIX, report_content=report)

    logger.info("step 4: extracting predictions from report")
    predictions_dict = agent.extract_predictions(report)

    logger.info("step 5: inserting report into database")
    for ticker in WATCHLIST:
        market_data[ticker]["pred_move"] = predictions_dict.get(ticker, "Neutral")
        db.insert_morning_prediction(
            ticker=ticker,
            data=market_data[ticker],
            report_path=report_path
        )

    logger.info("day analysis completed and saved to DB")


if __name__ == "__main__":
    try:
        run_day_analysis()
    except Exception as e:
        logger.error(f"an error occurred during the pipeline execution: {str(e)}", exc_info=True)


