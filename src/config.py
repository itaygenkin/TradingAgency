# --- Market Settings ---
import os

WATCHLIST: list[str] = ["AAPL", "TSLA", "NVDA", "AMD", "MSFT", "GOOGL"]

# --- AI Model Settings ---
MODEL_NAME: str = "gemini-3-flash-preview"
TEMPERATURE: float = 0.2

# --- File System Settings ---
REPORTS_DIR: str = "data/reports"
REPORT_FILE_PREFIX: str = "market_report"

# --- Analysis Preferences ---
# This helps guide the Agent's persona without hardcoding it in the class
AGENT_ROLE: str = "Expert Day-Trading Analyst"

# --- Logging Settings ---
LOGS_DIR: str = "data/logs"
LOG_FILE: str = os.path.join(LOGS_DIR, "trading_agent.log")

# ensure logs directory exists
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
