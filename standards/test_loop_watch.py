"""Tests for standards/loop_watch.py with a fake gh (no network).

    python3 -m unittest standards/test_loop_watch.py
"""
import datetime as dt
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loop_watch as lw

NOW = dt.datetime(2026, 11, 12, 12, 0, tzinfo=dt.UTC)
SLA = json.loads((Path(__file__).resolve().parent / "loop_sla.json").read_text(encoding="utf-8"))
REG = {".github": {"status": "active"}, "fama": {"status": "active"}, "old": {"status": "archive"}}


def ago(h):
    return (NOW - dt.timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ")


def item(repo, number, title, labels=(), comments=0, age=100, idle=None, user="HUIIIM", pr=False, draft=False):
    it = {"repository_url": f"https://api.github.com/repos/HUIIIM/{repo}", "number": number, "title": title,
          "user": {"login": user}, "labels": [{"name": n} for n in labels], "comments": comments,
          "created_at": ago(age), "updated_at": ago(age if idle is None else idle), "draft": draft}
    if pr:
        it["pull_request"] = {}
    return it


class FakeGh:
    """Answers `gh api` from canned data. `search` maps a query substring to items."""

    def __init__(self, search=None, pulls=None, comments=None, unreadable=(), fail=None, incomplete=False):
        self.search, self.pulls, self.comments = search or {}, pulls or {}, comments or {}
        self.unreadable, self.fail, self.incomplete, self.argv = set(unreadable), fail, incomplete, []

    def __call__(self, args):
        self.argv.append(list(args))
        path = args[3]
        if self.fail and self.fail in " ".join(args):
            return 1, "", "gh: connection timed out"
        if path == "search/issues":
            q = next(a for a in args if a.startswith("q="))[2:]
            if q.startswith("repo:"):
                repo = q.split()[0].split("/", 1)[1]
                if repo in self.unreadable:
                    return 1, "", ("gh: Validation Failed (HTTP 422)\nThe listed users and repositories cannot be "
                                   "searched either because the resources do not exist or you do not have permission")
                return 0, json.dumps({"total_count": 0, "incomplete_results": False, "items": []}), ""
            items = next((v for k, v in self.search.items() if k in q), [])
            doc = {"total_count": len(items) + (5 if self.incomplete else 0), "incomplete_results": False, "items": items}
            return 0, json.dumps(doc), ""
        m = path.split("/")
        if "pulls" in m:
            key = (m[2], int(m[4]))
            if key not in self.pulls:
                return 1, "", "gh: Not Found (HTTP 404)"
            return 0, json.dumps(self.pulls[key]), ""
        if "comments" in path:
            return 0, json.dumps(self.comments.get((m[2], int(m[4])), [])), ""
        return 1, "", "unexpected call"


def bus(gh):
    return lw.Bus(gh, pause=0)


def run(gh, deep=False):
    return lw.patrol(bus(gh), REG, SLA, NOW, deep=deep)


def rules(report):
    return sorted((f["rule"], f["repo"], f["number"]) for f in report["findings"])


class StateMachine(unittest.TestCase):
    def test_task_without_state_label_is_named(self):
        gh = FakeGh({"label:jarvis-task": [item(".github", 1, "[jarvis-task] a", ["jarvis-task"])]})
        self.assertEqual(rules(run(gh)), [("NO_STATE", ".github", 1)])

    def test_two_state_labels_are_named_too(self):
        gh = FakeGh({"label:jarvis-task": [item(".github", 1, "t", ["jarvis-task", "jarvis-task:queued", "jarvis-task:review"])]})
        r = run(gh)
        self.assertEqual(rules(r), [("NO_STATE", ".github", 1)])
        self.assertIn("多个状态标签", r["findings"][0]["detail"])

    def test_state_within_window_is_quiet_and_past_window_is_named(self):
        gh = FakeGh({"label:jarvis-task": [
            item(".github", 1, "t", ["jarvis-task", "jarvis-task:queued"], idle=47),
            item(".github", 2, "t", ["jarvis-task", "jarvis-task:queued"], idle=49),
            item(".github", 3, "t", ["jarvis-task", "jarvis-task:blocked"], idle=60),
            item(".github", 4, "t", ["jarvis-task", "jarvis-task:done"], idle=900)]})
        self.assertEqual(rules(run(gh)), [("STALE_STATE", ".github", 2)])


class RulingsAndAdvice(unittest.TestCase):
    def test_ruling_past_48h_is_named_and_says_whether_anyone_replied(self):
        gh = FakeGh({"待中枢裁": [
            item("fama", 5, "[jarvis-task] 待中枢裁：x", age=50, comments=0),
            item("fama", 6, "[jarvis-task] 待中枢裁：y", age=50, comments=2),
            item("fama", 7, "[jarvis-task] 待中枢裁：z", age=40),
            item("fama", 8, "正文里才提到裁决的别的单", age=500)]})
        r = run(gh)
        self.assertEqual(rules(r), [("RULING_OVERDUE", "fama", 5), ("RULING_OVERDUE", "fama", 6)])
        details = {f["number"]: f["detail"] for f in r["findings"]}
        self.assertEqual(details[5], "无任何回执")
        self.assertIn("未关单", details[6])
        self.assertEqual(r["population"]["ruling"], 3)

    def test_advice_with_no_reply_past_window_is_named(self):
        gh = FakeGh({"label:claude-advice": [
            item("fama", 1, "a", ["claude-advice"], age=80, comments=0),
            item("fama", 2, "b", ["claude-advice"], age=80, comments=1),
            item("fama", 3, "c", ["claude-advice"], age=10, comments=0)]})
        self.assertEqual(rules(run(gh)), [("ADVICE_NO_RECEIPT", "fama", 1)])


class SingletonsAndPrs(unittest.TestCase):
    def test_duplicate_ivv_issue_is_named_once(self):
        t = "[独立评估] 全仓审查 · HUIIIM/.github"
        gh = FakeGh({"独立评估": [item(".github", 93, t), item(".github", 94, t), item("fama", 3, "[独立评估] 全仓审查 · HUIIIM/fama")]})
        r = run(gh)
        self.assertEqual(rules(r), [("SINGLETON_DUP", ".github", 94)])
        self.assertIn("#93、#94", r["findings"][0]["detail"])

    def test_pr_windows_differ_by_kind(self):
        gh = FakeGh({"is:pr": [
            item("fama", 1, "ready", pr=True, idle=73),
            item("fama", 2, "ready fresh", pr=True, idle=71),
            item("fama", 3, "draft", pr=True, draft=True, idle=100),
            item("fama", 4, "draft old", pr=True, draft=True, idle=169),
            item("fama", 5, "bump", pr=True, user="dependabot[bot]", idle=300),
            item("fama", 6, "bump old", pr=True, user="dependabot[bot]", idle=337)]})
        self.assertEqual(rules(run(gh)), [("PR_STALE", "fama", 1), ("PR_STALE", "fama", 4), ("PR_STALE", "fama", 6)])


SHA = "a982e6c68e29753b3280df906e73644ca49e3d64"
PASS_EN = f"## Independent verdict — PASS (bound to head `{SHA}`)\n\n| Dimension | Result |"
PASS_ZH = f"### 独立评估 · SOTA v1.0 · {SHA[:7]}\n判定：PASS\n"
FAIL_ZH = f"### 独立评估 · SOTA v1.0 · {SHA[:7]}\n判定：FAIL（MUST 未过 1 条）\n"


class Deep(unittest.TestCase):
    """The real case behind these: HUIIIM/.github #127 (PASS on head, still open) and its dispatch #129."""

    def world(self, comment_body, comment_age=30, dispatch_pr=127):
        pr = item(".github", 127, "fix", pr=True, idle=10)
        dispatch = item(".github", 129, f"[jarvis-task] 独立评估派发:PR #{dispatch_pr} 当前 head a982e6c6",
                        ["jarvis-task", "jarvis-task:review"], idle=10)
        return FakeGh({"is:pr": [pr], "label:jarvis-task": [dispatch]},
                      pulls={(".github", 127): {"head": {"sha": SHA}, "state": "open", "merged": False},
                             (".github", 70): {"head": {"sha": "f" * 40}, "state": "closed", "merged": True}},
                      comments={(".github", 127): [{"body": comment_body, "created_at": ago(comment_age)}]})

    def test_pass_on_current_head_and_still_open_names_both_the_pr_and_its_dispatch(self):
        for body in (PASS_EN, PASS_ZH):
            with self.subTest(body=body[:20]):
                r = run(self.world(body), deep=True)
                self.assertEqual(rules(r), [("DISPATCH_NOT_CLOSED", ".github", 129), ("VERDICT_NOT_EXECUTED", ".github", 127)])

    def test_fresh_pass_is_inside_the_execute_window(self):
        r = run(self.world(PASS_EN, comment_age=5), deep=True)
        self.assertEqual(rules(r), [("DISPATCH_NOT_CLOSED", ".github", 129)])

    def test_verdict_for_an_older_head_does_not_count(self):
        r = run(self.world(PASS_EN.replace(SHA, "b" * 40)), deep=True)
        self.assertEqual(rules(r), [])

    def test_fail_on_head_closes_the_dispatch_but_is_not_an_unexecuted_pass(self):
        r = run(self.world(FAIL_ZH), deep=True)
        self.assertEqual(rules(r), [("DISPATCH_NOT_CLOSED", ".github", 129)])

    def test_dispatch_for_a_merged_pr_is_named(self):
        r = run(self.world("no verdict here", dispatch_pr=70), deep=True)
        self.assertEqual(rules(r), [("DISPATCH_NOT_CLOSED", ".github", 129)])
        self.assertIn("已合并", r["findings"][0]["detail"])

    def test_dispatch_naming_a_pr_that_does_not_exist_is_named_not_fatal(self):
        r = run(self.world("no verdict here", dispatch_pr=999), deep=True)
        self.assertIn("不存在", r["findings"][0]["detail"])

    def test_without_deep_no_pull_is_read(self):
        gh = self.world(PASS_EN)
        run(gh)
        self.assertFalse([a for a in gh.argv if "pulls" in a[3]])


class FailLoud(unittest.TestCase):
    def test_unreadable_registered_repo_is_a_coverage_gap_exit_2(self):
        r = run(FakeGh(unreadable={"fama"}))
        self.assertEqual(r["coverage"]["unreadable"], ["fama"])
        self.assertEqual(lw.exit_code(r), 2)
        self.assertIn("未覆盖≠无异常", lw.to_markdown(r))

    def test_archived_repos_are_not_probed(self):
        gh = FakeGh()
        run(gh)
        self.assertFalse([a for a in gh.argv if "q=repo:HUIIIM/old " in " ".join(a)])

    def test_a_failed_query_is_unknown_never_clean(self):
        with self.assertRaises(lw.QueryError):
            run(FakeGh(fail="label:claude-advice"))

    def test_incomplete_search_results_are_unknown_never_clean(self):
        with self.assertRaises(lw.QueryError):
            run(FakeGh({"is:pr": [item("fama", 1, "x", pr=True)]}, incomplete=True))

    def test_exit_codes(self):
        clean = run(FakeGh())
        self.assertEqual((lw.exit_code(clean), clean["findings"]), (0, []))
        dirty = run(FakeGh({"label:jarvis-task": [item(".github", 1, "t", ["jarvis-task"])]}))
        self.assertEqual(lw.exit_code(dirty), 1)

    def test_main_returns_3_when_a_query_fails(self):
        broken = lw.Bus(FakeGh(fail="search/issues"), pause=0)
        with mock.patch.object(lw, "Bus", return_value=broken):
            self.assertEqual(lw.main([]), 3)


class Output(unittest.TestCase):
    def test_markdown_never_prints_titles(self):
        gh = FakeGh({"label:jarvis-task": [item("fama", 9, "SECRET-TITLE-TEXT", ["jarvis-task"])]})
        md = lw.to_markdown(run(gh))
        self.assertNotIn("SECRET-TITLE-TEXT", md)
        self.assertIn("HUIIIM/fama#9", md)

    def test_markdown_caps_rows_but_counts_all(self):
        rows = [item("fama", n, "t", ["jarvis-task"]) for n in range(1, 31)]
        r = run(FakeGh({"label:jarvis-task": rows}))
        md = lw.to_markdown(r)
        self.assertEqual(r["counts"]["NO_STATE"], 30)
        self.assertIn(f"另 {30 - lw.LIST_CAP} 件", md)


class Filing(unittest.TestCase):
    def gh(self, existing=""):
        calls = []

        def fake(args):
            calls.append(args[:2])
            return 0, (existing if args[:2] == ["issue", "list"] else ""), ""
        return fake, calls

    def report(self, findings):
        return {"owner": "HUIIIM", "generated": "g", "findings": findings, "coverage": {"unreadable": []}}

    def test_findings_create_then_update_one_issue(self):
        fake, calls = self.gh()
        self.assertEqual(lw.file_issue(self.report([{}]), "body", fake), "filed")
        self.assertIn(["issue", "create"], calls)
        fake, calls = self.gh("42")
        self.assertEqual(lw.file_issue(self.report([{}]), "body", fake), "updated #42")
        self.assertNotIn(["issue", "create"], calls)

    def test_clean_run_closes_the_open_issue(self):
        fake, calls = self.gh("42")
        self.assertEqual(lw.file_issue(self.report([]), "body", fake), "closed #42")
        fake, _ = self.gh()
        self.assertEqual(lw.file_issue(self.report([]), "body", fake), "clean")


if __name__ == "__main__":
    unittest.main()
