import pygame
import random

pygame.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 24
BOARD_WIDTH = GRID_WIDTH * CELL_SIZE
BOARD_HEIGHT = GRID_HEIGHT * CELL_SIZE
BOARD_X = (SCREEN_WIDTH - BOARD_WIDTH) // 4
BOARD_Y = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2
FALL_SPEED = 500  # 毫秒

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (255, 50, 50)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 255)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
ORANGE = (255, 160, 0)

# 方块定义
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]]   # L
]
SHAPE_COLORS = [CYAN, YELLOW, PURPLE, GREEN, RED, BLUE, ORANGE]
random.seed(42)

def rotate_shape(shape):
    return [list(row) for row in zip(*reversed(shape))]

class Tetromino:
    def __init__(self):
        self.shape_idx = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_idx]
        self.color = SHAPE_COLORS[self.shape_idx]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self, board):
        rotated = rotate_shape(self.shape)
        for i in range(len(rotated)):
            for j in range(len(rotated[0])):
                if rotated[i][j]:
                    new_x = self.x + j
                    new_y = self.y + i
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT or board[new_y][new_x]:
                        return
        self.shape = rotated

    def move(self, dx, dy, board):
        for i in range(len(self.shape)):
            for j in range(len(self.shape[0])):
                if self.shape[i][j]:
                    new_x = self.x + j + dx
                    new_y = self.y + i + dy
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT or board[new_y][new_x]:
                        return False
        self.x += dx
        self.y += dy
        return True

    def hard_drop(self, board):
        while self.move(0, 1, board):
            pass

    def draw(self, surface):
        for i in range(len(self.shape)):
            for j in range(len(self.shape[0])):
                if self.shape[i][j]:
                    rect = pygame.Rect(
                        BOARD_X + (self.x + j) * CELL_SIZE,
                        BOARD_Y + (self.y + i) * CELL_SIZE,
                        CELL_SIZE, CELL_SIZE
                    )
                    pygame.draw.rect(surface, self.color, rect)
                    pygame.draw.rect(surface, WHITE, rect, 1)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Medium")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)
        self.reset()

    def reset(self):
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = Tetromino()
        self.game_over = False
        self.score = 0
        self.lines_cleared = 0
        self.fall_time = 0

    def lock_piece(self):
        for i in range(len(self.current_piece.shape)):
            for j in range(len(self.current_piece.shape[0])):
                if self.current_piece.shape[i][j]:
                    if self.current_piece.y + i < 0:
                        self.game_over = True
                        return
                    self.board[self.current_piece.y + i][self.current_piece.x + j] = self.current_piece.color
        self.clear_lines()
        self.current_piece = Tetromino()
        if not self.current_piece.move(0, 0, self.board):
            self.game_over = True

    def clear_lines(self):
        lines_to_clear = []
        for i in range(GRID_HEIGHT):
            if all(self.board[i]):
                lines_to_clear.append(i)
        for line in lines_to_clear:
            del self.board[line]
            self.board.insert(0, [0 for _ in range(GRID_WIDTH)])
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            if len(lines_to_clear) == 1:
                self.score += 100
            elif len(lines_to_clear) == 2:
                self.score += 300
            elif len(lines_to_clear) == 3:
                self.score += 500
            elif len(lines_to_clear) == 4:
                self.score += 800

    def draw_board(self):
        board_surface = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT))
        board_surface.fill(BLACK)
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                if self.board[i][j]:
                    rect = pygame.Rect(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(board_surface, self.board[i][j], rect)
                    pygame.draw.rect(board_surface, WHITE, rect, 1)
        for i in range(GRID_HEIGHT + 1):
            pygame.draw.line(board_surface, GRAY, (0, i * CELL_SIZE), (BOARD_WIDTH, i * CELL_SIZE))
        for j in range(GRID_WIDTH + 1):
            pygame.draw.line(board_surface, GRAY, (j * CELL_SIZE, 0), (j * CELL_SIZE, BOARD_HEIGHT))
        self.screen.blit(board_surface, (BOARD_X, BOARD_Y))

    def draw_hud(self):
        title = self.font.render("TETRIS MEDIUM", True, CYAN)
        self.screen.blit(title, (BOARD_X + BOARD_WIDTH + 50, BOARD_Y))
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (BOARD_X + BOARD_WIDTH + 50, BOARD_Y + 60))
        lines_text = self.small_font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (BOARD_X + BOARD_WIDTH + 50, BOARD_Y + 100))
        controls = [
            "Controls:",
            "Left/Right: Move",
            "Up: Rotate",
            "Down: Soft Drop",
            "Space: Hard Drop",
            "R: Restart",
            "ESC: Quit"
        ]
        for idx, line in enumerate(controls):
            text = self.small_font.render(line, True, WHITE)
            self.screen.blit(text, (BOARD_X + BOARD_WIDTH + 50, BOARD_Y + 180 + idx * 30))
        if self.game_over:
            overlay = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (BOARD_X, BOARD_Y))
            game_over_text = self.font.render("GAME OVER", True, RED)
            final_score = self.small_font.render(f"Final Score: {self.score}", True, WHITE)
            restart = self.small_font.render("Press R to Restart", True, WHITE)
            self.screen.blit(game_over_text, (BOARD_X + BOARD_WIDTH // 2 - game_over_text.get_width() // 2, BOARD_Y + BOARD_HEIGHT // 2 - 50))
            self.screen.blit(final_score, (BOARD_X + BOARD_WIDTH // 2 - final_score.get_width() // 2, BOARD_Y + BOARD_HEIGHT // 2))
            self.screen.blit(restart, (BOARD_X + BOARD_WIDTH // 2 - restart.get_width() // 2, BOARD_Y + BOARD_HEIGHT // 2 + 40))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            self.fall_time += dt

            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_r:
                        self.reset()
                    if not self.game_over:
                        if event.key == pygame.K_LEFT:
                            self.current_piece.move(-1, 0, self.board)
                        elif event.key == pygame.K_RIGHT:
                            self.current_piece.move(1, 0, self.board)
                        elif event.key == pygame.K_UP:
                            self.current_piece.rotate(self.board)
                        elif event.key == pygame.K_DOWN:
                            self.current_piece.move(0, 1, self.board)
                        elif event.key == pygame.K_SPACE:
                            self.current_piece.hard_drop(self.board)
                            self.lock_piece()

            # 自动下落
            if not self.game_over and self.fall_time >= FALL_SPEED:
                if not self.current_piece.move(0, 1, self.board):
                    self.lock_piece()
                self.fall_time = 0

            # 绘制
            self.screen.fill(BLACK)
            self.draw_board()
            if not self.game_over:
                self.current_piece.draw(self.screen)
            self.draw_hud()
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()