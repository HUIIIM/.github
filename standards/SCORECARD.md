# Portfolio scorecard · 组合记分卡

Generated 2026-11-08 10:46Z by `standards/audit.py` (independent assessor; live probes on). Bar = **A++** (score ≥ 90 and no failing MUST). Below the bar is an incident with the severity shown. Grades: S ≥95 · A++ ≥90 · A ≥85 · B ≥70 · C <70. Unprobed checks count as failed.

| repo | kind/status | score | grade | bar | incident | failing (MUST in bold) |
|---|---|---:|---|---|---|---|
| miao-ai | app/active | 96.5 | S | ✗ | P0 | **SEC-6** |
| vertciti-translator | app/active | 88.2 | A | ✗ | P0 | SEC-9, DOC-11, UI-2, OPS-5, **REL-1**, REL-2, CONT-1, PRIV-1, AI-1 |
| vertciti-chat | app/active | 71.0 | B | ✗ | P1 | SEC-7, SEC-9, QA-4, **DOC-2**, **DOC-3**, DOC-4, DOC-5, DOC-11, **UI-1**, UI-2, OPS-3, **REL-1**, REL-2, PERF-1, PUB-2, CONT-1, CONT-2, AI-1, AI-2 |
| echowatch | app/active | 71.0 | B | ✗ | P0 | **SEC-1**, SEC-4, SEC-5, **SEC-6**, **SEC-8**, SEC-9, SEC-10, QA-3, QA-4, **DOC-2**, **UI-1**, UI-2, PERF-1, CONT-1, CONT-2, AI-1, AI-2 |
| vertciti-dealdesk | app/active | 94.6 | A++ | ✗ | P0 | SEC-9, **REL-1**, REL-2 |
| phonehands | library/active | 67.2 | C | ✗ | P0 | GOV-3, **SEC-1**, **SEC-2**, **SEC-3**, SEC-4, SEC-5, SEC-7, SEC-10, **QA-2**, QA-3, **DOC-2**, DOC-5 |
| founder-visual-director | skill/active | 98.2 | S | ✓ | — | DOC-5 |
| think-tank | skill/active | 98.2 | S | ✓ | — | DOC-5 |
| website-qa-gates | skill/active | 92.9 | A++ | ✗ | P1 | **SEC-2**, DOC-5 |
| vertciti-security-watch | tool/active | 97.1 | S | ✓ | — | SEC-7, DOC-5 |
| vertciti-website | site/active | 94.6 | A++ | ✗ | P0 | **SEC-6** |
| fama | app/active | 89.5 | A | ✗ | P0 | **SEC-6**, **SEC-8**, **SEC-11** |
| Miao | docs/active | 92.7 | A++ | ✗ | P1 | **SEC-2** |
| HUIIIM | profile/active | 81.2 | B | ✗ | P1 | **SEC-8** |
| vault-app | app/active | 37.2 | C | ✗ | P0 | **GOV-1**, **GOV-2**, GOV-3, **SEC-1**, **SEC-2**, **SEC-3**, SEC-4, SEC-5, **SEC-8**, **QA-1**, **QA-2**, QA-3, QA-4, QA-5, **DOC-1**, **DOC-2**, **DOC-3**, DOC-4, DOC-5, **DOC-6**, DOC-7, DOC-11, **OPS-1**, OPS-3, OPS-5, CONT-1, CONT-2, PRIV-1 |
| jarvis-architecture | library/active | 37.3 | C | ✗ | P0 | **GOV-1**, **GOV-2**, GOV-3, **SEC-2**, **SEC-3**, SEC-4, **SEC-6**, **SEC-8**, **QA-1**, **QA-2**, QA-3, **DOC-1**, **DOC-2**, **DOC-3**, DOC-4, DOC-5, **DOC-6**, DOC-7 |
| .github | meta/active | 100.0 | S | ✓ | — | — |
| operator-session-permissions | skill/active | 53.6 | C | ✗ | P0 | **GOV-2**, GOV-3, **GOV-4**, **SEC-1**, **SEC-2**, SEC-5, **DOC-1**, **DOC-2**, DOC-5, **DOC-6**, DOC-7, DOC-11 |
| agent-send-gate | library/active | 35.8 | C | ✗ | P0 | **GOV-2**, GOV-3, **GOV-4**, **SEC-1**, **SEC-2**, **SEC-3**, SEC-4, SEC-5, **QA-1**, **QA-2**, QA-3, **DOC-2**, **DOC-3**, DOC-4, DOC-5, **DOC-6**, DOC-7, **DOC-8**, **DOC-9** |
| vertciti-sp07-builder | tool/archive | 77.4 | B | ✗ | P1 | **GOV-2**, GOV-3, **SEC-8** |
| vertciti-prototype | app/archive | 77.4 | B | ✗ | P1 | **GOV-2**, GOV-3, **SEC-8** |
| vertciti-ts-spaces | docs/placeholder | 64.3 | C | ✗ | P0 | **GOV-2**, GOV-3, **SEC-8**, **SEC-11** |
| vertciti-auto-gpt | app/archive | 58.1 | C | ✗ | P0 | **GOV-1**, **GOV-2**, GOV-3, **GOV-5**, **SEC-1** |

