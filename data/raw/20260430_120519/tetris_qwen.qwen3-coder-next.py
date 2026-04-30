import pygame
import random

# Fixed initialization
pygame.init()
random.seed(42)

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BLOCK_SIZE = 24
GRID_COLS = 10
GRID_ROWS = 20
GAME_WIDTH = GRID_COLS * BLOCK_SIZE
GAME_HEIGHT = GRID_ROWS * BLOCK_SIZE
FPS = 60
AUTO_DROP_INTERVAL = 500  # ms

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GREEN = (0, 128, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PINK = (255, 105, 180)

# Tetromino shapes: list of [rotation states] with shape coordinates
SHAPES = {
    'I': [
        [[0, 0], [1, 0], [2, 0], [3, 0]],
        [[2, -1], [2, 0], [2, 1], [2, 2]],
        [[0, 1], [1, 1], [2, 1], [3, 1]],
        [[1, -1], [1, 0], [1, 1], [1, 2]],
    ],
    'O': [
        [[1, 0], [2, 0], [1, 1], [2, 1]],
        [[1, 0], [2, 0], [1, 1], [2, 1]],
        [[1, 0], [2, 0], [1, 1], [2, 1]],
        [[1, 0], [2, 0], [1, 1], [2, 1]],
    ],
    'T': [
        [[1, 0], [0, 1], [1, 1], [2, 1]],
        [[1, 0], [1, 1], [2, 1], [1, 2]],
        [[0, 1], [1, 1], [2, 1], [1, 2]],
        [[1, 0], [0, 1], [1, 1], [1, 2]],
    ],
    'S': [
        [[1, 0], [2, 0], [0, 1], [1, 1]],
        [[1, 0], [1, 1], [2, 1], [2, 2]],
        [[1, 1], [2, 1], [0, 2], [1, 2]],
        [[0, 0], [0, 1], [1, 1], [1, 2]],
    ],
    'Z': [
        [[0, 0], [1, 0], [1, 1], [2, 1]],
        [[2, 0], [1, 1], [2, 1], [1, 2]],
        [[0, 1], [1, 1], [1, 2], [2, 2]],
        [[1, 0], [0, 1], [1, 1], [0, 2]],
    ],
    'J': [
        [[0, 0], [0, 1], [1, 1], [2, 1]],
        [[1, 0], [2, 0], [1, 1], [1, 2]],
        [[0, 1], [1, 1], [2, 1], [2, 2]],
        [[1, 0], [1, 1], [0, 2], [1, 2]],
    ],
    'L': [
        [[2, 0], [0, 1], [1, 1], [2, 1]],
        [[1, 0], [1, 1], [1, 2], [2, 2]],
        [[0, 1], [1, 1], [2, 1], [0, 2]],
        [[0, 0], [1, 0], [1, 1], [1, 2]],
    ],
}

# Colors for each shape
SHAPE_COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': PURPLE,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE,
}

# Center offset for game board
GAME_OFFSET_X = (WINDOW_WIDTH - GAME_WIDTH) // 2 - 50
GAME_OFFSET_Y = (WINDOW_HEIGHT - GAME_HEIGHT) // 2

# Initialize screen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tetris Medium")
clock = pygame.time.Clock()


class Tetromino:
    def __init__(self, shape_type):
        self.type = shape_type
        self.shape = SHAPES[shape_type][0]
        self.color = SHAPE_COLORS[shape_type]
        self.x = GRID_COLS // 2 - 2
        self.y = 0
        self.rotation = 0

    def rotate(self):
        self.rotation = (self.rotation + 1) % 4
        self.shape = SHAPES[self.type][self.rotation]

    def get_positions(self):
        return [(self.x + pos[0], self.y + pos[1]) for pos in self.shape]


def create_board():
    return [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]


def check_collision(board, piece, x_offset=0, y_offset=0):
    positions = piece.get_positions()
    for x, y in positions:
        new_x = x + x_offset
        new_y = y + y_offset
        if new_x < 0 or new_x >= GRID_COLS or new_y >= GRID_ROWS:
            return True
        if new_y >= 0 and board[new_y][new_x] is not None:
            return True
    return False


def lock_piece(board, piece):
    positions = piece.get_positions()
    for i, (x, y) in enumerate(positions):
        if y >= 0:
            board[y][x] = piece.color
        else:
            return False  # Overlap at spawn -> game over
    return True


def clear_lines(board):
    lines_cleared = 0
    y = GRID_ROWS - 1
    while y >= 0:
        if all(board[y][x] is not None for x in range(GRID_COLS)):
            del board[y]
            board.insert(0, [None for _ in range(GRID_COLS)])
            lines_cleared += 1
        else:
            y -= 1
    return lines_cleared


def calculate_score(lines_cleared):
    scores = {1: 100, 2: 300, 3: 500, 4: 800}
    return scores.get(lines_cleared, 0)


def draw_grid(surface, offset_x, offset_y):
    for x in range(GRID_COLS + 1):
        pygame.draw.line(
            surface, GRAY,
            (offset_x + x * BLOCK_SIZE, offset_y),
            (offset_x + x * BLOCK_SIZE, offset_y + GAME_HEIGHT)
        )
    for y in range(GRID_ROWS + 1):
        pygame.draw.line(
            surface, GRAY,
            (offset_x, offset_y + y * BLOCK_SIZE),
            (offset_x + GAME_WIDTH, offset_y + y * BLOCK_SIZE)
        )


def draw_block(surface, x, y, color, offset_x, offset_y):
    rect = (offset_x + x * BLOCK_SIZE, offset_y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, BLACK, rect, 1)


def draw_text(surface, text, size, x, y, color=WHITE, center=True):
    font = pygame.font.SysFont('Arial', size, bold=True)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)


