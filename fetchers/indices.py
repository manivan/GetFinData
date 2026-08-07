"""
Fetcher for stock index data from Yahoo Finance.
"""

import logging
import yfinance as yf
from datetime import date, timedelta

logger = logging.getLogger(__name__)


def fetch_index(ticker: str, target: date, verify_ssl: bool = True) -> float | None:
    """
    Fetch adjusted closing price for a stock index from Yahoo Finance.
    
    If data is not available for the target date, step back day-by-day (up to 7 days)
    to find the most recent prior trading session. Returns None if no data is found
    within 7 days or if an error occurs.
    
    Args:
        ticker: Yahoo Finance ticker symbol (e.g., '^DJI')
        target: Target date
        verify_ssl: Whether to verify SSL certificate (default: True; set False for testing environments with SSL issues)
        
    Returns:
        Adjusted closing price (float) rounded to 2 decimal places, or None if not found
    """
    for offset in range(8):  # Try target date, then up to 7 days back
        d = target - timedelta(days=offset)
        try:
            df = yf.download(
                ticker,
                start=d,
                end=d + timedelta(days=1),
                auto_adjust=True,
                progress=False
            )
            if not df.empty:
                close_price = float(df['Close'].iloc[-1])
                return round(close_price, 2)
        except Exception as e:
            logger.warning(f"Error fetching {ticker} for {d}: {e}")
            continue
    
    logger.warning(f"No data found for ticker {ticker} within 7 days of {target}")
    return None
