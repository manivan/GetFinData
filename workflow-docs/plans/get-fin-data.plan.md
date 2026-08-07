# Plan: get-fin-data

**Feature**: get-fin-data  
**Phase**: Write Plan  
**Created**: 2026-08-06  
**Approach**: Vertical slices (tracer bullets through all layers)

---

## Overview

This plan converts the spec into a sequence of **vertical slices**, each of which delivers a thin but complete path from CLI input through to file output. Each slice is independently testable and shippable. Upon completion, all acceptance criteria will be met and the script will be production-ready.

---

## Vertical Slice Breakdown

The plan is organized into 4 core slices, each building on prior slices:

1. **Slice 1**: Project setup + core scaffolding (CLI parsing, date validation, config loading)
2. **Slice 2**: Indices fetching with fallback (yfinance integration)
3. **Slice 3**: Currencies fetching (frankfurter.app integration)
4. **Slice 4**: End-to-end integration + output formatting

Each slice includes its own tests and can be validated independently.

---

## Slice 1: Project Setup and Core Scaffolding

**Goal**: Establish project structure, CLI argument parsing, date validation, and config file loading. Verify basic I/O and configuration flow.

### Steps

1. Create project directory structure:
   - `GetFinData/` (root)
   - `GetFinData/fetchers/` (subdirectory for fetcher modules)
   - `GetFinData/tests/` (test suite)
   - `GetFinData/output/` (output directory)

2. Create `requirements.txt` with core dependencies:
   - `yfinance>=0.2.30`
   - `requests>=2.28.0`
   - `pytest>=7.0`
   - `pytest-mock>=3.10` (for mocking)

3. Create `main.py` with:
   - `parse_date(date_str: str) -> date` — validates CLI arg in `M/D/YYYY` format
   - `load_config() -> dict` — reads `config.ini` and returns `{"indices": [...], "currencies": [...]}`
   - `main()` — entry point that parses args, loads config, and prints a summary

4. Create `config.ini` (sample) with example indices and currency pairs:
   ```ini
   [indices]
   symbols = ^DJI, ^GSPC, ^IXIC
   
   [currencies]
   pairs = EUR/USD, GBP/USD
   ```

5. Create `fetchers/__init__.py` (empty module init)

6. Create `tests/` directory structure and first test file `tests/test_main.py`:
   - Test `parse_date()` with valid date, invalid date, wrong format
   - Test `load_config()` with valid file, missing file
   - Test basic script invocation

### Files to Change

- Create: `main.py`
- Create: `config.ini` (sample)
- Create: `requirements.txt`
- Create: `fetchers/__init__.py`
- Create: `tests/test_main.py`
- Create: `.gitignore` (exclude `output/`, `__pycache__`, `.pytest_cache`)

### Checkpoint 1

**Validation**:
```bash
cd /Users/IXMT/Development/Projects/Python/GetFinData
python main.py 7/31/2026  # Should parse successfully, load config, print summary
pytest tests/test_main.py -v  # All date/config tests pass
```

**Expected**:
- Script exits with code 0, prints config-loaded message to stdout.
- Date parsing rejects invalid formats.
- Config file is correctly parsed.
- All unit tests pass.

**Acceptance Criteria Covered**: AC-01 (partial, structure in place), AC-06 (date validation error handling)

---

## Slice 2: Indices Fetching with Fallback

**Goal**: Integrate yfinance, implement the 7-day fallback logic, and output index data to file.

### Steps

1. Create `fetchers/indices.py`:
   - `fetch_index(ticker: str, target: date) -> float | None`
   - Calls yfinance with fallback loop (up to 7 days)
   - Returns rounded adjusted close or `None` if not found
   - Logs warnings for missing data

2. Modify `main.py`:
   - Import `fetch_index` from `fetchers.indices`
   - Call `fetch_index()` for each configured ticker
   - Collect results into a dict `{ticker_label: value}`
   - Call new function `write_output()` to write results to `output/output.txt`

3. Create `write_output(indices: dict, currencies: dict) -> None`:
   - Create `output/` directory if missing
   - Write tab-separated rows to `output/output.txt`
   - Format: index label (ticker with `^` stripped), then value to 2 dp
   - Output indices first, then currencies (both in config order)

4. Create `tests/test_indices.py`:
   - Mock yfinance downloads
   - Test successful fetch on target date
   - Test fallback to prior day (step back 1 day)
   - Test fallback exhaustion (return `None` after 7 days)
   - Test output formatting (label stripping, decimal rounding)

