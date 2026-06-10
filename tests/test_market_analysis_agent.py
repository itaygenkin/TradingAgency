import unittest
from src.core_logic.llm_engine import MarketAnalysisAgent


class TestExtractPredictions(unittest.TestCase):

    def test_extract_single_prediction(self):
        """Test extracting a single prediction from a report"""
        report = """# Daily Pre-Market Analysis
Some analysis here...
DATA_START
AAPL:Bullish
DATA_END"""
        result = MarketAnalysisAgent.extract_predictions(report)
        self.assertEqual(result, {"AAPL": "Bullish"})

    def test_extract_multiple_predictions(self):
        """Test extracting multiple predictions from a report"""
        report = """# Daily Pre-Market Analysis
Some analysis here...
DATA_START
AAPL:Bullish
TSLA:Bearish
NVDA:Neutral
DATA_END"""
        result = MarketAnalysisAgent.extract_predictions(report)
        expected = {"AAPL": "Bullish", "TSLA": "Bearish", "NVDA": "Neutral"}
        self.assertEqual(result, expected)

    def test_extract_predictions_with_whitespace(self):
        report = """DATA_START
AAPL : Bullish
TSLA:  Bearish  
NVDA  :Neutral
DATA_END"""
        result = MarketAnalysisAgent.extract_predictions(report)
        expected = {"AAPL": "Bullish", "TSLA": "Bearish", "NVDA": "Neutral"}
        self.assertEqual(result, expected)

    def test_extract_predictions_empty_data_block(self):
        """Test handling of empty data block"""
        report = """Some analysis...
DATA_START
DATA_END"""
        result = MarketAnalysisAgent.extract_predictions(report)
        self.assertEqual(result, {})

    def test_extract_predictions_no_data_block(self):
        """Test handling when no data block is present"""
        report = "Just a regular report without any data block."
        result = MarketAnalysisAgent.extract_predictions(report)
        self.assertEqual(result, {})

    def test_extract_predictions_malformed_lines(self):
        report = """DATA_START
AAPL:Bullish
INVALID_LINE
TSLA:Bearish
DATA_END"""
        result = MarketAnalysisAgent.extract_predictions(report)
        expected = {"AAPL": "Bullish", "TSLA": "Bearish"}
        self.assertEqual(result, expected)

    def test_extract_predictions_with_multiline_content(self):
        report = """# Daily Pre-Market Analysis

## Executive Summary
Market sentiment is mixed today.

## Stock Watchlist
| Ticker | Price Change% | Sentiment |
|--------|----------------|-----------|
| AAPL   | +2.5%         | Bullish   |
| TSLA   | -1.8%         | Bearish   |

DATA_START
AAPL:Bullish
TSLA:Bearish
GOOGL:Neutral
DATA_END"""
        result = MarketAnalysisAgent.extract_predictions(report)
        expected = {"AAPL": "Bullish", "TSLA": "Bearish", "GOOGL": "Neutral"}
        self.assertEqual(result, expected)

    def test_extract_predictions_case_preservation(self):
        """Test that ticker and move case is preserved"""
        report = """DATA_START
aapl:bullish
TSLA:BEARISH
NvDa:NeUtRaL
DATA_END"""
        result = MarketAnalysisAgent.extract_predictions(report)
        expected = {"aapl": "bullish", "TSLA": "BEARISH", "NvDa": "NeUtRaL"}
        self.assertEqual(result, expected)

    def test_extract_predictions_multiple_colons_in_line(self):
        """Test handling of lines with multiple colons (split on first colon)"""
        report = """DATA_START
AAPL:Bullish:Extra
TSLA:Bearish
DATA_END"""
        expected_result = {"AAPL": "Bullish", "TSLA": "Bearish"}
        result = MarketAnalysisAgent.extract_predictions(report)
        self.assertEqual(result, expected_result)

    def test_extract_predictions_empty_string(self):
        result = MarketAnalysisAgent.extract_predictions("")
        self.assertEqual(result, {})

    def test_extract_predictions_only_data_markers(self):
        report = "DATA_START\nDATA_END"
        result = MarketAnalysisAgent.extract_predictions(report)
        self.assertEqual(result, {})

    def test_extract_predictions_annoying_data(self):
        report = """some data analysis\n\t\nmore non relevant data
DATA_START
AAPL:Neutral::some annoying data
TSLA:BEARISH\n\n
NVDA::Bearish
DATA_END"""
        expected_result = {"AAPL": "Neutral", "TSLA": "BEARISH", "NVDA": "Bearish"}
        result = MarketAnalysisAgent.extract_predictions(report)
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
