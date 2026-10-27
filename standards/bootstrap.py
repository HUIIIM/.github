#!/usr/bin/env python3
"""Bring a repository up to the vertciti baseline without touching what it already has.

    python3 standards/bootstrap.py ~/src/echowatch            # dry run: print the plan
    python3 standards/bootstrap.py ~/src/echowatch --write    # apply

What it does (all idempotent, never overwrites an existing file):
  * adds CODEOWNERS and .editorconfig
  * adds the standard gitleaks / scorecard / dependency-review / CodeQL workflows the repo's kind needs
  * creates or extends .github/dependabot.yml so every detected ecosystem + github-actions is covered
  * adds `timeout-minutes` to jobs that lack one and `permissions: contents: read` to workflows that lack it
  * pins core actions given by tag (checkout / setup-python / setup-node @vN) to the v7 commit SHA

It does NOT write CHANGELOG.md, PRODUCT.md or a LICENSE: those need real content or a legal decision.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TPL = HERE / "templates"
REGISTRY = json.loads((HERE / "repos.json").read_text(encoding="utf-8"))["repos"]
SKIP = {".git", "node_modules", ".venv", "venv", ".next", "dist", "build", "__pycache__", "evidence"}
# Core actions pinned to a full commit SHA (SOTA.md SEC-A5); the trailing comment names the
# release so Dependabot can keep the pin current. Same pins as standards/templates/workflows.
ACTION_PINS = {
    "actions/checkout": ("3d3c42e5aac5ba805825da76410c181273ba90b1", "v7"),
    "actions/setup-python": ("6d4fd22b20465ccc0f7354476588e8df7c9ca0e0", "v7"),
    "actions/setup-node": ("949feb2413d6458794dcd2491c4babbbce0c15c1", "v7"),
}
DEFAULT_TIMEOUT = 30


def files(root, names):
    for p in root.rglob("*"):
        if p.is_file() and p.name in names and not any(s in p.relative_to(root).parts for s in SKIP):
            yield p


def ecosystems(root):
    """(ecosystem, directory) pairs, one per manifest location.

    npm is keyed on lockfiles, so a workspace monorepo yields one entry, not one per package.
    Paths listed in repos.json `vendored` (copied third-party/legacy code) are skipped.
    """
    vendored = tuple(REGISTRY.get(root.name, {}).get("vendored", []))
    found = []
    for name, eco in (("requirements.txt", "pip"), ("pyproject.toml", "pip"), ("package-lock.json", "npm"),
                      ("pnpm-lock.yaml", "npm"), ("yarn.lock", "npm"), ("Dockerfile", "docker")):
        for p in files(root, {name}):
            if str(p.relative_to(root)).startswith(vendored) if vendored else False:
                continue
            rel = p.parent.relative_to(root).as_posix()
            d = "/" if rel == "." else "/" + rel
            if (eco, d) not in found:
                found.append((eco, d))
    found.append(("github-actions", "/"))
    return found


def dependabot_entry(eco, directory):
    group = "" if eco in ("docker", "github-actions") else (
        "    groups:\n      minor-and-patch:\n        update-types: [\"minor\", \"patch\"]\n")
    return (f"  - package-ecosystem: \"{eco}\"\n    directory: \"{directory}\"\n    schedule:\n      interval: \"weekly\"\n"
            f"    labels: [\"dependencies\"]\n    open-pull-requests-limit: 5\n{group}")


def plan_dependabot(root):
    path = root / ".github" / "dependabot.yml"
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    missing = []
    for eco, d in ecosystems(root):
        pattern = rf'package-ecosystem:\s*"?{re.escape(eco)}"?\s*\n\s*directory:\s*"?{re.escape(d)}"?\s*\n'
        if not re.search(pattern, current):
            missing.append((eco, d))
    if not missing:
        return None
    body = current or "version: 2\nupdates:\n"
    if body and not body.endswith("\n"):
        body += "\n"
    body += "".join(dependabot_entry(e, d) for e, d in missing)
    return path, body, f"dependabot: add {', '.join(f'{e}:{d}' for e, d in missing)}"


def harden_workflow(text):
    changed = []
    for action, (sha, ver) in ACTION_PINS.items():
        new = re.sub(rf"({re.escape(action)})@v\d+(\.\d+)*\b([ \t]*#[^\n]*)?", rf"\1@{sha} # {ver}", text)
        if new != text:
            changed.append(f"{action}@{sha[:7]} ({ver})")
            text = new
    if "workflow_call" not in text or "runs-on" in text:
        if not re.search(r"^permissions:", text, re.MULTILINE):
            text = re.sub(r"^jobs:", "permissions:\n  contents: read\njobs:", text, count=1, flags=re.MULTILINE)
            changed.append("permissions: contents: read")
        lines, out = text.split("\n"), []
        i = 0
        while i < len(lines):
            line = lines[i]
            out.append(line)
            m = re.match(r"^(\s+)runs-on:", line)
            if m:
                indent = m.group(1)
                # look ahead inside this job for an existing timeout
                j, has = i + 1, False
                while j < len(lines) and (lines[j].startswith(indent) or not lines[j].strip()):
                    if re.match(rf"^{indent}timeout-minutes:", lines[j]):
                        has = True
                    if re.match(rf"^{indent[:-2]}\S", lines[j]) and indent[:-2]:
                        break
                    j += 1
                # also check lines above (timeout may precede runs-on)
                k = len(out) - 2
                while k >= 0 and out[k].startswith(indent):
                    if re.match(rf"^{indent}timeout-minutes:", out[k]):
                        has = True
                    k -= 1
                if not has:
                    out.append(f"{indent}timeout-minutes: {DEFAULT_TIMEOUT}")
                    changed.append("timeout-minutes")
            i += 1
        text = "\n".join(out)
    return text, changed


def codeql_languages(root):
    langs = []
    if any(files(root, {"requirements.txt", "pyproject.toml"})) or any(root.rglob("*.py")):
        langs.append("python")
    if any(files(root, {"package.json"})):
        langs.append("javascript-typescript")
    return langs


def plan(root):
    meta = REGISTRY.get(root.name, {"kind": "app", "status": "active"})
    kind, status = meta["kind"], meta["status"]
    if status == "fork":
        return []
    actions = []

    def add(rel, content, why):
        p = root / rel
        if not p.exists():
            actions.append((p, content, why))

    add(".github/CODEOWNERS", (TPL / "CODEOWNERS").read_text(encoding="utf-8"), "CODEOWNERS (GOV-2)")
    add(".editorconfig", (TPL / "editorconfig").read_text(encoding="utf-8"), ".editorconfig (GOV-3)")

    wf = root / ".github" / "workflows"
    existing = "\n".join(p.read_text(encoding="utf-8") for p in wf.glob("*.y*ml")) if wf.is_dir() else ""
    if "gitleaks" not in existing:
        add(".github/workflows/gitleaks.yml", (TPL / "workflows/gitleaks.yml").read_text(encoding="utf-8"), "secret scan (SEC-1)")
    if status == "active" and kind != "profile":
        if "scorecard-action" not in existing:
            add(".github/workflows/scorecard.yml", (TPL / "workflows/scorecard.yml").read_text(encoding="utf-8"), "OpenSSF Scorecard (SEC-5)")
        if kind in ("app", "library", "tool"):
            if "dependency-review-action" not in existing:
                add(".github/workflows/dependency-review.yml", (TPL / "workflows/dependency-review.yml").read_text(encoding="utf-8"), "dependency review (SEC-4)")
            langs = codeql_languages(root)
            if "codeql-action/init" not in existing and langs:
                body = (TPL / "workflows/codeql.yml").read_text(encoding="utf-8").replace("__LANGUAGES__", ", ".join(langs))
                add(".github/workflows/codeql.yml", body, f"CodeQL {langs} (SEC-3)")
        dep = plan_dependabot(root)
        if dep:
            actions.append(dep)

    if wf.is_dir():
        for p in sorted(wf.glob("*.y*ml")):
            text = p.read_text(encoding="utf-8")
            new, changed = harden_workflow(text)
            if new != text:
                actions.append((p, new, f"harden {p.name}: {', '.join(sorted(set(changed)))}"))
    return actions


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    root = Path(sys.argv[1]).expanduser().resolve()
    write = "--write" in sys.argv
    acts = plan(root)
    for p, content, why in acts:
        print(("WRITE " if write else "PLAN  ") + f"{p.relative_to(root)}  — {why}")
        if write:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content if content.endswith("\n") else content + "\n", encoding="utf-8")
    if not acts:
        print("baseline already satisfied")


if __name__ == "__main__":
    main()
