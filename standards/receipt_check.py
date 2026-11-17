#!/usr/bin/env python3
"""回执回读闸: a receipt is a claim; this reads every pointer in it back from GitHub.

    GH_TOKEN=... python3 standards/receipt_check.py --repo HUIIIM/.github receipt.md
    ... | python3 standards/receipt_check.py --repo HUIIIM/.github -          # receipt text on stdin
    python3 standards/receipt_check.py --repo HUIIIM/.github --comment 6627677221   # a posted comment
    python3 standards/receipt_check.py --repo HUIIIM/.github --done receipt.md      # 完成回执格式也查

Why it exists: on 2026-11-07 a background process reported a pull-request merge that never
happened, complete with a merge SHA, a comment id and CI counts, and only a manual
read-back caught it (audit 2026-11, issue #150, 样本 B). The rule written afterwards,
"后台回执一律未验证输入", had no mechanism behind it. This is the mechanism: run it on the
receipt before the ledger entry is written, and write the entry only on exit 0.

What it reads back (the receipt's own words are never trusted, only GitHub's answer):

  pr        every pull request the receipt points at exists
  merged    a pull request named on a line that says 合并/合入/merged is in fact merged, and a
            SHA on that line is that pull request's merge commit
  sha       every commit SHA in the receipt exists in the repository
  comment   every #issuecomment-<id> exists, on the issue or pull request the link names

--done additionally enforces the completion receipt of standards/jarvis-task-loop.md
(PR link, merge SHA, new main tip SHA): a merged pull request, its merge SHA quoted, and
at least one further SHA that exists.

Not read back (say so in the ledger rather than assume it): CI counts, prose claims,
anything outside GitHub. A SHA written as digits only is not recognised as a SHA.

Exit codes:

  0  at least one pointer, and every pointer read back as claimed
  1  a pointer was refuted, or the receipt carries no pointer at all, or --done is unmet
  3  a read did not complete: UNKNOWN, which is not a pass
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import traceback
from pathlib import Path

PR_URL_RE = re.compile(r"https://github\.com/([\w.-]+/[\w.-]+)/pull/(\d+)")
ISSUE_URL_RE = re.compile(r"https://github\.com/([\w.-]+/[\w.-]+)/(?:pull|issues)/(\d+)#issuecomment-(\d+)")
BARE_COMMENT_RE = re.compile(r"(?<![\w/])#issuecomment-(\d+)")
BARE_PR_RE = re.compile(r"\bPR\s*#(\d+)")
SHA_RE = re.compile(r"(?<![\w/#-])[0-9a-f]{7,40}(?![\w-])")
MERGE_WORD_RE = re.compile(r"(合并|合入|已并入|merged|merge\s+sha)", re.IGNORECASE)
OK, BAD, UNKNOWN = "VERIFIED", "REFUTED", "UNKNOWN"


def run_gh(args):
    try:
        p = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return 124, "", "timeout after 60s"
    return p.returncode, p.stdout, p.stderr.strip()


class Reader:
    def __init__(self, gh=run_gh):
        self.gh, self.cache = gh, {}

    def get(self, path):
        """(status, document): status is 'ok', 'missing' (404) or 'error' (anything else)."""
        if path not in self.cache:
            code, out, err = self.gh(["api", path])
            if code == 0:
                try:
                    self.cache[path] = ("ok", json.loads(out))
                except json.JSONDecodeError:
                    self.cache[path] = ("error", "unparseable answer")
            elif "HTTP 404" in err or "HTTP 422" in err:
                self.cache[path] = ("missing", None)
            else:
                self.cache[path] = ("error", err[:160] or f"exit {code}")
        return self.cache[path]


def is_sha(token):
    return not token.isdigit()


def extract(text, repo):
    """Pointers in the receipt: PRs, comments and SHAs, plus the per-line merge claims."""
    prs, comments, shas, merges = {}, {}, [], []
    for line in text.splitlines():
        line_prs = [(r, int(n)) for r, n in PR_URL_RE.findall(line)]
        line_prs += [(repo, int(n)) for n in BARE_PR_RE.findall(line)]
        for r, n, cid in ISSUE_URL_RE.findall(line):
            comments[(r, int(cid))] = int(n)
        scrubbed = ISSUE_URL_RE.sub(" ", line)
        for cid in BARE_COMMENT_RE.findall(scrubbed):
            comments.setdefault((repo, int(cid)), None)
        line_shas = [s for s in SHA_RE.findall(PR_URL_RE.sub(" ", scrubbed)) if is_sha(s)]
        for key in line_prs:
            prs[key] = True
        for s in line_shas:
            if s not in shas:
                shas.append(s)
        if MERGE_WORD_RE.search(line) and line_prs:
            merges.append((line_prs, line_shas))
    return list(prs), comments, shas, merges


def check(text, repo, reader, done=False):
    """Returns (rows, verdict). A row is (kind, pointer, result, evidence)."""
    prs, comments, shas, merges = extract(text, repo)
    rows, pulls = [], {}

    for r, n in prs:
        status, doc = reader.get(f"repos/{r}/pulls/{n}")
        pulls[(r, n)] = doc if status == "ok" else None
        if status == "ok":
            state = "merged" if doc.get("merged") else doc.get("state", "?")
            rows.append(("pr", f"{r}#{n}", OK, f"exists, {state}"))
        else:
            rows.append(("pr", f"{r}#{n}", BAD if status == "missing" else UNKNOWN,
                         "no such pull request" if status == "missing" else doc))

    merge_shas = set()
    for line_prs, line_shas in merges:
        for key in line_prs:
            doc = pulls.get(key)
            if doc is None:
                continue  # already reported as a pr row
            name = f"{key[0]}#{key[1]}"
            if not doc.get("merged"):
                rows.append(("merged", name, BAD, f"receipt says merged; GitHub says {doc.get('state', '?')}, merged=false"))
                continue
            actual = doc.get("merge_commit_sha") or ""
            claimed = [s for s in line_shas if actual.startswith(s)]
            merge_shas.update(claimed)
            if line_shas and not claimed and len(line_prs) == 1:
                rows.append(("merged", name, BAD, f"merged, but as {actual[:10]}, not {'/'.join(s[:10] for s in line_shas)}"))
            else:
                rows.append(("merged", name, OK, f"merged as {actual[:10]}"))

    for s in shas:
        status, doc = reader.get(f"repos/{repo}/commits/{s}")
        rows.append(("sha", s[:12], OK if status == "ok" else BAD if status == "missing" else UNKNOWN,
                     "commit exists" if status == "ok" else f"no such commit in {repo}" if status == "missing" else doc))

    for (r, cid), number in comments.items():
        status, doc = reader.get(f"repos/{r}/issues/comments/{cid}")
        if status != "ok":
            rows.append(("comment", f"{r} comment {cid}", BAD if status == "missing" else UNKNOWN,
                         "no such comment" if status == "missing" else doc))
        elif number is not None and not doc.get("issue_url", "").endswith(f"/{number}"):
            rows.append(("comment", f"{r} comment {cid}", BAD, f"exists, but not on #{number}"))
        else:
            rows.append(("comment", f"{r} comment {cid}", OK, "exists" + (f" on #{number}" if number is not None else "")))

    if not rows:
        rows.append(("pointers", "-", BAD, "回执不含任何可回读指针（PR／SHA／评论），不得落账"))
    if done:
        merged = [k for k, d in pulls.items() if d and d.get("merged")]
        if not merged:
            rows.append(("done", "PR 链接", BAD, "完成回执须指向一个已合并的 PR"))
        elif not merge_shas:
            rows.append(("done", "合并 SHA", BAD, "完成回执须在写明合并的那一行给出该 PR 的合并 SHA"))
        elif len([s for s in shas if s not in merge_shas]) < 1:
            rows.append(("done", "main 顶端 SHA", BAD, "完成回执须另给新的 main 顶端 SHA"))
        else:
            rows.append(("done", "格式", OK, "PR 链接、合并 SHA、main 顶端 SHA 三件齐"))

    results = {r[2] for r in rows}
    verdict = BAD if BAD in results else UNKNOWN if UNKNOWN in results else OK
    return rows, verdict


def to_markdown(rows, verdict):
    head = {OK: "回读通过：可以落账", BAD: "回读不通过：不得落账", UNKNOWN: "回读未完成（UNKNOWN）：不得落账，重跑"}[verdict]
    lines = [f"**{head}**", "", "| 类 | 指针 | 回读结果 | GitHub 实况 |", "|---|---|---|---|"]
    lines += [f"| {k} | `{p}` | {r} | {e} |" for k, p, r, e in rows]
    lines += ["", "未机核面：CI 计数、文字性结论、GitHub 以外的指针。"]
    return "\n".join(lines) + "\n"


def main(argv=None, gh=run_gh):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "-h" in argv or "--help" in argv or "--repo" not in argv:
        print(__doc__)
        return 0 if ("-h" in argv or "--help" in argv) else 1
    repo = argv[argv.index("--repo") + 1]
    reader = Reader(gh)
    try:
        if "--comment" in argv:
            status, doc = reader.get(f"repos/{repo}/issues/comments/{argv[argv.index('--comment') + 1]}")
            if status != "ok":
                print(f"::error::cannot read the comment ({status}); UNKNOWN is not a pass", file=sys.stderr)
                return 3
            text = doc.get("body") or ""
        else:
            src = argv[-1]
            text = sys.stdin.read() if src == "-" else Path(src).read_text(encoding="utf-8")
        rows, verdict = check(text, repo, reader, done="--done" in argv)
    except Exception:  # noqa: BLE001 - a crash is UNKNOWN (exit 3), never "refuted" and never a pass
        traceback.print_exc()
        return 3
    print(to_markdown(rows, verdict), end="")
    return {OK: 0, BAD: 1, UNKNOWN: 3}[verdict]


if __name__ == "__main__":
    sys.exit(main())
