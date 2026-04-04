# --- Market Settings ---
WATCHLIST: list[str] = ["AAPL", "TSLA", "NVDA", "AMD", "MSFT", "GOOGL"]

# --- AI Model Settings ---
MODEL_NAME: str = "gemini-1.5-flash"
TEMPERATURE: float = 0.2

# --- File System Settings ---
REPORTS_DIR: str = "data/reports"
REPORT_FILE_PREFIX: str = "market_report"

# --- Analysis Preferences ---
# This helps guide the Agent's persona without hardcoding it in the class
AGENT_ROLE: str = "Expert Day-Trading Analyst"