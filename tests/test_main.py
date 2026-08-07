"""
Unit tests for core functionality: date parsing, config loading.
"""

import pytest
from datetime import date
from pathlib import Path
import tempfile
from main import parse_date, load_config


class TestParseDate:
    """Tests for date parsing."""
    
    def test_parse_valid_date(self):
        """Valid M/D/YYYY date is parsed correctly."""
        result = parse_date('7/31/2026')
        assert result == date(2026, 7, 31)
    
    def test_parse_single_digit_month_day(self):
        """Single digit month/day are handled."""
        result = parse_date('1/5/2026')
        assert result == date(2026, 1, 5)
    
    def test_parse_invalid_format_raises_error(self):
        """Invalid date format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid date format"):
            parse_date('07-31-2026')
    
    def test_parse_invalid_month_raises_error(self):
        """Invalid month raises ValueError."""
        with pytest.raises(ValueError, match="Invalid date format"):
            parse_date('13/1/2026')
    
    def test_parse_invalid_day_raises_error(self):
        """Invalid day raises ValueError."""
        with pytest.raises(ValueError, match="Invalid date format"):
            parse_date('2/30/2026')
    
    def test_parse_non_existent_date_raises_error(self):
        """Non-existent date (e.g., Feb 30) raises ValueError."""
        with pytest.raises(ValueError, match="Invalid date format"):
            parse_date('2/30/2026')


class TestLoadConfig:
    """Tests for config loading."""
    
    def test_load_valid_config(self):
        """Valid config.ini is loaded correctly."""
        result = load_config('config.ini')
        assert isinstance(result, dict)
        assert 'indices' in result
        assert 'currencies' in result
        assert isinstance(result['indices'], list)
        assert isinstance(result['currencies'], list)
    
    def test_load_config_indices_parsed(self):
        """Indices are correctly parsed from config."""
        result = load_config('config.ini')
        # The sample config has ^DJI, ^GSPC, ^IXIC
        assert '^DJI' in result['indices']
        assert '^GSPC' in result['indices']
        assert '^IXIC' in result['indices']
    
    def test_load_config_currencies_parsed(self):
        """Currencies are correctly parsed from config."""
        result = load_config('config.ini')
        # The sample config has EUR/USD, GBP/USD
        assert 'EUR/USD' in result['currencies']
        assert 'GBP/USD' in result['currencies']
    
    def test_load_missing_config_raises_error(self):
        """Missing config file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Config file"):
            load_config('nonexistent.ini')
    
    def test_load_empty_config_sections(self):
        """Empty config sections return empty lists."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write('[indices]\nsymbols = \n\n[currencies]\npairs = \n')
            temp_path = f.name
        
        try:
            result = load_config(temp_path)
            assert result['indices'] == []
            assert result['currencies'] == []
        finally:
            Path(temp_path).unlink()
    
    def test_load_config_with_whitespace(self):
        """Whitespace in config values is stripped."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write('[indices]\nsymbols =  ^DJI ,  ^GSPC  \n\n[currencies]\npairs =  EUR/USD , GBP/USD  \n')
            temp_path = f.name
        
        try:
            result = load_config(temp_path)
            assert result['indices'] == ['^DJI', '^GSPC']
            assert result['currencies'] == ['EUR/USD', 'GBP/USD']
        finally:
            Path(temp_path).unlink()
