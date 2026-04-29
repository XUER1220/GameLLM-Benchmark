import pygame
import random

# 固定常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SPEED = 7
PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
BALL_SIZE = 18
INITIAL_BALL_SPEED = 5
WINNING_SCORE = 7

# 颜色常量
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pong Easy")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 32)
    
    # 设置随机种子
    random.seed(42)
    
    # 初始化游戏状态
    def reset_game():
        # 左右球拍初始位置
        left_paddle = pygame.Rect(20, (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        right_paddle = pygame.Rect(SCREEN_WIDTH - 20 - PADDLE_WIDTH, (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        
        # 小球初始位置在屏幕中心
        ball = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
        
        # 小球速度：x方向随机选择，y方向固定为5像素/帧
        dx = random.choice([-1, 1]) * INITIAL_BALL_SPEED
        dy = INITIAL_BALL_SPEED
        
        score_left = 0
        score_right = 0
        game_over = False
        winner = None
        
        return left_paddle, right_paddle, ball, dx, dy, score_left, score_right, game_over, winner
    
    left_paddle, right_paddle, ball, dx, dy, score_left, score_right, game_over, winner = reset_game()
    
    # 键盘状态
    keys = pygame.key.get_pressed()
    
    running = True
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    left_paddle, right_paddle, ball, dx, dy, score_left, score_right, game_over, winner = reset_game()
        
        # 更新游戏逻辑
        if not game_over:
            # 获取按键状态（每次循环重新获取）
            keys = pygame.key.get_pressed()
            
            # 左侧球拍控制（W/S）
            if keys[pygame.K_w] and left_paddle.top > 0:
                left_paddle.y -= PLAYER_SPEED
            if keys[pygame.K_s] and left_paddle.bottom < SCREEN_HEIGHT:
                left_paddle.y += PLAYER_SPEED
            
            # 右侧球拍控制（上下方向键）
            if keys[pygame.K_UP] and right_paddle.top > 0:
                right_paddle.y -= PLAYER_SPEED
            if keys[pygame.K_DOWN] and right_paddle.bottom < SCREEN_HEIGHT:
                right_paddle.y += PLAYER_SPEED
            
            # 移动小球
            ball.x += dx
            ball.y += dy
            
            # 碰到上下边界反弹
            if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
                dy = -dy
            
            # 碰到球拍反弹（简单反弹，不旋转物理）
            if ball.colliderect(left_paddle) and dx < 0:
                dx = abs(dx)  # 强制向右反弹
            elif ball.colliderect(right_paddle) and dx > 0:
                dx = -abs(dx)  # 强制向左反弹
            
            # 得分检测
            if ball.left <= 0:  # 右侧得分
                score_right += 1
                if score_right == WINNING_SCORE:
                    game_over = True
                    winner = "Right"
                else:
                    ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                    dx = abs(dx) if dx >= 0 else -abs(dx)  # 右侧得分则向左发球
                    dy = INITIAL_BALL_SPEED  # 重置y速度
                ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                # 随机决定x方向（由于固定随机种子，结果稳定）
                dx = random.choice([-1, 1]) * INITIAL_BALL_SPEED
                dy = INITIAL_BALL_SPEED
            elif ball.right >= SCREEN_WIDTH:  # 左侧得分
                score_left += 1
                if score_left == WINNING_SCORE:
                    game_over = True
                    winner = "Left"
                else:
                    # 清空上次得分后的球位置，重新发球
                    ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                    dx = random.choice([-1, 1]) * INITIAL_BALL_SPEED  # 利用固定种子确保结果可重复
                    dy = INITIAL_BALL_SPEED
                # 确保在得分后重置球位置
                ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                dx = random.choice([-1, 1]) * INITIAL_BALL_SPEED
                dy = INITIAL_BALL_SPEED
        
        # 绘制画面
        screen.fill(BLACK)
        
        # 绘制中线
        pygame.draw.line(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)
        
        # 绘制球拍
        pygame.draw.rect(screen, WHITE, left_paddle)
        pygame.draw.rect(screen, WHITE, right_paddle)
        
        # 绘制小球
        pygame.draw.rect(screen, GREEN, ball)
        
        # 显示分数
        score_text = font.render(f"{score_left}   {score_right}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 50))
        
        # 游戏结束时显示胜利信息
        if game_over:
            win_text = font.render(f"{winner} Wins!", True, WHITE)
            screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            
            restart_text = small_font.render("Press R to Restart", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()