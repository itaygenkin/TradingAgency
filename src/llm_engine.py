import os
import re

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Any

from src.config import MODEL_NAME, AGENT_ROLE, TEMPERATURE
from src.logger import get_logger

logger = get_logger("market_agent")
load_dotenv()

class MarketAnalysisAgent:
    def __init__(self):
        """
        initializes the AI Analyst with the Gemini model
        """
        api_key = os.getenv("GOOGLE_API_KEY", "")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")

        self.llm: ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            google_api_key=api_key,
            temperature=TEMPERATURE
        )

    def analyze_market_data(self, market_data: dict[str, Any], news_data: dict[str, str]) -> str:
        """
        Synthesizes price data and news into a professional trading report.
        :param market_data: the dictionary returned by get_premarket_data.
        :param news_data: the dictionary returned by get_news_data.
        :return: a string containing the AI's analysis and recommendation.
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
            f"3. CRITICAL TECHNICAL REQUIREMENTS:\n"
            f"At the very end of you response, after the entire report, you must add a technical data block for system parsing."
            f"This block must be titled 'DATA_SUMMARY' and follow this exact format:\n"
            f"DATA_START\n"
            f"TICKER:MOVE\n"
            f"DATA_END\n"
            f"replace 'MOVE' with exactly one of the following labels: Bullish, Bearish or Neutral."
            f"Ensure the sentiment in the table matches the move in this data block.\n\n"
            f"EXAMPLE:\n"
            f"DATA_START\n"
            f"AAPL:Bullish\n"
            f"TSLA:Bearish\n"
            f"NVDA:Neutral\n"
            f"DATA_END\n"
        )

        response = self.llm.invoke(prompt)
        if response and "text" in response.content[0]:
            return response.content[0]["text"]

        return "Error while analyzing market data."

    @staticmethod
    def extract_predictions(full_report: str) -> dict[str, str]:
        predictions: dict[str, str] = {}
        pattern = r"DATA_START\n(.*?)\nDATA_END"
        match = re.search(pattern, full_report, re.DOTALL)

        if match:
            data_block = match.group(1)
            lines = data_block.strip().split("\n")
            for line in lines:
                if ':' in line:
                    ticker, move = line.split(':')
                    predictions[ticker.strip()] = move.strip()

        logger.info(f"extracted {len(predictions)} predictions from report")
        return predictions
