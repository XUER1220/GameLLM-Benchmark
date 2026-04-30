import pygame
import sys
import random

# 常量定义
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
BALL_SIZE = 18
PADDLE_SPEED = 7
BALL_SPEED_X = 5
BALL_SPEED_Y = 5
WINNING_SCORE = 7

# 颜色常量
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# 初始化pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pong Easy")
clock = pygame.time.Clock()
font_large = pygame.font.SysFont(None, 64)
font_small = pygame.font.SysFont(None, 32)

# 设置随机种子
random.seed(42)

def reset_ball():
    ball_rect = pygame.Rect(WINDOW_WIDTH // 2 - BALL_SIZE // 2, WINDOW_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
    direction_x = random.choice([-1, 1])
    ball_velocity = [direction_x * BALL_SPEED_X, random.choice([-1, 1]) * BALL_SPEED_Y]
    return ball_rect, ball_velocity

def draw_center_line():
    for y in range(0, WINDOW_HEIGHT, 30):
        pygame.draw.rect(screen, GRAY, (WINDOW_WIDTH // 2 - 2, y, 4, 15))

def main():
    # 初始化游戏状态
    left_score = 0
    right_score = 0
    game_over = False
    winner = None
    
    # 初始化球拍位置
    left_paddle = pygame.Rect(20, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = pygame.Rect(WINDOW_WIDTH - 20 - PADDLE_WIDTH, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    
    # 初始化球
    ball_rect, ball_velocity = reset_ball()
    
    # 键盘按键状态
    keys = pygame.key.get_pressed()
    
    while True:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r and game_over:
                    # 重新开始游戏
                    left_score = 0
                    right_score = 0
                    game_over = False
                    winner = None
                    left_paddle = pygame.Rect(20, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
                    right_paddle = pygame.Rect(WINDOW_WIDTH - 20 - PADDLE_WIDTH, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
                    ball_rect, ball_velocity = reset_ball()
                elif event.key == pygame.K_r and not game_over and (left_score >= WINNING_SCORE or right_score >= WINNING_SCORE):
                    # 若游戏已结束才允许R键重新开始（已在上面实现），否则可忽略
                    pass
        
        # 如果游戏未结束，处理输入和更新逻辑
        if not game_over:
            keys = pygame.key.get_pressed()
            
            # 左侧球拍控制 (W/S)
            if keys[pygame.K_w] and left_paddle.top > 0:
                left_paddle.y -= PADDLE_SPEED
            if keys[pygame.K_s] and left_paddle.bottom < WINDOW_HEIGHT:
                left_paddle.y += PADDLE_SPEED
                
            # 右侧球拍控制 (UP/DOWN)
            if keys[pygame.K_UP] and right_paddle.top > 0:
                right_paddle.y -= PADDLE_SPEED
            if keys[pygame.K_DOWN] and right_paddle.bottom < WINDOW_HEIGHT:
                right_paddle.y += PADDLE_SPEED
            
            # 更新球的位置
            ball_rect.x += ball_velocity[0]
            ball_rect.y += ball_velocity[1]
            
            # 球碰到上下边界反弹
            if ball_rect.top <= 0 or ball_rect.bottom >= WINDOW_HEIGHT:
                ball_velocity[1] = -ball_velocity[1]
            
            # 球碰到左侧球拍
            if ball_rect.left <= left_paddle.right and left_paddle.top <= ball_rect.bottom and left_paddle.bottom >= ball_rect.top:
                ball_velocity[0] = abs(ball_velocity[0])  # 强制向右反弹
                # 防止卡在球拍里
                ball_rect.left = left_paddle.right + 1
            
            # 球碰到右侧球拍
            if ball_rect.right >= right_paddle.left and right_paddle.top <= ball_rect.bottom and right_paddle.bottom >= ball_rect.top:
                ball_velocity[0] = -abs(ball_velocity[0])  # 强制向左反弹
                # 防止卡在球拍里
                ball_rect.right = right_paddle.left - 1
            
            # 检查是否得分
            if ball_rect.left < 0:
                right_score += 1
                if right_score >= WINNING_SCORE:
                    game_over = True
                    winner = "Right Player"
                else:
                    ball_rect, ball_velocity = reset_ball()
            elif ball_rect.right > WINDOW_WIDTH:
                left_score += 1
                if left_score >= WINNING_SCORE:
                    game_over = True
                    winner = "Left Player"
                else:
                    ball_rect, ball_velocity = reset_ball()
        
        # 绘制屏幕
        screen.fill(BLACK)
        
        # 绘制中线
        draw_center_line()
        
        # 绘制球拍
        pygame.draw.rect(screen, WHITE, left_paddle)
        pygame.draw.rect(screen, WHITE, right_paddle)
        
        # 绘制球
        pygame.draw.rect(screen, GREEN, ball_rect)
        
        # 显示分数 HUD
        left_score_text = font_large.render(str(left_score), True, WHITE)
        right_score_text = font_large.render(str(right_score), True, WHITE)
        screen.blit(left_score_text, (WINDOW_WIDTH // 4 - left_score_text.get_width() // 2, 50))
        screen.blit(right_score_text, (3 * WINDOW_WIDTH // 4 - right_score_text.get_width() // 2, 50))
        
        # 游戏结束显示
        if game_over:
            winner_text = font_large.render(f"{winner} Wins!", True, RED)
            restart_text = font_small.render("Press R to Restart", True, WHITE)
            
            # 居中显示文本
            screen.blit(winner_text, (WINDOW_WIDTH // 2 - winner_text.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
            screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2 + 30))
        
        # 更新屏幕显示
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()