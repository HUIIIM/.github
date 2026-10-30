#!/usr/bin/env python3
"""Independent assessment of the portfolio against STANDARDS.md (v2: graded).

    python3 standards/audit.py ~/src                 # every repo in repos.json found under ~/src
    python3 standards/audit.py ~/src --md            # markdown scorecard (SCORECARD.md)
    python3 standards/audit.py ~/src --json out.json # machine scorecard (scorecard.json)
    python3 standards/audit.py ~/src --live          # also probe deployed URLs (repos.json "url")
    python3 standards/audit.py ~/src --only echowatch
    python3 standards/audit.py ~/src --incidents     # JSON list of repos below the bar

Read-only against the repositories. The assessor is independent of the
repositories it grades: it lives here, runs on its own schedule, and the
grade is published whatever it says (STANDARDS.md §考核).

Grading: every applicable check carries weight 3 (MUST) or 1 (SHOULD);
score = earned / applicable * 100. Grades: S >= 95, A++ >= 90, A >= 85,
B >= 70, C below. The bar is A++ ("state of the art" line). A repo below
the bar is an incident: P0 < 70 or a failing safety MUST, P1 < 85 or any
failing MUST, P2 < 90. Checks that cannot run (no URL, tool missing) are
"unprobed" and count as failed for the score: an empty stratum is
"unverified", never "passed". A deployment that is private by design is
declared in repos.json ("public": false + "public_reason"); its live checks
are then recorded as n/a with the reason, not scored.

A registered repository that cannot be read (clone failed, not found) is not
dropped: it gets a MISSING row (score 0, grade C, P0) on every output.

Exit code 2 when any registered repository is MISSING, else 1 when any
applicable MUST check fails, else 0.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTRY = json.loads((HERE / "repos.json").read_text(encoding="utf-8"))["repos"]

ALL = {"app", "library", "skill", "tool", "site", "docs", "profile", "meta"}
CODE = {"app", "library", "tool"}
WEIGHT = {"MUST": 3, "SHOULD": 1}
GRADES = (("S", 95), ("A++", 90), ("A", 85), ("B", 70), ("C", 0))
BAR = "A++"
BAR_MIN = 90
SAFETY_MUST = {"SEC-1", "SEC-6", "GOV-1", "REL-1"}  # a failing one of these is P0 on its own
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", ".next", "dist", "build", "__pycache__", "evidence"}
LIVE = {"enabled": False, "timeout": 12}


# ----------------------------------------------------------------------------- helpers

def exists(root, *paths):
    return any((root / p).exists() for p in paths)


def read(root, *paths):
    for p in paths:
        f = root / p
        if f.is_file():
            return f.read_text(encoding="utf-8", errors="replace")
    return ""


def skipped(root, p):
    """True when p lies under a vendored/build directory *inside* the repository.

    Judged on the path relative to root: the directory the portfolio is checked
    out under (/tmp/build/..., ~/dist/...) must not change any grade.
    """
    return any(part in SKIP_DIRS for part in p.relative_to(root).parts)


def iter_files(root, suffixes):
    for p in root.rglob("*"):
        if skipped(root, p):
            continue
        if p.is_file() and (p.name in suffixes or p.suffix in suffixes):
            yield p


def grep(root, pattern, suffixes):
    rx = re.compile(pattern, re.MULTILINE)
    for p in iter_files(root, suffixes):
        try:
            if rx.search(p.read_text(encoding="utf-8", errors="replace")):
                return True
        except OSError:
            continue
    return False


COMMENT = re.compile(r"(^|\s)#.*$", re.MULTILINE)


def workflows(root):
    """All workflow files, YAML comments removed: a tool named in a comment is not a tool that runs."""
    d = root / ".github" / "workflows"
    return "\n".join(COMMENT.sub("", f.read_text(encoding="utf-8", errors="replace"))
                     for f in sorted(d.glob("*.y*ml"))) if d.is_dir() else ""


def substantive(root, *paths, min_chars=40):
    """The file exists AND has real content: at least min_chars of text outside headings.

    STANDARDS.md 诚实条款: a check that can be passed by faking (an empty CHANGELOG) counts as failed.
    """
    for p in paths:
        f = root / p
        if f.is_file():
            body = "\n".join(l for l in f.read_text(encoding="utf-8", errors="replace").splitlines()
                             if l.strip() and not l.lstrip().startswith("#"))
            if len(re.sub(r"\s+", "", body)) >= min_chars:
                return True
    return False


def readme(root):
    return read(root, "README.md", "README.rst")


def has_section(text, *words):
    heads = "\n".join(l for l in text.splitlines() if l.lstrip().startswith("#") or l.startswith("**"))
    return any(re.search(w, heads, re.IGNORECASE) for w in words)


def meta_of(root):
    return REGISTRY.get(root.name, {})


def ui_repo(root):
    return "ui" in meta_of(root)


def uses_llm(root):
    return grep(root, r"anthropic|openai|gemini|ollama|cloudflare.*ai|llm", (".py", ".ts", ".tsx")) if meta_of(root).get("kind") == "app" else False


def dependabot_ok(root):
    cfg = read(root, ".github/dependabot.yml", ".github/dependabot.yaml")
    if not cfg or "github-actions" not in cfg:
        return False
    need = set()
    if any(iter_files(root, ("requirements.txt", "pyproject.toml"))):
        need.add("pip")
    if any(iter_files(root, ("package.json",))):
        need.add("npm")
    return all(n in cfg for n in need)


def top_level_permissions(text):
    """(inline value, block lines) of the workflow-level `permissions:` key, or None if absent."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^permissions:\s*(.*)$", line)
        if m:
            block = []
            for nxt in lines[i + 1:]:
                if nxt.strip() and not nxt[0].isspace():
                    break
                block.append(nxt)
            return m.group(1).strip().strip("'\""), block
    return None


