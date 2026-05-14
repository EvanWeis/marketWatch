# CLAUDE.md — Market Stress Monitor

This file provides context for AI coding agents working on this repository.

-----

## Project Purpose

This is a daily automated market stress monitor. It fetches financial indicator data from public APIs, scores them against predefined thresholds, and delivers a plain text digest via email and Atom RSS feed. It runs as a scheduled GitHub Actions workflow on weekdays.

The goal is early signal detection for macro stress conditions, particularly in tech and AI-exposed equity markets.

-----

## Architecture

This project follows two core patterns that must be preserved in all changes:

### Repository Pattern

Each financial indicator is encapsulated in its own repository class under `/src/repositories/`. Repositories are the only consumers of adapters. Nothing outside a repository should call an adapter directly.

### API Factory Pattern

`/src/api_factory.py` maps source identifiers to adapter instances. To add a new data source, add one adapter file to `/src/adapters/` and register it in the factory. No other files should need to change.

### Key constraint

When adding new indicators or sources, the rule is: **one new adapter file, one new repository file, one new scoring rule in config**. If a change requires touching the scoring engine, notifier, or workflow, that is a signal the architecture is being violated.

-----

## Data Sources

### FRED (Federal Reserve Economic Data)

- **Adapter:** `src/adapters/fred_adapter.py`
- **Base URL:** `https://api.stlouisfed.org/fred/series/observations`
- **Auth:** `DEMO_KEY` query param — no account required
- **Series in use:** `T10Y2Y`, `DFII10`, `BAMLH0A0HYM2`

### CFTC (Commodity Futures Trading Commission)

- **Adapter:** `src/adapters/cftc_adapter.py`
- **Base URL:** `https://publicreporting.cftc.gov/api/odata/v1/CorrectionsAndRevisions`
- **Auth:** None
- **Data:** Leveraged fund net positioning on Nasdaq Mini futures

-----

## Scoring

Scoring logic lives in `src/scoring/scoring_engine.py`. Thresholds are defined in `config.yml` — do not hardcode thresholds in Python files.

Current scoring model: 4 indicators, 1 point each, 0–4 scale.

|Score|Status  |
|-----|--------|
|0–1  |NEUTRAL |
|2    |ELEVATED|
|3    |WARNING |
|4    |CRITICAL|

-----

## Outputs

### Email

Plain text only. Sent via Gmail SMTP using `smtplib`. No HTML. Credentials come from GitHub Actions secrets.

### RSS Feed

Static Atom XML file (`feed.xml`) committed to the repo root after each run. Capped at 90 entries. Subscribable via raw GitHub URL.

-----

## Environment & Secrets

|Secret              |Purpose                                  |
|--------------------|-----------------------------------------|
|`GMAIL_USER`        |Gmail sending address                    |
|`GMAIL_APP_PASSWORD`|Gmail app password (not account password)|
|`ALERT_EMAIL_TO`    |Recipient email address                  |

Secrets are set in GitHub repository Settings → Secrets and variables → Actions.

-----

## Dependencies

- Python 3.11
- `requests` — only external HTTP library permitted
- No pandas. Use `statistics` module from stdlib for calculations.
- See `requirements.txt` for full list.

-----

## Workflow

File: `.github/workflows/daily_monitor.yml`

- Runs weekdays at 8am ET (`0 13 * * 1-5`)
- Can be triggered manually via `workflow_dispatch`
- On each run: fetch → score → email → update feed.xml → commit feed.xml

-----

## Extending This Project

### Adding a new FRED series (Phase 2 example: VIXCLS)

1. Add series ID and threshold to `config.yml`
1. Create `src/repositories/vix_repo.py` — extend `FredRepository` base
1. Add scoring rule to `scoring_engine.py`
1. No other files need to change

### Adding a new API source

1. Create `src/adapters/new_source_adapter.py` implementing `BaseAdapter.fetch(series_id) -> dict`
1. Register in `src/api_factory.py`
1. Create repository under `src/repositories/`
1. Add scoring rule and config thresholds

-----

## What Not To Do

- Do not call APIs directly from `main.py` or the scoring engine
- Do not hardcode thresholds — they belong in `config.yml`
- Do not use pandas or any data science libraries
- Do not send HTML email — plain text only
- Do not modify the workflow file unless changing schedule or secrets
- Do not break the `BaseAdapter` interface when adding adapters
