#!/usr/bin/env python3
"""
GetFinData: Fetch financial data (stock indices and FX rates) for a given date.
"""

import sys
import argparse
import logging
import os
from datetime import datetime, date
from pathlib import Path
import configparser

from fetchers.indices import fetch_index
from fetchers.currencies import fetch_rate

# Suppress yfinance verbose output
import warnings
warnings.filterwarnings('ignore')
os.environ['YFINANCE_PROGRESS_BAR'] = 'false'

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def parse_date(date_str: str) -> date:
    """
    Parse a date string in M/D/YYYY format (e.g., '7/31/2026').
    
    Args:
        date_str: Date string in M/D/YYYY format
        
    Returns:
        datetime.date object
        
    Raises:
        ValueError: If date format is invalid or date is invalid
    """
    try:
        parsed = datetime.strptime(date_str, '%m/%d/%Y')
        return parsed.date()
    except ValueError as e:
        raise ValueError(f"Invalid date format '{date_str}'. Expected M/D/YYYY (e.g., 7/31/2026).") from e


def load_config(config_path: str = 'config.ini') -> dict:
    """
    Load configuration from INI file.
    
    Args:
        config_path: Path to config.ini file
        
    Returns:
        Dictionary with 'indices' (list of symbols) and 'currencies' (list of pairs)
        
    Raises:
        FileNotFoundError: If config file does not exist
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file '{config_path}' not found.")
    
    config = configparser.ConfigParser()
    config.read(config_file)
    
    result = {
        'indices': [],
        'currencies': []
    }
    
    # Parse indices section
    if config.has_section('indices') and config.has_option('indices', 'symbols'):
        symbols_str = config.get('indices', 'symbols').strip()
        if symbols_str:
            result['indices'] = [s.strip() for s in symbols_str.split(',')]
    
    # Parse currencies section
    if config.has_section('currencies') and config.has_option('currencies', 'pairs'):
        pairs_str = config.get('currencies', 'pairs').strip()
        if pairs_str:
            result['currencies'] = [p.strip() for p in pairs_str.split(',')]
    
    return result


def write_output(indices_dict: dict, currencies_dict: dict) -> None:
    """
    Write results to output/output.txt in tab-separated format.
    
    Args:
        indices_dict: Dictionary of {label: value} for indices
        currencies_dict: Dictionary of {pair: value} for currencies
    """
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / 'output.txt'
    
    with open(output_file, 'w') as f:
        # Write indices first
        for label, value in indices_dict.items():
            f.write(f"{label}\t{value:.2f}\n")
        
        # Write currencies
        for pair, value in currencies_dict.items():
            f.write(f"{pair}\t{value:.2f}\n")
    
    return output_file


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Fetch stock index and FX rate data for a given date.'
    )
    parser.add_argument(
        'date',
        help='Target date in M/D/YYYY format (e.g., 7/31/2026)'
    )
    parser.add_argument(
        '--no-verify-ssl',
        action='store_true',
        help='Disable SSL certificate verification (for testing environments with SSL issues)'
    )
    
    args = parser.parse_args()
    
    # Parse and validate date
    try:
        target_date = parse_date(args.date)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Load configuration
    try:
        config = load_config()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Determine SSL verification setting
    verify_ssl = not args.no_verify_ssl
    
    # Fetch indices
    indices_data = {}
    for ticker in config['indices']:
        value = fetch_index(ticker, target_date, verify_ssl=verify_ssl)
        if value is not None:
            # Strip leading '^' from ticker for label
            label = ticker.lstrip('^')
            indices_data[label] = value
    
    # Fetch currencies
    currencies_data = {}
    for pair in config['currencies']:
        parts = pair.split('/')
        if len(parts) != 2:
            logger.warning(f"Invalid currency pair format: {pair}")
            continue
        base, quote = parts
        value = fetch_rate(base.strip(), quote.strip(), target_date, verify_ssl=verify_ssl)
        if value is not None:
            currencies_data[pair] = value
    
    # Write output
    output_file = write_output(indices_data, currencies_data)
    
    # Print summary to stdout
    print(f"Fetched data for {target_date.strftime('%B %d, %Y')}")
    print(f"Indices: {len(indices_data)} of {len(config['indices'])}")
    print(f"Currencies: {len(currencies_data)} of {len(config['currencies'])}")
    print(f"Output written to {output_file}")


if __name__ == '__main__':
    main()
