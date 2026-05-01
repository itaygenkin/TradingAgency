class TradingAgentError(Exception):
    """base exception for trading agent errors."""
    pass

class MarketDataError(TradingAgentError):
    """raised when critical market data is missing."""
    pass


class DatabaseError(TradingAgentError):
    """base exception for database errors."""
    pass

class DatabaseConnectionError(DatabaseError):
    """raised when we cannot connect to the database."""
    pass