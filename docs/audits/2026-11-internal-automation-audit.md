# 公司内部全自动化系统 · 独立审查报告与提升方案

- 令源：董事长 2026-11-11 20:18 EST 亲令，经中枢转 Claude 自主开发组。执行席：Claude Code 网页席，仓 `HUIIIM/.github`。
- 仓内载体：issue #150（开工前申报在其文末）；本文件是文档版，随 PR #165。
- 取数时点：2026-11-12 01:27Z、2026-11-12 20:17Z、2026-11-17 00:46Z 三次。每个数字的查询式见 §9，可复跑。
- **交付迟到，如实记**：首切死线 2026-11-13 20:15 ET 未达。本席三度停转（11-12 约 18 小时、11-12 至 11-17 约 100 小时、11-17 约 17 小时），三次都是人工在会话里键入「继续」才恢复；停转原因本席未能取证。这段经历本身进了证据（§3.5）。
- 公开性：本仓公开。本文不落凭证、个人线／家人线／案件线内容和内部坐标；引自私有仓 `jarvis-architecture` 的内容只给「文件:行」指针和本席实测数；会话只报聚合数。

## 0. 结论先行

**一句话**：这套系统的传感器测的是「执行者活着、动作发生过」，环的终点是「写下一行字」；它几乎不测「工作到了末态」，也不测「被控对象变了没有」。所以它能在全绿的同时，让一条 PASS 判定躺 13 天没人合并，让 30 件裁决请求全部超时，让停席靠人键入「继续」恢复。

五个机制根因（后文每条发现都归到其中之一）：

| 根 | 说明 | 最硬的一条证据 |
|---|---|---|
| R1 测存活不测末态 | 探针的对象是账号、进程、调度器，不是工作产物 | 账号探活连报 PASS 期间大批会话停席（样本 A）；本席三度停转共约 135 小时，无任何机制点名 |
| R2 环的终点是一行字 | 点名、裁字、回执都以「写了」为完成，不以「状态变了」为完成 | 11-13「全清」给 184 件 issue 写了裁字，其中 150 件至今仍开；#150 在报告成文前被裁定「结论并轨、关单」 |
| R3 入口没有背压 | 发现由机器批量产生，处置集中在合并席、裁决席和董事长 | 10-22 至 11-12 全舰队新开 issue 402 件、关闭 68 件 |
| R4 监测与被监测同因 | 同调度库、同订阅额度、同模型族、同一席 | 唯一的外部死人开关没上膛，且只以设计频次的 2.8% 在跑；评估席同时是作者席 |
| R5 计时器挂在启动上，不挂在停留上 | 没有任何一件工作项带着「在当前状态最多停多久」的计时器 | jarvis-task 121 件中 109 件没有状态标签，状态机没在跑 |

**本席已直接改掉的**（PR #165，draft，不自合）：GitHub 面闭环末态巡检 `standards/loop_watch.py`、回执回读闸 `standards/receipt_check.py`、会话末态巡检规程 `standards/session-patrol.md`，均带测试或验收。VM 侧够不到的六处给了可直接套用的改稿全文（§6.3）。

**最值得先做的三件**：会话末态巡检上线（I-01）；外部死人开关上膛并按真实节律重定阈值（I-02）；把「裁字」和「销账」分开计数，销账必须带回读指针（I-03）。

## 1. 范围、方法、取证边界

审查对象是简报所列五块：① cron 舰队、② heartbeat 监测面、③ 每日自检、④ 派工与台账闭环、⑤ 外部执行面纳管。

方法是控制环分析：对每个环问四件事——传感器测的是什么、设定值写在哪、执行器是谁、反馈有没有回到比较点；再做队列流量核算（入口速率、出口速率、在制品龄）。

| 块 | 取证深度 | 证据来源 |
|---|---|---|
| ① cron 舰队 | 口径与结构层。任务体、调度库不可达 | 简报实测数；`jarvis-architecture` 舰队图（2026-11-01 快照） |
| ② heartbeat | 对外痕迹层。检查清单原文、点名台账不可达 | 心跳痕迹分支；外部死人开关的运行记录；简报描述 |
| ③ 每日自检 | 机制文本层。日报原文不可达 | 架构包机制描述 |
| ④ 派工与台账 | GitHub 面全量实测。decision-log 与内部台账不可达 | 搜索 API 全舰队 issue／PR；本仓规程原文 |
| ⑤ 外部执行面 | 全量实测 | 平台会话接口；GitHub 面；本席自身经历 |

样本 A／B／C 按简报口径作为给定实证，未复证。`jarvis-architecture` 2026-11 架构审计（O／U／B／A／X／L／F／S／V 系列）已覆盖的条目，本文只引不重提。未取证项集中列在 §8。

## 2. 必答一：名义自动、实际靠人发现的面

| # | 面 | 自动声称 | 实际发现者 | 证据 |
|---|---|---|---|---|
| 1 | 会话停席 | 账号探活每 6h 一轮 | 董事长截图（11-09、11-11）；11-12 与 11-17 人工逐席键入「继续」 | 样本 A；§3.5 |
| 2 | PASS 判定后的合并 | IVV 每 6h 判一轮，Jarvis 合并 | 无人。本审点出 | #127：11-04 判 PASS，11-17 仍开 |
| 3 | 裁决请求 48h 时限 | `CLAUDE.md` 三自第 7 条 | 无人。本审点出 | 标题标「待中枢裁」30 件，30 件超 48h（11-17） |
| 4 | jarvis-task 状态机 | 标签即状态 | 无人。本审点出 | 121 件中 109 件无状态标签（11-17） |
| 5 | 建议的处置回执 | 三自第 7 条「处置结论写回原 issue」 | 董事长 11-12「160 件全清」令 | 全清评论自述令源；零回执件 26→0 |
| 6 | 后台回执的真实性 | 回执 | 当轮人工回读 | 样本 B |
| 7 | 调度器停摆 | heartbeat 与带外哨互守，外加外部死人开关 | 若发生，只能是人 | 外部腿未上膛（§4.2） |
| 8 | 外部探针自己的节律 | 设计每 10 分钟 | 本审量出 | 228h 内 39 次，设计应为 1368 次 |
| 9 | GitHub 定时器守时 | cron 写 03:40Z | #145 发现注释不符；本审量化 | 14 次日运行实际起跑 09:57Z–12:08Z |
| 10 | 舰队数目口径 | 调度库即正本 | 中枢在发简报前直查才发现 | 派单口径 385，实测启用 355 |
| 11 | 全公司广播送达 | 五处送达 | 事后人工统计 | 样本 C：ack 0/5 |
| 12 | 订阅额度耗尽 | 无监测 | 全线停摆之后 | 样本 C |
| 13 | 「唯一 issue」重复 | IVV 规程「exactly ONE」 | 本审点出 | #93 与 #94 同标题，自 11-03 并存 |

