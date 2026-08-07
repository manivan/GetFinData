# Spec: get-fin-data

**Feature**: get-fin-data  
**Phase**: Write Spec  
**Created**: 2026-08-06  
**Status**: Final — no open questions

---

## Summary

A CLI Python script (`main.py`) that accepts a date argument, reads a configuration file listing stock market indices and currency pairs, fetches the relevant data from two sources (Yahoo Finance for indices, frankfurter.app for FX rates), and writes a tab-separated flat-file output (one item per line) to `output/output.txt`.

---

## Goals / Non-goals

### Goals
- Fetch adjusted closing prices for one or more stock indices from Yahoo Finance for a given date.
- Fetch mid-rate (ECB daily reference) exchange rates for one or more currency pairs from the frankfurter.app public API for a given date.
- Accept the target date as a CLI argument in `M/D/YYYY` format.
- Read indices and currency pairs from an INI config file (`config.ini`).
- Write results to `output/output.txt` (tab-separated, one row per item, overwritten each run).
- Handle non-trading days gracefully by falling back to the most recent prior available data point.

### Non-goals
- Real-time / intraday data.
- Oanda scraping or any paid data source.
- Separate bid/ask rates (ECB reference rate is a mid-rate; this is the accepted rate type).
- Multiple output formats (CSV, JSON, etc.).
- Scheduling / automation (the script is run manually).
- GUI or web interface.
- Storing historical results across runs (output is overwritten each run).

---

## Requirements

### FR-01 — Date input
The script accepts exactly one positional CLI argument: the target date in `M/D/YYYY` format (e.g., `7/31/2026`). Any other format is an error.

### FR-02 — Configuration file
A file named `config.ini` at the project root controls which items to fetch. It contains two sections:

```ini
[indices]
symbols = ^DJI, ^GSPC, ^IXIC

[currencies]
pairs = EUR/USD, GBP/USD
```

- `symbols`: comma-separated list of Yahoo Finance ticker symbols (e.g., `^DJI`, `^GSPC`).
- `pairs`: comma-separated list of currency pairs in `BASE/QUOTE` format (e.g., `EUR/USD`).
- Either section may be empty or omitted; the script processes whichever sections are present.

### FR-03 — Index data (Yahoo Finance via yfinance)
- Use the `yfinance` library to download adjusted closing prices.
- For each ticker, fetch data for the target date.
- If no data is returned for the target date (weekend / holiday / market closed), step back day-by-day (up to 7 calendar days) to find the most recent prior trading session's adjusted close.
- If no data is found within 7 days, log a warning and omit that ticker from the output.

### FR-04 — Currency data (frankfurter.app)
- For each `BASE/QUOTE` pair, call:  
  `GET https://api.frankfurter.app/{YYYY-MM-DD}?from={BASE}&to={QUOTE}`
- Parse the `rates` field from the JSON response.
- frankfurter.app automatically returns the most recent business day if the requested date is a weekend or ECB holiday — no additional fallback logic is needed.
- If the API returns a non-200 response or the pair is not found, log a warning and omit that pair from the output.

### FR-05 — Output file
- Write results to `output/output.txt` (create `output/` directory if it does not exist).
- Overwrite the file on every run.
- Format: one row per item, tab-separated label and value:
  ```
  DJI	53885.11
  GSPC	5611.85
  EUR/USD	1.0823
  GBP/USD	1.2945
  ```
- Index label: strip the leading `^` from the ticker symbol (e.g., `^DJI` → `DJI`).
- Currency label: use the pair as written in the config (e.g., `EUR/USD`).
- Values: formatted to 2 decimal places.
- Output order: all indices first (in config order), then all currency pairs (in config order).

### FR-06 — Logging
- Print a summary to stdout on completion: date used, items fetched, output file path.
- Print warnings to stderr for any items that could not be fetched.

### FR-07 — Dependencies
- Python 3.10+
- `yfinance` — Yahoo Finance data
- `requests` — HTTP calls to frankfurter.app
- `configparser` — INI file parsing (stdlib, no install needed)
- Dependencies listed in `requirements.txt`

---

## Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-01 | `python main.py 7/31/2026` produces `output/output.txt` with one tab-separated row per configured item. |
| AC-02 | Each index row label is the ticker symbol with `^` stripped; value is the adjusted close rounded to 2 dp. |
| AC-03 | Each currency row label is the `BASE/QUOTE` string from config; value is the mid-rate rounded to 2 dp. |
| AC-04 | Running on a date that is a weekend or holiday returns data from the nearest prior valid session (indices) or prior ECB business day (currencies). |
| AC-05 | Adding or removing a ticker/pair in `config.ini` changes the output on the next run without code changes. |
| AC-06 | An invalid date argument prints a clear error message to stderr and exits with code 1. |
| AC-07 | A ticker or pair that cannot be resolved logs a warning to stderr and is absent from the output; other items still appear. |
| AC-08 | Running the script twice for the same date overwrites `output/output.txt` (does not append). |
| AC-09 | No API key or credentials are required to run the script. |

---

## Design

### Directory structure

```
GetFinData/
├── main.py              # Entry point and orchestration
├── fetchers/
│   ├── __init__.py
│   ├── indices.py       # yfinance fetching logic
│   └── currencies.py    # frankfurter.app fetching logic
├── config.ini           # User-editable configuration
├── requirements.txt
└── output/              # Created at runtime
    └── output.txt
```

### Data flow

