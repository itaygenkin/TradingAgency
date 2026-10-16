# AI Trading Agent
An automated end-to-end pipeline that performs pre-market stock analysis using LLMs (Gemini) and audits performance after market close. The system tracks predictions in a PostgreSQL database to measure AI accuracy over time.

---

## Project Structure
```text
├── data/                   # Generated Markdown reports & logs
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
├── .env
├── entrypoints/
│   ├── day_analysis.py        # Entry point: Trigger morning_pipeline
│   ├── night_audit.py         # Entry point: Trigger evening_pipeline
│   └── celery_app.py          # Celery worker/beat instantiation
├── src/
│   ├── application/
│   │   ├── morning_pipeline.py     # Day analysis logic (orchestration)
│   │   └── evening_pipeline.py     # Night audit logic (orchestration)
│   ├── domain/             # Data Blueprints
│   │   │   models.py
│   │   └── result.py               # Result Data Class
│   ├── infrastructure/     # Framework & Shared Components
│   │   │   database_adapter.py     # PostgreSQL Adapter
│   │   │   market_provider.py      # yfinance & DuckDuckGo fetching
│   │   └── llm_engine.py           # LLM report generation & parsing
│   ├── utils/              # Shared Helpers
│   │   ├── exceptions.py     
│   │   ├── utils.py 
│   │   └── logger.py         
│   └── config.py           # Environment & Watchlist settings
└── tests/
    ├── integration/
    └── unit/
```
---

## Tech Stack
* **Language:** Python 3.13+
* **Containerization:** Docker & Docker Compose
* **Task Queue & Message Broker:** Celery & Redis
* **AI Engine:** Google Gemini (via LangChain)
* **Database:** PostgreSQL 16
* **Data Sources & Utils:** `yfinance`, DuckDuckGo (News catalysts), `pandas_market_calendars` (Market hours validation)
* **Monitoring:** Flower (Celery Workers Dashboard)

---

## Setup Instructions
1. Clone the repository.
2. Create a `.env` file from `.env.example` and fill the required API keys and database credentials.
3. Install all dependencies: `pip install -r requirements.txt`.
4. Build and start the entire system (Database, Redis, Celery): `docker-compose up -d --build`.
5. Launch the Streamlit dashboard: `streamlit run src/application/dashboard.py`. // not implemented yet

### Running the Pipelines
1. Ensure the system is running: `docker-compose up -d` (or `docker-compose start`).
2. Run the morning pipeline: `python -m entrypoints/day_analysis.py`.
3. To stop the pipelines: `docker-compose down`.