# Portfolio scorecard · 组合记分卡

Generated 2026-11-02 11:41Z by `standards/audit.py` (independent assessor; live probes on). Bar = **A++** (score ≥ 90 and no failing MUST). Below the bar is an incident with the severity shown. Grades: S ≥95 · A++ ≥90 · A ≥85 · B ≥70 · C <70. Unprobed checks count as failed.

| repo | kind/status | score | grade | bar | incident | failing (MUST in bold) |
|---|---|---:|---|---|---|---|
| miao-ai | app/active | 96.5 | S | ✗ | P0 | **SEC-6** |
| vertciti-translator | app/active | 91.4 | A++ | ✓ | — | DOC-11, UI-2, OPS-5, REL-2, PERF-1, CONT-1, PRIV-1, AI-1 |
| vertciti-chat | app/active | 73.1 | B | ✗ | P1 | SEC-7, SEC-9, QA-4, **DOC-2**, **DOC-3**, DOC-4, DOC-5, DOC-11, **UI-1**, UI-2, OPS-3, **REL-1**, REL-2, PERF-1, PUB-2, CONT-1, CONT-2 |
| echowatch | app/active | 65.6 | C | ✗ | P0 | **SEC-1**, SEC-4, SEC-5, **SEC-6**, **SEC-8**, SEC-9, SEC-10, QA-3, QA-4, **DOC-2**, **UI-1**, UI-2, **REL-1**, REL-2, PERF-1, PUB-2, CONT-1, CONT-2, AI-1, AI-2 |
| vertciti-dealdesk | app/active | 82.8 | B | ✗ | P0 | **SEC-6**, SEC-7, **SEC-8**, SEC-10, **DOC-2**, **UI-1**, UI-2, PRIV-1 |
| phonehands | library/active | 67.2 | C | ✗ | P0 | GOV-3, **SEC-1**, **SEC-2**, **SEC-3**, SEC-4, SEC-5, SEC-7, SEC-10, **QA-2**, QA-3, **DOC-2**, DOC-5 |
| founder-visual-director | skill/active | 92.9 | A++ | ✗ | P1 | **SEC-8**, DOC-5 |
| think-tank | skill/active | 98.2 | S | ✓ | — | DOC-5 |
| website-qa-gates | skill/active | 98.2 | S | ✓ | — | DOC-5 |
| vertciti-security-watch | tool/active | 97.1 | S | ✓ | — | SEC-7, DOC-5 |
| vertciti-website | site/active | 78.6 | B | ✗ | P0 | **GOV-1**, **SEC-2**, **SEC-6**, **DOC-1** |
| fama | app/active | 58.1 | C | ✗ | P0 | GOV-3, **SEC-1**, **SEC-3**, SEC-4, SEC-5, **SEC-6**, SEC-7, **SEC-8**, SEC-9, QA-3, QA-5, **DOC-1**, **DOC-2**, DOC-4, DOC-5, **DOC-6**, DOC-7, **REL-1**, REL-2, PERF-1, PUB-2, CONT-1, CONT-2 |
| Miao | docs/active | 90.2 | A++ | ✗ | P0 | **SEC-1**, SEC-5 |
| HUIIIM | profile/active | 81.2 | B | ✗ | P1 | **SEC-8** |
| vault-app | app/active | 0.0 | C | ✗ | P0 | **MISSING** |
| jarvis-architecture | library/active | 0.0 | C | ✗ | P0 | **MISSING** |
| .github | meta/active | 85.0 | A | ✗ | P1 | **SEC-8** |
| operator-session-permissions | skill/active | 53.6 | C | ✗ | P0 | **GOV-2**, GOV-3, **GOV-4**, **SEC-1**, **SEC-2**, SEC-5, **DOC-1**, **DOC-2**, DOC-5, **DOC-6**, DOC-7, DOC-11 |
| agent-send-gate | library/active | 34.3 | C | ✗ | P0 | **GOV-2**, GOV-3, **GOV-4**, GOV-6, **SEC-1**, **SEC-2**, **SEC-3**, SEC-4, SEC-5, **QA-1**, **QA-2**, QA-3, **DOC-2**, **DOC-3**, DOC-4, DOC-5, **DOC-6**, DOC-7, **DOC-8**, **DOC-9** |
| vertciti-sp07-builder | tool/archive | 77.4 | B | ✗ | P1 | **GOV-2**, GOV-3, **SEC-8** |
| vertciti-prototype | app/archive | 77.4 | B | ✗ | P1 | **GOV-2**, GOV-3, **SEC-8** |
| vertciti-ts-spaces | docs/placeholder | 64.3 | C | ✗ | P0 | **GOV-2**, GOV-3, **SEC-8**, **SEC-11** |
| vertciti-auto-gpt | app/archive | 0.0 | C | ✗ | P0 | **MISSING** |

