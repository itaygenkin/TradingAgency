from src.models.result import Result, EvaluationValue
from src.utils.logger import get_logger
from src.core_logic.audit_service import PerformanceValidator
from src.adapters.market_provider import MarketProvider
from src.adapters.repository import MarketRepository
from src.utils.utils import zip_prediction_and_actual_market_data

logger = get_logger("ValidationMain")

def run_night_audit() -> None:
    logger.info("starting Night Audit pipeline")

    db = MarketRepository()
    validator = PerformanceValidator()

    # pop all prediction of the current day
    pending_predictions = db.get_pending_predictions()

    if not pending_predictions:
        logger.info(f"no pending predictions found for today. skipping validation.")
        return

    # data extraction
    tickers = list(pending_predictions.keys())
    actual_market_data_result_list = MarketProvider.get_actual_market_performance(tickers)

    # zip the prediction and the actual data
    zipped_prediction_actual_market_data = zip_prediction_and_actual_market_data(pending_predictions,
                                                                                 actual_market_data_result_list)

    updates_to_process: list = []
    for prediction, actual in zipped_prediction_actual_market_data:
        evaluation: Result[EvaluationValue] = validator.evaluate(prediction, actual)
        if evaluation.is_success():
            updates_to_process.append((
                actual.open,
                actual.actual_change_pct,
                evaluation.value.is_correct,
                evaluation.value.confidence_score,
                actual.ticker
            ))
        else:
            logger.info(f"failed to evaluate performance for {actual.ticker}: {evaluation.msg}")

    if updates_to_process:
        db.bulk_update_evening_validation(updates_to_process)

    logger.info(f"night audit completed. processed {len(updates_to_process)} records.")


if __name__ == "__main__":
    if not MarketProvider.is_market_open_today():
        exit(1)

    run_night_audit()