def job_blocks(text):
    """{job id: its lines} for the jobs under the top-level `jobs:` key (2-space job keys)."""
    jobs, current, inside = {}, None, False
    for line in text.splitlines():
        if re.match(r"^jobs:\s*$", line):
            inside = True
            continue
        if inside and line.strip() and not line[0].isspace():
            break  # next top-level key
        m = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line) if inside else None
        if m:
            current = m.group(1)
            jobs[current] = []
        elif current:
            jobs[current].append(line)
    return jobs


def all_workflows_have_permissions(root):
    """SEC-6: every workflow declares least-privilege permissions.

    Either workflow-level permissions that grant no write, or -- when there is no
    workflow-level key -- a `permissions:` on every job. write-all (quoted or not) fails
    anywhere; `<scope>: write` fails at workflow level, where it reaches every job.
    """
    d = root / ".github" / "workflows"
    if not d.is_dir():
        return True, "no workflows"
    for f in sorted(d.glob("*.y*ml")):
        text = COMMENT.sub("", f.read_text(encoding="utf-8", errors="replace"))
        if re.search(r"permissions:\s*['\"]?write-all\b", text):
            return False, f"{f.name}: write-all"
        top = top_level_permissions(text)
        if top is None:
            jobs = job_blocks(text)
            bare = [j for j, lines in jobs.items() if not any(re.match(r"^    permissions:", ln) for ln in lines)]
            if not jobs or bare:
                return False, f"{f.name}: no workflow-level permissions" + (f" and job(s) {', '.join(bare)} declare none" if bare else "")
            continue  # every job declares its own permissions: least privilege at job level
        inline, block = top
        if inline and inline not in ("read-all", "{}"):
            return False, f"{f.name}: workflow-level permissions: {inline}"
        writes = [b.strip() for b in block if re.search(r":\s*['\"]?write\b", b)]
        if writes:
            return False, f"{f.name}: workflow-level {', '.join(writes)} (move write scopes to the job)"
    return True, "every workflow declares least-privilege permissions (workflow-level read-only, or on every job)"


RUN_PREFIX = re.compile(r"^(?:\w+=\S*\s+)*(?:(?:uv|poetry|pipenv|hatch)\s+run\s+|python3?\s+-m\s+|npx\s+|bunx\s+|"
                        r"pnpm\s+(?:exec|dlx)\s+|yarn\s+dlx\s+|sudo\s+)*")


PR_TRIGGER = re.compile(r"^on:.*\bpull_request\b|^\s+pull_request(?:_target)?:|^\s*-\s*pull_request\b", re.MULTILINE)
SWALLOWED = re.compile(r"\|\|\s*(?:true|:|exit\s+0)\b")


def run_commands(root, pr_only=False):
    """Every command a workflow `run:` STEP executes (split on && || ; | and newlines), prefixes removed.

    Only real step-level `run:` keys count (not a `with:` input that happens to be called run),
    a command chain that cannot fail (`pytest || true`) does not count, and with pr_only only
    workflows triggered by pull_request are read.
    """
    d = root / ".github" / "workflows"
    cmds = []
    if not d.is_dir():
        return cmds
    for f in sorted(d.glob("*.y*ml")):
        text = COMMENT.sub("", f.read_text(encoding="utf-8", errors="replace"))
        if pr_only and not PR_TRIGGER.search(text):
            continue
        lines = text.splitlines()
        i, step_keys = 0, None  # indent of the current step's own keys
        while i < len(lines):
            dash = re.match(r"^(\s*)-\s+", lines[i])
            if dash:
                step_keys = len(dash.group(1)) + 2
            m = re.match(r"^(\s*)(-\s+)?run:\s*(.*)$", lines[i])
            if not m or (not m.group(2) and len(m.group(1)) != step_keys):
                i += 1
                continue
            body, indent = [m.group(3)], len(m.group(1))
            if m.group(3).strip() in ("|", ">", "|-", ">-", "|+", ">+"):
                body = []
                i += 1
                while i < len(lines) and (not lines[i].strip() or len(lines[i]) - len(lines[i].lstrip()) > indent):
                    body.append(lines[i])
                    i += 1
            else:
                i += 1
            for chain in re.split(r";|\n", "\n".join(body)):
                if SWALLOWED.search(chain):
                    continue  # `pytest || true` can never fail the job
                for part in re.split(r"&&|\|\||\|", chain):
                    c = RUN_PREFIX.sub("", part.strip().strip("'\""))
                    if c:
                        cmds.append(c)
    return cmds


