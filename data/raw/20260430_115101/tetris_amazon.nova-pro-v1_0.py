import pygame
import random
import sys

pygame.init()
random.seed(42)
clock = pygame.time.Clock()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Tetris Medium")

BLOCK_SIZE = 24
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BOARD_X = 160
BOARD_Y = 60
SCORE_X = 500
SCORE_Y = 100
FONT = pygame.font.Font(None, 36)
MOVE_DELAY = 500
MOVE_TIMER = 0
GAME_OVER = False
SCORE = 0
LINES_CLEARED = 0
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = [
    (0, 255, 255),  # I
    (255, 255, 0),  # O
    (128, 0, 128),  # T
    (0, 255, 0),    # S
    (255, 0, 0),    # Z
    (0, 0, 255),    # J
    (255, 165, 0)   # L
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

def draw_board(board):
    for y in range(len(board)):
        for x in range(len(board[y])):
            if board[y][x]!= 0:
                pygame.draw.rect(screen, COLORS[board[y][x] - 1],
                                 (BOARD_X + x * BLOCK_SIZE, BOARD_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, BLACK, (BOARD_X + x * BLOCK_SIZE, BOARD_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def rotate(shape):
    return [list(reversed(col)) for col in zip(*shape)]

def check_collision(board, shape, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                if x + off_x < 0 or x + off_x >= BOARD_WIDTH or y + off_y >= BOARD_HEIGHT or board[y + off_y][x + off_x]:
                    return True
    return False

def remove_line(board, line):
    del board[line]
    return [[0 for _ in range(BOARD_WIDTH)]] + board

def join_matrices(mat1, mat2, mat2_off):
    def inside(rect):
        ((x, y), (w, h)) = rect
        return 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT

    (off_x, off_y) = mat2_off
    for cy, row in enumerate(mat2):
        for cx, cell in enumerate(row):
            if inside(((cx + off_x, cy + off_y), (1, 1))) and cell:
                mat1[cy + off_y][cx + off_x] = cell
    return mat1

def new_board():
    return [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

def new_piece():
    shape = random.choice(SHAPES)
    piece = {
        "shape": shape,
        "color": random.randint(0, len(COLORS) - 1),
        "offset": [BOARD_WIDTH // 2 - len(shape[0]) // 2, -1]
    }
    return piece

def drop(board, piece):
    while not check_collision(board, piece["shape"], (0, piece["offset"][1] + 1)):
        piece["offset"][1] += 1
    join_matrices(board, piece["shape"], piece["offset"])
    return board

def check_lines(board):
    lines = [y for y, row in enumerate(board) if 0 not in row]
    for y in sorted(lines, reverse=True):
        board = remove_line(board, y)
        global SCORE, LINES_CLEARED
        SCORE += [100, 300, 500, 800][len(lines) - 1]
        LINES_CLEARED += len(lines)
    return board

def game_over(board):
    for x in range(BOARD_WIDTH):
        if board[0][x]:
            return True
    return False

def main():
    global GAME_OVER, SCORE, LINES_CLEARED, MOVE_TIMER
    board = new_board()
    piece = new_piece()
    while True:
        screen.fill(BLACK)
        draw_board(board)
        pygame.draw.rect(screen, WHITE, (BOARD_X - 2, BOARD_Y - 2, BLOCK_SIZE * BOARD_WIDTH + 4, BLOCK_SIZE * BOARD_HEIGHT + 4), 2)
        score_text = FONT.render(f"Score: {SCORE}", True, WHITE)
        lines_text = FONT.render(f"Lines: {LINES_CLEARED}", True, WHITE)
        screen.blit(score_text, (SCORE_X, SCORE_Y))
        screen.blit(lines_text, (SCORE_X, SCORE_Y + 40))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    board = new_board()
                    piece = new_piece()
                    SCORE = 0
                    LINES_CLEARED = 0
                    GAME_OVER = False
                if event.key == pygame.K_LEFT and not GAME_OVER:
                    if not check_collision(board, piece["shape"], (piece["offset"][0] - 1, piece["offset"][1])):
                        piece["offset"][0] -= 1
                if event.key == pygame.K_RIGHT and not GAME_OVER:
                    if not check_collision(board, piece["shape"], (piece["offset"][0] + 1, piece["offset"][1])):
                        piece["offset"][0] += 1
                if event.key == pygame.K_UP and not GAME_OVER:
                    rotated_shape = rotate(piece["shape"])
                    if not check_collision(board, rotated_shape, piece["offset"]):
                        piece["shape"] = rotated_shape
                if event.key == pygame.K_DOWN and not GAME_OVER:
                    if not check_collision(board, piece["shape"], (piece["offset"][0], piece["offset"][1] + 1)):
                        piece["offset"][1] += 1
                if event.key == pygame.K_SPACE and not GAME_OVER:
                    while not check_collision(board, piece["shape"], (piece["offset"][0], piece["offset"][1] + 1)):
                        piece["offset"][1] += 1

        if not GAME_OVER:
            MOVE_TIMER += clock.get_rawtime()
            clock.tick()
            if MOVE_TIMER / 1000 >= MOVE_DELAY / 1000:
                MOVE_TIMER = 0
                if not check_collision(board, piece["shape"], (piece["offset"][0], piece["offset"][1] + 1)):
                    piece["offset"][1] += 1
                else:
                    board = drop(board, piece)
                    board = check_lines(board)
                    if game_over(board):
                        GAME_OVER = True
                        game_over_text = FONT.render("Game Over", True, WHITE)
                        restart_text = FONT.render("Press R to Restart", True, WHITE)
                        screen.blit(game_over_text, (SCORE_X, SCORE_Y + 80))
                        screen.blit(restart_text, (SCORE_X, SCORE_Y + 120))
                    piece = new_piece()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()