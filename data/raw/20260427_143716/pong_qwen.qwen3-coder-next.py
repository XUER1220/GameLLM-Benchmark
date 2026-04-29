import pygame
import random

# 初始化 Pygame
pygame.init()

# 固定参数
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
BALL_SIZE = 18
PADDLE_SPEED = 7
BALL_SPEED_X = 5
BALL_SPEED_Y = 5
WIN_SCORE = 7

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)

# 初始化窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 32)

# 设置随机种子
random.seed(42)

def reset_ball():
    ball_rect = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
    direction_x = random.choice([-1, 1])
    dir_y_choices = [1, -1]
    direction_y = random.choice(dir_y_choices)
    return ball_rect, direction_x * BALL_SPEED_X, direction_y * BALL_SPEED_Y

# 游戏状态
running = True
game_over = False
winner = None

# 初始化球拍
left_paddle = pygame.Rect(10, (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
right_paddle = pygame.Rect(SCREEN_WIDTH - 10 - PADDLE_WIDTH, (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

# 初始化球
ball_rect, ball_x_speed, ball_y_speed = reset_ball()

# 分数
left_score = 0
right_score = 0

# 输入状态
keys_state = {}

while running:
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            keys_state[event.key] = True
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r and game_over:
                left_score = 0
                right_score = 0
                game_over = False
                left_paddle.top = (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2
                right_paddle.top = (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2
                ball_rect, ball_x_speed, ball_y_speed = reset_ball()
            elif event.key == pygame.K_r and not game_over and (left_score >= WIN_SCORE or right_score >= WIN_SCORE):
                # 防止游戏未结束时误触R
                pass
        elif event.type == pygame.KEYUP:
            keys_state[event.key] = False

    if not game_over:
        # 更新球拍位置
        if keys_state.get(pygame.K_w) and left_paddle.top > 0:
            left_paddle.y -= PADDLE_SPEED
        if keys_state.get(pygame.K_s) and left_paddle.bottom < SCREEN_HEIGHT:
            left_paddle.y += PADDLE_SPEED
        if keys_state.get(pygame.K_UP) and right_paddle.top > 0:
            right_paddle.y -= PADDLE_SPEED
        if keys_state.get(pygame.K_DOWN) and right_paddle.bottom < SCREEN_HEIGHT:
            right_paddle.y += PADDLE_SPEED

        # 更新球位置
        ball_rect.x += ball_x_speed
        ball_rect.y += ball_y_speed

        # 上下边界反弹
        if ball_rect.top <= 0 or ball_rect.bottom >= SCREEN_HEIGHT:
            ball_y_speed = -ball_y_speed

        # 与球拍碰撞检测
        if ball_rect.colliderect(left_paddle) and ball_x_speed < 0:
            ball_x_speed = -ball_x_speed
            # 稍微增加_y波动以避免死循环，但保持简单物理
            if abs(ball_y_speed) < BALL_SPEED_Y * 2:
                ball_y_speed += 1 if ball_y_speed > 0 else -1
            else:
                ball_y_speed *= -1
        elif ball_rect.colliderect(right_paddle) and ball_x_speed > 0:
            ball_x_speed = -ball_x_speed
            if abs(ball_y_speed) < BALL_SPEED_Y * 2:
                ball_y_speed += 1 if ball_y_speed > 0 else -1
            else:
                ball_y_speed *= -1

        # 得分检测
        if ball_rect.left <= 0:
            right_score += 1
            ball_rect, ball_x_speed, ball_y_speed = reset_ball()
        elif ball_rect.right >= SCREEN_WIDTH:
            left_score += 1
            ball_rect, ball_x_speed, ball_y_speed = reset_ball()

        # 检查胜利条件
        if left_score >= WIN_SCORE or right_score >= WIN_SCORE:
            game_over = True
            winner = "Left" if left_score >= WIN_SCORE else "Right"

    # 渲染画面
    screen.fill(BLACK)

    # 绘制中线
    pygame.draw.line(screen, LIGHT_GRAY, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)

    # 绘制球拍
    pygame.draw.rect(screen, WHITE, left_paddle)
    pygame.draw.rect(screen, WHITE, right_paddle)

    # 绘制球
    pygame.draw.rect(screen, WHITE, ball_rect)

    # 绘制分数
    left_text = font.render(str(left_score), True, WHITE)
    right_text = font.render(str(right_score), True, WHITE)
    screen.blit(left_text, (SCREEN_WIDTH // 2 - 60, 20))
    screen.blit(right_text, (SCREEN_WIDTH // 2 + 40, 20))

    # 游戏结束信息
    if game_over:
        win_text = font.render(f"{winner} Wins!", True, WHITE)
        restart_text = small_font.render("Press R to Restart", True, WHITE)
        screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 30))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()