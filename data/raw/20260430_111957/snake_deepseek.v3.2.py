import pygame
import random
import sys

# 固定初始化
pygame.init()
random.seed(42)

# ------------------ 常量定义 ------------------
# 窗口和帧率
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 网格参数
GRID_COLS = 30
GRID_ROWS = 24
CELL_SIZE = 20
GRID_WIDTH = GRID_COLS * CELL_SIZE
GRID_HEIGHT = GRID_ROWS * CELL_SIZE
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_WIDTH) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_HEIGHT) // 2 + 30

# 游戏参数
INIT_SNAKE_LENGTH = 3
SNAKE_SPEED_PER_SECOND = 10
SCORE_PER_FOOD = 10
MOVE_INTERVAL = 1000 // SNAKE_SPEED_PER_SECOND  # 毫秒

# 颜色定义
COLOR_BG = (20, 20, 20)
COLOR_GRID = (40, 40, 40)
COLOR_SNAKE_HEAD = (50, 200, 100)
COLOR_SNAKE_BODY = (100, 200, 150)
COLOR_FOOD = (200, 50, 50)
COLOR_TEXT = (240, 240, 240)
COLOR_GAME_OVER_BG = (0, 0, 0, 180)

# 方向
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# ------------------ 游戏类 ------------------
class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont(None, 24)
        self.reset_game()

    def reset_game(self):
        self.score = 0
        self.game_over = False
        self.snake = []
        center_x = GRID_COLS // 2
        center_y = GRID_ROWS // 2
        for i in range(INIT_SNAKE_LENGTH):
            self.snake.append((center_x - i, center_y))
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.food = self.generate_food()
        self.last_move_time = pygame.time.get_ticks()
        self.move_timer = 0

    def generate_food(self):
        while True:
            pos = (random.randint(0, GRID_COLS - 1), random.randint(0, GRID_ROWS - 1))
            if pos not in self.snake:
                return pos

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    self.reset_game()
                if not self.game_over:
                    if event.key == pygame.K_UP and self.direction != DOWN:
                        self.next_direction = UP
                    elif event.key == pygame.K_DOWN and self.direction != UP:
                        self.next_direction = DOWN
                    elif event.key == pygame.K_LEFT and self.direction != RIGHT:
                        self.next_direction = LEFT
                    elif event.key == pygame.K_RIGHT and self.direction != LEFT:
                        self.next_direction = RIGHT

    def update(self):
        if self.game_over:
            return
        current_time = pygame.time.get_ticks()
        self.move_timer += current_time - self.last_move_time
        self.last_move_time = current_time
        if self.move_timer >= MOVE_INTERVAL:
            self.move_timer = 0
            self.direction = self.next_direction
            head = self.snake[0]
            new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
            # 检查碰撞
            if (new_head[0] < 0 or new_head[0] >= GRID_COLS or
                new_head[1] < 0 or new_head[1] >= GRID_ROWS or
                new_head in self.snake):
                self.game_over = True
                return
            self.snake.insert(0, new_head)
            # 检查食物
            if new_head == self.food:
                self.score += SCORE_PER_FOOD
                self.food = self.generate_food()
            else:
                self.snake.pop()

    def draw_grid(self):
        for x in range(GRID_COLS + 1):
            px = GRID_OFFSET_X + x * CELL_SIZE
            pygame.draw.line(self.screen, COLOR_GRID,
                             (px, GRID_OFFSET_Y),
                             (px, GRID_OFFSET_Y + GRID_HEIGHT))
        for y in range(GRID_ROWS + 1):
            py = GRID_OFFSET_Y + y * CELL_SIZE
            pygame.draw.line(self.screen, COLOR_GRID,
                             (GRID_OFFSET_X, py),
                             (GRID_OFFSET_X + GRID_WIDTH, py))

    def draw(self):
        self.screen.fill(COLOR_BG)
        # HUD
        title = self.font.render("Snake Easy", True, COLOR_TEXT)
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(title, (20, 10))
        self.screen.blit(score_text, (SCREEN_WIDTH - 150, 10))
        # 网格区域
        grid_rect = pygame.Rect(GRID_OFFSET_X, GRID_OFFSET_Y, GRID_WIDTH, GRID_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_BG, grid_rect)
        self.draw_grid()
        # 蛇
        for i, (x, y) in enumerate(self.snake):
            rect = pygame.Rect(
                GRID_OFFSET_X + x * CELL_SIZE,
                GRID_OFFSET_Y + y * CELL_SIZE,
                CELL_SIZE, CELL_SIZE)
            color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE_BODY
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, COLOR_GRID, rect, 1)
        # 食物
        food_rect = pygame.Rect(
            GRID_OFFSET_X + self.food[0] * CELL_SIZE,
            GRID_OFFSET_Y + self.food[1] * CELL_SIZE,
            CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, COLOR_FOOD, food_rect)
        pygame.draw.rect(self.screen, COLOR_GRID, food_rect, 1)
        # 游戏结束
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(COLOR_GAME_OVER_BG)
            self.screen.blit(overlay, (0, 0))
            game_over_text = self.font.render("Game Over", True, COLOR_TEXT)
            final_score = self.font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
            restart_text = self.small_font.render("Press R to Restart", True, COLOR_TEXT)
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(final_score, (SCREEN_WIDTH // 2 - final_score.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

# ------------------ 主程序 ------------------
if __name__ == "__main__":
    game = SnakeGame()
    game.run()