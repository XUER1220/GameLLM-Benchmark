import pygame
import random

# 常量定义
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BLOCK_SIZE = 24
GRID_COLS = 10
GRID_ROWS = 20
GAME_WIDTH = GRID_COLS * BLOCK_SIZE
GAME_HEIGHT = GRID_ROWS * BLOCK_SIZE
FPS = 60
AUTO_DROP_INTERVAL = 500  # ms

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (192, 192, 192)
DARK_GRAY = (64, 64, 64)

# 方块形状及颜色定义（7种）
SHAPES = {
    'I': (0, 0, 0, 0,
          1, 1, 1, 1,
          0, 0, 0, 0,
          0, 0, 0, 0),
    'O': (1, 1,
          1, 1),
    'T': (0, 1, 0,
          1, 1, 1,
          0, 0, 0),
    'S': (0, 1, 1,
          1, 1, 0,
          0, 0, 0),
    'Z': (1, 1, 0,
          0, 1, 1,
          0, 0, 0),
    'J': (1, 0, 0,
          1, 1, 1,
          0, 0, 0),
    'L': (0, 0, 1,
          1, 1, 1,
          0, 0, 0)
}

SHAPE_COLORS = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (128, 0, 128),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
    'J': (0, 0, 255),
    'L': (255, 165, 0)
}


class Tetromino:
    def __init__(self, shape_type):
        self.shape_type = shape_type
        self.shape = SHAPES[shape_type]
        self.color = SHAPE_COLORS[shape_type]
        self.width = self._get_width(shape_type)
        self.height = self._get_height(shape_type)
        self.x = GRID_COLS // 2 - self.width // 2
        self.y = 0

    def _get_width(self, shape_type):
        if shape_type == 'I':
            return 4
        elif shape_type == 'O':
            return 2
        else:
            return 3

    def _get_height(self, shape_type):
        if shape_type == 'I' or shape_type == 'O':
            return 4 if shape_type == 'I' else 2
        else:
            return 3

    def rotate(self):
        # 旋转矩阵 (顺时针)
        new_shape = [0] * len(self.shape)
        for r in range(self.width):
            for c in range(self.height):
                new_shape[r * self.height + (self.height - 1 - c)] = self.shape[c * self.width + r]
        self.shape = new_shape
        self.width, self.height = self.height, self.width

    def get_cells(self):
        cells = []
        for r in range(self.height):
            for c in range(self.width):
                if self.shape[r * self.width + c]:
                    cells.append((self.x + c, self.y + r))
        return cells


def create_board():
    return [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]


def valid_position(board, piece):
    for cx, cy in piece.get_cells():
        if cx < 0 or cx >= GRID_COLS or cy >= GRID_ROWS:
            return False
        if cy >= 0 and board[cy][cx]:
            return False
    return True


def lock_piece(board, piece):
    for cx, cy in piece.get_cells():
        if 0 <= cx < GRID_COLS and 0 <= cy < GRID_ROWS:
            board[cy][cx] = piece.color


def clear_lines(board):
    lines_cleared = 0
    y = GRID_ROWS - 1
    while y >= 0:
        if all(board[y][x] != 0 for x in range(GRID_COLS)):
            del board[y]
            board.insert(0, [0] * GRID_COLS)
            lines_cleared += 1
        else:
            y -= 1
    return lines_cleared


def get_score(lines):
    if lines == 1:
        return 100
    elif lines == 2:
        return 300
    elif lines == 3:
        return 500
    elif lines == 4:
        return 800
    else:
        return 0


def get_next_piece(all_pieces):
    return random.choice(all_pieces)


def draw_block(surface, x, y, color, size=BLOCK_SIZE):
    if color != 0:
        pygame.draw.rect(surface, color, (x, y, size, size))
        pygame.draw.rect(surface, LIGHT_GRAY, (x, y, size, size), 1)


def draw_board(surface, board):
    for y in range(GRID_ROWS):
        for x in range(GRID_COLS):
            draw_block(surface, x * BLOCK_SIZE, y * BLOCK_SIZE, board[y][x])


