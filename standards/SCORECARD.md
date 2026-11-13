# Portfolio scorecard · 组合记分卡

Generated 2026-11-13 11:34Z by `standards/audit.py` (independent assessor; live probes on). Bar = **A++** (score ≥ 90 and no failing MUST). Below the bar is an incident with the severity shown. Grades: S ≥95 · A++ ≥90 · A ≥85 · B ≥70 · C <70. Unprobed checks count as failed.

| repo | kind/status | score | grade | bar | incident | failing (MUST in bold) |
|---|---|---:|---|---|---|---|
| miao-ai | app/active | 100.0 | S | ✓ | — | — |
| vertciti-translator | app/active | 88.2 | A | ✗ | P0 | 9 failing (1 MUST); private repo: detail in its own incident issue |
| vertciti-chat | app/active | 71.0 | B | ✗ | P1 | 19 failing (4 MUST); private repo: detail in its own incident issue |
| echowatch | app/active | 87.1 | A | ✗ | P0 | 6 failing (3 MUST); private repo: detail in its own incident issue |
| vertciti-dealdesk | app/active | 94.6 | A++ | ✗ | P0 | SEC-9, **REL-1**, REL-2 |
| phonehands | library/active | 98.5 | S | ✓ | — | SEC-10 |
| founder-visual-director | skill/active | 98.2 | S | ✓ | — | DOC-5 |
| think-tank | skill/active | 98.2 | S | ✓ | — | DOC-5 |
| website-qa-gates | skill/active | 92.9 | A++ | ✗ | P1 | **SEC-2**, DOC-5 |
| vertciti-security-watch | tool/active | 97.1 | S | ✓ | — | SEC-7, DOC-5 |
| vertciti-website | site/active | 100.0 | S | ✓ | — | — |
| fama | app/active | 98.8 | S | ✓ | — | 1 failing (0 MUST); private repo: detail in its own incident issue |
| Miao | docs/active | 100.0 | S | ✓ | — | — |
| HUIIIM | profile/active | 100.0 | S | ✓ | — | — |
| vault-app | app/active | 37.2 | C | ✗ | P0 | 28 failing (13 MUST); private repo: detail in its own incident issue |
| jarvis-architecture | library/active | 37.3 | C | ✗ | P0 | 18 failing (12 MUST); private repo: detail in its own incident issue |
| .github | meta/active | 100.0 | S | ✓ | — | — |
| operator-session-permissions | skill/active | 53.6 | C | ✗ | P0 | **GOV-2**, GOV-3, **GOV-4**, **SEC-1**, **SEC-2**, SEC-5, **DOC-1**, **DOC-2**, DOC-5, **DOC-6**, DOC-7, DOC-11 |
| agent-send-gate | library/active | 35.8 | C | ✗ | P0 | **GOV-2**, GOV-3, **GOV-4**, **SEC-1**, **SEC-2**, **SEC-3**, SEC-4, SEC-5, **QA-1**, **QA-2**, QA-3, **DOC-2**, **DOC-3**, DOC-4, DOC-5, **DOC-6**, DOC-7, **DOC-8**, **DOC-9** |
| vertciti-sp07-builder | tool/archive | 77.4 | B | ✗ | P1 | **GOV-2**, GOV-3, **SEC-8** |
| vertciti-prototype | app/archive | 77.4 | B | ✗ | P1 | 3 failing (2 MUST); private repo: detail in its own incident issue |
| vertciti-ts-spaces | docs/archive | 58.1 | C | ✗ | P0 | 5 failing (4 MUST); private repo: detail in its own incident issue |
| vertciti-auto-gpt | app/archive | 58.1 | C | ✗ | P0 | 5 failing (4 MUST); private repo: detail in its own incident issue |
| helm | app/active | 38.7 | C | ✗ | P0 | **GOV-1**, **GOV-2**, GOV-3, **SEC-1**, **SEC-2**, **SEC-3**, SEC-4, SEC-5, SEC-9, **QA-1**, **QA-2**, QA-3, QA-4, QA-5, **DOC-1**, **DOC-2**, **DOC-3**, DOC-4, DOC-5, **DOC-6**, DOC-7, **UI-1**, UI-2, **OPS-1**, OPS-3, OPS-5, REL-2, PUB-2, CONT-1, CONT-2, PRIV-1 |
| skill-card-gate | skill/active | 42.9 | C | ✗ | P0 | **GOV-2**, GOV-3, **GOV-4**, **SEC-1**, **SEC-2**, SEC-5, **DOC-2**, **DOC-3**, DOC-5, **DOC-6**, DOC-7, **DOC-8**, **DOC-9**, DOC-11 |
| vertciti-anchors | tool/archive | 67.7 | C | ✗ | P0 | **GOV-1**, **GOV-2**, GOV-3, **SEC-1** |
| family-crest | library/active | 89.6 | A | ✗ | P1 | 5 failing (1 MUST); private repo: detail in its own incident issue |