**4 of 23 at or above the bar; 19 incident(s).**

**3 registered repo(s) could not be read by the assessor and are graded MISSING (score 0, C, P0): vault-app, jarvis-architecture, vertciti-auto-gpt.**

## Incidents · 事故

### P0 · miao-ai · 96.5 (S)

- `SEC-6` MUST FAIL: Workflows declare least-privilege `permissions:` — anchor-deadman.yml: workflow-level issues: write (move write scopes to the job)

### P0 · Miao · 90.2 (A++)

- `SEC-1` MUST FAIL: Secret scanning in CI (gitleaks or equivalent)
- `SEC-5` SHOULD FAIL: OpenSSF Scorecard published

### P0 · vertciti-dealdesk · 82.8 (B)

- `SEC-6` MUST FAIL: Workflows declare least-privilege `permissions:` — quality.yml: workflow-level permissions: { contents: read }
- `SEC-7` SHOULD FAIL: .env.example documents config; .env is git-ignored
- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)
- `SEC-10` SHOULD FAIL: Reproducible dependencies: lockfile or pinned requirements for every manifest
- `DOC-2` MUST FAIL: Product one-pager docs/PRODUCT.md
- `UI-1` MUST FAIL: Vendored vertciti DNA stylesheet (dna.css / dna-tailwind.css)
- `UI-2` SHOULD FAIL: dna-drift check wired in CI (vendored DNA cannot silently diverge)
- `PRIV-1` SHOULD FAIL: Data handling stated: retention / what is stored / redaction (PRIVACY.md or a section)

### P0 · vertciti-website · 78.6 (B)

- `GOV-1` MUST FAIL: LICENSE file present (or README states proprietary/pending) — no LICENSE/LICENSE.md/LICENSE.txt/COPYING, and no README licence section stating the status (proprietary / all rights reserved / pending)
- `SEC-2` MUST FAIL: Dependabot covers github-actions + every package ecosystem in repo
- `SEC-6` MUST FAIL: Workflows declare least-privilege `permissions:` — anchor.yml: workflow-level contents: write (move write scopes to the job)
- `DOC-1` MUST FAIL: README has a quickstart

### P0 · phonehands · 67.2 (C)

- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `SEC-1` MUST FAIL: Secret scanning in CI (gitleaks or equivalent)
- `SEC-2` MUST FAIL: Dependabot covers github-actions + every package ecosystem in repo
- `SEC-3` MUST FAIL: CodeQL / SAST runs on PRs
- `SEC-4` SHOULD FAIL: Dependency review blocks vulnerable additions on PRs
- `SEC-5` SHOULD FAIL: OpenSSF Scorecard published
- `SEC-7` SHOULD FAIL: .env.example documents config; .env is git-ignored
- `SEC-10` SHOULD FAIL: Reproducible dependencies: lockfile or pinned requirements for every manifest
- `QA-2` MUST FAIL: Linter/formatter enforced in CI (ruff/eslint/biome/prettier)
- `QA-3` SHOULD FAIL: pre-commit hooks mirror CI
- `DOC-2` MUST FAIL: Product one-pager docs/PRODUCT.md
- `DOC-5` SHOULD FAIL: Visual proof (screenshot/GIF) in README

