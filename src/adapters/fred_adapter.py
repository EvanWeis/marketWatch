from datetime import date, timedelta

import requests

from .base_adapter import BaseAdapter

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
API_KEY = "DEMO_KEY"


class FredAdapter(BaseAdapter):
    def fetch(self, series_id: str, observation_days: int = 30) -> dict:
        start = (date.today() - timedelta(days=observation_days)).isoformat()
        params = {
            "series_id": series_id,
            "api_key": API_KEY,
            "file_type": "json",
            "observation_start": start,
        }
        response = requests.get(FRED_BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
