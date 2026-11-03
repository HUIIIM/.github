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
- Workflows (`.github/workflows/`). Required checks: **gitleaks**, **lint**,
  **typecheck** (lint and typecheck are the two jobs of `quality.yml`).
  | File | Name | Runs on | Role |
  |---|---|---|---|
  | `gitleaks.yml` | Secret scan (gitleaks) | push, PR, schedule | secret scanning (required) |
  | `quality.yml` | Quality gate | push, PR | `lint` (ruff) + `typecheck` (mypy) (required) |
  | `standards-tests.yml` | standards-tests | push, PR | unit tests: discovers every `standards/test_*.py` |
  | `standards-audit.yml` | standards-audit | daily schedule, dispatch, PR | `assess`: grade the fleet, publish the card PR, file incidents; `check`: PR-safe dry run |
  | `card-freshness.yml` | card-freshness | daily schedule, dispatch | fails when the published card on `main` is older than 36 h (freshness SLO, STANDARDS §考核 6) |
  | `codeql.yml` | CodeQL | push, PR, schedule | SAST for this repo's Python |
  | `scorecard.yml` | Scorecard | push, schedule, branch-protection change | OpenSSF Scorecard |
  | `design.yml` | design | push, PR (design paths) | DNA token build check (contrast matrix, DTCG export) + browser contrast and layout gates |
  | `dna-drift.yml` | dna-drift | `workflow_call` | reusable: product repos check their vendored DNA |
  | `claude.yml` | Claude Code | dispatch, `@claude` in issues/comments/reviews | Claude Code action for jarvis-task runs |

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


## 三自与能力跃升（董事长令 2026-11-01）

1. **全自动完成、自主决定、自主研发**：每个项目的活都要想办法全自动完成、自主决定、自主研发。遇到需要人介入的环节，先穷尽自动化路径，并把卡点与已试路径写回 issue，不许默认等人。
2. **持续提升 Jarvis 的全自动化与自主决策**：干活同时持续回答——Jarvis 的全自动化能力与自主决策还能怎么提升；发现即在本仓开 improvement issue（带预期收益与改法），不许只记在会话里。
3. **未想到项盘点**：主动盘点董事长没想到的能力与资源——新工具、新通道、新数据源、闲置资产，逐项带验证方法与接入成本。
4. **串联与闭环**：每个项目的产出要指明喂给谁、谁的产出喂给我；闭环缺口（孤儿产出、无人消费的报告、开了不关的环）当缺陷处理并开单。
5. **State of the Art 铁律**：每个项目在每一个面（含从未碰过的面）都要 state of the art——逐面拿最强参照对标（代码质量／架构／设计／安全／性能／测试／文档／体验…），差距开 gap issue 并标当前等级与目标等级；未检面显性列为「未检面」（未检≠默认合格）；验收只认对标证据或实测数据，自报通过、「差不多／凑合／部分通过」一律算未完成。
6. **永不向董事长提问**：会话执行中遇分歧、冲突或需裁决事项，永不在会话界面向董事长提问、不等他点选——默认按自己给出的 Recommended 方案继续执行，并把裁决请求写成仓内 issue（打 jarvis-task 标＋注明「待中枢裁」），由中枢在 GitHub 面裁决回执。复核/审计类长活的结论一律回仓（issue/PR 评论）为唯一交付面，不以会话内长文呈董事长。
7. **建议入单打标、回执必读**：会话产出的改进建议一律开 improvement issue 并打 `claude-advice` 标签，不许只散在 PR 评论或会话文本里（散件由 GitHub 团队回收补单）；中枢/团队的处置结论（采纳附工单指针／改编／不采附理由）写回原 issue。**开工前先读本仓未闭环建议的处置回执**，据此校准，不重复提已处置建议。建议与中枢裁决冲突时写仓内 issue 交中枢 48h 裁，永不呈董事长。
