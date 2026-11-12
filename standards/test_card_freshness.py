"""Tests for standards/card_freshness.py (issue #85).

    python3 -m unittest standards/test_card_freshness.py
"""
import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import card_freshness as cf

NOW = dt.datetime(2026, 11, 3, 6, 0, tzinfo=dt.UTC)


class Check(unittest.TestCase):
    def test_fresh_within_budget(self):
        ok, msg = cf.check({"generated": "2026-11-02 11:41Z"}, NOW, 36)
        self.assertTrue(ok, msg)
        self.assertIn("18.3 h old", msg)

    def test_stale_past_budget(self):
        ok, msg = cf.check({"generated": "2026-11-01 10:48Z"}, NOW, 36)
        self.assertFalse(ok)
        self.assertIn("STALE", msg)

    def test_exactly_at_budget_is_fresh(self):
        ok, _ = cf.check({"generated": "2026-11-01 18:00Z"}, NOW, 36)
        self.assertTrue(ok)

    def test_future_timestamp_is_not_fresh(self):
        ok, msg = cf.check({"generated": "2026-11-04 00:00Z"}, NOW, 36)
        self.assertFalse(ok)
        self.assertIn("future", msg)


class Main(unittest.TestCase):
    def run_main(self, text):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "scorecard.json"
            if text is not None:
                p.write_text(text, encoding="utf-8")
            return cf.main(["--card", str(p)])

    def test_missing_card_is_unreadable_not_fresh(self):
        self.assertEqual(self.run_main(None), 2)

    def test_malformed_timestamp_is_unreadable(self):
        self.assertEqual(self.run_main(json.dumps({"generated": "yesterday"})), 2)

    def test_no_generated_key_is_unreadable(self):
        self.assertEqual(self.run_main(json.dumps({"repos": []})), 2)

    def test_old_card_fails(self):
        self.assertEqual(self.run_main(json.dumps({"generated": "2020-01-01 00:00Z"})), 1)

    def test_current_card_passes(self):
        now = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%MZ")
        self.assertEqual(self.run_main(json.dumps({"generated": now})), 0)


if __name__ == "__main__":
    unittest.main()
