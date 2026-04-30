import pygame
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 24
GRID_ORIGIN_X = (SCREEN_WIDTH - GRID_WIDTH * CELL_SIZE) // 2 - 50
GRID_ORIGIN_Y = (SCREEN_HEIGHT - GRID_HEIGHT * CELL_SIZE) // 2
FPS = 60
MOVE_INTERVAL = 500  # ms
SCORE_1_LINE = 100
SCORE_2_LINE = 300
SCORE_3_LINE = 500
SCORE_4_LINE = 800

SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]]   # L
]
SHAPE_COLORS = [
    (0, 255, 255),    # I cyan
    (255, 255, 0),    # O yellow
    (128, 0, 128),    # T purple
    (0, 255, 0),      # S green
    (255, 0, 0),      # Z red
    (0, 0, 255),      # J blue
    (255, 165, 0)     # L orange
]

random.seed(42)

class Tetromino:
    def __init__(self, shape_idx, x=GRID_WIDTH // 2 - 1, y=0):
        self.shape_idx = shape_idx
        self.shape_matrix = SHAPES[shape_idx]
        self.color = SHAPE_COLORS[shape_idx]
        self.x = x
        self.y = y

    def rotate(self):
        h, w = len(self.shape_matrix), len(self.shape_matrix[0])
        rotated = [[0] * h for _ in range(w)]
        for r in range(h):
            for c in range(w):
                rotated[c][h - 1 - r] = self.shape_matrix[r][c]
        self.shape_matrix = rotated

    def get_positions(self):
        positions = []
        for r, row in enumerate(self.shape_matrix):
            for c, cell in enumerate(row):
                if cell:
                    positions.append((self.x + c, self.y + r))
        return positions

class TetrisGame:
    def __init__(self):
        self.grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.lines_cleared = 0
        self.fall_time = 0
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Medium")
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)

    def new_piece(self):
        shape_idx = random.randint(0, len(SHAPES) - 1)
        piece = Tetromino(shape_idx)
        if self.check_collision(piece.get_positions()):
            self.game_over = True
        return piece

    def check_collision(self, positions):
        for x, y in positions:
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT or (y >= 0 and self.grid[y][x]):
                return True
        return False

    def lock_piece(self):
        for x, y in self.current_piece.get_positions():
            if 0 <= y < GRID_HEIGHT:
                self.grid[y][x] = self.current_piece.color
        self.clear_lines()
        if not self.game_over:
            self.current_piece = self.new_piece()

    def move(self, dx, dy):
        self.current_piece.x += dx
        self.current_piece.y += dy
        if self.check_collision(self.current_piece.get_positions()):
            self.current_piece.x -= dx
            self.current_piece.y -= dy
            if dy > 0:
                self.lock_piece()
            return False
        return True

    def rotate_piece(self):
        old_shape = self.current_piece.shape_matrix
        self.current_piece.rotate()
        if self.check_collision(self.current_piece.get_positions()):
            self.current_piece.shape_matrix = old_shape

    def hard_drop(self):
        while self.move(0, 1):
            pass

    def clear_lines(self):
        full_lines = []
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                full_lines.append(y)
        for line in full_lines:
            del self.grid[line]
            self.grid.insert(0, [0] * GRID_WIDTH)
        if full_lines:
            count = len(full_lines)
            self.lines_cleared += count
            if count == 1:
                self.score += SCORE_1_LINE
            elif count == 2:
                self.score += SCORE_2_LINE
            elif count == 3:
                self.score += SCORE_3_LINE
            elif count == 4:
                self.score += SCORE_4_LINE

    def draw_grid(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    GRID_ORIGIN_X + x * CELL_SIZE,
                    GRID_ORIGIN_Y + y * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                color = self.grid[y][x]
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (50, 50, 50), rect, 1)

    def draw_current_piece(self):
        for x, y in self.current_piece.get_positions():
            if y >= 0:
                rect = pygame.Rect(
                    GRID_ORIGIN_X + x * CELL_SIZE,
                    GRID_ORIGIN_Y + y * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(self.screen, self.current_piece.color, rect)
                pygame.draw.rect(self.screen, (50, 50, 50), rect, 1)

    def draw_hud(self):
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, (255, 255, 255))
        controls = [
            "Controls:",
            "Left/Right: Move",
            "Up: Rotate",
            "Down: Soft Drop",
            "Space: Hard Drop",
            "R: Restart",
            "ESC: Quit"
        ]
        self.screen.blit(score_text, (GRID_ORIGIN_X + GRID_WIDTH * CELL_SIZE + 30, 50))
        self.screen.blit(lines_text, (GRID_ORIGIN_X + GRID_WIDTH * CELL_SIZE + 30, 100))
        for i, line in enumerate(controls):
            text = self.small_font.render(line, True, (200, 200, 200))
            self.screen.blit(text, (GRID_ORIGIN_X + GRID_WIDTH * CELL_SIZE + 30, 150 + i * 30))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        go_text = self.font.render("GAME OVER", True, (255, 50, 50))
        score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        restart_text = self.font.render("Press R to Restart", True, (255, 255, 255))
        self.screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

    def reset(self):
        self.grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.lines_cleared = 0
        self.fall_time = 0

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            self.screen.fill((30, 30, 30))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.reset()
                    else:
                        if event.key == pygame.K_LEFT:
                            self.move(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move(1, 0)
                        elif event.key == pygame.K_UP:
                            self.rotate_piece()
                        elif event.key == pygame.K_DOWN:
                            self.move(0, 1)
                        elif event.key == pygame.K_SPACE:
                            self.hard_drop()
                        elif event.key == pygame.K_r:
                            self.reset()
                    if event.key == pygame.K_ESCAPE:
                        running = False

            if not self.game_over:
                self.fall_time += dt
                if self.fall_time >= MOVE_INTERVAL:
                    self.move(0, 1)
                    self.fall_time = 0

            self.draw_grid()
            self.draw_current_piece()
            self.draw_hud()
            if self.game_over:
                self.draw_game_over()

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()