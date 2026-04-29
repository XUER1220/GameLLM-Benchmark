import pygame
import random
import sys

# 固定常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_COLS = 30
GRID_ROWS = 24
GRID_CELL_SIZE = 20
GRID_AREA_WIDTH = GRID_COLS * GRID_CELL_SIZE
GRID_AREA_HEIGHT = GRID_ROWS * GRID_CELL_SIZE
GRID_ORIGIN_X = (SCREEN_WIDTH - GRID_AREA_WIDTH) // 2
GRID_ORIGIN_Y = (SCREEN_HEIGHT - GRID_AREA_HEIGHT) // 2
FPS = 60
SNAKE_SPEED = 10  # 每秒移动10格
INITIAL_SNAKE_LENGTH = 3
FOOD_SCORE = 10
RANDOM_SEED = 42

# 颜色
BACKGROUND_COLOR = (20, 20, 40)
GRID_LINE_COLOR = (40, 40, 70)
GRID_BACKGROUND_COLOR = (30, 30, 60)
SNAKE_HEAD_COLOR = (0, 200, 0)
SNAKE_BODY_COLOR = (0, 180, 0)
FOOD_COLOR = (255, 50, 50)
TEXT_COLOR = (255, 255, 255)
GAME_OVER_BG_COLOR = (0, 0, 0, 180)

# 初始化随机种子
random.seed(RANDOM_SEED)


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        mid_x = GRID_COLS // 2
        mid_y = GRID_ROWS // 2
        self.body = [(mid_x - i, mid_y) for i in range(INITIAL_SNAKE_LENGTH)]
        self.direction = (1, 0)  # 初始向右
        self.next_direction = (1, 0)
        self.grow = False

    def change_direction(self, dx, dy):
        # 不允许直接反向
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.next_direction = (dx, dy)

    def move(self):
        self.direction = self.next_direction
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def check_collision(self):
        head = self.body[0]
        # 撞墙
        if head[0] < 0 or head[0] >= GRID_COLS or head[1] < 0 or head[1] >= GRID_ROWS:
            return True
        # 撞自己
        if head in self.body[1:]:
            return True
        return False

    def check_eat(self, food_pos):
        if self.body[0] == food_pos:
            self.grow = True
            return True
        return False

    def in_body(self, pos):
        return pos in self.body


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)
        self.snake = Snake()
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.move_timer = 0
        self.move_interval = 1000 // SNAKE_SPEED  # 毫秒

    def generate_food(self):
        while True:
            pos = (random.randint(0, GRID_COLS - 1), random.randint(0, GRID_ROWS - 1))
            if not self.snake.in_body(pos):
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
                if self.game_over and event.key == pygame.K_r:
                    self.reset_game()
                if not self.game_over:
                    if event.key == pygame.K_UP:
                        self.snake.change_direction(0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction(0, 1)
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction(1, 0)

    def reset_game(self):
        self.snake.reset()
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.move_timer = 0

    def update(self, dt):
        if self.game_over:
            return
        self.move_timer += dt
        if self.move_timer >= self.move_interval:
            self.move_timer = 0
            self.snake.move()
            if self.snake.check_eat(self.food):
                self.score += FOOD_SCORE
                self.food = self.generate_food()
            if self.snake.check_collision():
                self.game_over = True

    def draw_grid(self):
        # 填充背景
        self.screen.fill(BACKGROUND_COLOR)
        grid_rect = pygame.Rect(GRID_ORIGIN_X, GRID_ORIGIN_Y, GRID_AREA_WIDTH, GRID_AREA_HEIGHT)
        pygame.draw.rect(self.screen, GRID_BACKGROUND_COLOR, grid_rect)
        # 画网格线
        for x in range(GRID_COLS + 1):
            pygame.draw.line(self.screen, GRID_LINE_COLOR,
                             (GRID_ORIGIN_X + x * GRID_CELL_SIZE, GRID_ORIGIN_Y),
                             (GRID_ORIGIN_X + x * GRID_CELL_SIZE, GRID_ORIGIN_Y + GRID_AREA_HEIGHT))
        for y in range(GRID_ROWS + 1):
            pygame.draw.line(self.screen, GRID_LINE_COLOR,
                             (GRID_ORIGIN_X, GRID_ORIGIN_Y + y * GRID_CELL_SIZE),
                             (GRID_ORIGIN_X + GRID_AREA_WIDTH, GRID_ORIGIN_Y + y * GRID_CELL_SIZE))

    def draw_snake(self):
        for i, (x, y) in enumerate(self.snake.body):
            rect = pygame.Rect(GRID_ORIGIN_X + x * GRID_CELL_SIZE,
                               GRID_ORIGIN_Y + y * GRID_CELL_SIZE,
                               GRID_CELL_SIZE, GRID_CELL_SIZE)
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_BODY_COLOR
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

    def draw_food(self):
        rect = pygame.Rect(GRID_ORIGIN_X + self.food[0] * GRID_CELL_SIZE,
                           GRID_ORIGIN_Y + self.food[1] * GRID_CELL_SIZE,
                           GRID_CELL_SIZE, GRID_CELL_SIZE)
        pygame.draw.rect(self.screen, FOOD_COLOR, rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

    def draw_hud(self):
        title_text = self.font.render("Snake Easy", True, TEXT_COLOR)
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(title_text, (20, 20))
        self.screen.blit(score_text, (20, 60))

    def draw_game_over(self):
        # 半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(GAME_OVER_BG_COLOR)
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("GAME OVER", True, (255, 50, 50))
        final_score_text = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
        restart_text = self.small_font.render("Press R to Restart", True, TEXT_COLOR)
        quit_text = self.small_font.render("Press ESC to Quit", True, TEXT_COLOR)

        self.screen.blit(game_over_text,
                         (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(final_score_text,
                         (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(restart_text,
                         (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(quit_text,
                         (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

    def draw(self):
        self.draw_grid()
        self.draw_snake()
        self.draw_food()
        self.draw_hud()
        if self.game_over:
            self.draw_game_over()

    def run(self):
        while True:
            self.handle_events()
            dt = self.clock.tick(FPS)
            self.update(dt)
            self.draw()
            pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()