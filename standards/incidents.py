#!/usr/bin/env python3
"""File, update and close standards incidents from a scorecard (STANDARDS.md §考核 4).

    GH_TOKEN=... python3 standards/incidents.py standards/scorecard.json

For every active registered repository on the card:
  * below the bar  -> open or update ONE issue labelled `standards-incident` + its severity
  * at the bar     -> close any open `standards-incident` issue, with a comment saying why
  * MISSING        -> skipped here (the assessor could not read it, so it cannot file there
                      either); the audit run already fails on MISSING repos

Labels are created if the repository lacks them; an updated incident carries only its
current severity label. Every gh failure is reported as an
error annotation and makes the script exit 1 after all repositories were processed,
so a filing problem is never silent. Filing UNAVAILABLE counts as a failure too:
when the token itself cannot file (a fine-grained PAT without issues access answers
"Resource not accessible by personal access token") or the repository has issues
disabled, the per-repository calls short-circuit after the first denial, the repo is
reported with an error annotation plus a summary line, and the script exits 1 -- a
daily run that files nothing must never report success (issue #17 round-4 P1-1;
this reverses the warn-and-exit-0 behavior of 2026-10-28).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABEL = "standards-incident"
LABEL_COLORS = {LABEL: "B60205", "P0": "B60205", "P1": "D93F0B", "P2": "FBCA04"}
SEVERITIES = ("P0", "P1", "P2")
ALIAS = {"miao-ai": "anomalies-autogpt", "vertciti-prototype": "vertcity-prototype"}
CARD_URL = "https://github.com/HUIIIM/.github/blob/main/standards/SCORECARD.md"


def run_gh(args):
    p = subprocess.run(["gh", *args], capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


UNAVAILABLE_MARKERS = ("Resource not accessible by personal access token", "has disabled issues")


class Filer:
    def __init__(self, gh=run_gh, owner="HUIIIM"):
        self.gh, self.owner, self.errors = gh, owner, []
        self.unavailable: dict[str, str] = {}

    def call(self, repo, args, what):
        if repo in self.unavailable:
            return None
        code, out, err = self.gh([*args, "-R", f"{self.owner}/{repo}"])
        if code != 0:
            detail = err or out or "exit " + str(code)
            if any(marker in detail for marker in UNAVAILABLE_MARKERS):
                self.unavailable[repo] = detail
                print(f"::error::{repo}: filing unavailable ({what}): {detail[:200]}")
                return None
            self.errors.append(f"{repo}: {what} failed: {detail}")
            print(f"::error::{repo}: {what} failed: {detail[:200]}")
            return None
        return out

    def ensure_labels(self, repo, severity):
        for name in (LABEL, severity):
            self.call(repo, ["label", "create", name, "--color", LABEL_COLORS.get(name, "BFD4F2"), "--force"],
                      f"label {name}")

    def open_issue(self, repo):
        """(listed, number): listed is False when the lookup itself failed, so callers never
        mistake "could not list" for "no open incident" and file a duplicate."""
        out = self.call(repo, ["issue", "list", "-l", LABEL, "--state", "open", "--json", "number", "-q", ".[0].number"],
                        "list incidents")
        return (out is not None), (out or None)

    def file(self, repo, row, generated):
        if repo in self.unavailable:
            return "skipped (filing unavailable)"
        self.ensure_labels(repo, row["severity"])
        if repo in self.unavailable:
            return "skipped (filing unavailable)"
        title = f"[standards] {row['severity']}: score {row['score']} ({row['grade']}) below the A++ bar"
        body = (f"Independent assessment (HUIIIM/.github standards/audit.py), {generated}. Failing checks: "
                + ", ".join(row["failing"])
                + (". Unprobed: " + ", ".join(row["unprobed"]) if row["unprobed"] else "")
                + f".\n\nFull card: {CARD_URL}\n"
                "Closed automatically by the first assessment that finds the repo at or above the bar.")
        listed, existing = self.open_issue(repo)
        if not listed:
            return "FAILED to list (not filed, to avoid a duplicate)"
        if existing:
            current = self.call(repo, ["issue", "view", existing, "--json", "labels", "-q", ".labels[].name"],
                                f"read labels of #{existing}") or ""
            stale = [sev for sev in SEVERITIES if sev != row["severity"] and sev in current.split()]
            args = ["issue", "edit", existing, "-t", title, "-b", body, "--add-label", f"{LABEL},{row['severity']}"]
            if stale:
                args += ["--remove-label", ",".join(stale)]
            ok = self.call(repo, args, f"update #{existing}")
            return f"updated #{existing}" if ok is not None else "FAILED to update"
        ok = self.call(repo, ["issue", "create", "-t", title, "-b", body, "-l", f"{LABEL},{row['severity']}"], "create incident")
        return "filed" if ok is not None else "FAILED to file"

    def close(self, repo, row, generated):
        if repo in self.unavailable:
            return "skipped (filing unavailable)"
        listed, existing = self.open_issue(repo)
        if repo in self.unavailable:
            return "skipped (filing unavailable)"
        if not listed:
            return "FAILED to list"
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


def run_failed(filer):
    """The run fails when any incident operation failed OR filing was unavailable
    for any repository: a control that silently did not run is the failure."""
    return bool(filer.errors or filer.unavailable)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    card = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    registry = json.loads((HERE / "repos.json").read_text(encoding="utf-8"))["repos"]
    filer = Filer()
    for name, action in process(card, registry, filer).items():
        print(f"{name}: {action}")
    if filer.unavailable:
        print(f"::error::incident filing unavailable for {len(filer.unavailable)} repo(s) "
              "(token has no issues access, or issues are disabled there): "
              + ", ".join(sorted(filer.unavailable))
              + " -- the filing control did not run for those repos, so this run fails.")
    if filer.errors:
        print(f"{len(filer.errors)} incident operation(s) failed:\n  " + "\n  ".join(filer.errors), file=sys.stderr)
    if run_failed(filer):
        sys.exit(1)


if __name__ == "__main__":
    main()
