import pygame
import random
import sys

# 常量定义
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_COLS = 30
GRID_ROWS = 24
GRID_SIZE = 20
GAME_WIDTH = GRID_COLS * GRID_SIZE
GAME_HEIGHT = GRID_ROWS * GRID_SIZE
FPS = 60
SNAKE_SPEED = 10

# 颜色定义
COLOR_BG = (20, 20, 30)
COLOR_GRID = (40, 40, 50)
COLOR_SNAKE_HEAD = (50, 205, 50)
COLOR_SNAKE_BODY = (34, 139, 34)
COLOR_FOOD = (255, 69, 0)
COLOR_TEXT = (255, 255, 255)
COLOR_HUD_BG = (0, 0, 0)

# 游戏状态
START = 0
PLAYING = 1
GAME_OVER = 2

# 初始化 pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snake Easy")
clock = pygame.time.Clock()

# 字体设置
font_large = pygame.font.Font(None, 72)
font_small = pygame.font.Font(None, 36)
font_hud = pygame.font.Font(None, 32)

# 全局游戏变量
snake = []
direction = (1, 0)
next_direction = (1, 0)
food = (0, 0)
score = 0
game_state = START
last_move_time = 0


def init_game():
    global snake, direction, next_direction, food, score, game_state, last_move_time
    
    # 初始化蛇
    center_x = GRID_COLS // 2
    center_y = GRID_ROWS // 2
    snake = [(center_x - i, center_y) for i in range(3)]
    direction = (1, 0)
    next_direction = (1, 0)
    score = 0
    game_state = START
    last_move_time = 0
    spawn_food()


def spawn_food():
    global food
    while True:
        food = (
            random.randint(0, GRID_COLS - 1),
            random.randint(0, GRID_ROWS - 1)
        )
        if food not in snake:
            break


def handle_events():
    global next_direction, game_state
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            
            if game_state == START:
                game_state = PLAYING
            elif game_state == PLAYING:
                if event.key == pygame.K_UP and direction != (0, 1):
                    next_direction = (0, -1)
                elif event.key == pygame.K_DOWN and direction != (0, -1):
                    next_direction = (0, 1)
                elif event.key == pygame.K_LEFT and direction != (1, 0):
                    next_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                    next_direction = (1, 0)
            elif game_state == GAME_OVER:
                if event.key == pygame.K_r or event.key == pygame.K_R:
                    init_game()
    
    return True


def update_game(current_time):
    global snake, direction, score, game_state, last_move_time
    
    if game_state != PLAYING:
        return
    
    # 控制蛇移动速度：每秒移动 SNAKE_SPEED 次
    if current_time - last_move_time < 1000 // SNAKE_SPEED:
        return
    
    last_move_time = current_time
    
    # 更新方向
    direction = next_direction
    
    # 计算新头位置
    head_x, head_y = snake[0]
    new_head = (head_x + direction[0], head_y + direction[1])
    
    # 碰撞检测：墙壁
    if (new_head[0] < 0 or new_head[0] >= GRID_COLS or 
        new_head[1] < 0 or new_head[1] >= GRID_ROWS):
        game_state = GAME_OVER
        return
    
    # 碰撞检测：自身
    if new_head in snake:
        game_state = GAME_OVER
        return
    
    # 移动蛇
    snake.insert(0, new_head)
    
    # 检测食物
    if new_head == food:
        score += 10
        if game_state != GAME_OVER:  # 确保游戏未结束才生成新食物
            spawn_food()
    else:
        snake.pop()


def draw_game():
    # 清空屏幕
    screen.fill(COLOR_BG)
    
    # 绘制网格背景区域
    game_rect_left = (WINDOW_WIDTH - GAME_WIDTH) // 2
    game_rect_top = (WINDOW_HEIGHT - GAME_HEIGHT) // 2
    game_rect = pygame.Rect(game_rect_left, game_rect_top, GAME_WIDTH, GAME_HEIGHT)
    pygame.draw.rect(screen, COLOR_GRID, game_rect)
    
    # 绘制网格线
    for x in range(GRID_COLS + 1):
        pygame.draw.line(screen, (70, 70, 80),
                        (game_rect_left + x * GRID_SIZE, game_rect_top),
                        (game_rect_left + x * GRID_SIZE, game_rect_top + GAME_HEIGHT))
    for y in range(GRID_ROWS + 1):
        pygame.draw.line(screen, (70, 70, 80),
                        (game_rect_left, game_rect_top + y * GRID_SIZE),
                        (game_rect_left + GAME_WIDTH, game_rect_top + y * GRID_SIZE))
    
    # 绘制食物
    food_x = game_rect_left + food[0] * GRID_SIZE + 2
    food_y = game_rect_top + food[1] * GRID_SIZE + 2
    food_rect = pygame.Rect(food_x, food_y, GRID_SIZE - 4, GRID_SIZE - 4)
    pygame.draw.rect(screen, COLOR_FOOD, food_rect)
    
    # 绘制蛇
    for i, segment in enumerate(snake):
        seg_x = game_rect_left + segment[0] * GRID_SIZE + 2
        seg_y = game_rect_top + segment[1] * GRID_SIZE + 2
        segment_rect = pygame.Rect(seg_x, seg_y, GRID_SIZE - 4, GRID_SIZE - 4)
        color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE_BODY
        pygame.draw.rect(screen, color, segment_rect)
    
    # HUD - 显示标题与分数
    title_text = font_large.render("SNAKE EASY", True, COLOR_TEXT)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 30))
    screen.blit(title_text, title_rect)
    
    score_text = font_hud.render(f"Score: {score}", True, COLOR_TEXT)
    score_rect = score_text.get_rect(topleft=(10, 10))
    pygame.draw.rect(screen, COLOR_HUD_BG, (score_rect.left - 5, score_rect.top - 5, score_rect.width + 10, score_rect.height + 10))
    screen.blit(score_text, score_rect)
    
    # 游戏结束屏幕
    if game_state == GAME_OVER:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        game_over_text = font_large.render("GAME OVER", True, COLOR_TEXT)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
        screen.blit(game_over_text, game_over_rect)
        
        final_score_text = font_small.render(f"Final Score: {score}", True, COLOR_TEXT)
        final_score_rect = final_score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))
        screen.blit(final_score_text, final_score_rect)
        
        restart_text = font_small.render("Press R to Restart", True, COLOR_TEXT)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
        screen.blit(restart_text, restart_rect)
    elif game_state == START:
        start_text = font_small.render("Press any key to Start", True, COLOR_TEXT)
        start_rect = start_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        screen.blit(start_text, start_rect)


# 主循环
random.seed(42)
init_game()

running = True
while running:
    current_time = pygame.time.get_ticks()
    
    running = handle_events()
    
    update_game(current_time)
    
    draw_game()
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()