def runs_tool(root, pattern):
    """A workflow `run:` command starts with one of these tools (not `echo pytest`)."""
    rx = re.compile(rf"^(?:{pattern})(?:\s|$)")
    return any(rx.match(c) for c in run_commands(root, pr_only=True))


def all_jobs_have_timeouts(root):
    d = root / ".github" / "workflows"
    if not d.is_dir():
        return True
    for f in d.glob("*.y*ml"):
        text = f.read_text(encoding="utf-8", errors="replace")
        if "workflow_call" in text and "uses:" in text and "runs-on" not in text:
            continue
        lines = COMMENT.sub("", text).splitlines()
        for i, line in enumerate(lines):
            m = re.match(r"^(\s+)runs-on:", line)
            if not m:
                continue
            indent = m.group(1)
            # the job's own keys share runs-on's indent; a step-level timeout does not count
            j = i - 1
            while j >= 0 and (not lines[j].strip() or lines[j].startswith(indent)):
                j -= 1
            k = i + 1
            while k < len(lines) and (not lines[k].strip() or lines[k].startswith(indent)):
                k += 1
            if not any(re.match(rf"^{indent}timeout-minutes:", l) for l in lines[j + 1:k]):
                return False
    return True


USES_REF = re.compile(r"^\s*-?\s*uses:\s*['\"]?([^\s'\"#]+)", re.MULTILINE)
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def uses_tool(root, *tools):
    """True iff a real `uses:` step's action path names one of the tools.

    A tool mentioned in a `run:` line, an env value or a step name is not a
    tool that runs -- only a `uses:` ref counts. (Issue #17, PR #21 verdict:
    substring search over workflow text passed `run: echo gitleaks`.)"""
    text = workflows(root)
    for m in USES_REF.finditer(text):
        segments = m.group(1).lower().split("@", 1)[0].split("/")
        if any(seg == t or seg.startswith(t + "-") for t in tools for seg in segments):
            return True
    return False


def unpinned_actions(root):
    """SEC-11 evidence: every workflow `uses:` ref that is not pinned by full SHA."""
    d = root / ".github" / "workflows"
    if not d.is_dir():
        return []
    bad = []
    for f in sorted(d.glob("*.y*ml")):
        for m in USES_REF.finditer(f.read_text(encoding="utf-8", errors="replace")):
            ref = m.group(1)
            if ref.startswith(("./", "docker://")):
                continue  # local actions and docker images are not remote action refs
            if "@" not in ref:
                bad.append(f"{f.name}: {ref} (no ref)")
            elif not FULL_SHA.match(ref.rsplit("@", 1)[1]):
                bad.append(f"{f.name}: {ref}")
    return bad


def actions_sha_pinned(root):
    d = root / ".github" / "workflows"
    if not d.is_dir() or not any(d.glob("*.y*ml")):
        return True, "no workflows"
    bad = unpinned_actions(root)
    if not bad:
        return True, "all action refs pinned by full-length SHA"
    shown = "; ".join(bad[:6]) + (f" (+{len(bad) - 6} more)" if len(bad) > 6 else "")
    return False, "unpinned: " + shown


def env_ok(root):
    if not grep(root, r"os\.environ|os\.getenv|process\.env|BaseSettings", (".py", ".ts", ".tsx", ".js")):
        return True
    ignore = read(root, ".gitignore")
    return any(iter_files(root, (".env.example",))) and ".env" in ignore


def lockfile_ok(root):
    """Every package manifest has a lockfile (or pinned requirements) next to it."""
    manifests = list(iter_files(root, ("package.json",))) + list(iter_files(root, ("pyproject.toml", "requirements.txt")))
    if not manifests:
        return True
    for m in manifests:
        d = m.parent
        if m.name == "package.json":
            if not any((d / l).exists() for l in ("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb")):
                return False
        elif m.name == "requirements.txt":
            lines = [l.strip() for l in m.read_text(encoding="utf-8", errors="replace").splitlines()
                     if l.strip() and not l.startswith(("#", "-"))]
            if lines and not all("==" in l for l in lines):
                return False
        elif m.name == "pyproject.toml":
            if (d / "requirements.txt").exists():
                continue  # judged by the requirements file above
            if not any((d / l).exists() for l in ("uv.lock", "poetry.lock", "pdm.lock", "requirements.lock")):
                return False
    return True


def bilingual(root):
    rd = readme(root)
    has_zh = bool(re.search(r"[一-鿿]", rd))
    has_en = bool(re.search(r"\b(the|and|with|for)\b", rd))
    return (has_zh and has_en) or exists(root, "README.zh-CN.md", "README.zh.md", "README.en.md", "en", "frontend/messages", "locales", "i18n")


# ----------------------------------------------------------------------------- live probes

