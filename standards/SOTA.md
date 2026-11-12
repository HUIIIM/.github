# SOTA 定义 · 什么叫"业内最高水平"（v1.2 · 2026-11-12）

"State of the art"不是形容词，是一组**可测量、有出处**的条款。本文件是 HUIIIM 全部产品判断"是否达到最高水平"的唯一依据；
由独立评估 AI（见 [`IVV.md`](IVV.md)）按条判定，作者本人（包括写代码的 Claude 会话）不能给自己打分。

- **来源**：条款尽量引一手资料，研究底稿见 [`research/2026-10-25-motion-interaction-nasa-dossier.md`](research/2026-10-25-motion-interaction-nasa-dossier.md)（含逐条 URL 与"未核实"标注）。
  如实记：出处为「—」（VER-5、OPS-2）或「独立审查 2026-10-25」（ARCH-5、ARCH-6、ARCH-9）的条款尚无外部一手来源；MOT-6 所引 WCAG 2.2.2、OPS-1 所引 SOC 2 在底稿中标注为 **[from prior knowledge]**，未在研究时取原文。这些在下次月度复核时补证或改写。
- **修订**：每月由独立研究会话重新取证一次；来源超过 12 个月未复核的条款降为 SHOULD，直到复核（逐条核实日期尚未记录，此规则目前由月度复核人工执行）。定义的改动走 PR，由主人合并——评估者与被评估者都不能单方面改尺子。
- **修订记录**：v1.2（2026-11-12，#125 / #86 采纳改编）增「适用画像」：哪些条款适用由仓的 `repos.json` kind 决定，不由评估者逐次判 N/A；增试点条款 DS-1、GRD-1（只对试点仓 website-qa-gates 判定）。v1.1（2026-11-09，#88 选项 A）DES-1 增列第五义「青＝中性信息」，DNA `--info` 由 ✗ 转为可判；v1.0（2026-10-25）初版。v1.0 下作出的判定不因修订失效。
- **适用面**：按下文「适用画像」，只对仓的 kind 所列条款判定；未列条款对该 kind 不适用，评估者不得改判，也不得因此扣分。
- **判定**：MUST 全过 + SHOULD ≥ 80% = 达到本阶段 SOTA；任一 MUST 不过 = 未达到，按 [`STANDARDS.md`](STANDARDS.md) §考核 记事故。
- **口径**：对外只说"按 SOTA v1.2 条款独立评估：通过 N/M"；与 NASA 相关只说"映射到 / 对齐 NPR 7150.2D（自评，Class D 画像）"，**永不**说 NASA 认证、合规、批准或"NASA 级"。

---

## 阶段 1 · 设计（DES）

