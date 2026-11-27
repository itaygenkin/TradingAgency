import re
from typing import Optional

from langchain_core.language_models import BaseChatModel
from pydantic import ValidationError

from src.trading_agency.config import AGENT_ROLE
from src.trading_agency.infrastructure.llm_factory import get_analysis_model
from src.trading_agency.domain.models import MarketAnalysisContent, MarketAnalysisResponse, MarketSnapshot
from src.trading_agency.utils.exceptions import MarketDataError
from src.trading_agency.utils.logger import get_logger

logger = get_logger("market_agent")

class MarketAnalystAgent:
    def __init__(self, llm: Optional[BaseChatModel] = None):
        """initializes the AI Analyst with the Gemini model"""
        self.structured_llm = get_analysis_model(MarketAnalysisContent)

    def analyze_market_data(self, market_data: list[MarketSnapshot], news_data: dict[str, str]) -> MarketAnalysisResponse:
        """
        Synthesizes price data and news into a professional trading report.
        :param market_data: the dictionary returned by get_premarket_data.
        :param news_data: the dictionary returned by get_news_data.
        :return: the report, extracted predictions, and model used for the analysis.
        """
        logger.info("Starting AI synthesis of market data and news.")
        prompt: str = (
            f"You are an {AGENT_ROLE}. Analyze the following pre-market data and news:\n"
            f"Prices: {market_data}\n"
            f"News: {news_data}\n\n"
            f"Instructions:\n"
            f"1. Generate a professional daily trading report in Markdown format. Use the following structure:\n"
            f"  - # Daily Pre-Market Analysis (Header 1)\n"
            f"  - ## Executive Summary (A brief paragraph about the overall market sentiment)\n"
            f"  - ## Stock Watchlist (A Markdown Table with columns: Ticker, Price Change%, Sentiment)\n"
            f"  - ## Deep Dive per Ticker (Header 3 for each stock, explaining the 'Why' behind the move based on news)\n"
            f"  - ## Trading Strategy (Key levels or warnings for the open)\n\n"
            f"2. Be specific, professional, and concise. Avoid generic statements.\n\n"
            f"3. Return the report and predictions in the requested structured output.\n"
            f"4. The predictions object must have one key per analyzed ticker, and each value must be exactly "
            f"Bullish, Bearish, or Neutral. Ensure its values match the sentiment in the report.\n"
        )

        response = self.structured_llm.invoke(prompt)
        try:
            parsed = response["parsed"]
            raw_response = response["raw"]
            parsing_error = response["parsing_error"]
            if parsing_error is not None or parsed is None:
                raise MarketDataError(f"couldn't parse structured market analysis from LLM response: {parsing_error}")

            content = MarketAnalysisContent.model_validate(parsed)
            if not content.report.strip():
                raise MarketDataError("LLM returned an empty market analysis report")

            expected_tickers = {snapshot.ticker for snapshot in market_data}
            actual_tickers = set(content.predictions)
            if actual_tickers != expected_tickers:
                raise MarketDataError(
                    f"structured predictions do not match the analyzed tickers "
                    f"(missing={expected_tickers - actual_tickers}, extra={actual_tickers - expected_tickers})"
                )

            response_metadata = getattr(raw_response, "response_metadata", {}) or {}
            used_model = response_metadata.get("model_name", "Unknown")
            return MarketAnalysisResponse(**content.model_dump(), model_used=used_model)
        except (KeyError, AttributeError, TypeError, ValidationError) as e:
            raise MarketDataError("couldn't parse structured market analysis from LLM response") from e

    @staticmethod
    def extract_predictions(full_report: str) -> dict[str, str]:
        if not full_report:
            raise MarketDataError("report is empty")

        predictions: dict[str, str] = {}
        pattern = r"DATA_START\n(.*?)\nDATA_END"
        match = re.search(pattern, full_report, re.DOTALL)

        if match:
            data_block = match.group(1)
            lines = data_block.strip().split("\n")
            for line in lines:
                if ':' in line:
                    split_line = filter(lambda x: x, line.split(':'))
                    ticker, move = split_line.__next__(), split_line.__next__()
                    predictions[ticker.strip()] = move.strip()

        logger.info(f"extracted {len(predictions)} predictions from report")
        return predictions
