import os
from celery import Celery

from src.adapters.market_provider import MarketProvider
from src.adapters.repository import MarketRepository
from src.core_logic.audit_service import PerformanceValidator
from src.utils.logger import get_logger

logger = get_logger("CeleryTasks")

CELERY_COUNTDOWN = 90  # time in seconds
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "validation_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/New_York",
    enable_utc=True,
)


@celery_app.task(name="tasks.validate_single_prediction", bind=True, max_retries=3)
def validate_single_prediction_task(self, prediction_row: dict):
    ticker  = prediction_row.get("ticker")
    logger.info(f"[Celery] starting EOD validation task for {ticker}")

    try:
        market_results = MarketProvider.get_actual_market_performance([ticker])
        if not market_results or not market_results[0].is_success():
            logger.warning(f"[Celery] could not fetch EOD market data for {ticker}")
            return

        actual_data = market_results[0].value

        validator = PerformanceValidator()
        evaluation = validator.evaluate(prediction_row, actual_data)

        if evaluation.is_success():
            db = MarketRepository()
            update_data = [
                (actual_data.open,
                 actual_data.actual_change_pct,
                 evaluation.value.is_correct,
                 evaluation.value.confidence_score,
                 ticker,)
            ]
            db.bulk_update_evening_validation(update_data)
            logger.info(f"[Celery] successfully validated and updated prediction for {ticker}")
        else:
            logger.error(f"[Celery] failed to validate and update prediction for {ticker}: {evaluation.msg}")

    except Exception as e:
        logger.error(f"[Celery] Error in task for {ticker}: {e}")
        raise self.retry(exc=e, countdown=CELERY_COUNTDOWN)
