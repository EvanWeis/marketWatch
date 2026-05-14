# Market Stress Monitor

A daily automated monitor for macro stress signals in tech and AI-exposed equity markets. Runs as a GitHub Actions workflow every weekday at 8am ET. Delivers results by email and an Atom RSS feed committed to this repository.

---

## What it monitors

| Indicator | Source | Flag condition |
|---|---|---|
| Yield curve (T10Y2Y) | FRED | Inverted **and** trending more negative week-over-week |
| 10Y real yield (DFII10) | FRED | Rising week-over-week |
| HY credit spread (BAMLH0A0HYM2) | FRED | > 400 bps **or** risen > 20 bps in 7 days |
| CFTC Nasdaq Mini net long | CFTC | Above 80th percentile of trailing 52 weeks |

Each flag adds 1 point to the overall score (0–4):

| Score | Status |
|---|---|
| 0–1 | NEUTRAL |
| 2 | ELEVATED |
| 3 | WARNING |
| 4 | CRITICAL |

---

## Setup

### 1. Fork this repository

Fork to your own GitHub account so you can configure secrets and enable Actions.

### 2. Add GitHub Actions secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Value |
|---|---|
| `GMAIL_USER` | Your Gmail address used to send alerts |
| `GMAIL_APP_PASSWORD` | A Gmail [App Password](https://support.google.com/accounts/answer/185833) (not your account password) |
| `ALERT_EMAIL_TO` | The email address to receive alerts |

### 3. Enable GitHub Actions

Actions are enabled by default on forks. Confirm the workflow is active under the **Actions** tab.

The monitor will now run automatically every weekday at 8am ET. You can also trigger it manually from the **Actions** tab using **Run workflow**.

---

## RSS Feed

After each run, `feed.xml` is committed to the repository root. Subscribe to it at:

```
https://raw.githubusercontent.com/{your-username}/{your-repo}/main/feed.xml
```

Paste this URL into any RSS reader (Feedly, NetNewsWire, etc.). The feed is capped at 90 entries.

---

## Running locally

```bash
pip install -r requirements.txt

export GMAIL_USER=you@gmail.com
export GMAIL_APP_PASSWORD=your-app-password
export ALERT_EMAIL_TO=recipient@example.com

python src/main.py
```

---

## Running tests

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## Adjusting thresholds

All thresholds are in `config.yml` — no Python changes needed:

```yaml
fred:
  series:
    BAMLH0A0HYM2:
      absolute_threshold: 400   # bps
      weekly_delta_threshold: 20

cftc:
  percentile_threshold: 80
```

---

## Architecture

```
src/
  adapters/         # One file per API source. Implement BaseAdapter.fetch()
  repositories/     # One file per indicator. Consumers of adapters only.
  scoring/          # Stateless scoring engine. Reads thresholds from config.
  notifiers/        # Email sender and RSS feed writer.
  api_factory.py    # Maps source names to adapter instances.
  main.py           # Orchestration only. No business logic.
```

Adding a new indicator requires: one adapter file (if new source), one repository file, one scoring rule in `config.yml`. No changes to core modules.

---

*This is an automated signal monitor. Not financial advice.*
