from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from src.config import DB_CONFIG
from src.logger import get_logger
logger = get_logger(__name__)


class MarketRepository:
    def __init__(self):
        self._table_name: str = "market"
        self._create_table()

    def _get_connection(self):
        return psycopg2.connect(**DB_CONFIG)

    def _create_table(self):
        query = f"""
        CREATE TABLE IF NOT EXISTS {self._table_name} (
            id                  SERIAL      PRIMARY KEY,
            ticker              VARCHAR(10) NOT NULL,
            trade_date          DATE    DEFAULT CURRENT_DATE,
            prev_close_price    DECIMAL(10, 2),
            pre_market_price    DECIMAL(10, 2),
            predicted_move      VARCHAR(20), -- Bullish/Bearish/Neutral
            actual_open_price   DECIMAL(10, 2),
            actual_move_pct     DECIMAL(10, 2),
            is_correct          BOOLEAN,
            confidence_score    INTEGER,
            ai_report_path      TEXT,
            created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            status              VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        );
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    conn.commit()
            logger.info(f"database table '{self._table_name}' created")
        except psycopg2.Error as e:
            logger.error("failed to create table", e)

    def insert_morning_prediction(self, ticker: str, data: dict[str, Any], report_path: str) -> None:
        query = f"""
            INSERT INTO {self._table_name} (
                ticker, trade_date, prev_close_price, pre_market_price, predicted_move, ai_report_path, created_at, status) 
            VALUES (%s, CURRENT_DATE, %s, %s, %s, %s, CURRENT_TIMESTAMP, 'PENDING');
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (
                        ticker,
                        data.get("prev_close_price"),
                        data.get("pre_market_price"),
                        data.get("predicted_move", "Neutral"),
                        report_path
                    ))
                    conn.commit()
            logger.info(f"morning data for ticker: '{ticker}' saved to DB")
        except psycopg2.Error as e:
            logger.error(f"failed to insert morning data for ticker: '{ticker}'. {e}")

    def update_evening_validation(self, ticker: str, actual_data: dict[str, Any], is_correct: bool, score: int) -> None:
        query = f"""
            UPDATE {self._table_name}
            SET actual_open_price = %s,
                actual_move_pct = %s,
                is_correct = %s,
                confidence_score = %s,
                status = 'COMPLETED'
            WHERE ticker = %s AND trade_date = CURRENT_DATE;
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (
                        actual_data.get("open_price"),
                        actual_data.get("actual_move_pct"),
                        is_correct,
                        score,
                        ticker
                    ))
                    conn.commit()
            logger.info(f"evening validation for ticker: '{ticker}' updated in DB")
        except psycopg2.Error as e:
            logger.error(f"failed to update evening validation for ticker: '{ticker}'. {e}")

    def get_pending_predictions(self) -> list[dict[str, Any]]:
        query = f"""
        SELECT ticker, pre_market_price, prev_close_price, predicted_move
        FROM {self._table_name}
        WHERE trade_date = CURRENT_DATE AND status = 'PENDING';
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as rd_cur:
                    rd_cur.execute(query)
                    results = rd_cur.fetchall()

                    # convert RealDictRow objects to standard dictionaries for cleaner precessing
                    predictions = [dict(row) for row in results]

                    logger.info(f"retrieved {len(predictions)} pending predictions for audit")
                    return predictions
        except psycopg2.Error as e:
            logger.error(f"failed to get pending predictions. {e}")
            return []
