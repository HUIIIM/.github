"""Tests for standards/incidents.py with a fake gh (no network).

    python3 -m unittest standards/test_incidents.py
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import incidents  # noqa: E402

REG = {"echowatch": {"status": "active"}, "phonehands": {"status": "active"},
       "miao-ai": {"status": "active"}, "vertciti-sp07-builder": {"status": "archive"}}


def row(repo, meets_bar, severity=None, missing=False):
    return {"repo": repo, "meets_bar": meets_bar, "severity": severity, "score": 95.0 if meets_bar else 60.0,
            "grade": "S" if meets_bar else "C", "failing": [] if meets_bar else ["SEC-1"], "unprobed": [],
            **({"missing": True} if missing else {})}


class FakeGh:
    def __init__(self, open_issues=None, fail=()):
        self.open_issues, self.fail, self.calls = dict(open_issues or {}), set(fail), []

    def __call__(self, args):
        repo = args[args.index("-R") + 1].split("/", 1)[1]
        self.calls.append((repo, args[:2]))
        if (repo, *args[:2]) in self.fail:
            return 1, "", "HTTP 403: Resource not accessible by integration"
        if args[:2] == ["issue", "list"]:
            return 0, self.open_issues.get(repo, ""), ""
        return 0, "", ""

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


if __name__ == "__main__":
    unittest.main()
