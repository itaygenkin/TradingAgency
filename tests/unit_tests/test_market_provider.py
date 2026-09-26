from unittest.mock import patch
import pandas as pd

from src.adapters.market_provider import MarketProvider
from src.models.models import MarketSnapshot


def test_market_snapshot_creation():
    """Test if the Data Class initializes correctly"""
    snapshot = MarketSnapshot(
        ticker="AAPL",
        yesterday_close_price=150.0,
        last_session_change_pct=1.5,
        pre_market_price=152.0,
        pre_market_gap_pct=1.33
    )

    assert snapshot.ticker == "AAPL"
    assert snapshot.pre_market_price == 152.0

@patch("yfinance.Ticker")
def test_get_premarket_data_success(mock_ticker):
    """
    Test marketProvider with a mocked yfinance response.
    This avoids network calls and ensures our logic is sound.
    """
    # 1. setup mock for stock.history()
    mock_hist = pd.DataFrame({
        "Close": [100.0, 110.0]
    }, index=pd.to_datetime(["2026-04-30", "2026-05-01"])) # Use actual dates for a more realistic mock
    mock_ticker.return_value.history.return_value = mock_hist

    #. setup mock for stock.fast_info
    mock_ticker.return_value.fast_info = {
        "last_price": 115.5, # Corrected key
        "regularMarketPreviousClose": 110.0
    }

    # 3. call the provider
    results = MarketProvider.get_premarket_data(tickers=["TEST"])

    # 4. assertions
    assert len(results) == 1
    assert isinstance(results[0], MarketSnapshot)
    assert results[0].ticker == "TEST"
    assert results[0].last_session_change_pct == 10.0  # (110 - 100) / 100 * 100
    assert results[0].pre_market_gap_pct == 5.0     # (115.5 - 110) / 110 * 100
