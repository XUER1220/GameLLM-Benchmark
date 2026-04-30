import pygame
import random
import sys

pygame.init()

# 固定参数
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_COLS = 30
GRID_ROWS = 24
CELL_SIZE = 20
GRID_WIDTH = GRID_COLS * CELL_SIZE
GRID_HEIGHT = GRID_ROWS * CELL_SIZE
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_WIDTH) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_HEIGHT) // 2 + 30
FPS = 60
INITIAL_LENGTH = 3
SNAKE_SPEED = 10  # 每秒移动的网格数
SCORE_PER_FOOD = 10
SEED = 42

# 颜色
BACKGROUND_COLOR = (20, 20, 40)
GRID_COLOR = (40, 40, 60)
HUD_TEXT_COLOR = (220, 220, 220)
SNAKE_HEAD_COLOR = (0, 200, 100)
SNAKE_BODY_COLOR = (0, 180, 80)
FOOD_COLOR = (220, 50, 50)
GAME_OVER_BG_COLOR = (0, 0, 0, 180)  # 半透明黑色
GAME_OVER_TEXT_COLOR = (255, 100, 100)

# 方向
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

random.seed(SEED)

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.reset_game()

    def reset_game(self):
        self.snake = []
        start_x = GRID_COLS // 2
        start_y = GRID_ROWS // 2
        for i in range(INITIAL_LENGTH):
            self.snake.append((start_x - i, start_y))
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.score = 0
        self.game_over = False
        self.food = self.generate_food()
        self.move_timer = 0.0

    def generate_food(self):
        while True:
            food_pos = (random.randint(0, GRID_COLS - 1), random.randint(0, GRID_ROWS - 1))
            if food_pos not in self.snake:
                return food_pos

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r and self.game_over:
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
        move_interval = 1.0 / SNAKE_SPEED
        if self.move_timer >= move_interval:
            self.move_timer -= move_interval
            head = self.snake[0]
            new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

            # 检查撞墙
            if (new_head[0] < 0 or new_head[0] >= GRID_COLS or
                new_head[1] < 0 or new_head[1] >= GRID_ROWS):
                self.game_over = True
                return

            # 检查撞自己
            if new_head in self.snake:
                self.game_over = True
                return

            self.snake.insert(0, new_head)

            # 检查吃食物
            if new_head == self.food:
                self.score += SCORE_PER_FOOD
                self.food = self.generate_food()
            else:
                self.snake.pop()

    def draw_grid(self):
        for x in range(GRID_COLS + 1):
            pygame.draw.line(self.screen, GRID_COLOR,
                             (GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y),
                             (GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y + GRID_HEIGHT),
                             1)
        for y in range(GRID_ROWS + 1):
            pygame.draw.line(self.screen, GRID_COLOR,
                             (GRID_OFFSET_X, GRID_OFFSET_Y + y * CELL_SIZE),
                             (GRID_OFFSET_X + GRID_WIDTH, GRID_OFFSET_Y + y * CELL_SIZE),
                             1)

    def draw_snake(self):
        for i, (x, y) in enumerate(self.snake):
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_BODY_COLOR
            rect = pygame.Rect(GRID_OFFSET_X + x * CELL_SIZE,
                               GRID_OFFSET_Y + y * CELL_SIZE,
                               CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

    def draw_food(self):
        rect = pygame.Rect(GRID_OFFSET_X + self.food[0] * CELL_SIZE,
                           GRID_OFFSET_Y + self.food[1] * CELL_SIZE,
                           CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, FOOD_COLOR, rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

    def draw_hud(self):
        title = self.font.render("Snake Easy", True, HUD_TEXT_COLOR)
        score_text = self.font.render(f"Score: {self.score}", True, HUD_TEXT_COLOR)
        self.screen.blit(title, (GRID_OFFSET_X, 10))
        self.screen.blit(score_text, (SCREEN_WIDTH - GRID_OFFSET_X - score_text.get_width(), 10))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(GAME_OVER_BG_COLOR)
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("GAME OVER", True, GAME_OVER_TEXT_COLOR)
        score_text = self.font.render(f"Final Score: {self.score}", True, HUD_TEXT_COLOR)
        restart_text = self.small_font.render("Press R to Restart", True, HUD_TEXT_COLOR)

        self.screen.blit(game_over_text,
                         (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                          SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(score_text,
                         (SCREEN_WIDTH // 2 - score_text.get_width() // 2,
                          SCREEN_HEIGHT // 2))
        self.screen.blit(restart_text,
                         (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                          SCREEN_HEIGHT // 2 + 50))

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
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