import pygame
import sys
import random
import time

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_WIDTH, GRID_HEIGHT = 10, 20
GRID_SIZE = 24
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_WIDTH * GRID_SIZE) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_HEIGHT * GRID_SIZE) // 2
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
COLORS = [(0, 255, 255), (255, 255, 0), (128, 0, 128), (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 165, 0)]

SHAPES = [
    [[1, 1, 1, 1]],
    [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
    [[1, 1, 0], [0, 1, 1], [0, 1, 0]],
    [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
    [[1, 1, 0], [1, 1, 0], [0, 0, 0]],
    [[0, 0, 1], [1, 1, 1], [0, 0, 0]],
    [[1, 0, 0], [1, 1, 1], [0, 0, 0]]
]

def rotate(shape):
    return [list(reversed(col)) for col in zip(*shape)]

def check_collision(grid, shape, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell and (off_x + x < 0 or off_x + x >= len(grid[0]) or off_y + y >= len(grid) or grid[off_y + y][off_x + x]):
                return True
    return False

def clear_rows(grid, lines):
    for line in sorted(lines, reverse=True):
        del grid[line]
        grid.insert(0, [0] * GRID_WIDTH)

def draw_grid(screen, grid):
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, COLORS[cell], (GRID_OFFSET_X + x * GRID_SIZE, GRID_OFFSET_Y + y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)
                pygame.draw.rect(screen, GRAY, (GRID_OFFSET_X + x * GRID_SIZE, GRID_OFFSET_Y + y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

def draw_shape(screen, shape, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, COLORS[cell], (GRID_OFFSET_X + (off_x + x) * GRID_SIZE, GRID_OFFSET_Y + (off_y + y) * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)
                pygame.draw.rect(screen, GRAY, (GRID_OFFSET_X + (off_x + x) * GRID_SIZE, GRID_OFFSET_Y + (off_y + y) * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

def draw_text(screen, text, size, x, y, color=WHITE):
    font = pygame.font.SysFont('consolas', size, bold=True)
    label = font.render(text, 1, color)
    screen.blit(label, (x, y))

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()

    grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    shape = random.choice(SHAPES)
    shape_color = random.randint(0, len(COLORS) - 1)
    shape_pos = [GRID_WIDTH // 2 - len(shape[0]) // 2, 0]
    game_over = False
    score = 0
    lines = 0
    fall_time = time.time()

    while True:
        grid_copy = [row.copy() for row in grid]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    shape_pos[0] -= 1
                    if check_collision(grid, shape, shape_pos):
                        shape_pos[0] += 1
                elif event.key == pygame.K_RIGHT:
                    shape_pos[0] += 1
                    if check_collision(grid, shape, shape_pos):
                        shape_pos[0] -= 1
                elif event.key == pygame.K_UP:
                    rotated_shape = rotate(shape)
                    if not check_collision(grid, rotated_shape, shape_pos):
                        shape = rotated_shape
                elif event.key == pygame.K_DOWN:
                    shape_pos[1] += 1
                    if check_collision(grid, shape, shape_pos):
                        shape_pos[1] -= 1
                elif event.key == pygame.K_SPACE:
                    while not check_collision(grid, shape, shape_pos):
                        shape_pos[1] += 1
                    shape_pos[1] -= 1
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r and game_over:
                    main()

        if not game_over:
            current_time = time.time()
            if current_time - fall_time > 0.5:
                shape_pos[1] += 1
                if check_collision(grid, shape, shape_pos):
                    shape_pos[1] -= 1
                    for y, row in enumerate(shape):
                        for x, cell in enumerate(row):
                            if cell:
                                grid[y + shape_pos[1]][x + shape_pos[0]] = shape_color
                    shape, shape_color = random.choice(SHAPES), random.randint(0, len(COLORS) - 1)
                    shape_pos = [GRID_WIDTH // 2 - len(shape[0]) // 2, 0]
                    if check_collision(grid, shape, shape_pos):
                        game_over = True
                    fall_time = time.time()

            for y, row in enumerate(shape):
                for x, cell in enumerate(row):
                    if cell:
                        grid[y + shape_pos[1]][x + shape_pos[0]] = shape_color

            lines_to_clear = [idx for idx, row in enumerate(grid) if 0 not in row]
            if lines_to_clear:
                clear_rows(grid, lines_to_clear)
                lines += len(lines_to_clear)
                score += {1: 100, 2: 300, 3: 500, 4: 800}[len(lines_to_clear)]

        screen.fill(BLACK)
        draw_grid(screen, grid)
        if not game_over:
            draw_shape(screen, shape, shape_pos)
        draw_text(screen, f'Score: {score}', 30, 400, 50)
        draw_text(screen, f'Lines: {lines}', 30, 400, 100)
        if game_over:
            draw_text(screen, 'Game Over', 50, 200, 200)
            draw_text(screen, f'Final Score: {score}', 30, 250, 300)
            draw_text(screen, 'Press R to Restart', 30, 200, 350)
        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()