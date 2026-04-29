import pygame
import random

pygame.init()

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 24
BOARD_WIDTH = GRID_WIDTH * CELL_SIZE
BOARD_HEIGHT = GRID_HEIGHT * CELL_SIZE
BOARD_X = (SCREEN_WIDTH - BOARD_WIDTH) // 3
BOARD_Y = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2
FPS = 60
FALL_INTERVAL = 500  # 毫秒
SCORE_1 = 100
SCORE_2 = 300
SCORE_3 = 500
SCORE_4 = 800

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
DARK_GRAY = (40, 40, 40)

# 方块形状定义 (相对于旋转中心的坐标)
SHAPES = {
    'I': [[(0, -1), (0, 0), (0, 1), (0, 2)],
          [(-1, 0), (0, 0), (1, 0), (2, 0)]],
    'O': [[(0, 0), (1, 0), (0, 1), (1, 1)]],
    'T': [[(0, -1), (-1, 0), (0, 0), (1, 0)],
          [(0, -1), (0, 0), (1, 0), (0, 1)],
          [(-1, 0), (0, 0), (1, 0), (0, 1)],
          [(0, -1), (-1, 0), (0, 0), (0, 1)]],
    'S': [[(0, 0), (1, 0), (-1, 1), (0, 1)],
          [(0, -1), (0, 0), (1, 0), (1, 1)]],
    'Z': [[(-1, 0), (0, 0), (0, 1), (1, 1)],
          [(1, -1), (0, 0), (1, 0), (0, 1)]],
    'J': [[(-1, -1), (-1, 0), (0, 0), (1, 0)],
          [(0, -1), (1, -1), (0, 0), (0, 1)],
          [(-1, 0), (0, 0), (1, 0), (1, 1)],
          [(0, -1), (0, 0), (-1, 1), (0, 1)]],
    'L': [[(1, -1), (-1, 0), (0, 0), (1, 0)],
          [(0, -1), (0, 0), (0, 1), (1, 1)],
          [(-1, 0), (0, 0), (1, 0), (-1, 1)],
          [(-1, -1), (0, -1), (0, 0), (0, 1)]]
}
SHAPE_COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': MAGENTA,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE
}
SHAPE_LIST = list(SHAPES.keys())

# 随机种子
random.seed(42)

# 初始化pygame
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris Medium")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)
large_font = pygame.font.SysFont(None, 48)