**10 of 27 at or above the bar; 17 incident(s).**

## Incidents · 事故

### P0 · vertciti-dealdesk · 94.6 (A++)

- `SEC-9` SHOULD FAIL: [live] Security headers on the deployed site: CSP, nosniff, frame protection, HSTS, Referrer-Policy — missing: content-security-policy, x-content-type-options, frame, referrer-policy
- `REL-1` MUST FAIL: [live] Deployed URL answers (2xx/3xx) within 12 s — https://vertciti-dealdesk.vercel.app/app/ -> 402 in 83 ms
- `REL-2` SHOULD FAIL: [live] Health endpoint returns 200 on the deployment — https://vertciti-dealdesk.vercel.app/app/healthz -> 402 in 57 ms

### P0 · vertciti-translator · 88.2 (A)

- Private repository: 9 failing check(s), 1 of them MUST. Which checks, with evidence, is recorded only in the repository's own `standards-incident` issue (STANDARDS.md §考核 6).

### P0 · echowatch · 87.1 (A)

- Private repository: 6 failing check(s), 3 of them MUST. Which checks, with evidence, is recorded only in the repository's own `standards-incident` issue (STANDARDS.md §考核 6).

### P0 · vertciti-anchors · 67.7 (C)

- `GOV-1` MUST FAIL: LICENSE file present (or README states proprietary/pending) — no LICENSE/LICENSE.md/LICENSE.txt/COPYING, and no README licence section stating the status (proprietary / all rights reserved / pending)
- `GOV-2` MUST FAIL: CODEOWNERS routes reviews
- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `SEC-1` MUST FAIL: Secret scanning in CI (gitleaks or equivalent)

### P0 · vertciti-ts-spaces · 58.1 (C)

- Private repository: 5 failing check(s), 4 of them MUST. Which checks, with evidence, is recorded only in the repository's own `standards-incident` issue (STANDARDS.md §考核 6).

### P0 · vertciti-auto-gpt · 58.1 (C)

- Private repository: 5 failing check(s), 4 of them MUST. Which checks, with evidence, is recorded only in the repository's own `standards-incident` issue (STANDARDS.md §考核 6).

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

### P0 · skill-card-gate · 42.9 (C)

- `GOV-2` MUST FAIL: CODEOWNERS routes reviews
- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `GOV-4` MUST FAIL: Status is stated honestly in README (active/archive/early/etc.)
- `SEC-1` MUST FAIL: Secret scanning in CI (gitleaks or equivalent)
- `SEC-2` MUST FAIL: Dependabot covers github-actions + every package ecosystem in repo
- `SEC-5` SHOULD FAIL: OpenSSF Scorecard published
- `DOC-2` MUST FAIL: Product one-pager docs/PRODUCT.md
- `DOC-3` MUST FAIL: CHANGELOG.md (Keep a Changelog)
- `DOC-5` SHOULD FAIL: Visual proof (screenshot/GIF) in README
- `DOC-6` MUST FAIL: README links back to vertciti.com
- `DOC-7` SHOULD FAIL: README has security + license section
- `DOC-8` MUST FAIL: README is left-aligned (no align=center / <center>)
- `DOC-9` MUST FAIL: README has no badge strip (shields.io / badge.svg render as '?' in private repos and the mobile app)
- `DOC-11` SHOULD FAIL: Bilingual (zh + en) README or localised UI

