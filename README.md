# GetFinData

A Python CLI tool to fetch financial data (stock index closing prices and currency exchange rates) for a given date.

## Features

- Fetch adjusted closing prices for stock indices from Yahoo Finance
- Fetch exchange rates from frankfurter.app (ECB daily reference rates)
- Configurable via INI file (`config.ini`)
- Automatic fallback to most recent prior trading day if the requested date is a non-trading day
- Tab-separated output file for easy parsing

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python main.py M/D/YYYY [--no-verify-ssl]
```

Example:
```bash
python main.py 1/15/2025
```

**Optional flag** (for environments with SSL certificate issues):
```bash
python main.py --no-verify-ssl 1/15/2025
```

This will:
1. Parse the date (M/D/YYYY format)
2. Load configuration from `config.ini`
3. Fetch data for all configured indices and currency pairs
4. Write results to `output/output.txt`
5. Print a summary to stdout

### Configuration

Edit `config.ini` to specify which indices and currency pairs to fetch:

```ini
[indices]
symbols = ^DJI, ^GSPC, ^IXIC

[currencies]
pairs = EUR/USD, GBP/USD, CHF/USD
```

- **indices**: Comma-separated list of Yahoo Finance ticker symbols (e.g., `^DJI`, `^GSPC`)
- **currencies**: Comma-separated list of currency pairs in `BASE/QUOTE` format (e.g., `EUR/USD`)

Either section can be omitted or left empty.

### Output Format

Results are written to `output/output.txt` as tab-separated values:

```
DJI	53885.11
GSPC	5611.85
IXIC	6543.21
EUR/USD	1.0823
GBP/USD	1.2945
```

- Index labels: ticker symbol with leading `^` stripped (e.g., `^DJI` → `DJI`)
- Currency labels: pair as written in config (e.g., `EUR/USD`)
- Values: formatted to 2 decimal places
- Order: indices first (in config order), then currencies (in config order)

## Non-Trading Days

- **Indices**: Automatically steps back up to 7 calendar days to find the most recent prior trading session
- **Currencies**: frankfurter.app automatically returns the most recent ECB business day

## Error Handling

- Invalid date format → Error message to stderr, exit code 1
- Missing config file → Error message to stderr, exit code 1
- Failed fetch for specific item → Warning logged to stderr, item omitted from output
- File is overwritten on each run (not appended)
- Partial failures: If some items cannot be fetched, others are still included in the output

## SSL Certificate Issues

If you encounter SSL certificate verification errors (especially in corporate networks or with system certificate issues), use the `--no-verify-ssl` flag:

```bash
python main.py --no-verify-ssl 1/15/2025
```

⚠️ **Note**: This disables SSL certificate verification for the frankfurter.app API. Use only in testing environments or when you understand the security implications.

## Running Tests

```bash
pytest tests/
```

**Important**: All external API calls (yfinance, frankfurter.app) are mocked in tests. No live API calls occur during testing. This is why all tests pass reliably without requiring SSL certificate fixes.

### Test Types

- **Unit tests** (31 tests): Date parsing, config loading, individual fetchers with mocked external calls
- **Integration tests** (16 tests): End-to-end flows, output formatting, all acceptance criteria
- **Total**: 47 tests, all passing, fully deterministic

## Test Coverage

- Date parsing with validation (invalid formats rejected, exit code 1)
- Config loading and parsing
- yfinance integration with 7-day fallback
- frankfurter.app REST API with comprehensive error handling
- Output file creation, formatting, and overwrite behavior
- Partial failure handling
- All 9 acceptance criteria (AC-01 through AC-09)

## Comparing Tests vs Live Usage

| Aspect | Tests (Mocked) | Live Usage |
|---|---|---|
| External APIs | Mocked (deterministic) | Real (may have SSL/network issues) |
| Test Duration | ~1 second | ~5-10 seconds |
| Reliability | 100% ✅ | Depends on network/SSL setup |
| SSL Cert Issues | None (mocked) | May occur (use `--no-verify-ssl`) |

## Requirements

- Python 3.10+
- See `requirements.txt` for dependencies

## No Credentials Required

This tool uses free, public APIs:
- Yahoo Finance (via yfinance library)
- frankfurter.app (ECB daily reference rates, no API key needed)

## Troubleshooting

**Q: I get SSL certificate errors when running the script**  
A: Use the `--no-verify-ssl` flag to disable certificate verification:
```bash
python main.py --no-verify-ssl 1/15/2025
```

**Q: Why do tests pass but live usage fails?**  
A: Tests use mocked external APIs (deterministic, no network calls). Live usage makes real HTTP requests which may encounter SSL or network issues. Tests verify the application logic is correct.

**Q: No data found for a date — why?**  
A: The date may be:
- In the future (markets haven't traded yet)
- A weekend (no trading)
- A holiday when markets are closed
- 8+ days before the most recent trading day

The application tries to find data from the target date, then steps back up to 7 calendar days. If still no data, it logs a warning and omits that item.

## Author

Generated as part of the GetFinData project workflow.
