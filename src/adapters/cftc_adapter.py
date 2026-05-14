import requests

from .base_adapter import BaseAdapter

CFTC_BASE_URL = "https://publicreporting.cftc.gov/api/odata/v1/CorrectionsAndRevisions"
MARKET_FILTER = "Market_and_Exchange_Names eq 'NASDAQ MINI - CHICAGO MERCANTILE EXCHANGE'"


class CftcAdapter(BaseAdapter):
    def fetch(self, series_id: str = None, weeks: int = 52) -> dict:
        params = {
            "$filter": MARKET_FILTER,
            "$orderby": "Report_Date_as_YYYY_MM_DD desc",
            "$top": weeks,
        }
        response = requests.get(CFTC_BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