共性：能被机器发现的只有「动作没发生」（任务失败、进程没了）。「动作发生了但没到末态」这一类，十三行里没有一行是机器发现的。

## 3. 必答二：只有开环的闭环

每条给：现行机制原文依据 → 断点位置 → 证据。

### 3.1 判定 → 执行（判了没人执行）

- 依据：`standards/IVV.md`「合并只认当前 head 的判定」；`LOOP.md`「Merge owner: Jarvis」。
- 断点：判定落在 PR 评论里就结束了。没有任何东西在「当前 head 已 PASS」这个状态上挂计时器，也没有人被点名去合并。
- 证据：#127 在 2026-11-04 09:43Z 得到绑定 head `a982e6c` 的 PASS 判定，判词写明「The GitHub team can merge」。到 2026-11-17 PR 仍开，`updated_at` 停在 11-04。

### 3.2 派发 → 销单（互等）

- 依据：`standards/jarvis-task-loop.md`：`review → done` 由 Jarvis 合并后发回执。
- 断点：派发单等合并，合并等「有人看见判定已出」，没有第三方盯这两者的差。
- 证据：#129 是 #127 的判定派发单，判定完成回执已写在单内，单仍开、无状态标签。样本 A 所说「会话等判定、判定方等会话产物」在 GitHub 面就是这个形状。

### 3.3 采纳 → 执行（采了没做）

- 依据：三自第 7 条「采纳附工单指针」。
- 断点：采纳之后转成另一张单，新单进入同一个没有计时器的队列。
- 证据：#84（判定应成为强制合并门）11-03 裁「采纳，执行单 #95」；#95 标 `queued`，到 11-17 闲置 331 小时。

### 3.4 裁字 → 处置（全清清的是计数）

- 依据：REG-037 入口治理「owner＋死线＋完成定义三件不齐不入册」（`jarvis-architecture` `03-standards/core-mechanisms.md:19`）；REG-012「销记须非产出方回读确认」（同文件 `:24`）。
- 断点：裁字本身被当成处置。裁字不带 owner、死线和工单指针，也没有人回读它引发了什么。
- 证据：
  - 11-13 的「全清裁定」评论出现在 184 件 issue 上，其中 150 件仍开、34 件已关（11-17 搜索）。
  - 抽读两件（本仓 #145、`jarvis-architecture#26`），裁词逐字相同：「采纳。实施波次按分诊表规则……次日对账改判状态。」没有 owner、没有死线、没有工单指针，所引分诊表是仓外文件。四天后两件都没有后续。
  - 「零回执的 claude-advice」从 11-12 的 26 件变成 11-17 的 0 件，同期在开的 claude-advice 只从 83 件降到 73 件。指标归零，队列没清。
  - **#150（本审的载体）在 2026-11-13 04:57Z 被裁「采纳并轨。本报告结论入升级审计总册消费……报告件就此关单」。当时 issue 正文只有开工前申报，报告结论尚不存在。**

### 3.5 停席 → 恢复 → 回读（重启了没回读）

- 依据：简报：外部执行面「没有机器注册表、没有末态巡检」。
- 断点：恢复动作是人工键入「继续」。键入之后没有人回读该席是否真的续上、产物是否落地。
- 证据：
  - 11-12 01:27Z 会话快照（取最近 100 席）：未归档 28 席，其中 WORKING 7、REVIEW_READY 9、COMPLETED 12；另有 FAILED 11 席，全部已归档。REVIEW_READY 的 9 席里 8 席创建已满 10 天。COMPLETED 的席里至少 5 席的末轮摘要写着待办（待合并、待裁决）。
  - 11-17 00:48Z 再取：至少 10 席的 `updated_at` 集中在 00:45Z–00:48Z，其中一席的摘要自述是在「继续」后恢复，另一席写「main 已前移 4 天」（摘要是他席自报）。即 11-12 之后又是一轮成批停席，五天后由人工成批恢复。
  - 本席第一手：三度停转，合计约 135 小时，首切死线因此错过。其间没有任何点名、消息或续跑到达本席。第三次发生在报告已推送、只差回填 issue 的时候，又停了约 17 小时。
- 未取证：11 席 FAILED 是否各有后继席接手（需逐席比对标题与父席）；停转原因（疑为用量上限，未证）。

### 3.6 点名 → 销账（heartbeat 四态）

- 依据：简报：NAMED→ACKED→DISPOSED→CLOSED，按龄升级；点名记录写入一份人工维护的台账。
- 断点：四态迁移靠人工改台账；CLOSED 是否带回读指针没有机器检查；升级梯的终点「>72h 升中枢」进入的正是 3.4 那个裁字队列。
- 证据：机制描述来自简报；台账各态存量与龄**未取证**（台账在 VM）。

### 3.7 演练 → 上膛

