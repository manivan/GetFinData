"""
Fetcher for exchange rates from frankfurter.app API.
"""

import logging
import requests
from datetime import date

logger = logging.getLogger(__name__)


def fetch_rate(base: str, quote: str, target: date, verify_ssl: bool = True) -> float | None:
    """
    Fetch exchange rate from frankfurter.app API.
    
    Calls the frankfurter.app API to get the exchange rate for a given currency pair
    on a target date. frankfurter.app automatically returns the most recent business day
    if the requested date is a weekend or ECB holiday.
    
    Args:
        base: Base currency code (e.g., 'EUR')
        quote: Quote currency code (e.g., 'USD')
        target: Target date
        verify_ssl: Whether to verify SSL certificate (default: True; set False for testing environments with SSL issues)
        
    Returns:
        Exchange rate (float) rounded to 2 decimal places, or None if not found or API error
    """
    url = f"https://api.frankfurter.app/{target.isoformat()}"
    params = {
        'from': base,
        'to': quote
    }
    
    try:
        response = requests.get(url, params=params, timeout=10, verify=verify_ssl)
        
        if response.status_code != 200:
            logger.warning(
                f"API error for {base}/{quote} on {target}: "
                f"HTTP {response.status_code}"
            )
            return None
        
        data = response.json()
        
        # Extract rate from response
        if 'rates' not in data or quote not in data['rates']:
            logger.warning(f"Rate not found for {base}/{quote} on {target}")
            return None
        
        rate = float(data['rates'][quote])
        return round(rate, 2)
    
    except requests.RequestException as e:
        logger.warning(f"Network error fetching {base}/{quote} on {target}: {e}")
        return None
    except (KeyError, ValueError, TypeError) as e:
        logger.warning(f"Error parsing response for {base}/{quote} on {target}: {e}")
        return None
