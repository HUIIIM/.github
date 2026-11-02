# Loop state — .github

Updated: 2026-11-01 (loop bootstrap). Facts here are the standing state;
when one changes, the PR that changes it updates this file.

## Direction channel

- Tasks: GitHub Issues labeled `jarvis-task` in this repo.
- Reviews and verdicts: PR comments only (off-repo documents do not count).
- Merge owner: Jarvis. External Claude opens PRs from `claude/*` branches.
- The standing `standards/daily-card` card PR is a bot card: its workflow
  run waits in `action_required` until approved via the fleet PAT, then
  merges on green through the normal channel.

## Decisions in force

- Verdicts bind to head SHAs: a merge requires a PASS verdict for the
  current head where a verdict regime applies; a new head voids coverage.
- The Claude GitHub App's repository selection covers every active own
  repo (20 repositories, verified 2026-11-01); new repos are added to the
  selection the day they are created.
- Branch protection: PR required, zero approving reviews required,
  required checks gitleaks + lint + typecheck (strict).

## Acceptance rules

- CI green on the current head (gitleaks, lint, typecheck).
- Registry or audit changes state their fleet-wide effect in the PR body.