class Tetromino:
    def __init__(self, shape, board):
        self.shape_name = shape
        self.color = SHAPE_COLORS[shape]
        self.rotations = SHAPES[shape]
        self.rotation_index = 0
        self.board = board
        self.x = GRID_WIDTH // 2 - 1
        self.y = 0 if shape != 'I' else -1

    def current_coords(self):
        return [(self.x + dx, self.y + dy) for dx, dy in self.rotations[self.rotation_index]]

    def rotate(self):
        original_index = self.rotation_index
        self.rotation_index = (self.rotation_index + 1) % len(self.rotations)
        if self.collides():
            self.rotation_index = original_index
            return False
        return True

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        if self.collides():
            self.x -= dx
            self.y -= dy
            return False
        return True

    def collides(self):
        for cx, cy in self.current_coords():
            if cx < 0 or cx >= GRID_WIDTH or cy >= GRID_HEIGHT:
                return True
            if cy >= 0 and self.board[cy][cx]:
                return True
        return False

    def hard_drop(self):
        while self.move(0, 1):
            pass

    def draw(self, surface):
        for cx, cy in self.current_coords():
            if cy >= 0:
                rect = pygame.Rect(
                    BOARD_X + cx * CELL_SIZE,
                    BOARD_Y + cy * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(surface, self.color, rect)
                pygame.draw.rect(surface, WHITE, rect, 1)

class Game:
    def __init__(self):
        self.board = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.fall_timer = 0
        self.spawn_new_piece()

    def spawn_new_piece(self):
        if self.next_piece is None:
            self.next_piece = Tetromino(random.choice(SHAPE_LIST), self.board)
        self.current_piece = self.next_piece
        self.next_piece = Tetromino(random.choice(SHAPE_LIST), self.board)
        if self.current_piece.collides():
            self.game_over = True
        self.fall_timer = pygame.time.get_ticks()

    def lock_piece(self):
        for cx, cy in self.current_piece.current_coords():
            if 0 <= cy < GRID_HEIGHT and 0 <= cx < GRID_WIDTH:
                self.board[cy][cx] = self.current_piece.color
        self.clear_lines()
        self.spawn_new_piece()

    def clear_lines(self):
        lines_to_clear = []
        for row in range(GRID_HEIGHT):
            if all(self.board[row]):
                lines_to_clear.append(row)
        if not lines_to_clear:
            return
        for row in lines_to_clear:
            for col in range(GRID_WIDTH):
                self.board[row][col] = None
        for row in lines_to_clear:
            for above_row in range(row - 1, -1, -1):
                for col in range(GRID_WIDTH):
                    self.board[above_row + 1][col] = self.board[above_row][col]
            for col in range(GRID_WIDTH):
                self.board[0][col] = None
        cleared = len(lines_to_clear)
        self.lines_cleared += cleared
        if cleared == 1:
            self.score += SCORE_1
        elif cleared == 2:
            self.score += SCORE_2
        elif cleared == 3:
            self.score += SCORE_3
        elif cleared == 4:
            self.score += SCORE_4

    def update(self, dt):
        if self.game_over:
            return
        if pygame.time.get_ticks() - self.fall_timer >= FALL_INTERVAL:
            if not self.current_piece.move(0, 1):
                self.lock_piece()
            self.fall_timer = pygame.time.get_ticks()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.__init__()
                return
            if event.key == pygame.K_ESCAPE:
                return 'quit'
            if self.game_over:
                return
            if event.key == pygame.K_LEFT:
                self.current_piece.move(-1, 0)
            elif event.key == pygame.K_RIGHT:
                self.current_piece.move(1, 0)
            elif event.key == pygame.K_UP:
                self.current_piece.rotate()
            elif event.key == pygame.K_DOWN:
                self.current_piece.move(0, 1)
                self.fall_timer = pygame.time.get_ticks()
            elif event.key == pygame.K_SPACE:
                self.current_piece.hard_drop()
                self.lock_piece()
        return None

    def draw(self, surface):
        surface.fill(BLACK)
        # 绘制网格背景
        grid_rect = pygame.Rect(BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT)
        pygame.draw.rect(surface, DARK_GRAY, grid_rect)
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(
                surface, GRAY,
                (BOARD_X + x * CELL_SIZE, BOARD_Y),
                (BOARD_X + x * CELL_SIZE, BOARD_Y + BOARD_HEIGHT)
            )
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(
                surface, GRAY,
                (BOARD_X, BOARD_Y + y * CELL_SIZE),
                (BOARD_X + BOARD_WIDTH, BOARD_Y + y * CELL_SIZE)
            )
        # 绘制已经固定的方块
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.board[y][x]:
                    rect = pygame.Rect(
                        BOARD_X + x * CELL_SIZE,
                        BOARD_Y + y * CELL_SIZE,
                        CELL_SIZE, CELL_SIZE
                    )
                    pygame.draw.rect(surface, self.board[y][x], rect)
                    pygame.draw.rect(surface, WHITE, rect, 1)
        # 绘制当前下落的方块
        if self.current_piece:
            self.current_piece.draw(surface)
        # 绘制HUD
        hud_x = BOARD_X + BOARD_WIDTH + 50
        # 分数
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        surface.blit(score_text, (hud_x, BOARD_Y))
        # 消除行数
        lines_text = font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        surface.blit(lines_text, (hud_x, BOARD_Y + 50))
        # 下一个方块预览
        next_text = font.render("Next:", True, WHITE)
        surface.blit(next_text, (hud_x, BOARD_Y + 120))
        if self.next_piece:
            for dx, dy in self.next_piece.rotations[0]:
                rect = pygame.Rect(
                    hud_x + (dx + 1) * CELL_SIZE,
                    BOARD_Y + 160 + (dy + 1) * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(surface, self.next_piece.color, rect)
                pygame.draw.rect(surface, WHITE, rect, 1)
        # 控制说明
        controls_y = BOARD_Y + 280
        controls = [
            "Controls:",
            "Left/Right: Move",
            "Up: Rotate",
            "Down: Soft Drop",
            "Space: Hard Drop",
            "R: Restart",
            "ESC: Quit"
        ]
        for i, text in enumerate(controls):
            ctrl_text = font.render(text, True, WHITE)
            surface.blit(ctrl_text, (hud_x, controls_y + i * 30))
        # 游戏结束提示
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            game_over_text = large_font.render("Game Over", True, RED)
            surface.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            final_score_text = font.render(f"Final Score: {self.score}", True, WHITE)
            surface.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))
            restart_text = font.render("Press R to Restart", True, GREEN)
            surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))

def main():
    game = Game()
    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            result = game.handle_input(event)
            if result == 'quit':
                running = False
        game.update(dt)
        game.draw(screen)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()