- 依据：外部死人开关 workflow 头注：观察模式持续到 11-04 联合暂停演练，由后续 PR 转正式模式（`jarvis-architecture` `.github/workflows/x01-deadman-probe.yml:14-16`）。
- 断点：演练之后没有后续 PR，也没有任何一处记录演练做没做、结果如何。
- 证据：11-17 主干仍是 `OBSERVE_ONLY: "true"`；对应条目 `jarvis-architecture#36` 至今零评论。详见 §4.2。

### 3.8 审计条目 → 处置

- 证据：`jarvis-architecture` 带 `audit-2026-11` 标签的 79 件，11-12 时 77 件在开、其中 60 件零评论；11-13 全清后有了裁字，仍在开。属 3.4 同型。

### 3.9 广播 → ack；报告 → 消费

- 广播 ack 0/5 见样本 C。
- 报告消费：晨间包无读取回执已由架构审计 B-05／L-06 提出，不重提。新增一条实证：3.4 的 #150 说明「入总册消费」可以在被消费物不存在时发生。

## 4. 必答三：监测面自身的盲区

### 4.1 「监测者查错对象」同型，逐个点名

| 监测者 | 它查的 | 它该查的 | 证据 |
|---|---|---|---|
| 账号探活 | 账号存活、用量 | 每席的末态 | 样本 A |
| 外部死人开关 | 读一次心跳并打印，运行恒为 success | 心跳断了要有人知道 | 本席读到的 43 次运行记录（第 1–39、56–59 次）全部 success；按文件逻辑，判 MISS 时也只打印 |
| claude-advice 回执计数 | 评论数是否为 0 | 回执是否带处置和指针 | §3.4：计数归零、队列未清 |
| 独立评估 | 评论里有没有判词 | 判词之后 PR 的去向 | §3.1 |
| 标准审计的若干检查 | workflow 文本 | workflow 是否真的执行 | 已有 #83／#123，不重提 |

`loop_watch.py` 的 `ADVICE_NO_RECEIPT` 规则本身也属于第三行这一型：它只看评论数。本席把它如实留在报告里，改法见 I-03。

### 4.2 互守对没有闭合

名义结构是三层：heartbeat（30 分钟）与带外哨 heartbeat-oob-watch 互守，再由 GitHub 上的外部死人开关兜底。实测：

1. **内层两哨同源。** 舰队图把 `heartbeat` 与 `heartbeat-oob-watch` 都列在同一调度库的启用任务里（`04-capabilities/cron-fleet-map.md:129-130`，2026-11-01 快照）。调度器停，两个一起停。现况是否已迁出**未取证**。
2. **外层没有上膛。** `OBSERVE_ONLY: "true"`：不开 issue、不发信、运行不失败。
3. **外层的节律只有设计值的 2.8%。** workflow 写 `*/10 * * * *`，头注据此算出「最坏约 32 分钟发现」。实测 2026-11-02 11:44Z 至 11-11 23:39Z 共 228 小时只跑了 39 次，相邻两次间隔最短 3.1 小时、中位 6.2 小时、最长 10.5 小时。到 11-17 00:46Z 累计运行 59 次（含手动触发），最近三次定时运行间隔 6.7 小时和 10.3 小时，节律没变。按「连续两次 MISS 才判 DOWN」的现行语义，真实发现时间在 6 到 21 小时之间。
4. **验收演练的窗口里一次探测都没有。** 演练窗是 11-04 15:00–16:00 ET（20:00–21:00Z）。当天探针在 17:35Z 和 22:49Z 各跑一次，窗内为零。即使演练如期做了，这个探针也看不见。
5. **没有人监测探针的节律。** 上面四条在十五天里没有被任何机制发现。
6. **P1 单点的缓解被并到了这个没上膛的控制上。** `jarvis-architecture#22`（调度库单点）11-13 的裁字是「并入 X-01 死手开关（#36）」。

对照一条实测到的好消息：心跳写端是好的。痕迹分支从 11-12 01:25Z 的第 2587 轮走到 11-17 00:49Z 的第 4011 轮，119.4 小时写了 1424 轮，应有 1433 轮，到位率 99.4%。坏的是读端。

GitHub 官方文档对定时事件的原话：「The `schedule` event can be delayed during periods of high loads of GitHub Actions workflow runs. … If the load is sufficiently high enough, some queued jobs may be dropped.」本账号实测到的延迟远超这句话给人的印象；成因**未取证**。

### 4.3 定时器不守时，而覆盖率按名义频次在算

本仓 `standards-audit` 的定时是 03:40Z。10-29 至 11-11 的 14 次定时运行实际起跑在 09:57Z–12:08Z，晚 6 小时 17 分到 8 小时 28 分，无一例外。凡是按「每 N 分钟／每天几点」推算出来的新鲜度、覆盖轮次、发现时间，在 GitHub 这一侧都要按实测节律重算。IVV「每 6 小时一轮」是否按时，属 VM 侧定时，**未取证**。

### 4.4 监测者停摆时谁发现监测者

- 每日自检是单条 cron，是多数标准的唯一强制消费面（架构审计 O-01，不重提）。
- 会话面：停着的席读不了自己。所有依赖「该席自报」的监测对停席天然失明。本席停转 100 小时就是这种情形。
- 额度面：监测会话与被监测会话共用同一订阅额度。额度耗尽时两者一起停（样本 C 的周额度事件）。

### 4.5 聚合查询超时读成无异常

运营方在 U-12 已自认此项，本席无法读 heartbeat 任务体，现状**未取证**。本席给出的做法落在自己的工具里：`loop_watch.py` 的任何一次查询失败、超时或结果不完整，都以退出码 3（UNKNOWN）结束，并有测试钉住（`test_a_failed_query_is_unknown_never_clean`、`test_incomplete_search_results_are_unknown_never_clean`）。改稿见 §6.3 V-1。

### 4.6 独立性塌缩

