import pygame
import random

# 固定配置常量
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

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pong Easy")
    clock = pygame.time.Clock()
    
    # 设置随机种子
    random.seed(42)
    
    # 游戏状态
    state = "playing"  # "playing", "game_over"
    
    # 初始化球拍位置
    left_paddle = pygame.Rect(30, (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = pygame.Rect(SCREEN_WIDTH - 30 - PADDLE_WIDTH, (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    
    # 初始化球
    def reset_ball():
        ball = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
        # 随机决定左右方向（固定种子保证每次运行一致）
        direction_x = random.choice([-1, 1])
        direction_y = random.choice([-1, 1])
        ball_speed_x = direction_x * BALL_SPEED_X
        ball_speed_y = direction_y * BALL_SPEED_Y
        return ball, ball_speed_x, ball_speed_y
    
    ball, ball_speed_x, ball_speed_y = reset_ball()
    
    # 分数
    left_score = 0
    right_score = 0
    
    # 按键状态
    keys_pressed = set()
    
    # 字体（使用Pygame内置字体）
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 32)
    
    while True:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                elif event.key == pygame.K_r:
                    # 重置游戏
                    left_score = 0
                    right_score = 0
                    left_paddle.top = (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2
                    right_paddle.top = (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2
                    ball, ball_speed_x, ball_speed_y = reset_ball()
                    state = "playing"
                elif event.key == pygame.K_w:
                    keys_pressed.add('w')
                elif event.key == pygame.K_s:
                    keys_pressed.add('s')
                elif event.key == pygame.K_UP:
                    keys_pressed.add('up')
                elif event.key == pygame.K_DOWN:
                    keys_pressed.add('down')
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    keys_pressed.discard('w')
                elif event.key == pygame.K_s:
                    keys_pressed.discard('s')
                elif event.key == pygame.K_UP:
                    keys_pressed.discard('up')
                elif event.key == pygame.K_DOWN:
                    keys_pressed.discard('down')
        
        if state == "playing":
            # 移动球拍
            if 'w' in keys_pressed and left_paddle.top > 0:
                left_paddle.top -= PADDLE_SPEED
            if 's' in keys_pressed and left_paddle.top < SCREEN_HEIGHT - PADDLE_HEIGHT:
                left_paddle.top += PADDLE_SPEED
            if 'up' in keys_pressed and right_paddle.top > 0:
                right_paddle.top -= PADDLE_SPEED
            if 'down' in keys_pressed and right_paddle.top < SCREEN_HEIGHT - PADDLE_HEIGHT:
                right_paddle.top += PADDLE_SPEED
            
            # 移动小球
            ball.x += ball_speed_x
            ball.y += ball_speed_y
            
            # 墙壁碰撞（上下边界）
            if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
                ball_speed_y = -ball_speed_y
            
            # 球拍碰撞检测
            if ball.colliderect(left_paddle) and ball_speed_x < 0:
                ball_speed_x = -ball_speed_x
                # 简单的偏转处理：根据球击中球拍的位置微调Y方向
                overlap = ball.center[1] - left_paddle.center[1]
                ball_speed_y += overlap * 0.1
                # 限制Y速度幅度
                ball_speed_y = max(-ball_speed_y * 2, min(ball_speed_y, ball_speed_y * 2))
                # 修正位置防止粘连
                ball.left = left_paddle.right + 1
            
            if ball.colliderect(right_paddle) and ball_speed_x > 0:
                ball_speed_x = -ball_speed_x
                overlap = ball.center[1] - right_paddle.center[1]
                ball_speed_y += overlap * 0.1
                ball_speed_y = max(-ball_speed_y * 2, min(ball_speed_y, ball_speed_y * 2))
                ball.right = right_paddle.left - 1
            
            # 边界检测（左右边界）及得分
            if ball.left <= 0:
                right_score += 1
                if right_score >= WIN_SCORE:
                    state = "game_over"
                    winner = "Right"
                else:
                    ball, ball_speed_x, ball_speed_y = reset_ball()
            elif ball.right >= SCREEN_WIDTH:
                left_score += 1
                if left_score >= WIN_SCORE:
                    state = "game_over"
                    winner = "Left"
                else:
                    ball, ball_speed_x, ball_speed_y = reset_ball()
        
        # 绘制画面
        screen.fill(BLACK)
        
        # 绘制中线
        for i in range(0, SCREEN_HEIGHT, 20):
            pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH // 2 - 2, i, 4, 10))
        
        # 绘制球拍
        pygame.draw.rect(screen, WHITE, left_paddle)
        pygame.draw.rect(screen, WHITE, right_paddle)
        
        # 绘制球
        pygame.draw.rect(screen, WHITE, ball)
        
        # 绘制分数
        left_text = font.render(str(left_score), True, WHITE)
        right_text = font.render(str(right_score), True, WHITE)
        screen.blit(left_text, (SCREEN_WIDTH // 4 - left_text.get_width() // 2, 20))
        screen.blit(right_text, (3 * SCREEN_WIDTH // 4 - right_text.get_width() // 2, 20))
        
        # 游戏结束提示
        if state == "game_over":
            win_text = font.render(f"{winner} Wins!", True, WHITE)
            restart_text = small_font.render("Press R to Restart", True, WHITE)
            screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 3))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()