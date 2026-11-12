# 可读性门禁（对比度）· Readable-text gate

**一句话：屏幕上任何一段字——包括按钮、禁用控件、占位提示、深色卡片里的字——在真实浏览器里实际渲染出来的颜色，都必须达到 WCAG AA。由脚本在 CI 里量，不靠肉眼。**

## 为什么要这道门（2026-10-22 实际踩到的坑）

| 产品 | 症状 | 原因 |
|---|---|---|
| EchoWatch 演示站 | iPhone 上「标注」按钮、日期框、占位字几乎看不见 | 禁用控件用 `opacity:.45`；iOS 又给禁用输入框文字再上一层灰；空的禁用日期框直接空白 |
| 官网首页 | 黑色磁贴里的小标题「生产线」黑字黑底，完全看不见；深色模式黄磁贴白字 1.5:1 | 小标题颜色跟页面主题走，没跟磁贴走 |
| DNA 本身 | `.dna-btn[disabled]{opacity:.45}`；墨色卡里标题黑字黑底 | 设计系统把错误写进了源头，所有产品继承 |

## 规则

- **A11Y-1** 可见文字对比度 ≥ 4.5:1（≥24px 或 ≥18.66px 粗体：≥ 3:1）。**禁用控件不豁免**（WCAG 豁免它，我们不豁免——用户要看得清"这里不能用"）。
- **A11Y-2** 不用 `opacity` 表达"禁用 / 过期 / 次要"。用颜色（`--fg-2` / `--fg-3`）、虚线边框、文字标签。
- **A11Y-3** 反色表面（墨色卡、黄卡、黑色磁贴）**局部重定义主题变量**（`--fg` `--strong` `--fg-2` `--fg-3` …），让里面的一切自动跟随表面。
- **A11Y-4** 禁用输入框同时设 `color` 和 `-webkit-text-fill-color`（iOS）。

## 用法

```bash
npm i playwright            # 或用已装的 Chromium
node standards/a11y/contrast_audit.js <url> [--width 390|1280] [--scheme light|dark] [--inject guard.html]
```

- 量的是**实际渲染**：文字色（含 `-webkit-text-fill-color`）× 祖先 `opacity` 连乘，叠在逐层合成的背景上；
  颜色走浏览器 canvas 转换，`lab()`/`oklab()`（Tailwind v4）也对。
- 先整页滚动、等动画结束；可疑项再逐个滚到屏幕中央复测（避免"滚动淡入"误报）。
- 不可见的（`display:none`、被 `overflow:hidden` 裁掉、屏幕外）不算。
- 登录后的界面：`--fixtures api.json` 用一份 JSON（`{"GET /api/v1/x": {status, contentType, body}}`，按「方法 + 路径」匹配、忽略查询串、缺的一律 404）回放全部 `/api/` 请求，CI 不必起后端；fixture 只能放合成数据，不放个人数据和密钥。
- 应用自带的主题开关（不走 `prefers-color-scheme` 的深夜模式等）：`--ls key=value` 在应用启动前预置 localStorage。
- 有不达标即退出码 1，可直接放进 CI。

## 接入

- **DNA**：`.github/workflows/design.yml` 的 `contrast` 作业对 `design/preview/components.html`（全部组件 × 全部状态）跑浅/深 × 390/1280。新组件必须加进这一页。
- **DNA 表面矩阵**：`design/preview/surfaces.html` 由 `build.py` 生成——每个文字 token、徽章、证据档、链接放在页面/软底/卡片/墨色/强调五种表面上，同样跑四组组合。v4.0 的深色卡片上状态徽章只有 2.84–4.44:1，就是因为没有这一页（#40）。
- **产品**：在各产品 CI 里起服务后，对主要页面跑同样的四组组合（见各仓库的 `contrast` 作业）。

## 版式门禁 · layout gate

```bash
node standards/a11y/layout_audit.js <url> [--width 390|1280] [--scheme light|dark] [--min 44]
```

- **溢出**：页面宽于视口（WCAG 1.4.10 重排）即失败。
- **一字一行**：一段文字折行数 ≥ 字数的一半（例：v4.0 画廊里没有 `dna-span-*` 的卡片被挤成 1/12 宽）。
- **触控目标**：链接、按钮、表单控件、标签页 < 44×44px 即失败；句中链接豁免（同 WCAG 2.2 SC 2.5.8）。其他刻意例外标 `data-target-exempt="理由"`，留痕可审。

## 非文本对比度门禁 · Non-text contrast gate（WCAG 2.2 SC 1.4.11，SOTA DS-1）

`node standards/a11y/nontext_audit.js <url> [--width 390] [--scheme light|dark] [--min 3]`

- **组件边界**：画成形状的控件（有填充或描边：输入框、按钮、标签页）靠填充或描边与周围拉开 ≥ 3:1。只有文字的控件（文字按钮、链接）靠文字识别，由上面的文字门禁管，这里跳过。
- **焦点指示**：像键盘用户一样逐个 Tab；每个拿到焦点的元素必须画出 outline 或 box-shadow，颜色对其背后实际渲染的颜色 ≥ 3:1。
- 刻意的例外标 `data-nontext-exempt="<原因>"`，可审。
- **反例夹具**：`fixtures/nontext-bad.html` 有 4 个已知缺陷，CI 要求门禁在这一页上报告恰好 4 个，证明门禁没有退化成永远通过。
- 首次运行就抓到 DNA 4.1.1 的真实缺陷：黄色强调卡里的焦点环是橙色，2.28:1（见 `design/CHANGELOG.md` 4.1.2）。