- 评估席成了作者席。PR #127 正文落款的作者会话，在会话列表里带 `ivv-assessor` 标签、标题是一轮独立评估。`IVV.md` 隔离第 3 条写的是「评估者只读、只评论；不推代码」。
- 多个 `ivv-assessor` 席的末轮摘要自述合并过 PR。摘要是他席自报，GitHub 侧的 `merged_by` 本席**未取证**，这一条不进结论，只列为待查。
- 关闭核验与产出同模型族，已由架构审计 V-05 提出，不重提。

## 5. 必答四：对标 SOTA，差在哪几层

### 5.1 一手源与取证状态

| 源 | 状态 |
|---|---|
| Prometheus 官方文档 *Alerting*（practices） | 原文已取（prometheus/docs 源仓） |
| prometheus-operator runbook *Watchdog* | 原文已取（源仓） |
| Kubernetes 官方文档 *Controllers* | 原文已取（kubernetes/website 源仓） |
| GitHub 官方文档 *Events that trigger workflows* 的 `schedule` 节 | 原文已取（github/docs 源仓） |
| Atlassian *Incident Management Handbook · Postmortems* | 只经搜索索引取回一句，未能直连原页复核 |
| Google SRE Workbook *Postmortem Culture* | 只经搜索索引取回一句，未能直连原页复核 |
| Google SRE Book：*Monitoring Distributed Systems*、*Eliminating Toil*、*The Evolution of Automation at Google*、*Distributed Periodic Scheduling with Cron*、*Embracing Risk* | **原句未取**。本席网络策略不放行 `sre.google`。下表引这些章节时只按章名转述，不加引号，套用前须回读原文 |
| Google Cloud Pub/Sub、Temporal、SLSA | **未取**，下表不用作依据 |

放行 `sre.google` 与 `www.atlassian.com` 两个域名后可补齐；本席按「不在会话界面请示」的规矩没有弹权限卡。

### 5.2 分层对照

| 层 | SOTA 形态 | 我方现形态 | 差距定性 |
|---|---|---|---|
| L1 观测对象 | 按症状告警，不按原因。Prometheus：「alerting on symptoms that are associated with end-user pain rather than trying to catch every possible way that pain could be caused」。批任务看的是「最近有没有成功」：「page if the batch job has not succeeded recently enough」 | 探存活、探进程、数评论。工作末态基本不在观测面内 | **结构性**（R1）。差的是观测对象，加频次补不上 |
| L2 告警可行动 | 「avoid having pages where there is nothing to do」；SRE Book *Monitoring Distributed Systems* 同旨（转述） | 点名不强制带 owner、下一动作、死线；全清裁词无三件 | 机制缺口。运营方 U-05 已看到点名这一半，没看到裁字这一半 |
| L3 监测的监测 | Prometheus *Metamonitoring*：「It is important to have confidence that monitoring is working」「external blackbox monitoring can catch problems that are otherwise invisible, and also serves as a fallback in case internal systems completely fail」。Watchdog：一条恒亮告警，「If not firing then it should alert external systems that this alerting system is no longer working」 | 内层两哨同源；外层在观察模式，节律 2.8%，无人监测探针 | **结构性**（R4）。形有了，没有通电 |
| L4 调谐环 | Kubernetes 控制器：以对象的 current state 对 desired state 持续调谐，状态以被控对象实测为准（原文：「The thermostat acts to bring the current state closer to the desired state」） | 状态以执行者回执和人工台账为准；没有「期望态」的机读表达；状态机 109/121 未赋态 | **结构性**（R2、R5）。缺的是「被控对象的实测状态」这个比较点 |
| L5 行动项治理 | Atlassian：优先行动项带时限 SLO（搜索索引取回句：「Designated "priority actions" have an agreed Service Level Objective (SLO) which is either 4 or 8 weeks…with reminders and reports to ensure they are completed」）。SRE Workbook（搜索索引取回句）：「Without a formal tracking process, action items from postmortems are often forgotten, resulting in outages」 | 有时限成文（24h、48h），没有逐项计时器，也没有逾期报表；30/30 裁决超时 | 机制缺口。运营方 U-11 已对齐到此 |
| L6 流量与背压 | 错误预算烧尽即冻结变更（SRE Book *Embracing Risk*，转述）；toil 设上限（*Eliminating Toil*，转述） | 入口 402、出口 68；只有 U-09 拟对 cron 新建设冻结，issue／建议／审计条目的入口无闸 | **结构性**（R3） |
| L7 周期调度 | cron 服务不知道任务的业务是否成功，owner 须自行监测产物；幂等与跳过／重跑的取舍要显式（*Distributed Periodic Scheduling with Cron*，转述） | 启用 355、禁用 271 无生命周期标注；产物哨刚起步（U-03）；数目三源不一（300／385／355） | 机制缺口＋卫生项 |
| L8 回执的可信度 | 完成证明由平台状态给出，不由执行方自述（本席推论；SLSA 原文未取，不作依据） | 「回执不可信」是纪律，没有闸 | 机制缺口。`receipt_check.py` 补的是这一层 |

三处结构性差距（L1、L3、L4）是同一件事的三个面：系统里没有一个地方持有「被控对象的实测末态」。GitHub 面和会话面其实都现成地给出了这个末态，只是没人去读。

## 6. 提升清单

### 6.1 按收益／成本排序

层的取值：舰队结构／监测面／派工台账／自检／升级销账／外部执行面纳管。

