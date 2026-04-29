import pygame
import random
import sys

# Initialization
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_COL = 10
GRID_ROW = 20
CELL_SIZE = 24
GRID_WIDTH = GRID_COL * CELL_SIZE
GRID_HEIGHT = GRID_ROW * CELL_SIZE
OFFSET_X = (SCREEN_WIDTH - GRID_WIDTH) // 2
OFFSET_Y = (SCREEN_HEIGHT - GRID_HEIGHT) // 2

FPS = 60
DROP_INTERVAL = 500  # ms

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (192, 192, 192)

# Tetromino colors (I, O, T, S, Z, J, L)
COLORS = {
    'I': (0, 255, 255),    # Cyan
    'O': (255, 255, 0),    # Yellow
    'T': (128, 0, 128),    # Purple
    'S': (0, 255, 0),      # Green
    'Z': (255, 0, 0),      # Red
    'J': (0, 0, 255),      # Blue
    'L': (255, 165, 0),    # Orange
}

# Shapes definition (as lists of [x, y] coordinates relative to origin)
SHAPES = {
    'I': [[0, 0], [0, 1], [0, 2], [0, 3]],
    'O': [[0, 0], [1, 0], [0, 1], [1, 1]],
    'T': [[0, 0], [-1, 1], [0, 1], [1, 1]],
    'S': [[1, 0], [0, 0], [0, 1], [-1, 1]],
    'Z': [[-1, 0], [0, 0], [0, 1], [1, 1]],
    'J': [[-1, 0], [0, 0], [1, 0], [1, 1]],
    'L': [[1, 0], [0, 0], [-1, 0], [-1, 1]]
}

# Scoring
SCORE_TABLE = {1: 100, 2: 300, 3: 500, 4: 800}

# Seed for reproducibility
random.seed(42)

# Font setup
font_large = pygame.font.SysFont(None, 48)
font_medium = pygame.font.SysFont(None, 24)
font_small = pygame.font.SysFont(None, 20)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris Medium")
clock = pygame.time.Clock()


def create_board():
    """Return empty board (2D list) of size GRID_ROW x GRID_COL filled with None."""
    return [[None for _ in range(GRID_COL)] for _ in range(GRID_ROW)]


def get_new_piece():
    """Generate a new random piece with fixed seed."""
    pieces = 'IOTSZJL'
    shape_type = random.choice(pieces)
    shape = SHAPES[shape_type]
    # Center the piece horizontally
    center_col = GRID_COL // 2
    # Adjust shape to be centered at column center; use x=offset to be relative to the piece itself
    # Instead of absolute coordinates, we store relative coordinates and then adjust origin
    min_x = min(cell[0] for cell in shape)
    min_y = min(cell[1] for cell in shape)
    # Normalize shape
    normalized = [[cell[0] - min_x, cell[1] - min_y] for cell in shape]
    # Place piece at top and centered
    x = center_col - 2  # For 'I' and 'O' shapes which extend to 2 cols wide
    y = 0
    return {'type': shape_type, 'shape': normalized, 'x': x, 'y': y}


def rotate(piece):
    """Rotate piece 90 degrees clockwise: (x, y) -> (y, -x)."""
    new_shape = [[cell[1], -cell[0]] for cell in piece['shape']]
    return {'type': piece['type'], 'shape': new_shape, 'x': piece['x'], 'y': piece['y']}


def collide(board, piece):
    """Check if piece collides with walls or existing blocks."""
    for cell in piece['shape']:
        x = piece['x'] + cell[0]
        y = piece['y'] + cell[1]
        # Check board boundaries
        if x < 0 or x >= GRID_COL or y >= GRID_ROW:
            return True
        # Check occupied cells
        if y >= 0 and board[y][x] is not None:
            return True
    return False


def lock_piece(board, piece):
    """Lock the current piece into the board."""
    for cell in piece['shape']:
        x = piece['x'] + cell[0]
        y = piece['y'] + cell[1]
        if y >= 0:
            board[y][x] = piece['type']


def clear_lines(board):
    """Clear completed lines and return how many."""
    lines_cleared = 0
    y = GRID_ROW - 1
    while y >= 0:
        if all(board[y][x] is not None for x in range(GRID_COL)):
            # Remove line
            del board[y]
            # Add empty line at top
            board.insert(0, [None for _ in range(GRID_COL)])
            lines_cleared += 1
            # Don't decrement y, since lines shifted down
        else:
            y -= 1
    return lines_cleared


def draw_board(board, surface):
    """Draw the game board."""
    # Draw grid
    for y in range(GRID_ROW + 1):
        pygame.draw.line(surface, LIGHT_GRAY,
                         (OFFSET_X, OFFSET_Y + y * CELL_SIZE),
                         (OFFSET_X + GRID_WIDTH, OFFSET_Y + y * CELL_SIZE))
    for x in range(GRID_COL + 1):
        pygame.draw.line(surface, LIGHT_GRAY,
                         (OFFSET_X + x * CELL_SIZE, OFFSET_Y),
                         (OFFSET_X + x * CELL_SIZE, OFFSET_Y + GRID_HEIGHT))

    # Draw cells
    for y in range(GRID_ROW):
        for x in range(GRID_COL):
            if board[y][x] is not None:
                color = COLORS[board[y][x]]
                cell_rect = pygame.Rect(OFFSET_X + x * CELL_SIZE,
                                        OFFSET_Y + y * CELL_SIZE,
                                        CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, color, cell_rect)
                pygame.draw.rect(surface, BLACK, cell_rect, 1)


