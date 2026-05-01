from dataclasses import dataclass
from typing import Optional


@dataclass
class MarketSnapshot:
    """Blueprint for pre-market data fetched from yfinance."""
    ticker: str
    last_close: float
    last_session_change_pct: float
    pre_market_price: float
    pre_market_gap_pct: float
    prediction: Optional[str] = None  # will be filled after AI analysis
    report_path: Optional[str] = None

    def as_tuple(self) -> tuple:
        """Convert the MarketSnapshot instance into a tuple for database insertion."""
        return (
            self.ticker,
            self.last_close,
            self.pre_market_price,
            self.prediction or "Neutral",
            self.report_path or "",
        )