| # | 改什么 | 层 | 验收标准 | owner 建议 | 状态 |
|---|---|---|---|---|---|
| I-01 | 会话末态巡检：读平台会话接口，停席、等答、待回收、失败未接手逐席点名 | 外部执行面纳管 | `standards/session-patrol.md` §验收三条；首轮点名席数与人工数出的一致 | Control Loop 组 | 规程与固定提示词已入 PR #165；挂到既有每日调度会话由 Control Loop 套用 |
| I-02 | 外部死人开关上膛，并按真实节律重定阈值；探针自测节律 | 监测面 | 暂停心跳写端 30 分钟，下一次探针运行失败并开出告警 issue；探针间隔 >60 分钟时有降级标记 | 全自动化部门＋GitHub 团队 | 改稿全文见 §6.3 V-2 |
| I-03 | 裁字与销账分开计数。销账必须带回读指针；裁字必须带 owner、死线、工单指针 | 升级销账 | 抽 20 件已裁 issue，三件齐全率 100%；`receipt_check.py` 对每条销账回执退出码为 0 | 中枢＋GitHub 团队 | 回读闸已入 PR #165；裁词模板见 §6.3 V-5 |
| I-04 | GitHub 面闭环末态巡检常态化 | 派工台账 | 手动触发一次 `loop-watch`（`deep` 开），#127 与 #129 必须被点到；之后每日点名数单调下降或有书面说明 | GitHub 团队 | 工具与 workflow 已入 PR #165；定时触发待中枢定（本审红线：不新建定时任务） |
| I-05 | 判定后合并设时限：当前 head PASS 满 24h 未合并即点名合并席 | 升级销账 | `VERDICT_NOT_EXECUTED` 连续 7 天为 0 | GitHub 团队 | 检测已在 `loop_watch.py --deep`；`ivv/verdict` 设为必需检查属 #84／#95 既有单 |
| I-06 | 入口背压：在开件超过阈值时暂停同类新开，先清后开 | 派工台账 | 连续两周「新开 ≤ 关闭」；超阈值期间无新开同类件 | 中枢 | 口径稿见 §6.3 V-6 |
| I-07 | 回执落账闸：台账写入前跑 `receipt_check.py`，非 0 不落账 | 派工台账 | 回放样本 B 那条伪造回执，闸必须拒绝；抽 20 条近期销账回执全部通过 | Control Loop 组 | 工具已入 PR #165；台账侧改稿见 §6.3 V-4 |
| I-08 | 派单入仓：简报写成 `jarvis-task` issue，会话启动只贴 issue 号 | 外部执行面纳管 | 新开的每一席都能在 GitHub 上找到对应的派单 issue | 中枢 | 表单已有（`.github/ISSUE_TEMPLATE/jarvis-task.yml`），缺的是用它 |
| I-09 | 状态机赋态：存量 109 件一次性补状态标签，之后入口强制 | 派工台账 | `NO_STATE` 为 0 | GitHub 团队 | 检测已有；补标是一次性人工或脚本动作 |
| I-10 | heartbeat L1 增「工作末态」三项，并把聚合超时定为 UNKNOWN | 监测面 | 注入一次聚合超时，当轮输出为 UNKNOWN 且有降级旗 | 全自动化部门 | 改稿见 §6.3 V-1 |
| I-11 | 每日自检增「外部执行面末态」与「巡检自检」两项 | 自检 | 日报出现两项且数字与 `loop_watch` 当日输出一致 | 全自动化部门 | 改稿见 §6.3 V-3 |
| I-12 | cron 生命周期标注：禁用的 271 条逐条归为退役／暂停／待复活，带 owner 与复审日 | 舰队结构 | 无标注数为 0；舰队总数由调度库单一查询生成，不手抄 | 全自动化部门 | 字段稿见 §6.3 V-6 |
| I-13 | 评估席与作者席隔离落到机制：带 `ivv-assessor` 标签的席不得有产出分支 | 外部执行面纳管 | 巡检核对：`ivv-assessor` 席的产出分支数为 0 | Control Loop 组 | 可并入 I-01 的巡检判据 |
| I-14 | 按实测节律重算所有 GitHub 侧定时的新鲜度承诺 | 监测面 | 每条定时 workflow 的注释写的是实测起跑窗，不是 cron 字面值 | GitHub 团队 | #145 已提其中一处 |

### 6.2 本席已直接改的件（PR #165，逐件留指针）

| 件 | 路径 | 做了什么 | 实测 |
|---|---|---|---|
| 闭环末态巡检 | `standards/loop_watch.py`、`standards/loop_sla.json` | 八条规则，阈值逐条注明成文出处；查询失败即 UNKNOWN；不印标题 | 对真实舰队跑过两次，22 个在册仓全部可读；24 项测试 |
| 手动触发入口 | `.github/workflows/loop-watch.yml` | 只有 `workflow_dispatch`，不带定时 | 未实跑（需合入后触发） |
| 回执回读闸 | `standards/receipt_check.py` | PR、合并、SHA、评论四类指针逐个回读；无指针不得落账 | 14 项测试，含样本 B 型伪造回执。未对真实 API 跑过 |
| 会话末态巡检规程 | `standards/session-patrol.md` | 判据、载体、固定提示词、验收 | 数据源两次实测可用；提示词未经调度会话实跑 |

`loop_watch.py --deep`（读每个 PR 的判定）本席没有实跑：本席的 `gh` 只放行搜索接口。这一档只有夹具测试，夹具照 #127／#129 的真实正文做。

两次实跑的数字（规则含义见工具文档）：

| | 11-12 20:17Z | 11-17 00:46Z |
|---|---|---|
| 在开 jarvis-task／待中枢裁／claude-advice／PR | 124／33／83／111 | 121／30／73／114 |
| `NO_STATE` | 114 | 109 |
| `STALE_STATE` | 8 | 10 |
| `RULING_OVERDUE` | 28 | 30 |
| `ADVICE_NO_RECEIPT` | 26 | 0 |
| `SINGLETON_DUP` | 1 | 1 |
| `PR_STALE` | 34 | 42 |

### 6.3 VM 侧改稿全文

任务体原文本席读不到。「改前」一栏写的是简报对现行行为的描述，不是原文；V-2 例外，其改前是本席读到的真实文件。

**V-1 · heartbeat L1 段**

