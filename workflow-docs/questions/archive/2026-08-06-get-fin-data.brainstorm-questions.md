---
status: ingested
feature: get-fin-data
phase: brainstorm
created: 2026-08-06 00:00 UTC
ingested_into: workflow-docs/audit.md
ingested_at: 2026-08-06 00:30 UTC
---

# Brainstorm Questions — get-fin-data

Answer each question by filling in `[Answer]: ` with the letter of your choice (or a freeform answer after "Other").

---

## Q1: Oanda access method

Oanda offers both a public website and an official REST API (requires a free/live account + API key). Which should the app use?

A. Oanda v20 REST API (requires account + API key — most reliable, returns exact mid/bid/ask rates)
B. Scrape the public Oanda.com website (no account needed, but fragile if layout changes)
C. Other

[Answer]: B

---

## Q2: Yahoo Finance access method

yfinance is the most common Python library for Yahoo Finance data. Are there any constraints on using it, or should the app use a different approach?

A. Use `yfinance` library (install via pip, no API key needed)
B. Use Yahoo Finance REST API directly (manual HTTP requests, no library)
C. Other (specify)

[Answer]: A

---

## Q3: Price type for indices

When a date is provided, which price should the app retrieve for each index?

A. Adjusted closing price for that calendar date
B. Regular (unadjusted) closing price for that calendar date
C. Other (e.g., open, high, low)

[Answer]: A

---

## Q4: Non-trading day behaviour

If the supplied date is a weekend or market holiday (no trading data available), what should the app do?

A. Use the most recent prior trading day's close (e.g., Monday → Friday's close)
B. Exit with a clear error message and do not produce output
C. Other

[Answer]: A

---

## Q5: Currency rate type (Oanda)

What rate should the app record for each currency pair?

A. Mid-rate (average of bid and ask) at market close on the given date
B. Bid rate
C. Ask rate
D. Other (e.g., daily average, specific time)

[Answer]: B

---

## Q6: Currency pair format in config and output

How should currency pairs be expressed in the config file and in the output file?

A. Slash-separated (e.g., `EUR/USD`) — config and output both use this format
B. Concatenated (e.g., `EURUSD`) — config and output both use this format
C. Other (different format for config vs. output)

[Answer]: A

---

## Q7: Configuration file format

What format should the configuration file use?

A. YAML (e.g., `config.yaml`)
B. TOML (e.g., `config.toml`)
C. JSON (e.g., `config.json`)
D. INI / plain key-value (e.g., `config.ini`)
E. Other

[Answer]: D

---

## Q8: Output file format and naming

How should the output file be formatted and named?

A. Plain text, space-separated, one item per line; named by date (e.g., `2026-07-31.txt`)
B. CSV (comma-separated); named by date (e.g., `2026-07-31.csv`)
C. Plain text, tab-separated; fixed filename (e.g., `output.txt`, overwritten each run)
D. Other

[Answer]: C

---

## Q9: Output file location

Where should the output file be written?

A. A dedicated `output/` subfolder within the project
B. The current working directory where the script is run
C. A path specified in the config file
D. Other

[Answer]: A

---

## Q10: How the date is passed to the app

How will the date be supplied at runtime?

A. Command-line argument (e.g., `python main.py 7/31/2026`)
B. Environment variable
C. Prompted interactively at runtime
D. Other

[Answer]: A

---

## Q11: Python version and packaging

Any constraints on Python version or project packaging?

A. No constraints — use whatever is simplest (Python 3.10+, plain requirements.txt)
B. Python 3.12+ specifically
C. Must use a specific package manager (Poetry, uv, conda, etc.)
D. Other

[Answer]: A

---

## Q12: Secrets / API key storage

If Oanda API is chosen (Q1-A), how should the API key be stored?

A. `.env` file (loaded via `python-dotenv`), excluded from version control
B. Environment variable set by the user before running
C. In the config file (less secure — only if no API key is needed)
D. N/A — not using the Oanda API (scraping instead)
E. Other

[Answer]: D
