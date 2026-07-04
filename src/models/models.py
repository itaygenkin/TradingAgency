from dataclasses import dataclass
from typing import Optional


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


@dataclass
class Prediction:
    """the prediction the llm model predict for a ticker."""
    ticker: str
    yesterday_close_price: float
    pre_market_price: float
    predicted_move: str
    report_path: Optional[str]
    llm_model: Optional[str]
    status: str = "PENDING"

    @staticmethod
    def convert_snapshot_to_prediction(market_snapshot: MarketSnapshot, llm_model: Optional[str] = None) -> Prediction:
        return Prediction(
            ticker=market_snapshot.ticker,
            yesterday_close_price=market_snapshot.yesterday_close_price,
            pre_market_price=market_snapshot.pre_market_price,
            predicted_move=market_snapshot.prediction or "Neutral",
            report_path=market_snapshot.report_path,
            llm_model=llm_model,
            status="PENDING"
        )


@dataclass
class MarketPerformance:
    ticker: str
    open: float
    close: float
    actual_change_pct: float