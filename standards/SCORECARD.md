# Portfolio scorecard · 组合记分卡

Generated 2026-10-30 23:34Z by `standards/audit.py` (independent assessor; live probes on). Bar = **A++** (score ≥ 90 and no failing MUST). Below the bar is an incident with the severity shown. Grades: S ≥95 · A++ ≥90 · A ≥85 · B ≥70 · C <70. Unprobed checks count as failed.

| repo | kind/status | score | grade | bar | incident | failing (MUST in bold) |
|---|---|---:|---|---|---|---|
| miao-ai | app/active | 96.5 | S | ✗ | P0 | **SEC-6** |
| vertciti-translator | app/active | 88.2 | A | ✗ | P1 | **SEC-11**, DOC-11, UI-2, OPS-5, REL-2, PERF-1, CONT-1, PRIV-1, AI-1 |
| vertciti-chat | app/active | 69.9 | C | ✗ | P0 | SEC-7, SEC-9, **SEC-11**, QA-4, **DOC-2**, **DOC-3**, DOC-4, DOC-5, DOC-11, **UI-1**, UI-2, OPS-3, **REL-1**, REL-2, PERF-1, PUB-2, CONT-1, CONT-2 |
| echowatch | app/active | 63.4 | C | ✗ | P0 | **SEC-1**, SEC-4, SEC-5, **SEC-6**, **SEC-8**, SEC-9, SEC-10, **SEC-11**, QA-3, QA-4, **DOC-2**, **UI-1**, UI-2, **REL-1**, REL-2, PUB-2, CONT-1, CONT-2, AI-1, AI-2 |
| vertciti-dealdesk | app/active | 79.6 | B | ✗ | P0 | **SEC-6**, SEC-7, **SEC-8**, SEC-10, **SEC-11**, **DOC-2**, **UI-1**, UI-2, PRIV-1 |
| phonehands | library/active | 67.2 | C | ✗ | P0 | GOV-3, **SEC-1**, **SEC-2**, **SEC-3**, SEC-4, SEC-5, SEC-7, SEC-10, **QA-2**, QA-3, **DOC-2**, DOC-5 |
| founder-visual-director | skill/active | 92.9 | A++ | ✗ | P0 | **SEC-6**, DOC-5 |
| think-tank | skill/active | 98.2 | S | ✓ | — | DOC-5 |
| website-qa-gates | skill/active | 98.2 | S | ✓ | — | DOC-5 |
| vertciti-security-watch | tool/active | 97.1 | S | ✓ | — | SEC-7, DOC-5 |
| vertciti-website | site/active | 78.6 | B | ✗ | P0 | **GOV-1**, **SEC-2**, **SEC-6**, **DOC-1** |
| fama | app/active | 52.7 | C | ✗ | P0 | **GOV-2**, GOV-3, GOV-6, **SEC-1**, **SEC-3**, SEC-4, SEC-5, **SEC-6**, SEC-7, **SEC-8**, SEC-9, QA-3, QA-5, **DOC-1**, **DOC-2**, DOC-4, DOC-5, **DOC-6**, DOC-7, OPS-3, **REL-1**, REL-2, PERF-1, PUB-2, CONT-1, CONT-2 |
| Miao | docs/active | 90.2 | A++ | ✗ | P0 | **SEC-1**, SEC-5 |
| HUIIIM | profile/active | 100.0 | S | ✓ | — | — |
| .github | meta/active | 100.0 | S | ✓ | — | — |
| vertciti-sp07-builder | tool/archive | 67.7 | C | ✗ | P0 | **GOV-2**, GOV-3, **SEC-8**, **SEC-11** |
| vertciti-prototype | app/archive | 67.7 | C | ✗ | P0 | **GOV-2**, GOV-3, **SEC-8**, **SEC-11** |
| vertciti-ts-spaces | docs/placeholder | 64.3 | C | ✗ | P0 | **GOV-2**, GOV-3, **SEC-8**, **SEC-11** |

**5 of 18 at or above the bar; 13 incident(s).**

## Incidents · 事故

### P0 · miao-ai · 96.5 (S)

- `SEC-6` MUST FAIL: Workflows declare least-privilege `permissions:` — anchor-deadman.yml: workflow-level issues: write (move write scopes to the job)

### P0 · founder-visual-director · 92.9 (A++)

- `SEC-6` MUST FAIL: Workflows declare least-privilege `permissions:` — dependency-review.yml: workflow-level pull-requests: write (move write scopes to the job)
- `DOC-5` SHOULD FAIL: Visual proof (screenshot/GIF) in README

### P0 · Miao · 90.2 (A++)

