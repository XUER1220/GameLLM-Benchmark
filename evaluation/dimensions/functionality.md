# Dimension 2: Functionality

维度2只计算 5 个上位标准，每项 0/1/2 分，总分 10 分。游戏专用项不单独加分，只作为证据端口支撑上位标准判分。

## Main Criteria

| 标准 | 评估对象 | 0 分 | 1 分 | 2 分 |
|---|---|---|---|---|
| Rule Completeness | 行为 -> 结果 -> 反馈是否闭合 | 没有核心规则 | 有规则但断链 | 行为、结果、反馈形成闭环 |
| State Evolution | 游戏是否随时间持续变化 | 基本静态 | 有变化但弱或不稳定 | 循环驱动、状态持续演化 |
| Interaction Validity | 输入是否真实影响状态 | 无有效交互 | 有输入但影响弱 | 输入稳定改变游戏状态 |
| Goal-Feedback Alignment | 目标和反馈是否一致 | 无目标且无反馈 | 目标或反馈不完整 | 目标明确，反馈与行为结果一致 |
| Constraint & Termination | 约束和终止是否清晰 | 无边界无结束 | 有部分约束或结束 | 限制清晰且可进入胜负/结束状态 |

## Scoring Flow

1. 根据 `game_id` 选择游戏 profile。
2. 执行该 profile 下的专用测试端口，端口只产出 `PASS/PARTIAL/FAIL` 证据。
3. 将端口证据映射到 5 个上位标准。
4. 对每个上位标准按 0/1/2 判分，总分为 5 项相加。
5. 若没有对应 profile，则回退到通用静态/运行时评分。

## Evidence Policy

静态证据为主，runtime 证据为辅。静态证据检查代码结构、变量、分支、碰撞、反馈输出等机制；runtime 证据来自 D1 或更细粒度的 `runtime_signals["test_ports"]`。

当前支持两类 runtime：

- `generic_runtime`：D1 提供的通用信号，如 `state_changed`、`input_effective`、`feedback_visible`、`terminated`。
- `test_port`：未来可由专用动态测试注入的细粒度端口结果，如 `{"food_growth": {"status": "PASS"}}`。

冲突处理：

- 静态强、runtime 无支持：该上位标准最高 1 分。
- runtime 端口强、静态弱：可给 1-2 分，但证据中保留来源。
- 静态和 runtime 都无：0 分。
