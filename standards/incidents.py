#!/usr/bin/env python3
"""File, update and close standards incidents from a scorecard (STANDARDS.md §考核 4).

    GH_TOKEN=... python3 standards/incidents.py standards/scorecard.json

For every active registered repository on the card:
  * below the bar  -> open or update ONE issue labelled `standards-incident` + its severity
  * at the bar     -> close any open `standards-incident` issue, with a comment saying why
  * MISSING        -> skipped here (the assessor could not read it, so it cannot file there
                      either); the audit run already fails on MISSING repos

Labels are created if the repository lacks them. Every gh failure is reported as an
error annotation and makes the script exit 1 after all repositories were processed,
so a filing problem is never silent.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABEL = "standards-incident"
LABEL_COLORS = {LABEL: "B60205", "P0": "B60205", "P1": "D93F0B", "P2": "FBCA04"}
ALIAS = {"miao-ai": "anomalies-autogpt", "vertciti-prototype": "vertcity-prototype"}
CARD_URL = "https://github.com/HUIIIM/.github/blob/main/standards/SCORECARD.md"


def run_gh(args):
    p = subprocess.run(["gh", *args], capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


class Filer:
    def __init__(self, gh=run_gh, owner="HUIIIM"):
        self.gh, self.owner, self.errors = gh, owner, []

    def call(self, repo, args, what):
        code, out, err = self.gh([*args, "-R", f"{self.owner}/{repo}"])
        if code != 0:
            self.errors.append(f"{repo}: {what} failed: {err or out or 'exit ' + str(code)}")
            print(f"::error::{repo}: {what} failed: {(err or out)[:200]}")
            return None
        return out

    def ensure_labels(self, repo, severity):
        for name in (LABEL, severity):
            self.call(repo, ["label", "create", name, "--color", LABEL_COLORS.get(name, "BFD4F2"), "--force"],
                      f"label {name}")

    def open_issue(self, repo):
        out = self.call(repo, ["issue", "list", "-l", LABEL, "--state", "open", "--json", "number", "-q", ".[0].number"],
                        "list incidents")
        return out or None

    def file(self, repo, row, generated):
        self.ensure_labels(repo, row["severity"])
        title = f"[standards] {row['severity']}: score {row['score']} ({row['grade']}) below the A++ bar"
        body = (f"Independent assessment (HUIIIM/.github standards/audit.py), {generated}. Failing checks: "
                + ", ".join(row["failing"])
                + (". Unprobed: " + ", ".join(row["unprobed"]) if row["unprobed"] else "")
                + f".\n\nFull card: {CARD_URL}\n"
                "Closed automatically by the first assessment that finds the repo at or above the bar.")
        existing = self.open_issue(repo)
        if existing:
            ok = self.call(repo, ["issue", "edit", existing, "-t", title, "-b", body,
                                  "--add-label", f"{LABEL},{row['severity']}"], f"update #{existing}")
            return f"updated #{existing}" if ok is not None else "FAILED to update"
        ok = self.call(repo, ["issue", "create", "-t", title, "-b", body, "-l", f"{LABEL},{row['severity']}"], "create incident")
        return "filed" if ok is not None else "FAILED to file"

    def close(self, repo, row, generated):
        existing = self.open_issue(repo)
        if not existing:
            return "clean"
        ok = self.call(repo, ["issue", "close", existing, "-r", "completed", "-c",
                              f"Closed by the independent assessment of {generated}: score {row['score']} ({row['grade']}), "
                              f"at or above the A++ bar with no failing MUST. Card: {CARD_URL}"], f"close #{existing}")
        return f"closed #{existing}" if ok is not None else "FAILED to close"


def process(card, registry, filer):
    actions = {}
    for row in card["repos"]:
        name = row["repo"]
        if registry.get(name, {}).get("status") != "active":
            continue
        repo = ALIAS.get(name, name)
        if row.get("missing"):
            actions[name] = "skipped (MISSING)"
        elif row["meets_bar"]:
            actions[name] = filer.close(repo, row, card["generated"])
        else:
            actions[name] = filer.file(repo, row, card["generated"])
    return actions


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    card = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    registry = json.loads((HERE / "repos.json").read_text(encoding="utf-8"))["repos"]
    filer = Filer()
    for name, action in process(card, registry, filer).items():
        print(f"{name}: {action}")
    if filer.errors:
        print(f"{len(filer.errors)} incident operation(s) failed:\n  " + "\n  ".join(filer.errors), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
