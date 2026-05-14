import unittest
from unittest.mock import patch, MagicMock

from src.adapters.fred_adapter import FredAdapter
from src.adapters.cftc_adapter import CftcAdapter


class TestFredAdapter(unittest.TestCase):
    @patch("src.adapters.fred_adapter.requests.get")
    def test_fetch_constructs_correct_url(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"observations": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        adapter = FredAdapter()
        result = adapter.fetch("T10Y2Y", observation_days=30)

        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args
        params = call_kwargs[1]["params"] if "params" in call_kwargs[1] else call_kwargs[0][1]
        self.assertEqual(params["series_id"], "T10Y2Y")
        self.assertEqual(params["api_key"], "DEMO_KEY")
        self.assertEqual(params["file_type"], "json")
        self.assertIn("observation_start", params)
        self.assertEqual(result, {"observations": []})

    @patch("src.adapters.fred_adapter.requests.get")
    def test_fetch_raises_on_http_error(self, mock_get):
        import requests
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("403")
        mock_get.return_value = mock_response

        adapter = FredAdapter()
        with self.assertRaises(Exception):
            adapter.fetch("T10Y2Y")

    @patch("src.adapters.fred_adapter.requests.get")
    def test_fetch_different_series(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"observations": [{"value": "1.5"}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        adapter = FredAdapter()
        adapter.fetch("BAMLH0A0HYM2", observation_days=30)

        call_params = mock_get.call_args[1]["params"]
        self.assertEqual(call_params["series_id"], "BAMLH0A0HYM2")


class TestCftcAdapter(unittest.TestCase):
    @patch("src.adapters.cftc_adapter.requests.get")
    def test_fetch_applies_nasdaq_filter(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"value": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        adapter = CftcAdapter()
        result = adapter.fetch(weeks=52)

        mock_get.assert_called_once()
        call_params = mock_get.call_args[1]["params"]
        self.assertIn("NASDAQ MINI", call_params["$filter"])
        self.assertEqual(call_params["$top"], 52)
        self.assertEqual(result, {"value": []})

    @patch("src.adapters.cftc_adapter.requests.get")
    def test_fetch_raises_on_http_error(self, mock_get):
        import requests
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("500")
        mock_get.return_value = mock_response

        adapter = CftcAdapter()
        with self.assertRaises(Exception):
            adapter.fetch()


if __name__ == "__main__":
    unittest.main()
