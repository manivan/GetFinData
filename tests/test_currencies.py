"""
Tests for currency rate fetching from frankfurter.app.
"""

import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from fetchers.currencies import fetch_rate


class TestFetchRate:
    """Tests for fetch_rate function."""
    
    @patch('fetchers.currencies.requests.get')
    def test_fetch_rate_success(self, mock_get):
        """Successfully fetch exchange rate."""
        target = date(2026, 7, 31)
        
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'amount': 1.0,
            'base': 'EUR',
            'date': '2026-07-31',
            'rates': {'USD': 1.0823}
        }
        mock_get.return_value = mock_response
        
        result = fetch_rate('EUR', 'USD', target)
        
        assert result == 1.08
        mock_get.assert_called_once()
    
    @patch('fetchers.currencies.requests.get')
    def test_fetch_rate_rounded_to_2_decimals(self, mock_get):
        """Result is rounded to 2 decimal places."""
        target = date(2026, 7, 31)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'rates': {'GBP': 1.29456}
        }
        mock_get.return_value = mock_response
        
        result = fetch_rate('EUR', 'GBP', target)
        
        assert result == 1.29
    
    @patch('fetchers.currencies.requests.get')
    def test_fetch_rate_handles_non_200_response(self, mock_get):
        """Returns None on non-200 HTTP response."""
        target = date(2026, 7, 31)
        
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = fetch_rate('EUR', 'XXX', target)
        
        assert result is None
    
    @patch('fetchers.currencies.requests.get')
    def test_fetch_rate_handles_500_error(self, mock_get):
        """Returns None on 500 server error."""
        target = date(2026, 7, 31)
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = fetch_rate('EUR', 'USD', target)
        
        assert result is None
    
    @patch('fetchers.currencies.requests.get')
    def test_fetch_rate_handles_missing_rate_in_response(self, mock_get):
        """Returns None if rate not found in response."""
        target = date(2026, 7, 31)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'rates': {'EUR': 1.0}  # Missing USD
        }
        mock_get.return_value = mock_response
        
        result = fetch_rate('EUR', 'USD', target)
        
        assert result is None
    
    @patch('fetchers.currencies.requests.get')
    def test_fetch_rate_handles_missing_rates_key(self, mock_get):
        """Returns None if 'rates' key missing from response."""
        target = date(2026, 7, 31)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'base': 'EUR',
            'date': '2026-07-31'
            # No 'rates' key
        }
        mock_get.return_value = mock_response
        
        result = fetch_rate('EUR', 'USD', target)
        
        assert result is None
    
    @patch('fetchers.currencies.requests.get')
    def test_fetch_rate_handles_network_error(self, mock_get):
        """Returns None on network error."""
        import requests
        target = date(2026, 7, 31)
        
        mock_get.side_effect = requests.RequestException("Connection refused")
        
        result = fetch_rate('EUR', 'USD', target)
        
        assert result is None
    
    @patch('fetchers.currencies.requests.get')
    def test_fetch_rate_handles_malformed_json(self, mock_get):
        """Returns None when response JSON cannot be parsed."""
        target = date(2026, 7, 31)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        result = fetch_rate('EUR', 'USD', target)
        
        assert result is None
    
    @patch('fetchers.currencies.requests.get')
    def test_fetch_rate_handles_invalid_rate_value(self, mock_get):
        """Returns None if rate value cannot be converted to float."""
        target = date(2026, 7, 31)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'rates': {'USD': 'invalid'}
        }
        mock_get.return_value = mock_response
        
        result = fetch_rate('EUR', 'USD', target)
        
        assert result is None
    
    @patch('fetchers.currencies.requests.get')
    def test_fetch_rate_calls_correct_url_and_params(self, mock_get):
        """API is called with correct URL and parameters."""
        target = date(2026, 7, 31)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'rates': {'USD': 1.08}}
        mock_get.return_value = mock_response
        
        fetch_rate('EUR', 'USD', target)
        
        # Verify the call was made with correct URL and params
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert args[0] == 'https://api.frankfurter.app/2026-07-31'
        assert kwargs['params'] == {'from': 'EUR', 'to': 'USD'}
        assert kwargs['timeout'] == 10
    
    @patch('fetchers.currencies.requests.get')
    def test_fetch_rate_handles_same_base_and_quote(self, mock_get):
        """Handles same currency pair (e.g., USD/USD returns 1.0)."""
        target = date(2026, 7, 31)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'rates': {'USD': 1.0}
        }
        mock_get.return_value = mock_response
        
        result = fetch_rate('USD', 'USD', target)
        
        assert result == 1.0