### P0 · echowatch · 65.6 (C)

- `SEC-1` MUST FAIL: Secret scanning in CI (gitleaks or equivalent)
- `SEC-4` SHOULD FAIL: Dependency review blocks vulnerable additions on PRs
- `SEC-5` SHOULD FAIL: OpenSSF Scorecard published
- `SEC-6` MUST FAIL: Workflows declare least-privilege `permissions:` — codeql.yml: workflow-level security-events: write (move write scopes to the job)
- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)
- `SEC-9` SHOULD FAIL: [live] Security headers on the deployed site: CSP, nosniff, frame protection, HSTS, Referrer-Policy — https://echowatch-demo.netlify.app/ -> The read operation timed out in 12614 ms
- `SEC-10` SHOULD FAIL: Reproducible dependencies: lockfile or pinned requirements for every manifest
- `QA-3` SHOULD FAIL: pre-commit hooks mirror CI
- `QA-4` SHOULD FAIL: Type checking in CI (mypy/pyright/tsc)
- `DOC-2` MUST FAIL: Product one-pager docs/PRODUCT.md
- `UI-1` MUST FAIL: Vendored vertciti DNA stylesheet (dna.css / dna-tailwind.css)
- `UI-2` SHOULD FAIL: dna-drift check wired in CI (vendored DNA cannot silently diverge)
- `REL-1` MUST FAIL: [live] Deployed URL answers (2xx/3xx) within 12 s — https://echowatch-demo.netlify.app/ -> The read operation timed out in 12614 ms
- `REL-2` SHOULD FAIL: [live] Health endpoint returns 200 on the deployment — https://echowatch-demo.netlify.app/healthz -> The read operation timed out in 12224 ms
- `PERF-1` SHOULD FAIL: [live] Landing response within 800 ms from the assessor — https://echowatch-demo.netlify.app/ -> The read operation timed out in 12614 ms
- `PUB-2` SHOULD FAIL: Public demo or product URL registered and named in README (outsiders can see it run) — README does not mention echowatch-demo.netlify.app
- `CONT-1` SHOULD FAIL: Runbook (docs/RUNBOOK.md): deploy, rollback, backup, restore, key rotation
- `CONT-2` SHOULD FAIL: Backup and restore are written down (a restore never tested is not a backup)
- `AI-1` SHOULD FAIL: LLM-using app has evals with recorded results (not claims)
- `AI-2` SHOULD FAIL: LLM-using app tests prompt-injection / untrusted-content handling

### P0 · vertciti-ts-spaces · 64.3 (C)

- `GOV-2` MUST FAIL: CODEOWNERS routes reviews
- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)
- `SEC-11` MUST FAIL: Every action referenced by a workflow is pinned by full-length commit SHA (no tag or branch pins) — unpinned: gitleaks.yml: actions/checkout@v7; gitleaks.yml: gitleaks/gitleaks-action@v3

### P0 · fama · 58.1 (C)

- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `SEC-1` MUST FAIL: Secret scanning in CI (gitleaks or equivalent)
- `SEC-3` MUST FAIL: CodeQL / SAST runs on PRs
- `SEC-4` SHOULD FAIL: Dependency review blocks vulnerable additions on PRs
- `SEC-5` SHOULD FAIL: OpenSSF Scorecard published
- `SEC-6` MUST FAIL: Workflows declare least-privilege `permissions:` — image.yml: workflow-level packages: write (move write scopes to the job)
- `SEC-7` SHOULD FAIL: .env.example documents config; .env is git-ignored
- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)
- `SEC-9` SHOULD unprobed: [live] Security headers on the deployed site: CSP, nosniff, frame protection, HSTS, Referrer-Policy — no url (unprobed)
- `QA-3` SHOULD FAIL: pre-commit hooks mirror CI
- `QA-5` SHOULD FAIL: Browser-level test or contrast gate in CI (playwright / contrast)
- `DOC-1` MUST FAIL: README has a quickstart
- `DOC-2` MUST FAIL: Product one-pager docs/PRODUCT.md
- `DOC-4` SHOULD FAIL: Architecture doc or diagram
- `DOC-5` SHOULD FAIL: Visual proof (screenshot/GIF) in README
- `DOC-6` MUST FAIL: README links back to vertciti.com
- `DOC-7` SHOULD FAIL: README has security + license section
- `REL-1` MUST unprobed: [live] Deployed URL answers (2xx/3xx) within 12 s — no url in repos.json (unprobed)
- `REL-2` SHOULD unprobed: [live] Health endpoint returns 200 on the deployment — no url (unprobed)
- `PERF-1` SHOULD unprobed: [live] Landing response within 800 ms from the assessor — no url (unprobed)
- `PUB-2` SHOULD FAIL: Public demo or product URL registered and named in README (outsiders can see it run) — no public url registered
- `CONT-1` SHOULD FAIL: Runbook (docs/RUNBOOK.md): deploy, rollback, backup, restore, key rotation
- `CONT-2` SHOULD FAIL: Backup and restore are written down (a restore never tested is not a backup)

