import pygame
import random

# 初始化pygame
pygame.init()

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
BALL_SIZE = 18
PADDLE_SPEED = 7
BALL_SPEED_X = 5
BALL_SPEED_Y = 5
WINNING_SCORE = 7

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# 设置窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong Easy")
clock = pygame.time.Clock()
random.seed(42)

# 游戏状态变量
player1_score = 0
player2_score = 0
game_over = False
winner = None

# 球拍和小球
player1_rect = pygame.Rect(20, (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
player2_rect = pygame.Rect(SCREEN_WIDTH - 20 - PADDLE_WIDTH, (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball_rect = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

# 球速度
ball_speed_x = BALL_SPEED_X * random.choice([-1, 1])
ball_speed_y = BALL_SPEED_Y * random.choice([-1, 1])

def reset_game():
    global player1_score, player2_score, game_over, winner, ball_speed_x, ball_speed_y
    player1_score = 0
    player2_score = 0
    game_over = False
    winner = None
    reset_ball()
    
def reset_ball():
    global ball_rect, ball_speed_x, ball_speed_y
    ball_rect.x = SCREEN_WIDTH // 2 - BALL_SIZE // 2
    ball_rect.y = SCREEN_HEIGHT // 2 - BALL_SIZE // 2
    ball_speed_x = BALL_SPEED_X * random.choice([-1, 1])
    ball_speed_y = BALL_SPEED_Y * random.choice([-1, 1])

# 主游戏循环
running = True
while running:
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                reset_game()
    
    # 获取按键状态
    keys = pygame.key.get_pressed()
    
    # 玩家1控制 (W/S)
    if not game_over:
        if keys[pygame.K_w] and player1_rect.top > 0:
            player1_rect.y -= PADDLE_SPEED
        if keys[pygame.K_s] and player1_rect.bottom < SCREEN_HEIGHT:
            player1_rect.y += PADDLE_SPEED
            
        # 玩家2控制 (上/下方向键)
        if keys[pygame.K_UP] and player2_rect.top > 0:
            player2_rect.y -= PADDLE_SPEED
        if keys[pygame.K_DOWN] and player2_rect.bottom < SCREEN_HEIGHT:
            player2_rect.y += PADDLE_SPEED
    
    # 更新游戏逻辑
    if not game_over:
        # 移动球
        ball_rect.x += ball_speed_x
        ball_rect.y += ball_speed_y
        
        # 上下边界反弹
        if ball_rect.top <= 0 or ball_rect.bottom >= SCREEN_HEIGHT:
            ball_speed_y = -ball_speed_y
        
        # 球拍碰撞检测
        # 玩家1（左侧）球拍
        if (ball_rect.left <= player1_rect.right and 
            player1_rect.top < ball_rect.bottom and 
            player1_rect.bottom > ball_rect.top):
            ball_speed_x = abs(ball_speed_x)  # 强制向右反弹
            # 防止球卡在球拍里
            ball_rect.left = player1_rect.right + 1
            
        # 玩家2（右侧）球拍
        if (ball_rect.right >= player2_rect.left and 
            player2_rect.top < ball_rect.bottom and 
            player2_rect.bottom > ball_rect.top):
            ball_speed_x = -abs(ball_speed_x)  # 强制向左反弹
            # 防止球卡在球拍里
            ball_rect.right = player2_rect.left - 1
        
        # 得分检测
        if ball_rect.left <= 0:
            player2_score += 1
            if player2_score >= WINNING_SCORE:
                game_over = True
                winner = "Player 2"
            else:
                reset_ball()
                
        if ball_rect.right >= SCREEN_WIDTH:
            player1_score += 1
            if player1_score >= WINNING_SCORE:
                game_over = True
                winner = "Player 1"
            else:
                reset_ball()
    
    # 绘制屏幕
    screen.fill(BLACK)
    
    # 绘制中线
    pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 2, 0, 4, SCREEN_HEIGHT))
    
    # 绘制球拍
    pygame.draw.rect(screen, WHITE, player1_rect)
    pygame.draw.rect(screen, WHITE, player2_rect)
    
    # 绘制球
    pygame.draw.rect(screen, GREEN, ball_rect)
    
    # 绘制分数
    font = pygame.font.Font(None, 74)
    score_text = f"{player1_score}   {player2_score}"
    text_surface = font.render(score_text, True, WHITE)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
    screen.blit(text_surface, text_rect)
    
    # 胜利信息
    if game_over:
        font big = pygame.font.Font(None, 64)
        winner_text = f"{winner} Wins!"
        text_surface = font.render(winner_text, True, RED)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text_surface, text_rect)
        
        restart_text = "Press R to Restart"
        restart_font = pygame.font.Font(None, 36)
        restart_surface = restart_font.render(restart_text, True, WHITE)
        restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        screen.blit(restart_surface, restart_rect)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()