- `SEC-1` MUST FAIL: Secret scanning in CI (gitleaks or equivalent)
- `SEC-5` SHOULD FAIL: OpenSSF Scorecard published

### P0 · vertciti-dealdesk · 79.6 (B)

- `SEC-6` MUST FAIL: Workflows declare least-privilege `permissions:` — quality.yml: workflow-level permissions: { contents: read }
- `SEC-7` SHOULD FAIL: .env.example documents config; .env is git-ignored
- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)
- `SEC-10` SHOULD FAIL: Reproducible dependencies: lockfile or pinned requirements for every manifest
- `SEC-11` MUST FAIL: Every action referenced by a workflow is pinned by full-length commit SHA (no tag or branch pins) — unpinned: ci.yml: actions/checkout@v7; ci.yml: actions/setup-python@v7; codeql.yml: actions/checkout@v7; codeql.yml: github/codeql-action/init@v4; codeql.yml: github/codeql-action/analyze@v4; dependency-review.yml: actions/checkout@v7 (+14 more)
- `DOC-2` MUST FAIL: Product one-pager docs/PRODUCT.md
- `UI-1` MUST FAIL: Vendored vertciti DNA stylesheet (dna.css / dna-tailwind.css)
- `UI-2` SHOULD FAIL: dna-drift check wired in CI (vendored DNA cannot silently diverge)
- `PRIV-1` SHOULD FAIL: Data handling stated: retention / what is stored / redaction (PRIVACY.md or a section)

### P0 · vertciti-website · 78.6 (B)

- `GOV-1` MUST FAIL: LICENSE file present (or README states proprietary/pending) — no LICENSE/LICENSE.md/LICENSE.txt/COPYING, and no README licence section stating the status (proprietary / all rights reserved / pending)
- `SEC-2` MUST FAIL: Dependabot covers github-actions + every package ecosystem in repo
- `SEC-6` MUST FAIL: Workflows declare least-privilege `permissions:` — anchor.yml: workflow-level contents: write (move write scopes to the job)
- `DOC-1` MUST FAIL: README has a quickstart

### P0 · vertciti-chat · 69.9 (C)

- `SEC-7` SHOULD FAIL: .env.example documents config; .env is git-ignored
- `SEC-9` SHOULD unprobed: [live] Security headers on the deployed site: CSP, nosniff, frame protection, HSTS, Referrer-Policy — no url (unprobed)
- `SEC-11` MUST FAIL: Every action referenced by a workflow is pinned by full-length commit SHA (no tag or branch pins) — unpinned: ci.yml: actions/checkout@v7; ci.yml: actions/setup-python@v7; ci.yml: actions/checkout@v7; ci.yml: actions/setup-node@v7; codeql.yml: actions/checkout@v7; codeql.yml: github/codeql-action/init@v4 (+8 more)
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

### P0 · vertciti-sp07-builder · 67.7 (C)

- `GOV-2` MUST FAIL: CODEOWNERS routes reviews
- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)
- `SEC-11` MUST FAIL: Every action referenced by a workflow is pinned by full-length commit SHA (no tag or branch pins) — unpinned: ci.yml: actions/checkout@v7; ci.yml: actions/setup-python@v6; ci.yml: actions/checkout@v7; codeql.yml: actions/checkout@v7; codeql.yml: github/codeql-action/init@v4; codeql.yml: github/codeql-action/analyze@v4 (+7 more)

### P0 · vertciti-prototype · 67.7 (C)

- `GOV-2` MUST FAIL: CODEOWNERS routes reviews
- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)
- `SEC-11` MUST FAIL: Every action referenced by a workflow is pinned by full-length commit SHA (no tag or branch pins) — unpinned: ci.yml: actions/checkout@v7; ci.yml: actions/setup-python@v6; codeql.yml: actions/checkout@v7; codeql.yml: github/codeql-action/init@v4; codeql.yml: github/codeql-action/analyze@v4; dependency-review.yml: actions/checkout@v7 (+6 more)

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

### P0 · echowatch · 63.4 (C)

