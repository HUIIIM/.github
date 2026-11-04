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

    VERIFIED_BIN = (
        "      - run: |\n"
        "          curl -sSfL -o g.tgz https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz\n"
        f"          echo \"{'a' * 64}  g.tgz\" | sha256sum -c -\n"
        "          tar -xzf g.tgz gitleaks\n"
        "      - run: ./gitleaks git --redact --exit-code 1 .\n")

    def test_checksum_verified_binary_counts_for_sec1(self):
        # A pinned-sha256 binary is a stronger supply chain than an action that downloads
        # an unverified one (SOTA SEC-A5); Miao #9 verdict.
        root = make(self.base, {".github/workflows/ci.yml": GOOD_WF.replace(
            "      - uses: gitleaks/gitleaks-action@v3\n", self.VERIFIED_BIN)})
        self.assertIs(result(root, "SEC-1"), True)

    def test_binary_without_checksum_or_from_elsewhere_does_not_count(self):
        unverified = self.VERIFIED_BIN.replace("| sha256sum -c -", "")
        elsewhere = self.VERIFIED_BIN.replace("github.com/gitleaks/gitleaks", "evil.example/gitleaks")
        no_scan = self.VERIFIED_BIN.replace("./gitleaks git", "echo gitleaks git")
        for name, steps in (("unverified", unverified), ("elsewhere", elsewhere), ("no_scan", no_scan)):
            root = make(Path(self.base) / name, {".github/workflows/ci.yml": GOOD_WF.replace(
                "      - uses: gitleaks/gitleaks-action@v3\n", steps)})
            self.assertIs(result(root, "SEC-1"), False, name)

    def _bin_wf(self, steps):
        return GOOD_WF.replace("      - uses: gitleaks/gitleaks-action@v3\n", steps)

    def test_sec1_text_bypasses_fail(self):
        # #94 / #108 SEC-1 bypasses: text that looks like a scan but never executes.
        v = self.VERIFIED_BIN
        scan = "      - run: ./gitleaks git --redact --exit-code 1 .\n"
        cases = {
            "comment": v.replace(scan, "      # - run: ./gitleaks git --redact .\n      - run: echo hi\n"),
            "comment_in_block": v.replace(scan, "      - run: |\n          # gitleaks git .\n          echo hi\n"),
            "if_false": v.replace(scan, "      - if: false\n        run: ./gitleaks git .\n"),
            "if_false_expr": v.replace(scan, "      - if: ${{ false }}\n        run: ./gitleaks git .\n"),
            "job_if_false": v.replace("    steps:", "    steps:") and GOOD_WF.replace(
                "    timeout-minutes: 10\n", "    timeout-minutes: 10\n    if: false\n").replace(
                "      - uses: gitleaks/gitleaks-action@v3\n", v),
            "heredoc_print": v.replace(scan, "      - run: |\n          cat <<EOF\n          gitleaks git .\n          EOF\n"),
            "echo_print": v.replace(scan, "      - run: echo 'gitleaks git .'\n"),
            "swallowed": v.replace(scan, "      - run: ./gitleaks git . || true\n"),
            "continue_on_error": v.replace(scan, "      - run: ./gitleaks git .\n        continue-on-error: true\n"),
            "download_only_in_echo": v.replace("          curl -sSfL -o g.tgz", "          echo curl -sSfL -o g.tgz"),
            "verify_only_in_heredoc": v.replace(
                f"          echo \"{'a' * 64}  g.tgz\" | sha256sum -c -\n",
                f"          cat <<EOF\n          echo \"{'a' * 64}  g.tgz\" | sha256sum -c -\n          EOF\n"),
        }
        for name, steps in cases.items():
            wf = steps if name == "job_if_false" else self._bin_wf(steps)
            root = make(Path(self.base) / name, {".github/workflows/ci.yml": wf})
            self.assertIs(result(root, "SEC-1"), False, name)

    def test_sec1_real_executed_scan_passes(self):
        v = self.VERIFIED_BIN
        scan = "      - run: ./gitleaks git --redact --exit-code 1 .\n"
        cases = {
            "plain": v,
            "if_true": v.replace(scan, "      - if: always()\n        run: ./gitleaks git .\n"),
            "in_block": v.replace(scan, "      - run: |\n          echo scanning\n          ./gitleaks git --redact .\n"),
            "chained": v.replace(scan, "      - run: cd . && ./gitleaks detect --redact\n"),
            "after_heredoc": v.replace(scan, "      - run: |\n          cat <<EOF > note\n          x\n          EOF\n          ./gitleaks dir .\n"),
        }
        for name, steps in cases.items():
            root = make(Path(self.base) / name, {".github/workflows/ci.yml": self._bin_wf(steps)})
            self.assertIs(result(root, "SEC-1"), True, name)

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
                          ("h.py", "from google import genai\n"),
                          ("i.py", 'client.post(f"{settings.llm_base_url}/chat/completions", json=body)\n'),
                          ("j.ts", "await fetch('https://api.deepseek.com/v1/chat/completions', init);\n")):
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

    def test_flow_mapping_permissions(self):
        # `permissions: { contents: read }` is read-only; a write inside the braces still fails.
        self.assertIs(self.wf("permissions: { contents: read }\n", "      - run: pytest\n")["SEC-6"], True)
        self.assertIs(self.wf("permissions: {contents: read, issues: write}\n", "      - run: pytest\n")["SEC-6"], False)
        self.assertIs(self.wf("permissions: {}\n", "      - run: pytest\n")["SEC-6"], True)
        self.assertIs(self.wf("permissions: read-all\n", "      - run: pytest\n")["SEC-6"], True)

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


if __name__ == "__main__":
    unittest.main()
