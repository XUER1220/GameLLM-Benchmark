import pygame
import random

# 初始化
pygame.init()

# 常量定义
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_SIZE = 24
GRID_COLS, GRID_ROWS = 10, 20
GAME_WIDTH = GRID_COLS * GRID_SIZE
GAME_HEIGHT = GRID_ROWS * GRID_SIZE
FPS = 60
DROP_SPEED = 500

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
PURPLE = (128, 0, 128)

# 方块形状定义（标准7种）
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]]   # L
]

# 方块颜色
SHAPE_COLORS = [CYAN, YELLOW, PURPLE, GREEN, RED, BLUE, ORANGE]

# 生成新方块
def create_new_piece():
    shape_idx = random.randint(0, len(SHAPES) - 1)
    return {
        "shape": SHAPES[shape_idx],
        "color": SHAPE_COLORS[shape_idx],
        "x": GRID_COLS // 2 - len(SHAPES[shape_idx][0]) // 2,
        "y": 0
    }

# 旋转方块
def rotate_piece(piece):
    shape = piece["shape"]
    # 旋转矩阵
    rotated = [[shape[j][i] for j in range(len(shape))] for i in range(len(shape[0]) - 1, -1, -1)]
    return {
        "shape": rotated,
        "color": piece["color"],
        "x": piece["x"],
        "y": piece["y"]
    }

# 检查碰撞
def check_collision(board, piece, offset_x, offset_y):
    shape = piece["shape"]
    for r, row in enumerate(shape):
        for c, cell in enumerate(row):
            if cell:
                new_x, new_y = piece["x"] + c + offset_x, piece["y"] + r + offset_y
                if (
                    new_x < 0 or new_x >= GRID_COLS or 
                    new_y >= GRID_ROWS or 
                    (new_y >= 0 and board[new_y][new_x])
                ):
                    return True
    return False

# 消除行
def clear_lines(board):
    lines_cleared = 0
    for r in range(GRID_ROWS - 1, -1, -1):
        if all(board[r]):
            board.pop(r)
            board.insert(0, [0] * GRID_COLS)
            lines_cleared += 1
    return lines_cleared

# 绘制网格
def draw_grid(screen, start_x, start_y):
    for x in range(0, GAME_WIDTH + 1, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (start_x + x, start_y), (start_x + x, start_y + GAME_HEIGHT))
    for y in range(0, GAME_HEIGHT + 1, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (start_x, start_y + y), (start_x + GAME_WIDTH, start_y + y))

# 绘制方块
def draw_block(screen, x, y, color):
    rect = pygame.Rect(x * GRID_SIZE + GAME_OFFSET_X, y * GRID_SIZE + GAME_OFFSET_Y, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)

# 绘制文本
def draw_text(screen, text, font, x, y, color=WHITE):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

# 初始化游戏
def init_game():
    board = [[0] * GRID_COLS for _ in range(GRID_ROWS)]
    current_piece = create_new_piece()
    next_piece = create_new_piece()
    last_drop_time = 0
    score = 0
    lines_cleared = 0
    game_over = False
    return {
        "board": board,
        "current_piece": current_piece,
        "next_piece": next_piece,
        "last_drop_time": last_drop_time,
        "score": score,
        "lines_cleared": lines_cleared,
        "game_over": game_over
    }