改前（简报描述）：L1 限值含「cron 舰队健康聚合、僵尸子代理点名：静默 >6h 记 STALL、>24h 记 ZOMBIE」。聚合查询超时的口径未成文。

改后（整段追加到 L1）：

```text
L1-末态（每轮必跑，与舰队健康聚合并列）
  a. GitHub 面：执行 `python3 standards/loop_watch.py --json <当轮产物路径>`。
     退出码 0＝无超时件；1＝有超时件，把 counts 六个数写入当轮记录，新增的点名进四态机；
     2＝有在册仓读不到，记「覆盖缺口」并点名 GitHub 团队；
     3＝UNKNOWN，本项记「未完成」，落降级旗，下一轮必须重跑，不得写「无异常」。
  b. 会话面：读最近一轮「[会话末态点名]」issue 的更新时间。超过 26h 未更新，记「会话巡检失联」并点名 Control Loop 组。
  c. 外部死人开关：读其最近一次定时运行的起跑时间。距今超过 12h，记「外部探针失联」。

通则（适用于 L1、L2 全部聚合查询）
  任何一次查询超时、报错或返回不完整，该项结果一律写 UNKNOWN，并在当轮记录首行落降级旗。
  UNKNOWN 不是 PASS，也不是 FAIL。连续两轮 UNKNOWN 的项，第三轮起按 FAIL 进点名。
  禁止用「上一轮的值」填充本轮。
```

**V-2 · 外部死人开关 workflow**（`jarvis-architecture` `.github/workflows/x01-deadman-probe.yml`）

改前（真实文件的判定语义）：`OBSERVE_ONLY: "true"`；心跳龄 >720s 记一次 MISS，连续两次 MISS 判 DOWN；任何情形运行都以 success 结束；头注称最坏约 32 分钟发现。

改后（整文件替换；语义变化有三处）：

1. 单次运行即可判 DOWN。写端 5 分钟一写，心跳龄超过 20 分钟已是连丢四轮，不必等第二次探测。按实测节律，等第二次要再等 3 到 10 小时。
2. DOWN 时运行失败，并开或更新一件告警 issue。失败的定时运行会由 GitHub 通知 workflow 的 actor，这是不花钱的第二通道。
3. 探针自测节律：距上一次定时运行超过 60 分钟，写降级告警。

```yaml
name: X-01 deadman probe

# External deadman switch for the scheduler. The scheduler writes heartbeat.json to the
# `heartbeat` branch every 5 minutes; this workflow reads it from outside the scheduler.
# DOWN-external = heartbeat older than DOWN_AFTER_SECONDS in a single run (20 min = four
# missed writes). Honest detection time: GitHub starts this schedule far less often than
# the cron says (measured 2026-11-02..11: 39 runs in 228 h, gaps 3.1-10.5 h), so the
# worst case is the gap to the next run plus 20 minutes, not 32 minutes. A timer outside
# GitHub's scheduler is needed to reach the 45-minute yardstick.

on:
  schedule:
    - cron: "*/10 * * * *"
  workflow_dispatch:

permissions: {}

env:
  DOWN_AFTER_SECONDS: "1200"
  PROBE_GAP_WARN_MINUTES: "60"
  ALERT_TITLE: "[alert-chain external] DOWN-external"

jobs:
  probe:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    permissions:
      contents: read
      actions: read
      issues: write
    steps:
      - name: Checkout heartbeat branch
        uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8 # v5.0.0
        with:
          ref: heartbeat
          persist-credentials: false
      - name: Probe cadence (who watches the probe)
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          set -euo pipefail
          prev=$(gh api "repos/${GITHUB_REPOSITORY}/actions/workflows/x01-deadman-probe.yml/runs?event=schedule&status=completed&per_page=1" --jq '.workflow_runs[0].run_started_at // empty')
          if [ -z "$prev" ]; then echo "no earlier scheduled run"; exit 0; fi
          gap=$(( ( $(date -u +%s) - $(date -u -d "$prev" +%s) ) / 60 ))
          echo "previous scheduled run started ${gap} min ago (cron says 10)"
          if [ "$gap" -gt "$PROBE_GAP_WARN_MINUTES" ]; then
            echo "::warning::probe cadence degraded: ${gap} min since the previous scheduled run"
            echo "**Probe cadence degraded:** ${gap} min since the previous scheduled run." >> "$GITHUB_STEP_SUMMARY"
          fi
      - name: Judge heartbeat freshness
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          set -euo pipefail
          ts=$(python3 -c "import json,datetime; d=json.load(open('heartbeat.json')); print(int(datetime.datetime.strptime(d['ts'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc).timestamp()))")
          age=$(( $(date -u +%s) - ts ))
          echo "heartbeat_age_seconds=$age"
          open=$(gh issue list -R "$GITHUB_REPOSITORY" --state open --search "\"$ALERT_TITLE\" in:title" --json number -q '.[0].number')
          if [ "$age" -gt "$DOWN_AFTER_SECONDS" ]; then
            body="Heartbeat is ${age}s old at $(date -u +%FT%TZ) (limit ${DOWN_AFTER_SECONDS}s). Run: ${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}"
            if [ -n "$open" ]; then gh issue comment "$open" -R "$GITHUB_REPOSITORY" -b "$body"
            else gh issue create -R "$GITHUB_REPOSITORY" -t "$ALERT_TITLE $(date -u +%FT%TZ)" -b "$body"; fi
            echo "::error::DOWN-external: heartbeat ${age}s old"
            exit 1
          fi
          if [ -n "$open" ]; then
            gh issue close "$open" -R "$GITHUB_REPOSITORY" -c "UP-external: heartbeat ${age}s old at $(date -u +%FT%TZ)."
          fi
          echo "FRESH (age ${age}s)"
```

这份改稿本席没有跑过。套用前在 PR 分支上用 `workflow_dispatch` 跑一次，再做一次暂停写端的演练，演练结果写回 `jarvis-architecture#36`。