def draw_piece(piece, surface):
    """Draw the current active piece."""
    if piece is None:
        return
    color = COLORS[piece['type']]
    for cell in piece['shape']:
        x, y = piece['x'] + cell[0], piece['y'] + cell[1]
        if y >= 0:
            cell_rect = pygame.Rect(OFFSET_X + x * CELL_SIZE,
                                    OFFSET_Y + y * CELL_SIZE,
                                    CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, color, cell_rect)
            pygame.draw.rect(surface, BLACK, cell_rect, 1)


def draw_hud(score, lines_cleared, surface):
    """Draw HUD on the right side of the board."""
    hud_x = OFFSET_X + GRID_WIDTH + 30
    hud_y = OFFSET_Y

    # Labels
    score_label = font_medium.render(f"Score: {score}", True, WHITE)
    lines_label = font_medium.render(f"Lines: {lines_cleared}", True, WHITE)

    surface.blit(score_label, (hud_x, hud_y))
    surface.blit(lines_label, (hud_x, hud_y + 50))


def draw_game_over(surface, score):
    """Draw Game Over screen."""
    # Overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    surface.blit(overlay, (0, 0))

    # Game Over text
    game_over_text = font_large.render("GAME OVER", True, WHITE)
    score_text = font_medium.render(f"Final Score: {score}", True, WHITE)
    restart_text = font_medium.render("Press R to Restart", True, WHITE)
    exit_text = font_small.render("Press ESC to Exit", True, WHITE)

    # Center texts
    rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
    surface.blit(game_over_text, rect)
    rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    surface.blit(score_text, rect)
    rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
    surface.blit(restart_text, rect)
    rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
    surface.blit(exit_text, rect)


def draw_start_message(surface):
    """Draw initial start message."""
    text1 = font_small.render("Press any key to start", True, WHITE)
    rect = text1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    surface.blit(text1, rect)


def main():
    # Initialize game state
    board = create_board()
    drop_time = 0
    current_piece = None
    next_drop = DROP_INTERVAL
    score = 0
    lines = 0
    game_over = False
    waiting_to_start = True

    running = True

    # Generate first piece (initially None until start)
    current_piece = None

    while running:
        dt = clock.tick(FPS)
        drop_time += dt

        # Input handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and (game_over or waiting_to_start):
                    # Restart game
                    board = create_board()
                    score = 0
                    lines = 0
                    game_over = False
                    waiting_to_start = False
                    current_piece = get_new_piece()
                    next_drop = DROP_INTERVAL
                    drop_time = 0
                elif not waiting_to_start and not game_over:
                    if event.key == pygame.K_LEFT:
                        new_piece = {'type': current_piece['type'],
                                     'shape': current_piece['shape'],
                                     'x': current_piece['x'] - 1,
                                     'y': current_piece['y']}
                        if not collide(board, new_piece):
                            current_piece = new_piece
                    elif event.key == pygame.K_RIGHT:
                        new_piece = {'type': current_piece['type'],
                                     'shape': current_piece['shape'],
                                     'x': current_piece['x'] + 1,
                                     'y': current_piece['y']}
                        if not collide(board, new_piece):
                            current_piece = new_piece
                    elif event.key == pygame.K_UP:
                        rotated = rotate(current_piece)
                        if not collide(board, rotated):
                            current_piece = rotated
                    elif event.key == pygame.K_DOWN:
                        new_piece = {'type': current_piece['type'],
                                     'shape': current_piece['shape'],
                                     'x': current_piece['x'],
                                     'y': current_piece['y'] + 1}
                        if not collide(board, new_piece):
                            current_piece = new_piece
                            drop_time = 0
                    elif event.key == pygame.K_SPACE:
                        # Hard drop
                        while not collide(board, {
                                'type': current_piece['type'],
                                'shape': current_piece['shape'],
                                'x': current_piece['x'],
                                'y': current_piece['y'] + 1}):
                            current_piece['y'] += 1
                        drop_time = 0

        # Start game on first key press
        if waiting_to_start and not game_over:
            # Draw initial screen
            screen.fill(BLACK)
            draw_board(board, screen)
            draw_start_message(screen)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key != pygame.K_ESCAPE and event.key != pygame.K_r:
                    waiting_to_start = False
                    current_piece = get_new_piece()
                    next_drop = DROP_INTERVAL
                    drop_time = 0
            continue

        # Update game
        if not waiting_to_start and not game_over:
            # Auto drop
            if drop_time >= next_drop:
                drop_time = 0
                new_piece = {'type': current_piece['type'],
                             'shape': current_piece['shape'],
                             'x': current_piece['x'],
                             'y': current_piece['y'] + 1}
                if collide(board, new_piece):
                    # Lock piece
                    lock_piece(board, current_piece)
                    # Check lines
                    cleared = clear_lines(board)
                    if cleared > 0:
                        score += SCORE_TABLE[cleared]
                        lines += cleared
                    # Get new piece
                    current_piece = get_new_piece()
                    # Check for immediate collision (game over)
                    if collide(board, current_piece):
                        game_over = True
                else:
                    current_piece = new_piece

        # Render
        screen.fill(BLACK)
        draw_board(board, screen)
        draw_piece(current_piece, screen)
        draw_hud(score, lines, screen)

        if game_over:
            draw_game_over(screen, score)
        elif waiting_to_start:
            draw_start_message(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()