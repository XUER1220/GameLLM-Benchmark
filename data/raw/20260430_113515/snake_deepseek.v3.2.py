import pygame
import random
import sys

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_COLS = 30
GRID_ROWS = 24
CELL_SIZE = 20
GRID_WIDTH = GRID_COLS * CELL_SIZE
GRID_HEIGHT = GRID_ROWS * CELL_SIZE
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_WIDTH) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_HEIGHT) // 2 + 40
FPS = 60
SNAKE_SPEED = 10  # 每秒移动的格子数
INITIAL_SNAKE_LENGTH = 3
FOOD_SCORE = 10
BG_COLOR = (20, 20, 35)
GRID_COLOR = (40, 40, 60)
SNAKE_HEAD_COLOR = (0, 200, 100)
SNAKE_BODY_COLOR = (0, 180, 80)
FOOD_COLOR = (220, 60, 60)
TEXT_COLOR = (240, 240, 240)
GAME_OVER_BG_COLOR = (0, 0, 0, 180)

# 随机种子
random.seed(42)

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)
        self.reset_game()

    def reset_game(self):
        # 蛇的初始位置（网格中心附近）
        start_x = GRID_COLS // 2
        start_y = GRID_ROWS // 2
        self.snake = []
        for i in range(INITIAL_SNAKE_LENGTH):
            self.snake.append([start_x - i, start_y])
        self.direction = (1, 0)  # 向右
        self.next_direction = (1, 0)
        self.score = 0
        self.game_over = False
        self.food = self.generate_food()
        self.move_timer = 0
        self.move_interval = 1000 // SNAKE_SPEED  # 毫秒

    def generate_food(self):
        while True:
            food = [random.randint(0, GRID_COLS - 1),
                    random.randint(0, GRID_ROWS - 1)]
            if food not in self.snake:
                return food

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
                    if event.key == pygame.K_UP and self.direction != (0, 1):
                        self.next_direction = (0, -1)
                    elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                        self.next_direction = (0, 1)
                    elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                        self.next_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                        self.next_direction = (1, 0)

    def update(self, dt):
        if self.game_over:
            return

        # 方向更新
        self.direction = self.next_direction

        # 移动计时器
        self.move_timer += dt
        if self.move_timer >= self.move_interval:
            self.move_timer -= self.move_interval

            # 计算新的头部位置
            head = self.snake[0].copy()
            head[0] += self.direction[0]
            head[1] += self.direction[1]

            # 碰撞检测
            if (head[0] < 0 or head[0] >= GRID_COLS or
                head[1] < 0 or head[1] >= GRID_ROWS or
                head in self.snake):
                self.game_over = True
                return

            # 插入新的头部
            self.snake.insert(0, head)

            # 吃食物检测
            if head == self.food:
                self.score += FOOD_SCORE
                self.food = self.generate_food()
            else:
                self.snake.pop()

    def draw_grid(self):
        # 绘制网格背景
        grid_rect = pygame.Rect(GRID_OFFSET_X, GRID_OFFSET_Y, GRID_WIDTH, GRID_HEIGHT)
        pygame.draw.rect(self.screen, GRID_COLOR, grid_rect)

        # 绘制网格线
        for x in range(GRID_COLS + 1):
            pygame.draw.line(self.screen, BG_COLOR,
                             (GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y),
                             (GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y + GRID_HEIGHT),
                             1)
        for y in range(GRID_ROWS + 1):
            pygame.draw.line(self.screen, BG_COLOR,
                             (GRID_OFFSET_X, GRID_OFFSET_Y + y * CELL_SIZE),
                             (GRID_OFFSET_X + GRID_WIDTH, GRID_OFFSET_Y + y * CELL_SIZE),
                             1)

    def draw_snake(self):
        for i, segment in enumerate(self.snake):
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_BODY_COLOR
            rect = pygame.Rect(
                GRID_OFFSET_X + segment[0] * CELL_SIZE,
                GRID_OFFSET_Y + segment[1] * CELL_SIZE,
                CELL_SIZE, CELL_SIZE
            )
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

    def draw_food(self):
        rect = pygame.Rect(
            GRID_OFFSET_X + self.food[0] * CELL_SIZE,
            GRID_OFFSET_Y + self.food[1] * CELL_SIZE,
            CELL_SIZE, CELL_SIZE
        )
        pygame.draw.rect(self.screen, FOOD_COLOR, rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

    def draw_hud(self):
        # 标题
        title = self.font.render("Snake Easy", True, TEXT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 10))

        # 分数
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (GRID_OFFSET_X, GRID_OFFSET_Y - 40))

        # 操作提示
        controls = self.small_font.render("Arrow Keys: Move | R: Restart | ESC: Exit", True, TEXT_COLOR)
        self.screen.blit(controls, (SCREEN_WIDTH // 2 - controls.get_width() // 2, SCREEN_HEIGHT - 30))

    def draw_game_over(self):
        # 半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(GAME_OVER_BG_COLOR)
        self.screen.blit(overlay, (0, 0))

        # 游戏结束文本
        game_over_text = self.font.render("Game Over", True, (220, 50, 50))
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))

        final_score = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(final_score, (SCREEN_WIDTH // 2 - final_score.get_width() // 2, SCREEN_HEIGHT // 2 - 10))

        restart_text = self.small_font.render("Press R to Restart", True, (100, 200, 255))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))

    def run(self):
        last_time = pygame.time.get_ticks()

        while True:
            current_time = pygame.time.get_ticks()
            dt = current_time - last_time
            last_time = current_time

            self.handle_events()
            self.update(dt)

            # 绘制
            self.screen.fill(BG_COLOR)
            self.draw_grid()
            self.draw_food()
            self.draw_snake()
            self.draw_hud()

            if self.game_over:
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = SnakeGame()
    game.run()