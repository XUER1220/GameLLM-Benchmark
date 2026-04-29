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
GAME_WIDTH = GRID_COLS * GRID_SIZE  # 600
GAME_HEIGHT = GRID_ROWS * GRID_SIZE  # 480
FPS = 60
SNAKE_SPEED = 10  # 每秒移动的格数
SCORE_PER_FOOD = 10

# 颜色定义
BACKGROUND_COLOR = (40, 44, 52)     # 深灰背景
GRID_COLOR = (64, 68, 76)          # 网格线颜色
SNAKE_HEAD_COLOR = (153, 217, 102) # 蛇头：深绿色
SNAKE_BODY_COLOR = (69, 163, 79)   # 蛇身：中绿色
FOOD_COLOR = (240, 115, 100)       # 食物：橙红色
TEXT_COLOR = (236, 239, 244)       # 文本颜色
GAME_OVER_COLOR = (234, 153, 153)  # 游戏结束提示颜色

# 游戏窗口设置
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Easy")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)

# 重置游戏状态
def reset_game():
    random.seed(42)  # 固定随机种子
    # 初始蛇位置（居中）
    start_col = GRID_COLS // 2
    start_row = GRID_ROWS // 2
    snake = [
        (start_col, start_row),       # 头
        (start_col - 1, start_row),
        (start_col - 2, start_row)
    ]
    direction = (1, 0)  # 向右
    food = generate_food(snake)
    score = 0
    game_over = False
    return snake, direction, food, score, game_over

# 生成食物位置
def generate_food(snake):
    while True:
        pos = (random.randint(0, GRID_COLS - 1), random.randint(0, GRID_ROWS - 1))
        if pos not in snake:
            return pos

# 定义方向常量
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# 主循环
def main():
    snake, direction, food, score, game_over = reset_game()
    running = True
    snake_move_timer = 0
    snake_move_interval = 1000 // SNAKE_SPEED  # 毫秒间隔

    while running:
        dt = clock.tick(FPS) / 1000  # 帧时间(秒)
        snake_move_timer += clock.tick(FPS)  # 累加时间（ms）

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    snake, direction, food, score, game_over = reset_game()
                elif not game_over:
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        if direction != DOWN:
                            new_direction = UP
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        if direction != UP:
                            new_direction = DOWN
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        if direction != RIGHT:
                            new_direction = LEFT
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        if direction != LEFT:
                            new_direction = RIGHT
                    else:
                        continue
                    direction = new_direction

        # 游戏逻辑更新（非游戏结束时）
        if not game_over:
            # 蛇移动
            if snake_move_timer >= snake_move_interval:
                snake_move_timer = 0
                head = snake[0]
                new_head = (head[0] + direction[0], head[1] + direction[1])

                # 检查撞墙
                if (new_head[0] < 0 or new_head[0] >= GRID_COLS or
                    new_head[1] < 0 or new_head[1] >= GRID_ROWS):
                    game_over = True
                # 检查撞自己
                elif new_head in snake:
                    game_over = True
                else:
                    snake.insert(0, new_head)  # 移动头
                    # 检查吃到食物
                    if new_head == food:
                        score += SCORE_PER_FOOD
                        food = generate_food(snake)
                    else:
                        snake.pop()  # 移除尾部

        # 绘制
        screen.fill(BACKGROUND_COLOR)
        # 绘制游戏区域背景（网格）
        game_x = (SCREEN_WIDTH - GAME_WIDTH) // 2
        game_y = (SCREEN_HEIGHT - GAME_HEIGHT) // 2
        for x in range(GRID_COLS + 1):
            pygame.draw.line(
                screen, GRID_COLOR,
                (game_x + x * GRID_SIZE, game_y),
                (game_x + x * GRID_SIZE, game_y + GAME_HEIGHT)
            )
        for y in range(GRID_ROWS + 1):
            pygame.draw.line(
                screen, GRID_COLOR,
                (game_x, game_y + y * GRID_SIZE),
                (game_x + GAME_WIDTH, game_y + y * GRID_SIZE)
            )
        
        # 绘制食物
        food_rect = pygame.Rect(
            game_x + food[0] * GRID_SIZE + 2,
            game_y + food[1] * GRID_SIZE + 2,
            GRID_SIZE - 4, GRID_SIZE - 4
        )
        pygame.draw.rect(screen, FOOD_COLOR, food_rect)

        # 绘制蛇
        for i, segment in enumerate(snake):
            seg_rect = pygame.Rect(
                game_x + segment[0] * GRID_SIZE + 1,
                game_y + segment[1] * GRID_SIZE + 1,
                GRID_SIZE - 2, GRID_SIZE - 2
            )
            if i == 0:
                pygame.draw.rect(screen, SNAKE_HEAD_COLOR, seg_rect)
            else:
                pygame.draw.rect(screen, SNAKE_BODY_COLOR, seg_rect)

        # HUD绘制
        score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
        title_text = font.render("SNAKE EASY", True, TEXT_COLOR)
        title_rect = title_text.get_rect()
        title_rect.left = 20
        title_rect.top = 20
        score_rect = score_text.get_rect()
        score_rect.left = 20
        score_rect.top = 60
        screen.blit(title_text, title_rect)
        screen.blit(score_text, score_rect)
        
        # 游戏结束提示
        if game_over:
            game_over_text = font.render("GAME OVER", True, GAME_OVER_COLOR)
            game_over_rect = game_over_text.get_rect()
            game_over_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)
            screen.blit(game_over_text, game_over_rect)
            
            final_score_text = small_font.render(f"Final Score: {score}", True, TEXT_COLOR)
            final_score_rect = final_score_text.get_rect()
            final_score_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10)
            screen.blit(final_score_text, final_score_rect)
            
            restart_text = small_font.render("Press R to Restart", True, TEXT_COLOR)
            restart_rect = restart_text.get_rect()
            restart_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
            screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()