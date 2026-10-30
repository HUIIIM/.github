"""Tests for standards/incidents.py with a fake gh (no network).

    python3 -m unittest standards/test_incidents.py
"""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import incidents

REG = {"echowatch": {"status": "active"}, "phonehands": {"status": "active"},
       "miao-ai": {"status": "active"}, "vertciti-sp07-builder": {"status": "archive"},
       "HUIIIM": {"status": "active", "issues": False, "issues_reason": "profile repo"}}


def row(repo, meets_bar, severity=None, missing=False):
    return {"repo": repo, "meets_bar": meets_bar, "severity": severity, "score": 95.0 if meets_bar else 60.0,
            "grade": "S" if meets_bar else "C", "failing": [] if meets_bar else ["SEC-1"], "unprobed": [],
            **({"missing": True} if missing else {})}


class FakeGh:
    def __init__(self, open_issues=None, fail=(), labels=None):
        self.open_issues, self.fail, self.calls = dict(open_issues or {}), set(fail), []
        self.labels, self.argv = dict(labels or {}), []

    def __call__(self, args):
        repo = args[args.index("-R") + 1].split("/", 1)[1]
        self.calls.append((repo, args[:2]))
        self.argv.append((repo, list(args)))
        if (repo, *args[:2]) in self.fail:
            return 1, "", "HTTP 403: Resource not accessible by integration"
        if args[:2] == ["issue", "list"]:
            return 0, self.open_issues.get(repo, ""), ""
        if args[:2] == ["issue", "view"]:
            return 0, "\n".join(self.labels.get(repo, [])), ""
        return 0, "", ""

    def edit_args(self, repo):
        return next(a for r, a in self.argv if r == repo and a[:2] == ["issue", "edit"])

    def did(self, repo, verb):
        return (repo, ["issue", verb]) in self.calls


class IncidentLifecycle(unittest.TestCase):
    def card(self, *rows):
        return {"generated": "2026-10-27 03:40Z", "repos": list(rows)}

    def test_below_bar_files_new_incident_with_labels(self):
        gh = FakeGh()
        f = incidents.Filer(gh)
        out = incidents.process(self.card(row("echowatch", False, "P1")), REG, f)
        self.assertEqual(out["echowatch"], "filed")
        self.assertTrue(gh.did("echowatch", "create"))
        self.assertIn(("echowatch", ["label", "create"]), gh.calls)
        self.assertEqual(f.errors, [])

    def test_below_bar_updates_existing_incident(self):
        gh = FakeGh({"echowatch": "7"})
        out = incidents.process(self.card(row("echowatch", False, "P0")), REG, incidents.Filer(gh))
        self.assertEqual(out["echowatch"], "updated #7")
        self.assertTrue(gh.did("echowatch", "edit"))
        self.assertFalse(gh.did("echowatch", "create"))

    def test_severity_change_removes_the_stale_label(self):
        # #24 verdict / #17 P2-2: a P0 that improves to P1 must not stay labelled P0.
        gh = FakeGh({"echowatch": "7"}, labels={"echowatch": ["standards-incident", "P0"]})
        incidents.process(self.card(row("echowatch", False, "P1")), REG, incidents.Filer(gh))
        args = gh.edit_args("echowatch")
        self.assertEqual(args[args.index("--add-label") + 1], "standards-incident,P1")
        self.assertEqual(args[args.index("--remove-label") + 1], "P0")

    def test_same_severity_removes_nothing(self):
        gh = FakeGh({"echowatch": "7"}, labels={"echowatch": ["standards-incident", "P1"]})
        incidents.process(self.card(row("echowatch", False, "P1")), REG, incidents.Filer(gh))
        self.assertNotIn("--remove-label", gh.edit_args("echowatch"))

    def test_issues_off_by_design_is_skipped_without_calls(self):
        gh = FakeGh()
        f = incidents.Filer(gh)
        out = incidents.process(self.card(row("HUIIIM", False, "P2")), REG, f)
        self.assertEqual(out["HUIIIM"], "skipped (issues off by design: profile repo)")
        self.assertEqual(gh.calls, [])
        self.assertEqual((f.errors, f.unavailable), ([], {}))

    def test_at_bar_closes_open_incident(self):
        gh = FakeGh({"phonehands": "3"})
        out = incidents.process(self.card(row("phonehands", True)), REG, incidents.Filer(gh))
        self.assertEqual(out["phonehands"], "closed #3")
        self.assertTrue(gh.did("phonehands", "close"))

    def test_at_bar_without_incident_does_nothing(self):
        gh = FakeGh()
        out = incidents.process(self.card(row("phonehands", True)), REG, incidents.Filer(gh))
        self.assertEqual(out["phonehands"], "clean")
        self.assertFalse(gh.did("phonehands", "close"))

    def test_missing_repo_is_skipped_and_alias_used_otherwise(self):
        gh = FakeGh()
        out = incidents.process(self.card(row("miao-ai", False, "P0", missing=True)), REG, incidents.Filer(gh))
        self.assertEqual(out["miao-ai"], "skipped (MISSING)")
        self.assertEqual(gh.calls, [])
        gh2 = FakeGh()
        incidents.process(self.card(row("miao-ai", False, "P1")), REG, incidents.Filer(gh2))
        self.assertTrue(gh2.did("anomalies-autogpt", "create"))

    def test_non_active_repos_are_ignored(self):
        gh = FakeGh()
        out = incidents.process(self.card(row("vertciti-sp07-builder", False, "P1")), REG, incidents.Filer(gh))
        self.assertEqual(out, {})

    def test_gh_failure_is_recorded_not_swallowed(self):
        gh = FakeGh(fail={("echowatch", "issue", "create")})
        f = incidents.Filer(gh)
        out = incidents.process(self.card(row("echowatch", False, "P1")), REG, f)
        self.assertEqual(out["echowatch"], "FAILED to file")
        self.assertEqual(len(f.errors), 1)
        self.assertIn("create incident failed", f.errors[0])

    def test_list_failure_never_files_a_duplicate(self):
        gh = FakeGh(open_issues={"echowatch": "7"}, fail={("echowatch", "issue", "list")})
        f = incidents.Filer(gh)
        out = incidents.process(self.card(row("echowatch", False, "P1")), REG, f)
        self.assertEqual(out["echowatch"], "FAILED to list (not filed, to avoid a duplicate)")
        self.assertFalse(gh.did("echowatch", "create"))
        self.assertEqual(len(f.errors), 1)

    def test_list_failure_on_close_is_reported(self):
        gh = FakeGh(fail={("phonehands", "issue", "list")})
        f = incidents.Filer(gh)
        out = incidents.process(self.card(row("phonehands", True)), REG, f)
        self.assertEqual(out["phonehands"], "FAILED to list")
        self.assertEqual(len(f.errors), 1)


