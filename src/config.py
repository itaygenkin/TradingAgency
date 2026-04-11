import os

from dotenv import load_dotenv

load_dotenv()

WATCHLIST: list[str] = ["AAPL", "AKAM", "NVDA", "GOOGL"]

# --- AI Model Settings ---
MODEL_NAME: str = "gemini-3-flash-preview"
TEMPERATURE: float = 0.2

# --- File System Settings ---
REPORTS_DIR: str = "./data/reports"
REPORT_FILE_PREFIX: str = "prediction_market_report"
REPORT_FILE_EXTENSION: str = "md"

# --- Analysis Preferences ---
# This helps guide the Agent's persona without hardcoding it in the class
AGENT_ROLE: str = "Expert Day-Trading Analyst"

# --- Validation Settings ---
VALIDATION_REPORT_PREFIX: str = "performance_validation"
VALIDATION_LOG_FILE: str = "validation.log"

# --- Logging Settings ---
LOGS_DIR: str = "./logs"

# ensure logs directory exists
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# --- Database Settings ---
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "trading_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "port": os.getenv("DB_PORT", "5432"),
}
