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
from typing import ClassVar
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

    def test_lookalike_action_is_not_the_tool(self):
        # #17 round 4 P2-11: a path segment that merely starts with the tool's name passed SEC-1.
        sha = "0" * 40
        root = make(self.base, {".github/workflows/ci.yml": GOOD_WF.replace(
            "gitleaks/gitleaks-action@v3", f"attacker/gitleaks-lookalike@{sha}") + (
            f"      - uses: evil/codeql-action/init@{sha}\n      - uses: x/scorecard-action-fake@{sha}\n")})
        for cid in ("SEC-1", "SEC-3", "SEC-5"):
            self.assertIs(result(root, cid), False, cid)

    def test_sarif_upload_alone_is_not_codeql(self):
        # The Scorecard template uploads its SARIF with github/codeql-action/upload-sarif;
        # that step runs no analysis, so it must not satisfy SEC-3 (CodeQL / SAST runs).
        root = make(self.base, {".github/workflows/ci.yml": GOOD_WF.replace(
            "      - uses: gitleaks/gitleaks-action@v3\n",
            f"      - uses: github/codeql-action/upload-sarif@{'0' * 40}\n")})
        self.assertIs(result(root, "SEC-3"), False)

    def test_real_actions_by_owner_repo_count(self):
        sha = "0" * 40
        root = make(self.base, {".github/workflows/ci.yml": GOOD_WF.replace(
            "      - uses: gitleaks/gitleaks-action@v3\n",
            f"      - uses: trufflesecurity/trufflehog@{sha}\n      - uses: github/codeql-action/analyze@{sha}\n"
            f"      - uses: actions/dependency-review-action@{sha}\n      - uses: ossf/scorecard-action@{sha}\n")})
        for cid in ("SEC-1", "SEC-3", "SEC-4", "SEC-5"):
            self.assertIs(result(root, cid), True, cid)

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
                          ("e.js", "const Anthropic = require('@anthropic-ai/sdk');\n"),
                          ("f.ts", "await fetch('https://api.anthropic.com/v1/messages', init);\n"),
                          ("g.py", "httpx.post('https://api.openai.com/v1/chat/completions', json=body)\n"),
                          ("h.py", "from google import genai\n")):
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

    def test_negated_status_does_not_pass(self):
        for text in ("This project is not proprietary.", "No rights reserved.", "本项目非专有。"):
            with tempfile.TemporaryDirectory() as a:
                root = make(a, {"README.md": "# x\n\n## License\n\n" + text + "\n"})
                self.assertIs(result(root, "GOV-1"), False, text)

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

    def test_swallowed_failure_and_with_inputs_do_not_count(self):
        ro = "permissions:\n  contents: read\n"
        self.assertIs(self.wf(ro, "      - run: pytest || true\n")["QA-1"], False)
        self.assertIs(self.wf(ro, "      - uses: some/action@" + "0" * 40 + "\n        with:\n          run: pytest\n")["QA-1"], False)
        self.assertIs(self.wf(ro, "      - name: t\n        run: pytest\n")["QA-1"], True)

    def test_tests_must_run_on_pull_requests(self):
        with tempfile.TemporaryDirectory() as a:
            root = make(a, {".github/workflows/ci.yml": "on: push\npermissions:\n  contents: read\n" + self.JOB
                            + "    steps:\n      - run: pytest\n"})
            self.assertIs(result(root, "QA-1"), False)

    def test_job_level_permissions_on_every_job_pass(self):
        job = "  {n}:\n    runs-on: x\n    timeout-minutes: 5\n{perm}    steps:\n      - run: pytest\n"
        both = "on: pull_request\njobs:\n" + job.format(n="a", perm="    permissions:\n      contents: read\n") \
            + job.format(n="b", perm="    permissions:\n      contents: write\n")
        one = "on: pull_request\njobs:\n" + job.format(n="a", perm="    permissions:\n      contents: read\n") \
            + job.format(n="b", perm="")
        for wf, want in ((both, True), (one, False)):
            with tempfile.TemporaryDirectory() as a:
                self.assertIs(result(make(a, {".github/workflows/ci.yml": wf}), "SEC-6"), want)

class BootstrapDependabot(unittest.TestCase):
    def test_dotted_directory_keeps_its_dots(self):
        with tempfile.TemporaryDirectory() as a:
            root = make(a, {"apps/web.v2/package-lock.json": "{}\n"})
            self.assertIn(("npm", "/apps/web.v2"), bootstrap.ecosystems(root))

    def test_root_manifest_is_slash(self):
        with tempfile.TemporaryDirectory() as a:
            root = make(a, {"requirements.txt": "x==1\n"})
            self.assertIn(("pip", "/"), bootstrap.ecosystems(root))