### Files to Change

- Create: `fetchers/indices.py`
- Modify: `main.py` (add `fetch_index` calls, `write_output()` function)
- Create: `tests/test_indices.py`

### Checkpoint 2

**Validation**:
```bash
pytest tests/test_indices.py -v  # All index fetch and fallback tests pass
python main.py 7/31/2026  # Outputs index data to output/output.txt
cat output/output.txt  # Shows indices only (currencies not yet implemented)
```

**Expected**:
- Indices are fetched and written with correct labels and decimal formatting.
- Fallback logic works (yfinance calls step back day-by-day).
- `output/output.txt` contains one row per index (tab-separated).
- Warnings logged for missing indices.

**Acceptance Criteria Covered**: AC-01 (indices only), AC-02, AC-04, AC-07 (partial, indices only), AC-08 (file overwrite)

---

## Slice 3: Currencies Fetching

**Goal**: Integrate frankfurter.app API, fetch exchange rates, and merge results with indices output.

### Steps

1. Create `fetchers/currencies.py`:
   - `fetch_rate(base: str, quote: str, date: date) -> float | None`
   - Calls `GET https://api.frankfurter.app/{YYYY-MM-DD}?from={base}&to={quote}`
   - Parses JSON response, extracts `rates[quote]`
   - Returns rate rounded to 2 dp or `None` if not found or non-200 response
   - Logs warnings for failures

2. Modify `main.py`:
   - Import `fetch_rate` from `fetchers.currencies`
   - Call `fetch_rate()` for each configured currency pair
   - Collect results into a dict `{pair_label: value}`
   - Pass both `indices_dict` and `currencies_dict` to `write_output()`

3. Modify `write_output()`:
   - Now receives both dicts and writes all results
   - Output order: all indices first (in config order), then all currencies (in config order)

4. Create `tests/test_currencies.py`:
   - Mock HTTP requests to frankfurter.app
   - Test successful rate fetch with valid JSON response
   - Test handling of non-200 HTTP responses
   - Test handling of missing pair in response
   - Test decimal rounding

### Files to Change

- Create: `fetchers/currencies.py`
- Modify: `main.py` (add `fetch_rate` calls, update `write_output` signature)
- Modify: `tests/test_main.py` (integration test now includes both indices and currencies)
- Create: `tests/test_currencies.py`

### Checkpoint 3

**Validation**:
```bash
pytest tests/test_currencies.py -v  # All currency fetch tests pass
python main.py 7/31/2026  # Outputs both indices and currencies to output/output.txt
cat output/output.txt  # Shows indices, then currencies
```

**Expected**:
- Both indices and currencies fetched and formatted correctly.
- `output/output.txt` has indices first, then currencies, all tab-separated.
- Warnings logged for missing currencies.
- Currency labels are `BASE/QUOTE` (from config).

**Acceptance Criteria Covered**: AC-01, AC-02, AC-03, AC-04, AC-07

---

## Slice 4: End-to-End Integration + Output & Logging

**Goal**: Complete integration, verify output formatting, add summary logging to stdout/stderr, and validate all acceptance criteria.

### Steps

1. Add comprehensive logging:
   - Import `logging` module
   - Configure stderr for warnings/errors, stdout for summary
   - Print summary to stdout on completion: date used, count of fetched items, output file path
   - Print warnings to stderr for any items that could not be fetched (already in place from slices 2–3)

2. Create integration test `tests/test_integration.py`:
   - Mock both yfinance and frankfurter.app
   - Test end-to-end with known data (mock all external calls)
   - Verify output file format, order, and overwrite behavior
   - Test behavior when some items fail to fetch (partial output)
   - Test empty config sections
   - Test all acceptance criteria together

3. Validate edge cases:
   - Missing `config.ini` → error message to stderr, exit code 1
   - Empty ticker/pair list → script handles gracefully
   - Invalid CLI date argument → error message to stderr, exit code 1
   - Network failure (mocked) → warnings logged, partial output written

4. Add sample run documentation:
   - Update or create `README.md` with usage examples and expected output

### Files to Change

- Modify: `main.py` (add logging, summary output, exit codes)
- Create: `tests/test_integration.py`
- Create/Modify: `README.md` (usage, examples)

### Checkpoint 4 (Final)

