import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Any

load_dotenv()

class MarketAnalysisAgent:
    def __init__(self, model_name: str = "gemini-3-flash-preview"):
        """
        initializes the AI Analyst with the Gemini model
        :param model_name:
        """
        api_key = os.getenv("GOOGLE_API_KEY", None)
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")

        self.llm: ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.2  # low temperature for more factual financial analysis
        )

    def analyze_market_data(self, market_data: dict[str, Any]) -> str:
        """
        Sends raw data to Gemini and receives a structured trading insights.
        :param market_data: the dictionary returned by get_premarket_data.
        :return: a string containing the AI's analysis and recommendation.
        """
        prompt: str = (
            f"You are an expert day-trading analyst. Analyze the following pre-market data: {market_data}. "
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

