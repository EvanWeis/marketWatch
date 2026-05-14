from datetime import date, timedelta

from src.api_factory import get_adapter


def _parse_observations(raw: dict) -> list[dict]:
    return [o for o in raw.get("observations", []) if o.get("value") != "."]


def _closest_to_date(observations: list[dict], target: date) -> float | None:
    best = None
    best_delta = None
    for obs in observations:
        try:
            obs_date = date.fromisoformat(obs["date"])
            delta = abs((obs_date - target).days)
            if best_delta is None or delta < best_delta:
                best_delta = delta
                best = float(obs["value"])
        except (KeyError, ValueError):
            continue
    return best


class RealYieldRepo:
    def get(self, config: dict) -> dict:
        try:
            adapter = get_adapter("fred")
            days = config["fred"]["observation_days"]
            raw = adapter.fetch("DFII10", observation_days=days)
            observations = _parse_observations(raw)
            if not observations:
                return {"error": "No observations returned", "flagged": False}

            current = _closest_to_date(observations, date.today())
            prior = _closest_to_date(observations, date.today() - timedelta(days=7))

            if current is None:
                return {"error": "Could not extract current value", "flagged": False}

            flagged = (prior is not None) and (current > prior)

            return {
                "current": current,
                "prior": prior,
                "flagged": flagged,
                "label": config["fred"]["series"]["DFII10"]["label"],
            }
        except Exception as exc:
            return {"error": str(exc), "flagged": False,
                    "label": config["fred"]["series"]["DFII10"]["label"]}
