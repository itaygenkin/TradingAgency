from typing import Any

from src.llm_engine import MarketAnalysisAgent
from src.config import VALIDATION_LOG_FILE, WATCHLIST, VALIDATION_REPORT_PREFIX
from src.logger import get_logger
from src.market_provider import get_actual_market_performance
from src.utils import save_report_to_file

logger = get_logger("ValidationService", log_file=VALIDATION_LOG_FILE)


class PerformanceValidator:
    def __init__(self):
        self.agent = MarketAnalysisAgent()

    def validate_predictions(self, pre_market_summary: str, actual_data: dict[str, Any]) -> str:
        """
        Hybrid approach: Use AI to compare the morning's report with evening's reality.
        """
        logger.info("starting hybrid validation analysis")

        prompt: str = (
            f"You are an Expert Trading Auditor. Below is the Pre-Market Report you wrote earlier today:\n"
            f"--- MORNING REPORT ---\n{pre_market_summary}\n\n"
            f"And here is what actually happened in the market (Open vs Close): {actual_data}\n\n"
            f"Task:\n"
            f"1. Compare your predictions to actual results.\n"
            f"2. Identify where you were accurate and where you missed the mark.\n"
            f"3. Provide a 'Confidence Score' (0-100) for today's analysis.\n"
            f"4. Suggest one improvement for tomorrow's pre-market logic.\n"
            f"Keep it brief and professional."
        )

        response = self.agent.llm.invoke(prompt)
        if response and "text" in response.content[0]:
            return response.content[0]["text"]

        return "Error while analyzing performance data."


def run_validation_pipeline(morning_report_content: str) -> None:
    """
    main entry point for the validation service.
    """
    logger.info("initializing validation pipeline")

    # step 1: fetch actual data using GET/yfinance
    actual_stats = get_actual_market_performance(WATCHLIST)

    # step 2: run AI analysis
    validator = PerformanceValidator()
    audit_report = validator.validate_predictions(morning_report_content, actual_stats)

    # step 3: output results
    logger.info("validation complete. storing results")
    path: str = save_report_to_file(report_name=VALIDATION_REPORT_PREFIX, report_content=audit_report)

    logger.info(f"report saved to: {path}")
    logger.info(f"pipeline Completed Successfully")