class BootstrapHarden(unittest.TestCase):
    """bootstrap.harden_workflow: pins keep the named version; inserted keys keep YAML valid."""

    SHAS: ClassVar[dict] = {("actions/checkout", "v4"): "a" * 40, ("github/codeql-action", "v4"): "b" * 40}

    def resolve(self, repo, ref):
        return self.SHAS.get((repo, ref))

    def test_block_list_runs_on_stays_valid(self):
        wf = "on: push\njobs:\n  build:\n    runs-on:\n      - self-hosted\n    steps:\n      - run: make\n"
        new, _ = bootstrap.harden_workflow(wf, self.resolve)
        self.assertIn("    timeout-minutes: 30\n    runs-on:\n      - self-hosted\n", new)
        self.assertNotIn("runs-on:\n    timeout-minutes", new)

    def test_pin_keeps_the_named_major(self):
        new, changed = bootstrap.harden_workflow(
            "jobs:\n  a:\n    runs-on: x\n    timeout-minutes: 5\n    steps:\n"
            "      - uses: actions/checkout@v4\n      - uses: github/codeql-action/init@v4 # v4\n", self.resolve)
        self.assertIn("uses: actions/checkout@" + "a" * 40 + " # v4\n", new)
        self.assertIn("uses: github/codeql-action/init@" + "b" * 40 + " # v4\n", new)
        self.assertNotIn("# v7", new)

    def test_unresolvable_and_local_refs_are_left_and_reported(self):
        wf = ("jobs:\n  a:\n    runs-on: x\n    timeout-minutes: 5\n    steps:\n"
              "      - uses: ./local\n      - uses: someone/thing@v1\n      - uses: actions/checkout@" + "c" * 40 + " # v7\n")
        new, changed = bootstrap.harden_workflow(wf, self.resolve)
        self.assertEqual(new.count("uses: ./local\n"), 1)
        self.assertIn("uses: someone/thing@v1\n", new)
        self.assertIn("uses: actions/checkout@" + "c" * 40 + " # v7\n", new)
        self.assertIn("UNPINNED (could not resolve) someone/thing@v1", changed)

    def test_quoted_refs_are_pinned_too(self):
        wf = ("jobs:\n  a:\n    runs-on: x\n    timeout-minutes: 5\n    steps:\n"
              "      - uses: 'actions/checkout@v4'\n      - uses: \"github/codeql-action/init@v4\"\n")
        new, _ = bootstrap.harden_workflow(wf, self.resolve)
        self.assertIn("uses: actions/checkout@" + "a" * 40 + " # v4\n", new)
        self.assertIn("uses: github/codeql-action/init@" + "b" * 40 + " # v4\n", new)

    def test_branch_refs_are_reported_not_pinned(self):
        bootstrap._BRANCH_ONLY.add(("someone/action", "main"))
        try:
            wf = "jobs:\n  a:\n    runs-on: x\n    timeout-minutes: 5\n    steps:\n      - uses: someone/action@main\n"
            new, changed = bootstrap.harden_workflow(wf, lambda repo, ref: None)
            self.assertIn("uses: someone/action@main\n", new)
            self.assertIn("UNPINNED (branch ref, pin a release tag by hand) someone/action@main", changed)
        finally:
            bootstrap._BRANCH_ONLY.discard(("someone/action", "main"))


SHA = "3d3c42e5aac5ba805825da76410c181273ba90b1"
PLACEHOLDER = "0" * 40


