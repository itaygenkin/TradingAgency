import os
from datetime import datetime
from typing import Any

from src.agent import MarketAnalysisAgent
from src.config import REPORTS_DIR, WATCHLIST, REPORT_FILE_PREFIX
from src.tools import get_premarket_data

def ensure_directories() -> None:
    """
    Creates necessary directories if they don't already exist.
    """
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

def save_report_to_file(report_content: str) -> str:
    timestamp: str = datetime.now().strftime("%d-%m-%Y_%H-%M")
    filename: str = f"{REPORT_FILE_PREFIX}_{timestamp}.txt"
    file_path: str = os.path.join(REPORTS_DIR, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return file_path

def run_agent_pipeline() -> None:
    """
    Executes the full agent workflow: Fetch -> Analyze -> Save.
    :return:
    """
    print("--- Starting AI Trading Agent Pipeline ---")

    ensure_directories()

    # Step 1: Fetching data using our tool
    print(f"Step 1: Fetching pre-market data for {len(WATCHLIST)} stocks...")
    raw_market_data: dict[str, Any] = get_premarket_data(WATCHLIST)

    # Step 2: Passing data to the Gemini Agent
    print(f"Step 2: Sending data to Gemini for analysis...")
    analyst = MarketAnalysisAgent()
    analyzed_report = analyst.analyze_market_data(raw_market_data)

    # Step 3: Saving the output to a file
    print(f"Step 3: Saving report to disk...")
    path: str = save_report_to_file(analyzed_report)

    print(f"\n--- Pipeline Completed Successfully ---")
    print(f"Report saved to: {path}")

if __name__ == "__main__":
    try:
        run_agent_pipeline()
    except Exception as e:
        print(f"An error occurred during the pipeline execution: {e}")


