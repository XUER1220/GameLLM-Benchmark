import pygame
import random
import sys

pygame.init()

# --- 常量声明 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_WIDTH = 30
GRID_HEIGHT = 24
CELL_SIZE = 20
GRID_AREA_WIDTH = GRID_WIDTH * CELL_SIZE
GRID_AREA_HEIGHT = GRID_HEIGHT * CELL_SIZE
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_AREA_WIDTH) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_AREA_HEIGHT) // 2 + 40
FPS = 60
SNAKE_SPEED = 10
INITIAL_LENGTH = 3
SCORE_PER_FOOD = 10
BACKGROUND_COLOR = (15, 15, 30)
GRID_LINE_COLOR = (40, 40, 70)
GRID_BG_COLOR = (20, 20, 40)
SNAKE_HEAD_COLOR = (50, 200, 100)
SNAKE_BODY_COLOR = (70, 160, 80)
FOOD_COLOR = (220, 60, 60)
TEXT_COLOR = (240, 240, 255)
GAME_OVER_BG_COLOR = (0, 0, 0, 180)

# 随机种子
random.seed(42)

# --- 游戏逻辑类 ---
class SnakeGame:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        center_x = GRID_WIDTH // 2
        center_y = GRID_HEIGHT // 2
        self.snake = [(center_x, center_y), (center_x - 1, center_y), (center_x - 2, center_y)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.move_timer = 0
        self.move_interval = 1000 // SNAKE_SPEED

    def generate_food(self):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in self.snake:
                return pos

    def update(self, dt):
        if self.game_over:
            return
        self.direction = self.next_direction
        self.move_timer += dt
        if self.move_timer >= self.move_interval:
            self.move_timer = 0
            head_x, head_y = self.snake[0]
            dx, dy = self.direction
            new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)
            if new_head in self.snake:
                self.game_over = True
                return
            self.snake.insert(0, new_head)
            if new_head == self.food:
                self.score += SCORE_PER_FOOD
                self.food = self.generate_food()
            else:
                self.snake.pop()

    def change_direction(self, new_dir):
        if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
            self.next_direction = new_dir

    def draw(self, screen, font):
        screen.fill(BACKGROUND_COLOR)
        grid_rect = pygame.Rect(GRID_OFFSET_X, GRID_OFFSET_Y, GRID_AREA_WIDTH, GRID_AREA_HEIGHT)
        pygame.draw.rect(screen, GRID_BG_COLOR, grid_rect)
        for x in range(0, GRID_AREA_WIDTH, CELL_SIZE):
            pygame.draw.line(screen, GRID_LINE_COLOR, (GRID_OFFSET_X + x, GRID_OFFSET_Y),
                             (GRID_OFFSET_X + x, GRID_OFFSET_Y + GRID_AREA_HEIGHT))
        for y in range(0, GRID_AREA_HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, GRID_LINE_COLOR, (GRID_OFFSET_X, GRID_OFFSET_Y + y),
                             (GRID_OFFSET_X + GRID_AREA_WIDTH, GRID_OFFSET_Y + y))
        for idx, (x, y) in enumerate(self.snake):
            color = SNAKE_HEAD_COLOR if idx == 0 else SNAKE_BODY_COLOR
            rect = pygame.Rect(GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (color[0]//2, color[1]//2, color[2]//2), rect, 1)
        food_rect = pygame.Rect(GRID_OFFSET_X + self.food[0] * CELL_SIZE, GRID_OFFSET_Y + self.food[1] * CELL_SIZE,
                                CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, FOOD_COLOR, food_rect)
        pygame.draw.rect(screen, (FOOD_COLOR[0]//2, FOOD_COLOR[1]//2, FOOD_COLOR[2]//2), food_rect, 1)
        score_text = font.render(f"Score: {self.score}", True, TEXT_COLOR)
        screen.blit(score_text, (20, 20))
        title_text = font.render("Snake Easy", True, TEXT_COLOR)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 10))
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(GAME_OVER_BG_COLOR)
            screen.blit(overlay, (0, 0))
            game_over_text = font.render("Game Over", True, (255, 80, 80))
            final_score_text = font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            restart_text = font.render("Press R to Restart", True, TEXT_COLOR)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))

# --- 主游戏循环 ---
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake Easy")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    game = SnakeGame()
    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game.reset_game()
                elif not game.game_over:
                    if event.key == pygame.K_UP:
                        game.change_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        game.change_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        game.change_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        game.change_direction((1, 0))
        game.update(dt)
        game.draw(screen, font)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()