import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_WIDTH, GRID_HEIGHT = 10, 20
CELL_SIZE = 24
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_WIDTH * CELL_SIZE) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_HEIGHT * CELL_SIZE) // 2
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255), (255, 255, 0), (128, 0, 128), (0, 255, 0),
    (255, 165, 0), (0, 0, 255), (255, 0, 0)
]
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]]
]

score = 0
lines = 0
game_over = False
grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
current_piece = None
current_rotation = 0
current_x = GRID_WIDTH // 2 - 1
current_y = 0
fall_time = 0

def new_piece():
    global current_piece, current_rotation, current_x, current_y
    piece = random.choice(SHAPES)
    current_piece = piece
    current_rotation = 0
    current_x = GRID_WIDTH // 2 - 1
    current_y = 0
    if check_collision(grid, current_piece, (current_x, current_y, current_rotation)):
        game_over = True

def rotate(piece):
    return [list(row) for row in zip(*piece[::-1])]

def check_collision(grid, piece, position):
    x, y, rotation = position
    piece = rotate(piece, rotation)
    for px, py in [(i, j) for j, row in enumerate(piece) for i, val in enumerate(row) if val]:
        if x + px < 0 or x + px >= GRID_WIDTH or y + py >= GRID_HEIGHT:
            return True
        if y + py >= 0 and grid[y + py][x + px]:
            return True
    return False

def clear_lines(grid):
    global lines, score
    new_grid = [row for row in grid if any(row)]
    while len(new_grid) < GRID_HEIGHT:
        new_grid.insert(0, [0] * GRID_WIDTH)
    cleared = GRID_HEIGHT - len(new_grid)
    lines += cleared
    if cleared == 1:
        score += 100
    elif cleared == 2:
        score += 300
    elif cleared == 3:
        score += 500
    elif cleared == 4:
        score += 800
    return new_grid

def draw_grid(surface, grid):
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(surface, COLORS[cell - 1], (GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 0)
            pygame.draw.rect(surface, GRAY, (GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

def draw_piece(surface, piece, x, y, rotation):
    piece = rotate(piece, rotation)
    for px, py in [(i, j) for j, row in enumerate(piece) for i, val in enumerate(row) if val]:
        pygame.draw.rect(surface, COLORS[len(SHAPES) - 1], (GRID_OFFSET_X + (x + px) * CELL_SIZE, GRID_OFFSET_Y + (y + py) * CELL_SIZE, CELL_SIZE, CELL_SIZE), 0)

def draw_hud(surface, score, lines):
    font = pygame.font.Font(None, 36)
    score_text = font.render(f'Score: {score}', True, WHITE)
    lines_text = font.render(f'Lines: {lines}', True, WHITE)
    surface.blit(score_text, (GRID_OFFSET_X + GRID_WIDTH * CELL_SIZE + 20, GRID_OFFSET_Y))
    surface.blit(lines_text, (GRID_OFFSET_X + GRID_WIDTH * CELL_SIZE + 20, GRID_OFFSET_Y + 40))

def draw_game_over(surface, score):
    font = pygame.font.Font(None, 74)
    game_over_text = font.render('Game Over', True, WHITE)
    score_text = font.render(f'Score: {score}', True, WHITE)
    restart_text = font.render('Press R to Restart', True, WHITE)
    surface.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    surface.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
    surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

def main():
    global score, lines, game_over, grid, fall_time, current_piece
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris Medium")
    clock = pygame.time.Clock()
    new_piece()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r and game_over:
                    score = 0
                    lines = 0
                    game_over = False
                    grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
                    new_piece()
                if not game_over:
                    if event.key == pygame.K_LEFT:
                        if not check_collision(grid, current_piece, (current_x - 1, current_y, current_rotation)):
                            current_x -= 1
                    if event.key == pygame.K_RIGHT:
                        if not check_collision(grid, current_piece, (current_x + 1, current_y, current_rotation)):
                            current_x += 1
                    if event.key == pygame.K_UP:
                        if not check_collision(grid, current_piece, (current_x, current_y, (current_rotation + 1) % 4)):
                            current_rotation = (current_rotation + 1) % 4
                    if event.key == pygame.K_DOWN:
                        if not check_collision(grid, current_piece, (current_x, current_y + 1, current_rotation)):
                            current_y += 1
                    if event.key == pygame.K_SPACE:
                        while not check_collision(grid, current_piece, (current_x, current_y + 1, current_rotation)):
                            current_y += 1

        current_time = pygame.time.get_ticks()
        if current_time - fall_time > 500:
            fall_time = current_time
            if not check_collision(grid, current_piece, (current_x, current_y + 1, current_rotation)):
                current_y += 1
            else:
                for px, py in [(i, j) for j, row in enumerate(current_piece) for i, val in enumerate(row) if val]:
                    grid[current_y + py][current_x + px] = len(SHAPES) - SHAPES.index(current_piece) + 1
                grid = clear_lines(grid)
                new_piece()

        screen.fill(BLACK)
        draw_grid(screen, grid)
        if not game_over:
            draw_piece(screen, current_piece, current_x, current_y, current_rotation)
        draw_hud(screen, score, lines)
        if game_over:
            draw_game_over(screen, score)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()