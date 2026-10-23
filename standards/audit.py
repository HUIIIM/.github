#!/usr/bin/env python3
"""Audit local clones of the portfolio against STANDARDS.md.

    python3 standards/audit.py ~/src            # every repo in repos.json found under ~/src
    python3 standards/audit.py ~/src --md        # markdown table (for PRs / reports)
    python3 standards/audit.py ~/src --only echowatch

Read-only. Exit code 1 when any applicable MUST check fails.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTRY = json.loads((HERE / "repos.json").read_text(encoding="utf-8"))["repos"]

ALL = {"app", "library", "skill", "tool", "site", "docs", "profile", "meta"}
CODE = {"app", "library", "tool"}


def exists(root, *paths):
    return any((root / p).exists() for p in paths)


def read(root, *paths):
    for p in paths:
        f = root / p
        if f.is_file():
            return f.read_text(encoding="utf-8", errors="replace")
    return ""


def workflows(root):
    d = root / ".github" / "workflows"
    return "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in sorted(d.glob("*.y*ml"))) if d.is_dir() else ""


def readme(root):
    return read(root, "README.md", "README.rst")


def has_section(text, *words):
    heads = "\n".join(l for l in text.splitlines() if l.lstrip().startswith("#") or l.startswith("**"))
    return any(re.search(w, heads, re.I) for w in words)


# (id, level, kinds, statuses, description, check)
CHECKS = [
    # ---- governance (every repo) ----
    ("GOV-1", "MUST", ALL - {"profile", "meta"}, {"active", "archive", "placeholder"}, "LICENSE file present (or README states proprietary/pending)",
     lambda r: exists(r, "LICENSE", "LICENSE.md", "LICENSE.txt")),
    ("GOV-2", "MUST", ALL, {"active", "archive", "placeholder"}, "CODEOWNERS routes reviews",
     lambda r: exists(r, "CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS")),
    ("GOV-3", "SHOULD", ALL, {"active", "archive", "placeholder"}, ".editorconfig for consistent whitespace",
     lambda r: exists(r, ".editorconfig")),
    ("GOV-4", "MUST", ALL - {"profile", "meta"}, {"active"}, "Status is stated honestly in README (active/archive/early/etc.)",
     lambda r: bool(re.search(r"status|状态|历史档案|archive|early|experimental|stable|beta|alpha|phase", readme(r)[:4000], re.I))),
    ("GOV-5", "MUST", ALL, {"archive"}, "Archive banner at top of README",
     lambda r: bool(re.search(r"历史档案|历史快照|archive|已封存", readme(r)[:1500], re.I))),
    # ---- supply chain / security ----
    ("SEC-1", "MUST", ALL, {"active", "archive", "placeholder"}, "Secret scanning in CI (gitleaks or equivalent)",
     lambda r: "gitleaks" in workflows(r) or "trufflehog" in workflows(r)),
    ("SEC-2", "MUST", ALL - {"profile"}, {"active"}, "Dependabot covers github-actions + every package ecosystem in repo",
     lambda r: dependabot_ok(r)),
    ("SEC-3", "MUST", CODE, {"active"}, "CodeQL / SAST runs on PRs",
     lambda r: "codeql-action" in workflows(r)),
    ("SEC-4", "SHOULD", CODE, {"active"}, "Dependency review blocks vulnerable additions on PRs",
     lambda r: "dependency-review-action" in workflows(r)),
    ("SEC-5", "SHOULD", ALL - {"profile"}, {"active"}, "OpenSSF Scorecard published",
     lambda r: "scorecard-action" in workflows(r)),
    ("SEC-6", "MUST", ALL, {"active", "archive", "placeholder"}, "Workflows declare least-privilege `permissions:`",
     lambda r: all_workflows_have_permissions(r)),
    ("SEC-7", "SHOULD", CODE, {"active"}, ".env.example documents config; .env is git-ignored",
     lambda r: env_ok(r)),
    ("SEC-8", "MUST", ALL, {"active", "archive", "placeholder"}, "Workflows set timeout-minutes (no 6h runaway jobs)",
     lambda r: all_jobs_have_timeouts(r)),
    # ---- quality ----
    ("QA-1", "MUST", CODE, {"active"}, "CI workflow runs tests on PRs",
     lambda r: bool(re.search(r"pytest|vitest|npm (run )?test|jest|go test|cargo test|node --test", workflows(r)))),
    ("QA-2", "MUST", CODE, {"active"}, "Linter/formatter enforced in CI (ruff/eslint/biome/prettier)",
     lambda r: bool(re.search(r"ruff|eslint|biome|prettier|flake8|black|npm run lint", workflows(r)))),
    ("QA-3", "SHOULD", CODE, {"active"}, "pre-commit hooks mirror CI",
     lambda r: exists(r, ".pre-commit-config.yaml")),
    ("QA-4", "SHOULD", {"app"}, {"active"}, "Type checking in CI (mypy/pyright/tsc)",
     lambda r: bool(re.search(r"mypy|pyright|tsc|typecheck|type-check", workflows(r) + read(r, "package.json", "frontend/package.json")))),
    # ---- product kit / docs ----
    ("DOC-1", "MUST", ALL - {"meta", "profile", "docs"}, {"active"}, "README has a quickstart",
     lambda r: has_section(readme(r), r"quick ?start", r"快速开始", r"getting started", r"30 ?秒", r"30-second")),
    ("DOC-2", "MUST", {"app", "library", "skill", "tool"}, {"active"}, "Product one-pager docs/PRODUCT.md",
     lambda r: exists(r, "docs/PRODUCT.md")),
    ("DOC-3", "MUST", {"app", "library", "skill", "tool"}, {"active"}, "CHANGELOG.md (Keep a Changelog)",
     lambda r: exists(r, "CHANGELOG.md")),
    ("DOC-4", "SHOULD", {"app", "library", "tool"}, {"active"}, "Architecture doc or diagram",
     lambda r: exists(r, "ARCHITECTURE.md", "docs/ARCHITECTURE.md", "docs/architecture.md", "docs/assets/architecture.png")),
    ("DOC-5", "SHOULD", {"app", "library", "skill", "tool"}, {"active"}, "Visual proof (screenshot/GIF) in README",
     lambda r: bool(re.search(r"!\[[^\]]*\]\([^)]+\.(png|gif|jpg|webp|svg)\)", readme(r)))),
    ("DOC-6", "MUST", ALL - {"profile", "meta"}, {"active"}, "README links back to vertciti.com",
     lambda r: "vertciti.com" in readme(r)),
    ("DOC-7", "SHOULD", {"app", "library", "skill", "tool"}, {"active"}, "README has security + license section",
     lambda r: has_section(readme(r), r"secur", r"安全") and has_section(readme(r), r"licen", r"许可")),
    ("DOC-8", "MUST", ALL - {"profile", "meta"}, {"active", "archive", "placeholder"}, "README is left-aligned (no align=center / <center>)",
     lambda r: not re.search(r"align=[\"']?center|<center>", readme(r), re.I)),
    ("DOC-9", "MUST", ALL - {"profile", "meta"}, {"active", "archive", "placeholder"}, "README has no badge strip (shields.io / badge.svg render as '?' in private repos and the mobile app)",
     lambda r: not re.search(r"img\.shields\.io|badge\.svg|badgen\.net", readme(r), re.I)),
    ("DOC-10", "MUST", ALL - {"profile", "meta"}, {"active", "archive", "placeholder"}, "README images are public https URLs (relative images break in private repos and the mobile app)",
     lambda r: not re.search(r"!\[[^\]]*\]\((?!https://)[^)]+\)|<img[^>]+src=[\"'](?!https://)", readme(r), re.I)),
    # ---- design (UI repos) ----
    ("UI-1", "MUST", {"app", "skill", "site"}, {"active"}, "Vendored vertciti DNA stylesheet (dna.css / dna-tailwind.css)",
     lambda r: ui_repo(r) is False or any(r.rglob("dna*.css"))),
    # ---- ops (apps) ----
    ("OPS-1", "MUST", {"app"}, {"active"}, "Health endpoint (/healthz or /health)",
     lambda r: grep(r, r"[\"'](/api)?(/v1)?/(healthz|health|livez|readyz)[\"']", (".py", ".ts", ".tsx", ".js"))),
    ("OPS-2", "SHOULD", {"app"}, {"active"}, "Container HEALTHCHECK or compose healthcheck",
     lambda r: not exists(r, "Dockerfile", "backend/Dockerfile", "docker-compose.yml") or grep(r, r"HEALTHCHECK|healthcheck:", ("Dockerfile", ".yml", ".yaml"))),
    ("OPS-3", "SHOULD", {"app"}, {"active"}, "Security response headers set (CSP / X-Content-Type-Options / frame-ancestors)",
     lambda r: grep(r, r"Content-Security-Policy|X-Content-Type-Options|frame-ancestors", (".py", ".ts", ".js", ".mjs", ".json"))),
    ("OPS-4", "SHOULD", {"app"}, {"active"}, "Container runs as non-root",
     lambda r: not exists(r, "Dockerfile", "backend/Dockerfile", "frontend/Dockerfile") or grep(r, r"^\s*USER\s+(?!root)", ("Dockerfile",))),
]

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", ".next", "dist", "build", "__pycache__", "evidence"}


def iter_files(root, suffixes):
    for p in root.rglob("*"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.is_file() and (p.name in suffixes or p.suffix in suffixes):
            yield p


def grep(root, pattern, suffixes):
    rx = re.compile(pattern, re.M)
    for p in iter_files(root, suffixes):
        try:
            if rx.search(p.read_text(encoding="utf-8", errors="replace")):
                return True
        except OSError:
            continue
    return False


def ui_repo(root):
    name = root.name
    return "ui" in REGISTRY.get(name, {})


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


def all_workflows_have_permissions(root):
    d = root / ".github" / "workflows"
    if not d.is_dir():
        return True
    return all(re.search(r"^\s*permissions:", f.read_text(encoding="utf-8", errors="replace"), re.M) for f in d.glob("*.y*ml"))


def all_jobs_have_timeouts(root):
    d = root / ".github" / "workflows"
    if not d.is_dir():
        return True
    for f in d.glob("*.y*ml"):
        text = f.read_text(encoding="utf-8", errors="replace")
        if "workflow_call" in text and "uses:" in text and "runs-on" not in text:
            continue
        runs = len(re.findall(r"^\s+runs-on:", text, re.M))
        timeouts = len(re.findall(r"^\s+timeout-minutes:", text, re.M))
        if timeouts < runs:
            return False
    return True


def env_ok(root):
    if not grep(root, r"os\.environ|os\.getenv|process\.env|BaseSettings", (".py", ".ts", ".tsx", ".js")):
        return True
    ignore = read(root, ".gitignore")
    return any(iter_files(root, (".env.example",))) and ".env" in ignore


def audit(root, meta):
    kind, status = meta["kind"], meta["status"]
    results = []
    for cid, level, kinds, statuses, desc, fn in CHECKS:
        if kind not in kinds or status not in statuses:
            continue
        try:
            ok = bool(fn(root))
        except Exception as exc:  # a broken check must not hide the rest of the report
            ok = False
            desc += f" (check error: {exc})"
        results.append((cid, level, desc, ok))
    return results


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    base = Path(sys.argv[1]).expanduser()
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    md = "--md" in sys.argv
    failed_must = 0
    if md:
        print("| repo | kind/status | MUST | SHOULD | failing |\n|---|---|---|---|---|")
    for name, meta in REGISTRY.items():
        if only and name != only:
            continue
        if meta["status"] == "fork":
            continue
        root = base / name
        if not root.is_dir():
            print(f"{name}: not found under {base}", file=sys.stderr)
            continue
        res = audit(root, meta)
        must = [r for r in res if r[1] == "MUST"]
        should = [r for r in res if r[1] == "SHOULD"]
        fails = [r for r in res if not r[3]]
        failed_must += sum(1 for r in must if not r[3])
        score_m = f"{sum(r[3] for r in must)}/{len(must)}"
        score_s = f"{sum(r[3] for r in should)}/{len(should)}"
        if md:
            print(f"| {name} | {meta['kind']}/{meta['status']} | {score_m} | {score_s} | {', '.join(r[0] for r in fails) or '—'} |")
        else:
            print(f"\n{name}  [{meta['kind']}/{meta['status']}]  MUST {score_m}  SHOULD {score_s}")
            for cid, level, desc, ok in fails:
                print(f"  ✗ {cid:6} {level:6} {desc}")
    sys.exit(1 if failed_must else 0)


if __name__ == "__main__":
    main()
