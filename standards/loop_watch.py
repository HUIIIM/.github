#!/usr/bin/env python3
"""闭环末态巡检（GitHub 面）: find the loops that were opened and never closed.

    GH_TOKEN=... python3 standards/loop_watch.py                # roll-call (markdown) on stdout
    GH_TOKEN=... python3 standards/loop_watch.py --json out.json
    GH_TOKEN=... python3 standards/loop_watch.py --deep         # also read every open PR: verdicts, dispatches
    GH_TOKEN=... python3 standards/loop_watch.py --file         # keep ONE roll-call issue in this repo current

GitHub is the shared bus of the jarvis-task loop (standards/jarvis-task-loop.md), so the
END STATE of dispatched work is readable there by a machine. This patrol reads that end
state, not the liveness of whoever was supposed to do the work: an account that is alive
and a queue that has not moved for eight days are different facts (audit 2026-11, issue #150).

What it names (thresholds and their written sources live in standards/loop_sla.json):

  NO_STATE              a jarvis-task issue that does not carry exactly one state label
  STALE_STATE           a jarvis-task issue idle in its state longer than that state allows
  RULING_OVERDUE        a 「待中枢裁」 issue still open past the ruling window
  ADVICE_NO_RECEIPT     a claude-advice issue with no reply at all past the receipt window
  SINGLETON_DUP         more than one open issue with the same 「[独立评估] …」 title in a repo
  PR_STALE              an open pull request nobody has touched (ready / draft / dependabot windows)
  --deep only:
  VERDICT_NOT_EXECUTED  an open PR whose CURRENT head already carries a PASS verdict
  DISPATCH_NOT_CLOSED   a 派发/判定 issue whose pull request is already judged, merged or closed

Fail-loud, like the standards audit: a query that fails, times out or comes back
incomplete is never read as "nothing found". Exit codes:

  0  every query completed and nothing is overdue
  1  every query completed and at least one loop is overdue
  2  a registered active repository could not be read (coverage gap; findings still printed)
  3  a query failed or returned incomplete results: the result is UNKNOWN, not clean

Read-only except --file, which creates/updates/closes one issue labelled `loop-watch` in
this repository. Titles are never printed: this repository is public and half the fleet
is not, so a row is `owner/repo#N` plus ages. Search-API only unless --deep.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import subprocess
import sys
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
OWNER = "HUIIIM"
HOME_REPO = ".github"
WATCH_LABEL = "loop-watch"
WATCH_TITLE = "[闭环巡检] 末态点名 · GitHub 面"
STATE_PREFIX = "jarvis-task:"
RULING_MARK = "待中枢裁"
IVV_MARK = "[独立评估]"
LIST_CAP = 12  # rows shown per rule in markdown; the JSON always carries every finding
SEARCH_PAUSE = 2.1  # seconds between search calls: the search API allows 30 requests a minute
DISPATCH_RE = re.compile(r"(派发|判定|复评)")
PR_REF_RE = re.compile(r"PR\s*#(\d+)")
VERDICT_PASS_RE = re.compile(r"(判定[:：]\s*\**\s*PASS|verdict\s*[—:\-–]+\s*\**\s*PASS|→\s*PASS)", re.IGNORECASE)
VERDICT_FAIL_RE = re.compile(r"(判定[:：]\s*\**\s*FAIL|verdict\s*[—:\-–]+\s*\**\s*FAIL|→\s*FAIL)", re.IGNORECASE)

RULES = {
    "NO_STATE": "jarvis-task 没有恰好一个状态标签（状态机没在跑）",
    "STALE_STATE": "jarvis-task 在当前状态超时未动",
    "RULING_OVERDUE": "「待中枢裁」超过裁决时限仍未关单",
    "ADVICE_NO_RECEIPT": "claude-advice 超时无任何处置回执",
    "SINGLETON_DUP": "「[独立评估]」唯一 issue 出现重复",
    "PR_STALE": "PR 超时无人触碰",
    "VERDICT_NOT_EXECUTED": "当前 head 已有 PASS 判定，PR 仍未合并（判了没人执行）",
    "DISPATCH_NOT_CLOSED": "判定/派发单所指 PR 已判定或已关，派发单未销",
}


class QueryError(RuntimeError):
    """A read that did not complete. The patrol result is then UNKNOWN, never clean."""


class Unreadable(QueryError):
    """A repository the token cannot see (the coverage gap is reported, not swallowed)."""


class NotFound(QueryError):
    """A pointer that resolves to nothing (a dispatch naming a PR that does not exist)."""


def run_gh(args):
    try:
        p = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return 124, "", "timeout after 120s"
    return p.returncode, p.stdout, p.stderr.strip()


def parse_ts(ts):
    return dt.datetime.fromisoformat(ts)


def hours(now, ts):
    return (now - parse_ts(ts)).total_seconds() / 3600


def decode_pages(text):
    """`gh api --paginate` prints one JSON document per page, back to back."""
    dec, pos, pages = json.JSONDecoder(), 0, []
    while pos < len(text):
        while pos < len(text) and text[pos].isspace():
            pos += 1
        if pos >= len(text):
            break
        doc, pos = dec.raw_decode(text, pos)
        pages.append(doc)
    return pages


class Bus:
    """The GitHub reads the patrol needs, behind one injectable `gh` runner."""

    def __init__(self, gh=run_gh, owner=OWNER, pause=SEARCH_PAUSE, sleep=time.sleep):
        self.gh, self.owner, self.pause, self.sleep, self.calls = gh, owner, pause, sleep, 0

    def _api(self, path, fields=(), paginate=True):
        args = ["api", "-X", "GET", path]
        for k, v in fields:
            args += ["-f", f"{k}={v}"]
        if paginate:
            args.append("--paginate")
        code, out, err = self.gh(args)
        self.calls += 1
        return code, out, err

    def search(self, query):
        """Every open item matching `query`, or QueryError. Never a partial list."""
        if self.calls and self.pause:
            self.sleep(self.pause)
        code, out, err = self._api("search/issues", (("q", query), ("per_page", "100")))
        if code != 0:
            if "cannot be searched" in err or "HTTP 422" in err:
                raise Unreadable(err[:200])
            raise QueryError(f"search failed ({query!r}): {err[:200] or 'exit ' + str(code)}")
        try:
            pages = decode_pages(out)
        except json.JSONDecodeError as e:
            raise QueryError(f"search returned unparseable output ({query!r}): {e}") from e
        if not pages:
            raise QueryError(f"search returned no document ({query!r})")
        items = [it for page in pages for it in page.get("items", [])]
        total = pages[0].get("total_count", 0)
        if any(page.get("incomplete_results") for page in pages) or len(items) < total:
            raise QueryError(f"search incomplete ({query!r}): got {len(items)} of {total}")
        return [self._row(it) for it in items]

    @staticmethod
    def _row(it):
        return {"repo": it["repository_url"].rsplit("/", 1)[-1], "number": it["number"], "title": it["title"],
                "user": (it.get("user") or {}).get("login", ""), "labels": [lab["name"] for lab in it.get("labels", [])],
                "comments": it.get("comments", 0), "created_at": it["created_at"], "updated_at": it["updated_at"],
                "draft": bool(it.get("draft")), "is_pr": "pull_request" in it}

    def readable(self, repo):
        try:
            self.search(f"repo:{self.owner}/{repo} is:issue is:open")
        except Unreadable:
            return False
        return True

    def get(self, path, paginate=False):
        code, out, err = self._api(path, paginate=paginate)
        if code != 0:
            if "HTTP 404" in err:
                raise NotFound(f"not found ({path})")
            raise QueryError(f"read failed ({path}): {err[:200] or 'exit ' + str(code)}")
        try:
            pages = decode_pages(out)
        except json.JSONDecodeError as e:
            raise QueryError(f"unparseable output ({path}): {e}") from e
        if not paginate:
            return pages[0] if pages else None
        return [row for page in pages for row in (page if isinstance(page, list) else [page])]

    def pull(self, repo, number):
        return self.get(f"repos/{self.owner}/{repo}/pulls/{number}")

    def comments(self, repo, number):
        return self.get(f"repos/{self.owner}/{repo}/issues/{number}/comments?per_page=100", paginate=True)


def finding(rule, row, now, detail=""):
    return {"rule": rule, "repo": row["repo"], "number": row["number"], "is_pr": row.get("is_pr", False),
            "age_h": round(hours(now, row["created_at"])), "idle_h": round(hours(now, row["updated_at"])),
            "detail": detail}


def state_labels(row):
    return sorted(lab for lab in row["labels"] if lab.startswith(STATE_PREFIX))


def check_tasks(rows, sla, now):
    out = []
    for r in rows:
        states = state_labels(r)
        if len(states) != 1:
            out.append(finding("NO_STATE", r, now, "无状态标签" if not states else "多个状态标签：" + "、".join(states)))
            continue
        state = states[0][len(STATE_PREFIX):]
        limit = sla["state_idle_h"].get(state)
        if limit is not None and hours(now, r["updated_at"]) > limit:
            out.append(finding("STALE_STATE", r, now, f"{state} 已闲置超过 {limit}h"))
    return out


def check_rulings(rows, sla, now):
    out = []
    for r in rows:
        if RULING_MARK not in r["title"]:
            continue  # the search also matches bodies that merely mention the phrase
        if hours(now, r["created_at"]) > sla["ruling_h"]:
            out.append(finding("RULING_OVERDUE", r, now,
                               "无任何回执" if r["comments"] == 0 else f"有 {r['comments']} 条评论但未关单（未裁，或裁了没销）"))
    return out


def check_advice(rows, sla, now):
    return [finding("ADVICE_NO_RECEIPT", r, now, "0 条评论")
            for r in rows if r["comments"] == 0 and hours(now, r["created_at"]) > sla["advice_receipt_h"]]


def check_singletons(rows, now):
    seen, out = {}, []
    for r in rows:
        if r["title"].startswith(IVV_MARK):
            seen.setdefault((r["repo"], r["title"]), []).append(r)
    for group in seen.values():
        if len(group) > 1:
            numbers = "、".join(f"#{g['number']}" for g in sorted(group, key=lambda g: g["number"]))
            newest = max(group, key=lambda g: g["number"])
            out.append(finding("SINGLETON_DUP", newest, now, f"同标题在开 {len(group)} 件：{numbers}"))
    return out


def pr_kind(row):
    if row["user"] == "dependabot[bot]":
        return "dependabot"
    return "draft" if row["draft"] else "ready"


def check_prs(rows, sla, now):
    out = []
    for r in rows:
        kind = pr_kind(r)
        limit = sla["pr_idle_h"][kind]
        if hours(now, r["updated_at"]) > limit:
            out.append(finding("PR_STALE", r, now, f"{kind} 已闲置超过 {limit}h"))
    return out


def verdict_on_head(comments, head_sha):
    """(verdict, created_at) of the newest verdict comment bound to `head_sha`, else (None, None)."""
    for c in sorted(comments, key=lambda c: c["created_at"], reverse=True):
        body = c.get("body") or ""
        if head_sha[:7] not in body:
            continue
        if VERDICT_FAIL_RE.search(body):
            return "FAIL", c["created_at"]
        if VERDICT_PASS_RE.search(body):
            return "PASS", c["created_at"]
    return None, None


def check_deep(bus, prs, tasks, sla, now):
    out, judged = [], {}
    for r in prs:
        if pr_kind(r) == "dependabot":
            continue
        head = bus.pull(r["repo"], r["number"])["head"]["sha"]
        verdict, at = verdict_on_head(bus.comments(r["repo"], r["number"]), head)
        judged[(r["repo"], r["number"])] = verdict
        if verdict == "PASS" and hours(now, at) > sla["verdict_execute_h"]:
            out.append(finding("VERDICT_NOT_EXECUTED", r, now,
                               f"head {head[:7]} 的 PASS 判定已 {round(hours(now, at))}h 未执行"))
    open_prs = {(r["repo"], r["number"]) for r in prs}
    for t in tasks:
        m = PR_REF_RE.search(t["title"])
        if not (m and DISPATCH_RE.search(t["title"])):
            continue
        key = (t["repo"], int(m.group(1)))
        if key not in open_prs:
            try:
                state = bus.pull(*key)
            except NotFound:
                state = None
            why = ("不存在" if state is None else "已合并" if state.get("merged")
                   else "已关闭" if state.get("state") == "closed" else None)
        else:
            why = f"当前 head 已有 {judged[key]} 判定" if judged.get(key) else None
        if why:
            out.append(finding("DISPATCH_NOT_CLOSED", t, now, f"所指 PR #{key[1]} {why}"))
    return out


def patrol(bus, registry, sla, now, deep=False):
    """Returns the report dict. Raises QueryError when any read did not complete."""
    active = sorted(name for name, meta in registry.items() if meta.get("status") == "active")
    unreadable = [name for name in active if not bus.readable(name)]
    scope = f"user:{bus.owner} archived:false is:open"
    tasks = bus.search(f"{scope} is:issue label:jarvis-task")
    rulings = bus.search(f'{scope} is:issue "{RULING_MARK}" in:title')
    advice = bus.search(f"{scope} is:issue label:claude-advice")
    ivv = bus.search(f'{scope} is:issue "独立评估" in:title')
    prs = bus.search(f"{scope} is:pr")
    findings = (check_tasks(tasks, sla, now) + check_rulings(rulings, sla, now) + check_advice(advice, sla, now)
                + check_singletons(ivv, now) + check_prs(prs, sla, now))
    if deep:
        findings += check_deep(bus, prs, tasks, sla, now)
    findings.sort(key=lambda f: (list(RULES).index(f["rule"]), -f["idle_h"], f["repo"], f["number"]))
    return {"generated": now.strftime("%Y-%m-%d %H:%MZ"), "owner": bus.owner, "deep": deep,
            "coverage": {"active_registered": len(active), "unreadable": unreadable},
            "population": {"jarvis_task": len(tasks), "ruling": sum(RULING_MARK in r["title"] for r in rulings),
                           "claude_advice": len(advice), "open_prs": len(prs)},
            "counts": {rule: sum(f["rule"] == rule for f in findings) for rule in RULES},
            "findings": findings}


def exit_code(report):
    if report["coverage"]["unreadable"]:
        return 2
    return 1 if report["findings"] else 0


def to_markdown(report):
    cov, pop = report["coverage"], report["population"]
    lines = [f"# 闭环末态巡检 · GitHub 面 · {report['generated']}", "",
             f"覆盖：在册 active 仓 {cov['active_registered']} 个"
             + (f"，**其中 {len(cov['unreadable'])} 个读不到：{'、'.join(cov['unreadable'])}（未覆盖≠无异常）**"
                if cov["unreadable"] else "，全部可读") + "。"
             + ("" if report["deep"] else " 本轮未开 `--deep`：`VERDICT_NOT_EXECUTED`／`DISPATCH_NOT_CLOSED` 两项未检。"),
             f"在开总量：jarvis-task {pop['jarvis_task']}｜待中枢裁 {pop['ruling']}｜claude-advice {pop['claude_advice']}｜PR {pop['open_prs']}。",
             "", "| 规则 | 点名数 | 含义 |", "|---|---|---|"]
    for rule, meaning in RULES.items():
        lines.append(f"| `{rule}` | {report['counts'][rule]} | {meaning} |")
    for rule in RULES:
        rows = [f for f in report["findings"] if f["rule"] == rule]
        if not rows:
            continue
        lines += ["", f"## `{rule}`（{len(rows)}）", "", "| 件 | 龄 | 闲置 | 说明 |", "|---|---|---|---|"]
        for f in rows[:LIST_CAP]:
            lines.append(f"| {report['owner']}/{f['repo']}#{f['number']} | {f['age_h']}h | {f['idle_h']}h | {f['detail']} |")
        if len(rows) > LIST_CAP:
            lines.append(f"| …另 {len(rows) - LIST_CAP} 件（全量见 JSON） | | | |")
    if not report["findings"]:
        lines += ["", "本轮全部查询完成，无超时件。"]
    lines += ["", "口径与阈值：`standards/loop_sla.json`。本表只列编号与龄，不列标题（公开仓）。"]
    return "\n".join(lines) + "\n"


def file_issue(report, body, gh=run_gh):
    """Keep exactly one open `loop-watch` issue in this repository in step with the report."""
    repo = f"{report['owner']}/{HOME_REPO}"

    def call(args, what):
        code, out, err = gh([*args, "-R", repo])
        if code != 0:
            raise QueryError(f"{what} failed: {err[:200] or 'exit ' + str(code)}")
        return out.strip()

    call(["label", "create", WATCH_LABEL, "--color", "D93F0B", "--force"], "label")
    existing = call(["issue", "list", "-l", WATCH_LABEL, "--state", "open", "--json", "number", "-q", ".[0].number"], "list")
    if not report["findings"] and not report["coverage"]["unreadable"]:
        if existing:
            call(["issue", "close", existing, "-r", "completed", "-c",
                  f"闭环巡检 {report['generated']}：全部查询完成，无超时件，自动销单。"], "close")
            return f"closed #{existing}"
        return "clean"
    if existing:
        call(["issue", "edit", existing, "-b", body], "update")
        return f"updated #{existing}"
    call(["issue", "create", "-t", WATCH_TITLE, "-b", body, "-l", WATCH_LABEL], "create")
    return "filed"


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0
    json_path = argv[argv.index("--json") + 1] if "--json" in argv else None
    registry = json.loads((HERE / "repos.json").read_text(encoding="utf-8"))["repos"]
    sla = json.loads((HERE / "loop_sla.json").read_text(encoding="utf-8"))
    now = dt.datetime.now(dt.UTC)
    try:
        report = patrol(Bus(), registry, sla, now, deep="--deep" in argv)
        body = to_markdown(report)
        if json_path:
            Path(json_path).write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(body, end="")
        if "--file" in argv:
            print(f"roll-call issue: {file_issue(report, body)}", file=sys.stderr)
    except QueryError as e:
        print(f"::error::闭环巡检未完成，结果为 UNKNOWN（不是无异常）：{e}", file=sys.stderr)
        return 3
    except Exception:  # noqa: BLE001 - a crash is UNKNOWN too, and must not look like exit 1 ("findings")
        traceback.print_exc()
        return 3
    return exit_code(report)


if __name__ == "__main__":
    sys.exit(main())
