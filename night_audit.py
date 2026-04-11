from src.logger import get_logger
from src.audit_service import PerformanceValidator
from src.market_provider import MarketProvider
from src.repository import MarketRepository

logger = get_logger("ValidationMain")

def run_night_audit() -> None:
    logger.info("starting Night Audit pipeline")
    if not MarketProvider.is_market_open_today():
        return
    db = MarketRepository()
    validator = PerformanceValidator()

    # pop all prediction of the current day
    pending_predictions = db.get_pending_predictions()

    if not pending_predictions:
        logger.info(f"no pending predictions found for today. skipping validation.")
        return

    # data extraction
    tickers = [prediction["ticker"] for prediction in pending_predictions]
    actual_market_data = MarketProvider.get_actual_market_performance(tickers)

    for prediction in pending_predictions:
        ticker = prediction["ticker"]
        actual = actual_market_data.get(ticker)

        if not actual:
            continue

        is_correct, score = validator.evaluate(prediction, actual)

        db.update_evening_validation(
            ticker=ticker,
            actual_data=actual,
            is_correct=is_correct,
            score=score
        )

    logger.info(f"night audit completed for {len(pending_predictions)} pending predictions")


if __name__ == "__main__":
    run_night_audit()




