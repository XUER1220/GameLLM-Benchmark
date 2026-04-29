import pygame
import sys
import random
import time

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_SIZE = 24
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
SHAPES = {
    'I': [(0, 1, 1, 1, 1)],
    'O': [(0, 1, 1), (0, 1, 1)],
    'T': [(0, 1, 0), (1, 1, 1)],
    'S': [(0, 0, 1, 1), (0, 1, 1, 0)],
    'Z': [(1, 1, 0, 0), (0, 1, 1, 0)],
    'J': [(0, 1, 0), (0, 1, 0), (1, 1, 0)],
    'L': [(0, 1, 0), (0, 1, 0), (0, 1, 1)],
}
COLORS = [(0, 255, 255), (255, 255, 0), (128, 0, 128), (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 140, 0)]

def rotate_shape(shape):
    return [list(reversed(col)) for col in zip(*shape)]

def check_collision(grid, shape, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell and (x + off_x < 0 or x + off_x >= GRID_WIDTH or y + off_y >= GRID_HEIGHT or grid[y + off_y][x + off_x]):
                return True
    return False

def merge_shape(grid, shape, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                grid[y + off_y][x + off_x] = cell

def clear_lines(grid):
    new_grid = [row for row in grid if 0 in row]
    cleared_lines = GRID_HEIGHT - len(new_grid)
    while len(new_grid) < GRID_HEIGHT:
        new_grid.insert(0, [0] * GRID_WIDTH)
    return new_grid, cleared_lines

def new_shape():
    shape_type = random.choice(list(SHAPES.keys()))
    return shape_type, SHAPES[shape_type], COLORS[list(SHAPES.keys()).index(shape_type)]

def draw_grid(screen, grid, shape=None, shape_offset=(0, 0)):
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, cell, (x * GRID_SIZE + 112, y * GRID_SIZE + 10, GRID_SIZE - 1, GRID_SIZE - 1))
    if shape:
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, shape[2], ((x + shape_offset[0]) * GRID_SIZE + 112, (y + shape_offset[1]) * GRID_SIZE + 10, GRID_SIZE - 1, GRID_SIZE - 1))

def draw_hud(screen, score, lines_cleared):
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    lines_text = font.render(f"Lines: {lines_cleared}", True, WHITE)
    screen.blit(score_text, (512, 10))
    screen.blit(lines_text, (512, 50))

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    shape, next_shape = new_shape(), new_shape()
    shape_offset = [GRID_WIDTH // 2 - len(shape[1][0]) // 2, 0]
    fall_time = 0
    score, lines_cleared = 0, 0
    game_over = False

    while True:
        fall_speed = 500
        if not game_over:
            fall_time += clock.get_rawtime()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        new_offset = [shape_offset[0] - 1, shape_offset[1]]
                        if not check_collision(grid, shape[1], new_offset):
                            shape_offset = new_offset
                    if event.key == pygame.K_RIGHT:
                        new_offset = [shape_offset[0] + 1, shape_offset[1]]
                        if not check_collision(grid, shape[1], new_offset):
                            shape_offset = new_offset
                    if event.key == pygame.K_UP:
                        new_shape = rotate_shape(shape[1])
                        if not check_collision(grid, new_shape, shape_offset):
                            shape[1] = new_shape
                    if event.key == pygame.K_DOWN:
                        fall_speed = 50
                    if event.key == pygame.K_SPACE:
                        while not check_collision(grid, shape[1], [shape_offset[0], shape_offset[1] + 1]):
                            shape_offset[1] += 1
                    if event.key == pygame.K_r:
                        grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
                        shape, next_shape = new_shape(), new_shape()
                        shape_offset = [GRID_WIDTH // 2 - len(shape[1][0]) // 2, 0]
                        fall_time = 0
                        score, lines_cleared = 0, 0
                        game_over = False
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
        
        if fall_time / fall_speed > 1:
            fall_time = 0
            new_offset = [shape_offset[0], shape_offset[1] + 1]
            if check_collision(grid, shape[1], new_offset):
                merge_shape(grid, shape[1], shape_offset)
                grid, cleared = clear_lines(grid)
                lines_cleared += cleared
                score += [0, 100, 300, 500, 800][cleared]
                shape = next_shape
                next_shape = new_shape()
                shape_offset = [GRID_WIDTH // 2 - len(shape[1][0]) // 2, 0]
                if check_collision(grid, shape[1], shape_offset):
                    game_over = True
            else:
                shape_offset = new_offset
        
        screen.fill(BLACK)
        draw_grid(screen, grid, shape[1], shape_offset)
        draw_hud(screen, score, lines_cleared)
        
        if game_over:
            font = pygame.font.Font(None, 48)
            game_over_text = font.render("Game Over", True, WHITE)
            score_text = font.render(f"Score: {score}", True, WHITE)
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(game_over_text, (280, 250))
            screen.blit(score_text, (280, 300))
            screen.blit(restart_text, (280, 350))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()