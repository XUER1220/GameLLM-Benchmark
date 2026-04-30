import pygame
import sys
import random

pygame.init()
random.seed(42)

WINDOW_SIZE = (800, 600)
BOARD_SIZE = (10, 20)
CELL_SIZE = 24
BOARD_WIDTH = BOARD_SIZE[0] * CELL_SIZE
BOARD_HEIGHT = BOARD_SIZE[1] * CELL_SIZE
FPS = 60
AUTO_DROP_INTERVAL = 500

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = [
    (0, 0, 0),
    (0, 255, 255),
    (255, 255, 0),
    (128, 0, 128),
    (0, 255, 0),
    (255, 0, 0),
    (0, 0, 255),
    (255, 165, 0)
]

SHAPES = [
    [[1, 1, 1, 1]],
    [[0, 1, 1, 0], [0, 1, 1, 0]],
    [[1, 1, 1], [0, 1, 0]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]]
]

screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Tetris Medium")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

def draw_board(board):
    for y in range(BOARD_SIZE[1]):
        for x in range(BOARD_SIZE[0]):
            cell_value = board[y][x]
            cell_rect = pygame.Rect(100 + x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, COLORS[cell_value], cell_rect)
            pygame.draw.rect(screen, BLACK, cell_rect, 1)

def draw_shape(shape, offset):
    for y in range(len(shape)):
        for x in range(len(shape[y])):
            if shape[y][x]:
                cell_rect = pygame.Rect(100 + (x + offset[0]) * CELL_SIZE, (y + offset[1]) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, COLORS[shape[y][x]], cell_rect)
                pygame.draw.rect(screen, BLACK, cell_rect, 1)

def rotate(shape):
    return [list(reversed(col)) for col in zip(*shape)]

def check_collision(board, shape, offset):
    for y in range(len(shape)):
        for x in range(len(shape[y])):
            if shape[y][x]:
                if x + offset[0] < 0 or x + offset[0] >= BOARD_SIZE[0] or y + offset[1] >= BOARD_SIZE[1]:
                    return True
                if y + offset[1] >= 0 and board[y + offset[1]][x + offset[0]]:
                    return True
    return False

def merge_shape(board, shape, offset):
    for y in range(len(shape)):
        for x in range(len(shape[y])):
            if shape[y][x]:
                board[y + offset[1]][x + offset[0]] = shape[y][x]
    return board

def clear_lines(board):
    new_board = [row for row in board if any(cell == 0 for cell in row)]
    while len(new_board) < BOARD_SIZE[1]:
        new_board.insert(0, [0] * BOARD_SIZE[0])
    return new_board

def get_score(cleared_lines):
    return cleared_lines * (100 if cleared_lines == 1 else (300 if cleared_lines == 2 else (500 if cleared_lines == 3 else 800)))

def game_over(board):
    for x in range(BOARD_SIZE[0]):
        if board[0][x]:
            return True
    return False

def draw_hud(score, lines_cleared):
    score_text = font.render(f"Score: {score}", True, WHITE)
    lines_text = font.render(f"Lines: {lines_cleared}", True, WHITE)
    screen.blit(score_text, (350, 20))
    screen.blit(lines_text, (350, 60))

def main():
    board = [[0] * BOARD_SIZE[0] for _ in range(BOARD_SIZE[1])]
    shape = random.choice(SHAPES)
    shape_color = random.randint(1, len(COLORS) - 1)
    shape = [[shape_color if cell else 0 for cell in row] for row in shape]
    shape_offset = [BOARD_SIZE[0] // 2 - len(shape[0]) // 2, 0]
    next_shape = random.choice(SHAPES)
    next_shape_color = random.randint(1, len(COLORS) - 1)
    next_shape = [[next_shape_color if cell else 0 for cell in row] for row in next_shape]
    score = 0
    lines_cleared = 0
    drop_timer = AUTO_DROP_INTERVAL
    paused = False

    while True:
        drop_timer -= clock.get_rawtime()
        screen.fill(BLACK)
        draw_board(board)
        draw_shape(shape, shape_offset)
        draw_hud(score, lines_cleared)

        if paused:
            game_over_text = font.render("Game Over", True, WHITE)
            restart_text = font.render("Press R to Restart", True, WHITE)
            score_text = font.render(f"Final Score: {score}", True, WHITE)
            screen.blit(game_over_text, (350, 150))
            screen.blit(restart_text, (350, 200))
            screen.blit(score_text, (350, 250))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        main()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    new_offset = [shape_offset[0] - 1, shape_offset[1]]
                    if not check_collision(board, shape, new_offset):
                        shape_offset[0] -= 1
                elif event.key == pygame.K_RIGHT:
                    new_offset = [shape_offset[0] + 1, shape_offset[1]]
                    if not check_collision(board, shape, new_offset):
                        shape_offset[0] += 1
                elif event.key == pygame.K_UP:
                    new_shape = rotate(shape)
                    if not check_collision(board, new_shape, shape_offset):
                        shape = new_shape
                elif event.key == pygame.K_DOWN:
                    new_offset = [shape_offset[0], shape_offset[1] + 1]
                    if not check_collision(board, shape, new_offset):
                        shape_offset[1] += 1
                elif event.key == pygame.K_SPACE:
                    while not check_collision(board, shape, [shape_offset[0], shape_offset[1] + 1]):
                        shape_offset[1] += 1
                elif event.key == pygame.K_r:
                    main()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        if drop_timer <= 0:
            drop_timer = AUTO_DROP_INTERVAL
            new_offset = [shape_offset[0], shape_offset[1] + 1]
            if not check_collision(board, shape, new_offset):
                shape_offset[1] += 1
            else:
                board = merge_shape(board, shape, shape_offset)
                cleared_lines = 0
                while True:
                    new_board = clear_lines(board)
                    if len(new_board) == len(board):
                        break
                    board = new_board
                    cleared_lines += 1
                score += get_score(cleared_lines)
                lines_cleared += cleared_lines
                shape = next_shape
                shape_color = next_shape_color
                next_shape = random.choice(SHAPES)
                next_shape_color = random.randint(1, len(COLORS) - 1)
                shape = [[shape_color if cell else 0 for cell in row] for row in shape]
                shape_offset = [BOARD_SIZE[0] // 2 - len(shape[0]) // 2, 0]
                if check_collision(board, shape, shape_offset):
                    paused = True

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()