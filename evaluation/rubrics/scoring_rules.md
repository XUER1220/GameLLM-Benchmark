# Scoring Rules

## Dimension 2 Functionality

D2 = 规则闭合性 + 状态演化性 + 交互有效性 + 目标与反馈一致性 + 约束与终止机制。每项 0/1/2 分，满分 10 分。

| 上位标准 | 静态主证据 | Runtime 辅证据 | 红线与封顶 |
|---|---|---|---|
| Rule Completeness | 规则判断、状态更新、反馈输出 | 核心事件后状态或反馈变化 | 仅有展示无规则时最高 1 分 |
| State Evolution | 主循环、时间步、实体状态持续更新 | 连续运行中状态变化 | 无持续更新机制时最高 1 分 |
| Interaction Validity | 输入事件分支、输入到状态变量链路 | 注入输入后状态变化 | 输入完全无效直接 0 分 |
| Goal-Feedback Alignment | 目标条件、计分、进度或胜负提示 | 行为后反馈可见 | 反馈与目标脱钩时最高 1 分 |
| Constraint & Termination | 边界、碰撞、失败/通关条件、结束状态 | 触发后进入结束/胜负状态 | 缺失终止机制直接 0 分 |

## Specialized Test Ports

每个游戏 profile 定义 3-8 个测试端口。端口不是分数项，只是证据探针。

端口结论：

- `PASS`：静态结构完整且有 runtime 支持，或专用 runtime 端口通过。
- `PARTIAL`：只有部分静态证据，或只有弱 runtime 证据。
- `FAIL`：无可用证据。

上位标准判分：

- 有 `PASS` 端口支撑且 runtime 不冲突：2 分。
- 只有 `PARTIAL` 端口，或静态强但 runtime 不支持：1 分。
- 无可用端口证据：0 分。

报告必须同时输出主分、端口结论、静态命中、runtime 来源和冲突封顶原因。