class Probe:
    """One HTTP fetch, remembered per URL so several checks share it.

    ms = time to first response (status line + headers received, after redirects),
    not the time to download the body -- PERF-1 budgets the first response (首响).
    """
    # Process-wide memo by design (see class docstring); shared mutable state is the point.
    cache: dict[str, Probe] = {}  # noqa: RUF012

    def __init__(self, url):
        self.url, self.status, self.headers, self.ms, self.body, self.error = url, None, {}, None, b"", ""
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={"User-Agent": "vertciti-standards-audit/2.0 (+https://github.com/HUIIIM/.github)"})
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=LIVE["timeout"], context=ctx) as r:
                self.ms = round((time.monotonic() - t0) * 1000)
                self.body = r.read(400_000)
                self.status = r.status
                self.headers = {k.lower(): v for k, v in r.headers.items()}
        except urllib.error.HTTPError as e:
            self.status = e.code
            self.headers = {k.lower(): v for k, v in e.headers.items()} if e.headers else {}
            self.error = f"HTTP {e.code}"
        except (TimeoutError, urllib.error.URLError, ssl.SSLError, OSError) as e:
            self.error = str(getattr(e, "reason", e))[:120]
        if self.ms is None:  # error before or instead of a 2xx/3xx response
            self.ms = round((time.monotonic() - t0) * 1000)

    @classmethod
    def get(cls, url):
        if url not in cls.cache:
            cls.cache[url] = cls(url)
        return cls.cache[url]

    def evidence(self):
        return f"{self.url} -> {self.status or self.error} in {self.ms} ms"


def live_url(root):
    return meta_of(root).get("url", "")


def probe_ok(root):
    """REL-1: deployed URL answers 2xx (after redirects) within the timeout."""
    url = live_url(root)
    if not url:
        return None, "no url in repos.json (unprobed)"
    p = Probe.get(url)
    return (p.status is not None and 200 <= p.status < 400), p.evidence()


def health_ok(root):
    m = meta_of(root)
    url = m.get("health") or (m.get("url", "").rstrip("/") + "/healthz" if m.get("url") else "")
    if not url:
        return None, "no url (unprobed)"
    p = Probe.get(url)
    return (p.status == 200), p.evidence()


def live_headers_ok(root):
    """SEC-9: CSP + nosniff + frame protection + HSTS + referrer policy on the live site."""
    url = live_url(root)
    if not url:
        return None, "no url (unprobed)"
    p = Probe.get(url)
    if p.status is None:
        return False, p.evidence()
    h = p.headers
    want = {
        "content-security-policy": "content-security-policy" in h,
        "x-content-type-options": h.get("x-content-type-options", "").lower() == "nosniff",
        "frame": "x-frame-options" in h or "frame-ancestors" in h.get("content-security-policy", ""),
        "strict-transport-security": "strict-transport-security" in h,
        "referrer-policy": "referrer-policy" in h,
    }
    missing = [k for k, v in want.items() if not v]
    return (not missing), ("all five present" if not missing else "missing: " + ", ".join(missing))


def ttfb_ok(root):
    url = live_url(root)
    if not url:
        return None, "no url (unprobed)"
    p = Probe.get(url)
    if p.status is None:
        return False, p.evidence()
    return (p.ms <= 800), f"{p.ms} ms to first response (budget 800 ms)"


def discoverability_ok(root):
    """PUB-1 (sites): robots.txt, sitemap.xml and llms.txt all served."""
    url = live_url(root)
    if not url:
        return None, "no url (unprobed)"
    base = url.rstrip("/")
    missing = [f for f in ("robots.txt", "sitemap.xml", "llms.txt") if Probe.get(f"{base}/{f}").status != 200]
    return (not missing), ("all served" if not missing else "missing: " + ", ".join(missing))


def demo_link_ok(root):
    url = live_url(root)
    if not url:
        return False, "no public url registered"
    host = re.sub(r"^https?://", "", url).split("/")[0]
    return (host in readme(root)), f"README mentions {host}" if host in readme(root) else f"README does not mention {host}"


