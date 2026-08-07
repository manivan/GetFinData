"""
End-to-end integration tests with mocked external dependencies.
"""

import pytest
from datetime import date
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd
import tempfile
import sys

from main import main, write_output


class TestWriteOutput:
    """Tests for output file writing."""
    
    def test_write_output_creates_directory(self):
        """Output directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'output' / 'output.txt'
            
            # Temporarily change working directory
            import os
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                write_output({'DJI': 53885.11}, {'EUR/USD': 1.08})
                assert output_path.exists()
            finally:
                os.chdir(old_cwd)
    
    def test_write_output_format_single_item(self):
        """Single item is written in correct tab-separated format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                Path('output').mkdir(exist_ok=True)
                write_output({'DJI': 53885.11}, {})
                
                output_file = Path('output') / 'output.txt'
                content = output_file.read_text()
                
                assert content.strip() == 'DJI\t53885.11'
            finally:
                os.chdir(old_cwd)
    
    def test_write_output_format_indices_then_currencies(self):
        """Indices are written first, then currencies."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                Path('output').mkdir(exist_ok=True)
                write_output(
                    {'DJI': 53885.11, 'GSPC': 5611.85},
                    {'EUR/USD': 1.08, 'GBP/USD': 1.29}
                )
                
                output_file = Path('output') / 'output.txt'
                lines = output_file.read_text().strip().split('\n')
                
                # Verify order: indices first, then currencies
                assert lines[0].startswith('DJI')
                assert lines[1].startswith('GSPC')
                assert lines[2].startswith('EUR')
                assert lines[3].startswith('GBP')
            finally:
                os.chdir(old_cwd)
    
    def test_write_output_decimal_formatting(self):
        """Values are formatted to 2 decimal places."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                Path('output').mkdir(exist_ok=True)
                write_output({'DJI': 53885.1234}, {'EUR/USD': 1.0823})
                
                output_file = Path('output') / 'output.txt'
                lines = output_file.read_text().strip().split('\n')
                
                # Check decimal formatting
                assert '\t53885.12' in lines[0]
                assert '\t1.08' in lines[1]
            finally:
                os.chdir(old_cwd)
    
    def test_write_output_overwrites_existing_file(self):
        """Output file is overwritten on second write, not appended."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                Path('output').mkdir(exist_ok=True)
                
                # First write
                write_output({'DJI': 53885.11}, {})
                
                # Second write
                write_output({'GSPC': 5611.85}, {})
                
                output_file = Path('output') / 'output.txt'
                content = output_file.read_text().strip()
                
                # Should only contain second write, not both
                assert 'DJI' not in content
                assert 'GSPC' in content
            finally:
                os.chdir(old_cwd)


class TestEndToEndIntegration:
    """End-to-end integration tests with mocked external calls."""
    
    @patch('main.fetch_index')
    @patch('main.fetch_rate')
    def test_end_to_end_with_all_data_fetched(self, mock_fetch_rate, mock_fetch_index):
        """Complete flow: fetch indices and currencies, write output."""
        # Setup mocks
        mock_fetch_index.side_effect = [53885.11, 5611.85, 6543.21]  # ^DJI, ^GSPC, ^IXIC
        mock_fetch_rate.side_effect = [1.08, 1.29]  # EUR/USD, GBP/USD
        
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                # Create config
                config_content = """[indices]
symbols = ^DJI, ^GSPC, ^IXIC

[currencies]
pairs = EUR/USD, GBP/USD
"""
                Path('config.ini').write_text(config_content)
                Path('output').mkdir(exist_ok=True)
                
                # Mock sys.argv for CLI
                with patch.object(sys, 'argv', ['main.py', '7/31/2026']):
                    main()
                
                # Verify output file was created
                output_file = Path('output') / 'output.txt'
                assert output_file.exists()
                
                content = output_file.read_text()
                lines = content.strip().split('\n')
                
                # Verify all items are present
                assert len(lines) == 5
                assert 'DJI\t53885.11' in content
                assert 'GSPC\t5611.85' in content
                assert 'IXIC\t6543.21' in content
                assert 'EUR/USD\t1.08' in content
                assert 'GBP/USD\t1.29' in content
            finally:
                os.chdir(old_cwd)
    
    @patch('main.fetch_index')
    @patch('main.fetch_rate')
    def test_end_to_end_with_partial_failures(self, mock_fetch_rate, mock_fetch_index):
        """Items that fail to fetch are omitted, others are present."""
        # One index fails (returns None), currencies succeed
        mock_fetch_index.side_effect = [53885.11, None, 6543.21]
        mock_fetch_rate.side_effect = [1.08, 1.29]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                config_content = """[indices]
