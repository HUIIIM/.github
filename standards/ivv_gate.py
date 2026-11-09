#!/usr/bin/env python3
"""IVV merge gate: turn the independent verdict into a commit status (issue #84, SOTA VER-3).

    python3 standards/ivv_gate.py <owner/repo> <pr-number>             # in CI; needs GITHUB_TOKEN
    python3 standards/ivv_gate.py <owner/repo> <pr-number> --dry-run   # print the status, post nothing

Sets the commit status `ivv/verdict` on the PR's current head:

- success  -- the PR is outside IVV scope (not Claude-authored), or trusted verdicts for the
              current head exist, the newest reads PASS or N/A, and no FAIL for this head stands;
- failure  -- a trusted FAIL for the current head stands. A FAIL is sticky: a later PASS does
              not clear it unless it explicitly names the FAIL comment it replaces
              ("取代：<comment id>" / "Supersedes: <comment id>"), so a FAIL can never be
              overwritten silently. Pushing a new head starts coverage afresh;
- pending  -- no trusted verdict exists for the current head yet (a new push resets coverage:
              LOOP.md "a new head voids coverage").

A verdict counts only when it (1) uses the IVV.md header for the *current* head
("### 独立评估 · SOTA v1.0 · <sha7>"), (2) was posted after the head commit, and (3) comes from
an OWNER / MEMBER / COLLABORATOR, or from the Claude GitHub App itself (login `claude[bot]`,
type Bot: its comments carry author_association NONE). A drive-by commenter cannot post a
verdict. The verdict word may carry Markdown emphasis ("判定：**FAIL**"). Scope follows IVV.md
v1.3: a PR is in scope when any commit is authored or committed by Claude (noreply@anthropic.com,
or the Claude App's `claude[bot]` identity) or the PR was opened by the Claude GitHub App.

Known limit (stated in #84): verdicts are posted under the same login that merges, so this gate
cannot tell the assessor from the author by identity. It enforces "a current-head verdict exists
and no FAIL for it stands", which closes the merged-after-FAIL and merged-without-verdict paths
seen in #40; an explicit supersession is visible in the PR thread and reviewable.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request

CONTEXT = "ivv/verdict"
CLAUDE_EMAIL = "noreply@anthropic.com"
CLAUDE_APP_LOGINS = {"claude[bot]", "claude"}
CLAUDE_BOT_EMAIL_SUFFIX = "+claude[bot]@users.noreply.github.com"
TRUSTED = {"OWNER", "MEMBER", "COLLABORATOR"}
TRUSTED_BOTS = {"claude[bot]"}
HEADER = re.compile(r"^\s*###\s*独立评估\s*·\s*SOTA\s*v[\d.]+\s*·\s*([0-9a-f]{7,40})\s*$", re.MULTILINE)
VERDICT = re.compile(r"判定\s*[：:]\s*[*_]*\s*(PASS|FAIL|N/A)")
SUPERSEDES = re.compile(r"(?:取代|Supersedes)\s*[：:]?\s*(?:#issuecomment-)?(\d+)", re.IGNORECASE)


def _is_claude(email: str) -> bool:
    email = (email or "").lower()
    return email == CLAUDE_EMAIL or email.endswith(CLAUDE_BOT_EMAIL_SUFFIX)


def trusted(c: dict) -> bool:
    """A verdict author the gate believes: repo insiders, or the Claude GitHub App itself."""
    if c.get("author_association") in TRUSTED:
        return True
    user = c.get("user") or {}
    return user.get("login", "").lower() in TRUSTED_BOTS and user.get("type") == "Bot"


def in_scope(pr: dict, commits: list[dict]) -> bool:
    if (pr.get("user") or {}).get("login", "").lower() in CLAUDE_APP_LOGINS:
        return True
    for c in commits:
        if any((c.get(k) or {}).get("login", "").lower() in TRUSTED_BOTS for k in ("author", "committer")):
            return True
        meta = c.get("commit", {})
        if any(_is_claude((meta.get(k) or {}).get("email", "")) for k in ("author", "committer")):
            return True
    return False


def parse_verdict(body: str, head_sha: str) -> str | None:
    """The verdict in an IVV-format comment for this head, or None."""
    m = HEADER.search(body or "")
    if not m or not head_sha.startswith(m.group(1)):
        return None
    v = VERDICT.search(body[m.end():])
    return v.group(1) if v else None


def evaluate(pr: dict, commits: list[dict], comments: list[dict]) -> tuple[str, str]:
    head = pr["head"]["sha"]
    sha7 = head[:7]
    if not in_scope(pr, commits):
        return "success", "Not Claude-authored: outside IVV scope"
    head_time = (commits[-1]["commit"]["committer"]["date"] if commits else "") or ""
    verdicts = []  # (created_at, comment id, verdict, ids it supersedes)
    for c in comments:
        if not trusted(c):
            continue
        if head_time and c.get("created_at", "") < head_time:
            continue  # posted before the current head existed: it judged an older diff
        v = parse_verdict(c.get("body", ""), head)
        if v:
            verdicts.append((c.get("created_at", ""), str(c.get("id", "")), v,
                             set(SUPERSEDES.findall(c.get("body", "")))))
    if not verdicts:
        return "pending", f"Awaiting an independent verdict for {sha7} (IVV.md)"
    verdicts.sort(key=lambda t: t[0])
    standing_fails = []
    for i, (at, cid, v, _) in enumerate(verdicts):
        if v != "FAIL":
            continue
        later = verdicts[i + 1:]
        if not any(cid and cid in sup for (_, _, _, sup) in later):
            standing_fails.append(cid or at)
    if standing_fails:
        return "failure", f"Independent verdict for {sha7}: FAIL stands (comment {standing_fails[-1]})"
    return "success", f"Independent verdict for {sha7}: {verdicts[-1][2]}"

def _api(method: str, url: str, token: str, body: dict | None = None):
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
               "User-Agent": "huiiim-ivv-gate"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body else None, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or b"null")


def _paged(url: str, token: str) -> list:
    out, page = [], 1
    while True:
        batch = _api("GET", f"{url}{'&' if '?' in url else '?'}per_page=100&page={page}", token)
        out += batch
        if len(batch) < 100:
            return out
        page += 1


def main(argv: list[str]) -> int:
    dry = "--dry-run" in argv
    args = [a for a in argv if a != "--dry-run"]
    if len(args) != 2:
        sys.exit(__doc__)
    repo, number = args[0], int(args[1])
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token and not dry:
        sys.exit("GITHUB_TOKEN is required to post the status (use --dry-run to only print it)")
    base = f"https://api.github.com/repos/{repo}"
    pr = _api("GET", f"{base}/pulls/{number}", token)
    commits = _paged(f"{base}/pulls/{number}/commits", token)
    comments = _paged(f"{base}/issues/{number}/comments", token)
    state, desc = evaluate(pr, commits, comments)
    if dry:
        print(f"[dry-run] {repo}#{number} @ {pr['head']['sha'][:7]}: {CONTEXT} would be {state} ({desc})")
        return 0
    _api("POST", f"{base}/statuses/{pr['head']['sha']}", token, {
        "state": state, "context": CONTEXT, "description": desc[:140],
        "target_url": f"https://github.com/{repo}/pull/{number}"})
    print(f"{repo}#{number} @ {pr['head']['sha'][:7]}: {CONTEXT} = {state} ({desc})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
