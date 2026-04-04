import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Any

from src.config import MODEL_NAME, AGENT_ROLE, TEMPERATURE

load_dotenv()

class MarketAnalysisAgent:
    def __init__(self):
        """
        initializes the AI Analyst with the Gemini model
        """
        api_key = os.getenv("GOOGLE_API_KEY", None)
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")

        self.llm: ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            google_api_key=api_key,
            temperature=TEMPERATURE
        )

    def analyze_market_data(self, market_data: dict[str, Any]) -> str:
        """
        Sends raw data to Gemini and receives a structured trading insights.
        :param market_data: the dictionary returned by get_premarket_data.
        :return: a string containing the AI's analysis and recommendation.
        """
        prompt: str = (
            f"You are an {AGENT_ROLE}. Analyze the following pre-market data: {market_data}. "
            "For each stock, provide: \n"
            "1. Current trend (Bullshit/Bearish/Neutral).\n"
            "2. Potential price action for the market open.\n"
            "3. A risk assessment for an active day trader.\n"
            "Keep the report concise and professional."
        )

        response = self.llm.invoke(prompt)
        return str(response.content)

# Test block for the agent
if __name__ == "__main__":
    # Mock data for testing
    sample_data: dict[str, Any] = {
        "AAPL": {"price": 185.2, "change_pct": 1.5, "volume": 500000}
    }
    analyst = MarketAnalysisAgent()
    print(analyst.analyze_market_data(sample_data))

