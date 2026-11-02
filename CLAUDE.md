# .github

Organization profile repository and the fleet standards engine: the
standards audit (`standards/audit.py`), the repository registry
(`standards/repos.json`), and the daily standards card automation.

## How work happens here

- Direction arrives in-repo: GitHub Issues labeled `jarvis-task`, PR review
  comments, and the committed files `CLAUDE.md` (this file) and `LOOP.md`.
  Read both at session start.
- External Claude (Claude Code web) works on `claude/*` branches and opens
  PRs. It never merges its own PRs.
- Jarvis reviews, gates, and merges. Review verdicts exist only as PR
  comments — off-repo documents cannot create, amend, or void a verdict
  (charter: `IVV.md`).
- When a change alters a fact stated in `CLAUDE.md` or `LOOP.md`, update the
  file in the same PR.

## Repository map

- `standards/` — audit engine, registry (`repos.json`), generated cards.
- `profile/` — organization profile surfaces.
- Workflows: gitleaks, lint, typecheck (all three are required checks).

## Working rules

- `standards/repos.json` is the fleet registry: every own non-fork repo is
  listed, and the audit reads it as ground truth. Keep it current in the
  same PR that creates or retires a repo.
- The standards audit is fail-loud: an unreadable registered repo fails the
  run and files/updates its incident issue. Never silence a read failure.
- Licensing is dual (see `LICENSE`): brand/profile content all rights
  reserved; standalone code files MIT.
- Never delete `__pycache__` artifacts tracked under `standards/` as
  cleanup; they are part of the tracked tree here.
