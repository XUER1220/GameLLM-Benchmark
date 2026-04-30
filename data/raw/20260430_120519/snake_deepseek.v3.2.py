import pygame
import random
import sys

# ========== 常量定义 ==========
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_COLS = 30
GRID_ROWS = 24
GRID_SIZE = 20
GRID_AREA_WIDTH = GRID_COLS * GRID_SIZE
GRID_AREA_HEIGHT = GRID_ROWS * GRID_SIZE
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_AREA_WIDTH) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_AREA_HEIGHT) // 2
FPS = 60
SPEED = 10  # 每秒移动的网格数
INITIAL_LENGTH = 3
FOOD_VALUE = 10
SEED = 42

# 颜色
COLOR_BG = (15, 15, 25)
COLOR_GRID = (40, 40, 60)
COLOR_SNAKE_HEAD = (50, 200, 100)
COLOR_SNAKE_BODY = (80, 160, 80)
COLOR_FOOD = (220, 60, 60)
COLOR_TEXT = (240, 240, 255)
COLOR_GAME_OVER_BG = (0, 0, 0, 180)

random.seed(SEED)

# ========== 游戏状态类 ==========
class SnakeGame:
    def __init__(self):
        self.reset()

    def reset(self):
        # 蛇身列表，每个元素为 (col, row)，头部在末尾
        self.snake = []
        center_col = GRID_COLS // 2
        center_row = GRID_ROWS // 2
        for i in range(INITIAL_LENGTH):
            self.snake.append((center_col - i, center_row))
        self.direction = (1, 0)   # 向右
        self.next_direction = (1, 0)
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.move_timer = 0.0
        self.move_interval = 1.0 / SPEED

    def generate_food(self):
        while True:
            col = random.randint(0, GRID_COLS - 1)
            row = random.randint(0, GRID_ROWS - 1)
            if (col, row) not in self.snake:
                return (col, row)

    def update(self, dt):
        if self.game_over:
            return

        # 方向更新：防止直接反向
        head_col, head_row = self.snake[-1]
        new_dir = self.next_direction
        current_dir = self.direction
        if (new_dir[0] != -current_dir[0] or new_dir[1] != -current_dir[1]):
            self.direction = new_dir

        self.move_timer += dt
        if self.move_timer >= self.move_interval:
            self.move_timer = 0.0
            # 计算新头部位置
            dcol, drow = self.direction
            head_col, head_row = self.snake[-1]
            new_head = (head_col + dcol, head_row + drow)

            # 检查撞墙
            if not (0 <= new_head[0] < GRID_COLS and 0 <= new_head[1] < GRID_ROWS):
                self.game_over = True
                return

            # 检查撞自己
            if new_head in self.snake:
                self.game_over = True
                return

            # 移动蛇
            self.snake.append(new_head)

            # 检查吃食物
            if new_head == self.food:
                self.score += FOOD_VALUE
                self.food = self.generate_food()
            else:
                self.snake.pop(0)  # 删除尾部

    def draw(self, screen, font):
        # 绘制背景
        screen.fill(COLOR_BG)

        # 绘制网格区域边框和内部网格
        pygame.draw.rect(screen, COLOR_GRID,
                         (GRID_OFFSET_X - 2, GRID_OFFSET_Y - 2,
                          GRID_AREA_WIDTH + 4, GRID_AREA_HEIGHT + 4), 2)
        for x in range(GRID_COLS + 1):
            pygame.draw.line(screen, COLOR_GRID,
                             (GRID_OFFSET_X + x * GRID_SIZE, GRID_OFFSET_Y),
                             (GRID_OFFSET_X + x * GRID_SIZE, GRID_OFFSET_Y + GRID_AREA_HEIGHT),
                             1)
        for y in range(GRID_ROWS + 1):
            pygame.draw.line(screen, COLOR_GRID,
                             (GRID_OFFSET_X, GRID_OFFSET_Y + y * GRID_SIZE),
                             (GRID_OFFSET_X + GRID_AREA_WIDTH, GRID_OFFSET_Y + y * GRID_SIZE),
                             1)

        # 绘制食物
        fx, fy = self.food
        food_rect = pygame.Rect(
            GRID_OFFSET_X + fx * GRID_SIZE,
            GRID_OFFSET_Y + fy * GRID_SIZE,
            GRID_SIZE, GRID_SIZE
        )
        pygame.draw.rect(screen, COLOR_FOOD, food_rect)

        # 绘制蛇
        for idx, (col, row) in enumerate(self.snake):
            rect = pygame.Rect(
                GRID_OFFSET_X + col * GRID_SIZE,
                GRID_OFFSET_Y + row * GRID_SIZE,
                GRID_SIZE, GRID_SIZE
            )
            color = COLOR_SNAKE_HEAD if idx == len(self.snake) - 1 else COLOR_SNAKE_BODY
            pygame.draw.rect(screen, color, rect)
            # 身体格子稍微内缩一点
            if idx < len(self.snake) - 1:
                inner = rect.inflate(-4, -4)
                pygame.draw.rect(screen, COLOR_SNAKE_BODY, inner, border_radius=2)

        # 绘制分数和标题
        title_surf = font.render("Snake Easy", True, COLOR_TEXT)
        score_surf = font.render(f"Score: {self.score}", True, COLOR_TEXT)
        screen.blit(title_surf, (GRID_OFFSET_X, GRID_OFFSET_Y - 40))
        screen.blit(score_surf, (GRID_OFFSET_X, GRID_OFFSET_Y - 70))

        # 游戏结束提示
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(COLOR_GAME_OVER_BG)
            screen.blit(overlay, (0, 0))

            go_text = font.render("Game Over", True, COLOR_TEXT)
            final_score = font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
            restart_text = font.render("Press R to Restart", True, COLOR_TEXT)

            screen.blit(go_text, go_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50)))
            screen.blit(final_score, final_score.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
            screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)))

# ========== 主程序 ==========
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake Easy")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    game = SnakeGame()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # 转换为秒

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game.reset()
                if not game.game_over:
                    if event.key == pygame.K_UP:
                        game.next_direction = (0, -1)
                    elif event.key == pygame.K_DOWN:
                        game.next_direction = (0, 1)
                    elif event.key == pygame.K_LEFT:
                        game.next_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        game.next_direction = (1, 0)

        # 游戏逻辑更新
        game.update(dt)

        # 绘制
        game.draw(screen, font)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()