import sys
from typing import Any

from src.models.models import MarketSnapshot, Prediction
from src.utils.exceptions import MarketDataError, DatabaseConnectionError
from src.utils.logger import get_logger
from src.core_logic.llm_engine import MarketAnalysisAgent
from src.config import WATCHLIST, REPORT_FILE_PREFIX
from src.adapters.market_provider import MarketProvider
from src.adapters.repository import MarketRepository
from src.utils.utils import ensure_directories, save_report_to_file, clean_report

logger = get_logger("day_analysis")


def preliminary_conditions() -> None:
    if not MarketProvider.is_market_open_today():
        exit()

    ensure_directories()


def run_day_analysis() -> None:
    preliminary_conditions()
    logger.info("starting day analysis pipeline")

    try:
        db = MarketRepository()
        agent = MarketAnalysisAgent()

        if db.has_run_today():
            logger.info("day analysis has already been run today")
            return

        logger.info(f"step 1: fetching pre-market data and stock news for {len(WATCHLIST)} stocks")
        market_data: list[MarketSnapshot] = MarketProvider.get_premarket_data(WATCHLIST)
        news_data: dict[str, Any] = MarketProvider.get_stock_news_for_watchlist(WATCHLIST)

        logger.info("step 2: sending data to agent for analysis and creating report")
        report = agent.analyze_market_data(market_data, news_data)

        logger.info("step 3: extracting predictions from report")
        predictions_dict = agent.extract_predictions(report)  # TODO: verify it runs properly

        logger.info("step 4: clean and save report to file")
        report = clean_report(report)
        report_path: str = save_report_to_file(report_name=REPORT_FILE_PREFIX, report_content=report)

        logger.info("preparing data to insert into database")
        for snapshot in market_data:
            snapshot.prediction = predictions_dict.get(snapshot.ticker, "Neutral")
            snapshot.report_path = report_path

        logger.info("step 5: inserting report into database")
        db.bulk_insert_morning_predictions(map(Prediction.convert_snapshot_to_prediction, market_data))

    except DatabaseConnectionError as e:
        logger.error(f"DATABASE CONNECTION ERROR: {e}")
        sys.exit(1)
    except MarketDataError as e:
        logger.error(f"DATA ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"UNEXPECTED EXCEPTION: {e}")
        sys.exit(1)
    else:
        logger.info("day analysis completed")


if __name__ == "__main__":
    run_day_analysis()