**Validation**:
```bash
pytest tests/ -v  # All tests pass (unit + integration)
python main.py 7/31/2026  # Script runs successfully
cat output/output.txt  # Correct format, values, order
python main.py 7/31/2026  # Run again to verify overwrite (not append)
python main.py invalid_date  # Error message, exit code 1
```

**Expected**:
- All 13 acceptance criteria (AC-01 through AC-09) verified.
- Summary printed to stdout.
- Warnings printed to stderr for missing items.
- Output file overwritten on second run.
- Script exits with code 0 on success, code 1 on error.
- No credentials or API keys required.

---

## Files to Create/Modify

### Create (new files)

- `main.py` — Entry point and orchestration
- `config.ini` — Sample configuration
- `requirements.txt` — Python dependencies
- `fetchers/__init__.py` — Package init
- `fetchers/indices.py` — yfinance integration
- `fetchers/currencies.py` — frankfurter.app integration
- `tests/test_main.py` — Core tests (date, config)
- `tests/test_indices.py` — Index fetching tests
- `tests/test_currencies.py` — Currency fetching tests
- `tests/test_integration.py` — End-to-end tests
- `.gitignore` — Exclude output/, __pycache__, .pytest_cache

### Modify (if already exist)

- `README.md` — Add usage documentation

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| yfinance API changes or ticker symbol errors | Medium | Low | Mock all yfinance calls in tests; validate with live test on a known date |
| frankfurter.app downtime or API changes | Medium | Low | Mock all HTTP calls in tests; test with a known working pair locally |
| Date parsing edge cases (leap years, month boundaries) | Low | Low | Use Python's `datetime.strptime()` which handles all cases; test boundary dates |
| Config file missing at runtime | Low | Medium | Check for file existence in `load_config()` and raise clear error with exit code 1 |
| Empty config sections or whitespace issues | Low | Low | Use `configparser` with careful strip/split logic; test with edge-case configs |
| Output directory not writable | Low | Medium | Create `output/` upfront and test write permissions; catch `OSError` and log clearly |

---

## Test Strategy

- **Unit tests**: Date parsing, config loading, fetcher logic (all external calls mocked)
- **Integration tests**: Full script run with mocked external dependencies
- **No live API calls**: All tests use mocks (`pytest-mock`, `unittest.mock`)

Test coverage target: ≥ 90% (all critical paths exercised)

---

## Acceptance Criteria → Verification Mapping

| AC ID | Criterion | Verified In Slice | Test ID(s) |
|---|---|---|---|
| AC-01 | Script produces output.txt with one row per item | 2, 3, 4 | T-10, T-13 |
| AC-02 | Index labels stripped of `^`, values to 2 dp | 2 | T-13 |
| AC-03 | Currency labels as `BASE/QUOTE`, values to 2 dp | 3 | T-13 |
| AC-04 | Non-trading day returns nearest prior valid data | 2, 3 | T-06, (frankfurter handles automatically) |
| AC-05 | Config changes update output without code changes | 1, 4 | T-10, Integration test |
| AC-06 | Invalid date prints error to stderr, exit 1 | 1, 4 | T-02, Integration test |
| AC-07 | Missing item omitted, others present | 2, 3, 4 | T-12 |
| AC-08 | File overwritten on second run | 4 | T-11 |
| AC-09 | No API key required | 2, 3, 4 | All integration tests |

---

## Checkpoints Summary

| Checkpoint | After Slice | Key Validation |
|---|---|---|
| 1 | Setup | Date parsing, config loading, script scaffold works |
| 2 | Indices | Index data fetched, formatted, written to file with fallback |
| 3 | Currencies | Both indices and currencies output correctly formatted |
| 4 | Integration | All acceptance criteria met, summary logging, error handling complete |

---

## Next Steps

1. Start Slice 1 (Project Setup): Create directory structure, write `main.py` with CLI parsing and config loading, write `requirements.txt`.
2. Run Checkpoint 1: Validate date parsing and config loading with unit tests.
3. Proceed through Slices 2–4 in sequence, validating at each checkpoint.
4. After Slice 4, run full test suite (`pytest tests/`).
5. Verify with a live test run using a known historical date (e.g., `7/31/2026` if available, or adjust to a past date).
6. Tag release when all acceptance criteria are met.

---

## Notes

- This is a greenfield project, so all files are created from scratch.
- All external HTTP and yfinance calls are mocked in tests — no live API calls during CI/testing.
- The script is stateless; no persistent state or database.
- Manual CLI run only; no scheduling or automation out of scope.