**4 of 23 at or above the bar; 19 incident(s).**

## Incidents · 事故

### P0 · miao-ai · 96.5 (S)

- `SEC-6` MUST FAIL: Workflows declare least-privilege `permissions:` — anchor-deadman.yml: workflow-level issues: write (move write scopes to the job)

### P0 · vertciti-dealdesk · 94.6 (A++)

- `SEC-9` SHOULD FAIL: [live] Security headers on the deployed site: CSP, nosniff, frame protection, HSTS, Referrer-Policy — missing: content-security-policy, x-content-type-options, frame, referrer-policy
- `REL-1` MUST FAIL: [live] Deployed URL answers (2xx/3xx) within 12 s — https://vertciti-dealdesk.vercel.app/app/ -> 402 in 124 ms
- `REL-2` SHOULD FAIL: [live] Health endpoint returns 200 on the deployment — https://vertciti-dealdesk.vercel.app/app/healthz -> 402 in 131 ms

### P0 · vertciti-website · 94.6 (A++)

- `SEC-6` MUST FAIL: Workflows declare least-privilege `permissions:` — contrast.yml: workflow-level issues: write (move write scopes to the job)

### P0 · fama · 89.5 (A)

- `SEC-6` MUST FAIL: Workflows declare least-privilege `permissions:` — pr-template-check.yml: workflow-level pull-requests: write, issues: write (move write scopes to the job)
- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)
- `SEC-11` MUST FAIL: Every action referenced by a workflow is pinned by full-length commit SHA (no tag or branch pins) — unpinned: pr-template-check.yml: actions/checkout@v4; pr-template-check.yml: actions/setup-node@v4

### P0 · vertciti-translator · 88.2 (A)

- `SEC-9` SHOULD FAIL: [live] Security headers on the deployed site: CSP, nosniff, frame protection, HSTS, Referrer-Policy — missing: content-security-policy, x-content-type-options, frame, referrer-policy
- `DOC-11` SHOULD FAIL: Bilingual (zh + en) README or localised UI
- `UI-2` SHOULD FAIL: dna-drift check wired in CI (vendored DNA cannot silently diverge)
- `OPS-5` SHOULD FAIL: Structured logs with a request/trace id (OpenTelemetry-style)
- `REL-1` MUST FAIL: [live] Deployed URL answers (2xx/3xx) within 12 s — https://vertciti-translator.vercel.app/ -> 402 in 180 ms
- `REL-2` SHOULD FAIL: [live] Health endpoint returns 200 on the deployment — https://vertciti-translator.vercel.app/health -> 402 in 127 ms
- `CONT-1` SHOULD FAIL: Runbook (docs/RUNBOOK.md): deploy, rollback, backup, restore, key rotation
- `PRIV-1` SHOULD FAIL: Data handling stated: retention / what is stored / redaction (PRIVACY.md or a section)
- `AI-1` SHOULD FAIL: LLM-using app has evals with recorded results (not claims)