| ID | 级别 | 条款 | 怎么测 | 出处 |
|---|---|---|---|---|
| DES-1 | MUST | 颜色只承担一种语义：橙＝指针、黄＝注意、绿＝正常、红＝失败/拦截、青＝中性信息（提示、说明、数据链接；**非状态、非指针**，不得用作状态灯或代替绿/红/黄）；限值越界前不着色 | 静态扫描组件 class/token；截图审（青色只出现在 info 变体与数据链接上） | vertciti DNA；Open MCT limit evaluators；[GOV.UK notification banner](https://design-system.service.gov.uk/components/notification-banner/)（中性信息与成功分立）；[Carbon notification](https://carbondesignsystem.com/components/notification/usage/)（info 与 success/warning/error 四态分立） |
| DES-2 | MUST | 白天/深夜两套主题全部走 token，无硬编码色值；文本对比度 WCAG AA | `Contrast` CI 任务 + `grep '#[0-9a-f]{6}'` 于组件 | WCAG 2.2；Stripe 感知均匀色阶 |
| DES-3 | MUST | 数字一律等宽数字（tabular-nums），位置稳定，刷新不跳版 | 组件审；截图对比 | Vercel Web Interface Guidelines；Bloomberg |
| DES-4 | SHOULD | 高密度：一屏回答"安全吗、在干什么、花了多少、可信吗"四问，无需滚动（1440×900） | 截图 + 任务计时（见 INT-6） | Linear UI redesign（密度、降噪） |
| DES-5 | MUST | 双语：界面文案走中英文案表，不写死在组件里；`<html lang>` 随语言切换 | 抽取率脚本（组件内 CJK 字面量计数） | 产品承诺"bilingual zh/en" |
| DES-6 | MUST | 空态、加载、错误三态都有诚实文案；后端不可达显示"不可达"，绝不显示 0 或假数据 | 组件测试断言三态 | STANDARDS §诚实条款 |

## 阶段 2 · 动效（MOT）

| ID | 级别 | 条款 | 怎么测 | 出处 |
|---|---|---|---|---|
| MOT-1 | MUST | 动效只表达因果或状态变化；无装饰性循环、闪光、视差 | 代码审：每个 animation/transition 必须注明对应的状态事件 | Apple HIG Motion；Vercel |
| MOT-2 | MUST | 采用 productive 令牌：70/110/150/240 ms，系统级通告 400 ms 封顶；曲线 `(0.2,0,0.38,0.9)` / `(0,0,0.38,0.9)` / `(0.2,0,1,0.9)`；无回弹 | token 文件比对；grep 未登记的 duration/cubic-bezier | IBM Carbon motion |
| MOT-3 | MUST | 只动 `opacity` 与 `transform`；禁止 `transition: all` | grep | Vercel |
| MOT-4 | MUST | 动效可打断、不阻塞输入（急停永远可点） | e2e：动画进行中点击/键入 | Apple HIG；Vercel |
| MOT-5 | MUST | 数据驱动的动效"如实"：脉冲由已封印事件触发、每跳匀速、被拦停在拦截处；积压折叠成 "+N"，不加速 | liveModel 单测 + 审计序号对照 | dossier A.2 #8 |
| MOT-6 | MUST | `prefers-reduced-motion`：位移改为瞬时或 ≤110 ms 透明度；持续 >5 s 的自动动效有暂停（Space） | e2e 在 reduced-motion 下断言 | WCAG 2.2.2；Carbon |
| MOT-7 | SHOULD | 退场比入场快一级 | token 审 | Carbon |

## 阶段 3 · 交互（INT）

| ID | 级别 | 条款 | 怎么测 | 出处 |
|---|---|---|---|---|
| INT-1 | MUST | ⌘K 指令面板、`/` 搜索、`?` 快捷键表、`G`+字母导航；同一注册表生成面板与快捷键表，单测保证无重复绑定 | 单测 + e2e | Linear；Blueprint；Raycast |
| INT-2 | MUST | 危险操作两步且独立：批准高风险、急停、退出安全模式——永远不是单键 | e2e | NPR 7150.2D SWE-134(d) |
| INT-3 | MUST | 不提前报完成：批准/工具调用显示"已批准·待封印"，直到封印事件到达；乐观更新只用于可逆、无守卫的动作并带撤销 | 组件测试 | dossier A.2 #14；Vercel |
| INT-4 | MUST | 输入响应 ≤100 ms 有反馈；>1 s 显示进度；加载指示延迟 150–300 ms 出现、至少显示 300–500 ms | e2e 计时 | NN/g；Vercel |
| INT-5 | SHOULD | URL 承载视图状态（时间范围、筛选、选中事件、抽屉），可深链 | e2e | Vercel |
| INT-6 | SHOULD | 五个标准问题（安全模式？正在跑什么？今天花了多少？最近被拦什么？审计链完好吗？）首屏 10 秒内可答 | 脚本化任务计时 | NN/g 10 s 注意力上限 |
| INT-7 | MUST | 单键快捷键在输入框内与中文输入法组字（`isComposing`）时不触发 | 单测 | Vercel locale-aware shortcuts |
| INT-8 | SHOULD | 一个全局时间控制（实时 / 固定区间），图表、示意图、审计列表、账本共用 | e2e | NASA Open MCT Time Conductor |

## 阶段 4 · 架构（ARCH）

| ID | 级别 | 条款 | 怎么测 | 出处 |
|---|---|---|---|---|
| ARCH-1 | MUST | 控制路径（网关、检查链、安全模式、急停、审批、审计封印）满足 SWE-134 a–l 自愿采纳清单，每项有测试 | 追溯矩阵（需求 ID 标在测试上，CI 生成） | NPR 7150.2D SWE-134、SWE-052 |
| ARCH-2 | MUST | 孪生预演与生产用同一份网关与检查链代码和配置；每次预演记录两者指纹并比对 | 单测 + 运行时断言 | SWE-073 "test like you fly" |
| ARCH-3 | MUST | 守卫策略、提示词、工具注册表、飞行规则的任何改动，上线前有正常与失败两类验收测试 | CI 门 | SWE-193 |
| ARCH-4 | MUST | 每个循环有上界：智能体步数、工具调用、时长、token、花费均有硬上限 | 配置审 + 单测 | JPL Power of 10 #2（意译） |
| ARCH-5 | MUST | 生产不跑开发模式；数据库迁移有版本表；进行中的运行在重启后被对账（不留孤儿） | 部署模板审 + 测试 | 独立审查 2026-10-25 |
| ARCH-6 | MUST | 健康检查反映依赖真实状态（数据库不可达 → 503） | 测试 | 独立审查 2026-10-25 |
| ARCH-7 | SHOULD | 检查链各段建成带类型端口的组件；控制台示意图由同一定义生成，不可能与实际漂移 | 代码审 | F Prime 组件/端口模型 |
| ARCH-8 | SHOULD | 工具注册表＝指令字典，指标＝遥测字典；事件分七级严重度并可节流 | 代码审 | F Prime / FPP |
| ARCH-9 | SHOULD | 单进程状态（事件总线、急停、队列）有外置方案与切换开关后再上第二个工作进程 | 设计记录 | 独立审查 2026-10-25 |

## 阶段 5 · 安全（SEC）

| ID | 级别 | 条款 | 怎么测 | 出处 |
|---|---|---|---|---|
| SEC-A1 | MUST | 授权按主体隔离，不只按租户；每条读路由都有越权回归测试 | 测试清单 | OWASP ASVS 5.0 L2（授权章节） |
| SEC-A2 | MUST | 出站请求每一跳都过 SSRF 检查，并核对实际连接地址 | 测试 | ASVS；独立审查 |
| SEC-A3 | MUST | 任意代码执行在无网络、只读、无数据卷的隔离环境中运行 | 部署 + 测试 | OWASP LLM06 Excessive Agency |
| SEC-A4 | MUST | 审计链头哈希每日锚定到系统外（只追加的外部记录） | 外部记录存在且连续 | SWE-134(f) 篡改检测 |
| SEC-A5 | MUST | 供应链：Actions 按 SHA 固定、镜像按 digest 固定、依赖按锁文件加哈希安装 | CI 扫描 | SLSA v1.2 L2；NIST SSDF |
| SEC-A6 | MUST | 控制台有 CSP；错误边界页存在 | 响应头检测 + 文件存在 | OWASP ASVS 5.0（前端安全章节） |
| SEC-A7 | SHOULD | 提示注入与过度代理按 OWASP LLM Top 10 2025 逐项有对应测试 | 测试清单 | OWASP LLM Top 10 2025 |

## 阶段 6 · 验证与发布（VER）

| ID | 级别 | 条款 | 怎么测 | 出处 |
|---|---|---|---|---|
| VER-1 | MUST | 全量测试绿；lint 与类型检查阻断式（非建议式） | CI 配置 | SWE-191 |
| VER-2 | MUST | 每个缺陷修复带"旧代码上红、新代码上绿"的回归测试 | PR 证据 | SWE-191 |
| VER-3 | MUST | 每个 PR 经独立评估（IVV.md）给出判定后才能报"完成" | PR 评论存在 | SWE-087/088 同行评审（意译） |
| VER-4 | SHOULD | 发布产物可复现、带 SBOM 与签名；回滚＝重新部署上一个标签 | 发布流程 | SLSA；SSDF PS.3 |
| VER-5 | SHOULD | 前后端契约由 OpenAPI 生成并在 CI 比对 | CI | — |

## 阶段 7 · 运营（OPS）

| ID | 级别 | 条款 | 怎么测 | 出处 |
|---|---|---|---|---|
| OPS-1 | MUST | 异地备份 + 每季度计时恢复演练，记录 RTO/RPO | 演练记录 | SOC 2 可用性准则（就绪口径） |
| OPS-2 | MUST | 结构化日志（含 trace_id）、两条 SLO（可用性、运行成功率）与告警 | 配置 + 告警记录 | — |
| OPS-3 | SHOULD | 实时界面有 LIVE / STALE / PAUSED 心跳指示 | e2e | Open MCT；dossier A.2 #9 |

---

## 适用画像（按 `repos.json` kind，v1.2 新增）

本尺子最初为运营控制台写成（#40 §R：用在设计系统＋评分器仓上，45 条有 27 条不适用）。v1.2 起适用面由 [`repos.json`](repos.json) 的 `kind` 决定。
只对 `status: active` 的仓；archive / placeholder 只按 [`STANDARDS.md`](STANDARDS.md) 的检查表评，不评 SOTA。

| kind | 适用条款 | 理由 |
|---|---|---|
| `app` | 全部条款（DES、MOT、INT、ARCH、SEC、VER、OPS） | 本尺子的原始对象：有界面、有后端、有运行时 |
| `site` | DES-1、DES-2、DES-3、DES-5、DES-6；MOT-1、MOT-2、MOT-3、MOT-6、MOT-7；INT-4、INT-7；SEC-A5、SEC-A6；VER-1–VER-4；OPS-2 | 有界面、无智能体控制路径与数据库 |
| `meta` | DES-1、DES-2、DES-3、DES-5；MOT-1、MOT-2、MOT-3、MOT-6、MOT-7；SEC-A5；VER-1–VER-4；OPS-2 | 本仓：设计系统（DNA）＋评分器；OPS-2 指记分卡新鲜度 SLO |
| `library` | SEC-A5；VER-1–VER-4 | 被别人调用的代码：供应链与验证 |
| `tool` | ARCH-4；SEC-A2、SEC-A5；VER-1–VER-4；OPS-2 | 自动运行的工具：循环有界、出站受控、运行可观测 |
| `skill` | SEC-A5、SEC-A7；VER-1–VER-4 | 智能体技能：提示注入与过度代理测试 |
| `profile` | DES-1、DES-2、DES-5；VER-3 | 公开展示面 |
| `docs` | VER-3 | 只有文字 |

**分类来源与对齐**：#125 要求画像与 REG-097 类目对齐、不另起分类学。REG-097 不在本仓，本 PR 的会话读不到（卡点写回 #125）；
上表用的是本仓已有的、审计器每天在用的 `repos.json` kind，是现成分类，不是新分类。REG-097 类目与之有出入时，以中枢在 #125 给出的映射为准改本表。

## 试点条款（v1.2 新增，先只对试点仓判定）

#125 ③：设计系统与评分器条款先在试点仓 **website-qa-gates**（kind `skill`：一个网站发布前质检评分器，自带引用 DNA 的演示站）验一轮，再决定全量。
试点期间这两条只对 website-qa-gates 判定，不进其他仓的分母；全量时在上表按 kind 加入并升版。

| ID | 级别 | 条款 | 怎么测 | 出处 |
|---|---|---|---|---|
| DS-1 | MUST（试点） | 非文本对比度：界面组件的边界（输入框、按钮描边）、焦点指示与状态图形，对相邻颜色 ≥ 3:1，**每个主题、每个表面**（页面、柔底、卡片、反色面）都成立，并由真实浏览器门禁在 CI 中测量，不只是计算 | 浏览器门禁逐表面测焦点环与组件边界的渲染颜色 | [WCAG 2.2 SC 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) |
| GRD-1 | MUST（试点） | 评分器自带夹具语料：每个机器判定项至少有一个「必过」与一个「必拦」用例；用例↔判定项的矩阵由测试标注生成，CI 校验矩阵完整；在语料上的误放行数为 0 | 读矩阵；CI 上跑语料 | [Semgrep rule testing](https://semgrep.dev/docs/writing-rules/testing-rules)（每条规则带 `ruleid:` 必中与 `ok:` 必不中的注释用例） |

**试点验证（2026-11-12，website-qa-gates `2291edd`，只读）**：

| 条款 | 结果 | 证据 | 未检 |
|---|---|---|---|
| DS-1 | **测量推翻了计算；门禁已建** | 演示站引用的 DNA 为 **v4.0.0**（`demo/www/dna.css`），按令牌计算全部 ≥ 3:1（最低：浅色柔底焦点环 3.07），演示页不用任何反色面。本仓随后建了测量门禁 `standards/a11y/nontext_audit.js`（#149）：它在 DNA 4.1.1 上实测到**黄色强调面的焦点环是橙色，2.28:1**（强调柔底 2.02:1）——令牌计算说「黑色，14.08:1」，因为 `--focus-ring` 在 `:root` 上就已解析，表面只改 `--pointer` 传不到它。DNA 4.1.2（#149）修复后两页 × 浅/深 × 390/1280 共 8 组全过，CI 还要求门禁在已知缺陷页上报恰好 4 处。这正是本条款要「测量、不只计算」的理由。 | website-qa-gates 尚未接入 `nontext_audit.js`（它的 G16 是 axe，不覆盖 1.4.11）；接入并在其 CI 上跑通前，试点仓上的 DS-1 判为**未达**。 |
| GRD-1 | 矩阵达标 | `docs/TRACEABILITY.md`（由 `tools/trace-matrix.py --write` 生成，CI `--check`）列出 21 个机器门禁，每个都有 pass 与 fail 用例；`trace-matrix.py --check` 输出「TRACE OK: 21 个机器门禁均有正反用例」。 | 34 个门禁中 13 个为人工门禁，不在机器语料内（条款只要求机器判定项）。语料上的误放行数需要跑测试：本会话不执行外仓代码，CI 结果读取需要该仓的 API 权限，未检。 |

**全量前的条件**：DS-1 的测量门禁已在本仓（#149），还需 website-qa-gates 接入并跑通；GRD-1 需要读到试点仓 CI 的语料运行结果。两项满足后，按 kind 把 DS-1 加入 `meta`、`site`、`app`，把 GRD-1 加入 `meta`（本仓 `audit.py`）与评分器类 `skill`，并升版。

## 不算数的（"表演"清单，禁止拿来宣称）

CMMI 评级、"NASA IV&V"字样（我们叫"独立评估"）、全产品 100% MC/DC、在 Python/TS 里逐字套 Power of 10 的 C 语言条款、NASA-STD-1006、任何 NASA 名称或徽标作背书。见底稿 B.7。