class UnavailableGh:
    """Every call fails the way a fine-grained read-only PAT (or a repo with
    issues disabled) does."""

    def __init__(self, message):
        self.message, self.calls = message, []

    def __call__(self, args):
        repo = args[args.index("-R") + 1].split("/", 1)[1]
        self.calls.append((repo, args[:2]))
        return 1, "", self.message


class FilingUnavailable(unittest.TestCase):
    def card(self, *rows):
        return {"generated": "2026-10-27 03:40Z", "repos": list(rows)}

    def test_readonly_pat_marks_repo_unavailable(self):
        gh = UnavailableGh("HTTP 403: Resource not accessible by personal access token "
                           "(https://api.github.com/repos/HUIIIM/echowatch/labels)")
        f = incidents.Filer(gh)
        out = incidents.process(self.card(row("echowatch", False, "P1")), REG, f)
        self.assertEqual(out["echowatch"], "skipped (filing unavailable)")
        self.assertIn("echowatch", f.unavailable)
        self.assertEqual(len(gh.calls), 1)  # short-circuits after the first denial

    def test_issues_disabled_repo_is_unavailable_on_close_path(self):
        gh = UnavailableGh("the 'HUIIIM/phonehands' repository has disabled issues")
        f = incidents.Filer(gh)
        out = incidents.process(self.card(row("phonehands", True)), REG, f)
        self.assertEqual(out["phonehands"], "skipped (filing unavailable)")
        self.assertEqual(f.errors, [])
        self.assertIn("phonehands", f.unavailable)


    def test_unavailable_filing_fails_the_run(self):
        # #17 round 4 P1-1: run 41040949024 skipped every below-bar repo and still exited 0.
        # An incident that cannot be filed is not handled, so main() must exit non-zero.
        card = self.card(row("echowatch", False, "P0"), row("phonehands", False, "P1"))
        gh = UnavailableGh("HTTP 403: Resource not accessible by personal access token")
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "card.json"
            path.write_text(json.dumps(card), encoding="utf-8")
            with mock.patch.object(incidents, "run_gh", gh), mock.patch.object(sys, "argv", ["incidents.py", str(path)]), \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
                with self.assertRaises(SystemExit) as exit_:
                    incidents.main()
        self.assertEqual(exit_.exception.code, 1)
        self.assertIn("filing unavailable for 2 repo(s)", err.getvalue())


if __name__ == "__main__":
    unittest.main()