### P0 · operator-session-permissions · 53.6 (C)

- `GOV-2` MUST FAIL: CODEOWNERS routes reviews
- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `GOV-4` MUST FAIL: Status is stated honestly in README (active/archive/early/etc.)
- `SEC-1` MUST FAIL: Secret scanning in CI (gitleaks or equivalent)
- `SEC-2` MUST FAIL: Dependabot covers github-actions + every package ecosystem in repo
- `SEC-5` SHOULD FAIL: OpenSSF Scorecard published
- `DOC-1` MUST FAIL: README has a quickstart
- `DOC-2` MUST FAIL: Product one-pager docs/PRODUCT.md
- `DOC-5` SHOULD FAIL: Visual proof (screenshot/GIF) in README
- `DOC-6` MUST FAIL: README links back to vertciti.com
- `DOC-7` SHOULD FAIL: README has security + license section
- `DOC-11` SHOULD FAIL: Bilingual (zh + en) README or localised UI

### P0 · agent-send-gate · 34.3 (C)

- `GOV-2` MUST FAIL: CODEOWNERS routes reviews
- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `GOV-4` MUST FAIL: Status is stated honestly in README (active/archive/early/etc.)
- `GOV-6` SHOULD FAIL: SECURITY.md in repo (vulnerability reporting route, not only the org default)
- `SEC-1` MUST FAIL: Secret scanning in CI (gitleaks or equivalent)
- `SEC-2` MUST FAIL: Dependabot covers github-actions + every package ecosystem in repo
- `SEC-3` MUST FAIL: CodeQL / SAST runs on PRs
- `SEC-4` SHOULD FAIL: Dependency review blocks vulnerable additions on PRs
- `SEC-5` SHOULD FAIL: OpenSSF Scorecard published
- `QA-1` MUST FAIL: CI workflow runs tests on PRs
- `QA-2` MUST FAIL: Linter/formatter enforced in CI (ruff/eslint/biome/prettier)
- `QA-3` SHOULD FAIL: pre-commit hooks mirror CI
- `DOC-2` MUST FAIL: Product one-pager docs/PRODUCT.md
- `DOC-3` MUST FAIL: CHANGELOG.md (Keep a Changelog)
- `DOC-4` SHOULD FAIL: Architecture doc or diagram
- `DOC-5` SHOULD FAIL: Visual proof (screenshot/GIF) in README
- `DOC-6` MUST FAIL: README links back to vertciti.com
- `DOC-7` SHOULD FAIL: README has security + license section
- `DOC-8` MUST FAIL: README is left-aligned (no align=center / <center>)
- `DOC-9` MUST FAIL: README has no badge strip (shields.io / badge.svg render as '?' in private repos and the mobile app)

### P0 · vault-app · 0.0 (C)

- `MISSING` MUST FAIL: Registered repository could not be read by the assessor (clone failed or not found): not graded, counted as failing — not found under /tmp/portfolio

### P0 · jarvis-architecture · 0.0 (C)

