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
- 有不达标即退出码 1，可直接放进 CI。

## 接入

- **DNA**：`.github/workflows/design.yml` 的 `contrast` 作业对 `design/preview/components.html`（全部组件 × 全部状态）跑浅/深 × 390/1280。新组件必须加进这一页。
- **产品**：在各产品 CI 里起服务后，对主要页面跑同样的四组组合（见各仓库的 `contrast` 作业）。