### P0 · echowatch · 71.0 (B)

- `SEC-1` MUST FAIL: Secret scanning in CI (gitleaks or equivalent)
- `SEC-4` SHOULD FAIL: Dependency review blocks vulnerable additions on PRs
- `SEC-5` SHOULD FAIL: OpenSSF Scorecard published
- `SEC-6` MUST FAIL: Workflows declare least-privilege `permissions:` — codeql.yml: workflow-level security-events: write (move write scopes to the job)
- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)
- `SEC-9` SHOULD FAIL: [live] Security headers on the deployed site: CSP, nosniff, frame protection, HSTS, Referrer-Policy — missing: content-security-policy, strict-transport-security
- `SEC-10` SHOULD FAIL: Reproducible dependencies: lockfile or pinned requirements for every manifest
- `QA-3` SHOULD FAIL: pre-commit hooks mirror CI
- `QA-4` SHOULD FAIL: Type checking in CI (mypy/pyright/tsc)
- `DOC-2` MUST FAIL: Product one-pager docs/PRODUCT.md
- `UI-1` MUST FAIL: Vendored vertciti DNA stylesheet (dna.css / dna-tailwind.css)
- `UI-2` SHOULD FAIL: dna-drift check wired in CI (vendored DNA cannot silently diverge)
- `PERF-1` SHOULD FAIL: [live] Landing response within 800 ms from the assessor — 5008 ms to first response (budget 800 ms)
- `CONT-1` SHOULD FAIL: Runbook (docs/RUNBOOK.md): deploy, rollback, backup, restore, key rotation
- `CONT-2` SHOULD FAIL: Backup and restore are written down (a restore never tested is not a backup)
- `AI-1` SHOULD FAIL: LLM-using app has evals with recorded results (not claims)
- `AI-2` SHOULD FAIL: LLM-using app tests prompt-injection / untrusted-content handling

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

### P0 · vertciti-ts-spaces · 64.3 (C)

- `GOV-2` MUST FAIL: CODEOWNERS routes reviews
- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)
- `SEC-11` MUST FAIL: Every action referenced by a workflow is pinned by full-length commit SHA (no tag or branch pins) — unpinned: gitleaks.yml: actions/checkout@v7; gitleaks.yml: gitleaks/gitleaks-action@v3

### P0 · vertciti-auto-gpt · 58.1 (C)

- `GOV-1` MUST FAIL: LICENSE file present (or README states proprietary/pending) — no LICENSE/LICENSE.md/LICENSE.txt/COPYING, and no README licence section stating the status (proprietary / all rights reserved / pending)
- `GOV-2` MUST FAIL: CODEOWNERS routes reviews
- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `GOV-5` MUST FAIL: Archive banner at top of README
- `SEC-1` MUST FAIL: Secret scanning in CI (gitleaks or equivalent)

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

### P0 · jarvis-architecture · 37.3 (C)

- `GOV-1` MUST FAIL: LICENSE file present (or README states proprietary/pending) — no LICENSE/LICENSE.md/LICENSE.txt/COPYING, and no README licence section stating the status (proprietary / all rights reserved / pending)
- `GOV-2` MUST FAIL: CODEOWNERS routes reviews
- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `SEC-2` MUST FAIL: Dependabot covers github-actions + every package ecosystem in repo
- `SEC-3` MUST FAIL: CodeQL / SAST runs on PRs
- `SEC-4` SHOULD FAIL: Dependency review blocks vulnerable additions on PRs
- `SEC-6` MUST FAIL: Workflows declare least-privilege `permissions:` — x01-deadman-probe.yml: workflow-level issues: write (move write scopes to the job)
- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)
- `QA-1` MUST FAIL: CI workflow runs tests on PRs
- `QA-2` MUST FAIL: Linter/formatter enforced in CI (ruff/eslint/biome/prettier)
- `QA-3` SHOULD FAIL: pre-commit hooks mirror CI
- `DOC-1` MUST FAIL: README has a quickstart
- `DOC-2` MUST FAIL: Product one-pager docs/PRODUCT.md
- `DOC-3` MUST FAIL: CHANGELOG.md (Keep a Changelog)
- `DOC-4` SHOULD FAIL: Architecture doc or diagram
- `DOC-5` SHOULD FAIL: Visual proof (screenshot/GIF) in README
- `DOC-6` MUST FAIL: README links back to vertciti.com
- `DOC-7` SHOULD FAIL: README has security + license section

