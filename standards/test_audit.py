"""Regression tests for the assessor (standards/audit.py) and bootstrap.py.

    python3 -m unittest standards/test_audit.py

Each test builds a throw-away repository and asserts a grade the independent
assessment (issue #17) showed was wrong: checks passed by a comment or an empty
file, grades that depended on the checkout path, a lost dot in a Dependabot
directory. Old code red, new code green.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit
import bootstrap

NAME = "echowatch"  # any registered app/active repo; only its registry entry is used


def make(base, files):
    root = Path(base) / NAME
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return root


def result(root, cid):
    out = audit.audit(root, audit.REGISTRY[NAME])
    return next(c["ok"] for c in out["checks"] if c["id"] == cid)


GOOD_WF = """name: ci
on: pull_request
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - uses: gitleaks/gitleaks-action@v3
      - run: pytest
"""


class ChecksCannotBeGamed(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_tool_named_only_in_a_comment_does_not_count(self):
        root = make(self.base, {".github/workflows/ci.yml": "# TODO: gitleaks, codeql-action, pytest, ruff\n" + GOOD_WF.replace(
            "      - uses: gitleaks/gitleaks-action@v3\n      - run: pytest\n", "      - run: echo hi\n")})
        for cid in ("SEC-1", "SEC-3", "QA-1", "QA-2"):
            self.assertIs(result(root, cid), False, cid)

    def test_real_tools_still_count(self):
        root = make(self.base, {".github/workflows/ci.yml": GOOD_WF})
        self.assertIs(result(root, "SEC-1"), True)
        self.assertIs(result(root, "QA-1"), True)

    def test_tool_named_only_in_a_run_line_does_not_count(self):
        # The PR #21 verdict's probe: mentioning a tool in a run: echo is not running it.
        root = make(self.base, {".github/workflows/ci.yml": GOOD_WF.replace(
            "      - uses: gitleaks/gitleaks-action@v3\n      - run: pytest\n",
            "      - run: echo gitleaks codeql-action dependency-review-action scorecard-action\n")})
        for cid in ("SEC-1", "SEC-3", "SEC-4", "SEC-5"):
            self.assertIs(result(root, cid), False, cid)

    def test_codeql_uses_step_counts(self):
        root = make(self.base, {".github/workflows/ci.yml": GOOD_WF.replace(
            "      - uses: gitleaks/gitleaks-action@v3\n",
            "      - uses: github/codeql-action/init@v3\n")})
        self.assertIs(result(root, "SEC-3"), True)
        self.assertIs(result(root, "SEC-1"), False)

    def test_write_all_fails_least_privilege(self):
        root = make(self.base, {".github/workflows/ci.yml": GOOD_WF.replace("permissions:\n  contents: read", "permissions: write-all")})
        self.assertIs(result(root, "SEC-6"), False)

    def test_step_timeout_is_not_a_job_timeout(self):
        wf = GOOD_WF.replace("    timeout-minutes: 10\n", "").replace("      - run: pytest\n", "      - run: pytest\n        timeout-minutes: 5\n")
        root = make(self.base, {".github/workflows/ci.yml": wf})
        self.assertIs(result(root, "SEC-8"), False)

    def test_every_job_needs_its_own_timeout(self):
        wf = GOOD_WF + "  lint:\n    runs-on: ubuntu-24.04\n    steps:\n      - run: ruff check\n"
        root = make(self.base, {".github/workflows/ci.yml": wf})
        self.assertIs(result(root, "SEC-8"), False)
        root2 = make(tempfile.mkdtemp(dir=self.base), {".github/workflows/ci.yml": GOOD_WF})
        self.assertIs(result(root2, "SEC-8"), True)

    def test_empty_docs_do_not_pass(self):
        root = make(self.base, {"CHANGELOG.md": "# Changelog\n", "docs/PRODUCT.md": "", "docs/RUNBOOK.md": "# Runbook\n\n## Deploy\n"})
        for cid in ("DOC-2", "DOC-3", "CONT-1"):
            self.assertIs(result(root, cid), False, cid)

    def test_real_docs_pass(self):
        body = "## [1.0.0] - 2026-10-01\n### Added\n- First public release of the console with audit chain and approvals queue.\n"
        root = make(self.base, {"CHANGELOG.md": "# Changelog\n\n" + body})
        self.assertIs(result(root, "DOC-3"), True)

    def test_status_word_must_be_a_word(self):
        root = make(self.base, {"README.md": "# x\n\nThe alphabet of tools.\n"})
        self.assertIs(result(root, "GOV-4"), False)
        root2 = make(tempfile.mkdtemp(dir=self.base), {"README.md": "# x\n\nStatus: beta.\n"})
        self.assertIs(result(root2, "GOV-4"), True)


class CheckoutPathDoesNotChangeGrades(unittest.TestCase):
    def test_build_in_parent_path_is_not_skipped(self):
        files = {"web/package.json": '{"dependencies": {"x": "*"}}\n'}
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            plain = make(a, files)
            under_build = make(Path(b) / "build", files)
            for cid in ("SEC-2", "SEC-10"):
                self.assertEqual(result(plain, cid), result(under_build, cid), cid)
            self.assertIs(result(under_build, "SEC-10"), False)  # unlocked package.json is seen

    def test_build_inside_repo_is_still_skipped(self):
        with tempfile.TemporaryDirectory() as a:
            root = make(a, {"build/package.json": '{"dependencies": {"x": "*"}}\n'})
            self.assertIs(result(root, "SEC-10"), True)


class LeastPrivilegeAndRealTools(unittest.TestCase):
    """SEC-6 reads workflow-level permissions; QA-1/QA-2 need the tool to be the command that runs."""

    JOB = "jobs:\n  a:\n    runs-on: x\n    timeout-minutes: 5\n"

    def wf(self, head, steps):
        with tempfile.TemporaryDirectory() as a:
            root = make(a, {".github/workflows/ci.yml": "on: pull_request\n" + head + self.JOB + "    steps:\n" + steps})
            return {cid: result(root, cid) for cid in ("SEC-6", "QA-1", "QA-2")}

    def test_quoted_write_all_fails(self):
        self.assertIs(self.wf('permissions: "write-all"\n', "      - run: pytest\n")["SEC-6"], False)

    def test_workflow_level_write_fails_job_level_write_passes(self):
        self.assertIs(self.wf("permissions:\n  contents: write\n", "      - run: pytest\n")["SEC-6"], False)
        job_write = "permissions:\n  contents: read\n"
        with tempfile.TemporaryDirectory() as a:
            root = make(a, {".github/workflows/ci.yml": "on: push\n" + job_write + self.JOB
                            + "    permissions:\n      contents: write\n    steps:\n      - run: pytest\n"})
            self.assertIs(result(root, "SEC-6"), True)

    def test_echoing_tool_names_is_not_running_them(self):
        got = self.wf("permissions:\n  contents: read\n", "      - run: echo gitleaks codeql-action pytest ruff\n")
        self.assertIs(got["QA-1"], False)
        self.assertIs(got["QA-2"], False)

    def test_real_commands_count(self):
        got = self.wf("permissions:\n  contents: read\n",
                      "      - run: |\n          pip install ruff\n          ruff check .\n          python -m pytest -q\n")
        self.assertIs(got["QA-1"], True)
        self.assertIs(got["QA-2"], True)
        self.assertIs(self.wf("permissions:\n  contents: read\n", "      - run: test -f x && echo ok\n")["QA-1"], False)

class BootstrapDependabot(unittest.TestCase):
    def test_dotted_directory_keeps_its_dots(self):
        with tempfile.TemporaryDirectory() as a:
            root = make(a, {"apps/web.v2/package-lock.json": "{}\n"})
            self.assertIn(("npm", "/apps/web.v2"), bootstrap.ecosystems(root))

    def test_root_manifest_is_slash(self):
        with tempfile.TemporaryDirectory() as a:
            root = make(a, {"requirements.txt": "x==1\n"})
            self.assertIn(("pip", "/"), bootstrap.ecosystems(root))


if __name__ == "__main__":
    unittest.main()