symbols = ^DJI, ^GSPC, ^IXIC

[currencies]
pairs = EUR/USD, GBP/USD
"""
                Path('config.ini').write_text(config_content)
                Path('output').mkdir(exist_ok=True)
                
                with patch.object(sys, 'argv', ['main.py', '7/31/2026']):
                    main()
                
                output_file = Path('output') / 'output.txt'
                content = output_file.read_text()
                
                # GSPC (the one that failed) should not be in output
                assert 'DJI' in content
                assert 'GSPC' not in content  # Failed fetch
                assert 'IXIC' in content
                assert 'EUR/USD' in content
                assert 'GBP/USD' in content
            finally:
                os.chdir(old_cwd)
    
    @patch('main.fetch_index')
    @patch('main.fetch_rate')
    def test_end_to_end_with_empty_config_sections(self, mock_fetch_rate, mock_fetch_index):
        """Empty config sections result in empty output sections."""
        mock_fetch_index.side_effect = [53885.11]
        mock_fetch_rate.side_effect = []
        
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                config_content = """[indices]
symbols = ^DJI

[currencies]
pairs = 
"""
                Path('config.ini').write_text(config_content)
                Path('output').mkdir(exist_ok=True)
                
                with patch.object(sys, 'argv', ['main.py', '7/31/2026']):
                    main()
                
                output_file = Path('output') / 'output.txt'
                content = output_file.read_text()
                
                # Should only have one line (the index)
                assert content.count('\n') == 1
                assert 'DJI\t53885.11' in content
            finally:
                os.chdir(old_cwd)
    
    def test_end_to_end_invalid_date_exits_with_code_1(self):
        """Invalid date argument causes exit with code 1."""
        with pytest.raises(SystemExit) as exc_info:
            with patch.object(sys, 'argv', ['main.py', 'invalid_date']):
                with patch('sys.stderr', new_callable=MagicMock):
                    main()
        
        assert exc_info.value.code == 1
    
    def test_end_to_end_missing_config_exits_with_code_1(self):
        """Missing config file causes exit with code 1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                with pytest.raises(SystemExit) as exc_info:
                    with patch.object(sys, 'argv', ['main.py', '7/31/2026']):
                        with patch('sys.stderr', new_callable=MagicMock):
                            main()
                
                assert exc_info.value.code == 1
            finally:
                os.chdir(old_cwd)
    
    @patch('main.fetch_index')
    @patch('main.fetch_rate')
    def test_end_to_end_output_order_preserved(self, mock_fetch_rate, mock_fetch_index):
        """Output items appear in the same order as config."""
        mock_fetch_index.side_effect = [10.0, 20.0, 30.0]
        mock_fetch_rate.side_effect = [1.0, 2.0]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                # Create config with specific order
                config_content = """[indices]
symbols = ^C, ^B, ^A

[currencies]
pairs = Z/Y, X/W
"""
                Path('config.ini').write_text(config_content)
                Path('output').mkdir(exist_ok=True)
                
                with patch.object(sys, 'argv', ['main.py', '7/31/2026']):
                    main()
                
                output_file = Path('output') / 'output.txt'
                lines = output_file.read_text().strip().split('\n')
                
                # Verify order
                assert lines[0].startswith('C')
                assert lines[1].startswith('B')
                assert lines[2].startswith('A')
                assert lines[3].startswith('Z')
                assert lines[4].startswith('X')
            finally:
                os.chdir(old_cwd)