# ----------------------------------------------------------------------------- checks
# (id, level, kinds, statuses, description, check)
# check(root) -> bool | (bool|None, evidence). None = unprobed (counts as fail, labelled).
CHECKS = [
    # ---- governance (every repo) ----
    ("GOV-1", "MUST", ALL - {"profile", "meta"}, {"active", "archive", "placeholder"}, "LICENSE file present (or README states proprietary/pending)",
     lambda r: exists(r, "LICENSE", "LICENSE.md", "LICENSE.txt")),
    ("GOV-2", "MUST", ALL, {"active", "archive", "placeholder"}, "CODEOWNERS routes reviews",
     lambda r: exists(r, "CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS")),
    ("GOV-3", "SHOULD", ALL, {"active", "archive", "placeholder"}, ".editorconfig for consistent whitespace",
     lambda r: exists(r, ".editorconfig")),
    ("GOV-4", "MUST", ALL - {"profile", "meta"}, {"active"}, "Status is stated honestly in README (active/archive/early/etc.)",
     lambda r: bool(re.search(r"\b(status|archive[ds]?|early|experimental|stable|beta|alpha|phase)\b|状态|历史档案", readme(r)[:4000], re.IGNORECASE))),
    ("GOV-5", "MUST", ALL, {"archive"}, "Archive banner at top of README",
     lambda r: bool(re.search(r"历史档案|历史快照|archive|已封存", readme(r)[:1500], re.IGNORECASE))),
    ("GOV-6", "SHOULD", {"app", "library", "tool", "site"}, {"active"}, "SECURITY.md in repo (vulnerability reporting route, not only the org default)",
     lambda r: substantive(r, "SECURITY.md", ".github/SECURITY.md", "docs/SECURITY.md")),
    # ---- supply chain / security ----
    ("SEC-1", "MUST", ALL, {"active", "archive", "placeholder"}, "Secret scanning in CI (gitleaks or equivalent)",
     lambda r: uses_tool(r, "gitleaks", "trufflehog")),
    ("SEC-2", "MUST", ALL - {"profile"}, {"active"}, "Dependabot covers github-actions + every package ecosystem in repo",
     lambda r: dependabot_ok(r)),
    ("SEC-3", "MUST", CODE, {"active"}, "CodeQL / SAST runs on PRs",
     lambda r: uses_tool(r, "codeql-action")),
    ("SEC-4", "SHOULD", CODE, {"active"}, "Dependency review blocks vulnerable additions on PRs",
     lambda r: uses_tool(r, "dependency-review-action")),
    ("SEC-5", "SHOULD", ALL - {"profile"}, {"active"}, "OpenSSF Scorecard published",
     lambda r: uses_tool(r, "scorecard-action")),
    ("SEC-6", "MUST", ALL, {"active", "archive", "placeholder"}, "Workflows declare least-privilege `permissions:`",
     lambda r: all_workflows_have_permissions(r)),
    ("SEC-7", "SHOULD", CODE, {"active"}, ".env.example documents config; .env is git-ignored",
     lambda r: env_ok(r)),
    ("SEC-8", "MUST", ALL, {"active", "archive", "placeholder"}, "Workflows set timeout-minutes (no 6h runaway jobs)",
     lambda r: all_jobs_have_timeouts(r)),
    ("SEC-9", "SHOULD", {"app", "site"}, {"active"}, "[live] Security headers on the deployed site: CSP, nosniff, frame protection, HSTS, Referrer-Policy",
     live_headers_ok),
    ("SEC-10", "SHOULD", CODE, {"active"}, "Reproducible dependencies: lockfile or pinned requirements for every manifest",
     lambda r: lockfile_ok(r)),
    ("SEC-11", "MUST", ALL, {"active", "archive", "placeholder"}, "Every action referenced by a workflow is pinned by full-length commit SHA (no tag or branch pins)",
     actions_sha_pinned),
    # ---- quality ----
    ("QA-1", "MUST", CODE, {"active"}, "CI workflow runs tests on PRs",
     lambda r: runs_tool(r, r"pytest|vitest|jest|(?:npm|pnpm|yarn|bun) (?:run )?test|go test|cargo test|node --test|unittest|tox|nox|make test")),
    ("QA-2", "MUST", CODE, {"active"}, "Linter/formatter enforced in CI (ruff/eslint/biome/prettier)",
     lambda r: runs_tool(r, r"ruff|eslint|biome|prettier|flake8|black|(?:npm|pnpm|yarn|bun) (?:run )?lint|next lint")
     or bool(re.search(r"^\s*-?\s*uses:\s*['\"]?(?:astral-sh/ruff-action|biomejs/setup-biome|super-linter/)", workflows(r), re.MULTILINE))),
    ("QA-3", "SHOULD", CODE, {"active"}, "pre-commit hooks mirror CI",
     lambda r: exists(r, ".pre-commit-config.yaml")),
    ("QA-4", "SHOULD", {"app"}, {"active"}, "Type checking in CI (mypy/pyright/tsc)",
     lambda r: bool(re.search(r"mypy|pyright|tsc|typecheck|type-check", workflows(r) + read(r, "package.json", "frontend/package.json")))),
    ("QA-5", "SHOULD", {"app"}, {"active"}, "Browser-level test or contrast gate in CI (playwright / contrast)",
     lambda r: bool(re.search(r"playwright|contrast", workflows(r), re.IGNORECASE))),
    # ---- product kit / docs ----
    ("DOC-1", "MUST", ALL - {"meta", "profile", "docs"}, {"active"}, "README has a quickstart",
     lambda r: has_section(readme(r), r"quick ?start", r"快速开始", r"getting started", r"30 ?秒", r"30-second")),
    ("DOC-2", "MUST", {"app", "library", "skill", "tool"}, {"active"}, "Product one-pager docs/PRODUCT.md",
     lambda r: substantive(r, "docs/PRODUCT.md")),
    ("DOC-3", "MUST", {"app", "library", "skill", "tool"}, {"active"}, "CHANGELOG.md (Keep a Changelog)",
     lambda r: substantive(r, "CHANGELOG.md")),
    ("DOC-4", "SHOULD", {"app", "library", "tool"}, {"active"}, "Architecture doc or diagram",
     lambda r: substantive(r, "ARCHITECTURE.md", "docs/ARCHITECTURE.md", "docs/architecture.md") or exists(r, "docs/assets/architecture.png")),
    ("DOC-5", "SHOULD", {"app", "library", "skill", "tool"}, {"active"}, "Visual proof (screenshot/GIF) in README",
     lambda r: bool(re.search(r"!\[[^\]]*\]\([^)]+\.(png|gif|jpg|webp|svg)\)", readme(r)))),
    ("DOC-6", "MUST", ALL - {"profile", "meta"}, {"active"}, "README links back to vertciti.com",
     lambda r: "vertciti.com" in readme(r)),
    ("DOC-7", "SHOULD", {"app", "library", "skill", "tool"}, {"active"}, "README has security + license section",
     lambda r: has_section(readme(r), r"secur", r"安全") and has_section(readme(r), r"licen", r"许可")),
    ("DOC-8", "MUST", ALL - {"profile", "meta"}, {"active", "archive", "placeholder"}, "README is left-aligned (no align=center / <center>)",
     lambda r: not re.search(r"align=[\"']?center|<center>", readme(r), re.IGNORECASE)),
    ("DOC-9", "MUST", ALL - {"profile", "meta"}, {"active", "archive", "placeholder"}, "README has no badge strip (shields.io / badge.svg render as '?' in private repos and the mobile app)",
     lambda r: not re.search(r"img\.shields\.io|badge\.svg|badgen\.net", readme(r), re.IGNORECASE)),
    ("DOC-10", "MUST", ALL - {"profile", "meta"}, {"active", "archive", "placeholder"}, "README images are public https URLs (relative images break in private repos and the mobile app)",
     lambda r: not re.search(r"!\[[^\]]*\]\((?!https://)[^)]+\)|<img[^>]+src=[\"'](?!https://)", readme(r), re.IGNORECASE)),
    ("DOC-11", "SHOULD", {"app", "skill", "tool", "site"}, {"active"}, "Bilingual (zh + en) README or localised UI",
     lambda r: bilingual(r)),
    # ---- design (UI repos) ----
    ("UI-1", "MUST", {"app", "skill", "site"}, {"active"}, "Vendored vertciti DNA stylesheet (dna.css / dna-tailwind.css)",
     lambda r: ui_repo(r) is False or any(r.rglob("dna*.css"))),
    ("UI-2", "SHOULD", {"app", "site"}, {"active"}, "dna-drift check wired in CI (vendored DNA cannot silently diverge)",
     lambda r: ui_repo(r) is False or "dna-drift" in workflows(r)),
    # ---- ops / reliability (apps and sites) ----
    ("OPS-1", "MUST", {"app"}, {"active"}, "Health endpoint (/healthz or /health)",
     lambda r: grep(r, r"[\"'](/api)?(/v1)?/(healthz|health|livez|readyz)[\"']", (".py", ".ts", ".tsx", ".js"))),
    ("OPS-2", "SHOULD", {"app"}, {"active"}, "Container HEALTHCHECK or compose healthcheck",
     lambda r: not exists(r, "Dockerfile", "backend/Dockerfile", "docker-compose.yml") or grep(r, r"HEALTHCHECK|healthcheck:", ("Dockerfile", ".yml", ".yaml"))),
    ("OPS-3", "SHOULD", {"app"}, {"active"}, "Security response headers set in code (CSP / X-Content-Type-Options / frame-ancestors)",
     lambda r: grep(r, r"Content-Security-Policy|X-Content-Type-Options|frame-ancestors", (".py", ".ts", ".js", ".mjs", ".json"))),
    ("OPS-4", "SHOULD", {"app"}, {"active"}, "Container runs as non-root",
     lambda r: not exists(r, "Dockerfile", "backend/Dockerfile", "frontend/Dockerfile") or grep(r, r"^\s*USER\s+(?!root)", ("Dockerfile",))),
    ("OPS-5", "SHOULD", {"app"}, {"active"}, "Structured logs with a request/trace id (OpenTelemetry-style)",
     lambda r: grep(r, r"request_id|trace_id|structlog|JsonFormatter|json.*log|opentelemetry", (".py", ".ts", ".js"))),
    ("REL-1", "MUST", {"app", "site"}, {"active"}, "[live] Deployed URL answers (2xx/3xx) within 12 s",
     probe_ok),
    ("REL-2", "SHOULD", {"app"}, {"active"}, "[live] Health endpoint returns 200 on the deployment",
     health_ok),
    ("PERF-1", "SHOULD", {"app", "site"}, {"active"}, "[live] Landing response within 800 ms from the assessor",
     ttfb_ok),
    ("PUB-1", "SHOULD", {"site"}, {"active"}, "[live] robots.txt, sitemap.xml and llms.txt served (search + AI discoverability)",
     discoverability_ok),
    ("PUB-2", "SHOULD", {"app"}, {"active"}, "Public demo or product URL registered and named in README (outsiders can see it run)",
     demo_link_ok),
    # ---- continuity, privacy, AI, legal ----
    ("CONT-1", "SHOULD", {"app"}, {"active"}, "Runbook (docs/RUNBOOK.md): deploy, rollback, backup, restore, key rotation",
     lambda r: substantive(r, "docs/RUNBOOK.md", "RUNBOOK.md", "docs/ops/RUNBOOK.md", "deploy/RUNBOOK.md")),
    ("CONT-2", "SHOULD", {"app"}, {"active"}, "Backup and restore are written down (a restore never tested is not a backup)",
     lambda r: grep(r, r"restore|恢复演练|恢复步骤|backup|备份", ("RUNBOOK.md", "DOCKER_VERIFY.md", "DEPLOY.md", "MUSE-DEPLOY.md"))),
    ("PRIV-1", "SHOULD", {"app"}, {"active"}, "Data handling stated: retention / what is stored / redaction (PRIVACY.md or a section)",
     lambda r: exists(r, "PRIVACY.md", "docs/PRIVACY.md") or grep(r, r"retention|保留期|redact|脱敏|data handling|数据处理", ("SECURITY.md", "README.md", "PRODUCT.md"))),
    ("AI-1", "SHOULD", {"app"}, {"active"}, "LLM-using app has evals with recorded results (not claims)",
     lambda r: (not uses_llm(r)) or any(d.is_dir() and d.name in ("evals", "benchmarks") and not skipped(r, d) for d in r.rglob("*")) or grep(r, r"\beval(s|uation)?\b", ("CHANGELOG.md", "PRODUCT.md"))),
    ("AI-2", "SHOULD", {"app"}, {"active"}, "LLM-using app tests prompt-injection / untrusted-content handling",
     lambda r: (not uses_llm(r)) or grep(r, r"injection|untrusted|prompt.?inject", (".py", ".ts", ".tsx"))),
    ("LEGAL-1", "MUST", ALL - {"profile", "meta"}, {"active"}, "Third-party code copied into the repo (repos.json third_party) carries THIRD_PARTY_NOTICES / ATTRIBUTION",
     lambda r: (not meta_of(r).get("third_party")) or exists(r, "THIRD_PARTY_NOTICES.md", "ATTRIBUTION.md", "NOTICE", "NOTICE.md")),
]


