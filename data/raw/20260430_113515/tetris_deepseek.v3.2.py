import pygame
import random

pygame.init()

# ===== CONSTANTS =====
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_COLS = 10
GRID_ROWS = 20
CELL_SIZE = 24
GRID_WIDTH = GRID_COLS * CELL_SIZE
GRID_HEIGHT = GRID_ROWS * CELL_SIZE
GRID_X = (SCREEN_WIDTH // 2) - (GRID_WIDTH // 2) - 80
GRID_Y = (SCREEN_HEIGHT - GRID_HEIGHT) // 2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 150, 0)
COLORS = [CYAN, YELLOW, MAGENTA, GREEN, RED, BLUE, ORANGE]

# Shapes [I, O, T, S, Z, J, L]
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1],
     [1, 1]],
    [[0, 1, 0],
     [1, 1, 1]],
    [[0, 1, 1],
     [1, 1, 0]],
    [[1, 1, 0],
     [0, 1, 1]],
    [[1, 0, 0],
     [1, 1, 1]],
    [[0, 0, 1],
     [1, 1, 1]]
]

FALL_INTERVAL = 500  # ms
SCORES = {1: 100, 2: 300, 3: 500, 4: 800}
FPS = 60
random.seed(42)

# ===== GAME CLASSES =====
class Tetromino:
    def __init__(self, x, y, shape_idx):
        self.x = x
        self.y = y
        self.shape_idx = shape_idx
        self.color = COLORS[shape_idx]
        self.shape = SHAPES[shape_idx]
        self.rotation = 0

    def rotate(self):
        old_shape = self.shape
        self.shape = [list(row) for row in zip(*self.shape[::-1])]
        if self.collision(self.x, self.y):
            self.shape = old_shape

    def move(self, dx, dy, grid):
        if not self.collision(self.x + dx, self.y + dy, grid):
            self.x += dx
            self.y += dy
            return True
        return False

    def hard_drop(self, grid):
        while self.move(0, 1, grid):
            pass

    def collision(self, x, y, grid=None):
        for r, row in enumerate(self.shape):
            for c, cell in enumerate(row):
                if cell:
                    new_x = x + c
                    new_y = y + r
                    if (new_x < 0 or new_x >= GRID_COLS or 
                        new_y >= GRID_ROWS or 
                        (new_y >= 0 and grid[new_y][new_x])):
                        return True
        return False

    def draw(self, screen):
        for r, row in enumerate(self.shape):
            for c, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        GRID_X + (self.x + c) * CELL_SIZE,
                        GRID_Y + (self.y + r) * CELL_SIZE,
                        CELL_SIZE, CELL_SIZE
                    )
                    pygame.draw.rect(screen, self.color, rect)
                    pygame.draw.rect(screen, WHITE, rect, 1)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Medium")
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.fall_time = 0
        self.score = 0
        self.lines = 0
        self.game_over = False
        self.font = pygame.font.SysFont(None, 36)

    def new_piece(self):
        shape_idx = random.randint(0, len(SHAPES) - 1)
        return Tetromino(GRID_COLS // 2 - 1, 0, shape_idx)

    def lock_piece(self):
        for r, row in enumerate(self.current_piece.shape):
            for c, cell in enumerate(row):
                if cell:
                    y = self.current_piece.y + r
                    x = self.current_piece.x + c
                    if y >= 0:
                        self.grid[y][x] = self.current_piece.color

        lines_cleared = 0
        for r in range(GRID_ROWS):
            if all(self.grid[r]):
                lines_cleared += 1
                del self.grid[r]
                self.grid.insert(0, [0 for _ in range(GRID_COLS)])

        if lines_cleared:
            self.lines += lines_cleared
            self.score += SCORES.get(lines_cleared, 0)

        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()

        if self.current_piece.collision(self.current_piece.x, self.current_piece.y, self.grid):
            self.game_over = True

    def update(self, dt):
        if self.game_over:
            return

        self.fall_time += dt
        if self.fall_time >= FALL_INTERVAL:
            if not self.current_piece.move(0, 1, self.grid):
                self.lock_piece()
            self.fall_time = 0

    def draw_grid(self):
        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                rect = pygame.Rect(
                    GRID_X + x * CELL_SIZE,
                    GRID_Y + y * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                color = self.grid[y][x]
                if color:
                    pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, GRAY, rect, 1)

        for x in range(GRID_COLS + 1):
            pygame.draw.line(
                self.screen, GRAY,
                (GRID_X + x * CELL_SIZE, GRID_Y),
                (GRID_X + x * CELL_SIZE, GRID_Y + GRID_HEIGHT)
            )
        for y in range(GRID_ROWS + 1):
            pygame.draw.line(
                self.screen, GRAY,
                (GRID_X, GRID_Y + y * CELL_SIZE),
                (GRID_X + GRID_WIDTH, GRID_Y + y * CELL_SIZE)
            )

    def draw_hud(self):
        hud_x = GRID_X + GRID_WIDTH + 40
        hud_y = GRID_Y + 20

        title = self.font.render("TETRIS", True, WHITE)
        self.screen.blit(title, (hud_x, hud_y))

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (hud_x, hud_y + 60))

        lines_text = self.font.render(f"Lines: {self.lines}", True, WHITE)
        self.screen.blit(lines_text, (hud_x, hud_y + 110))

        next_text = self.font.render("Next:", True, WHITE)
        self.screen.blit(next_text, (hud_x, hud_y + 180))

        # Draw next piece preview
        for r, row in enumerate(self.next_piece.shape):
            for c, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        hud_x + c * CELL_SIZE,
                        hud_y + 220 + r * CELL_SIZE,
                        CELL_SIZE, CELL_SIZE
                    )
                    pygame.draw.rect(self.screen, self.next_piece.color, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)

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
            text = self.font.render(line, True, WHITE)
            self.screen.blit(text, (hud_x, hud_y + 320 + i * 40))

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            go = self.font.render("GAME OVER", True, RED)
            final = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart = self.font.render("Press R to Restart", True, GREEN)

            self.screen.blit(go, (SCREEN_WIDTH // 2 - go.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(final, (SCREEN_WIDTH // 2 - final.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()
        if not self.game_over:
            self.current_piece.draw(self.screen)
        self.draw_hud()
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif not self.game_over:
                        if event.key == pygame.K_LEFT:
                            self.current_piece.move(-1, 0, self.grid)
                        elif event.key == pygame.K_RIGHT:
                            self.current_piece.move(1, 0, self.grid)
                        elif event.key == pygame.K_DOWN:
                            self.current_piece.move(0, 1, self.grid)
                        elif event.key == pygame.K_UP:
                            self.current_piece.rotate()
                        elif event.key == pygame.K_SPACE:
                            self.current_piece.hard_drop(self.grid)

            self.update(dt)
            self.draw()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()