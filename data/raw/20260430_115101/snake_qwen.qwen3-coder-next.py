import pygame
import random
import sys

# 顶部常量
WIDTH, HEIGHT = 800, 600
GRID_COLS, GRID_ROWS = 30, 24
GRID_SIZE = 20
GAME_WIDTH, GAME_HEIGHT = GRID_COLS * GRID_SIZE, GRID_ROWS * GRID_SIZE
FPS = 60
SNAKE_SPEED = 10  # moves per second
WINDOW_TITLE = "Snake Easy"
SCORE_PER_FOOD = 10
INITIAL_SNAKE_LENGTH = 3
INITIAL_DIRECTION = (1, 0)  # Right
SEED = 42

# 颜色定义
COLOR_BG = (20, 20, 30)
COLOR_GRID = (40, 40, 50)
COLOR_SNAKE_HEAD = (0, 255, 0)
COLOR_SNAKE_BODY = (0, 200, 0)
COLOR_FOOD = (255, 0, 0)
COLOR_TEXT = (230, 230, 230)
COLOR_GAME_OVER = (255, 80, 80)
COLOR_HINT = (200, 200, 200)

# 初始化 Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)
clock = pygame.time.Clock()

# 设置随机种子
random.seed(SEED)

# 通用函数
def create_font(size):
    return pygame.font.SysFont(None, size)

def draw_text_centered(screen, text, y, font_size=40, color=COLOR_TEXT):
    font = create_font(font_size)
    surface = font.render(text, True, color)
    x = (WIDTH - surface.get_width()) // 2
    screen.blit(surface, (x, y))

def draw_text_left(screen, text, x, y, font_size=24, color=COLOR_TEXT):
    font = create_font(font_size)
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))

def draw_grid_area():
    # 绘制背景
    screen.fill(COLOR_BG)
    
    # 计算网格区域左上角坐标
    grid_left = (WIDTH - GAME_WIDTH) // 2
    grid_top = (HEIGHT - GAME_HEIGHT) // 2 + 50  # HUD 区域上方留出空间
    
    # 绘制网格线
    for x in range(GRID_COLS + 1):
        start_x = grid_left + x * GRID_SIZE
        y_start = grid_top
        y_end = grid_top + GAME_HEIGHT
        pygame.draw.line(screen, COLOR_GRID, (start_x, y_start), (start_x, y_end), 1)
    
    for y in range(GRID_ROWS + 1):
        start_y = grid_top + y * GRID_SIZE
        x_start = grid_left
        x_end = grid_left + GAME_WIDTH
        pygame.draw.line(screen, COLOR_GRID, (x_start, start_y), (x_end, start_y), 1)
    
    return grid_left, grid_top

class SnakeGame:
    def __init__(self):
        self.reset()
    
    def reset(self):
        # 计算初始蛇位置（居中）
        mid_col = GRID_COLS // 2
        mid_row = GRID_ROWS // 2
        
        self.snake = [(mid_col - i, mid_row) for i in range(INITIAL_SNAKE_LENGTH)]
        self.direction = INITIAL_DIRECTION
        self.next_direction = INITIAL_DIRECTION
        
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.last_move_time = pygame.time.get_ticks()
        self.move_accumulator = 0
    
    def generate_food(self):
        while True:
            food_pos = (random.randint(0, GRID_COLS - 1), random.randint(0, GRID_ROWS - 1))
            if food_pos not in self.snake:
                return food_pos
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.direction[1] != 1:
            self.next_direction = (0, -1)
        elif keys[pygame.K_DOWN] and self.direction[1] != -1:
            self.next_direction = (0, 1)
        elif keys[pygame.K_LEFT] and self.direction[0] != 1:
            self.next_direction = (-1, 0)
        elif keys[pygame.K_RIGHT] and self.direction[0] != -1:
            self.next_direction = (1, 0)
    
    def update(self):
        if self.game_over:
            return
        
        # 计算时间间隔
        current_time = pygame.time.get_ticks()
        delta_time = current_time - self.last_move_time
        self.last_move_time = current_time
        
        # 移动时间累计
        self.move_accumulator += delta_time
        
        # 根据速度更新（每 1000/SNAKE_SPEED 毫秒移动一次）
        move_interval = 1000 // SNAKE_SPEED
        while self.move_accumulator >= move_interval:
            self.move_accumulator -= move_interval
            self.move_snake()
    
    def move_snake(self):
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        
        # 检查墙壁碰撞
        if (new_head[0] < 0 or new_head[0] >= GRID_COLS or
            new_head[1] < 0 or new_head[1] >= GRID_ROWS):
            self.game_over = True
            return
        
        # 检查自身碰撞（忽略尾部，因为会移走）
        if new_head in self.snake[:-1]:
            self.game_over = True
            return
        
        self.snake.insert(0, new_head)
        
        # 检查食物
        if new_head == self.food:
            self.score += SCORE_PER_FOOD
            self.food = self.generate_food()
        else:
            self.snake.pop()
    
    def draw(self, grid_left, grid_top):
        # 绘制网格
        draw_grid_area()
        
        # 绘制食物
        fx, fy = self.food
        food_rect = pygame.Rect(
            grid_left + fx * GRID_SIZE + 4,
            grid_top + fy * GRID_SIZE + 4,
            GRID_SIZE - 8,
            GRID_SIZE - 8
        )
        pygame.draw.rect(screen, COLOR_FOOD, food_rect)
        
        # 绘制蛇
        for i, (x, y) in enumerate(self.snake):
            sx = grid_left + x * GRID_SIZE + 1
            sy = grid_top + y * GRID_SIZE + 1
            s_width = GRID_SIZE - 2
            s_height = GRID_SIZE - 2
            
            if i == 0:
                pygame.draw.rect(screen, COLOR_SNAKE_HEAD, (sx, sy, s_width, s_height))
            else:
                pygame.draw.rect(screen, COLOR_SNAKE_BODY, (sx, sy, s_width, s_height))
        
        # HUD（显示分数）
        hud_x = 20
        hud_y = 20
        draw_text_left(screen, f"Score: {self.score}", hud_x, hud_y)
        
        # 游戏结束画面
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            draw_text_centered(screen, "GAME OVER", HEIGHT // 2 - 40, 64, COLOR_GAME_OVER)
            draw_text_centered(screen, f"Final Score: {self.score}", HEIGHT // 2 + 10, 36, COLOR_TEXT)
            draw_text_centered(screen, "Press R to Restart", HEIGHT // 2 + 60, 24, COLOR_HINT)

def main():
    game = SnakeGame()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game.game_over:
                    game.reset()
        
        # 输入处理
        game.handle_input()
        
        # 更新逻辑
        game.update()
        
        # 绘制
        grid_left, grid_top = draw_grid_area()
        game.draw(grid_left, grid_top)
        
        # 更新窗口
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()