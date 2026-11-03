#!/usr/bin/env python3
"""Run the assessor and publish its card only if the run produced one (standards-audit Assess step).

    python3 standards/publish_card.py /tmp/portfolio --live

standards/scorecard.json and standards/SCORECARD.md are tracked, so a crashed audit must not
leave the previous card in place for every later step (standing card PR, incident filing, the
MISSING check) to read as today's. The audit writes to a scratch directory first; the card is
copied into standards/ only when both outputs are real: the JSON parses with a `repos` list and
the Markdown is non-empty. The audit's own exit code must be 0, 1 (a MUST failing) or 2 (repos
MISSING); anything else is a crash. Exit 0 = card published, 1 = nothing published.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRADED_EXITS = (0, 1, 2)


def run_audit(args, json_out, md_out):
    """Default runner: audit.py with --json/--md into the scratch files; returns its exit code."""
    with open(md_out, "w", encoding="utf-8") as md:
        return subprocess.run([sys.executable, str(HERE / "audit.py"), *args, "--json", str(json_out), "--md"],
                              stdout=md, check=False).returncode


def publish(args, dest=HERE, runner=run_audit):
    """(published, message). dest holds scorecard.json and SCORECARD.md and is untouched on failure."""
    with tempfile.TemporaryDirectory() as tmp:
        card_json, card_md = Path(tmp) / "card.json", Path(tmp) / "card.md"
        code = runner(args, card_json, card_md)
        if code not in GRADED_EXITS:
            return False, f"audit.py exited {code} (expected 0, 1 or 2): crashed; previous card kept"
        try:
            card = json.loads(card_json.read_text(encoding="utf-8"))
            if not isinstance(card.get("repos"), list):
                raise ValueError("no repos list")
        except (OSError, ValueError) as exc:
            return False, f"audit.py produced no readable scorecard ({exc}); previous card kept"
        if not card_md.read_text(encoding="utf-8").strip():
            return False, "audit.py produced an empty SCORECARD.md; previous card kept"
        shutil.copyfile(card_json, Path(dest) / "scorecard.json")
        shutil.copyfile(card_md, Path(dest) / "SCORECARD.md")
        return True, (f"card published ({len(card['repos'])} repos; audit exit {code}: "
                      "2 = repos MISSING, 1 = at least one MUST failing)")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    ok, msg = publish(sys.argv[1:])
    print(msg if ok else f"::error::{msg}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
