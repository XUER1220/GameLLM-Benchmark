import pygame
import sys
import random

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_WIDTH, GRID_HEIGHT = 10, 20
CELL_SIZE = 24
GRID_OFFSET_X, GRID_OFFSET_Y = 100, 50
HUD_OFFSET_X = GRID_OFFSET_X + GRID_WIDTH * CELL_SIZE + 20
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

SHAPE_COLORS = [COLORS[i] for i in range(len(SHAPES))]

score_table = {1: 100, 2: 300, 3: 500, 4: 800}

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        self.grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.current_shape = None
        self.current_shape_pos = [0, 0]
        self.next_shape = None
        self.drop_speed = 500
        self.last_drop_time = 0
        self.init_game()

    def init_game(self):
        self.grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.current_shape = self.get_next_shape()
        self.current_shape_pos = [0, GRID_WIDTH // 2 - len(self.current_shape[0]) // 2]
        self.next_shape = self.get_next_shape()

    def get_next_shape(self):
        shape = random.choice(SHAPES)
        return shape

    def rotate_shape(self, shape):
        return [[shape[y][x] for y in range(len(shape))] for x in range(len(shape[0]) - 1, -1, -1)]

    def check_collision(self, shape, shape_pos):
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    gx, gy = shape_pos[1] + x, shape_pos[0] + y
                    if gx < 0 or gx >= GRID_WIDTH or gy >= GRID_HEIGHT or self.grid[gy][gx]:
                        return True
        return False

    def merge_shape(self, shape, shape_pos):
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[shape_pos[0] + y][shape_pos[1] + x] = cell

    def clear_lines(self):
        lines_to_clear = [idx for idx, row in enumerate(self.grid) if 0 not in row]
        for line in lines_to_clear:
            del self.grid[line]
            self.grid.insert(0, [0] * GRID_WIDTH)
            self.score += score_table[len(lines_to_clear)]
            self.lines_cleared += 1

    def game_over_check(self):
        if self.check_collision(self.current_shape, self.current_shape_pos):
            self.game_over = True

    def draw_grid(self):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, SHAPE_COLORS[cell - 1], 
                                      (GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def draw_shape(self, shape, shape_pos):
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, SHAPE_COLORS[self.current_shape.index(row)], 
                                     (GRID_OFFSET_X + (shape_pos[1] + x) * CELL_SIZE, 
                                      GRID_OFFSET_Y + (shape_pos[0] + y) * CELL_SIZE, 
                                      CELL_SIZE, CELL_SIZE))

    def draw_hud(self):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        lines_text = font.render(f'Lines: {self.lines_cleared}', True, WHITE)
        self.screen.blit(score_text, (HUD_OFFSET_X, GRID_OFFSET_Y))
        self.screen.blit(lines_text, (HUD_OFFSET_X, GRID_OFFSET_Y + 30))
        
        if self.game_over:
            game_over_text = font.render('Game Over', True, WHITE)
            restart_text = font.render('Press R to Restart', True, WHITE)
            self.screen.blit(game_over_text, (HUD_OFFSET_X, GRID_OFFSET_Y + 60))
            self.screen.blit(restart_text, (HUD_OFFSET_X, GRID_OFFSET_Y + 100))

    def run(self):
        while True:
            current_time = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_r and self.game_over:
                        self.init_game()
                    elif not self.game_over:
                        if event.key == pygame.K_LEFT:
                            self.move_shape([0, -1])
                        elif event.key == pygame.K_RIGHT:
                            self.move_shape([0, 1])
                        elif event.key == pygame.K_UP:
                            self.rotate_current_shape()
                        elif event.key == pygame.K_DOWN:
                            self.move_shape([1, 0])
                        elif event.key == pygame.K_SPACE:
                            while not self.check_collision(self.current_shape, [self.current_shape_pos[0] + 1, self.current_shape_pos[1]]):
                                self.current_shape_pos[0] += 1
                            self.merge_shape(self.current_shape, self.current_shape_pos)
                            self.clear_lines()
                            self.game_over_check()
                            if not self.game_over:
                                self.current_shape = self.next_shape
                                self.current_shape_pos = [0, GRID_WIDTH // 2 - len(self.current_shape[0]) // 2]
                                self.next_shape = self.get_next_shape()

            if not self.game_over and current_time - self.last_drop_time > self.drop_speed:
                self.move_shape([1, 0])
                self.last_drop_time = current_time

            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_shape(self.current_shape, self.current_shape_pos)
            self.draw_hud()
            pygame.display.flip()
            self.clock.tick(FPS)

    def move_shape(self, direction):
        new_pos = [self.current_shape_pos[0] + direction[0], self.current_shape_pos[1] + direction[1]]
        if not self.check_collision(self.current_shape, new_pos):
            self.current_shape_pos = new_pos
        else:
            if direction[0] > 0:
                self.merge_shape(self.current_shape, self.current_shape_pos)
                self.clear_lines()
                self.game_over_check()
                if not self.game_over:
                    self.current_shape = self.next_shape
                    self.current_shape_pos = [0, GRID_WIDTH // 2 - len(self.current_shape[0]) // 2]
                    self.next_shape = self.get_next_shape()

    def rotate_current_shape(self):
        rotated_shape = self.rotate_shape(self.current_shape)
        if not self.check_collision(rotated_shape, self.current_shape_pos):
            self.current_shape = rotated_shape

game = Tetris()
game.run()