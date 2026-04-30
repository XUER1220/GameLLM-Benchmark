import pygame
import sys
import random

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_SIZE = 24
FPS = 60
MOVE_DELAY = 500
SCORE_PER_LINE = [0, 100, 300, 500, 800]

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)

SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[1, 1, 1], [0, 1, 0]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]]
}
SHAPE_COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': PURPLE,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE
}

def rotate(shape):
    return [list(reversed(row)) for row in zip(*shape)]

def check_collision(grid, shape, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                if x + off_x < 0 or x + off_x >= GRID_WIDTH or y + off_y >= GRID_HEIGHT or grid[y + off_y][x + off_x]:
                    return True
    return False

def clear_lines(grid):
    new_grid = [row for row in grid if 0 in row]
    lines_cleared = GRID_HEIGHT - len(new_grid)
    new_grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT - len(new_grid))] + new_grid
    return new_grid, lines_cleared

def new_piece():
    shape = random.choice(list(SHAPES.keys()))
    return shape, SHAPES[shape], SHAPE_COLORS[shape]

def draw_grid(screen, grid, piece=None, piece_offset=None):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if piece and piece_offset:
                piece_x, piece_y = piece_offset
                if (x >= piece_x and x < piece_x + len(piece[0])) and (y >= piece_y and y < piece_y + len(piece)):
                    if piece[y - piece_y][x - piece_x]:
                        pygame.draw.rect(screen, piece[1], (x * GRID_SIZE + 1, y * GRID_SIZE + 1, GRID_SIZE - 2, GRID_SIZE - 2))
                        continue
            if grid[y][x]:
                pygame.draw.rect(screen, grid[y][x], (x * GRID_SIZE + 1, y * GRID_SIZE + 1, GRID_SIZE - 2, GRID_SIZE - 2))
            else:
                pygame.draw.rect(screen, GRAY, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

def draw_hud(screen, score, lines_cleared):
    font = pygame.font.SysFont('Arial', 24)
    score_text = font.render(f'Score: {score}', True, WHITE)
    lines_text = font.render(f'Lines: {lines_cleared}', True, WHITE)
    screen.blit(score_text, (480, 100))
    screen.blit(lines_text, (480, 130))

def game_over_screen(screen, score):
    font = pygame.font.SysFont('Arial', 48)
    over_text = font.render('Game Over', True, RED)
    score_text = font.render(f'Score: {score}', True, WHITE)
    restart_text = font.render('Press R to Restart', True, WHITE)
    screen.blit(over_text, (300, 250))
    screen.blit(score_text, (300, 320))
    screen.blit(restart_text, (280, 370))

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Tetris')
    clock = pygame.time.Clock()
    grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    score = 0
    lines_cleared = 0
    piece, piece_shape, piece_color = new_piece()
    piece_offset = (GRID_WIDTH // 2 - len(piece_shape[0]) // 2, 0)
    move_timer = 0
    game_over = False

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
                    return main()
                if not game_over:
                    if event.key == pygame.K_LEFT:
                        new_offset = (piece_offset[0] - 1, piece_offset[1])
                        if not check_collision(grid, piece_shape, new_offset):
                            piece_offset = new_offset
                    if event.key == pygame.K_RIGHT:
                        new_offset = (piece_offset[0] + 1, piece_offset[1])
                        if not check_collision(grid, piece_shape, new_offset):
                            piece_offset = new_offset
                    if event.key == pygame.K_UP:
                        new_shape = rotate(piece_shape)
                        if not check_collision(grid, new_shape, piece_offset):
                            piece_shape = new_shape
                    if event.key == pygame.K_DOWN:
                        new_offset = (piece_offset[0], piece_offset[1] + 1)
                        if not check_collision(grid, piece_shape, new_offset):
                            piece_offset = new_offset
                            score += 1
                    if event.key == pygame.K_SPACE:
                        while not check_collision(grid, piece_shape, (piece_offset[0], piece_offset[1] + 1)):
                            piece_offset = (piece_offset[0], piece_offset[1] + 1)

        if not game_over:
            move_timer += clock.get_rawtime()
            if move_timer >= MOVE_DELAY:
                move_timer = 0
                new_offset = (piece_offset[0], piece_offset[1] + 1)
                if not check_collision(grid, piece_shape, new_offset):
                    piece_offset = new_offset
                else:
                    for y, row in enumerate(piece_shape):
                        for x, cell in enumerate(row):
                            if cell:
                                grid[y + piece_offset[1]][x + piece_offset[0]] = piece_color
                    grid, lines = clear_lines(grid)
                    lines_cleared += lines
                    score += SCORE_PER_LINE[lines]
                    piece, piece_shape, piece_color = new_piece()
                    piece_offset = (GRID_WIDTH // 2 - len(piece_shape[0]) // 2, 0)
                    if check_collision(grid, piece_shape, piece_offset):
                        game_over = True

        screen.fill(BLACK)
        draw_grid(screen, grid, piece_shape, piece_offset)
        draw_hud(screen, score, lines_cleared)
        if game_over:
            game_over_screen(screen, score)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()