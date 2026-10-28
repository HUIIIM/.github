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


class LlmDetection(unittest.TestCase):
    def test_identifier_containing_llm_is_not_an_llm_app(self):
        with tempfile.TemporaryDirectory() as a:
            root = make(a, {"app.py": "import re\nre.fullmatch(r'x', 'x')  # no openai here\n"})
            self.assertFalse(audit.uses_llm(root))

    def test_sdk_imports_are_detected(self):
        for rel, code in (("a.py", "from anthropic import Anthropic\n"),
                          ("b.py", "import openai\n"),
                          ("c.ts", 'import OpenAI from "openai";\n'),
                          ("d.ts", "import { generateText } from 'ai';\n"),
                          ("e.js", "const Anthropic = require('@anthropic-ai/sdk');\n")):
            with tempfile.TemporaryDirectory() as a:
                self.assertTrue(audit.uses_llm(make(a, {rel: code})), rel)


class LicenseCheck(unittest.TestCase):
    def test_license_file_passes(self):
        with tempfile.TemporaryDirectory() as a:
            self.assertIs(result(make(a, {"LICENSE": "MIT\n"}), "GOV-1"), True)

    def test_readme_licence_section_with_status_passes(self):
        with tempfile.TemporaryDirectory() as a:
            root = make(a, {"README.md": "# x\n\n## License\n\nProprietary. All rights reserved by the owner.\n"})
            self.assertIs(result(root, "GOV-1"), True)

    def test_status_word_outside_licence_section_fails(self):
        with tempfile.TemporaryDirectory() as a:
            root = make(a, {"README.md": "# x\n\nOur proprietary engine.\n\n## Usage\n\nrun it\n"})
            self.assertIs(result(root, "GOV-1"), False)


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