**V-3 · 每日自检 A 层新增两项**

改前（简报描述）：A 层含子代理状态、各 cron 上次结果、决策日志超 9h 未决、发布队列滞留、跟踪目标状态等；无外部执行面项。

改后（追加）：

```text
A-新增一 外部执行面末态
  读当日「[会话末态点名]」issue 与 `loop_watch` 当日 JSON。
  报六个数：停席数、僵尸席数、待回收席数、VERDICT_NOT_EXECUTED、DISPATCH_NOT_CLOSED、RULING_OVERDUE。
  任一数较昨日上升，写明新增的是哪几件。两份产物任一缺失或超过 26h，本项判 FAIL，不得判「无数据」。

A-新增二 巡检自检
  三个监测者各报一行「最近一次成功产出的时间」：heartbeat、会话末态巡检、外部死人开关。
  任一超过自身周期的两倍，本项判 FAIL 并直接升中枢，不走 24h 的 ack 梯。
```

**V-4 · 台账落账规则**

改前（简报描述）：「销账口径＝独立回读验讫才算完成」，落实靠纪律与人工回读。

改后（写入台账 owner 的操作规程）：

```text
落账前置闸
  1. 把待落账的回执全文存为文件，执行：
       python3 standards/receipt_check.py --repo <owner/repo> --done <回执文件>
  2. 退出码 0：可落账，把工具输出的表格整段贴在台账该条的「回读证据」栏。
     退出码 1：不得落账，把被驳回的指针回给回执方。
     退出码 3：不得落账，重跑；连续两次 3，记「回读通道故障」并点名。
  3. 台账条目的「回读证据」栏为空者，一律视为未销账，计入未完结数。
  4. 工具不核的面（CI 计数、文字结论、GitHub 以外的指针）须在该栏逐条写「未机核」，不得留白。
```

**V-5 · 裁词模板**

改前（实读两件全清裁词）：只有「裁定：采纳」和一段通用波次说明。

改后：

```text
裁定：采纳｜改编｜不采
owner：<具名的组或席>
死线：<日期，或「事件型：<事件>」>
工单：<owner/repo#号>（采纳、改编必填；不采写理由）
完成定义：<一句可回读的话>
本件状态：<保持 open 随工单推进｜即关，理由：…>
```

配套口径：只有裁词、没有工单指针的，不计入「已处置」。周报把「已裁」和「已销」分两个数报。

**V-6 · 入口背压与 cron 生命周期字段**

```text
入口背压（建议阈值，中枢定）
  任一类在开件（jarvis-task、claude-advice、待中枢裁、审计条目）超过 40 件，
  或该类近 7 天「新开 − 关闭」为正且在开件超过 20 件：暂停该类新开。
  暂停期内新发现写进既有件的评论，不另开件。解除条件：在开件回到阈值以下。
  本审自己照此执行：十四条提升项不逐条开单，只留在 #150 里（见 §7.3）。

cron 生命周期字段（调度库每条任务必填）
  lifecycle：active｜paused｜retired｜pending-revival
  owner：具名的组
  paused／pending-revival 必填 review_by（复审日）；过期未复审的自动进点名。
  retired 必填 retired_reason 与接替者（无接替者写「无」）。
  舰队总数、启用数、禁用数只允许由一条查询生成并带查询时间，文档里不手抄数字。
```

## 7. 与运营方自提方案 U-01～U-13 对表

本席手里只有简报附录的逐项摘要，没有方案正本。「一致」指方向一致，不是逐字核过。

### 7.1 逐项

| 项 | 判断 | 说明 |
|---|---|---|
| U-01 清本部悬置存量七件 | 一致 | 验收写的是「回读指针入台账」，与 I-07 同向 |
| U-02 双明细交付 | 一致 | 建议数字由单一查询生成（I-12） |
| U-03 触发器型 cron 产物哨 | 一致 | 这是 L1「测产物不测运行」在 cron 面的落地，方向对 |
| U-04 出件三态＋ack 老化周报 | 部分 | ack 只证收。升级梯终点「>72h 升中枢」进入的是 30/30 超时的裁决队列，升上去不等于有人处置 |
| U-05 点名可行动性 | 一致，但只管了一半 | 点名要三件，裁字同样要三件（I-03）。「单日点名上限 5 件」是在限流出口的可见度，不是限流入口；超出的件去哪要写明 |
| U-06 产物哨独立性 | 一致 | 「不得共用同一注意力面」的口径还应加上：不共用调度库、不共用订阅额度 |
| U-07 FTC 呈面降量 | 无法判断 | 摘要信息不足，未取证 |
| U-08 owner 注册面 | 一致 | 并入 I-12 的生命周期字段 |
| U-09 舰队健康错误预算 | 部分 | 冻结只管 cron 新建。真正失衡的入口是 issue、建议、审计条目（402 入、68 出） |
| U-10 toil 盘点与 50% 上限 | 一致 | 人工键入「继续」、人工粘贴简报、人工逐席回收，是当前最大的三项 toil，应进盘点 |
| U-11 复盘行动项 SLO | 一致 | 与 Atlassian 口径一致；需配逐项计时器，否则仍是成文时限 |
| U-12 观测降级口径 | 一致 | 给了可直接套用的通则（V-1）和一个已实现的参照（`loop_watch.py` 的退出码 3） |
| U-13 工具三载体一致性 | 无法判断 | 摘要信息不足，未取证 |
| 不采纳三项 | 一致 | 「不以增加点名频率代替处置」正确。本审的全部建议也不增加点名频率 |

### 7.2 自查盲区：本席看到、对方没看到的

