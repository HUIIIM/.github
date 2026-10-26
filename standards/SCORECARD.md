# Portfolio scorecard · 组合记分卡

Generated 2026-10-26 09:22Z by `standards/audit.py` (independent assessor; live probes on). Bar = **A++** (score ≥ 90 and no failing MUST). Below the bar is an incident with the severity shown. Grades: S ≥95 · A++ ≥90 · A ≥85 · B ≥70 · C <70. Unprobed checks count as failed.

| repo | kind/status | score | grade | bar | incident | failing (MUST in bold) |
|---|---|---:|---|---|---|---|
| vertciti-chat | app/active | 70.0 | B | ✗ | P1 | SEC-7, SEC-9, QA-4, **DOC-2**, **DOC-3**, DOC-4, DOC-5, DOC-11, **UI-1**, UI-2, OPS-3, **REL-1**, REL-2, PERF-1, PUB-2, CONT-1, CONT-2, AI-1, AI-2 |
| vertciti-dealdesk | app/active | 83.3 | B | ✗ | P1 | SEC-7, **SEC-8**, SEC-10, **DOC-2**, **UI-1**, UI-2, PRIV-1, AI-1, AI-2 |
| phonehands | library/active | 54.7 | C | ✗ | P0 | **GOV-2**, GOV-3, GOV-6, **SEC-1**, **SEC-2**, **SEC-3**, SEC-4, SEC-5, **SEC-6**, SEC-7, SEC-10, **QA-2**, QA-3, **DOC-2**, DOC-5 |
| founder-visual-director | skill/active | 98.1 | S | ✓ | — | DOC-5 |
| think-tank | skill/active | 98.1 | S | ✓ | — | DOC-5 |
| website-qa-gates | skill/active | 98.1 | S | ✓ | — | DOC-5 |
| vertciti-security-watch | tool/active | 96.9 | S | ✓ | — | SEC-7, DOC-5 |
| Miao | docs/active | 71.1 | B | ✗ | P0 | **GOV-2**, GOV-3, **SEC-1**, **SEC-2**, SEC-5 |
| HUIIIM | profile/active | 100.0 | S | ✓ | — | — |
| .github | meta/active | 100.0 | S | ✓ | — | — |
| vertciti-sp07-builder | tool/archive | 75.0 | B | ✗ | P1 | **GOV-2**, GOV-3, **SEC-8** |

**6 of 11 at or above the bar; 5 incident(s).**

## Incidents · 事故

### P0 · Miao · 71.1 (B)

- `GOV-2` MUST FAIL: CODEOWNERS routes reviews
- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `SEC-1` MUST FAIL: Secret scanning in CI (gitleaks or equivalent)
- `SEC-2` MUST FAIL: Dependabot covers github-actions + every package ecosystem in repo
- `SEC-5` SHOULD FAIL: OpenSSF Scorecard published

### P0 · phonehands · 54.7 (C)

- `GOV-2` MUST FAIL: CODEOWNERS routes reviews
- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `GOV-6` SHOULD FAIL: SECURITY.md in repo (vulnerability reporting route, not only the org default)
- `SEC-1` MUST FAIL: Secret scanning in CI (gitleaks or equivalent)
- `SEC-2` MUST FAIL: Dependabot covers github-actions + every package ecosystem in repo
- `SEC-3` MUST FAIL: CodeQL / SAST runs on PRs
- `SEC-4` SHOULD FAIL: Dependency review blocks vulnerable additions on PRs
- `SEC-5` SHOULD FAIL: OpenSSF Scorecard published
- `SEC-6` MUST FAIL: Workflows declare least-privilege `permissions:`
- `SEC-7` SHOULD FAIL: .env.example documents config; .env is git-ignored
- `SEC-10` SHOULD FAIL: Reproducible dependencies: lockfile or pinned requirements for every manifest
- `QA-2` MUST FAIL: Linter/formatter enforced in CI (ruff/eslint/biome/prettier)
- `QA-3` SHOULD FAIL: pre-commit hooks mirror CI
- `DOC-2` MUST FAIL: Product one-pager docs/PRODUCT.md
- `DOC-5` SHOULD FAIL: Visual proof (screenshot/GIF) in README

### P1 · vertciti-dealdesk · 83.3 (B)

- `SEC-7` SHOULD FAIL: .env.example documents config; .env is git-ignored
- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)
- `SEC-10` SHOULD FAIL: Reproducible dependencies: lockfile or pinned requirements for every manifest
- `DOC-2` MUST FAIL: Product one-pager docs/PRODUCT.md
- `UI-1` MUST FAIL: Vendored vertciti DNA stylesheet (dna.css / dna-tailwind.css)
- `UI-2` SHOULD FAIL: dna-drift check wired in CI (vendored DNA cannot silently diverge)
- `PRIV-1` SHOULD FAIL: Data handling stated: retention / what is stored / redaction (PRIVACY.md or a section)
- `AI-1` SHOULD FAIL: LLM-using app has evals with recorded results (not claims)
- `AI-2` SHOULD FAIL: LLM-using app tests prompt-injection / untrusted-content handling

### P1 · vertciti-sp07-builder · 75.0 (B)

- `GOV-2` MUST FAIL: CODEOWNERS routes reviews
- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)

### P1 · vertciti-chat · 70.0 (B)

- `SEC-7` SHOULD FAIL: .env.example documents config; .env is git-ignored
- `SEC-9` SHOULD unprobed: [live] Security headers on the deployed site: CSP, nosniff, frame protection, HSTS, Referrer-Policy — no url (unprobed)
- `QA-4` SHOULD FAIL: Type checking in CI (mypy/pyright/tsc)
- `DOC-2` MUST FAIL: Product one-pager docs/PRODUCT.md
- `DOC-3` MUST FAIL: CHANGELOG.md (Keep a Changelog)
- `DOC-4` SHOULD FAIL: Architecture doc or diagram
- `DOC-5` SHOULD FAIL: Visual proof (screenshot/GIF) in README
- `DOC-11` SHOULD FAIL: Bilingual (zh + en) README or localised UI
- `UI-1` MUST FAIL: Vendored vertciti DNA stylesheet (dna.css / dna-tailwind.css)
- `UI-2` SHOULD FAIL: dna-drift check wired in CI (vendored DNA cannot silently diverge)
- `OPS-3` SHOULD FAIL: Security response headers set in code (CSP / X-Content-Type-Options / frame-ancestors)
- `REL-1` MUST unprobed: [live] Deployed URL answers (2xx/3xx) within 12 s — no url in repos.json (unprobed)
- `REL-2` SHOULD unprobed: [live] Health endpoint returns 200 on the deployment — no url (unprobed)
- `PERF-1` SHOULD unprobed: [live] Landing response within 800 ms from the assessor — no url (unprobed)
- `PUB-2` SHOULD FAIL: Public demo or product URL registered and named in README (outsiders can see it run) — no public url registered
- `CONT-1` SHOULD FAIL: Runbook (docs/RUNBOOK.md): deploy, rollback, backup, restore, key rotation
- `CONT-2` SHOULD FAIL: Backup and restore are written down (a restore never tested is not a backup)
- `AI-1` SHOULD FAIL: LLM-using app has evals with recorded results (not claims)
- `AI-2` SHOULD FAIL: LLM-using app tests prompt-injection / untrusted-content handling