# ----------------------------------------------------------------------------- scoring

def grade_of(score):
    for g, lo in GRADES:
        if score >= lo:
            return g
    return "C"


def audit(root, meta):
    kind, status = meta["kind"], meta["status"]
    results = []
    for cid, level, kinds, statuses, desc, fn in CHECKS:
        if kind not in kinds or status not in statuses:
            continue
        is_live = desc.startswith("[live]")
        if (is_live or cid == "PUB-2") and meta.get("public") is False:
            # Private deployment by design (repos.json "public": false): the live
            # checks do not apply. Recorded, not scored -- and the reason is shown.
            results.append({"id": cid, "level": level, "desc": desc, "ok": "n/a",
                            "evidence": "n/a: " + meta.get("public_reason", "private deployment by design")})
            continue
        if is_live and not LIVE["enabled"]:
            results.append({"id": cid, "level": level, "desc": desc, "ok": None, "evidence": "live probes disabled (run with --live)"})
            continue
        try:
            out = fn(root)
        except Exception as exc:  # noqa: BLE001 -- a broken check must not hide the rest of the report
            out = (False, f"check error: {exc}")
        ok, ev = (out if isinstance(out, tuple) else (bool(out), ""))
        results.append({"id": cid, "level": level, "desc": desc, "ok": ok, "evidence": ev})
    scored = [r for r in results if r["ok"] != "n/a"]
    earned = sum(WEIGHT[r["level"]] for r in scored if r["ok"] is True)
    possible = sum(WEIGHT[r["level"]] for r in scored) or 1
    score = round(earned / possible * 100, 1)
    must_fail = [r["id"] for r in scored if r["level"] == "MUST" and r["ok"] is not True]
    safety_fail = [r["id"] for r in scored if r["id"] in SAFETY_MUST and r["ok"] is False]  # measured failure, not "unprobed"
    unprobed = [r["id"] for r in scored if r["ok"] is None]
    severity = None
    if score < 70 or safety_fail:
        severity = "P0"
    elif score < 85 or must_fail:
        severity = "P1"
    elif score < BAR_MIN:
        severity = "P2"
    return {
        "repo": root.name, "kind": kind, "status": status, "product": meta.get("product", ""),
        "url": meta.get("url", ""), "score": score, "grade": grade_of(score), "bar": BAR,
        "meets_bar": score >= BAR_MIN and not must_fail,
        "severity": severity, "must_failing": must_fail, "unprobed": unprobed,
        "failing": [r["id"] for r in scored if r["ok"] is not True],
        "not_applicable": [r["id"] for r in results if r["ok"] == "n/a"],
        "checks": results,
    }


