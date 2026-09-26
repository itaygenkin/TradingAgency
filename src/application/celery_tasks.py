from entrypoints.celery_app import celery_app
from entrypoints.celery_app import CELERY_COUNTDOWN
from src.application.audit_service import PerformanceValidator
from src.domain.models import Prediction
from src.infrastructure.market_provider import MarketProvider
from src.infrastructure.repository import MarketRepository
from src.utils.logger import get_logger

logger = get_logger("CeleryTasks")


@celery_app.task(name="celery_tasks.validate_single_prediction", bind=True, max_retries=3)
def validate_single_prediction_task(self, prediction: Prediction):
    # TODO: Confirm whether Celery should receive a Prediction instance or a serialized dict payload.
    ticker  = prediction.ticker
    logger.info(f"[Celery] starting EOD validation task for {ticker}")

    try:
        market_results = MarketProvider.get_actual_market_performance_for_single_ticker(ticker)
        if not market_results or not market_results.is_success():
            logger.warning(f"[Celery] could not fetch EOD market data for {ticker}")
            return

        actual_data = market_results.value

        validator = PerformanceValidator()
        evaluation = validator.evaluate(prediction, actual_data)

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