- `SEC-1` MUST FAIL: Secret scanning in CI (gitleaks or equivalent)
- `SEC-4` SHOULD FAIL: Dependency review blocks vulnerable additions on PRs
- `SEC-5` SHOULD FAIL: OpenSSF Scorecard published
- `SEC-6` MUST FAIL: Workflows declare least-privilege `permissions:` — codeql.yml: workflow-level security-events: write (move write scopes to the job)
- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)
- `SEC-9` SHOULD FAIL: [live] Security headers on the deployed site: CSP, nosniff, frame protection, HSTS, Referrer-Policy — missing: content-security-policy, x-content-type-options, frame, referrer-policy
- `SEC-10` SHOULD FAIL: Reproducible dependencies: lockfile or pinned requirements for every manifest
- `SEC-11` MUST FAIL: Every action referenced by a workflow is pinned by full-length commit SHA (no tag or branch pins) — unpinned: ci.yml: actions/checkout@v4; ci.yml: actions/setup-python@v5; ci.yml: actions/checkout@v4; ci.yml: actions/setup-python@v5; ci.yml: actions/checkout@v4; ci.yml: actions/setup-python@v5 (+12 more)
- `QA-3` SHOULD FAIL: pre-commit hooks mirror CI
- `QA-4` SHOULD FAIL: Type checking in CI (mypy/pyright/tsc)
- `DOC-2` MUST FAIL: Product one-pager docs/PRODUCT.md
- `UI-1` MUST FAIL: Vendored vertciti DNA stylesheet (dna.css / dna-tailwind.css)
- `UI-2` SHOULD FAIL: dna-drift check wired in CI (vendored DNA cannot silently diverge)
- `REL-1` MUST FAIL: [live] Deployed URL answers (2xx/3xx) within 12 s — https://echowatch-demo.netlify.app/ -> 500 in 702 ms
- `REL-2` SHOULD FAIL: [live] Health endpoint returns 200 on the deployment — https://echowatch-demo.netlify.app/healthz -> 500 in 294 ms
- `PUB-2` SHOULD FAIL: Public demo or product URL registered and named in README (outsiders can see it run) — README does not mention echowatch-demo.netlify.app
- `CONT-1` SHOULD FAIL: Runbook (docs/RUNBOOK.md): deploy, rollback, backup, restore, key rotation
- `CONT-2` SHOULD FAIL: Backup and restore are written down (a restore never tested is not a backup)
- `AI-1` SHOULD FAIL: LLM-using app has evals with recorded results (not claims)
- `AI-2` SHOULD FAIL: LLM-using app tests prompt-injection / untrusted-content handling

### P0 · fama · 52.7 (C)

- `GOV-2` MUST FAIL: CODEOWNERS routes reviews
- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `GOV-6` SHOULD FAIL: SECURITY.md in repo (vulnerability reporting route, not only the org default)
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
- `OPS-3` SHOULD FAIL: Security response headers set in code (CSP / X-Content-Type-Options / frame-ancestors)
- `REL-1` MUST unprobed: [live] Deployed URL answers (2xx/3xx) within 12 s — no url in repos.json (unprobed)
- `REL-2` SHOULD unprobed: [live] Health endpoint returns 200 on the deployment — no url (unprobed)
- `PERF-1` SHOULD unprobed: [live] Landing response within 800 ms from the assessor — no url (unprobed)
- `PUB-2` SHOULD FAIL: Public demo or product URL registered and named in README (outsiders can see it run) — no public url registered
- `CONT-1` SHOULD FAIL: Runbook (docs/RUNBOOK.md): deploy, rollback, backup, restore, key rotation
- `CONT-2` SHOULD FAIL: Backup and restore are written down (a restore never tested is not a backup)

### P1 · vertciti-translator · 88.2 (A)

- `SEC-11` MUST FAIL: Every action referenced by a workflow is pinned by full-length commit SHA (no tag or branch pins) — unpinned: ci.yml: actions/checkout@v7; ci.yml: actions/setup-python@v7; ci.yml: actions/checkout@v7; ci.yml: actions/setup-node@v7; ci.yml: actions/checkout@v7; ci.yml: actions/setup-node@v7 (+10 more)
- `DOC-11` SHOULD FAIL: Bilingual (zh + en) README or localised UI
- `UI-2` SHOULD FAIL: dna-drift check wired in CI (vendored DNA cannot silently diverge)
- `OPS-5` SHOULD FAIL: Structured logs with a request/trace id (OpenTelemetry-style)
- `REL-2` SHOULD FAIL: [live] Health endpoint returns 200 on the deployment — https://vertciti-translator.vercel.app/health -> 404 in 716 ms
- `PERF-1` SHOULD FAIL: [live] Landing response within 800 ms from the assessor — 1413 ms to first response (budget 800 ms)
- `CONT-1` SHOULD FAIL: Runbook (docs/RUNBOOK.md): deploy, rollback, backup, restore, key rotation
- `PRIV-1` SHOULD FAIL: Data handling stated: retention / what is stored / redaction (PRIVACY.md or a section)
- `AI-1` SHOULD FAIL: LLM-using app has evals with recorded results (not claims)


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
