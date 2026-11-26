"""Apply the migration that removes the obsolete report path column."""

from pathlib import Path

import psycopg2

from src.trading_agency.config import DB_CONFIG


MIGRATION_FILE = (
    Path(__file__).resolve().parents[1]
    / "migrations"
    / "001_drop_ai_report_path.sql"
)


def main() -> None:
    migration_sql = MIGRATION_FILE.read_text(encoding="utf-8")
    with psycopg2.connect(**DB_CONFIG) as connection:
        with connection.cursor() as cursor:
            cursor.execute(migration_sql)
    print("Migration 001 applied: ai_report_path removed if present.")


if __name__ == "__main__":
    main()
