from datetime import datetime
import time
from typing import Optional

import yfinance as yf
import pandas as pd
from langchain_community.tools import DuckDuckGoSearchRun

from src.models.models import MarketSnapshot, MarketPerformance
from src.models.result import Result
from src.models.result_status import ResultStatus
from src.utils.exceptions import MarketDataError
from src.utils.logger import get_logger

logger = get_logger("market_tools")


class MarketProvider:
    _search_tool = DuckDuckGoSearchRun()

    @staticmethod
    def get_premarket_data(tickers: list[str]) -> list[MarketSnapshot]:
        """
        Fetches pre-market or latest trading data for a given list of stock tickers.
        :param tickers: list of stock symbols (e.g., ["AAPL", "AKAM"]).
        :return: a dictionary containing price, change percentage, and volume for each ticker.
        """
        logger.info(f"fetching market data for {len(tickers)} stocks.")

        results: list[MarketSnapshot] = []
        for ticker in tickers:
            snapshot: Optional[MarketSnapshot] = MarketProvider._fetch_single_ticker_premarket_data(ticker)
            if snapshot:
                results.append(snapshot)

        if not results:
            logger.warning("No market data could be fetched for any ticker. Returning an empty list.")
            return []

        return results

    @staticmethod
    def _fetch_single_ticker_premarket_data(ticker: str) -> Optional[MarketSnapshot]:
        """
        Helper function to fetch pre-market or latest trading data for a single stock ticker.
        :param ticker: stock symbol (e.g., "AAPL").
        :return: a dictionary containing price, change percentage, and volume for the ticker, or a failure status.
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")

            if len(hist) < 2:
                raise MarketDataError(f"no historical data found for {ticker}")

            yesterday_close = float(hist['Close'].iloc[-1])
            day_before_yesterday_close = float(hist['Close'].iloc[-2])
            yesterday_change_pct = ((yesterday_close - day_before_yesterday_close) / day_before_yesterday_close) * 100

            # Data from fast_info (More accurate for real-time)
            info = stock.fast_info
            current_pre_market_price = info["last_price"]
            # Use regularMarketPreviousClose to ensure we compare against the 4:00 PM close
            reg_prev_close = info["regularMarketPreviousClose"]
            pre_market_gap_pct = ((current_pre_market_price - reg_prev_close) / reg_prev_close) * 100

            return MarketSnapshot(
                ticker=ticker,
                yesterday_close_price=round(reg_prev_close, 2),
                last_session_change_pct=round(yesterday_change_pct, 2),
                pre_market_price=round(current_pre_market_price, 2),
                pre_market_gap_pct=round(pre_market_gap_pct, 2)
            )

        except Exception as e:
            logger.error(f"error fetching data for {ticker}: {str(e)}")
            return None

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
    def get_actual_market_performance(tickers: list[str]) -> list[Result[MarketPerformance]]:
        logger.info(f"fetching actual market performance for {len(tickers)} stocks")

        results: list[Result[MarketPerformance]] = []
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                df: pd.DataFrame = stock.history(period="1d", interval="1m")

                if not df.empty:
                    open_price: float = round(float(df["Open"].iloc[0]), 2)
                    current_price: float = round(float(df["Close"].iloc[-1]), 2)
                    day_change_pct: float = round(((current_price - open_price) / open_price) * 100, 2)

                    stock_performance: MarketPerformance = MarketPerformance(
                        ticker=ticker,
                        open=open_price,
                        close=current_price,
                        actual_change_pct=day_change_pct,
                    )
                    results.append(Result(status=ResultStatus.SUCCESS, value=stock_performance))
                    logger.info(f"validated {ticker}: open ${open_price}, Close ${current_price}")
                else:
                    results.append(Result(status=ResultStatus.FAILURE,
                                          value=None,
                                          msg=f"no historical data found for {ticker}"))
                    logger.warning(f"no intraday data for {ticker} validation")

            except Exception as e:
                logger.error(f"error validating performance for {ticker}: {str(e)}")

        return results

    @staticmethod
    def is_market_open_today() -> bool:
        today = datetime.today()
        if today.weekday() >= 5:  # Saturday and Sunday
            logger.info(f"today({today.weekday()}) is weekend. market is closed.")
            return False
        # TODO: handle holidays
        return True