### P0 · helm · 38.7 (C)

- `GOV-1` MUST FAIL: LICENSE file present (or README states proprietary/pending) — no LICENSE/LICENSE.md/LICENSE.txt/COPYING, and no README licence section stating the status (proprietary / all rights reserved / pending)
- `GOV-2` MUST FAIL: CODEOWNERS routes reviews
- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `SEC-1` MUST FAIL: Secret scanning in CI (gitleaks or equivalent)
- `SEC-2` MUST FAIL: Dependabot covers github-actions + every package ecosystem in repo
- `SEC-3` MUST FAIL: CodeQL / SAST runs on PRs
- `SEC-4` SHOULD FAIL: Dependency review blocks vulnerable additions on PRs
- `SEC-5` SHOULD FAIL: OpenSSF Scorecard published
- `SEC-9` SHOULD FAIL: [live] Security headers on the deployed site: CSP, nosniff, frame protection, HSTS, Referrer-Policy — missing: content-security-policy, x-content-type-options, frame, referrer-policy
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
- `UI-1` MUST FAIL: Vendored vertciti DNA stylesheet (dna.css / dna-tailwind.css)
- `UI-2` SHOULD FAIL: dna-drift check wired in CI (vendored DNA cannot silently diverge)
- `OPS-1` MUST FAIL: Health endpoint (/healthz or /health)
- `OPS-3` SHOULD FAIL: Security response headers set in code (CSP / X-Content-Type-Options / frame-ancestors)
- `OPS-5` SHOULD FAIL: Structured logs with a request/trace id (OpenTelemetry-style)
- `REL-2` SHOULD FAIL: [live] Health endpoint returns 200 on the deployment — https://huiiim.github.io/helm/healthz -> 404 in 64 ms
- `PUB-2` SHOULD FAIL: Public demo or product URL registered and named in README (outsiders can see it run) — README does not mention huiiim.github.io
- `CONT-1` SHOULD FAIL: Runbook (docs/RUNBOOK.md): deploy, rollback, backup, restore, key rotation
- `CONT-2` SHOULD FAIL: Backup and restore are written down (a restore never tested is not a backup)
- `PRIV-1` SHOULD FAIL: Data handling stated: retention / what is stored / redaction (PRIVACY.md or a section)

### P0 · jarvis-architecture · 37.3 (C)

- Private repository: 18 failing check(s), 12 of them MUST. Which checks, with evidence, is recorded only in the repository's own `standards-incident` issue (STANDARDS.md §考核 6).

### P0 · vault-app · 37.2 (C)

- Private repository: 28 failing check(s), 13 of them MUST. Which checks, with evidence, is recorded only in the repository's own `standards-incident` issue (STANDARDS.md §考核 6).

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

### P1 · family-crest · 89.6 (A)

- Private repository: 5 failing check(s), 1 of them MUST. Which checks, with evidence, is recorded only in the repository's own `standards-incident` issue (STANDARDS.md §考核 6).

### P1 · vertciti-sp07-builder · 77.4 (B)

- `GOV-2` MUST FAIL: CODEOWNERS routes reviews
- `GOV-3` SHOULD FAIL: .editorconfig for consistent whitespace
- `SEC-8` MUST FAIL: Workflows set timeout-minutes (no 6h runaway jobs)

### P1 · vertciti-prototype · 77.4 (B)

- Private repository: 3 failing check(s), 2 of them MUST. Which checks, with evidence, is recorded only in the repository's own `standards-incident` issue (STANDARDS.md §考核 6).

### P1 · vertciti-chat · 71.0 (B)

- Private repository: 19 failing check(s), 4 of them MUST. Which checks, with evidence, is recorded only in the repository's own `standards-incident` issue (STANDARDS.md §考核 6).


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
