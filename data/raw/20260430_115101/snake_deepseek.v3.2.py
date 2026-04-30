import pygame
import sys
import random

# ========== 全局常量 ==========
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_COLS = 30
GRID_ROWS = 24
CELL_SIZE = 20
GRID_WIDTH = GRID_COLS * CELL_SIZE
GRID_HEIGHT = GRID_ROWS * CELL_SIZE
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_WIDTH) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_HEIGHT) // 2
FPS = 60
SNAKE_SPEED = 10
INITIAL_LENGTH = 3
SNAKE_MOVE_INTERVAL = FPS // SNAKE_SPEED
SCORE_PER_FOOD = 10
SEED = 42

# 颜色
BACKGROUND = (15, 15, 30)
GRID_COLOR = (40, 40, 60)
SNAKE_HEAD_COLOR = (0, 200, 100)
SNAKE_BODY_COLOR = (0, 180, 60)
FOOD_COLOR = (255, 50, 50)
TEXT_COLOR = (240, 240, 240)
GAME_OVER_BG = (0, 0, 0, 180)

# 随机种子
random.seed(SEED)

# ========== 游戏类 ==========
class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 30)
        self.large_font = pygame.font.SysFont(None, 50)
        self.reset_game()

    def reset_game(self):
        self.game_over = False
        self.score = 0
        # 蛇初始位置在网格中心附近，方向向右
        center_x = GRID_COLS // 2
        center_y = GRID_ROWS // 2
        self.snake = [(center_x, center_y),
                      (center_x - 1, center_y),
                      (center_x - 2, center_y)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self.generate_food()
        self.move_counter = 0

    def generate_food(self):
        while True:
            pos = (random.randint(0, GRID_COLS - 1),
                   random.randint(0, GRID_ROWS - 1))
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
                if event.key == pygame.K_r:
                    self.reset_game()
                if not self.game_over:
                    # 方向键控制，不允许直接反向
                    if event.key == pygame.K_UP and self.direction != (0, 1):
                        self.next_direction = (0, -1)
                    elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                        self.next_direction = (0, 1)
                    elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                        self.next_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                        self.next_direction = (1, 0)

    def update(self):
        if self.game_over:
            return
        self.move_counter += 1
        if self.move_counter >= SNAKE_MOVE_INTERVAL:
            self.move_counter = 0
            self.direction = self.next_direction
            head_x, head_y = self.snake[0]
            new_x = head_x + self.direction[0]
            new_y = head_y + self.direction[1]
            new_head = (new_x, new_y)

            # 检查撞墙
            if (new_x < 0 or new_x >= GRID_COLS or
                new_y < 0 or new_y >= GRID_ROWS):
                self.game_over = True
                return

            # 检查撞到自己
            if new_head in self.snake:
                self.game_over = True
                return

            # 移动蛇
            self.snake.insert(0, new_head)

            # 检查吃食物
            if new_head == self.food:
                self.score += SCORE_PER_FOOD
                self.food = self.generate_food()
            else:
                self.snake.pop()

    def draw(self):
        self.screen.fill(BACKGROUND)

        # 绘制网格区域背景
        pygame.draw.rect(self.screen, (30, 30, 50),
                         (GRID_OFFSET_X, GRID_OFFSET_Y,
                          GRID_WIDTH, GRID_HEIGHT))
        # 绘制网格线
        for x in range(GRID_COLS + 1):
            pygame.draw.line(self.screen, GRID_COLOR,
                             (GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y),
                             (GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y + GRID_HEIGHT), 1)
        for y in range(GRID_ROWS + 1):
            pygame.draw.line(self.screen, GRID_COLOR,
                             (GRID_OFFSET_X, GRID_OFFSET_Y + y * CELL_SIZE),
                             (GRID_OFFSET_X + GRID_WIDTH, GRID_OFFSET_Y + y * CELL_SIZE), 1)

        # 绘制食物
        fx, fy = self.food
        pygame.draw.rect(self.screen, FOOD_COLOR,
                         (GRID_OFFSET_X + fx * CELL_SIZE,
                          GRID_OFFSET_Y + fy * CELL_SIZE,
                          CELL_SIZE, CELL_SIZE))

        # 绘制蛇
        for i, (x, y) in enumerate(self.snake):
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_BODY_COLOR
            pygame.draw.rect(self.screen, color,
                             (GRID_OFFSET_X + x * CELL_SIZE,
                              GRID_OFFSET_Y + y * CELL_SIZE,
                              CELL_SIZE, CELL_SIZE))
            # 蛇身体内部稍暗
            if i > 0:
                pygame.draw.rect(self.screen, (color[0]//2, color[1]//2, color[2]//2),
                                 (GRID_OFFSET_X + x * CELL_SIZE + 4,
                                  GRID_OFFSET_Y + y * CELL_SIZE + 4,
                                  CELL_SIZE - 8, CELL_SIZE - 8))

        # 绘制 HUD
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (20, 20))
        title_text = self.font.render("Snake Easy", True, TEXT_COLOR)
        self.screen.blit(title_text, (SCREEN_WIDTH - title_text.get_width() - 20, 20))

        if self.game_over:
            # 半透明覆盖层
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(GAME_OVER_BG)
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.large_font.render("Game Over", True, TEXT_COLOR)
            final_score_text = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            restart_text = self.font.render("Press R to Restart", True, TEXT_COLOR)

            texts = [game_over_text, final_score_text, restart_text]
            total_height = sum(t.get_height() for t in texts) + 20 * (len(texts) - 1)
            y = (SCREEN_HEIGHT - total_height) // 2

            for text in texts:
                x = (SCREEN_WIDTH - text.get_width()) // 2
                self.screen.blit(text, (x, y))
                y += text.get_height() + 20

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = SnakeGame()
    game.run()