def draw_grid(surface, color=GRAY):
    for x in range(GRID_COLS + 1):
        pygame.draw.line(surface, color,
                         (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, GAME_HEIGHT))
    for y in range(GRID_ROWS + 1):
        pygame.draw.line(surface, color,
                         (0, y * BLOCK_SIZE), (GAME_WIDTH, y * BLOCK_SIZE))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tetris Medium")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 48)

    # 常量
    GAME_X = (WINDOW_WIDTH - GAME_WIDTH) // 2
    GAME_Y = (WINDOW_HEIGHT - GAME_HEIGHT) // 2

    # 初始化游戏状态
    random.seed(42)
    all_pieces = list(SHAPES.keys())

    def new_game():
        board = create_board()
        current_piece = Tetromino(get_next_piece(all_pieces))
        next_piece_type = get_next_piece(all_pieces)
        next_piece = Tetromino(next_piece_type)
        
        score = 0
        lines_cleared_total = 0
        drop_time = 0
        last_drop = 0
        game_over = False
        return board, current_piece, next_piece, next_piece_type, score, lines_cleared_total, drop_time, last_drop, game_over

    board, current_piece, next_piece, next_piece_type, score, lines_cleared_total, drop_time, last_drop, game_over = new_game()

    # 键盘重复延迟参数
    pygame.key.set_repeat(100, 100)

    # 游戏主循环
    running = True
    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    board, current_piece, next_piece, next_piece_type, score, lines_cleared_total, drop_time, last_drop, game_over = new_game()
                elif not game_over:
                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not valid_position(board, current_piece):
                            current_piece.x += 1
                    elif event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not valid_position(board, current_piece):
                            current_piece.x -= 1
                    elif event.key == pygame.K_UP:
                        current_piece.rotate()
                        if not valid_position(board, current_piece):
                            current_piece.rotate()  # 旋转回来
                    elif event.key == pygame.K_DOWN:
                        current_piece.y += 1
                        if not valid_position(board, current_piece):
                            current_piece.y -= 1
                    elif event.key == pygame.K_SPACE:  # 硬降
                        while valid_position(board, current_piece):
                            current_piece.y += 1
                        current_piece.y -= 1  # 回退到有效位置
                        lock_piece(board, current_piece)
                        cleared = clear_lines(board)
                        lines_cleared_total += cleared
                        score += get_score(cleared)
                        current_piece = next_piece
                        next_piece = Tetromino(next_piece_type)
                        next_piece_type = get_next_piece(all_pieces)
                        if not valid_position(board, current_piece):
                            game_over = True

        # 自动下落计时
        if not game_over:
            if current_time - last_drop > AUTO_DROP_INTERVAL:
                last_drop = current_time
                current_piece.y += 1
                if not valid_position(board, current_piece):
                    current_piece.y -= 1
                    lock_piece(board, current_piece)
                    cleared = clear_lines(board)
                    lines_cleared_total += cleared
                    score += get_score(cleared)
                    current_piece = next_piece
                    next_piece = Tetromino(next_piece_type)
                    next_piece_type = get_next_piece(all_pieces)
                    if not valid_position(board, current_piece):
                        game_over = True

        # 绘制
        screen.fill(BLACK)

        # 绘制游戏区域背景
        pygame.draw.rect(screen, DARK_GRAY, (GAME_X, GAME_Y, GAME_WIDTH, GAME_HEIGHT))
        pygame.draw.rect(screen, WHITE, (GAME_X, GAME_Y, GAME_WIDTH, GAME_HEIGHT), 2)
        draw_grid(screen, color=DARK_GRAY)
        draw_board(screen, board)

        # 绘制当前棋子
        for cx, cy in current_piece.get_cells():
            if 0 <= cy < GRID_ROWS:
                draw_block(screen, GAME_X + cx * BLOCK_SIZE, GAME_Y + cy * BLOCK_SIZE, current_piece.color)

        # HUD 区域
        hud_x = GAME_X + GAME_WIDTH + 30
        texts = [
            f"Score: {score}",
            f"Lines: {lines_cleared_total}",
        ]
        y_offset = GAME_Y + 30
        for text in texts:
            img = font.render(text, True, WHITE)
            screen.blit(img, (hud_x, y_offset))
            y_offset += 35

        # 下一个方块预览
        pygame.draw.rect(screen, BLACK, (hud_x, y_offset - 10, 80, 80))
        y_offset += 5
        preview_piece = Tetromino(next_piece_type)
        preview_x = hud_x + 10
        preview_y = y_offset
        preview_w = preview_piece.width
        preview_h = preview_piece.height
        scale_x = 16
        scale_y = 16

        # 居中预览
        start_x = preview_x + (80 - preview_w * scale_x) // 2
        start_y = preview_y + (80 - preview_h * scale_y) // 2
        for r in range(preview_h):
            for c in range(preview_w):
                if preview_piece.shape[r * preview_w + c]:
                    pygame.draw.rect(screen, preview_piece.color, 
                                     (start_x + c * scale_x, start_y + r * scale_y, scale_x, scale_y))
                    pygame.draw.rect(screen, LIGHT_GRAY,
                                     (start_x + c * scale_x, start_y + r * scale_y, scale_x, scale_y), 1)

        y_offset += 85
        screen.blit(font.render("Next:", True, WHITE), (hud_x, y_offset))
        y_offset += 30

        # 游戏结束信息
        if game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))

            game_over_text = big_font.render("Game Over", True, WHITE)
            score_text = font.render(f"Final Score: {score}", True, WHITE)
            restart_text = font.render("Press 'R' to Restart", True, WHITE)

            screen.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, 250))
            screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 320))
            screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, 360))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()