```
CLI argument (date string)
        │
        ▼
   parse_date()          M/D/YYYY → datetime.date
        │
        ▼
   load_config()         config.ini → list of tickers, list of pairs
        │
   ┌────┴────────────────┐
   ▼                     ▼
fetch_indices()     fetch_currencies()
(yfinance)          (frankfurter.app REST)
   │                     │
   └────────┬────────────┘
            ▼
      write_output()     output/output.txt
            │
            ▼
      print summary to stdout
```

### Key module responsibilities

| Module | Responsibility |
|---|---|
| `main.py` | Parse CLI args, load config, call fetchers, write output, print summary |
| `fetchers/indices.py` | `fetch_index(ticker, date) -> float \| None` — yfinance download + fallback loop |
| `fetchers/currencies.py` | `fetch_rate(base, quote, date) -> float \| None` — HTTP GET to frankfurter.app |

### frankfurter.app API

- Base URL: `https://api.frankfurter.app`
- Historical rate endpoint: `GET /{date}?from={BASE}&to={QUOTE}`
  - Example: `GET /2026-07-31?from=EUR&to=USD`
  - Response: `{"amount":1.0,"base":"EUR","date":"2026-07-31","rates":{"USD":1.0823}}`
- Coverage: ~30 major currencies tracked by the ECB. Exotic pairs not covered by ECB are unsupported and will produce a warning.
- No API key required. Rate limits: generous for single-user CLI use.

### yfinance usage

```python
import yfinance as yf
from datetime import date, timedelta

def fetch_index(ticker: str, target: date) -> float | None:
    for offset in range(8):           # try target date then up to 7 days back
        d = target - timedelta(days=offset)
        df = yf.download(ticker, start=d, end=d + timedelta(days=1), auto_adjust=True, progress=False)
        if not df.empty:
            return round(float(df["Close"].iloc[-1]), 2)
    return None
```

---

## Edge Cases

| Case | Behaviour |
|---|---|
| Target date is today or in the future | yfinance may return no data; fallback triggers as normal. |
| `config.ini` has empty `symbols` or `pairs` | Section is present but value is blank — treated as empty list; no fetch for that section. |
| `config.ini` is missing entirely | Script exits with a clear error message (exit code 1). |
| Currency pair `BASE == QUOTE` (e.g., `USD/USD`) | frankfurter.app returns `1.0`; written to output as-is. |
| Network unavailable | Both fetchers log warnings per item and the output file contains only successfully fetched items (may be empty). |
| `output/` directory does not exist | Created automatically before writing. |
| Ticker not found in yfinance (bad symbol) | Returns empty DataFrame; logged as warning; omitted from output. |
| Date argument in wrong format | `argparse` / `datetime.strptime` raises; script prints usage to stderr, exits 1. |
| ECB holidays (e.g., Christmas) | frankfurter.app handles automatically by returning the most recent prior business day. |

---

## Test Plan

Tests live in `tests/` and use `pytest`. External HTTP and yfinance calls are mocked.

| Test ID | Description | Type |
|---|---|---|
| T-01 | `parse_date("7/31/2026")` returns `date(2026, 7, 31)` | Unit |
| T-02 | `parse_date("13/1/2026")` raises `ValueError` | Unit |
| T-03 | `load_config()` with a valid `config.ini` returns correct ticker/pair lists | Unit |
| T-04 | `load_config()` with missing file raises `FileNotFoundError` | Unit |
| T-05 | `fetch_index` returns float when yfinance returns data for target date | Unit (mock) |
| T-06 | `fetch_index` steps back one day when target date has no data | Unit (mock) |
| T-07 | `fetch_index` returns `None` after 7-day fallback exhausted | Unit (mock) |
| T-08 | `fetch_rate` parses frankfurter.app JSON response correctly | Unit (mock) |
| T-09 | `fetch_rate` returns `None` on non-200 HTTP response | Unit (mock) |
| T-10 | End-to-end: given mocked fetchers returning known values, `output/output.txt` has correct content | Integration (mock) |
| T-11 | Output file is overwritten on second run, not appended | Integration (mock) |
| T-12 | Item that returns `None` is absent from output; other items present | Integration (mock) |
| T-13 | Index labels have `^` stripped; currency labels are `BASE/QUOTE` | Integration (mock) |

---

## Rollout / Backout

Not applicable — this is a local developer CLI tool with no deployment infrastructure.

---

## Open Questions (Resolved)

| # | Question | Resolution |
|---|---|---|
| 1 | Oanda API vs. scraping | Scraping abandoned due to JS-rendered page and lack of separate bid/ask on the public site. |
| 2 | Currency data source | frankfurter.app (free, no key, ECB daily reference rate / mid-rate, historical by date). |
| 3 | Rate type (bid vs. mid) | Mid-rate (ECB daily reference), accepted in place of bid — user confirmed Option B. |
| 4 | Non-trading day (indices) | Step back up to 7 calendar days to find the nearest prior trading session. |
| 5 | Non-trading day (currencies) | frankfurter.app handles automatically. |
| 6 | Config format | INI (`config.ini`), using stdlib `configparser`. |
| 7 | Output format | Tab-separated, `output/output.txt`, overwritten each run. |
| 8 | Date input | CLI positional argument, `M/D/YYYY` format. |
| 9 | Index output label | Ticker with `^` stripped. |
| 10 | ECB coverage limitation | Exotic currency pairs not in the ECB basket will produce a warning and be omitted. |
