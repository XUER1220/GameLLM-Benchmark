# Project Structure

## 1. Source of Truth

运行主链路只依赖以下来源：

| Path | Responsibility |
|---|---|
| `run_pipeline.py` | 单次完整实验入口：加载配置、读取 prompt、调用模型、评分、写结果 |
| `config.py` | 根目录、prompt 目录、数据目录和默认权重路径 |
| `config/games.yaml` | 启用的游戏 ID，按 `easy / medium / hard` 分组 |
| `config/models.yaml` | 模型名和 provider |
| `config/weights.yaml` | 四个评分维度的权重 |
| `prompts/<difficulty>/<game>/prompt.txt` | 发送给模型的完整任务定义 |

任务规则只维护在 `prompt.txt`。不再保留空的 `games/standard.py`、空 `baseline.md` 或未接入流水线的重复任务定义。

## 2. Runtime Flow

```text
config/games.yaml
        |
        v
prompts/<difficulty>/<game>/prompt.txt
        |
        v
run_pipeline.py -> llm_clients/*
        |
        v
data/raw/<run_id>/*.py
        |
        v
evaluator/* -> data/scores/<run_id>/*.json
        |
        v
scripts/visualize_results.py -> analysis/figures/<run_id>/*
```

`evaluator/dimension1` 和 `evaluator/dimension4` 自己负责受控子进程执行。旧的根级 `sandbox/runner.py` 没有被调用，已移除。

## 3. Evaluation Layers

| Path | Responsibility |
|---|---|
| `evaluator/dimension1/` | 可导入、窗口、事件循环、运行状态 |
| `evaluator/dimension2_functionality/` | 游戏专用 D2 静态探针和运行时辅助证据 |
| `evaluator/dimension3/` | 代码结构、命名、复用、复杂度 |
| `evaluator/dimension4/` | 可视反馈、流畅度、平衡性、动画表现 |
| `evaluation/rubrics/` | 评分口径说明 |
| `evaluation/test_specs/per_game/` | D2 游戏端口清单 |

当前 D2 仍以静态关键词和通用运行信号为主。严格 prompt 已增加独特机制；若要自动验证每个像素、颜色和独特机制，下一阶段需要增加专用动态测试端口。

## 4. Generated Data

| Path | Responsibility |
|---|---|
| `data/raw/<run_id>/` | 模型生成的 Python 文件 |
| `data/scores/<run_id>/` | 评分 JSON 和 `summary.json` |
| `analysis/figures/<run_id>/` | 图表、矩阵和 CSV |

仓库保留已有实验快照用于复现。`.gitignore` 会忽略后续新运行产生的文件，避免源码修改被实验输出淹没。

## 5. Utility Scripts

| Command | Responsibility |
|---|---|
| `python show_results.py` | 展示最新运行的汇总和逐条评分 |
| `python print_full_results.py --run <run_id>` | 过滤并打印完整评分 |
| `python scripts/run_repeated.py --times 5 --plot` | 重复执行流水线并生成稳定性分析 |
| `python scripts/visualize_results.py --run <run_id>` | 生成单次实验图表 |
| `python scripts/visualize_repeated_results.py --manifest <path>` | 生成重复实验图表 |
| `python scripts/check_prompt_contracts.py` | 校验启用 prompt 的章节、公共约束、模糊词和固定地图尺寸 |

## 6. Removed Skeletons

本次删除了未接入主链路的空配置、空文档、空脚本、空基准实现、空 notebook、旧日志、临时 API 探针和重复占位目录。历史 `data/` 与 `analysis/figures/` 保留。
