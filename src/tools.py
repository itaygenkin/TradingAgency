from typing import Any

import yfinance as yf
import pandas as pd
from langchain_community.tools import DuckDuckGoSearchRun

from src.logger import get_logger

logger = get_logger("market_tools")
search_tool = DuckDuckGoSearchRun()


def get_premarket_data(tickers: list[str]) -> dict[str, Any]:
    """
    Fetches pre-market or latest trading data for a given list of stock tickers.
    :param tickers: list of stock symbols (e.g., ["AAPL", "AKAM"]).
    :return: a dictionary containing price, change percentage, and volume for each ticker.
    """
    results: dict[str, Any] = {}
    logger.info(f"Fetching market data for {len(tickers)} stocks.")

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            df: pd.DataFrame = stock.history(period="1d", interval="1m", prepost=True)

            if not df.empty:
                last_price: float = float(df["Close"].iloc[-1])
                prev_close: float = stock.info.get("previousClose", last_price)
                change_pct: float = ((last_price - prev_close) / prev_close) * 100

                results[ticker] = {
                    "status": "success",
                    "price": round(last_price, 2),
                    "change_pct": round(change_pct, 2),
                    "volume": int(df["Volume"].iloc[-1]),
                    "timestamp": str(df.index[-1])
                }
            else:
                logger.warning(f"No data for {ticker}")

        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {str(e)}")

    return results

def get_stock_news(ticker: str) -> str:
    """
    searches for the most recent news for a specific ticker.
    """
    logger.info(f"Searching web for {ticker} news...")
    query: str = f"latest {ticker} stock market news and catalysts"

    try:
        # Performing the search using DuckDuckGo
        search_results: str = search_tool.invoke(query)
        return search_results
    except Exception as e:
        logger.error(f"search failed for {ticker}: {str(e)}")
        return "No recent news found."
