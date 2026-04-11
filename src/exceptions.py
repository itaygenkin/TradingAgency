class TradingAgentError(Exception):
    """base exception for trading agent errors."""
    pass


class DatabaseConnectionError(TradingAgentError):
    """raised when we cannot connect to the database."""

    
class MarketDataError(TradingAgentError):
    """raised when critical market data is missing."""
    pass