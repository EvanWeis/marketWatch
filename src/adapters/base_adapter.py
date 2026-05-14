from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    @abstractmethod
    def fetch(self, series_id: str) -> dict:
        """Fetch data for the given series_id. Returns a raw response dict."""
