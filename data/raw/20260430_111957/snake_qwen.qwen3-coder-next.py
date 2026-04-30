import pygame
import random

# 初始化 pygame
pygame.init()

# 固定参数
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_COLS, GRID_ROWS = 30, 24
CELL_SIZE = 20
GRID_WIDTH, GRID_HEIGHT = GRID_COLS * CELL_SIZE, GRID_ROWS * CELL_SIZE
FPS = 60
MOVEMENT_SPEED = 10  # 每秒移动格数
RANDOM_SEED = 42

# 颜色定义
BG_COLOR = (16, 16, 16)          # 背景黑色
GRID_COLOR = (32, 32, 32)        # 网格线深灰
SNAKE_HEAD_COLOR = (0, 255, 0)   # 蛇头绿色
SNAKE_BODY_COLOR = (0, 200, 0)   # 蛇身青绿色
FOOD_COLOR = (255, 50, 50)       # 食物红色
HUD_COLOR = (255, 255, 255)      # HUD 文字白色

# 计算网格区域左上角位置（居中）
GRID_TOP = (SCREEN_HEIGHT - GRID_HEIGHT) // 2
GRID_LEFT = (SCREEN_WIDTH - GRID_WIDTH) // 2

# 游戏窗口设置
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Easy")
clock = pygame.time.Clock()

# 全局状态
running = True
game_over = False
score = 0
snake = []
direction = (1, 0)  # 初始方向向右
food_pos = (0, 0)
last_move_time = 0
move_interval = 1000 // MOVEMENT_SPEED  # 毫秒
random.seed(RANDOM_SEED)


def init_game():
    global snake, direction, score, food_pos, game_over
    snake = [(GRID_COLS // 2, GRID_ROWS // 2), (GRID_COLS // 2 - 1, GRID_ROWS // 2), (GRID_COLS // 2 - 2, GRID_ROWS // 2)]
    direction = (1, 0)  # 向右
    score = 0
    game_over = False
    spawn_food()


def spawn_food():
    global food_pos
    while True:
        x = random.randint(0, GRID_COLS - 1)
        y = random.randint(0, GRID_ROWS - 1)
        if (x, y) not in snake:
            food_pos = (x, y)
            break


def handle_input():
    global direction
    keys = pygame.key.get_pressed()
    
    new_direction = direction
    
    if keys[pygame.K_UP] and direction != (0, 1):
        new_direction = (0, -1)
    elif keys[pygame.K_DOWN] and direction != (0, -1):
        new_direction = (0, 1)
    elif keys[pygame.K_LEFT] and direction != (1, 0):
        new_direction = (-1, 0)
    elif keys[pygame.K_RIGHT] and direction != (-1, 0):
        new_direction = (1, 0)
    
    if new_direction != direction and not game_over:
        direction = new_direction


def update_game(current_time):
    global score, game_over
    
    if game_over:
        return
    
    # 检查是否达到移动时间间隔
    if current_time - last_move_time < move_interval:
        return
    
    head_x, head_y = snake[0]
    dx, dy = direction
    new_head = (head_x + dx, head_y + dy)
    
    # 撞墙检测
    if (new_head[0] < 0 or new_head[0] >= GRID_COLS or
        new_head[1] < 0 or new_head[1] >= GRID_ROWS):
        game_over = True
        return
    
    # 撞自己检测
    if new_head in snake[:-1]:
        game_over = True
        return
    
    # 移动蛇
    snake.insert(0, new_head)
    
    # 吃食物检测
    if new_head == food_pos:
        score += 10
        spawn_food()
    else:
        snake.pop()


def draw():
    # 填充背景
    screen.fill(BG_COLOR)
    
    # 绘制网格（线）
    for x in range(GRID_LEFT, GRID_LEFT + GRID_WIDTH + 1, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, GRID_TOP), (x, GRID_TOP + GRID_HEIGHT))
    for y in range(GRID_TOP, GRID_TOP + GRID_HEIGHT + 1, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (GRID_LEFT, y), (GRID_LEFT + GRID_WIDTH, y))
    
    # 绘制蛇
    for i, pos in enumerate(snake):
        rect = pygame.Rect(GRID_LEFT + pos[0] * CELL_SIZE, GRID_TOP + pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_BODY_COLOR
        pygame.draw.rect(screen, color, rect)
    
    # 绘制食物
    food_rect = pygame.Rect(GRID_LEFT + food_pos[0] * CELL_SIZE, GRID_TOP + food_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, FOOD_COLOR, food_rect)
    
    # HUD（UI）信息
    font = pygame.font.SysFont(None, 36)
    title_text = font.render("Snake Easy", True, HUD_COLOR)
    screen.blit(title_text, (10, 10))
    
    score_text = font.render(f"Score: {score}", True, HUD_COLOR)
    screen.blit(score_text, (10, 50))
    
    if game_over:
        big_font = pygame.font.SysFont(None, 72)
        game_over_text = big_font.render("Game Over", True, HUD_COLOR)
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        final_score_text = font.render(f"Final Score: {score}", True, HUD_COLOR)
        screen.blit(final_score_text, (SCREEN_WIDTH//2 - final_score_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        
        restart_text = font.render("Press R to Restart", True, HUD_COLOR)
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 80))


def main():
    global running, last_move_time
    
    init_game()
    
    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    init_game()
        
        handle_input()
        update_game(current_time)
        draw()
        
        last_move_time = current_time
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()


if __name__ == "__main__":
    main()