任务身份
[TASK_IDENTITY]

输出契约
1. 只输出完整 Python 代码，不要输出解释、Markdown 或代码块标记。
2. 禁止读取图片、音频、字体、配置或其他外部文件。只使用 pygame 图元和 `pygame.font.SysFont(None, size)`。
3. 所有常量、颜色、固定序列、地图、路径、波次或对象表写在文件顶部。调用 `random.seed(42)`，但禁止用随机结果决定地图、生成序列或核心规则状态。

坐标与时间
所有窗口均固定为 `800x600` 和 `60 FPS`；若游戏规格给出网格、世界坐标、浮点位置或取整方式，严格按该规格执行。

[GAME_COORDINATES]

颜色表
[COLOR_TABLE]

布局与实体
[LAYOUT_ENTITIES]

输入
[INPUT_RULES]

更新顺序
[UPDATE_ORDER]

独特规则
[DISTINCTIVE_RULES]

计分与终止
[SCORING_TERMINATION]

绘制顺序与 HUD
[DRAWING_HUD]

禁止项
禁止任何未在本 prompt 中列出的额外模式、菜单、素材、音效、联网功能和规则扩展。

[GAME_FORBIDDEN_ITEMS]

提交前检查
提交前按本规格逐项自检，最终只输出代码。

[GAME_PREFLIGHT_CHECK]
