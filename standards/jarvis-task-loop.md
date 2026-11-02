# jarvis-task 循环 · 状态机规程 v1.0

`jarvis-task` issue 是 Jarvis 向外部 Claude 派发任务的唯一格式（GitHub 即共享总线）。
任务用 [issue 表单](../.github/ISSUE_TEMPLATE/jarvis-task.yml) 创建，状态由 issue 标签表达。
评审裁决只存在于 PR 评论（见 [`IVV.md`](IVV.md)）。

## 标签集

`jarvis-task`（任务标记，始终存在）加且仅加一个状态标签：

| 标签 | 状态 |
| --- | --- |
| `jarvis-task:queued` | 已派发，等待执行 |
| `jarvis-task:working` | 执行中 |
| `jarvis-task:review` | PR 已开，等待评审 |
| `jarvis-task:done` | 已合并并验证 |
| `jarvis-task:blocked` | 受阻 |

表单创建时自动带上 `jarvis-task` 与 `jarvis-task:queued`。

## 状态机

```text
queued → working → review → done
                     │
                     └→ working   (评审意见退回)

任意状态 → blocked
```

## 谁来推动每次转移

| 转移 | 执行者 | 触发 |
| --- | --- | --- |
| queued → working | Jarvis | 执行会话开始时派发 |
| working → review | 执行者（外部 Claude） | 开 PR（`claude/*` 分支，针对 `main`，PR 正文引用该 issue） |
| review → done | Jarvis | 合并 PR，并在 issue 上发布验证回执 |
| review → working | Jarvis | 带评审意见退回（意见写在 PR 评论） |
| 任意 → blocked | 遇到阻塞的一方 | 在 issue 评论中写明阻塞点与根因 |

执行者从不自行合并 PR。

## blocked

- 任何状态都可进入 `blocked`，由遇到阻塞的一方设置。
- 必须在 issue 评论里点名阻塞项及根因。

## 回执格式

完成时（`review → done`），Jarvis 在 issue 上发**一条**评论，包含：

1. PR 链接
2. 合并 SHA
3. 新的 `main` 顶端 SHA
4. 验收结论（逐条对照 issue 的「验收」）

执行者开 PR 后，按 issue 的「回执格式」字段在 issue 上留言（PR 链接、分支名、逐条自检）。
