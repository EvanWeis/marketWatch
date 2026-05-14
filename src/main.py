import os
import sys
from datetime import date

import yaml

from src.repositories.yield_curve_repo import YieldCurveRepo
from src.repositories.real_yield_repo import RealYieldRepo
from src.repositories.credit_spread_repo import CreditSpreadRepo
from src.repositories.cftc_positioning_repo import CftcPositioningRepo
from src.scoring import scoring_engine
from src.notifiers import email_notifier, feed_writer


def load_config() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.yml")
    with open(os.path.abspath(config_path)) as f:
        return yaml.safe_load(f)


def main() -> int:
    config = load_config()
    run_date = date.today().isoformat()

    indicators = {
        "yield_curve": YieldCurveRepo().get(config),
        "real_yield": RealYieldRepo().get(config),
        "credit_spread": CreditSpreadRepo().get(config),
        "cftc": CftcPositioningRepo().get(config),
    }

    scored = scoring_engine.score(indicators, config)

    body = email_notifier.build_body(scored, run_date)

    try:
        email_notifier.send(scored, run_date)
        print(f"Email sent. Score: {scored['score']}/4 — {scored['status']}")
    except Exception as exc:
        print(f"Email failed: {exc}", file=sys.stderr)

    try:
        feed_writer.write(scored, run_date, body, config["feed"]["max_entries"])
        print("feed.xml updated.")
    except Exception as exc:
        print(f"Feed write failed: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
