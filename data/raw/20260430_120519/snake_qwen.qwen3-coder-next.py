import pygame
import random

# 初始化pygame
pygame.init()

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_COLS = 30
GRID_ROWS = 24
GRID_SIZE = 20
GAME_WIDTH = GRID_COLS * GRID_SIZE
GAME_HEIGHT = GRID_ROWS * GRID_SIZE
FPS = 60
SNAKE_SPEED = 10  # per second
SCORE_PER_FOOD = 10

# 颜色定义
COLOR_BG = (30, 30, 30)
COLOR_GRID = (40, 40, 40)
COLOR_SNAKE_HEAD = (0, 255, 0)
COLOR_SNAKE_BODY = (0, 200, 0)
COLOR_FOOD = (255, 0, 0)
COLOR_TEXT = (255, 255, 255)
COLOR_HUD = (255, 255, 255)

# 游戏状态
STATE_PLAYING = 0
STATE_GAME_OVER = 1

# 初始化屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Easy")
clock = pygame.time.Clock()

# 随机种子
random.seed(42)

# 游戏常量
HUD_Y = 20
HUD_X = 20
FONT_SIZE = 32

font = pygame.font.SysFont(pygame.font.get_default_font(), FONT_SIZE)


def draw_grid(surface):
    """绘制网格背景"""
    for x in range(GRID_COLS + 1):
        px = GAME_WIDTH // 2 + x * GRID_SIZE
        py_start = (SCREEN_HEIGHT - GAME_HEIGHT) // 2
        py_end = py_start + GAME_HEIGHT
        pygame.draw.line(surface, COLOR_GRID, (px, py_start), (px, py_end))
    for y in range(GRID_ROWS + 1):
        py = (SCREEN_HEIGHT - GAME_HEIGHT) // 2 + y * GRID_SIZE
        px_start = (SCREEN_WIDTH - GAME_WIDTH) // 2
        px_end = px_start + GAME_WIDTH
        pygame.draw.line(surface, COLOR_GRID, (px_start, py), (px_end, py))


def draw_snake(surface, snake):
    """绘制蛇"""
    head_x, head_y = snake[0]
    for i, (x, y) in enumerate(snake):
        color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE_BODY
        screen_x = (SCREEN_WIDTH - GAME_WIDTH) // 2 + x * GRID_SIZE + 1
        screen_y = (SCREEN_HEIGHT - GAME_HEIGHT) // 2 + y * GRID_SIZE + 1
        rect = pygame.Rect(screen_x, screen_y, GRID_SIZE - 2, GRID_SIZE - 2)
        pygame.draw.rect(surface, color, rect)


def draw_food(surface, food):
    """绘制食物"""
    fx, fy = food
    screen_x = (SCREEN_WIDTH - GAME_WIDTH) // 2 + fx * GRID_SIZE + 2
    screen_y = (SCREEN_HEIGHT - GAME_HEIGHT) // 2 + fy * GRID_SIZE + 2
    rect = pygame.Rect(screen_x, screen_y, GRID_SIZE - 4, GRID_SIZE - 4)
    pygame.draw.rect(surface, COLOR_FOOD, rect)


def draw_hud(surface, score, state):
    """绘制HUD"""
    # 顶部标题
    title_text = font.render("SNAKE EASY", True, COLOR_HUD)
    screen.blit(title_text, (HUD_X, HUD_Y))
    
    # 分数
    score_text = font.render(f"Score: {score}", True, COLOR_HUD)
    screen.blit(score_text, (HUD_X, HUD_Y + 40))
    
    if state == STATE_GAME_OVER:
        # 游戏结束信息
        game_over_text = font.render("GAME OVER", True, COLOR_TEXT)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 40))
        
        final_score_text = font.render(f"Final Score: {score}", True, COLOR_TEXT)
        screen.blit(final_score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
        
        restart_text = font.render("Press R to Restart", True, COLOR_TEXT)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - 115, SCREEN_HEIGHT // 2 + 40))


def spawn_food(snake):
    """生成不在蛇身上的食物"""
    snake_set = set(snake)
    x, y = random.randint(0, GRID_COLS - 1), random.randint(0, GRID_ROWS - 1)
    while (x, y) in snake_set:
        x, y = random.randint(0, GRID_COLS - 1), random.randint(0, GRID_ROWS - 1)
    return (x, y)


def reset_game():
    """重置游戏"""
    # 初始位置在中心附近
    center_x = GRID_COLS // 2
    center_y = GRID_ROWS // 2
    snake = [(center_x - 2, center_y),
             (center_x - 1, center_y),
             (center_x, center_y)]
    direction = (1, 0)  # 向右
    next_direction = (1, 0)
    food = spawn_food(snake)
    score = 0
    return snake, direction, next_direction, food, score


def main():
    # 初始化游戏状态
    snake, direction, next_direction, food, score = reset_game()
    state = STATE_PLAYING
    
    # 移动计时
    time_since_last_move = 0.0
    move_interval = 1.0 / SNAKE_SPEED
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        time_since_last_move += dt
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and state == STATE_GAME_OVER:
                    snake, direction, next_direction, food, score = reset_game()
                    state = STATE_PLAYING
                elif state == STATE_PLAYING:
                    if event.key == pygame.K_UP and direction != (0, 1):
                        next_direction = (0, -1)
                    elif event.key == pygame.K_DOWN and direction != (0, -1):
                        next_direction = (0, 1)
                    elif event.key == pygame.K_LEFT and direction != (1, 0):
                        next_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                        next_direction = (1, 0)
        
        # 游戏逻辑更新
        if state == STATE_PLAYING:
            # 移动蛇
            if time_since_last_move >= move_interval:
                time_since_last_move = 0.0
                direction = next_direction
                new_head = (snake[-1][0] + direction[0], snake[-1][1] + direction[1])
                
                # 检查碰撞
                if (new_head[0] < 0 or new_head[0] >= GRID_COLS or
                    new_head[1] < 0 or new_head[1] >= GRID_ROWS or
                    new_head in snake):
                    state = STATE_GAME_OVER
                else:
                    snake.append(new_head)
                    
                    # 检查是否吃到食物
                    if new_head == food:
                        score += SCORE_PER_FOOD
                        food = spawn_food(snake)
                    else:
                        snake.pop(0)
        
        # 绘制
        screen.fill(COLOR_BG)
        draw_grid(screen)
        draw_snake(screen, snake)
        draw_food(screen, food)
        draw_hud(screen, score, state)
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()