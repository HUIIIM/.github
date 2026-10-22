# vertciti 证据分级标准 v1.0（数据可信度四档）

**一句话：界面上、API 里、报告里的每一个数字，都要说清它是「核实过的」「算出来的」「演示用的」还是「没有」——四档之一，不许第五种，不许不说。**

适用于 [@HUIIIM](https://github.com/HUIIIM) 下所有对外展示或输出数字的产品：DealDesk、EchoWatch、Miao、Translator、官网。
它是 [AESTHETICS.md](../design/AESTHETICS.md)「证据优先」一条在数据层的展开，视觉由 [vertciti DNA](../design) 的 `.dna-ev` 组件实现。

`MUST` 不达标 = 不许上线；`SHOULD` 不达标 = 要有书面理由。

## 先分清两套「档」

| 用途 | 档位 | 组件 |
|---|---|---|
| **项目/功能进度**（官网路线图、能力清单） | ■ 已验证 / ■ 建设中 / ■ 计划中 | `.dna-dot` |
| **数据可信度**（某个数字、某条结论能信几分）——本标准 | 已核实 / 估算 / 演示 / 缺失 | `.dna-ev` |

两套不混用：一个数字不能是"建设中"，一项功能也不能是"估算"。

## 四档定义

| 档 | 机器值 `tier` | 含义 | 必带字段 | DNA 视觉 |
|---|---|---|---|---|
| **已核实** | `verified` | 来自可点开复核的外部来源，且来源与数值一致 | `source`（URL 或可追溯出处）+ `as_of`（YYYY-MM-DD） | 绿方块 `--ok` |
| **估算** | `estimate` | 由录入值、公式或模型算出；可复现，但不是事实 | `method`（口径/模型名，如 `buyer-box v2.3`、`lexicon-estimate`） | 灰方块 `--fg-3` |
| **演示** | `demo` | 夹具、桩、模拟结算、示例数据——不是真的 | `note`（说明是什么演示） | 黄方块 `--warn`（注意） |
| **缺失** | `missing` | 没有数据。显示 `—`，绝不补一个看起来合理的数 | `reason`（为什么没有：未配置 / 未接入 / 无命中） | 空心方块 |

规则：

- **E-1 `MUST`** 每个对外数字都能归到四档之一。归不进去 = 不展示。
- **E-2 `MUST`** `verified` 必须有 `source` + `as_of`；缺任一项自动降为 `estimate`（有口径）或 `missing`。
- **E-3 `MUST`** `estimate` 必须写明 `method`，且在界面上与 `verified` 视觉可区分（不同色块 + 文字），不能只靠颜色。
- **E-4 `MUST`** `demo` 数据在界面、导出文件、截图里都必须带「演示」标记；API 里 `tier:"demo"`，或沿用已有的 `stub: true` / `simulated` 标注（见下方映射）。
- **E-5 `MUST`** 服务不可用、未配置、无命中时返回 `missing` + `reason`（或已有的 `unavailable: true` + `note`），**绝不编造**。
- **E-6 `SHOULD`** 汇总值的档位取组成部分里**最弱**的一档（verified > estimate > demo > missing）：一个估算参与计算，结果就是估算。
- **E-7 `SHOULD`** 人工把候选证据「采用」为已核实时，保留原始出处与日期（DealDesk 的 EchoWatch 采用即此模式）。

## API 契约

需要逐值标注时，用一个统一的 `evidence` 对象（字段可省略的按上表）：

```json
{
  "value": 14138.4,
  "evidence": {
    "tier": "estimate",
    "method": "DealDesk property_metrics（按录入值计算）",
    "source": null,
    "as_of": null
  }
}
```

已上线的产品不需要立刻改字段名；下表是现有标注与四档的**对应关系**，新代码按四档写。

## 现有标注 → 四档映射（2026-10-22 实查）

| 产品 | 现有标注 | 对应档 |
|---|---|---|
| DealDesk | `✅ 已核实`（有内容＋有来源） | `verified` |
| DealDesk | `⚪ 待补充` / `待核实`（无来源） | `missing`（无内容）或 `estimate`（有内容无出处时应降档显示） |
| DealDesk | `ESTIMATE_TAG = "估算"`、`FORECAST_TAG = "情景预测"` | `estimate`（`method` = 估值法 / 情景） |
| DealDesk | 卖方口径、待验证 | `estimate`（`method` = 卖方口径） |
| EchoWatch | 每条提及带 `url` + `published_at` | `verified`（这条提及确实存在；**不等于**它说的事实为真） |
| EchoWatch | `sentiment.caliber = "lexicon-estimate"` | `estimate` |
| EchoWatch | 无数据日 `mean_score: null` / `"no_data"` | `missing` |
| Miao | `"stub": true`、`tx_hash` 以 `simulated-` 开头 | `demo` |
| Miao 工具 | `unavailable: true` + `note` | `missing` |
| 官网 | 「演示准备中 / 即将」卡片 | `demo` / `missing` |

## 视觉（DNA `.dna-ev`）

```html
<span class="dna-ev dna-ev--verified">已核实 · FHFA · 2026-08-25</span>
<span class="dna-ev dna-ev--estimate">估算 · buyer-box v2.3</span>
<span class="dna-ev dna-ev--demo">演示数据</span>
<span class="dna-ev dna-ev--missing">缺失 · 未配置 EchoWatch</span>
```

方块 8px、直角，文字始终跟随（不只靠颜色，满足 WCAG 1.4.1）。黄色只给 `demo`（注意），绿色只给 `verified`（DNA：绿 = 已验证，仅此）。

## 检查

- 代码评审：新增对外数字的 PR 必须说明每个数字属于哪一档。
- 产品测试：已上线的诚实降级测试（EchoWatch `no_data`、Miao `unavailable`、DealDesk `未配置 EchoWatch`）即 E-5 的回归测试，不许删。
