# AI Trading Agent
An automated end-to-end pipeline that performs pre-market stock analysis using LLMs (Gemini) and audits performance after market close. The system tracks predictions in a PostgreSQL database to measure AI accuracy over time.

---

## Project Structure
```text
├── data/                   # Local storage for Markdown reports
├── src/
│   ├── audit_service.py    # LLM logic for performance validation
│   ├── config.py   
│   ├── data_access.py      # PostgreSQL Repository
│   ├── exceptions.py
│   ├── llm_engine.py       # Main AI Analysis & Parser logic
│   └── market_provider.py  # Data fetching from yfinance/web
├── day_analysis.py     # Morning Pipeline (Pre-market)
├── night_audit.py      # Evening Pipeline (Post-market)
└── .env                # API keys and DB credentials (ignored by git)
```
---

## Tech Stack
*   **Language:** Python 3.13+
*   **AI Engine:** Google Gemini (via LangChain)
*   **Database:** PostgreSQL (with `psycopg2` for bulk operations)
*   **Data Sources:** `yfinance` for stock data, `DuckDuckGo` (News catalysts)

---

## Setup Instructions
1. Clone the repository:
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows).
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file from `.env.example` and fill the required API keys and database credentials.
6. Run the agent: `python .\day_analysis.py`
7. Run the audit: `python .\night_audit.py`