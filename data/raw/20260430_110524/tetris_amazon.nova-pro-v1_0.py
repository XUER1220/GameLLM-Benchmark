import pygame
import random
import sys

pygame.init()
pygame.key.set_repeat(500, 50)
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BOARD_WIDTH, BOARD_HEIGHT = 10, 20
CELL_SIZE = 24
BOARD_START_X = (SCREEN_WIDTH - BOARD_WIDTH * CELL_SIZE) // 2
BOARD_START_Y = (SCREEN_HEIGHT - BOARD_HEIGHT * CELL_SIZE) // 2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255), (255, 255, 0), (128, 0, 128), (0, 255, 0), (255, 0, 0),
    (0, 0, 255), (255, 165, 0)
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

SCORE_LINES = {1: 100, 2: 300, 3: 500, 4: 800}

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris Medium')
        self.clock = pygame.time.Clock()
        self.board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.lines = 0
        self.game_over = False
        self.auto_drop_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.auto_drop_event, 500)

    def new_piece(self):
        piece = random.choice(SHAPES)
        piece_color = random.choice(COLORS)
        return {
           'shape': piece,
            'color': piece_color,
            'x': BOARD_WIDTH // 2 - len(piece[0]) // 2,
            'y': 0
        }

    def rotate(self, piece):
        rotated_piece = list(zip(*piece[::-1]))
        return {
           'shape': rotated_piece,
            'color': piece['color'],
            'x': piece['x'],
            'y': piece['y']
        }

    def check_collision(self, piece, offset=(0, 0)):
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    nx, ny = piece['x'] + x + offset[0], piece['y'] + y + offset[1]
                    if (nx < 0 or nx >= BOARD_WIDTH or ny >= BOARD_HEIGHT or
                            (ny >= 0 and self.board[ny][nx])):
                        return True
        return False

    def lock_piece(self, piece):
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    self.board[piece['y'] + y][piece['x'] + x] = piece['color']
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        if self.check_collision(self.current_piece):
            self.game_over = True

    def clear_lines(self):
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        lines_cleared = len(self.board) - len(new_board)
        self.lines += lines_cleared
        self.score += SCORE_LINES.get(lines_cleared, 0)
        self.board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT - len(new_board))] + new_board

    def draw_board(self):
        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, cell, (BOARD_START_X + x * CELL_SIZE, BOARD_START_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def draw_piece(self, piece):
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, piece['color'], (BOARD_START_X + (piece['x'] + x) * CELL_SIZE, BOARD_START_Y + (piece['y'] + y) * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def draw_hud(self):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        lines_text = font.render(f'Lines: {self.lines}', True, WHITE)
        self.screen.blit(score_text, (BOARD_START_X + BOARD_WIDTH * CELL_SIZE + 20, BOARD_START_Y))
        self.screen.blit(lines_text, (BOARD_START_X + BOARD_WIDTH * CELL_SIZE + 20, BOARD_START_Y + 40))

    def game_over_screen(self):
        font = pygame.font.Font(None, 74)
        text_surface = font.render('Game Over', True, WHITE)
        self.screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        font = pygame.font.Font(None, 36)
        score_surface = font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_surface, (SCREEN_WIDTH // 2 - score_surface.get_width() // 2, SCREEN_HEIGHT // 2))
        restart_surface = font.render('Press R to Restart', True, WHITE)
        self.screen.blit(restart_surface, (SCREEN_WIDTH // 2 - restart_surface.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

    def run(self):
        while True:
            self.screen.fill(BLACK)
            self.draw_board()
            self.draw_piece(self.current_piece)
            self.draw_hud()

            if self.game_over:
                self.game_over_screen()
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.__init__()
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if not self.check_collision(self.current_piece, (-1, 0)):
                            self.current_piece['x'] -= 1
                    elif event.key == pygame.K_RIGHT:
                        if not self.check_collision(self.current_piece, (1, 0)):
                            self.current_piece['x'] += 1
                    elif event.key == pygame.K_UP:
                        rotated_piece = self.rotate(self.current_piece)
                        if not self.check_collision(rotated_piece):
                            self.current_piece = rotated_piece
                    elif event.key == pygame.K_DOWN:
                        if not self.check_collision(self.current_piece, (0, 1)):
                            self.current_piece['y'] += 1
                    elif event.key == pygame.K_SPACE:
                        while not self.check_collision(self.current_piece, (0, 1)):
                            self.current_piece['y'] += 1
                        self.current_piece['y'] -= 1
                        self.lock_piece(self.current_piece)
                elif event.type == self.auto_drop_event:
                    if not self.check_collision(self.current_piece, (0, 1)):
                        self.current_piece['y'] += 1
                    else:
                        self.lock_piece(self.current_piece)

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == '__main__':
    game = Tetris()
    game.run()