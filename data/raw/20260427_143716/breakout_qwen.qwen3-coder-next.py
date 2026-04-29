import pygame
import random

# 常量定义
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
RANDOM_SEED = 42

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (220, 50, 50)
ORANGE = (255, 165, 0)
YELLOW = (255, 215, 0)
GREEN = (50, 205, 50)
BLUE = (0, 191, 255)

# 游戏参数
PADDLE_WIDTH = 110
PADDLE_HEIGHT = 18
PADDLE_Y_POS = WINDOW_HEIGHT - 50
PADDLE_SPEED = 8
BALL_WIDTH = 16
BALL_HEIGHT = 16
BALL_SPEED_X_INITIAL = 4
BALL_SPEED_Y_INITIAL = -5
LIVES = 3
BRICK_ROWS = 5
BRICK_COLS = 8
BRICK_WIDTH = 84
BRICK_HEIGHT = 24
BRICK_GAP_X = 4
BRICK_GAP_Y = 10

# 计算砖块起始位置以居中
BRICK_TOTAL_WIDTH = BRICK_COLS * BRICK_WIDTH + (BRICK_COLS - 1) * BRICK_GAP_X
BRICK_START_X = (WINDOW_WIDTH - BRICK_TOTAL_WIDTH) // 2
BRICK_START_Y = 60

# 随机种子
random.seed(RANDOM_SEED)

# 颜色映射（按行分配）
BRICK_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE]

def create_bricks():
    bricks = []
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            x = BRICK_START_X + col * (BRICK_WIDTH + BRICK_GAP_X)
            y = BRICK_START_Y + row * (BRICK_HEIGHT + BRICK_GAP_Y)
            color = BRICK_COLORS[row % len(BRICK_COLORS)]
            bricks.append(pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT))
    return bricks

def reset_game():
    # 重置球拍位置
    paddle = pygame.Rect(WINDOW_WIDTH // 2 - PADDLE_WIDTH // 2, PADDLE_Y_POS, PADDLE_WIDTH, PADDLE_HEIGHT)
    
    # 重置球位置（在球拍上方中央）
    ball = pygame.Rect(WINDOW_WIDTH // 2 - BALL_WIDTH // 2, PADDLE_Y_POS - BALL_HEIGHT, BALL_WIDTH, BALL_HEIGHT)
    ball_speed = [BALL_SPEED_X_INITIAL, BALL_SPEED_Y_INITIAL]
    
    # 创建砖块
    bricks = create_bricks()
    
    # 初始化游戏状态
    score = 0
    lives = LIVES
    game_state = "playing"  # "playing", "won", "lost"
    
    return paddle, ball, ball_speed, bricks, score, lives, game_state

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Breakout Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 28)
    
    paddle, ball, ball_speed, bricks, score, lives, game_state = reset_game()
    
    running = True
    while running:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_state != "playing":
                    paddle, ball, ball_speed, bricks, score, lives, game_state = reset_game()
        
        if game_state == "playing":
            # 控制球拍
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                paddle.x -= PADDLE_SPEED
            if keys[pygame.K_RIGHT]:
                paddle.x += PADDLE_SPEED
            
            # 限制球拍边界
            if paddle.x < 0:
                paddle.x = 0
            if paddle.x + paddle.width > WINDOW_WIDTH:
                paddle.x = WINDOW_WIDTH - paddle.width
            
            # 更新球位置
            ball.x += ball_speed[0]
            ball.y += ball_speed[1]
            
            # 边界反弹
            # 左右边界
            if ball.x <= 0 or ball.x + ball.width >= WINDOW_WIDTH:
                ball_speed[0] = -ball_speed[0]
            
            # 上边界
            if ball.y <= 0:
                ball_speed[1] = -ball_speed[1]
            
            # 底边界（失去生命）
            if ball.y + ball.height >= WINDOW_HEIGHT:
                lives -= 1
                if lives > 0:
                    # 重置球位置
                    ball.x = paddle.x + paddle.width // 2 - BALL_WIDTH // 2
                    ball.y = PADDLE_Y_POS - BALL_HEIGHT
                    ball_speed = [BALL_SPEED_X_INITIAL, BALL_SPEED_Y_INITIAL]
                else:
                    game_state = "lost"
            
            # 球拍反弹检测
            if ball.colliderect(paddle) and ball_speed[1] > 0:
                ball_speed[1] = -ball_speed[1]
                
                # 根据击中球拍的位置调整水平速度（简单增强手感）
                hit_pos = (ball.x + ball.width // 2) - (paddle.x + paddle.width // 2)
                ball_speed[0] = int(hit_pos / (paddle.width // 2) * 5)  # 调整水平偏移
                # 确保球速最小值
                if abs(ball_speed[0]) < 2:
                    ball_speed[0] = 2 if ball_speed[0] > 0 else -2
            
            # 砖块碰撞检测
            crash_brick = False
            for brick in bricks[:]:
                if ball.colliderect(brick):
                    bricks.remove(brick)
                    ball_speed[1] = -ball_speed[1]
                    score += 10
                    crash_brick = True
                    break  # 每帧只处理一个砖块
            
            # 胜利判定
            if len(bricks) == 0:
                game_state = "won"
        
        # 绘制
        screen.fill(BLACK)
        
        # 绘制球拍
        pygame.draw.rect(screen, WHITE, paddle)
        
        # 绘制球
        pygame.draw.ellipse(screen, WHITE, ball)
        
        # 绘制砖块
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = BRICK_START_X + col * (BRICK_WIDTH + BRICK_GAP_X)
                y = BRICK_START_Y + row * (BRICK_HEIGHT + BRICK_GAP_Y)
                brick_rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
                color = BRICK_COLORS[row % len(BRICK_COLORS)]
                pygame.draw.rect(screen, color, brick_rect)
        
        # 绘制HUD（只在非游戏结束状态）
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(score_text, (20, 20))
        screen.blit(lives_text, (WINDOW_WIDTH - 150, 20))
        
        # 游戏结束/胜利显示
        if game_state == "won" or game_state == "lost":
            if game_state == "won":
                result_text = font.render("VICTORY!", True, GREEN)
            else:
                result_text = font.render("GAME OVER", True, RED)
            
            text_width = result_text.get_width()
            screen.blit(result_text, ((WINDOW_WIDTH - text_width) // 2, WINDOW_HEIGHT // 2 - 60))
            
            restart_text = small_font.render("Press R to Restart", True, WHITE)
            text_width = restart_text.get_width()
            screen.blit(restart_text, ((WINDOW_WIDTH - text_width) // 2, WINDOW_HEIGHT // 2 + 10))
        
        # 更新显示
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()