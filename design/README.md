# vertciti DNA — 设计系统 v4

**一份 token，全部产品同一张脸。** 本目录是 vertciti 所有产品界面的唯一设计源，
从生产官网 [vertciti.com](https://vertciti.com)（官网 v4，`site.css`）提取，
2026-10-22 定版。官网改了，这里跟着改；这里改了，各仓库重新 vendor。

| 文件 | 用途 |
|---|---|
| [`tokens.json`](tokens.json) | **唯一事实源**：颜色（明/暗/品牌/色阶）、字体、版式、形状、动效、层级 |
| [`src/base.css`](src/base.css) | 元素默认样式 + `dna-` 前缀组件（按钮/卡片/表单/徽章/提示） |
| [`build.py`](build.py) | 生成 `dist/`；`--check` 在 CI 里校验产物未漂移 + WCAG 对比度 |
| [`dist/dna.css`](dist/dna.css) | 纯 HTML/CSS 项目用（FastAPI 模板、静态页） |
| [`dist/dna-tailwind.css`](dist/dna-tailwind.css) | Tailwind v4 项目用：把 Tailwind 默认色阶/圆角/字体整体映射到 DNA |

## DNA 七条

1. **黑白为骨。** 正文 `#000` on `#FFF`，暗色模式整体对调。灰只用四档：
   `#3F3F3F` / `#6B6B6B` / `#DEDEDE` / `#F3F3F3`。
2. **橙色只做"指向"。** `#FF4713` 用于焦点环、链接下划线、当前项标记——
   **不做大面积底色，不做正文文字色**（白底对比度 3.4，只够非文字 UI）。
3. **黄色只做"注意"。** `#FFCE00` 底 + 黑字（14:1），用于跳转链接、选中、警示徽章。
4. **直角。** 全站 `border-radius: 0`；唯一例外是圆点/头像 (`rounded-full`)。
5. **粗标题、松正文。** 标题 800/700 字重、负字距；正文 16px、行高 1.75、等宽数字
   (`tabular-nums`)；中文加 `.01em` 字距。
6. **系统字体，零外部请求。** 不加载 Google Fonts / CDN 字体——与官网 CSP 和隐私承诺一致。
7. **克制的动效。** 0.15–0.25s；尊重 `prefers-reduced-motion`；阴影只有一种（`--shadow-pop`）。

## 状态色（应用扩展）

官网是叙事站，没有错误态；产品需要。扩展四个语义色，全部过 WCAG AA：

| token | 明 | 暗 | 用法 |
|---|---|---|---|
| `--ok` | `#1D8348` | `#3FA86A` | 成功、通过、在线 |
| `--bad` | `#C62828` | `#E25555` | 错误、失败、危险操作（**不用橙色表示错误**——橙色是品牌指向色） |
| `--warn` / `--on-warn` | `#FFCE00` / `#000` | 同 | 警示（黄底黑字，永远不用黄字） |
| `--info` | `#2B7363` | `#5DB8A3` | 信息、中性提示、数据链接 |

色阶规则：浅色底上的文字用 **700 及以上**（品牌绿 600 在 100 底上只有 4.1:1）。

## 接入

**Tailwind v4（Next.js 项目）** —— `globals.css`：

```css
@import "tailwindcss";
@import "./dna-tailwind.css";   /* vendored from HUIIIM/.github design/dist */
```

现有 `bg-gray-100`、`text-blue-600`、`rounded-lg` 等类名**无需改动**，自动换成 DNA 色阶与直角。
新代码优先用语义类：`bg-dna-bg text-dna-fg border-dna-line text-dna-fg-3 bg-dna-soft`。

**纯 CSS（FastAPI/Jinja、静态 HTML）**：

```html
<link rel="stylesheet" href="/static/dna.css">
```

然后把页面里的硬编码颜色换成 `var(--fg)` / `var(--line)` 等，按钮用 `.dna-btn`。

**明暗切换**：默认跟随系统；强制主题设 `<html data-theme="dark|light">`。

## 更新流程

1. 改 `tokens.json`（或 `src/base.css`）→ `python3 design/build.py` → 提 PR。
2. CI（`design.yml`）跑 `build.py --check`：产物与源一致、对比度全过。
3. 合并后各仓库重新拷贝 `dist/` 文件；各仓库 CI 的 `dna-drift` 任务会提示版本落后。

## 不做什么

- 不发 npm 包：单人公司，vendor 一个文件比维护包发布链路更可靠；漂移由 CI 抓。
- 不改历史快照仓库（`vertciti-website`）：档案原样保留是它存在的意义。
- 不改上游 fork（`tenacity`、`pgvector-python`）：那是别人的项目。
