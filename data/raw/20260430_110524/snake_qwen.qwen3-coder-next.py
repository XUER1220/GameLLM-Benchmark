import pygame
import random

# 固定常量
WIDTH, HEIGHT = 800, 600
GRID_COLS, GRID_ROWS = 30, 24
GRID_SIZE = 20
GAME_WIDTH, GAME_HEIGHT = GRID_COLS * GRID_SIZE, GRID_ROWS * GRID_SIZE
FPS = 60
SNAKE_SPEED = 10  # cells per second
SCORE_PER_FOOD = 10
RANDOM_SEED = 42

# 颜色定义
BACKGROUND_COLOR = (40, 40, 40)
GRID_COLOR = (60, 60, 60)
TEXT_COLOR = (255, 255, 255)
SNAKE_HEAD_COLOR = (0, 200, 0)
SNAKE_BODY_COLOR = (0, 150, 0)
FOOD_COLOR = (255, 50, 50)
HUD_COLOR = (100, 200, 100)

# 初始化
random.seed(RANDOM_SEED)
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)


def get_center_grid_pos():
    start_x = (GRID_COLS - 3) // 2
    start_y = (GRID_ROWS - 1) // 2
    return [(start_x + i, start_y) for i in range(3)]


class SnakeGame:
    def __init__(self):
        self.reset()

    def reset(self):
        # 初始化蛇位置（3格长，向右移动）
        self.snake = get_center_grid_pos()
        self.direction = (1, 0)  # 正在向右
        self.next_direction = (1, 0)
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.time_accumulator = 0.0

    def generate_food(self):
        food_pos = None
        while food_pos is None or food_pos in self.snake:
            x = random.randint(0, GRID_COLS - 1)
            y = random.randint(0, GRID_ROWS - 1)
            food_pos = (x, y)
        return food_pos

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r and self.game_over:
                    self.reset()
                elif event.key == pygame.K_UP:
                    if self.direction != (0, 1):
                        self.next_direction = (0, -1)
                elif event.key == pygame.K_DOWN:
                    if self.direction != (0, -1):
                        self.next_direction = (0, 1)
                elif event.key == pygame.K_LEFT:
                    if self.direction != (1, 0):
                        self.next_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT:
                    if self.direction != (-1, 0):
                        self.next_direction = (1, 0)
        return True

    def update(self, dt):
        if self.game_over:
            return

        self.time_accumulator += dt
        move_interval = 1.0 / SNAKE_SPEED

        # 更新方向（每个帧只更新一次）
        if self.time_accumulator >= move_interval:
            self.direction = self.next_direction
            self.time_accumulator -= move_interval

        # 计算新头部位置
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # 撞墙检测
        if (new_head[0] < 0 or new_head[0] >= GRID_COLS or
                new_head[1] < 0 or new_head[1] >= GRID_ROWS):
            self.game_over = True
            return

        # 撞自己检测（不包括尾巴，因为尾巴即将移动）
        if new_head in self.snake[:-1]:
            self.game_over = True
            return

        # 移动蛇
        self.snake.insert(0, new_head)

        # 吃食物检测
        if new_head == self.food:
            self.score += SCORE_PER_FOOD
            self.food = self.generate_food()
        else:
            self.snake.pop()

    def draw(self):
        # 清屏
        screen.fill(BACKGROUND_COLOR)

        # 绘制网格区域（600x480），居中
        game_rect = pygame.Rect((WIDTH - GAME_WIDTH) // 2, (HEIGHT - GAME_HEIGHT) // 2,
                                 GAME_WIDTH, GAME_HEIGHT)
        pygame.draw.rect(screen, (0, 0, 0), game_rect)

        # 绘制网格线
        for x in range(GRID_COLS + 1):
            start_x = game_rect.left + x * GRID_SIZE
            pygame.draw.line(screen, GRID_COLOR, (start_x, game_rect.top),
                             (start_x, game_rect.bottom), 1)
        for y in range(GRID_ROWS + 1):
            start_y = game_rect.top + y * GRID_SIZE
            pygame.draw.line(screen, GRID_COLOR, (game_rect.left, start_y),
                             (game_rect.right, start_y), 1)

        # 绘制食物（单个网格）
        fx, fy = self.food
        food_rect = pygame.Rect(game_rect.left + fx * GRID_SIZE + 1,
                                game_rect.top + fy * GRID_SIZE + 1,
                                GRID_SIZE - 2, GRID_SIZE - 2)
        pygame.draw.rect(screen, FOOD_COLOR, food_rect)

        # 绘制蛇
        for i, (sx, sy) in enumerate(self.snake):
            rect = pygame.Rect(game_rect.left + sx * GRID_SIZE + 1,
                               game_rect.top + sy * GRID_SIZE + 1,
                               GRID_SIZE - 2, GRID_SIZE - 2)
            if i == 0:
                pygame.draw.rect(screen, SNAKE_HEAD_COLOR, rect)
            else:
                pygame.draw.rect(screen, SNAKE_BODY_COLOR, rect)

        # HUD（标题、分数、游戏结束提示）
        title_text = font.render("Snake Easy", True, HUD_COLOR)
        screen.blit(title_text, (20, 20))

        score_text = font.render(f"Score: {self.score}", True, TEXT_COLOR)
        screen.blit(score_text, (20, 60))

        if self.game_over:
            # 居中绘制 Game Over 和重新开始提示
            game_over_text = font.render("Game Over", True, (255, 100, 100))
            score_end_text = font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            restart_text = small_font.render("Press R to Restart", True, TEXT_COLOR)

            game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            score_end_rect = score_end_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

            screen.blit(game_over_text, game_over_rect)
            screen.blit(score_end_text, score_end_rect)
            screen.blit(restart_text, restart_rect)

    def run(self):
        running = True
        while running:
            dt = clock.tick(FPS) / 1000.0  # 秒为单位

            running = self.handle_input()

            self.update(dt)
            self.draw()
            pygame.display.flip()


if __name__ == "__main__":
    game = SnakeGame()
    game.run()
    pygame.quit()