- `MISSING` MUST FAIL: Registered repository could not be read by the assessor (clone failed or not found): not graded, counted as failing — not found under /tmp/portfolio

### P0 · vertciti-auto-gpt · 0.0 (C)

- `MISSING` MUST FAIL: Registered repository could not be read by the assessor (clone failed or not found): not graded, counted as failing — not found under /tmp/portfolio

### P1 · founder-visual-director · 92.9 (A++)

- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)
- `DOC-5` SHOULD FAIL: Visual proof (screenshot/GIF) in README

### P1 · .github · 85.0 (A)

- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)

### P1 · HUIIIM · 81.2 (B)

- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)

### P1 · vertciti-sp07-builder · 77.4 (B)

- `GOV-2` MUST FAIL: CODEOWNERS routes reviews
- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)

### P1 · vertciti-prototype · 77.4 (B)

- `GOV-2` MUST FAIL: CODEOWNERS routes reviews
- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)

### P1 · vertciti-chat · 73.1 (B)

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


## MSG-1 · 发信域 `vertciti.com`

**selector `resend`: FAIL** — at least one AUTH MUST failed or could not be shown to pass (UNMET).

| 规则 | 级别 | 结果 | 详情 |
|---|---|---|---|
| AUTH-2 SPF | MUST | ✅ PASS | v=spf1 include:zohomail.com ~all |
| AUTH-2 DKIM | MUST | ❌ FAIL | resend: 1024 位（需 ≥2048） |
| AUTH-3 DMARC | MUST | ✅ PASS | p=reject +rua |
| AUTH-4 MTA-STS | MUST | ❌ FAIL | 无 _mta-sts TXT |
| AUTH-4 TLS-RPT | MUST | ✅ PASS | v=TLSRPTv1; rua=mailto:contact@vertciti.com |
| AUTH-5 CAA | MUST | ✅ PASS | 0 iodef "mailto:contact@vertciti.com", 0 issue "comodoca.com", 0 issue "digicert.com; cansignhttpexchanges=yes", 0 issue "letsencrypt.org", 0 issue "pki.goog; cansignhttpexchanges=yes", 0 issue "ssl.com", 0 issuewild "comodoca.com", 0 issuewild "digicert.com; cansignhttpexchanges=yes", 0 issuewild "letsencrypt.org", 0 issuewild "pki.goog; cansignhttpexchanges=yes", 0 issuewild "ssl.com" |
| AUTH-6 BIMI | SHOULD | 🟡 WARN | 无 BIMI（DMARC 到 reject 后再做） |

**selector `zmail`: FAIL** — at least one AUTH MUST failed or could not be shown to pass (UNMET).

| 规则 | 级别 | 结果 | 详情 |
|---|---|---|---|
| AUTH-2 SPF | MUST | ✅ PASS | v=spf1 include:zohomail.com ~all |
| AUTH-2 DKIM | MUST | ❌ FAIL | zmail: 1024 位（需 ≥2048） |
| AUTH-3 DMARC | MUST | ✅ PASS | p=reject +rua |
| AUTH-4 MTA-STS | MUST | ❌ FAIL | 无 _mta-sts TXT |
| AUTH-4 TLS-RPT | MUST | ✅ PASS | v=TLSRPTv1; rua=mailto:contact@vertciti.com |
| AUTH-5 CAA | MUST | ✅ PASS | 0 iodef "mailto:contact@vertciti.com", 0 issue "comodoca.com", 0 issue "digicert.com; cansignhttpexchanges=yes", 0 issue "letsencrypt.org", 0 issue "pki.goog; cansignhttpexchanges=yes", 0 issue "ssl.com", 0 issuewild "comodoca.com", 0 issuewild "digicert.com; cansignhttpexchanges=yes", 0 issuewild "letsencrypt.org", 0 issuewild "pki.goog; cansignhttpexchanges=yes", 0 issuewild "ssl.com" |
| AUTH-6 BIMI | SHOULD | 🟡 WARN | 无 BIMI（DMARC 到 reject 后再做） |
