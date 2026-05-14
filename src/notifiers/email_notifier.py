import os
import smtplib
from email.mime.text import MIMEText


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

_FLAG_EXPLANATIONS = {
    "yield_curve": (
        "Yield curve is inverted and trending more negative — "
        "short-term rates exceed long-term rates, a historical recession signal."
    ),
    "real_yield": (
        "10-year real yield is rising week-over-week — "
        "tightening real financial conditions, headwind for growth assets."
    ),
    "credit_spread": (
        "High-yield credit spread is elevated or has widened sharply — "
        "markets are pricing higher default risk."
    ),
    "cftc": (
        "Leveraged fund net long positioning in Nasdaq Mini futures is above "
        "the 80th percentile of the past 52 weeks — crowded positioning raises reversal risk."
    ),
}


def build_body(scored: dict, run_date: str) -> str:
    indicators = scored["indicators"]
    score = scored["score"]
    status = scored["status"]

    def fmt_value(result: dict) -> str:
        if "error" in result:
            return f"ERROR: {result['error']}"
        val = result.get("current")
        return f"{val:.2f}" if val is not None else "N/A"

    def fmt_flag(result: dict) -> str:
        if "error" in result:
            return "UNAVAILABLE"
        return "FLAGGED" if result.get("flagged") else "OK"

    yc = indicators.get("yield_curve", {})
    ry = indicators.get("real_yield", {})
    cs = indicators.get("credit_spread", {})
    cftc = indicators.get("cftc", {})

    lines = [
        f"MARKET STRESS MONITOR — {run_date}",
        "",
        f"OVERALL SCORE: {score}/4 — {status}",
        "",
        "INDICATORS",
        "----------",
        f"Yield Curve (T10Y2Y):     {fmt_value(yc)}  [{fmt_flag(yc)}]",
        f"Real Yield (DFII10):      {fmt_value(ry)}  [{fmt_flag(ry)}]",
        f"HY Credit Spread:         {fmt_value(cs)}  [{fmt_flag(cs)}]",
        f"CFTC Nasdaq Positioning:  {fmt_value(cftc)}  [{fmt_flag(cftc)}]",
    ]

    notes = []
    if yc.get("flagged"):
        notes.append(_FLAG_EXPLANATIONS["yield_curve"])
    if ry.get("flagged"):
        notes.append(_FLAG_EXPLANATIONS["real_yield"])
    if cs.get("flagged"):
        notes.append(_FLAG_EXPLANATIONS["credit_spread"])
    if cftc.get("flagged"):
        notes.append(_FLAG_EXPLANATIONS["cftc"])

    lines += ["", "NOTES", "-----"]
    if notes:
        lines += notes
    else:
        lines.append("No flags triggered.")

    lines += ["", "---", "This is an automated daily signal. Not financial advice."]
    return "\n".join(lines)


def send(scored: dict, run_date: str) -> None:
    gmail_user = os.environ["GMAIL_USER"]
    gmail_password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = os.environ["ALERT_EMAIL_TO"]

    body = build_body(scored, run_date)
    subject = f"Market Stress Monitor — {scored['status']} ({scored['score']}/4) — {run_date}"

    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = recipient

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, [recipient], msg.as_string())
