import pygame
import random
import sys

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 24
BOARD_WIDTH = GRID_WIDTH * CELL_SIZE
BOARD_HEIGHT = GRID_HEIGHT * CELL_SIZE
BOARD_X = (SCREEN_WIDTH - BOARD_WIDTH) // 2 - 100
BOARD_Y = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2
FPS = 60
FALL_SPEED_INITIAL = 500  # 毫秒
SCORE_COLOR = (255, 255, 255)
GAME_OVER_COLOR = (255, 50, 50)
BACKGROUND_COLOR = (40, 40, 60)
GRID_COLOR = (70, 70, 90)
BOARD_BG_COLOR = (20, 20, 30)
COLORS = [
    (0, 240, 240),   # I 青色
    (240, 240, 0),   # O 黄色
    (160, 0, 240),   # T 紫色
    (0, 240, 0),     # S 绿色
    (240, 0, 0),     # Z 红色
    (0, 0, 240),     # J 蓝色
    (240, 160, 0)    # L 橙色
]
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]]   # L
]
random.seed(42)

def create_board():
    return [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def rotate_shape(shape):
    return [list(row) for row in zip(*reversed(shape))]

class Tetromino:
    def __init__(self):
        self.index = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.index]
        self.color = COLORS[self.index]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        rotated = rotate_shape(self.shape)
        return rotated

def valid_move(shape, x, y, board):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                board_x = x + j
                board_y = y + i
                if board_x < 0 or board_x >= GRID_WIDTH or board_y >= GRID_HEIGHT:
                    return False
                if board_y >= 0 and board[board_y][board_x]:
                    return False
    return True

def merge(board, tetromino):
    for i, row in enumerate(tetromino.shape):
        for j, cell in enumerate(row):
            if cell:
                board_y = tetromino.y + i
                board_x = tetromino.x + j
                if 0 <= board_y < GRID_HEIGHT and 0 <= board_x < GRID_WIDTH:
                    board[board_y][board_x] = tetromino.color

def remove_lines(board):
    lines_removed = 0
    new_board = [row for row in board if any(cell == 0 for cell in row)]
    lines_removed = GRID_HEIGHT - len(new_board)
    while len(new_board) < GRID_HEIGHT:
        new_board.insert(0, [0] * GRID_WIDTH)
    return lines_removed, new_board

def draw_board(surface, board, grid=True):
    pygame.draw.rect(surface, BOARD_BG_COLOR, (BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT))
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = board[y][x]
            if color:
                pygame.draw.rect(surface, color, (BOARD_X + x * CELL_SIZE, BOARD_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(surface, (255, 255, 255), (BOARD_X + x * CELL_SIZE, BOARD_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
    if grid:
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(surface, GRID_COLOR, (BOARD_X, BOARD_Y + y * CELL_SIZE), (BOARD_X + BOARD_WIDTH, BOARD_Y + y * CELL_SIZE))
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(surface, GRID_COLOR, (BOARD_X + x * CELL_SIZE, BOARD_Y), (BOARD_X + x * CELL_SIZE, BOARD_Y + BOARD_HEIGHT))

def draw_tetromino(surface, tetromino):
    for i, row in enumerate(tetromino.shape):
        for j, cell in enumerate(row):
            if cell:
                pygame.draw.rect(surface, tetromino.color, (BOARD_X + (tetromino.x + j) * CELL_SIZE, BOARD_Y + (tetromino.y + i) * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(surface, (255, 255, 255), (BOARD_X + (tetromino.x + j) * CELL_SIZE, BOARD_Y + (tetromino.y + i) * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

def draw_hud(surface, score, lines, game_over):
    font = pygame.font.SysFont(None, 36)
    title = font.render("TETRIS", True, (255, 200, 0))
    surface.blit(title, (BOARD_X + BOARD_WIDTH + 30, BOARD_Y))
    score_text = font.render(f"SCORE: {score}", True, SCORE_COLOR)
    surface.blit(score_text, (BOARD_X + BOARD_WIDTH + 30, BOARD_Y + 60))
    lines_text = font.render(f"LINES: {lines}", True, SCORE_COLOR)
    surface.blit(lines_text, (BOARD_X + BOARD_WIDTH + 30, BOARD_Y + 110))
    if game_over:
        over_font = pygame.font.SysFont(None, 48)
        game_over_text = over_font.render("GAME OVER", True, GAME_OVER_COLOR)
        surface.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
        restart_font = pygame.font.SysFont(None, 32)
        restart_text = restart_font.render("Press R to Restart", True, (200, 200, 100))
        surface.blit(restart_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 20))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris Medium")
    clock = pygame.time.Clock()

    board = create_board()
    current_tetromino = Tetromino()
    score = 0
    lines_cleared = 0
    fall_time = 0
    game_over = False

    while True:
        dt = clock.tick(FPS)
        fall_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    board = create_board()
                    current_tetromino = Tetromino()
                    score = 0
                    lines_cleared = 0
                    game_over = False
                if not game_over:
                    if event.key == pygame.K_LEFT:
                        if valid_move(current_tetromino.shape, current_tetromino.x - 1, current_tetromino.y, board):
                            current_tetromino.x -= 1
                    if event.key == pygame.K_RIGHT:
                        if valid_move(current_tetromino.shape, current_tetromino.x + 1, current_tetromino.y, board):
                            current_tetromino.x += 1
                    if event.key == pygame.K_UP:
                        rotated = current_tetromino.rotate()
                        if valid_move(rotated, current_tetromino.x, current_tetromino.y, board):
                            current_tetromino.shape = rotated
                    if event.key == pygame.K_DOWN:
                        if valid_move(current_tetromino.shape, current_tetromino.x, current_tetromino.y + 1, board):
                            current_tetromino.y += 1
                    if event.key == pygame.K_SPACE:
                        while valid_move(current_tetromino.shape, current_tetromino.x, current_tetromino.y + 1, board):
                            current_tetromino.y += 1

        if not game_over:
            if fall_time >= FALL_SPEED_INITIAL:
                fall_time = 0
                if valid_move(current_tetromino.shape, current_tetromino.x, current_tetromino.y + 1, board):
                    current_tetromino.y += 1
                else:
                    merge(board, current_tetromino)
                    removed, board = remove_lines(board)
                    if removed == 1:
                        score += 100
                    elif removed == 2:
                        score += 300
                    elif removed == 3:
                        score += 500
                    elif removed == 4:
                        score += 800
                    lines_cleared += removed
                    current_tetromino = Tetromino()
                    if not valid_move(current_tetromino.shape, current_tetromino.x, current_tetromino.y, board):
                        game_over = True

        screen.fill(BACKGROUND_COLOR)
        draw_board(screen, board)
        if not game_over:
            draw_tetromino(screen, current_tetromino)
        draw_hud(screen, score, lines_cleared, game_over)
        pygame.display.flip()

if __name__ == "__main__":
    main()