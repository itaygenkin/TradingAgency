from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional

from pydantic import BaseModel, Field


@dataclass
class MarketSnapshot:
    """Blueprint for pre-market data fetched from yfinance."""
    ticker: str
    yesterday_close_price: float
    last_session_change_pct: float
    pre_market_price: float
    pre_market_gap_pct: float
    prediction: Optional[str] = None  # will be filled after AI analysis
    report_path: Optional[str] = None


class MarketAnalysisContent(BaseModel):
    """Fields requested directly from the LLM using structured output."""
    report: str = Field(description="Complete daily market analysis report in Markdown format.")

    predictions: dict[str, Literal["Bullish", "Bearish", "Neutral"]] = Field(
        description="One prediction per analyzed ticker, using exactly Bullish, Bearish, or Neutral."
    )


class MarketAnalysisResponse(MarketAnalysisContent):
    """Validated structured result with the model that produced it."""
    model_used: str


@dataclass
class Prediction:
    """the prediction the llm model predict for a ticker."""
    ticker: str
    prev_close_price: float
    pre_market_price: float
    predicted_move: str
    status: str = "PENDING"
    llm_model: Optional[str] = None

    @staticmethod
    def convert_snapshot_to_prediction(market_snapshot: MarketSnapshot, llm_model: Optional[str] = None) -> Prediction:
        return Prediction(
            ticker=market_snapshot.ticker,
            prev_close_price=market_snapshot.yesterday_close_price,
            pre_market_price=market_snapshot.pre_market_price,
            predicted_move=market_snapshot.prediction or "Neutral",
            llm_model=llm_model,
            status="PENDING"
        )


@dataclass
class MarketPerformance:
    ticker: str
    open: float
    close: float
    actual_change_pct: float
