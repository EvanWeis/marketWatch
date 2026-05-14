import statistics

from src.api_factory import get_adapter


class CftcPositioningRepo:
    def get(self, config: dict) -> dict:
        try:
            adapter = get_adapter("cftc")
            weeks = config["cftc"]["weeks"]
            raw = adapter.fetch(weeks=weeks)
            records = raw.get("value", [])
            if not records:
                return {"error": "No CFTC records returned", "flagged": False}

            net_longs = []
            for r in records:
                try:
                    long_pos = float(r["Lev_Money_Positions_Long_All"])
                    short_pos = float(r["Lev_Money_Positions_Short_All"])
                    net_longs.append(long_pos - short_pos)
                except (KeyError, TypeError, ValueError):
                    continue

            if not net_longs:
                return {"error": "Could not parse net long positions", "flagged": False}

            current_net = net_longs[0]
            pct = config["cftc"]["percentile_threshold"]
            # statistics.quantiles uses exclusive method by default (n=4 for quartiles).
            # For an arbitrary percentile, use n=100 cut points.
            cutoff = statistics.quantiles(net_longs, n=100)[pct - 1]
            flagged = current_net > cutoff

            return {
                "current": current_net,
                "percentile_cutoff": cutoff,
                "flagged": flagged,
                "label": config["cftc"]["label"],
            }
        except Exception as exc:
            return {"error": str(exc), "flagged": False,
                    "label": config["cftc"]["label"]}
