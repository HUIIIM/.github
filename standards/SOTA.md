# SOTA 定义 · 什么叫"业内最高水平"（v1.0 · 2026-10-25）

"State of the art"不是形容词，是一组**可测量、有出处**的条款。本文件是 HUIIIM 全部产品判断"是否达到最高水平"的唯一依据；
由独立评估 AI（见 [`IVV.md`](IVV.md)）按条判定，作者本人（包括写代码的 Claude 会话）不能给自己打分。

- **来源**：每条都引一手资料，研究底稿见 [`research/2026-10-25-motion-interaction-nasa-dossier.md`](research/2026-10-25-motion-interaction-nasa-dossier.md)（含逐条 URL 与"未核实"标注）。
- **修订**：每月由独立研究会话重新取证一次；来源超过 12 个月未复核的条款自动降为 SHOULD，直到复核。定义的改动走 PR，由主人合并——评估者与被评估者都不能单方面改尺子。
- **判定**：MUST 全过 + SHOULD ≥ 80% = 达到本阶段 SOTA；任一 MUST 不过 = 未达到，按 [`STANDARDS.md`](STANDARDS.md) §考核 记事故。
- **口径**：对外只说"按 SOTA v1.0 条款独立评估：通过 N/M"；与 NASA 相关只说"映射到 / 对齐 NPR 7150.2D（自评，Class D 画像）"，**永不**说 NASA 认证、合规、批准或"NASA 级"。

---

## 阶段 1 · 设计（DES）

| ID | 级别 | 条款 | 怎么测 | 出处 |
|---|---|---|---|---|
| DES-1 | MUST | 颜色只承担一种语义：橙＝指针、黄＝注意、绿＝正常、红＝失败/拦截；限值越界前不着色 | 静态扫描组件 class/token；截图审 | vertciti DNA；Open MCT limit evaluators |
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

## 不算数的（"表演"清单，禁止拿来宣称）

CMMI 评级、"NASA IV&V"字样（我们叫"独立评估"）、全产品 100% MC/DC、在 Python/TS 里逐字套 Power of 10 的 C 语言条款、NASA-STD-1006、任何 NASA 名称或徽标作背书。见底稿 B.7。
