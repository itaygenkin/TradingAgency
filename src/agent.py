import os
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
        :return: a string containing the AI's analysis and recommendation.
        """
        logger.info("Starting AI synthesis of market data and news.")
        prompt: str = (
            f"You are an {AGENT_ROLE}. Analyze the following pre-market data and news:\n"
            f"Prices: {market_data}\n"
            f"News: {news_data}\n\n"
            f"Instructions:\n"
            f"Generate a professional daily trading report in Markdown format. Use the following structure:\n"
            f"1. # Daily Pre-Market Analysis (Header 1)\n"
            f"2. ## Executive Summary (A brief paragraph about the overall market sentiment)\n"
            f"3. ## Stock Watchlist (A Markdown Table with columns: Ticker, Price Change%, Sentiment)\n"
            f"4. ## Deep Dive per Ticker (Header 3 for each stock, explaining the 'Why' behind the move based on news)\n"
            f"5. ## Trading Strategy (Key levels or warnings for the open)\n\n"
            f"Be specific, professional, and concise. Avoid generic statements."
        )

        response = self.llm.invoke(prompt)
        if response and "text" in response.content[0]:
            return response.content[0]["text"]

        return "Error while analyzing market data."

# Test block for the agent
if __name__ == "__main__":
    # Mock data for testing
    sample_data: dict[str, Any] = {
        "AAPL": {"price": 185.2, "change_pct": 1.5, "volume": 500000}
    }
    analyst = MarketAnalysisAgent()
    print(analyst.analyze_market_data(sample_data))

