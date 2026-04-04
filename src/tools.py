from csv import excel
from typing import Any

import yfinance as yf
import pandas as pd


def get_premarket_data(tickers: list[str]) -> dict[str, Any]:
    """
    Fetches pre-market or latest trading data for a given list of stock tickers.
    :param tickers: list of stock symbols (e.g., ["AAPL", "AKAM"]).
    :return: a dictionary containing price, change percentage, and volume for each ticker.
    """
    results: dict[str, Any] = {}

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)

            # Fetching 1-minute interval data for the last day to capture pre-market
            # Note: Pre-market data availability depends on the time of day
            df: pd.DataFrame = stock.history(period="1d", interval="1m", prepost=True)

            if not df.empty:
                last_row = df.iloc[-1]
                current_price: float = float(last_row["Close"])

                # Fetching previous close to calculate price movement
                prev_close: float = stock.info.get("previousClose", current_price)
                price_change: float = current_price - prev_close
                change_percentage: float =( price_change / current_price) * 100

                results[ticker] = {
                    "status": "success",
                    "price": round(current_price, 2),
                    "change_pct": round(change_percentage, 2),
                    "volume": int(last_row["Volume"]),
                    "timestamp": str(df.index[-1])
                }
            else:
                results[ticker] = {"status": "error", "message": "No data found"}

        except Exception as e:
            results[ticker] = {"status": "error", "message": str(e)}

    return results



