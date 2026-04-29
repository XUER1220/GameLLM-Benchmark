import pygame
import random

# 固定常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_SIZE = 24
GRID_WIDTH = 10
GRID_HEIGHT = 20
BOARD_X = (SCREEN_WIDTH - GRID_WIDTH * BLOCK_SIZE) // 2 - BLOCK_SIZE // 2
BOARD_Y = (SCREEN_HEIGHT - GRID_HEIGHT * BLOCK_SIZE) // 2
FPS = 60
DROP_INTERVAL = 500  # ms

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
LIGHT_GRAY = (80, 80, 80)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# 定义方块形状和颜色
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'Z': [[1, 1, 0], [0, 1, 1]]
}
SHAPE_COLORS = {
    'I': CYAN,
    'J': BLUE,
    'L': ORANGE,
    'O': YELLOW,
    'S': GREEN,
    'T': MAGENTA,
    'Z': RED
}
SHAPE_KEYS = list(SHAPES.keys())

# 计分规则
SCORE_TABLE = {1: 100, 2: 300, 3: 500, 4: 800}


def main():
    random.seed(42)
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris Medium")
    clock = pygame.time.Clock()
    
    # 创建基础字体
    font = pygame.font.SysFont(None, 30)
    big_font = pygame.font.SysFont(None, 60)
    small_font = pygame.font.SysFont(None, 24)
    
    # 游戏状态变量
    score = 0
    lines_cleared = 0
    game_over = False
    board = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    current_piece = None
    current_x = 0
    current_y = 0
    piece_rotation = 0
    last_drop_time = 0
    
    def create_new_piece():
        nonlocal current_piece, current_x, current_y, piece_rotation
        shape_key = random.choice(SHAPE_KEYS)
        current_piece = [row[:] for row in SHAPES[shape_key]]
        piece_rotation = 0
        current_x = GRID_WIDTH // 2 - len(current_piece[0]) // 2
        current_y = 0
        
        # 检查新方块是否立即碰撞
        if not is_valid_position(current_x, current_y, current_piece):
            return True  # 游戏结束
        
        return False  # 正常生成
    
    def is_valid_position(x, y, piece=None):
        piece = piece if piece is not None else current_piece
        for r in range(len(piece)):
            for c in range(len(piece[r])):
                if piece[r][c]:
                    board_x = x + c
                    board_y = y + r
                    if board_x < 0 or board_x >= GRID_WIDTH or board_y >= GRID_HEIGHT:
                        return False
                    if board_y >= 0 and board[board_y][board_x] is not None:
                        return False
        return True
    
    def rotate_piece():
        nonlocal current_piece, piece_rotation, current_x
        rotated = [list(row) for row in zip(*reversed(current_piece))]
        old_x = current_x
        
        # 简单墙踢：尝试右移最多2格
        for offset in range(-1, 2):
            new_x = old_x + offset
            if is_valid_position(new_x, current_y, rotated):
                current_x = new_x
                current_piece = rotated
                piece_rotation = (piece_rotation + 1) % 4
                return
        
        # 仍然无效则不旋转
    
    def lock_piece():
        nonlocal board
        for r in range(len(current_piece)):
            for c in range(len(current_piece[r])):
                if current_piece[r][c]:
                    board_y = current_y + r
                    board_x = current_x + c
                    if board_y >= 0:
                        board[board_y][board_x] = SHAPE_COLORS[current_piece]
        
        # 消除完整行
        lines = 0
        for r in range(GRID_HEIGHT):
            if all(board[r][c] is not None for c in range(GRID_WIDTH)):
                del board[r]
                board.insert(0, [None for _ in range(GRID_WIDTH)])
                lines += 1
        
        if lines > 0:
            nonlocal score, lines_cleared
            score += SCORE_TABLE[lines]
            lines_cleared += lines
    
    def hard_drop():
        nonlocal current_y
        while is_valid_position(current_x, current_y + 1):
            current_y += 1
    
    def draw_board():
        # 绘制背景
        screen.fill(BLACK)
        
        # 绘制棋盘区域
        pygame.draw.rect(screen, GRAY, (BOARD_X - 2, BOARD_Y - 2, GRID_WIDTH * BLOCK_SIZE + 4, GRID_HEIGHT * BLOCK_SIZE + 4))
        pygame.draw.rect(screen, BLACK, (BOARD_X, BOARD_Y, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE))
        
        # 绘制网格线
        for x in range(GRID_WIDTH + 1):
            start_x = BOARD_X + x * BLOCK_SIZE
            end_x = start_x
            start_y = BOARD_Y
            end_y = BOARD_Y + GRID_HEIGHT * BLOCK_SIZE
            pygame.draw.line(screen, LIGHT_GRAY, (start_x, start_y), (end_x, end_y), 1)
        
        for y in range(GRID_HEIGHT + 1):
            start_y = BOARD_Y + y * BLOCK_SIZE
            end_y = start_y
            start_x = BOARD_X
            end_x = BOARD_X + GRID_WIDTH * BLOCK_SIZE
            pygame.draw.line(screen, LIGHT_GRAY, (start_x, start_y), (end_x, end_y), 1)
        
        # 绘制已固定的方块
        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                if board[r][c] is not None:
                    color = board[r][c] if isinstance(board[r][c], tuple) else SHAPE_COLORS.get('O')
                    x = BOARD_X + c * BLOCK_SIZE
                    y = BOARD_Y + r * BLOCK_SIZE
                    pygame.draw.rect(screen, color, (x + 1, y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
        
        # 绘制当前方块
        if current_piece:
            for r in range(len(current_piece)):
                for c in range(len(current_piece[r])):
                    if current_piece[r][c]:
                        x = BOARD_X + (current_x + c) * BLOCK_SIZE
                        y = BOARD_Y + (current_y + r) * BLOCK_SIZE
                        color = SHAPE_COLORS.get([k for k, v in SHAPES.items() if v == current_piece][0], YELLOW)
                        pygame.draw.rect(screen, color, (x + 1, y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
        
        # HUD 区域
        hud_x = BOARD_X + GRID_WIDTH * BLOCK_SIZE + 10
        hud_y = BOARD_Y
        
        # 绘制 HUD 背景
        hud_width = 200
        hud_height = GRID_HEIGHT * BLOCK_SIZE
        pygame.draw.rect(screen, GRAY, (hud_x - 5, hud_y - 5, hud_width, hud_height + 10))
        pygame.draw.rect(screen, BLACK, (hud_x, hud_y, hud_width - 10, hud_height))
        
        # 绘制 hud 文本
        title_text = font.render("SCORE:", True, WHITE)
        screen.blit(title_text, (hud_x, hud_y + 20))
        score_text = big_font.render(str(score), True, WHITE)
        screen.blit(score_text, (hud_x + 10, hud_y + 50))
        
        lines_text = font.render("LINES:", True, WHITE)
        screen.blit(lines_text, (hud_x, hud_y + 140))
        lines_count_text = font.render(str(lines_cleared), True, WHITE)
        screen.blit(lines_count_text, (hud_x, hud_y + 170))
        
        # 绘制控件提示
        tips = [
            "CONTROLS:",
            "← → : Move",
            "↑   : Rotate",
            "↓   : Soft Drop",
            "SPA   : Hard Drop",
            "R     : Restart",
            "ESC   : Exit"
        ]
        for i, tip in enumerate(tips):
            color = WHITE if ":" in tip else LIGHT_GRAY
            text = small_font.render(tip, True, color)
            screen.blit(text, (hud_x, hud_y + 230 + i * 25))
    
    def draw_game_over():
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        over_text = big_font.render("GAME OVER", True, RED)
        rect = over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(over_text, rect)
        
        final_score_text = font.render(f"Final Score: {score}", True, WHITE)
        rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 60))
        screen.blit(final_score_text, rect)
        
        restart_text = font.render("Press R to Restart", True, WHITE)
        rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 100))
        screen.blit(restart_text, rect)
    
    # 初始化游戏
    game_over = create_new_piece()
    
    running = True
    while running:
        dt = clock.tick(FPS)
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    # 重新开始
                    board = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
                    score = 0
                    lines_cleared = 0
                    game_over = False
                    create_new_piece()
                elif not game_over:
                    if event.key == pygame.K_LEFT:
                        if is_valid_position(current_x - 1, current_y):
                            current_x -= 1
                    elif event.key == pygame.K_RIGHT:
                        if is_valid_position(current_x + 1, current_y):
                            current_x += 1
                    elif event.key == pygame.K_UP:
                        rotate_piece()
                    elif event.key == pygame.K_DOWN:
                        if is_valid_position(current_x, current_y + 1):
                            current_y += 1
                    elif event.key == pygame.K_SPACE:
                        hard_drop()
        
        # 自动下落
        current_time = pygame.time.get_ticks()
        if current_time - last_drop_time >= DROP_INTERVAL:
            last_drop_time = current_time
            if not game_over:
                if is_valid_position(current_x, current_y + 1):
                    current_y += 1
                else:
                    lock_piece()
                    game_over = create_new_piece()
        
        # 渲染
        draw_board()
        if game_over:
            draw_game_over()
        
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()