import pygame
import random
import sys

# ==================================
# 固定参数定义
# ==================================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_COLS = 30
GRID_ROWS = 24
GRID_SIZE = 20  # 单格像素大小
GAME_WIDTH = GRID_COLS * GRID_SIZE  # 600
GAME_HEIGHT = GRID_ROWS * GRID_SIZE  # 480
FPS = 60
MOVES_PER_SECOND = 10  # 蛇移动速度（每秒格数）
SCORE_PER_FOOD = 10

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (220, 220, 220)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
DARK_GREEN = (30, 120, 30)
BLUE = (50, 100, 200)

# ==================================
# 初始化全局变量
# ==================================
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Easy")
clock = pygame.time.Clock()
random.seed(42)

font_score = pygame.font.SysFont("Arial", 32)
font_gameover = pygame.font.SysFont("Arial", 64)
font_hud = pygame.font.SysFont("Arial", 24)

# 游戏位置偏移（让网格区域居中）
GAME_OFFSET_X = (SCREEN_WIDTH - GAME_WIDTH) // 2
GAME_OFFSET_Y = (SCREEN_HEIGHT - GAME_HEIGHT) // 2

# ==================================
# 辅助函数
# ==================================
def draw_grid():
    for x in range(0, GAME_WIDTH + 1, GRID_SIZE):
        pygame.draw.line(screen, LIGHT_GRAY, (GAME_OFFSET_X + x, GAME_OFFSET_Y),
                         (GAME_OFFSET_X + x, GAME_OFFSET_Y + GAME_HEIGHT))
    for y in range(0, GAME_HEIGHT + 1, GRID_SIZE):
        pygame.draw.line(screen, LIGHT_GRAY, (GAME_OFFSET_X, GAME_OFFSET_Y + y),
                         (GAME_OFFSET_X + GAME_WIDTH, GAME_OFFSET_Y + y))

def draw_snake(snake):
    for i, segment in enumerate(snake):
        x = GAME_OFFSET_X + segment[0] * GRID_SIZE
        y = GAME_OFFSET_Y + segment[1] * GRID_SIZE
        color = DARK_GREEN if i == 0 else GREEN
        pygame.draw.rect(screen, color, (x, y, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, BLACK, (x, y, GRID_SIZE, GRID_SIZE), 1)

def draw_food(food):
    x = GAME_OFFSET_X + food[0] * GRID_SIZE
    y = GAME_OFFSET_Y + food[1] * GRID_SIZE
    pygame.draw.ellipse(screen, RED, (x + 2, y + 2, GRID_SIZE - 4, GRID_SIZE - 4))

def draw_hud(score):
    score_text = font_score.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (20, 20))

def draw_game_over(score):
    title_text = font_gameover.render("GAME OVER", True, RED)
    score_text = font_hud.render(f"Final Score: {score}", True, BLACK)
    restart_text = font_hud.render("Press R to Restart", True, BLACK)
    
    # 居中显示 Game Over 文本
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    
    screen.blit(title_text, title_rect)
    screen.blit(score_text, score_rect)
    screen.blit(restart_text, restart_rect)

def generate_food(snake):
    food = [random.randint(0, GRID_COLS - 1), random.randint(0, GRID_ROWS - 1)]
    while food in snake:
        food = [random.randint(0, GRID_COLS - 1), random.randint(0, GRID_ROWS - 1)]
    return food

def reset_game():
    snake = [[10, 12], [9, 12], [8, 12]]  # 初始3格长，居中附近
    direction = (1, 0)  # 初始方向向右
    food = generate_food(snake)
    score = 0
    return snake, direction, food, score

# ==================================
# 主程序
# ==================================
def main():
    snake, direction, food, score = reset_game()
    game_over = False
    
    move_interval = 1000 // MOVES_PER_SECOND  # 毫秒/移动
    last_move_time = 0
    
    running = True
    while running:
        # 获取当前时间（毫秒）
        current_time = pygame.time.get_ticks()
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    snake, direction, food, score = reset_game()
                    game_over = False
                elif not game_over:
                    # 控制方向（禁止反向）
                    if event.key == pygame.K_UP and direction != (0, 1):
                        direction = (0, -1)
                    elif event.key == pygame.K_DOWN and direction != (0, -1):
                        direction = (0, 1)
                    elif event.key == pygame.K_LEFT and direction != (1, 0):
                        direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                        direction = (1, 0)
        
        # 更新游戏逻辑（仅在移动间隔时更新）
        if not game_over and current_time - last_move_time >= move_interval:
            # 移动蛇
            head_x, head_y = snake[0]
            new_head = [head_x + direction[0], head_y + direction[1]]
            
            # 碰撞检测：墙壁
            if (new_head[0] < 0 or new_head[0] >= GRID_COLS or
                new_head[1] < 0 or new_head[1] >= GRID_ROWS or
                new_head in snake):
                game_over = True
            else:
                # 插入新头
                snake.insert(0, new_head)
                
                # 检查吃食物
                if new_head == food:
                    score += SCORE_PER_FOOD
                    food = generate_food(snake)
                else:
                    snake.pop()  # 没吃到食物，移除尾巴
                
            last_move_time = current_time
        
        # 渲染
        screen.fill(WHITE)
        draw_grid()
        draw_snake(snake)
        draw_food(food)
        draw_hud(score)
        
        if game_over:
            draw_game_over(score)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()