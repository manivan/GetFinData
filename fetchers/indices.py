"""
Fetcher for stock index data from Yahoo Finance.
"""

import logging
import pandas as pd
import yfinance as yf
from datetime import date, timedelta

logger = logging.getLogger(__name__)


def fetch_index(ticker: str, target: date) -> float | None:
    """
    Fetch adjusted closing price for a stock index from Yahoo Finance.
    
    If data is not available for the target date, step back day-by-day (up to 7 days)
    to find the most recent prior trading session. Returns None if no data is found
    within 7 days or if an error occurs.
    
    Args:
        ticker: Yahoo Finance ticker symbol (e.g., '^DJI')
        target: Target date
        
    Returns:
        Adjusted closing price (float) rounded to 2 decimal places, or None if not found
    """
    session = None
    try:
        from curl_cffi import requests as curl_requests
        session = curl_requests.Session(impersonate="chrome", verify=False)
    except ImportError:
        pass

    for offset in range(8):  # Try target date, then up to 7 days back
        d = target - timedelta(days=offset)
        try:
            kwargs = dict(
                start=d,
                end=d + timedelta(days=1),
                auto_adjust=True,
                progress=False,
            )
            if session is not None:
                kwargs['session'] = session
            df = yf.download(ticker, **kwargs)
            if not df.empty:
                close_col = df['Close']
                if isinstance(close_col, pd.DataFrame):
                    close_value = close_col.iloc[-1, -1]
                else:
                    close_value = close_col.iloc[-1]
                close_price = float(close_value)
                return round(close_price, 2)
        except Exception as e:
            logger.warning(f"Error fetching {ticker} for {d}: {e}")
            continue
    
    logger.warning(f"No data found for ticker {ticker} within 7 days of {target}")
    return None
