# Prompt Layout

Prompt 的维护源现在拆成两层：

- `prompts/main.md`：唯一主入口，包含公共规则、最终章节顺序和 `[PLACEHOLDER]` 占位符。
- `prompts/specs/<difficulty>/<game>.md`：每个游戏的差异规格。

流水线调用模型前会用 `prompt_builder.py` 静态拼接完整 prompt。`prompts/<difficulty>/<game>/prompt.txt` 是由 `python scripts/build_prompts.py` 生成的兼容产物，用于人工审阅和旧路径兼容，不是新的维护源。

统一结构和编写口径见 `STRICT_PROMPT_TEMPLATE.md`。

## Enabled Tasks

| Difficulty | Game ID | Distinctive rule |
|---|---|---|
| easy | `snake` | 每第三个信标会留下延迟激活的残留障碍 |
| easy | `flappy_bird` | 必须穿过管道间隙中的脉冲球，漏球立即失败 |
| easy | `dodge_blocks` | 固定车道移动，并穿插可收集的金色芯片 |
| easy | `pong` | 出界位置必须命中本回合指定得分门 |
| medium | `tetris` | 使用自定义五格符文块和通量单元，不使用标准七种方块 |
| medium | `space_invaders` | 玩家需要切换弹药极性匹配敌人颜色 |
| medium | `pacman` | 固定迷宫包含有顺序要求的开门开关 |
| medium | `super_mario_bros` | 横向卷轴出口需要先收集四个电池 |
| hard | `roguelike_dungeon` | 固定双层地牢中必须按顺序激活符文 |
| hard | `tower_defense` | 敌人具有双色护盾，塔型与护盾形成克制 |

修改 `main.md` 或 `specs/` 后，先运行：

```bash
python scripts/build_prompts.py
python scripts/check_prompt_contracts.py
```