class TextIsNotExecution(unittest.TestCase):
    """#83: a workflow that runs nothing must not pass the tool checks."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def wf(self, steps, extra=None):
        files = {".github/workflows/ci.yml": (
            "name: ci\non: pull_request\npermissions:\n  contents: read\njobs:\n  a:\n"
            "    runs-on: ubuntu-24.04\n    timeout-minutes: 5\n    steps:\n" + steps)}
        files.update(extra or {})
        return make(self.base, files)

    def test_fixture_from_issue_83_fails_every_tool_check(self):
        steps = (f"      - uses: gitleaks/gitleaks-action@{PLACEHOLDER}\n        if: false\n"
                 f"      - uses: actions/dependency-review-action@{PLACEHOLDER}\n        if: false\n"
                 f"      - uses: ossf/scorecard-action@{PLACEHOLDER}\n        if: ${{{{ false }}}}\n"
                 "      - run: echo pytest ruff mypy playwright dna-drift\n")
        root = self.wf(steps, {"a.py": 'x = "/healthz"  # Content-Security-Policy request_id injection\n'})
        for cid in ("SEC-1", "SEC-4", "SEC-5", "SEC-11", "QA-4", "QA-5", "UI-2", "OPS-1", "OPS-3", "OPS-5"):
            self.assertIsNot(result(root, cid), True, cid)

    def test_disabled_job_does_not_count(self):
        root = make(self.base, {".github/workflows/ci.yml": (
            "name: ci\non: pull_request\npermissions:\n  contents: read\njobs:\n  scan:\n    if: false\n"
            f"    runs-on: ubuntu-24.04\n    timeout-minutes: 5\n    steps:\n      - uses: gitleaks/gitleaks-action@{SHA}\n")})
        self.assertFalse(result(root, "SEC-1"))

    def test_enabled_steps_after_a_disabled_one_still_count(self):
        steps = (f"      - uses: ossf/scorecard-action@{SHA}\n        if: false\n"
                 f"      - uses: gitleaks/gitleaks-action@{SHA}\n      - run: mypy app\n")
        root = self.wf(steps)
        self.assertTrue(result(root, "SEC-1"))
        self.assertFalse(result(root, "SEC-5"))
        self.assertTrue(result(root, "QA-4"))

    def test_conditional_step_is_not_disabled(self):
        root = self.wf(f"      - uses: gitleaks/gitleaks-action@{SHA}\n        if: github.event_name == 'pull_request'\n")
        self.assertTrue(result(root, "SEC-1"))

    def test_placeholder_sha_is_not_a_pin(self):
        self.assertFalse(result(self.wf(f"      - uses: gitleaks/gitleaks-action@{PLACEHOLDER}\n"), "SEC-11"))
        self.assertTrue(result(self.wf(f"      - uses: gitleaks/gitleaks-action@{SHA}\n"), "SEC-11"))

    def test_typecheck_through_a_package_script_counts(self):
        # vertciti-translator: CI runs `npm run lint`, scripts.lint = "tsc --noEmit"
        root = self.wf("      - run: npm run lint\n", {"frontend/package.json": '{"scripts": {"lint": "tsc --noEmit"}}'})
        self.assertTrue(result(root, "QA-4"))

    def test_package_script_that_does_not_typecheck_does_not_count(self):
        root = self.wf("      - run: npm run lint\n", {"package.json": '{"scripts": {"lint": "eslint ."}}'})
        self.assertFalse(result(root, "QA-4"))

    def test_browser_gate_direct_and_through_script(self):
        self.assertTrue(result(self.wf("      - run: scripts/check-contrast.sh\n"), "QA-5"))
        # vertciti-dealdesk: `npm run e2e`, scripts.e2e = "playwright test"
        root = self.wf("      - run: npm run e2e\n", {"package.json": '{"scripts": {"e2e": "playwright test"}}'})
        self.assertTrue(result(root, "QA-5"))
        self.assertFalse(result(self.wf("      - run: npx playwright install chromium\n"), "QA-5"))

    def test_dna_drift_must_be_the_reusable_workflow(self):
        root = make(self.base, {".github/workflows/ci.yml": (
            "name: ci\non: pull_request\npermissions:\n  contents: read\njobs:\n  dna:\n"
            f"    uses: HUIIIM/.github/.github/workflows/dna-drift.yml@{SHA}\n"
            "    with:\n      vendored: static/dna.css\n      flavor: dna.css\n")})
        self.assertTrue(result(root, "UI-2"))

    def test_health_route_registration_counts_client_fetch_does_not(self):
        self.assertTrue(result(make(self.base, {"app/main.py": '@app.get("/healthz")\ndef h():\n    return {}\n'}), "OPS-1"))

    def test_client_fetch_of_health_is_not_an_endpoint(self):
        self.assertFalse(result(make(self.base, {"web/api.ts": 'fetch("/api/v1/health")\n'}), "OPS-1"))

    def test_next_route_file_is_an_endpoint(self):
        self.assertTrue(result(make(self.base, {"frontend/src/app/api/healthz/route.ts": "export function GET() {}\n"}), "OPS-1"))

    def test_headers_in_code_json_and_headers_file_count(self):
        self.assertTrue(result(make(self.base, {"app.py": 'h.setdefault("X-Content-Type-Options", "nosniff")\n'}), "OPS-3"))
        self.assertTrue(result(make(self.base, {"vercel.json": '{"headers": [{"key": "Content-Security-Policy", "value": "x"}]}'}), "OPS-3"))
        self.assertTrue(result(make(self.base, {"site/_headers": "/*\n  Content-Security-Policy: default-src 'self'\n"}), "OPS-3"))

    def test_header_named_in_a_comment_does_not_count(self):
        self.assertFalse(result(make(self.base, {"app.py": "# TODO: Content-Security-Policy, frame-ancestors\nx = 1\n"}), "OPS-3"))
        self.assertFalse(result(make(self.base, {"app.ts": "// set Content-Security-Policy later\nconst x = 1\n"}), "OPS-3"))

    def test_hash_inside_a_python_string_is_not_a_comment(self):
        src = 'CSP = "default-src #x; frame-ancestors \'none\'"\n'
        self.assertTrue(result(make(self.base, {"app.py": src}), "OPS-3"))

    def test_injection_tests_must_live_in_test_files(self):
        llm = {"app/llm.py": "import anthropic\n"}
        self.assertFalse(result(make(self.base, {**llm, "app/guard.py": "INJECTION = 1\n"}), "AI-2"))
        self.assertTrue(result(make(self.base, {**llm, "tests/test_guard.py": "def test_prompt_injection(): pass\n"}), "AI-2"))


if __name__ == "__main__":
    unittest.main()
