from typing import Any

from src.llm_engine import MarketAnalysisAgent
from src.config import VALIDATION_LOG_FILE
from src.logger import get_logger


logger = get_logger("ValidationService", log_file=VALIDATION_LOG_FILE)


class PerformanceValidator:
    def __init__(self):
        self.agent = MarketAnalysisAgent()

    def evaluate(self, prediction_row: dict[str, Any], actual_data: dict[str, Any]) -> tuple[bool, int]:
        """
        compares morning predictions with evening reality using the LLM
        :param prediction_row: dictionary containing ticker, predicted_move, etc.
        :param actual_data: dictionary containing open, close, and actual_change_pct.
        :return: a tuple of (is_correct: bool, score: int).
        """
        ticker = prediction_row.get("ticker")
        logger.info(f"evaluating performance for {ticker}")

        prompt = (
            f"Review the following trading prediction for {ticker}:\n"
            f"- Predicted Move: {prediction_row.get("predicted_move")}\n"
            f"- Actual Market Open Price: ${actual_data.get("open")}\n"
            f"- Actual Price Change during session: {actual_data.get("actual_change_pct")}%\n\n"
            f"Criteria:\n"
            f"1. Was the direction (Bullish/Bearish/Neutral) correct based on the actual move?\n"
            f"2. Provide a confidence score between 0 and 100 based on accuracy.\n\n"
            f"Return only a comma-separated string in this format: [True/False], [Score]\n"
            f"Example: True, 85"
        )

        try:
            response = self.agent.llm.invoke(prompt)
            result_text = str(response.content).strip()

            # parsing the llm response
            parts = result_text.split(",")
            is_correct = parts[0].strip().lower() == "true"
            score = int(parts[1].strip())

            logger.info(f"audit result for {ticker}: Correct: {is_correct}, Score: {score}")
            return is_correct, score
        except Exception as e:
            logger.error(f"failed to evaluate performance for {ticker}: {e}")
            # default fallback in case of llm error
            return False, 0


