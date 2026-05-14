def score(indicators: dict, config: dict) -> dict:
    """
    Accept a dict of indicator results keyed by name.
    Return overall score, status, and the full indicator map.
    """
    total = sum(1 for r in indicators.values() if r.get("flagged"))

    thresholds = config["scoring"]["thresholds"]
    if total <= thresholds["neutral"][1]:
        status = "NEUTRAL"
    elif total <= thresholds["elevated"][1]:
        status = "ELEVATED"
    elif total <= thresholds["warning"][1]:
        status = "WARNING"
    else:
        status = "CRITICAL"

    return {
        "score": total,
        "status": status,
        "indicators": indicators,
    }
