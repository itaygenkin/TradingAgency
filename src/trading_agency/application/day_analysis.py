from dataclasses import asdict
from datetime import datetime, time
import sys
from typing import Any

from psycopg2 import OperationalError

import pytz

from src.trading_agency.application.celery_tasks import validate_single_prediction_task
from src.trading_agency.celery_app import celery_app
from src.trading_agency.domain.models import MarketSnapshot, Prediction
from src.trading_agency.config import WATCHLIST, REPORT_FILE_PREFIX
from src.trading_agency.infrastructure.llm_engine import MarketAnalystAgent
from src.trading_agency.infrastructure.market_provider import MarketProvider
from src.trading_agency.infrastructure.repository import MarketRepository
from src.trading_agency.utils.exceptions import DatabaseConnectionError, MarketDataError
from src.trading_agency.utils.logger import get_logger
from src.trading_agency.utils.utils import (
    clean_report,
    ensure_directories,
    save_report_to_file,
    update_market_data_prediction_and_report_path,
)

logger = get_logger("day_analysis")


def preliminary_conditions() -> bool:
    if not MarketProvider.is_market_open_today():
        exit()

    ensure_directories()

    # Skip task scheduling when Celery is unavailable in local development.
    try:
        return bool(celery_app.control.ping(timeout=1))
    except Exception:
        logger.warning("Celery is not available")
        return False


def schedule_night_audits(predictions: list[Prediction]) -> None:
    """schedule Celery validation tasks for each stock prediction ro run at US market close"""
    ny_tz = pytz.timezone("US/Eastern")
    now_ny = datetime.now(ny_tz)

    # define US market close time today
    market_close_time = ny_tz.localize(datetime.combine(now_ny.date(), time(16, 5)))
    eta_utc = market_close_time.astimezone(pytz.utc)
    scheduling_disabled = False

    for pred in predictions:
        if scheduling_disabled:
            break

        try:
            # launch a Celery task for each prediction to run at market close
            validate_single_prediction_task.apply_async(
                args=[asdict(pred)],
                eta=eta_utc,
            )
            logger.info(f"scheduled audit task for {pred.ticker} at {market_close_time} NY time")
        except OperationalError as e:
            logger.warning(f"Could not schedule audit task for {pred.ticker}: {e}")
            scheduling_disabled = True
        except Exception as e:
            logger.warning(f"Could not schedule audit task for {pred.ticker}: {e}")
            scheduling_disabled = True


def run_day_analysis() -> None:
    celery_available = preliminary_conditions()
    logger.info("starting day analysis pipeline")

    try:
        db = MarketRepository()
        agent = MarketAnalystAgent()

        if db.has_run_today():
            logger.info("day analysis has already been run today")
            return

        logger.info(f"step 1: fetching pre-market data and stock news for {len(WATCHLIST)} stocks")
        market_data: list[MarketSnapshot] = MarketProvider.get_premarket_data(WATCHLIST)
        news_data: dict[str, Any] = MarketProvider.get_stock_news_for_watchlist(WATCHLIST)

        logger.info("step 2: sending data to agent for analysis and creating report")
        report, used_model = agent.analyze_market_data(market_data, news_data)

        logger.info("step 3: extracting predictions from report")
        predictions_dict = agent.extract_predictions(report)

        logger.info("step 4: clean and save report to file")
        report = clean_report(report)
        report_path: str = save_report_to_file(report_name=REPORT_FILE_PREFIX, report_content=report)

        logger.info("preparing data to insert into database")
        update_market_data_prediction_and_report_path(market_data, predictions_dict, report_path)

        logger.info("step 5: inserting report into database")
        predictions = [Prediction.convert_snapshot_to_prediction(snapshot, used_model) for snapshot in market_data]
        db.bulk_insert_morning_predictions(predictions)

        if celery_available:
            logger.info(f"step 6: scheduling night audits")
            schedule_night_audits(predictions)
        else:
            logger.warning(f"step 6 skipped: Celery is not available. Night audits will not be scheduled. Run the night_audit.py script manually after market close to validate predictions.")

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
