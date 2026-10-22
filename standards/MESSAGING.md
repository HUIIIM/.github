# vertciti 客户消息标准 v1.0（邮件 · 短信）

**一句话：发给客户的每一封邮件、每一条短信，都要能被收到、被信任、被退订、被追查——由 DNS 和脚本检查，而不是靠发信时的自觉。**

本标准适用于 [@HUIIIM](https://github.com/HUIIIM) 下所有会向真人发送邮件或短信的系统：
产品后端、官网表单、运营群发、告警。它是
[STANDARDS.md](STANDARDS.md) 在"对外消息"这一维上的展开，与
[vertciti DNA](../design) 的视觉规范、[AESTHETICS.md](../design/AESTHETICS.md) 的内容规范一致。

`MUST` 不达标 = 不许发；`SHOULD` 不达标 = 要有书面理由。每一条都对应一个公开框架。

## 对标框架

| 维度 | 对标 | 我们的门槛 |
|---|---|---|
| 发信身份 | [SPF (RFC 7208)](https://www.rfc-editor.org/rfc/rfc7208) · [DKIM (RFC 6376)](https://www.rfc-editor.org/rfc/rfc6376) · [DMARC (RFC 7489)](https://www.rfc-editor.org/rfc/rfc7489) | SPF + DKIM(≥2048) 全对齐，DMARC 走到 `p=reject` |
| 传输加密 | [MTA-STS (RFC 8461)](https://www.rfc-editor.org/rfc/rfc8461) · [TLS-RPT (RFC 8460)](https://www.rfc-editor.org/rfc/rfc8460) | `enforce` 模式 + 报告收件地址 |
| 品牌可信 | [BIMI](https://bimigroup.org) · [DNS CAA (RFC 8659)](https://www.rfc-editor.org/rfc/rfc8659) | DMARC 达标后发布 BIMI；CAA 限定签发机构 |
| 退订 | [RFC 8058](https://www.rfc-editor.org/rfc/rfc8058)（一键退订） | 营销邮件必带 `List-Unsubscribe` + `-Post` |
| 运营门槛 | [M3AAWG 发送者最佳实践](https://www.m3aawg.org/for-the-industry/published-documents) | 投诉率 < 0.1%、硬退 < 2%、有抑制表 |
| 邮件合规 | [CAN-SPAM](https://www.ftc.gov/legal-library/browse/rules/can-spam-rule) · [CASL](https://crtc.gc.ca/eng/internet/anti.htm) · [GDPR/ePrivacy](https://gdpr.eu) | 实体地址、真实退订、同意可查 |
| 短信合规 | [TCPA](https://www.fcc.gov/tcpa) · [CTIA 短信准则](https://www.ctia.org/the-wireless-industry/industry-commitments) · 10DLC/Toll-Free 登记 | 事前同意、STOP/HELP、安静时段 |
| 无障碍 | [WCAG 2.2](https://www.w3.org/TR/WCAG22/) AA | 正文/按钮对比由 DNA `build.py` 口径计算，不靠肉眼 |
| 可观测 | [OpenTelemetry](https://opentelemetry.io) | 投递/退信/投诉事件结构化留存，越阈告警 |

---

## 一、发信身份与可达性 AUTH（邮件）

- **AUTH-1 MUST** 用**独立发信子域**（如 `send.vertciti.com`），不要用根域直发。根域的信誉不被发信事故连累。
- **AUTH-2 MUST** SPF、DKIM、DMARC 三者对齐（aligned）。DKIM 选择子密钥 **≥ 2048 位**——1024 位已被视为过时。
- **AUTH-3 MUST** DMARC 的目标是 `p=reject`。上线路径固定：`p=none`（只收报告，两周）→ `p=quarantine`（灰度 `pct`）→ `p=reject`。带 `rua`/`ruf` 报告地址，每周看聚合报告再进档，不跳步。
- **AUTH-4 MUST** 发布 **MTA-STS** 策略为 `enforce`，并配 **TLS-RPT** 报告地址——传输层强制 TLS，降级可被发现。
- **AUTH-5 MUST** 发布 **CAA** 记录，限定谁能为本域签发证书。
- **AUTH-6 SHOULD** DMARC 到 `reject` 后发布 **BIMI**（需 VMC 证书），让收件箱显示品牌标。没到位之前不虚发。
- **AUTH-7 MUST** 专用 IP/子域要**预热**；新发信源不从零直接群发。

> **当前 vertciti.com 实况（2026-10）：** SPF(Zoho) + DMARC `p=quarantine` + Resend DKIM(**1024 位**) + `send.vertciti.com` 已有。
> **缺口（本标准要补）：** DKIM 升 2048；DMARC 进 `p=reject`；补 MTA-STS、TLS-RPT、CAA；BIMI 待 reject 后做。

## 二、邮件内容与结构 MAIL

- **MAIL-1 MUST** 每封邮件同时带 **纯文本 + HTML** 两部分，且**两者信息一致**——尤其是验证码、链接、帮助路径（"直接回复这封邮件"必须两边都有）。
- **MAIL-2 MUST** HTML 用**内联样式 + 表格布局**，不依赖外部 CSS/网络字体（邮件客户端不加载）。颜色取 DNA 令牌，正文/按钮对比满足 WCAG AA，由 `build.py` 口径计算。
- **MAIL-3 MUST** 发信人显示名与地址稳定、可辨识；**Reply-To** 指向真人可达的信箱，不是 `no-reply` 黑洞。
- **MAIL-4 MUST** 带规范头：`Message-ID`、`Date`、`MIME-Version`；事务邮件带 `Auto-Submitted: auto-generated` 与**每封唯一**的 `X-Entity-Ref-ID`（防止被折叠/串线）。
- **MAIL-5 MUST** **事务邮件与营销邮件分流**：不同子域/流，不同信誉。验证码、账单、告警是事务；推广、简报是营销。
- **MAIL-6 MUST** 营销邮件带 `List-Unsubscribe` 头 **且** `List-Unsubscribe-Post`（RFC 8058 一键退订），正文另有可见退订链接；事务邮件不夹带营销。
- **MAIL-7 MUST** 主题行不欺骗、不全大写、不堆表情；有信息量的 preheader。
- **MAIL-8 MUST** 反钓鱼：凡含验证码/敏感动作，正文写明"vertciti 不会在邮件/电话里向你索要完整验证码"，并给出识别真伪的锚点。
- **MAIL-9 SHOULD** 中英双语按收件人语言切换；默认跟随账号语言，未知时中英并列关键句。

## 三、发送可靠性 SEND

- **SEND-1 MUST** 每次发送带 **幂等键**（Idempotency-Key）——重试不产生重复邮件/短信。
- **SEND-2 MUST** 发送走**队列 + 重试（指数退避）**，不在请求线程里 fire-and-forget；失败要落日志、可重放。
- **SEND-3 MUST** 维护**抑制表**（suppression list）：硬退信、投诉、退订的地址永久不再发，发送前查表。
- **SEND-4 MUST** 接入 provider 的**退信/投诉 webhook**，自动回写抑制表与指标。
- **SEND-5 SHOULD** 关键事务邮件配**备用通道**（主 provider 故障时切换），验证码这类不能只押一家。
- **SEND-6 MUST** 生产环境缺发信 provider 时**显式报错**，绝不"降级成把验证码写进日志"。

## 四、短信 SMS

- **SMS-1 MUST** 号码一律 **E.164** 存储与校验；按落地国选合规通道。
- **SMS-2 MUST** 发送前完成运营商登记：美国 **10DLC**（A2P）或 Toll-Free 验证，其他地区按当地 Sender ID 规则；不借未登记号群发。
- **SMS-3 MUST** **事前同意可查**：记录同意的时间、方式、文案版本（TCPA 举证责任在发送方）。
- **SMS-4 MUST** 每条营销短信可 **STOP 退订 / HELP 求助**，并即时生效；**UNSTOP/START** 可重新订阅。事务短信（验证码）不夹带营销。
- **SMS-5 MUST** 尊重**安静时段**（默认收件人本地 08:00–21:00 外不发营销）。
- **SMS-6 MUST** 短信里**不放秘密**：不发完整密码；验证码短、短时效；不使用会被拦的公共短链，用可信品牌域短链。
- **SMS-7 SHOULD** 控制**计费段数**（GSM-7 单段 160 字），文案精炼；首句含品牌名。
- **SMS-8 MUST** 短信也走抑制表、幂等键、重试与投递回执，与邮件同一套可靠性要求（SEND-1/2/3/4）。

## 五、安全与隐私 SEC

- **SEC-1 MUST** 一次性验证码/魔法链接**只在 dev 模式可落日志**；生产环境日志里绝不出现验证码、完整链接 token、完整密码。
- **SEC-2 MUST** 日志里的邮箱/手机号**脱敏**（如 `a***@x***.com`、`+1••••••1234`）。
- **SEC-3 MUST** 敏感输入只存**哈希（sha256+）**，不存明文；验证码存哈希 + 过期时间 + 尝试次数上限。
- **SEC-4 MUST** 发信密钥只在**后端内存/密钥管理**，不进前端、不进仓库、不进客户端可见配置。
- **SEC-5 MUST** 验证码/魔法链接**短时效 + 限频 + 次数锁定**，防撞库与轰炸；对单一收件人有发送速率上限。
- **SEC-6 MUST** 魔法链接一次性、绑定会话、带签名，点击即失效。

## 六、合规 LAW

- **LAW-1 MUST** 营销邮件含**真实实体邮寄地址**与真实退订（CAN-SPAM），退订在 **10 天内**生效且不设障碍。
- **LAW-2 MUST** 面向加拿大收件人满足 **CASL**（明确同意 + 发送者身份 + 退订）；面向欧盟满足 **GDPR/ePrivacy**（同意合法性基础、可撤回、可被遗忘）。
- **LAW-3 MUST** 面向美国手机满足 **TCPA**（营销短信须事前书面同意）。
- **LAW-4 MUST** **同意台账**可随时导出：谁、何时、就什么、经何渠道同意，保留到法定年限。
- **LAW-5 MUST** 数据删除请求连带删除消息订阅与历史（符合 STANDARDS 的隐私条款）。

## 七、可观测 OBS

- **OBS-1 MUST** 每次发送与每个回执（投递/打开/点击/硬退/软退/投诉/退订）记成**结构化事件**，带请求 ID、模板版本、provider。
- **OBS-2 MUST** 看板常驻：投递率、退信率、投诉率、退订率。阈值告警对标 M3AAWG——**投诉率 ≥ 0.1% 或硬退 ≥ 2% 即告警并暂停相关流**。
- **OBS-3 SHOULD** DMARC/TLS-RPT 聚合报告自动解析入看板，身份配置漂移可见。
- **OBS-4 MUST** 验证码类发送失败有实时告警——这类失败等于用户登不进来。

---

## 落地与检查

| 检查 | 手段 |
|---|---|
| AUTH-1..7（DNS 身份） | DNS 探测脚本：核对 SPF/DKIM 位数/DMARC 策略/MTA-STS/TLS-RPT/CAA/BIMI，纳入 `audit.py` 的 site 类检查 |
| MAIL-1/4/6（头与双部件） | 发信单测：文本/HTML 关键信息一致、头唯一、营销带 RFC 8058 退订（见 miao `test_email_templates.py`） |
| MAIL-2（对比度） | 复用 DNA `build.py --check` 的对比口径，颜色不达标即失败 |
| SEC-1/2（日志卫生） | 单测断言：非 dev 下 log provider 拒发、日志脱敏（见 miao `test_guest_auth.py`） |
| SEND-1/3（幂等/抑制） | provider 适配层带 Idempotency-Key；集成测试覆盖退信→抑制回写 |
| OBS-2（阈值） | 事件管道 + 告警规则，演练一次投诉风暴 |

**参考实现：** `miao-ai` 的 `backend/app/security/email_templates.py` 与 `backend/app/api/guest_auth.py`
已按本标准实现事务 OTP 邮件（双部件一致、唯一 `X-Entity-Ref-ID`、`Auto-Submitted`、Reply-To、
AA 对比、幂等键、生产拒绝日志落码、邮箱脱敏）。其余产品与官网按本表逐条对齐。

## 附录：vertciti.com 当前整改清单

`check_messaging_dns.py vertciti.com --selector resend` 的实测结果（2026-10）与要加的记录：

| 规则 | 现状 | 要做的 |
|---|---|---|
| SPF | ✅ `v=spf1 include:zohomail.com ~all` | 若 Resend 也发根域，加 `include:_spf.resend.com` 并保持单条 SPF |
| DKIM | ❌ Resend selector 1024 位 | 在 Resend 重新生成 **2048 位** 密钥，更新 `resend._domainkey` CNAME/TXT |
| DMARC | 🟡 `p=quarantine` +rua | 看两周聚合报告无误报后，`_dmarc` 改 `p=reject`（可先 `pct=25` 灰度） |
| MTA-STS | ❌ 无 | 加 `_mta-sts` TXT `v=STSv1; id=...`，并在 `https://mta-sts.vertciti.com/.well-known/mta-sts.txt` 放 `version:STSv1 / mode:enforce / mx:... / max_age:604800` |
| TLS-RPT | ❌ 无 | 加 `_smtp._tls` TXT `v=TLSRPTv1; rua=mailto:tls-reports@vertciti.com` |
| CAA | ❌ 无 | 加 `CAA 0 issue "letsencrypt.org"`（按实际签发机构），限定谁能签证书 |
| BIMI | 🟡 无 | DMARC 到 `reject` 后，办 VMC 证书再发 `default._bimi` |

> 这些是 DNS/registrar 侧改动（不在代码仓），改完用上面的脚本复核到全绿。

---

> 本标准随实践演进。改动走 PR，并同步更新上面的"参考实现"与检查手段。
