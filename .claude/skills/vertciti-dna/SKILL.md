---
name: vertciti-dna
description: >-
  Apply the vertciti DNA design language to any web UI — the house "light institutional"
  look, aligned to BlackRock's public design system (same palette: black / white / orange
  #FF4713 / yellow #FFCE00). Use when building or restyling a vertciti product interface
  (landing page, dashboard, report, app shell, email), converting an off-brand or dark/
  rounded/webfont app to the house style, making a product "match the website / 官网 DNA",
  or when the user asks for the vertciti look, 高大上 / 机构级 / institutional, or references
  BlackRock. Produces black-and-white editorial layouts: orange = pointer only, yellow =
  attention only, green = ok-status only; square corners, self-hosted Nunito Sans (same files as the website), 8px grid, left-
  aligned, bilingual (zh/en), honest provenance. NOT for choosing chart colors or building
  a chart — pair this with the dataviz skill for that.
---

# vertciti DNA — 应用设计语言

**一句话：证据的美学。** 黑白编辑版式承载内容，橙色只"指向"，黄色只"注意"，绿色只做"已验证"状态，
每个数字带出处和日期。看起来像一份可审计的年报，不是后台模板。对标 BlackRock 公开设计系统
([blackrock.com/design](https://www.blackrock.com/design))——主色同源（黑/白/橙 `#FF4713`/黄 `#FFCE00`）。

权威源在 `HUIIIM/.github/design/`：[`tokens.json`](https://github.com/HUIIIM/.github/blob/main/design/tokens.json)（令牌）、
[`AESTHETICS.md`](https://github.com/HUIIIM/.github/blob/main/design/AESTHETICS.md)（完整法条）、
`dist/dna.css`（生成的 CSS）。本 skill 是"怎么把它应用到一个界面上"的操作手册；拿不准细节时读 AESTHETICS.md。

## 十条铁律（违反其一就是跑偏）

1. **黑白为骨。** 大面积只用黑 `#000`、白 `#fff`、`#F3F3F3`。**一屏彩色面积 ≤ 10%。**
2. **橙 = 指针，仅此。** `#FF4713` 只出现在：当前项下划线、链接下划线/箭头、焦点环、数据条、
   被选中项。不做橙色大色块、不做橙色正文。
3. **黄 = 注意，仅此。** `#FFCE00` 只出现在：强调卡片、警示徽章、几何装饰、PF/角标。配黑字。
4. **绿 = 已验证状态，仅此。** `--ok #1D8348` 只做小状态方块、"值得买/BUY"结论、k-ok 数字。
   **绝不**做按钮、链接、进度条、大色块——那是最常见的"丑"。主操作一律黑底白字。
5. **左对齐。** 标题、导语、正文、表头全部左对齐。居中只给极少数独立 CTA / 空状态单行 / 版权行。
6. **直角。** 圆角 = 0。结构线三档：1px 分隔 / 2px 控件边 / 4px 卡片顶线。圆点状态灯 → 方块。
7. **官网字体：自托管 Nunito Sans。** `--font` = Nunito Sans + 系统 CJK 回落。字体文件随 DNA 一起 vendor
   （`design/dist/fonts/`，SIL OFL），**绝不从 Google Fonts / CDN 请求**；删掉 Inter/Geist 等其他 webfont 的 `<link>`。
8. **字重即层级。** 800 标题/按钮，700 标签/导航，400 正文，300 大数字。不用颜色分层级。
9. **8px 间距。** 所有间距是 8 的倍数（8/16/24/32/40/48/56/64/72/80/88/120）。
10. **诚实。** 每个数字带"来源 · 截至 YYYY-MM-DD"，并标数据可信度四档 `.dna-ev`（已核实/估算/演示/缺失，见 `standards/EVIDENCE.md`）；
    功能进度用三档 `.dna-dot`（■已验证/■建设中/■计划中），两套不混用；
    截图是真实运行；演示数据明确标注。

## 令牌（粘贴即用，浅色 + 深色）

```css
:root{
  --bg:#FFFFFF; --fg:#000000; --fg-2:#3F3F3F; --fg-3:#6B6B6B; --soft:#F3F3F3;
  --line:#DEDEDE; --strong:#000000; --card:#FFFFFF;
  --ok:#1D8348; --warn:#FFCE00; --on-warn:#000000; --bad:#C62828; --info:#2B7363;
  --orange:#FF4713; --yellow:#FFCE00;
  --font:"Nunito Sans",-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans SC","Noto Sans CJK SC",sans-serif;
  --mono:ui-monospace,"SFMono-Regular","Cascadia Code",Menlo,Consolas,"Liberation Mono",monospace;
  --radius:0; --focus:3px solid #FF4713;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#000000; --fg:#FFFFFF; --fg-2:#F5F5F5; --fg-3:#DEDEDE; --soft:#161616;
  --line:#3A3A3A; --strong:#FFFFFF; --card:#0E0E0E;
  --ok:#3FA86A; --bad:#E25555; --info:#5DB8A3;
}}
:root[data-theme="dark"]{ /* 同上 dark 值，让手动切换两向生效 */ }
```
对外产品默认**浅色机构版**（像官网）。深色只在产品确实是夜用工具、且刻意选 DNA dark-mode 时启用。

## 类型与间距

| 角色 | 规格 |
|---|---|
| Eyebrow | 12px / 800 / 大写 / 字距 .1em（中文不大写，.08em），色 `--fg-3` |
| Display（首屏） | `clamp(40px,6vw,80px)` / 800 / 字距 −.03em / 行高 1.05–1.1 |
| H1 页标题 | `clamp(32px,4vw,56px)` / 800 / 字距 −.02em |
| H2 区块 | `clamp(24px,2.6vw,36px)` / 800 |
| H3 卡片 | 20–24px / 800 |
| 正文 | 16px / 400 / 行高 1.6–1.75；中文 +.01em |
| 大数字 | `clamp(40px,4vw,64px)` / 300 / 等宽数字 |
| 出处/辅助 | 12–13px / `--fg-3` |

行高走 8 的倍数（16/20/24/28/32/40/48…）。标题 `text-wrap:balance`，**不用 `<br>` 硬换行**。

## 应用壳（让所有产品像"同一家公司"）

- **公司条**（黑底白字，~40–56px）：`vertciti.` · 产品名 · ■状态点 · 中/EN · 主操作。
- **导航当前项**：3px 橙色下划线 + 黑字。不用黑底胶囊、不用色块高亮。
- **主操作**：产品头右侧**唯一**一个黑色实心按钮。一屏只有一个主按钮。
- **页脚**：4px 黑线 + `vertciti.` 版本 · 诚实边界图例 · 回官网。
- **移动端**：公司条保留；导航变横向可滚动标签条，任何标签不折行。
组件清单（dna-btn / dna-card / dna-input / dna-seg / dna-tabs / dna-dot / dna-stat / dna-alert）
见 AESTHETICS.md §4，Tailwind 项目用 `dist/dna-tailwind.css`。

## 两种落地方式

**A. 新建界面** → 直接用上面的令牌 + 类型阶 + 应用壳从零搭。参考实现：
`anomalies-autogpt/frontend/public/demo/index.html`（Miao 演示站，纯静态、动态可视化、明暗双主题）。

**B. 改造已有 App**（最省力、低风险）——"皮肤覆盖层"手法，参考 `vertciti-dealdesk`：
1. 看这个 App 是否已用 CSS 变量集中管理主题（大多数是）。
2. 在它主样式表**末尾**追加一个「DNA 浅色皮肤」块：重定义所有令牌为上面的浅色值，
   `--radius:0`，`body{font-family:var(--font)}`，`h1..h4{text-align:left}`。后写的同特异性规则胜出，
   不用动原有结构规则。模板见 [`references/skin-overlay.css`](references/skin-overlay.css)。
3. **收敛"杂色"**：把原来的青/蓝/紫等强调色（如 `--teal`/`--accent`）一律重映射到
   墨黑/中性；**主操作按钮改黑底白字**（别让它变绿/变青——这是最常见的翻车点）；
   链接改 `color:inherit` + 橙色下划线。绿色只留给 ok 状态方块。
4. 修少量**硬编码深色十六进制**（如 `#0d1526`、`#060a13`）→ 白/中性；圆点 `border-radius:50%` → `0`。
5. 删其他 webfont `<link>`（Inter/Geist）；把 `design/dist/fonts/`（woff2 + OFL.txt）拷进 App 的静态目录，
   在皮肤块前加 `@font-face`（模板里有）。
6. 三视口（390/768/1440）+ 明暗 + 中英 截图自检。

## 双语（所有对外界面都要）

中英双版。已有 i18n（`data-i18n` + 字典）的，**逐个保留 `data-i18n` 属性**，只改样式别动结构；
新建的用 `data-i18n` + 一个字典，或两套页面。切换入口放公司条右侧（中/EN），`?lang=en` 深链可直达。
缺项回退原文，**绝不留空**。

## 发布前质量门（全过才发）

- [ ] 390 / 768 / 1440 三视口截图：无折行、无横向溢出、无重叠；每页有可见 H1。
- [ ] 明 + 暗两主题都正确（`body` 有显式背景；无只在一种主题可读的颜色）。
- [ ] 中 + 英两版都通：EN 不漏翻、不撑破布局。
- [ ] 对比度 ≥ AA（正文 4.5:1 / 大字 3:1），用 `design/build.py --check` 口径算，不靠肉眼；
      页面级再跑 `standards/a11y/contrast_audit.js`（浅/深 × 390/1280），**禁用控件、占位字、反色卡片里的字都要过**。
- [ ] 禁用 / 过期 / 次要 **不用 opacity**（用 `--fg-2`/`--fg-3`、虚线边框、文字标签）；反色表面局部重定义 `--fg`/`--strong` 等变量。
- [ ] 无 DNA 外颜色、无圆角、无外部字体请求（只允许自托管 Nunito Sans；`dna-drift` + grep）。
- [ ] 触控目标 ≥ 44×44；焦点环可见；`prefers-reduced-motion` 下动效关闭。
- [ ] 诚实：每个数字有出处；演示数据标注；截图真实。

## 最常见的五个翻车点（照着避）

1. **绿/青按钮** → 主操作必须黑底白字；绿只做 ok 状态。
2. **居中版式** → 全部左对齐。
3. **圆角 + 杂牌 webfont** → 直角 + 自托管 Nunito Sans（和官网同一份文件）。
4. **彩色面积过大** → 橙/黄/绿都是"点睛"，一屏彩色 ≤ 10%。
5. **编数字 / 无出处 / 演示数据不标** → 诚实是硬门禁。

> 需要图表/数据可视化配色时，**叠加 `dataviz` skill**：本 skill 定方向与底色，dataviz 定图表的
> 分类/顺序/发散色与校验。两者一起用。
