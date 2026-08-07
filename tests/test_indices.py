"""
Tests for index fetching with fallback logic.
"""

import pytest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock
import pandas as pd
from fetchers.indices import fetch_index


class TestFetchIndex:
    """Tests for fetch_index function."""
    
    @patch('fetchers.indices.yf.download')
    def test_fetch_index_success_on_target_date(self, mock_download):
        """Successfully fetch index on target date."""
        target = date(2026, 7, 31)
        
        # Mock yfinance to return a DataFrame with Close price
        mock_df = pd.DataFrame({
            'Close': [53885.11]
        })
        mock_download.return_value = mock_df
        
        result = fetch_index('^DJI', target)
        
        assert result == 53885.11
        mock_download.assert_called_once()
    
    @patch('fetchers.indices.yf.download')
    def test_fetch_index_rounded_to_2_decimals(self, mock_download):
        """Result is rounded to 2 decimal places."""
        target = date(2026, 7, 31)
        
        # Return a price with more than 2 decimals
        mock_df = pd.DataFrame({
            'Close': [53885.1234]
        })
        mock_download.return_value = mock_df
        
        result = fetch_index('^DJI', target)
        
        assert result == 53885.12
    
    @patch('fetchers.indices.yf.download')
    def test_fetch_index_fallback_to_prior_day(self, mock_download):
        """Fallback one day when target date has no data."""
        target = date(2026, 7, 31)
        
        # First call (target date) returns empty, second call (day before) returns data
        empty_df = pd.DataFrame({'Close': []})
        data_df = pd.DataFrame({'Close': [53885.11]})
        mock_download.side_effect = [empty_df, data_df]
        
        result = fetch_index('^DJI', target)
        
        assert result == 53885.11
        assert mock_download.call_count == 2
    
    @patch('fetchers.indices.yf.download')
    def test_fetch_index_fallback_multiple_days(self, mock_download):
        """Fallback multiple days until data is found."""
        target = date(2026, 7, 31)
        
        # Empty for 2 days, then return data on day 3
        empty_df = pd.DataFrame({'Close': []})
        data_df = pd.DataFrame({'Close': [52000.00]})
        mock_download.side_effect = [empty_df, empty_df, data_df]
        
        result = fetch_index('^GSPC', target)
        
        assert result == 52000.00
        assert mock_download.call_count == 3
    
    @patch('fetchers.indices.yf.download')
    def test_fetch_index_returns_none_after_7_day_fallback(self, mock_download):
        """Returns None if no data found within 7 days."""
        target = date(2026, 7, 31)
        
        # Always return empty
        empty_df = pd.DataFrame({'Close': []})
        mock_download.return_value = empty_df
        
        result = fetch_index('^IXIC', target)
        
        assert result is None
        # Should try 8 times (target + 7 days back)
        assert mock_download.call_count == 8
    
    @patch('fetchers.indices.yf.download')
    def test_fetch_index_handles_exception_and_continues(self, mock_download):
        """Continues fallback if yfinance raises an exception."""
        target = date(2026, 7, 31)
        
        # First call raises exception, second call succeeds
        data_df = pd.DataFrame({'Close': [51234.56]})
        mock_download.side_effect = [Exception("API error"), data_df]
        
        result = fetch_index('^DJI', target)
        
        assert result == 51234.56
        assert mock_download.call_count == 2
    
    @patch('fetchers.indices.yf.download')
    def test_fetch_index_uses_last_row_if_multiple_rows(self, mock_download):
        """Uses the last row (most recent) if DataFrame has multiple rows."""
        target = date(2026, 7, 31)
        
        # Return a DataFrame with multiple rows (shouldn't happen with 1-day range, but test it)
        mock_df = pd.DataFrame({
            'Close': [53000.00, 53500.00, 53885.11]
        })
        mock_download.return_value = mock_df
        
        result = fetch_index('^DJI', target)
        
        # Should use the last row
        assert result == 53885.11
    
    @patch('fetchers.indices.yf.download')
    def test_fetch_index_dates_step_backward_correctly(self, mock_download):
        """Date stepping backward is correct (7 calendar days back)."""
        target = date(2026, 7, 31)
        empty_df = pd.DataFrame({'Close': []})
        mock_download.return_value = empty_df
        
        fetch_index('^DJI', target)
        
        # Check that calls are made for target and 7 days back
        calls = mock_download.call_args_list
        assert len(calls) == 8
        
        # First call should be for target date
        first_call_args = calls[0]
        assert first_call_args[1]['start'] == date(2026, 7, 31)
        
        # Last call should be for 7 days back
        last_call_args = calls[7]
        assert last_call_args[1]['start'] == date(2026, 7, 24)
