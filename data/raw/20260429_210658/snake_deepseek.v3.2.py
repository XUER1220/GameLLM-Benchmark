import pygame
import sys
import random

# 初始化 Pygame
pygame.init()

# 随机种子
random.seed(42)

# 窗口常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 网格常量
GRID_CELL_SIZE = 20
GRID_COLS = 30
GRID_ROWS = 24
GRID_WIDTH = GRID_COLS * GRID_CELL_SIZE  # 600
GRID_HEIGHT = GRID_ROWS * GRID_CELL_SIZE  # 480
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_WIDTH) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_HEIGHT) // 2 + 40  # 下移一点给 HUD 腾空间

# 颜色常量
COLOR_BG = (20, 20, 30)
COLOR_GRID = (40, 40, 60)
COLOR_HUD_TEXT = (200, 200, 220)
COLOR_SNAKE_HEAD = (70, 200, 70)
COLOR_SNAKE_BODY = (100, 230, 100)
COLOR_FOOD = (230, 70, 70)
COLOR_GAME_OVER_BG = (0, 0, 0, 180)  # 半透明黑色
COLOR_GAME_OVER_TEXT = (255, 100, 100)

# 游戏常量
SNAKE_INIT_LENGTH = 3
SNAKE_SPEED = 10  # 每秒移动的网格数
FOOD_SCORE = 10

# 方向向量
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)
        self.reset_game()

    def reset_game(self):
        # 蛇初始位置在中心偏左
        start_col = GRID_COLS // 2 - SNAKE_INIT_LENGTH
        start_row = GRID_ROWS // 2
        self.snake = [(start_col + i, start_row) for i in range(SNAKE_INIT_LENGTH)]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.score = 0
        self.game_over = False
        self.food = self.generate_food()
        self.move_timer = 0.0
        self.move_interval = 1.0 / SNAKE_SPEED

    def generate_food(self):
        while True:
            pos = (random.randint(0, GRID_COLS-1), random.randint(0, GRID_ROWS-1))
            if pos not in self.snake:
                return pos

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    self.reset_game()
                elif not self.game_over:
                    if event.key == pygame.K_UP and self.direction != DOWN:
                        self.next_direction = UP
                    elif event.key == pygame.K_DOWN and self.direction != UP:
                        self.next_direction = DOWN
                    elif event.key == pygame.K_LEFT and self.direction != RIGHT:
                        self.next_direction = LEFT
                    elif event.key == pygame.K_RIGHT and self.direction != LEFT:
                        self.next_direction = RIGHT

    def update(self, dt):
        if self.game_over:
            return
        self.direction = self.next_direction
        self.move_timer += dt
        if self.move_timer >= self.move_interval:
            self.move_timer = 0.0
            head = self.snake[0]
            new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

            # 撞墙检测
            if not (0 <= new_head[0] < GRID_COLS and 0 <= new_head[1] < GRID_ROWS):
                self.game_over = True
                return

            # 撞自己检测
            if new_head in self.snake:
                self.game_over = True
                return

            self.snake.insert(0, new_head)

            # 吃食物检测
            if new_head == self.food:
                self.score += FOOD_SCORE
                self.food = self.generate_food()
            else:
                self.snake.pop()

    def draw_grid(self):
        grid_rect = pygame.Rect(GRID_OFFSET_X, GRID_OFFSET_Y, GRID_WIDTH, GRID_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_GRID, grid_rect)
        # 画网格线
        for x in range(GRID_COLS + 1):
            pygame.draw.line(self.screen, COLOR_BG,
                             (GRID_OFFSET_X + x * GRID_CELL_SIZE, GRID_OFFSET_Y),
                             (GRID_OFFSET_X + x * GRID_CELL_SIZE, GRID_OFFSET_Y + GRID_HEIGHT),
                             1)
        for y in range(GRID_ROWS + 1):
            pygame.draw.line(self.screen, COLOR_BG,
                             (GRID_OFFSET_X, GRID_OFFSET_Y + y * GRID_CELL_SIZE),
                             (GRID_OFFSET_X + GRID_WIDTH, GRID_OFFSET_Y + y * GRID_CELL_SIZE),
                             1)

    def draw_snake(self):
        for i, (col, row) in enumerate(self.snake):
            color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE_BODY
            rect = pygame.Rect(
                GRID_OFFSET_X + col * GRID_CELL_SIZE,
                GRID_OFFSET_Y + row * GRID_CELL_SIZE,
                GRID_CELL_SIZE, GRID_CELL_SIZE
            )
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, COLOR_BG, rect, 1)

    def draw_food(self):
        rect = pygame.Rect(
            GRID_OFFSET_X + self.food[0] * GRID_CELL_SIZE,
            GRID_OFFSET_Y + self.food[1] * GRID_CELL_SIZE,
            GRID_CELL_SIZE, GRID_CELL_SIZE
        )
        pygame.draw.rect(self.screen, COLOR_FOOD, rect)
        pygame.draw.rect(self.screen, COLOR_BG, rect, 1)

    def draw_hud(self):
        title = self.font.render("Snake Easy", True, COLOR_HUD_TEXT)
        self.screen.blit(title, (20, 10))
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_HUD_TEXT)
        self.screen.blit(score_text, (SCREEN_WIDTH - 200, 10))

    def draw_game_over(self):
        # 半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLOR_GAME_OVER_BG)
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("Game Over", True, COLOR_GAME_OVER_TEXT)
        final_score_text = self.font.render(f"Final Score: {self.score}", True, COLOR_GAME_OVER_TEXT)
        restart_text = self.small_font.render("Press R to Restart", True, COLOR_GAME_OVER_TEXT)

        self.screen.blit(game_over_text,
                         (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
        self.screen.blit(final_score_text,
                         (SCREEN_WIDTH//2 - final_score_text.get_width()//2, SCREEN_HEIGHT//2 - 10))
        self.screen.blit(restart_text,
                         (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 40))

    def draw(self):
        self.screen.fill(COLOR_BG)
        self.draw_grid()
        self.draw_snake()
        self.draw_food()
        self.draw_hud()
        if self.game_over:
            self.draw_game_over()
        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()