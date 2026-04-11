from datetime import datetime
import time
from typing import Any

import yfinance as yf
import pandas as pd
from langchain_community.tools import DuckDuckGoSearchRun

from src.logger import get_logger

logger = get_logger("market_tools")


class MarketProvider:
    _search_tool = DuckDuckGoSearchRun()

    @staticmethod
    def get_premarket_data(tickers: list[str]) -> dict[str, Any]:
        """
        Fetches pre-market or latest trading data for a given list of stock tickers.
        :param tickers: list of stock symbols (e.g., ["AAPL", "AKAM"]).
        :return: a dictionary containing price, change percentage, and volume for each ticker.
        """
        results: dict[str, Any] = {}
        logger.info(f"fetching market data for {len(tickers)} stocks.")

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
                    results[ticker] = {"status": "failure"}

            except Exception as e:
                logger.error(f"error fetching data for {ticker}: {str(e)}")
                results[ticker] = {"status": "failure"}

        return results
    @staticmethod
    def _get_stock_news(ticker: str) -> str:
        """
        searches for the most recent news for a specific ticker.
        """
        logger.info(f"searching web for {ticker} news")
        query: str = f"latest {ticker} stock market news and catalysts"

        try:
            # Performing the search using DuckDuckGo
            search_results: str = MarketProvider._search_tool.invoke(query)
            return search_results
        except Exception as e:
            logger.error(f"search failed for {ticker}: {str(e)}")
            return "No recent news found."

    @staticmethod
    def get_stock_news_for_watchlist(tickers: list[str]) -> dict[str, str]:
        results: dict[str, str] = {}
        for ticker in tickers:
            results[ticker] = MarketProvider._get_stock_news(ticker)
            time.sleep(0.3)  # to avoid hitting search rate limits

        return results

    @staticmethod
    def get_actual_market_performance(tickers: list[str]) -> dict[str, dict[str, float]]:
        logger.info(f"fetching actual market performance for {len(tickers)} stocks")
        actual_results: dict[str, dict[str, float | None]] = {}
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                df: pd.DataFrame = stock.history(period="1d", interval="1m")

                if not df.empty:
                    open_price: float = float(df["Open"].iloc[0])
                    current_price: float = float(df["Close"].iloc[-1])
                    day_change_pct: float = ((current_price - open_price) / open_price) * 100

                    actual_results[ticker] = {
                        "open": round(open_price, 2),
                        "close": round(current_price, 2),
                        "actual_change_pct": round(day_change_pct, 2),
                    }
                    logger.info(f"validated {ticker}: open ${open_price}, Close ${current_price}")
                else:
                    actual_results[ticker] = {
                        "open": None,
                        "close": None,
                        "actual_change_pct": None,
                    }
                    logger.warning(f"no intraday data for {ticker} validation")

            except Exception as e:
                logger.error(f"error validating performance for {ticker}: {str(e)}")

        return actual_results

    @staticmethod
    def is_market_open_today() -> bool:
        today = datetime.today()
        if today.weekday() >= 5:  # Saturday and Sunday
            logger.info("today is weekend. market is closed.")
            return False
        # TODO: handle holidays
        return True

