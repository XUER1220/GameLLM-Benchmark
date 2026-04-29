import pygame
import sys
import random
import time

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRID_SIZE = 24
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BOARD_OFFSET_X = 120
BOARD_OFFSET_Y = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 0, 0),
    (0, 255, 255),
    (255, 255, 0),
    (128, 0, 128),
    (0, 255, 0),
    (255, 165, 0),
    (0, 0, 255),
    (255, 0, 0)
]

SHAPES = [
    [[1, 1, 1, 1]],
    [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]]
]

def rotate(shape):
    return [list(reversed(col)) for col in zip(*shape)]

def check_collision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[cy + off_y][cx + off_x]:
                    return True
            except IndexError:
                return True
    return False

def remove_row(board, row):
    del board[row]
    return [[0 for _ in range(BOARD_WIDTH)]] + board

def join_matrixes(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            mat1[cy+off_y-1][cx+off_x] += val
    return mat1

def new_board():
    board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
    board += [[1 for _ in range(BOARD_WIDTH)]]
    return board

def new_piece():
    shape = random.choice(SHAPES)
    piece = {'shape': shape, 'color': random.randint(1, len(COLORS) - 1)}
    piece['rotation'] = random.randint(0, len(shape) - 1)
    piece['cx'] = BOARD_WIDTH // 2 - len(shape[0]) // 2
    piece['cy'] = 0
    return piece

def draw_matrix(board, screen, offset=(0, 0)):
    off_x, off_y = offset
    for y, row in enumerate(board):
        for x, val in enumerate(row):
            if val:
                pygame.draw.rect(screen, COLORS[val], ((x * GRID_SIZE) + off_x, (y * GRID_SIZE) + off_y, GRID_SIZE - 2, GRID_SIZE - 2))

def draw_next_shape(piece, screen):
    font = pygame.font.Font(None, 36)
    title_surface = font.render('Next Shape:', True, WHITE)
    screen.blit(title_surface, (BOARD_OFFSET_X + BOARD_WIDTH * GRID_SIZE + 20, BOARD_OFFSET_Y))
    draw_matrix(piece['shape'], screen, (BOARD_OFFSET_X + BOARD_WIDTH * GRID_SIZE + 10, BOARD_OFFSET_Y + 60))

def draw_text(surface, text, size, x, y, color=WHITE):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

def check_game_over(board):
    for cell in board[0]:
        if cell:
            return True
    return False

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Tetris Medium')
    clock = pygame.time.Clock()
    board = new_board()
    piece = new_piece()
    next_piece = new_piece()
    score = 0
    lines = 0
    fall_time = time.time()
    fall_speed = 0.5

    while True:
        current_time = time.time()
        fall_delay = fall_speed
        if current_time - fall_time > fall_delay:
            piece['cy'] += 1
            if check_collision(board, piece['shape'], (piece['cx'], piece['cy'])):
                piece['cy'] -= 1
                board = join_matrixes(board, piece['shape'], (piece['cx'], piece['cy']))
                for i, row in enumerate(board[:-1]):
                    if 0 not in row:
                        score += 100 if 1 in row else 300 if sum(row) == 2 else 500 if sum(row) == 3 else 800
                        lines += 1 if 1 in row else 2 if sum(row) == 2 else 3 if sum(row) == 3 else 4
                        board = remove_row(board, i)
                piece = next_piece
                next_piece = new_piece()
                if check_game_over(board):
                    break
            fall_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    piece['cx'] -= 1
                    if check_collision(board, piece['shape'], (piece['cx'], piece['cy'])):
                        piece['cx'] += 1
                elif event.key == pygame.K_RIGHT:
                    piece['cx'] += 1
                    if check_collision(board, piece['shape'], (piece['cx'], piece['cy'])):
                        piece['cx'] -= 1
                elif event.key == pygame.K_DOWN:
                    piece['cy'] += 1
                    if check_collision(board, piece['shape'], (piece['cx'], piece['cy'])):
                        piece['cy'] -= 1
                elif event.key == pygame.K_UP:
                    new_shape = rotate(piece['shape'])
                    if not check_collision(board, new_shape, (piece['cx'], piece['cy'])):
                        piece['shape'] = new_shape
                elif event.key == pygame.K_SPACE:
                    while not check_collision(board, piece['shape'], (piece['cx'], piece['cy'])):
                        piece['cy'] += 1
                    piece['cy'] -= 1
                    board = join_matrixes(board, piece['shape'], (piece['cx'], piece['cy']))
                    for i, row in enumerate(board[:-1]):
                        if 0 not in row:
                            score += 100 if 1 in row else 300 if sum(row) == 2 else 500 if sum(row) == 3 else 800
                            lines += 1 if 1 in row else 2 if sum(row) == 2 else 3 if sum(row) == 3 else 4
                            board = remove_row(board, i)
                    piece = next_piece
                    next_piece = new_piece()
                    if check_game_over(board):
                        break
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    main()

        screen.fill(BLACK)
        draw_matrix(board, screen, (BOARD_OFFSET_X, BOARD_OFFSET_Y))
        draw_matrix(piece['shape'], screen, (piece['cx'] * GRID_SIZE + BOARD_OFFSET_X, piece['cy'] * GRID_SIZE + BOARD_OFFSET_Y))
        draw_next_shape(next_piece, screen)
        draw_text(screen, f'Score: {score}', 36, BOARD_OFFSET_X + BOARD_WIDTH * GRID_SIZE / 2, BOARD_OFFSET_Y - 30)
        draw_text(screen, f'Lines: {lines}', 36, BOARD_OFFSET_X + BOARD_WIDTH * GRID_SIZE / 2, BOARD_OFFSET_Y - 60)
        pygame.display.flip()
        clock.tick(FPS)

    draw_text(screen, 'Game Over', 72, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50, RED)
    draw_text(screen, f'Final Score: {score}', 50, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 10, RED)
    draw_text(screen, 'Press R to Restart', 36, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60, RED)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

if __name__ == '__main__':
    main()