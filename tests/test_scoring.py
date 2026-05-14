import unittest

from src.scoring.scoring_engine import score

CONFIG = {
    "scoring": {
        "thresholds": {
            "neutral":   [0, 1],
            "elevated":  [2, 2],
            "warning":   [3, 3],
            "critical":  [4, 4],
        }
    }
}


def _make_indicators(flags: dict) -> dict:
    return {
        "yield_curve":   {"flagged": flags.get("yield_curve", False), "current": -0.5},
        "real_yield":    {"flagged": flags.get("real_yield", False),  "current": 2.1},
        "credit_spread": {"flagged": flags.get("credit_spread", False), "current": 350.0},
        "cftc":          {"flagged": flags.get("cftc", False),        "current": 12000.0},
    }


class TestScoringEngine(unittest.TestCase):
    def test_zero_flags_is_neutral(self):
        result = score(_make_indicators({}), CONFIG)
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["status"], "NEUTRAL")

    def test_one_flag_is_neutral(self):
        result = score(_make_indicators({"yield_curve": True}), CONFIG)
        self.assertEqual(result["score"], 1)
        self.assertEqual(result["status"], "NEUTRAL")

    def test_two_flags_is_elevated(self):
        result = score(_make_indicators({"yield_curve": True, "real_yield": True}), CONFIG)
        self.assertEqual(result["score"], 2)
        self.assertEqual(result["status"], "ELEVATED")

    def test_three_flags_is_warning(self):
        result = score(
            _make_indicators({"yield_curve": True, "real_yield": True, "credit_spread": True}),
            CONFIG,
        )
        self.assertEqual(result["score"], 3)
        self.assertEqual(result["status"], "WARNING")

    def test_four_flags_is_critical(self):
        result = score(
            _make_indicators(
                {"yield_curve": True, "real_yield": True, "credit_spread": True, "cftc": True}
            ),
            CONFIG,
        )
        self.assertEqual(result["score"], 4)
        self.assertEqual(result["status"], "CRITICAL")

    def test_errored_indicator_does_not_flag(self):
        indicators = {
            "yield_curve":   {"error": "timeout", "flagged": False},
            "real_yield":    {"flagged": True, "current": 2.5},
            "credit_spread": {"flagged": False, "current": 300.0},
            "cftc":          {"flagged": False, "current": 8000.0},
        }
        result = score(indicators, CONFIG)
        self.assertEqual(result["score"], 1)
        self.assertEqual(result["status"], "NEUTRAL")

    def test_indicators_preserved_in_output(self):
        indicators = _make_indicators({"cftc": True})
        result = score(indicators, CONFIG)
        self.assertIn("indicators", result)
        self.assertEqual(result["indicators"]["cftc"]["flagged"], True)


if __name__ == "__main__":
    unittest.main()
