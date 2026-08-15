from dataclasses import asdict

import pytest

from src.adapters.llm_factory import get_analysis_model
from src.adapters.repository import MarketRepository
from src.core_logic.audit_service import PerformanceValidator
from src.core_logic.llm_engine import MarketAnalystAgent
from src.models.models import MarketPerformance, Prediction
from src.adapters.celery_app import validate_single_prediction_task


@pytest.fixture(scope="module")
def db():
    """Fixture providing repository instance"""
    return MarketRepository()

@pytest.fixture(scope="function")
def sample_prediction(db):
    """Fixture providing a mock Prediction instance and automatically cleaning it up after the test"""
    pred = Prediction(
        ticker="TEST_AAPL",
        prev_close_price=180.5, # Changed from yesterday_close_price
        pre_market_price=182.3,
        predicted_move="Bullish",
        ai_report_path="test_report_path", # Changed from report_path
        llm_model="gemini"
    )

    db.delete_prediction_by_ticker(pred.ticker)  # Ensure clean state before test

    yield pred

    db.delete_prediction_by_ticker(pred.ticker)  # Cleanup after test

class TestTradingPipelineIntegration:

    def test_llm_factory_fallback_integration(self):
        """verify that the LLM Fallback pipeline initializes correctly and returns a valid response metadata object"""
        llm = get_analysis_model()
        agent = MarketAnalystAgent(llm=llm)

        prompt = "Provide a short 1-line market outlook for Apple (AAPL)"
        response = agent.llm.invoke(prompt)

        assert response is not None
        assert len(response.content) > 0
        assert "model_name" in response.response_metadata and response.content != ""

    def test_morning_to_celery_task_dispatch(self, db, sample_prediction: Prediction):
        """verify DB insertion of PENDING prediction and Celery task dispatch"""
        db.bulk_insert_morning_predictions([sample_prediction])

        # retrieve pending prediction to verify insertion
        pending_records = db.get_pending_predictions()

        # Assert that a record with the correct ticker exists
        assert sample_prediction.ticker in pending_records

        retrieved_prediction = pending_records[sample_prediction.ticker]

        # Compare relevant fields
        assert retrieved_prediction.ticker == sample_prediction.ticker
        assert retrieved_prediction.prev_close_price == sample_prediction.prev_close_price
        assert float(retrieved_prediction.pre_market_price) == float(sample_prediction.pre_market_price)
        assert retrieved_prediction.predicted_move == sample_prediction.predicted_move
        assert retrieved_prediction.status == sample_prediction.status

        # trigger Celery task asynchronously (Testing Broker connection)
        task = validate_single_prediction_task.apply_async(
            args=[asdict(sample_prediction)],
            countdown=2
        )

        assert task.id is not None

    def test_eod_validation_and_db_update(self, db, sample_prediction):
        """tests full integration of PerformanceValidator with DB state update"""
        validator = PerformanceValidator()

        # simulated eod actual market performance
        mock_actual_performance = MarketPerformance(
            ticker=sample_prediction.ticker,
            open=150.0,
            close=155.0,
            actual_change_pct=3.33
        )

        # run validator logic
        eval_result = validator.evaluate(sample_prediction, mock_actual_performance)

        assert eval_result.is_success()
        assert isinstance(eval_result.value.is_correct, bool)
        assert 0 <= eval_result.value.confidence_score <= 100

        # perform evening db update
        update_data = [(
            mock_actual_performance.open,
            mock_actual_performance.actual_change_pct,
            eval_result.value.is_correct,
            eval_result.value.confidence_score,
            sample_prediction.ticker
        )]
        db.bulk_update_evening_validation(update_data)

        # cleanup test record from database
        # optional: add a db.delete_test_ticker("TEST_AAPLE") helper if exists
