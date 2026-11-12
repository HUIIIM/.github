#!/usr/bin/env python3
"""Freshness SLO for the published scorecard (STANDARDS.md §考核 6, issue #85).

    python3 standards/card_freshness.py                    # check standards/scorecard.json, 36 h budget
    python3 standards/card_freshness.py --max-age-hours 36 --card path/to/scorecard.json

The card is "graded daily", but it reaches main only through the standing
standards/daily-card PR. If that PR is not approved and merged, main's card,
the profile grading line and the website copy go stale with no failed run to
say so. This check fails (exit 1, a GitHub ::error) when the card on main is
older than the budget, so a stale card is an alert, not a silent drift.

Exit codes: 0 fresh, 1 stale, 2 card unreadable (a missing or malformed card
is never "fresh").
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_CARD = HERE / "scorecard.json"
DEFAULT_MAX_AGE_H = 36.0
STANDING_BRANCH = "standards/daily-card"


def parse_generated(value: str) -> dt.datetime:
    """audit.py writes e.g. '2026-11-02 11:41Z' (UTC, minute precision)."""
    return dt.datetime.strptime(value, "%Y-%m-%d %H:%MZ").replace(tzinfo=dt.UTC)


def check(card: dict, now: dt.datetime, max_age_h: float) -> tuple[bool, str]:
    generated = parse_generated(card["generated"])
    age_h = (now - generated).total_seconds() / 3600
    if age_h < 0:
        return False, f"card generated {card['generated']} is in the future ({-age_h:.1f} h ahead of {now:%Y-%m-%d %H:%MZ})"
    verdict = "fresh" if age_h <= max_age_h else "STALE"
    return age_h <= max_age_h, f"card generated {card['generated']}, {age_h:.1f} h old (budget {max_age_h:g} h): {verdict}"


def main(argv: list[str]) -> int:
    card_path = Path(argv[argv.index("--card") + 1]) if "--card" in argv else DEFAULT_CARD
    max_age_h = float(argv[argv.index("--max-age-hours") + 1]) if "--max-age-hours" in argv else DEFAULT_MAX_AGE_H
    try:
        card = json.loads(card_path.read_text(encoding="utf-8"))
        ok, msg = check(card, dt.datetime.now(dt.UTC), max_age_h)
    except (OSError, ValueError, KeyError) as exc:
        print(f"::error::scorecard unreadable ({card_path}): {exc}")
        return 2
    if ok:
        print(msg)
        return 0
    print(f"::error::Published scorecard is stale: {msg}. The daily card reaches main through the standing "
          f"'{STANDING_BRANCH}' PR; approve its run and merge it, or find why standards-audit stopped producing it.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
