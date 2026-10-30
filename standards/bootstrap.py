#!/usr/bin/env python3
"""Bring a repository up to the vertciti baseline without touching what it already has.

    python3 standards/bootstrap.py ~/src/echowatch            # dry run: print the plan
    python3 standards/bootstrap.py ~/src/echowatch --write    # apply

What it does (all idempotent, never overwrites an existing file):
  * adds CODEOWNERS and .editorconfig
  * adds the standard gitleaks / scorecard / dependency-review / CodeQL workflows the repo's kind needs
  * creates or extends .github/dependabot.yml so every detected ecosystem + github-actions is covered
  * adds `timeout-minutes` to jobs that lack one and `permissions: contents: read` to workflows that lack it
  * pins every action given by tag or branch to the commit SHA of that same ref (git ls-remote),
    keeping the version it names (no silent major upgrades); refs it cannot resolve are reported

It does NOT write CHANGELOG.md, PRODUCT.md or a LICENSE: those need real content or a legal decision.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TPL = HERE / "templates"
REGISTRY = json.loads((HERE / "repos.json").read_text(encoding="utf-8"))["repos"]
SKIP = {".git", "node_modules", ".venv", "venv", ".next", "dist", "build", "__pycache__", "evidence"}
DEFAULT_TIMEOUT = 30
# `uses: owner/repo[/path]@ref` where ref is not already a full commit SHA (SEC-11 / SOTA SEC-A5).
# quoted or not: `uses: a/b@v1`, `uses: 'a/b@v1'`, `uses: "a/b@v1"`
USES_REF = re.compile(r"^(\s*-?\s*uses:\s*)(['\"]?)([A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+)@([^\s#'\"]+)\2([ \t]*#[^\n]*)?$",
                      re.MULTILINE)
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
_RESOLVED: dict = {}
_BRANCH_ONLY: set = set()  # (repo, ref) that exist only as a branch: a moving target, never pinned


def resolve_ref(repo, ref):
    """Commit SHA of the release tag `ref` of github.com/<repo>, or None.

    Annotated tags are peeled to their commit. Same tag -> same code: nothing is upgraded.
    A ref that exists only as a branch (`@main`) is NOT pinned: its head moves and
    Dependabot cannot keep a branch pin current. It is recorded and reported instead.
    """
    key = (repo, ref)
    if key not in _RESOLVED:
        sha = None
        try:
            out = subprocess.run(["git", "ls-remote", f"https://github.com/{repo}",
                                  f"refs/tags/{ref}", f"refs/tags/{ref}^{{}}", f"refs/heads/{ref}"],
                                 capture_output=True, text=True, timeout=30).stdout
            refs = dict(reversed(line.split("\t")) for line in out.splitlines() if "\t" in line)
            sha = refs.get(f"refs/tags/{ref}^{{}}") or refs.get(f"refs/tags/{ref}")
            if not sha and refs.get(f"refs/heads/{ref}"):
                _BRANCH_ONLY.add(key)
        except (OSError, subprocess.SubprocessError):
            sha = None
        _RESOLVED[key] = sha
    return _RESOLVED[key]


def pin_actions(text, resolve=resolve_ref):
    """Replace tag/branch refs with the SHA of that same ref; returns (text, pinned, unresolved)."""
    pinned, unresolved = [], []

    def sub(m):
        lead, _quote, action, ref, _comment = m.groups()
        if FULL_SHA.match(ref):
            return m.group(0)
        repo = "/".join(action.split("/")[:2])
        sha = resolve(repo, ref)
        if not sha:
            why = "branch ref, pin a release tag by hand" if (repo, ref) in _BRANCH_ONLY else "could not resolve"
            unresolved.append(f"({why}) {action}@{ref}")
            return m.group(0)
        pinned.append(f"{action}@{sha[:7]} ({ref})")
        return f"{lead}{action}@{sha} # {ref}"

    return USES_REF.sub(sub, text), pinned, unresolved


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


def harden_workflow(text, resolve=resolve_ref):
    changed = []
    text, pinned, unresolved = pin_actions(text, resolve)
    changed += [f"pin {p}" for p in pinned]
    changed += [f"UNPINNED {u}" for u in unresolved]
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
                # runs-on's value may be a block (list/map) on the following lines, so a new
                # job key goes BEFORE runs-on, at the job's own indent: always valid YAML.
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
                    out.insert(len(out) - 1, f"{indent}timeout-minutes: {DEFAULT_TIMEOUT}")
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
            for c in changed:
                if c.startswith("UNPINNED"):
                    print(f"WARN  {p.relative_to(root)}: {c} -- pin it by hand (SEC-11)", file=sys.stderr)
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