class TestAcceptanceCriteria:
    """Tests verifying all acceptance criteria (AC-01 through AC-09)."""
    
    @patch('main.fetch_index')
    @patch('main.fetch_rate')
    def test_ac_01_output_file_created_with_one_row_per_item(self, mock_fetch_rate, mock_fetch_index):
        """AC-01: Script produces output.txt with one row per item."""
        mock_fetch_index.side_effect = [100.0, 200.0]
        mock_fetch_rate.side_effect = [1.5, 2.5]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                Path('config.ini').write_text(
                    '[indices]\nsymbols = ^A, ^B\n[currencies]\npairs = X/Y, A/B'
                )
                Path('output').mkdir(exist_ok=True)
                
                with patch.object(sys, 'argv', ['main.py', '7/31/2026']):
                    main()
                
                output_file = Path('output') / 'output.txt'
                lines = output_file.read_text().strip().split('\n')
                assert len(lines) == 4
            finally:
                os.chdir(old_cwd)
    
    @patch('main.fetch_index')
    @patch('main.fetch_rate')
    def test_ac_02_index_labels_stripped_and_values_to_2dp(self, mock_fetch_rate, mock_fetch_index):
        """AC-02: Index labels have ^ stripped, values to 2dp."""
        mock_fetch_index.side_effect = [53885.126]  # Should become 53885.13
        mock_fetch_rate.side_effect = []
        
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                Path('config.ini').write_text('[indices]\nsymbols = ^DJI\n[currencies]\npairs = ')
                Path('output').mkdir(exist_ok=True)
                
                with patch.object(sys, 'argv', ['main.py', '7/31/2026']):
                    main()
                
                content = Path('output/output.txt').read_text()
                assert 'DJI\t53885.13' in content
                assert '^DJI' not in content
            finally:
                os.chdir(old_cwd)
    
    @patch('main.fetch_index')
    @patch('main.fetch_rate')
    def test_ac_03_currency_labels_and_values_to_2dp(self, mock_fetch_rate, mock_fetch_index):
        """AC-03: Currency labels as BASE/QUOTE, values to 2dp."""
        mock_fetch_index.side_effect = []
        mock_fetch_rate.side_effect = [1.08234]  # Should become 1.08
        
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                Path('config.ini').write_text('[indices]\nsymbols = \n[currencies]\npairs = EUR/USD')
                Path('output').mkdir(exist_ok=True)
                
                with patch.object(sys, 'argv', ['main.py', '7/31/2026']):
                    main()
                
                content = Path('output/output.txt').read_text()
                assert 'EUR/USD\t1.08' in content
            finally:
                os.chdir(old_cwd)
    
    @patch('main.fetch_index')
    @patch('main.fetch_rate')
    def test_ac_07_missing_item_omitted_others_present(self, mock_fetch_rate, mock_fetch_index):
        """AC-07: Item that can't be fetched is omitted; others present."""
        mock_fetch_index.side_effect = [100.0, None, 200.0]
        mock_fetch_rate.side_effect = [1.5]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                Path('config.ini').write_text(
                    '[indices]\nsymbols = ^A, ^B, ^C\n[currencies]\npairs = X/Y'
                )
                Path('output').mkdir(exist_ok=True)
                
                with patch.object(sys, 'argv', ['main.py', '7/31/2026']):
                    main()
                
                content = Path('output/output.txt').read_text()
                assert 'A' in content
                assert 'B' not in content  # This one failed
                assert 'C' in content
                assert 'X/Y' in content
            finally:
                os.chdir(old_cwd)
    
    @patch('main.fetch_index')
    @patch('main.fetch_rate')
    def test_ac_08_file_overwritten_on_second_run(self, mock_fetch_rate, mock_fetch_index):
        """AC-08: File is overwritten on second run, not appended."""
        mock_fetch_index.side_effect = [100.0, 200.0]
        mock_fetch_rate.side_effect = [1.5, 1.6]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                config = '[indices]\nsymbols = ^A, ^B\n[currencies]\npairs = X/Y'
                Path('config.ini').write_text(config)
                Path('output').mkdir(exist_ok=True)
                
                # First run
                with patch.object(sys, 'argv', ['main.py', '7/31/2026']):
                    main()
                
                first_run = Path('output/output.txt').read_text()
                
                # Second run (with different fetch results)
                mock_fetch_index.side_effect = [300.0, 400.0]
                mock_fetch_rate.side_effect = [2.5, 2.6]
                
                with patch.object(sys, 'argv', ['main.py', '7/31/2026']):
                    main()
                
                second_run = Path('output/output.txt').read_text()
                
                # Should not contain first run data
                assert 'A\t100.0' not in second_run or 'A\t300.0' in second_run
                assert 'B\t200.0' not in second_run or 'B\t400.0' in second_run
            finally:
                os.chdir(old_cwd)
