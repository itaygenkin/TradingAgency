# AI Trading Agent
An automated end-to-end pipeline that performs pre-market stock analysis using LLMs (Gemini) and audits performance after market close. The system tracks predictions in a PostgreSQL database to measure AI accuracy over time.

---

## Project Structure
```text
├── data/                   # Generated Markdown reports & logs
├── src/
│   ├── core/               # Business Logic
│   │   ├── llm_engine.py       # LLM report generation & parsing
│   │   └── audit_service.py    # Performance evaluation logic
│   ├── adapters/           # External System Interfaces
│   │   ├── repository.py       # PostgreSQL Repository (Bulk Ops)
│   │   └── market_provider.py  # yfinance & news fetching
│   ├── models/             # Data Blueprints
|   |   |   models.py
│   │   └── result.py           # Result Data Class
│   ├── utils/              # Shared Helpers
│   │   ├── exceptions.py       
│   │   └── logger.py         
│   └── config.py           # Environment & Watchlist settings
├── tests/
├── day_analysis.py         # Entry point: Morning Pipeline
└── night_audit.py          # Entry point: Evening Audit
```
---

## Tech Stack
*   **Language:** Python 3.13+
*   **AI Engine:** Google Gemini (via LangChain)
*   **Database:** PostgreSQL 16 (with `psycopg2` for bulk operations)
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