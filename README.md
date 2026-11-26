# AI Trading Agent
An automated end-to-end pipeline that performs pre-market stock analysis using LLMs (Gemini) and audits performance after market close. The system tracks predictions in a PostgreSQL database to measure AI accuracy over time.

---

## Project Structure
```text
├── src/
│   └── trading_agency/
│       ├── application/       # Pipelines, audit services, and Celery tasks
│       ├── domain/            # Models and result types
│       ├── infrastructure/   # Market, LLM, and database integrations
│       ├── utils/
│       ├── celery_app.py
│       └── config.py
├── tests/
│   ├── integration/
│   └── unit/
├── data/                     # Generated reports and runtime data
├── logs/                     # Runtime logs
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
└── .env.example
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

### Running the Pipelines
1. Ensure the system is running: `docker-compose up -d` (or `docker-compose start`).
2. Run the morning pipeline from the repository root: `python -m src.trading_agency.application.day_analysis`.
3. Run the evening audit manually if needed: `python -m src.trading_agency.application.night_audit`.
4. To stop the pipelines: `docker-compose down`.

### Database migrations
After deploying a schema change to an existing database, run its versioned migration from the repository root while the Compose services are running. To remove the obsolete `ai_report_path` column, run it in the worker container so the `DB_HOST=db` setting resolves on the Compose network:

```powershell
docker compose exec worker python -m scripts.migrate_drop_ai_report_path
```

The command uses the database settings from `.env` and is safe to rerun. Back up the database first if the stored report paths may still be needed; dropping the column permanently removes those values.
