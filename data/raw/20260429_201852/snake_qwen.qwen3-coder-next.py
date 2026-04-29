import pygame
import random
import sys

# ==================== 常量定义 ====================
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

GRID_COLS = 30
GRID_ROWS = 24
GRID_SIZE = 20
GRID_WIDTH = GRID_COLS * GRID_SIZE
GRID_HEIGHT = GRID_ROWS * GRID_SIZE

GRID_OFFSET_X = (WINDOW_WIDTH - GRID_WIDTH) // 2
GRID_OFFSET_Y = (WINDOW_HEIGHT - GRID_HEIGHT) // 2 + 40  # 留出HUD空间

FPS_CLOCK = pygame.time.Clock()

SCORE_PER_FOOD = 10
SNAKE_SPEED = 10  # per second

# 颜色
BACKGROUND_COLOR = (30, 30, 30)
GRID_LINE_COLOR = (50, 50, 50)
SNAKE_HEAD_COLOR = (0, 255, 0)
SNAKE_BODY_COLOR = (0, 200, 0)
FOOD_COLOR = (255, 0, 0)
TEXT_COLOR = (255, 255, 255)
GAME_OVER_COLOR = (255, 100, 100)

# 游戏状态
STATE_PLAYING = 0
STATE_GAME_OVER = 1

random.seed(42)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake Easy")

    font = pygame.font.SysFont(None, 24)
    big_font = pygame.font.SysFont(None, 48)

    while True:
        game_loop(screen, font, big_font)


def game_loop(screen, font, big_font):
    # 初始化游戏变量
    state = STATE_PLAYING
    score = 0
    food = None

    # 蛇初始位置：中心附近，向右
    center_col = GRID_COLS // 2
    center_row = GRID_ROWS // 2
    snake = [
        (center_col - 2, center_row),
        (center_col - 1, center_row),
        (center_col, center_row)
    ]
    direction = (1, 0)
    next_direction = (1, 0)

    # 食物位置（初始）
    food = generate_food(snake)

    move_timer = 0.0
    move_interval = 1.0 / SNAKE_SPEED

    while True:
        dt = FPS_CLOCK.tick(FPS) / 1000.0
        move_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r and state == STATE_GAME_OVER:
                    return  # restart game
                elif state == STATE_PLAYING:
                    if event.key == pygame.K_UP and direction != (0, 1):
                        next_direction = (0, -1)
                    elif event.key == pygame.K_DOWN and direction != (0, -1):
                        next_direction = (0, 1)
                    elif event.key == pygame.K_LEFT and direction != (1, 0):
                        next_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                        next_direction = (1, 0)

        if state == STATE_PLAYING:
            # 更新蛇移动逻辑
            if move_timer >= move_interval:
                move_timer = 0.0
                direction = next_direction
                head_x, head_y = snake[-1]
                new_head = (head_x + direction[0], head_y + direction[1])

                # 检查死亡条件
                if (new_head[0] < 0 or new_head[0] >= GRID_COLS or
                    new_head[1] < 0 or new_head[1] >= GRID_ROWS or
                    new_head in snake[:-1]):
                    state = STATE_GAME_OVER
                else:
                    snake.append(new_head)
                    if new_head == food:
                        # 吃到食物
                        score += SCORE_PER_FOOD
                        food = generate_food(snake)
                    else:
                        # 没吃到食物，移除尾部
                        snake.pop(0)

        # 渲染画面
        screen.fill(BACKGROUND_COLOR)

        # 绘制网格区域
        pygame.draw.rect(screen, (0, 0, 0), (GRID_OFFSET_X, GRID_OFFSET_Y, GRID_WIDTH, GRID_HEIGHT))

        # 绘制网格线
        for x in range(0, GRID_WIDTH + 1, GRID_SIZE):
            start = (GRID_OFFSET_X + x, GRID_OFFSET_Y)
            end = (GRID_OFFSET_X + x, GRID_OFFSET_Y + GRID_HEIGHT)
            pygame.draw.line(screen, GRID_LINE_COLOR, start, end, 1)
        for y in range(0, GRID_HEIGHT + 1, GRID_SIZE):
            start = (GRID_OFFSET_X, GRID_OFFSET_Y + y)
            end = (GRID_OFFSET_X + GRID_WIDTH, GRID_OFFSET_Y + y)
            pygame.draw.line(screen, GRID_LINE_COLOR, start, end, 1)

        # 绘制HUD
        hud_text = font.render(f"Score: {score}", True, TEXT_COLOR)
        title_text = font.render("Snake Easy", True, TEXT_COLOR)
        screen.blit(title_text, (GRID_OFFSET_X, GRID_OFFSET_Y - 30))
        screen.blit(hud_text, (GRID_OFFSET_X + 10, GRID_OFFSET_Y + GRID_HEIGHT + 5))

        # 绘制食物
        if food:
            fx, fy = food[0] * GRID_SIZE + GRID_OFFSET_X, food[1] * GRID_SIZE + GRID_OFFSET_Y
            pygame.draw.rect(screen, FOOD_COLOR, (fx + 2, fy + 2, GRID_SIZE - 4, GRID_SIZE - 4))

        # 绘制蛇
        for i, (x, y) in enumerate(snake):
            sx = x * GRID_SIZE + GRID_OFFSET_X
            sy = y * GRID_SIZE + GRID_OFFSET_Y
            color = SNAKE_HEAD_COLOR if i == len(snake) - 1 else SNAKE_BODY_COLOR
            pygame.draw.rect(screen, color, (sx + 1, sy + 1, GRID_SIZE - 2, GRID_SIZE - 2))

        # 游戏结束画面
        if state == STATE_GAME_OVER:
            game_over_text = big_font.render("GAME OVER", True, GAME_OVER_COLOR)
            score_text = font.render(f"Final Score: {score}", True, TEXT_COLOR)
            restart_text = font.render("Press 'R' to Restart", True, TEXT_COLOR)

            # 绘制居中
            go_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
            score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 0))
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))

            screen.blit(game_over_text, go_rect)
            screen.blit(score_text, score_rect)
            screen.blit(restart_text, restart_rect)

        pygame.display.flip()


def generate_food(snake):
    # 生成不在蛇身上的食物位置
    while True:
        x = random.randint(0, GRID_COLS - 1)
        y = random.randint(0, GRID_ROWS - 1)
        if (x, y) not in snake:
            return (x, y)


if __name__ == "__main__":
    main()