1. **外部死人开关是空的。** 没上膛，节律是设计值的 2.8%，验收演练窗内零探测，而调度库单点这条 P1 的缓解刚被裁定并到它头上。十三条里没有一条碰它。（§4.2）
2. **全清清的是计数。** 184 件有了裁字，150 件还开着；本审的载体在报告写出来之前就被「采纳并轨、关单」。U-04、U-05、U-11 管的是出件和点名，没有一条区分「裁了」和「办了」。（§3.4）
3. **没有会话面。** 十三条全在 VM 和台账里打转。停席由人工键入「继续」恢复这件事，11-12 发生一次，11-17 又发生一次，本席自己就停了约 135 小时。方案里没有任何一条能发现它。（§3.5）
4. **评估者成了作者。** 方案把「独立回读」当作可信度的来源，但回读方和产出方可以是同一席。#127 的作者席带的就是评估席标签。（§4.6）
5. **入口没有闸，方案自己又是十三条新入口。** U-09 的冻结对象选错了队列。（§5.2 L6）
6. **GitHub 侧的定时器不守时。** 日任务晚 6 到 8.5 小时，10 分钟探针 6 小时一跑。方案里所有新增的「周检」「周报」如果落在 GitHub 定时上，会继承同样的漂移。（§4.3）
7. **判了没人执行。** 环断在执行权集中于一个合并席，而不是断在检测上。给检测加码解决不了它。（§3.1、§3.3）

### 7.3 本审自己的一处偏离，报中枢裁

三自第 7 条要求改进建议逐条开 improvement issue。本审查明入口已严重失衡，所以十四条提升项没有逐条开单，统一留在 #150（已带 `claude-advice` 标签），由中枢采纳哪条再拆哪条。这是对成文规则的偏离，已写入待裁单。

## 8. 未取证清单与取证路径

| 项 | 为什么没取到 | 取证路径 |
|---|---|---|
| heartbeat 检查清单与任务体原文；聚合超时的现行处理 | 在 VM | Control Loop 组贴原文到 #150，本席对照 V-1 出逐行差异 |
| 点名台账各态存量与龄 | 在 VM | 导出 NAMED／ACKED／DISPOSED／CLOSED 四态件数与最老龄 |
| 每日自检日报原文；升级旗是否被消费 | 在 VM | 取最近 7 份日报，逐份核「升级旗 → 次日处置」 |
| decision-log 撞号 9 次的现行防护 | 在 VM | 架构审计 V-09 已给验证法 |
| 禁用的 271 条 cron 的分类 | 调度库不可达 | I-12 的字段落地即得 |
| heartbeat-oob-watch 现在是否已迁出调度库 | 只有 11-01 快照 | 查该任务当前的调度载体 |
| 本席三次停转、以及 11-12 至 11-17 成批停席的原因 | 停着的席读不了自己 | 查订阅用量记录与各席事件流 |
| 11 席 FAILED 是否各有后继 | 需逐席比对 | I-01 巡检的 `S-FAILED` 判据首轮即得 |
| `ivv-assessor` 席是否合并过 PR | 本席 `gh` 只放行搜索 | 对摘要里自述的 PR 逐个读 `merged_by` |
| GitHub 定时严重延迟的成因 | 平台侧 | 查账号 Actions 用量与并发；向平台支持提单 |
| `loop_watch.py --deep`、`receipt_check.py` 对真实 API 的行为 | 本席 `gh` 只放行搜索 | PR 合入后手动触发 `loop-watch`；对 #129 的评论跑一次 `receipt_check.py --comment` |
| SRE Book 各章与 Atlassian 手册原句 | 域名未放行 | 放行 `sre.google`、`www.atlassian.com` 后回读 |
| U-07、U-13 的实质 | 只有摘要 | 取方案正本 |

## 9. 证据附录

- **GitHub 面全量**（搜索 API，`user:HUIIIM archived:false`）：`is:pr is:open`；`is:issue is:open label:jarvis-task`；`is:issue is:open label:claude-advice`；`is:issue is:open "待中枢裁" in:title`；`is:issue is:open "独立评估" in:title`；`is:issue created:>=2026-10-22`；`is:issue closed:>=2026-10-22`；`is:pr merged:>=2026-10-22`；`is:issue "全清裁定" in:comments`。
- **11-12 01:27Z 的补充数**：在开 PR 139（HUIIIM 80、dependabot 58、claude[bot] 1；草稿 42）；在开 jarvis-task 122，无状态标签 111，闲置中位 197h；在开 issue 334，零评论 192。10-22 起 PR 新开 880、合并 696。
- **11-12 之后**：issue 关闭 39（11-12 13 件、11-13 21 件、11-15 5 件）；PR 合并 83（11-12 50 件，之后逐日 16、7、7、3）；issue 新开 31。
- **外部死人开关**：`jarvis-architecture` Actions，workflow `x01-deadman-probe.yml` 的运行列表，第 1 次 2026-11-02 11:44:16Z，第 39 次 2026-11-11 23:39:46Z，第 58 次 2026-11-16 18:24:39Z；读到的 43 条记录（第 1–39、56–59 次）均为 `conclusion: success`，第 40–55 次未读。主干 `c4f0830` 上 `OBSERVE_ONLY: "true"`。
- **心跳痕迹**：`heartbeat` 分支 `heartbeat.json`，round 2587 @ 2026-11-12T01:25:10Z，round 4011 @ 2026-11-17T00:49:51Z。
- **本仓定时**：`standards-audit.yml` 定时运行列表，run 41（10-29）至 run 81（11-11）。
- **会话面**：`list_sessions`，2026-11-12 01:27Z（100 席）与 2026-11-17 00:48Z（45 席）。
- **个案**：#127 及其评论 6627689384；#129 及其评论 6627677221；#84、#95；#145 评论 6844038519；`jarvis-architecture#22` 评论 6844662690、`#26` 评论 6844477417、`#36`（零评论）；#150 评论 6813003016、6844529541。
- **巡检实跑产物**：`loop_watch.py` 于 11-12 20:17Z 与 11-17 00:46Z 的输出，数字见 §6.2。