# 绘制游戏状态
def draw_game(screen, game_state):
    # 填充背景
    screen.fill(BLACK)
    
    # 绘制棋盘
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if game_state["board"][r][c]:
                draw_block(screen, c, r, game_state["board"][r][c])
    
    # 绘制当前方块
    current = game_state["current_piece"]
    for r, row in enumerate(current["shape"]):
        for c, cell in enumerate(row):
            if cell:
                draw_block(screen, current["x"] + c, current["y"] + r, current["color"])
    
    # 绘制网格和边界
    draw_grid(screen, GAME_OFFSET_X, GAME_OFFSET_Y)
    
    # HUD区域
    hud_x = GAME_WIDTH + GAME_OFFSET_X + 20
    font = pygame.font.SysFont(None, 32)
    
    draw_text(screen, f"SCORE: {game_state['score']}", font, hud_x, GAME_OFFSET_Y)
    draw_text(screen, f"LINES: {game_state['lines_cleared']}", font, hud_x, GAME_OFFSET_Y + 50)
    draw_text(screen, f"LEVEL: 1", font, hud_x, GAME_OFFSET_Y + 100)
    draw_text(screen, f"NEXT:", font, hud_x, GAME_OFFSET_Y + 150)
    
    # 绘制下一个方块
    next_piece = game_state["next_piece"]
    if next_piece["shape"]:
        for r, row in enumerate(next_piece["shape"]):
            for c, cell in enumerate(row):
                if cell:
                    draw_block(screen, hud_x // GRID_SIZE + c, 7 + r, next_piece["color"])
    
    # 游戏结束提示
    if game_state["game_over"]:
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (GAME_OFFSET_X, GAME_OFFSET_Y))
        
        large_font = pygame.font.SysFont(None, 64)
        draw_text(screen, "GAME OVER", large_font, GAME_OFFSET_X + GAME_WIDTH // 2 - 120, 
                  GAME_HEIGHT // 2 + GAME_OFFSET_Y - 32, RED)
        draw_text(screen, f"FINAL SCORE: {game_state['score']}", font, 
                  GAME_OFFSET_X + GAME_WIDTH // 2 - 120, GAME_HEIGHT // 2 + GAME_OFFSET_Y + 32)
        draw_text(screen, "Press R to Restart", font, 
                  GAME_OFFSET_X + GAME_WIDTH // 2 - 140, GAME_HEIGHT // 2 + GAME_OFFSET_Y + 96)

# 主游戏循环
def main():
    # 设置窗口
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris Medium")

    # 全局常量
    global GAME_OFFSET_X, GAME_OFFSET_Y
    GAME_OFFSET_X = (SCREEN_WIDTH - GAME_WIDTH) // 2 - 50
    GAME_OFFSET_Y = (SCREEN_HEIGHT - GAME_HEIGHT) // 2

    # 初始化随机种子
    random.seed(42)

    # 游戏状态初始化
    game_state = init_game()

    # 控制变量
    clock = pygame.time.Clock()
    drop_timer = 0
    current_piece = game_state["current_piece"]
    board = game_state["board"]

    running = True
    while running:
        # 帧率控制
        dt = clock.tick(FPS)
        drop_timer += dt

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_state["game_over"]:
                    game_state = init_game()
                    board = game_state["board"]
                    current_piece = game_state["current_piece"]
                    drop_timer = 0
                    game_state["game_over"] = False
                elif not game_state["game_over"]:
                    if event.key == pygame.K_LEFT:
                        if not check_collision(board, current_piece, -1, 0):
                            current_piece["x"] -= 1
                    elif event.key == pygame.K_RIGHT:
                        if not check_collision(board, current_piece, 1, 0):
                            current_piece["x"] += 1
                    elif event.key == pygame.K_UP:
                        rotated = rotate_piece(current_piece)
                        if not check_collision(board, rotated, 0, 0):
                            current_piece = rotated
                    elif event.key == pygame.K_DOWN:
                        if not check_collision(board, current_piece, 0, 1):
                            current_piece["y"] += 1
                            drop_timer = 0
                    elif event.key == pygame.K_SPACE:
                        # 硬降
                        while not check_collision(board, current_piece, 0, 1):
                            current_piece["y"] += 1
                        drop_timer = 0

        # 自动下落逻辑
        if drop_timer >= DROP_SPEED and not game_state["game_over"]:
            drop_timer = 0
            if not check_collision(board, current_piece, 0, 1):
                current_piece["y"] += 1
            else:
                # 锁定方块到棋盘
                for r, row in enumerate(current_piece["shape"]):
                    for c, cell in enumerate(row):
                        if cell:
                            board_y = current_piece["y"] + r
                            board_x = current_piece["x"] + c
                            if 0 <= board_y < GRID_ROWS and 0 <= board_x < GRID_COLS:
                                board[board_y][board_x] = current_piece["color"]
                
                # 消除行
                lines = clear_lines(board)
                if lines > 0:
                    scores = {1: 100, 2: 300, 3: 500, 4: 800}
                    game_state["score"] += scores.get(lines, 0)
                    game_state["lines_cleared"] += lines

                # 生成新方块
                current_piece = game_state["next_piece"]
                game_state["next_piece"] = create_new_piece()
                
                # 检查游戏结束
                if check_collision(board, current_piece, 0, 0):
                    game_state["game_over"] = True
                
                # 更新当前方块到游戏状态
                game_state["current_piece"] = current_piece
                game_state["board"] = board

        # 绘制画面
        draw_game(screen, game_state)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()