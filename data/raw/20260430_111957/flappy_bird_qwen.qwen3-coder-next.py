import pygame
import sys
import random

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
BIRD_X = 160
BIRD_Y_START = 300
GRAVITY = 0.35
FLAP_STRENGTH = -7.5
PIPE_WIDTH = 80
PIPE_GAP = 170
PIPE_SPEED = 3
PIPE_SPAWN_INTERVAL = 90
PIPE_MIN_Y = 100
PIPE_MAX_Y = SCREEN_HEIGHT - 150 - PIPE_GAP
GROUND_HEIGHT = 50
TEXT_COLOR = (255, 255, 255)
BIRD_COLOR = (255, 255, 0)
PIPE_COLOR = (0, 200, 0)
BACKGROUND_COLOR = (135, 206, 235)
GROUND_COLOR = (101, 67, 33)
TITLE_COLOR = (255, 215, 0)

def main():
    # 初始化pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flappy Bird Easy")
    clock = pygame.time.Clock()
    font_large = pygame.font.Font(None, 64)
    font_small = pygame.font.Font(None, 32)
    
    # 设置随机种子
    random.seed(42)
    
    # 游戏状态
    def reset_game():
        bird_y = BIRD_Y_START
        bird_velocity = 0
        pipes = []
        score = 0
        frames = 0
        game_over = False
        passed_pipe_id = set()
        # 初始生成第一组管道，稍后出现
        first_pipe_time = PIPE_SPAWN_INTERVAL + 60
        return bird_y, bird_velocity, pipes, score, frames, game_over, passed_pipe_id, first_pipe_time
    
    bird_y, bird_velocity, pipes, score, frames, game_over, passed_pipe_id, first_pipe_time = reset_game()
    
    # 主游戏循环
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
                    bird_y, bird_velocity, pipes, score, frames, game_over, passed_pipe_id, first_pipe_time = reset_game()
                elif not game_over and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                    bird_velocity = FLAP_STRENGTH
        
        # 游戏逻辑
        if not game_over:
            # 更新帧数
            frames += 1
            
            # 鸟的物理
            bird_velocity += GRAVITY
            bird_y += bird_velocity
            
            # 生成管道
            if frames == first_pipe_time or (pipe['x'] + PIPE_WIDTH < SCREEN_WIDTH and frames % PIPE_SPAWN_INTERVAL == 0):
                # 随机生成中间高度
                center_y = random.randint(PIPE_MIN_Y + PIPE_GAP // 2, PIPE_MAX_Y + PIPE_GAP // 2)
                upper_pipe_height = center_y - PIPE_GAP // 2
                pipes.append({
                    'x': SCREEN_WIDTH,
                    'upper_height': upper_pipe_height,
                    'passed': False
                })
            
            # 移动管道
            for pipe in pipes:
                pipe['x'] -= PIPE_SPEED
            
            # 移除出屏幕管道
            pipes = [pipe for pipe in pipes if pipe['x'] + PIPE_WIDTH > 0]
            
            # 检测碰撞
            bird_rect = pygame.Rect(BIRD_X, bird_y, BIRD_WIDTH, BIRD_HEIGHT)
            
            # 地面/天花板检测
            if bird_y + BIRD_HEIGHT >= SCREEN_HEIGHT - GROUND_HEIGHT or bird_y <= 0:
                game_over = True
            
            # 管道碰撞检测
            for pipe in pipes:
                # 上管道Rect
                upper_rect = pygame.Rect(pipe['x'], 0, PIPE_WIDTH, pipe['upper_height'])
                # 下管道Rect
                lower_rect = pygame.Rect(pipe['x'], pipe['upper_height'] + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - (pipe['upper_height'] + PIPE_GAP) - GROUND_HEIGHT)
                
                if bird_rect.colliderect(upper_rect) or bird_rect.colliderect(lower_rect):
                    game_over = True
                
                # 计分检测
                if not pipe['passed'] and bird_rect.left > pipe['x'] + PIPE_WIDTH:
                    score += 1
                    pipe['passed'] = True
            
            # 移除被标记已计分的管道（已通过）
            pipes = [pipe for pipe in pipes if not pipe['passed']]
        
        # 绘制
        screen.fill(BACKGROUND_COLOR)
        
        # 地面
        pygame.draw.rect(screen, GROUND_COLOR, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        
        # 管道
        for pipe in pipes:
            # 上管道
            pygame.draw.rect(screen, PIPE_COLOR, (pipe['x'], 0, PIPE_WIDTH, pipe['upper_height']))
            # 下管道
            y_lower = pipe['upper_height'] + PIPE_GAP
            h_lower = SCREEN_HEIGHT - y_lower - GROUND_HEIGHT
            pygame.draw.rect(screen, PIPE_COLOR, (pipe['x'], y_lower, PIPE_WIDTH, h_lower))
            
            # 管道边框
            pygame.draw.rect(screen, (0, 100, 0), (pipe['x'], 0, PIPE_WIDTH, pipe['upper_height']), 2)
            pygame.draw.rect(screen, (0, 100, 0), (pipe['x'], y_lower, PIPE_WIDTH, h_lower), 2)
        
        # 鸟
        bird_rect = pygame.Rect(BIRD_X, bird_y, BIRD_WIDTH, BIRD_HEIGHT)
        pygame.draw.rect(screen, BIRD_COLOR, bird_rect)
        pygame.draw.rect(screen, (128, 0, 0), bird_rect, 2)
        
        # HUD - 当前分数
        score_text = font_small.render(f"Score: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))
        
        # 标题
        title_text = font_small.render("Flappy Bird Easy", True, TITLE_COLOR)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 20))
        
        # 游戏结束显示
        if game_over:
            # Game Over提示
            game_over_text = font_large.render("Game Over", True, (255, 0, 0))
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            
            # 最终分数
            final_score_text = font_small.render(f"Final Score: {score}", True, TEXT_COLOR)
            screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
            
            # 重新开始提示
            restart_text = font_small.render("Press 'R' to Restart", True, TEXT_COLOR)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 70))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()