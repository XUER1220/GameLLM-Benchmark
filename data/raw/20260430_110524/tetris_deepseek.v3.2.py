import pygame
import random
import sys

pygame.init()

# 常量定义
FPS = 60
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 24
AUTO_DROP_TIME = 500  # 毫秒

# 颜色定义 (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# 方块形状定义 (旋转状态)
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]]   # L
]
SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, GREEN, RED, BLUE, ORANGE]

# 随机种子
random.seed(42)

# 计算主棋盘位置 (左侧)
BOARD_PIXEL_WIDTH = GRID_WIDTH * CELL_SIZE
BOARD_PIXEL_HEIGHT = GRID_HEIGHT * CELL_SIZE
BOARD_X = (SCREEN_WIDTH - BOARD_PIXEL_WIDTH) // 4
BOARD_Y = (SCREEN_HEIGHT - BOARD_PIXEL_HEIGHT) // 2

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Medium")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)
        self.reset_game()

    def reset_game(self):
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.lines_cleared = 0
        self.drop_time_accumulator = 0
        self.last_drop_time = pygame.time.get_ticks()

    def new_piece(self):
        shape_idx = random.randint(0, len(SHAPES) - 1)
        shape = SHAPES[shape_idx]
        color = SHAPE_COLORS[shape_idx]
        piece = {
            'shape': shape,
            'color': color,
            'x': GRID_WIDTH // 2 - len(shape[0]) // 2,
            'y': 0
        }
        return piece

    def draw_grid(self):
        # 绘制棋盘背景
        pygame.draw.rect(self.screen, BLACK, (BOARD_X, BOARD_Y, BOARD_PIXEL_WIDTH, BOARD_PIXEL_HEIGHT))
        # 绘制网格线
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, GRAY,
                             (BOARD_X + x * CELL_SIZE, BOARD_Y),
                             (BOARD_X + x * CELL_SIZE, BOARD_Y + BOARD_PIXEL_HEIGHT), 1)
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, GRAY,
                             (BOARD_X, BOARD_Y + y * CELL_SIZE),
                             (BOARD_X + BOARD_PIXEL_WIDTH, BOARD_Y + y * CELL_SIZE), 1)

    def draw_board(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.board[y][x]:
                    color_idx = self.board[y][x] - 1
                    color = SHAPE_COLORS[color_idx]
                    rect = pygame.Rect(BOARD_X + x * CELL_SIZE + 1, BOARD_Y + y * CELL_SIZE + 1,
                                      CELL_SIZE - 2, CELL_SIZE - 2)
                    pygame.draw.rect(self.screen, color, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)

    def draw_current_piece(self):
        shape = self.current_piece['shape']
        color = self.current_piece['color']
        x0 = self.current_piece['x']
        y0 = self.current_piece['y']
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(BOARD_X + (x0 + x) * CELL_SIZE + 1,
                                       BOARD_Y + (y0 + y) * CELL_SIZE + 1,
                                       CELL_SIZE - 2, CELL_SIZE - 2)
                    pygame.draw.rect(self.screen, color, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)

    def draw_hud(self):
        hud_x = BOARD_X + BOARD_PIXEL_WIDTH + 50
        hud_y = BOARD_Y
        # 标题
        title = self.font.render("TETRIS", True, WHITE)
        self.screen.blit(title, (hud_x, hud_y))
        # 分数
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (hud_x, hud_y + 50))
        # 消除行数
        lines_text = self.small_font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (hud_x, hud_y + 90))
        # 操作说明
        controls = [
            "Controls:",
            "Left/Right: Move",
            "Up: Rotate",
            "Down: Soft Drop",
            "Space: Hard Drop",
            "R: Restart",
            "ESC: Quit"
        ]
        for i, line in enumerate(controls):
            control_text = self.small_font.render(line, True, WHITE)
            self.screen.blit(control_text, (hud_x, hud_y + 150 + i * 30))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        go_text = self.font.render("GAME OVER", True, RED)
        score_text = self.small_font.render(f"Final Score: {self.score}", True, WHITE)
        restart_text = self.small_font.render("Press R to Restart", True, GREEN)
        self.screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))

    def valid_move(self, piece, x_offset=0, y_offset=0, rotated_shape=None):
        shape = rotated_shape if rotated_shape is not None else piece['shape']
        x = piece['x'] + x_offset
        y = piece['y'] + y_offset
        for y_idx, row in enumerate(shape):
            for x_idx, cell in enumerate(row):
                if cell:
                    new_x = x + x_idx
                    new_y = y + y_idx
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return False
                    if new_y >= 0 and self.board[new_y][new_x]:
                        return False
        return True

    def rotate_piece(self):
        shape = self.current_piece['shape']
        # 转置矩阵并反转每一行以实现90度旋转
        rotated = [list(row) for row in zip(*shape[::-1])]
        if self.valid_move(self.current_piece, rotated_shape=rotated):
            self.current_piece['shape'] = rotated
            return True
        return False

    def lock_piece(self):
        shape = self.current_piece['shape']
        color_idx = SHAPE_COLORS.index(self.current_piece['color'])
        x0 = self.current_piece['x']
        y0 = self.current_piece['y']
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    board_y = y0 + y
                    board_x = x0 + x
                    if board_y >= 0:
                        self.board[board_y][board_x] = color_idx + 1
        self.clear_lines()
        self.current_piece = self.new_piece()
        if not self.valid_move(self.current_piece):
            self.game_over = True

    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.board[y]):
                lines_to_clear.append(y)
        if not lines_to_clear:
            return
        # 消除行
        for y in lines_to_clear:
            del self.board[y]
            self.board.insert(0, [0 for _ in range(GRID_WIDTH)])
        # 计分
        cleared = len(lines_to_clear)
        if cleared == 1:
            self.score += 100
        elif cleared == 2:
            self.score += 300
        elif cleared == 3:
            self.score += 500
        elif cleared >= 4:
            self.score += 800
        self.lines_cleared += cleared

    def hard_drop(self):
        while self.valid_move(self.current_piece, y_offset=1):
            self.current_piece['y'] += 1
        self.lock_piece()

    def update(self, dt):
        if self.game_over:
            return
        self.drop_time_accumulator += dt
        if self.drop_time_accumulator >= AUTO_DROP_TIME:
            if self.valid_move(self.current_piece, y_offset=1):
                self.current_piece['y'] += 1
            else:
                self.lock_piece()
            self.drop_time_accumulator = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    self.reset_game()
                if not self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.hard_drop()
                    if event.key == pygame.K_UP:
                        self.rotate_piece()
        if not self.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and self.valid_move(self.current_piece, x_offset=-1):
                self.current_piece['x'] -= 1
            if keys[pygame.K_RIGHT] and self.valid_move(self.current_piece, x_offset=1):
                self.current_piece['x'] += 1
            if keys[pygame.K_DOWN] and self.valid_move(self.current_piece, y_offset=1):
                self.current_piece['y'] += 1
                self.drop_time_accumulator = 0  # 手动下落重置自动计时器

    def run(self):
        while True:
            current_time = pygame.time.get_ticks()
            dt = current_time - self.last_drop_time
            self.last_drop_time = current_time
            self.handle_events()
            self.update(dt)
            self.screen.fill((50, 50, 50))
            self.draw_grid()
            self.draw_board()
            self.draw_current_piece()
            self.draw_hud()
            if self.game_over:
                self.draw_game_over()
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = TetrisGame()
    game.run()