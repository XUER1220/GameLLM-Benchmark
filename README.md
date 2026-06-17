# GameLLM-Benchmark

GameLLM-Benchmark 用同一套流程比较不同 LLM 生成单文件 `pygame` 游戏的能力：

`任务配置 -> 严格 Prompt -> 模型生成代码 -> 自动执行 -> 四维评分 -> 汇总与可视化`

## 快速开始

1. 在 `config/models.yaml` 配置模型，并设置对应环境变量。
2. 在 `config/games.yaml` 选择本次评测游戏。
3. 运行 `python run_pipeline.py`。
4. 运行 `python show_results.py` 查看最新汇总。
5. 运行 `python print_full_results.py --run <run_id>` 查看逐项评分。

修改 prompt 后先运行 `python scripts/check_prompt_contracts.py`。

## 核心目录

| 路径 | 职责 |
|---|---|
| `prompts/` | prompt 主入口、公共片段、游戏规格和生成的完整 prompt |
| `config/` | 启用游戏、模型和权重配置 |
| `llm_clients/` | 各模型厂商 API 适配器 |
| `evaluator/` | D1 可执行性、D2 功能、D3 代码质量、D4 体验评分实现 |
| `evaluation/` | 评分规则和 D2 游戏测试端口说明 |
| `data/raw/` | 模型生成代码；按运行时间保存 |
| `data/scores/` | 单任务评分和运行汇总；按运行时间保存 |
| `analysis/figures/` | 从评分结果生成的图表和 CSV |
| `scripts/` | 重复实验和可视化脚本 |

完整职责、数据流和清理边界见 `docs/project_structure.md`。

## 项目结构

```text
GameLLM-Benchmark/
├─ config/                         # 游戏、模型和评分权重
├─ prompts/                        # 发送给模型的严格任务定义
│  ├─ main.md                       # Prompt 主入口和章节顺序
│  ├─ specs/                        # 每个游戏的差异规格
│  ├─ easy/                        # 4 个基础任务
│  ├─ medium/                      # 4 个组合规则任务
│  ├─ hard/                        # 2 个复杂系统任务
│  └─ STRICT_PROMPT_TEMPLATE.md    # 新任务统一模板
├─ llm_clients/                    # OpenAI、Anthropic、Qwen、Gemini、Bedrock 适配
├─ evaluator/
│  ├─ dimension1/                  # D1 可执行性
│  ├─ dimension2_functionality/    # D2 游戏规则完整性
│  ├─ dimension3/                  # D3 代码质量
│  └─ dimension4/                  # D4 体验与交互
├─ evaluation/                     # 评分口径和游戏测试端口说明
├─ data/
│  ├─ raw/<run_id>/                # 模型生成的 Python 文件
│  └─ scores/<run_id>/             # 单任务评分与 summary.json
├─ analysis/figures/               # 可视化图表和 CSV
├─ scripts/                        # Prompt 校验、重复实验、可视化
├─ run_pipeline.py                 # 单次完整实验入口
├─ show_results.py                 # 查看最新汇总
└─ print_full_results.py           # 查看逐项评分
```

## Prompt 规范

Prompt 不再依赖经典游戏默认规则。每个任务必须明确写出坐标系、矩形尺寸、RGB 颜色、初始状态、更新顺序、碰撞边界、计分、结束条件和独特机制。

Prompt 维护源是 `prompts/main.md + prompts/specs/`；`main.md` 里用 `[PLACEHOLDER]` 占位符切换不同游戏规格，`prompts/<difficulty>/<game>/prompt.txt` 是生成的兼容产物。统一结构见 `prompts/STRICT_PROMPT_TEMPLATE.md`，当前任务清单见 `prompts/README.md`。

## 当前任务

| 难度 | ID | 新任务名 | 去模板化机制 |
|---|---|---|---|
| Easy | `snake` | Prism Relay | 每第三个信标留下延迟激活的残留障碍 |
| Easy | `flappy_bird` | Pulse Gates | 必须触碰门内脉冲球，漏球立即失败 |
| Easy | `dodge_blocks` | Lane Cipher | 固定车道移动并收集芯片 |
| Easy | `pong` | Gate Rally | 只有命中轮换高亮门才得分 |
| Medium | `tetris` | Glyph Stack | 六种自定义五格符文块和通量奖励 |
| Medium | `space_invaders` | Polarity Fleet | 弹药极性必须匹配敌人颜色 |
| Medium | `pacman` | Switch Maze | 固定迷宫中按顺序打开两道门 |
| Medium | `super_mario_bros` | Beacon Courier | 收集四个电池后才可触发出口 |
| Hard | `roguelike_dungeon` | Rune Vault | 固定双层地图和顺序符文 |
| Hard | `tower_defense` | Relay Defense | 双色护盾、塔型克制和限定建造格 |

## 评分维度

| 维度 | 权重 | 内容 |
|---|---:|---|
| D1 Executability | `0.20` | 导入、窗口、事件循环、运行状态 |
| D2 Functionality | `0.50` | 规则闭合、状态演化、交互、反馈、终止 |
| D3 Code Quality | `0.15` | 结构、复用、命名、常量、复杂度 |
| D4 UX | `0.15` | 可视反馈、流畅度、平衡性、动画表现 |

## 常用命令

```bash
python scripts/build_prompts.py
python scripts/check_prompt_contracts.py
python run_pipeline.py
python show_results.py
python print_full_results.py --run <run_id>
python scripts/run_repeated.py --times 5 --plot
python scripts/visualize_results.py --run <run_id>
```
