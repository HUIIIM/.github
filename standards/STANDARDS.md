# vertciti 工程与产品标准 v2.0

**一句话：每个仓库都按行业最高的公开标准衡量，由独立于仓库的脚本每天打分并公开；没到线就是事故，事故自动立案、自动派修。**

本标准适用于 [@HUIIIM](https://github.com/HUIIIM) 下所有自有仓库（上游 fork 除外）。
每一条都对应一个公开的行业框架。除「对外消息 MSG」三条（不计入 audit.py 分数：MSG-1 由 [`check_messaging_dns.py`](check_messaging_dns.py) 每日检查公司发信域并单列在记分卡上，MSG-2/3 人工核对）外，每一条都能被 [`audit.py`](audit.py) 自动检查。
`MUST` 不达标 = 不合格；`SHOULD` 不达标 = 要有书面理由。

```bash
python3 standards/audit.py ~/src                 # 逐仓列出未达标项与分数
python3 standards/audit.py ~/src --live --md     # 含线上探测的 markdown 记分卡（SCORECARD.md）
python3 standards/audit.py ~/src --live --json standards/scorecard.json
python3 standards/audit.py ~/src --incidents     # 低于线的仓库（JSON，给立案器）
```

最新记分卡：[`SCORECARD.md`](SCORECARD.md)（每日由 [`standards-audit`](../.github/workflows/standards-audit.yml) 重算并提交）。

仓库类型与状态登记在 [`repos.json`](repos.json)：`app` / `library` / `skill` / `tool` /
`site` / `docs` / `profile` / `meta`，状态 `active` / `archive` / `placeholder` / `fork`。
检查项按类型和状态自动适用——档案仓只查治理与安全，不要求它"继续开发"。

## 考核（§考核 · 独立评估，v2.0 新增）

**原则**

1. **独立。** 评估脚本住在本仓库，按自己的日程跑，读被评仓库只读；被评仓库改不了评分规则，也改不了发布结果。
2. **量化。** 每条检查项有权重：`MUST` 3 分、`SHOULD` 1 分；分数 = 得分 / 适用总分 × 100。
   不适用的项从分母剔除；**不能探测的项（没有公开 URL、工具缺失）算未通过**——"没测"不是"通过"（2026-10-23 分层校准事故的教训）。
3. **有线。** 等级：S ≥95 · A++ ≥90 · A ≥85 · B ≥70 · C <70。**业内最高水平线 = A++**（分数 ≥90 且无 MUST 不通过）。
4. **没到线就是事故。** 低于线的仓库自动立案：
   | 严重度 | 触发 | 处置时限 |
   |---|---|---|
   | P0 | 分数 <70，或安全类 MUST 不通过（SEC-1 泄密扫描 / SEC-6 最小权限 / GOV-1 许可证 / REL-1 线上不可达） | 24 小时 |
   | P1 | 分数 <85，或任一 MUST 不通过 | 72 小时 |
   | P2 | 分数 <90 | 7 天 |
   立案 = 在该仓库开 issue（标签 `standards-incident`、`P0/P1/P2`），正文是失败项与证据；同一事故不重复开，只更新。
5. **自动升级。** 每个事故同时派一次自动修复：能用 [`bootstrap.py`](bootstrap.py) 补齐的（CODEOWNERS、工作流、Dependabot、超时、权限）直接出 PR；
   需要真内容的（PRODUCT.md、CHANGELOG、RUNBOOK、evals）由 Miao / Claude 会话起草 PR。**只开 PR，不合并**——合并是人的决定。

   **实现状态（如实记，2026-10-27）**：第 4–5 条目前只有一部分在跑。`standards-audit` 工作流在配置了 `STANDARDS_TOKEN` 时开/更新事故 issue（仅 `active` 仓），
   但**不会自动关闭**已达线的事故，也**不会自动调用 bootstrap 出 PR**；这两步现由人工或每日 standards 例行会话完成，直到实现为止（见独立评估 #17 P1-5）。
6. **公开。** 记分卡（含不及格的）发布在 [`SCORECARD.md`](SCORECARD.md) 与 vertciti.com/standards。红的也发：这是"建造过程公开"的字面意思。
7. **对标再升级。** 每季度把每个产品与同类最强的公开产品逐项对比（功能、性能、安全、可访问性、文档），差距写进该仓库的 `docs/PRODUCT.md`「路线图」，并新增检查项把它变成可测的线。线只升不降。

**流程**

```
每日 03:40 UTC   standards-audit.yml：拉取全部仓库 → audit.py --live → 提交 SCORECARD.md / scorecard.json
同日             自动立案器：对低于线的仓库开/更新 issue；bootstrap 可补的直接开 PR；其余派会话起草 PR
人工             合并 PR；事故 issue 再次达线后关闭（自动关闭尚未实现，目前人工关闭）
```

**v2.0 新增检查项（"没想到的"）**：GOV-6 仓内 SECURITY.md · SEC-9 线上安全响应头实测 · SEC-10 依赖锁定可复现 ·
QA-5 浏览器级测试/对比度门禁 · DOC-11 中英双语 · UI-2 dna-drift 接入 · OPS-5 结构化日志与请求 ID ·
REL-1/REL-2 线上可达与健康检查实测 · PERF-1 首响 ≤800 ms 实测 · PUB-1 robots/sitemap/llms.txt · PUB-2 公开演示地址 ·
CONT-1/CONT-2 运行手册与备份恢复 · PRIV-1 数据处理声明 · AI-1/AI-2 评测记录与提示注入测试 · LEGAL-1 第三方声明。

## 最高水平定义与独立评估

"是否达到业内最高水平"按 [`SOTA.md`](SOTA.md) 的可测条款判定（设计、动效、交互、架构、安全、验证发布、运营七个阶段，每条带一手出处），由与作者隔离的 AI 按 [`IVV.md`](IVV.md) 独立评估；作者不给自己打分。

## 对标框架

| 维度 | 对标 | 我们的门槛 |
|---|---|---|
| 供应链安全 | [OpenSSF Scorecard](https://scorecard.dev) | 每个活跃仓库发布 Scorecard；目标 ≥ 8.0 |
| 开源成熟度 | [OpenSSF Best Practices](https://www.bestpractices.dev) | 活跃代码仓达 "passing" 级 |
| 应用安全 | [OWASP ASVS 5.0](https://owasp.org/www-project-application-security-verification-standard/) | 对外服务按 Level 2 自查 |
| 构建溯源 | [SLSA](https://slsa.dev) | 发布产物 Level 2（GitHub 构建 + provenance） |
| 无障碍 | [WCAG 2.2](https://www.w3.org/TR/WCAG22/) | AA；颜色对比由 DNA `build.py` 强制 |
| 性能 | [Core Web Vitals](https://web.dev/vitals/) | LCP < 2.5s、INP < 200ms、CLS < 0.1（p75） |
| 配置 | [Twelve-Factor](https://12factor.net) | 配置走环境变量；`.env.example` 写全；`.env` 不入库 |
| 版本 | [SemVer](https://semver.org) + [Keep a Changelog](https://keepachangelog.com) + [Conventional Commits](https://www.conventionalcommits.org) | 每个发布有版本号与变更记录 |
| 可观测 | [OpenTelemetry](https://opentelemetry.io) 语义约定 | 结构化日志（JSON）、请求 ID、健康检查 |

## 检查项

### 治理 GOV
- **GOV-1 MUST** 有 LICENSE 文件。许可证是法律决定：未定稿的（如 BSL pending GC）在 README 写明状态，不要猜。
- **GOV-2 MUST** 有 `CODEOWNERS`——每个 PR 自动指派审阅人。
- **GOV-3 SHOULD** 有 `.editorconfig`。
- **GOV-4 MUST** README 顶部如实写状态（active / early / mock / archive）。
- **GOV-5 MUST** 档案仓 README 第一屏有档案横幅。
- **GOV-6 SHOULD** 仓内有 `SECURITY.md`（漏洞上报路径不只靠组织默认文件）。

### 安全与供应链 SEC
- **SEC-1 MUST** CI 跑 secret 扫描（gitleaks）。
- **SEC-2 MUST** Dependabot 覆盖 `github-actions` 和仓库里的每个包生态（pip / npm / docker）。
- **SEC-3 MUST** 代码仓 PR 跑 CodeQL。
- **SEC-4 SHOULD** PR 跑 dependency-review，拦截新引入的已知漏洞。
- **SEC-5 SHOULD** 发布 OpenSSF Scorecard。
- **SEC-6 MUST** 每个 workflow 声明最小权限 `permissions:`（默认 `contents: read`）。
- **SEC-7 SHOULD** `.env.example` 列出全部配置项；`.gitignore` 忽略 `.env`。
- **SEC-8 MUST** 每个 job 设 `timeout-minutes`——防止失控任务跑满 6 小时。
- **SEC-9 SHOULD**（线上实测）部署站响应头齐全：CSP、`X-Content-Type-Options: nosniff`、frame 保护、HSTS、Referrer-Policy。
- **SEC-10 SHOULD** 依赖可复现：每个 manifest 旁有锁文件，或 requirements 全部 `==` 钉死。
- **SEC-11 MUST** workflow 引用的每个 action 必须钉全长 commit SHA（40 位十六进制），禁止 tag／分支钉（如 `@v7`、`@main`）；本地 action（`./` 前缀）与 docker 镜像引用不在此列。
- Actions 钉版形式统一：核心 action 亦按 SEC-11 钉全长 SHA、行尾注释标明对应版本，如 `actions/checkout@<40 位 SHA>  # v7`、`actions/setup-python@<40 位 SHA>  # v7`、`actions/setup-node@<40 位 SHA>  # v7`。

### 质量 QA
- **QA-1 MUST** 代码仓 CI 在 PR 上跑测试。
- **QA-2 MUST** CI 强制 lint/format（ruff / eslint / prettier）。
- **QA-3 SHOULD** pre-commit 钩子与 CI 一致。
- **QA-4 SHOULD** 应用仓 CI 跑类型检查（mypy / pyright / tsc）。
- **QA-5 SHOULD** 应用仓 CI 有浏览器级测试或对比度门禁（Playwright / contrast）。

### 产品全套 DOC
每个产品对外都是"全套"：

- **DOC-1 MUST** README 有 30 秒快速开始。
- **DOC-2 MUST** `docs/PRODUCT.md` 产品一页纸（模板见 [`templates/PRODUCT.md`](templates/PRODUCT.md)）：
  解决什么问题、给谁、怎么用、为什么是我们、证据、现状与边界、路线图、衡量指标。
- **DOC-3 MUST** `CHANGELOG.md`。
- **DOC-4 SHOULD** 架构文档或架构图。
- **DOC-5 SHOULD** README 有真实截图/GIF（不摆拍：真实运行录制）。
- **DOC-6 MUST** README 回链 [vertciti.com](https://vertciti.com)。
- **DOC-7 SHOULD** README 有"安全"与"许可证"小节。
- **DOC-8 MUST** README 左对齐，机构文风：不用 `align="center"` / `<center>`，首屏是「名称 → 一句话说清是什么、给谁 → 事实表（状态 / 部署 / 许可证 / 演示 / 联系）」，
  不放口号、感叹、无出处的竞品价格或比较（"别家一年五位数"这类话没有来源就不写）。骨架见 [`templates/README.md`](templates/README.md)。
- **DOC-9 MUST** README 不放徽章条（shields.io / `badge.svg`）。私有仓的 Actions 徽章对没有权限的人、以及 GitHub 手机 App 一律显示成「?」，
  而且徽章墙读起来像个人项目。CI、版本、许可证写进事实表，用文字。
- **DOC-10 MUST** README 里的图片用公开可访问的 `https://` 地址（产品演示站或 vertciti.com 的静态资源）。私有仓的相对路径图片在手机 App、
  包索引和转发出去的链接里都会坏成「?」。
- **DOC-11 SHOULD** 中英双语：README 双语或有本地化 UI（zh + en）。

### 设计 UI
- **UI-1 MUST** 有界面的仓库 vendor DNA 样式表（见 [`../design/`](../design/README.md)），
  并在 CI 里接 `dna-drift` 检查。
- **UI-2 SHOULD** `dna-drift` 已接入 CI（vendored 样式不能悄悄偏离）。

### 运维 OPS
- **OPS-1 MUST** 服务暴露健康检查端点（`/healthz`）。
- **OPS-2 SHOULD** 容器有 `HEALTHCHECK`。
- **OPS-3 SHOULD** 设安全响应头：CSP、`X-Content-Type-Options: nosniff`、`frame-ancestors`/`X-Frame-Options`、`Referrer-Policy`。
- **OPS-4 SHOULD** 容器以非 root 用户运行。
- **OPS-5 SHOULD** 结构化日志带请求/追踪 ID（OpenTelemetry 语义）。

### 可靠性与公开 REL / PERF / PUB（线上实测，需 `repos.json` 登记 `url`）
- **REL-1 MUST** 部署地址 12 秒内应答（2xx/3xx）。没有公开地址 = 未探测 = 未通过（把差距公开，不藏）。
- **REL-2 SHOULD** 部署的健康检查返回 200。
- **PERF-1 SHOULD** 首页从评估器处首响 ≤ 800 ms。
- **PUB-1 SHOULD**（站点）`robots.txt`、`sitemap.xml`、`llms.txt` 均可访问——搜索与 AI 可发现性。
- **PUB-2 SHOULD**（应用）登记了公开演示/产品地址且 README 写明——外人能看到它跑。

### 连续性、隐私、AI、法务 CONT / PRIV / AI / LEGAL
- **CONT-1 SHOULD** 有运行手册 `docs/RUNBOOK.md`：部署、回滚、备份、恢复、密钥轮换。
- **CONT-2 SHOULD** 备份与恢复写成步骤（没演练过恢复的备份不算备份）。
- **PRIV-1 SHOULD** 写明数据处理：存什么、留多久、怎么脱敏（`PRIVACY.md` 或章节）。
- **AI-1 SHOULD** 用 LLM 的应用有评测且有记录（`evals/` 或 CHANGELOG/PRODUCT 中的评测结果），不靠口头。
- **AI-2 SHOULD** 用 LLM 的应用有提示注入 / 不可信内容的测试。
- **LEGAL-1 MUST** 含 vendored 第三方代码的仓库有 `THIRD_PARTY_NOTICES.md` / `ATTRIBUTION.md` / `NOTICE`。

### 对外消息 MSG
面向真人发邮件或短信的系统，按 [MESSAGING.md](MESSAGING.md) 逐条对齐（发信身份、内容、可靠性、短信、安全、合规、可观测）。
- **MSG-1 MUST** 发信域通过 [`check_messaging_dns.py`](check_messaging_dns.py) 的 AUTH 检查（SPF/DKIM≥2048/DMARC 进档/MTA-STS/TLS-RPT/CAA）。
- **MSG-2 MUST** 一次性验证码只在 dev 可落日志；生产日志不出现验证码/明文 token，邮箱手机号脱敏。
- **MSG-3 MUST** 发送带幂等键、抑制表、退信/投诉回执；缺 provider 时显式报错而非降级写日志。

```bash
python3 standards/check_messaging_dns.py vertciti.com --selector resend --md
```

## 诚实条款（高于一切检查项）

vertciti 的品牌是"建造过程公开，接受验证"。因此：

- 数字只写测得的；徽章只挂真实跑的 CI；没有的功能不写"即将支持"。
- 截图和 GIF 必须是真实运行录制。
- 档案就是档案：不为了"看起来活跃"而翻新历史快照。
- 检查项可以靠造假通过的（比如空 CHANGELOG），视为不通过。