def draw_hud(surface, score, lines, offset_x, offset_y):
    # Draw HUD position beside the game board
    hud_x = offset_x + GAME_WIDTH + 50
    hud_y = offset_y
    draw_text(surface, "TETRIS", 32, hud_x, hud_y, WHITE)
    draw_text(surface, f"Score: {score}", 24, hud_x, hud_y + 80, WHITE)
    draw_text(surface, f"Lines: {lines}", 24, hud_x, hud_y + 130, WHITE)
    draw_text(surface, "Controls:", 20, hud_x, hud_y + 190, WHITE, center=False)
    draw_text(surface, "← →  Move", 16, hud_x, hud_y + 220, WHITE, center=False)
    draw_text(surface, "↑    Rotate", 16, hud_x, hud_y + 245, WHITE, center=False)
    draw_text(surface, "↓    Soft Drop", 16, hud_x, hud_y + 270, WHITE, center=False)
    draw_text(surface, "Space Hard Drop", 16, hud_x, hud_y + 295, WHITE, center=False)


def draw_game_over(surface, score, offset_x, offset_y):
    # Dark overlay
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    overlay.set_alpha(150)
    overlay.fill(BLACK)
    surface.blit(overlay, (offset_x, offset_y))

    # Game over text in center of game area
    center_x = offset_x + GAME_WIDTH // 2
    center_y = offset_y + GAME_HEIGHT // 2
    draw_text(surface, "GAME OVER", 60, center_x, center_y - 60, RED)
    draw_text(surface, f"Final Score: {score}", 30, center_x, center_y - 10, WHITE)
    draw_text(surface, "Press R to Restart", 24, center_x, center_y + 80, WHITE)
    draw_text(surface, "or ESC to Exit", 18, center_x, center_y + 120, WHITE)


def draw_piece(surface, piece, board, offset_x, offset_y):
    positions = piece.get_positions()
    for i, (x, y) in enumerate(positions):
        if y >= 0:
            draw_block(surface, x, y, piece.color, offset_x, offset_y)


def get_random_piece():
    types = list(SHAPES.keys())
    return Tetromino(random.choice(types))


def main():
    board = create_board()
    current_piece = get_random_piece()
    next_piece = get_random_piece()
    score = 0
    lines_cleared_total = 0
    drop_counter = 0
    last_drop_time = pygame.time.get_ticks()
    game_over = False

    while True:
        dt = clock.tick(FPS)
        current_time = pygame.time.get_ticks()

        # Input handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                if game_over and event.key == pygame.K_r:
                    # Reset game
                    board = create_board()
                    current_piece = get_random_piece()
                    next_piece = get_random_piece()
                    score = 0
                    lines_cleared_total = 0
                    drop_counter = 0
                    last_drop_time = current_time
                    game_over = False

                if not game_over:
                    if event.key == pygame.K_LEFT:
                        if not check_collision(board, current_piece, x_offset=-1):
                            current_piece.x -= 1
                    elif event.key == pygame.K_RIGHT:
                        if not check_collision(board, current_piece, x_offset=1):
                            current_piece.x += 1
                    elif event.key == pygame.K_UP:
                        rotated_piece = Tetromino(current_piece.type)
                        rotated_piece.x = current_piece.x
                        rotated_piece.y = current_piece.y
                        rotated_piece.rotation = (current_piece.rotation + 1) % 4
                        rotated_piece.shape = SHAPES[rotated_piece.type][rotated_piece.rotation]
                        if not check_collision(board, rotated_piece):
                            current_piece.rotate()
                    elif event.key == pygame.K_DOWN:
                        if not check_collision(board, current_piece, y_offset=1):
                            current_piece.y += 1
                        else:
                            drop_counter = AUTO_DROP_INTERVAL  # Force immediate drop
                    elif event.key == pygame.K_SPACE:
                        # Hard drop
                        while not check_collision(board, current_piece, y_offset=1):
                            current_piece.y += 1

        # Auto drop
        drop_counter += dt
        if drop_counter >= AUTO_DROP_INTERVAL:
            drop_counter = 0
            if not check_collision(board, current_piece, y_offset=1):
                current_piece.y += 1
            else:
                if lock_piece(board, current_piece):
                    # Success lock
                    lines = clear_lines(board)
                    if lines > 0:
                        score += calculate_score(lines)
                        lines_cleared_total += lines
                else:
                    # Spawn too high -> game over
                    game_over = True

                # Generate new piece
                current_piece = next_piece
                next_piece = get_random_piece()

                # Check for immediate collision (game over on spawn)
                if check_collision(board, current_piece):
                    game_over = True

        # Drawing
        screen.fill(BLACK)

        # Draw game background
        pygame.draw.rect(
            screen,
            (30, 30, 30),
            (GAME_OFFSET_X - 2, GAME_OFFSET_Y - 2, GAME_WIDTH + 4, GAME_HEIGHT + 4)
        )

        # Draw grid and blocks
        draw_grid(screen, GAME_OFFSET_X, GAME_OFFSET_Y)

        # Draw locked blocks
        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                if board[y][x] is not None:
                    draw_block(screen, x, y, board[y][x], GAME_OFFSET_X, GAME_OFFSET_Y)

        # Draw active piece
        draw_piece(screen, current_piece, board, GAME_OFFSET_X, GAME_OFFSET_Y)

        # Draw HUD
        draw_hud(screen, score, lines_cleared_total, GAME_OFFSET_X, GAME_OFFSET_Y)

        # Draw Game Over layer
        if game_over:
            draw_game_over(screen, score, GAME_OFFSET_X, GAME_OFFSET_Y)

        pygame.display.flip()


if __name__ == "__main__":
    main()