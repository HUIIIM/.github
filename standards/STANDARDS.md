# vertciti 工程与产品标准 v1.0

**一句话：每个仓库都按行业最高的公开标准衡量，并且由脚本检查，而不是靠自觉。**

本标准适用于 [@HUIIIM](https://github.com/HUIIIM) 下所有自有仓库（上游 fork 除外）。
每一条都对应一个公开的行业框架，每一条都能被 [`audit.py`](audit.py) 自动检查。
`MUST` 不达标 = 不合格；`SHOULD` 不达标 = 要有书面理由。

```bash
python3 standards/audit.py ~/src          # 逐仓列出未达标项
python3 standards/audit.py ~/src --md     # 输出 markdown 记分卡
```

仓库类型与状态登记在 [`repos.json`](repos.json)：`app` / `library` / `skill` / `tool` /
`site` / `docs` / `profile` / `meta`，状态 `active` / `archive` / `placeholder` / `fork`。
检查项按类型和状态自动适用——档案仓只查治理与安全，不要求它"继续开发"。

## 对标框架

| 维度 | 对标 | 我们的门槛 |
|---|---|---|
| 供应链安全 | [OpenSSF Scorecard](https://scorecard.dev) | 每个活跃仓库发布 Scorecard；目标 ≥ 8.0 |
| 开源成熟度 | [OpenSSF Best Practices](https://www.bestpractices.dev) | 活跃代码仓达 "passing" 级 |
| 应用安全 | [OWASP ASVS 4.0](https://owasp.org/www-project-application-security-verification-standard/) | 对外服务按 Level 2 自查 |
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

### 安全与供应链 SEC
- **SEC-1 MUST** CI 跑 secret 扫描（gitleaks）。
- **SEC-2 MUST** Dependabot 覆盖 `github-actions` 和仓库里的每个包生态（pip / npm / docker）。
- **SEC-3 MUST** 代码仓 PR 跑 CodeQL。
- **SEC-4 SHOULD** PR 跑 dependency-review，拦截新引入的已知漏洞。
- **SEC-5 SHOULD** 发布 OpenSSF Scorecard。
- **SEC-6 MUST** 每个 workflow 声明最小权限 `permissions:`（默认 `contents: read`）。
- **SEC-7 SHOULD** `.env.example` 列出全部配置项；`.gitignore` 忽略 `.env`。
- **SEC-8 MUST** 每个 job 设 `timeout-minutes`——防止失控任务跑满 6 小时。
- Actions 版本统一：`actions/checkout@v7`、`actions/setup-python@v7`、`actions/setup-node@v7`。

### 质量 QA
- **QA-1 MUST** 代码仓 CI 在 PR 上跑测试。
- **QA-2 MUST** CI 强制 lint/format（ruff / eslint / prettier）。
- **QA-3 SHOULD** pre-commit 钩子与 CI 一致。
- **QA-4 SHOULD** 应用仓 CI 跑类型检查（mypy / pyright / tsc）。

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

### 设计 UI
- **UI-1 MUST** 有界面的仓库 vendor DNA 样式表（见 [`../design/`](../design/README.md)），
  并在 CI 里接 `dna-drift` 检查。

### 运维 OPS
- **OPS-1 MUST** 服务暴露健康检查端点（`/healthz`）。
- **OPS-2 SHOULD** 容器有 `HEALTHCHECK`。
- **OPS-3 SHOULD** 设安全响应头：CSP、`X-Content-Type-Options: nosniff`、`frame-ancestors`/`X-Frame-Options`、`Referrer-Policy`。
- **OPS-4 SHOULD** 容器以非 root 用户运行。

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