def missing_row(name, meta, base):
    """A registered repository the assessor could not read (clone failed, not found).

    It is not left out of the card: an unread repository is graded MISSING --
    score 0, grade C, severity P0 -- so the denominator stays the whole
    registry and the gap is published, never hidden (STANDARDS.md §考核 2).
    """
    return {
        "repo": name, "kind": meta["kind"], "status": meta["status"], "product": meta.get("product", ""),
        "url": meta.get("url", ""), "score": 0.0, "grade": "C", "bar": BAR, "meets_bar": False,
        "severity": "P0", "missing": True, "must_failing": ["MISSING"], "unprobed": [],
        "failing": ["MISSING"], "not_applicable": [],
        "checks": [{"id": "MISSING", "level": "MUST", "ok": False,
                    "desc": "Registered repository could not be read by the assessor (clone failed or not found): not graded, counted as failing",
                    "evidence": f"not found under {base}"}],
    }


def to_markdown(rows, generated):
    out = []
    out.append("# Portfolio scorecard · 组合记分卡\n")
    out.append(f"Generated {generated} by `standards/audit.py` (independent assessor; live probes {'on' if LIVE['enabled'] else 'off'}). "
               f"Bar = **{BAR}** (score ≥ {BAR_MIN} and no failing MUST). Below the bar is an incident with the severity shown. "
               f"Grades: S ≥95 · A++ ≥90 · A ≥85 · B ≥70 · C <70. Unprobed checks count as failed.\n")
    out.append("| repo | kind/status | score | grade | bar | incident | failing (MUST in bold) |")
    out.append("|---|---|---:|---|---|---|---|")
    for r in rows:
        fails = ", ".join((f"**{c}**" if c in r["must_failing"] else c) for c in r["failing"]) or "—"
        out.append(f"| {r['repo']} | {r['kind']}/{r['status']} | {r['score']} | {r['grade']} | {'✓' if r['meets_bar'] else '✗'} | {r['severity'] or '—'} | {fails} |")
    below = [r for r in rows if not r["meets_bar"]]
    missing = [r["repo"] for r in rows if r.get("missing")]
    out.append("")
    out.append(f"**{len(rows) - len(below)} of {len(rows)} at or above the bar; {len(below)} incident(s).**\n")
    if missing:
        out.append(f"**{len(missing)} registered repo(s) could not be read by the assessor and are graded MISSING "
                   f"(score 0, C, P0): {', '.join(missing)}.**\n")
    if below:
        out.append("## Incidents · 事故\n")
        for r in sorted(below, key=lambda x: (x["severity"], -x["score"])):
            out.append(f"### {r['severity']} · {r['repo']} · {r['score']} ({r['grade']})\n")
            for c in r["checks"]:
                if c["ok"] is not True and c["ok"] != "n/a":
                    state = "unprobed" if c["ok"] is None else "FAIL"
                    ev = f" — {c['evidence']}" if c["evidence"] else ""
                    out.append(f"- `{c['id']}` {c['level']} {state}: {c['desc']}{ev}")
            out.append("")
    return "\n".join(out)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    args = sys.argv[1:]
    base = Path(args[0]).expanduser()
    only = args[args.index("--only") + 1] if "--only" in args else None
    json_out = args[args.index("--json") + 1] if "--json" in args else None
    md = "--md" in args
    incidents = "--incidents" in args
    LIVE["enabled"] = "--live" in args
    generated = _dt.datetime.now(_dt.UTC).strftime("%Y-%m-%d %H:%MZ")

    rows, missing = [], []
    for name, meta in REGISTRY.items():
        if only and name != only:
            continue
        if meta["status"] == "fork":
            continue
        root = base / name
        if not root.is_dir():
            missing.append(name)
            print(f"{name}: not found under {base} -- graded MISSING (0, C, P0)", file=sys.stderr)
            rows.append(missing_row(name, meta, base))
            continue
        rows.append(audit(root, meta))

    failed_must = sum(len(r["must_failing"]) for r in rows)
    if json_out:
        Path(json_out).write_text(json.dumps({
            "generated": generated, "bar": BAR, "bar_min": BAR_MIN, "live": LIVE["enabled"],
            "grades": dict(GRADES), "weights": WEIGHT, "missing_repos": missing,
            "summary": {"repos": len(rows), "at_bar": sum(1 for r in rows if r["meets_bar"]),
                        "incidents": sum(1 for r in rows if not r["meets_bar"])},
            "repos": rows,
        }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if incidents:
        print(json.dumps([{k: r[k] for k in ("repo", "score", "grade", "severity", "must_failing", "failing", "unprobed")}
                          for r in rows if not r["meets_bar"]], ensure_ascii=False, indent=1))
    elif md:
        print(to_markdown(rows, generated))
    else:
        for r in rows:
            print(f"\n{r['repo']}  [{r['kind']}/{r['status']}]  {r['score']} {r['grade']}  "
                  f"{'at bar' if r['meets_bar'] else 'INCIDENT ' + r['severity']}")
            for c in r["checks"]:
                if c["ok"] is not True and c["ok"] != "n/a":
                    state = "?" if c["ok"] is None else "✗"
                    print(f"  {state} {c['id']:7} {c['level']:6} {c['desc']}" + (f"  [{c['evidence']}]" if c["evidence"] else ""))
    # 2 = registered repositories could not be read (the card is incomplete);
    # 1 = at least one MUST failing; 0 = clean.
    sys.exit(2 if missing else 1 if failed_must else 0)


if __name__ == "__main__":
    main()