### P0 · vault-app · 37.2 (C)

- `GOV-1` MUST FAIL: LICENSE file present (or README states proprietary/pending) — no LICENSE/LICENSE.md/LICENSE.txt/COPYING, and no README licence section stating the status (proprietary / all rights reserved / pending)
- `GOV-2` MUST FAIL: CODEOWNERS routes reviews
- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `SEC-1` MUST FAIL: Secret scanning in CI (gitleaks or equivalent)
- `SEC-2` MUST FAIL: Dependabot covers github-actions + every package ecosystem in repo
- `SEC-3` MUST FAIL: CodeQL / SAST runs on PRs
- `SEC-4` SHOULD FAIL: Dependency review blocks vulnerable additions on PRs
- `SEC-5` SHOULD FAIL: OpenSSF Scorecard published
- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)
- `QA-1` MUST FAIL: CI workflow runs tests on PRs
- `QA-2` MUST FAIL: Linter/formatter enforced in CI (ruff/eslint/biome/prettier)
- `QA-3` SHOULD FAIL: pre-commit hooks mirror CI
- `QA-4` SHOULD FAIL: Type checking in CI (mypy/pyright/tsc)
- `QA-5` SHOULD FAIL: Browser-level test or contrast gate in CI (playwright / contrast)
- `DOC-1` MUST FAIL: README has a quickstart
- `DOC-2` MUST FAIL: Product one-pager docs/PRODUCT.md
- `DOC-3` MUST FAIL: CHANGELOG.md (Keep a Changelog)
- `DOC-4` SHOULD FAIL: Architecture doc or diagram
- `DOC-5` SHOULD FAIL: Visual proof (screenshot/GIF) in README
- `DOC-6` MUST FAIL: README links back to vertciti.com
- `DOC-7` SHOULD FAIL: README has security + license section
- `DOC-11` SHOULD FAIL: Bilingual (zh + en) README or localised UI
- `OPS-1` MUST FAIL: Health endpoint (/healthz or /health)
- `OPS-3` SHOULD FAIL: Security response headers set in code (CSP / X-Content-Type-Options / frame-ancestors)
- `OPS-5` SHOULD FAIL: Structured logs with a request/trace id (OpenTelemetry-style)
- `CONT-1` SHOULD FAIL: Runbook (docs/RUNBOOK.md): deploy, rollback, backup, restore, key rotation
- `CONT-2` SHOULD FAIL: Backup and restore are written down (a restore never tested is not a backup)
- `PRIV-1` SHOULD FAIL: Data handling stated: retention / what is stored / redaction (PRIVACY.md or a section)

### P0 · agent-send-gate · 35.8 (C)

- `GOV-2` MUST FAIL: CODEOWNERS routes reviews
- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `GOV-4` MUST FAIL: Status is stated honestly in README (active/archive/early/etc.)
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

### P1 · website-qa-gates · 92.9 (A++)

- `SEC-2` MUST FAIL: Dependabot covers github-actions + every package ecosystem in repo
- `DOC-5` SHOULD FAIL: Visual proof (screenshot/GIF) in README

### P1 · Miao · 92.7 (A++)

- `SEC-2` MUST FAIL: Dependabot covers github-actions + every package ecosystem in repo

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

### P1 · vertciti-chat · 71.0 (B)

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
