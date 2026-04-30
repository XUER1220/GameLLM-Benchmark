import pygame
import random

# 顶部常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SIZE = 60
PLAYER_Y = SCREEN_HEIGHT - 40 - PLAYER_SIZE
PLAYER_SPEED = 7
OBSTACLE_SIZE = 40
OBSTACLE_Y = -OBSTACLE_SIZE
OBSTACLE_SPEED_MIN = 4
OBSTACLE_SPEED_MAX = 8
OBSTACLE_SPAWN_RATE = 40
PLAYER_COLOR = (0, 255, 0)
OBSTACLE_COLOR = (255, 0, 0)
BACKGROUNDCOLOR = (50, 50, 50)
TEXT_COLOR = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge Blocks Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

def reset_game():
    player_x = (SCREEN_WIDTH - PLAYER_SIZE) // 2
    obstacles = []
    score = 0
    frame_count = 0
    start_time = pygame.time.get_ticks()
    game_over = False
    
    return player_x, obstacles, score, frame_count, start_time, game_over

def main():
    random.seed(42)
    
    player_x, obstacles, score, frame_count, start_time, game_over = reset_game()
    
    running = True
    while running:
        # 时间控制
        dt = clock.tick(FPS)
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    player_x, obstacles, score, frame_count, start_time, game_over = reset_game()
        
        if not game_over:
            # 更新帧计数器
            frame_count += 1
            
            # 计算存活时间（秒）并更新分数
            current_time = pygame.time.get_ticks()
            elapsed_seconds = (current_time - start_time) // 1000
            score = elapsed_seconds
            
            # 处理玩家移动输入
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_x += PLAYER_SPEED
            
            # 玩家边界限制
            if player_x < 0:
                player_x = 0
            if player_x > SCREEN_WIDTH - PLAYER_SIZE:
                player_x = SCREEN_WIDTH - PLAYER_SIZE
            
            # 生成新障碍物
            if frame_count % OBSTACLE_SPAWN_RATE == 0:
                obstacle_x = random.randint(0, SCREEN_WIDTH - OBSTACLE_SIZE)
                obstacle_speed = random.randint(OBSTACLE_SPEED_MIN, OBSTACLE_SPEED_MAX)
                obstacles.append([obstacle_x, OBSTACLE_Y, obstacle_speed])
            
            # 更新障碍物位置
            for obstacle in obstacles[:]:
                obstacle[1] += obstacle[2]
                if obstacle[1] > SCREEN_HEIGHT:  # 移除出屏幕的障碍物
                    obstacles.remove(obstacle)
            
            # 碰撞检测
            player_rect = pygame.Rect(player_x, PLAYER_Y, PLAYER_SIZE, PLAYER_SIZE)
            for obstacle in obstacles:
                obstacle_rect = pygame.Rect(obstacle[0], obstacle[1], OBSTACLE_SIZE, OBSTACLE_SIZE)
                if player_rect.colliderect(obstacle_rect):
                    game_over = True
        
        # 绘制
        screen.fill(BACKGROUNDCOLOR)
        
        # 绘制玩家
        pygame.draw.rect(screen, PLAYER_COLOR, (player_x, PLAYER_Y, PLAYER_SIZE, PLAYER_SIZE))
        
        # 绘制障碍物
        for obstacle in obstacles:
            pygame.draw.rect(screen, OBSTACLE_COLOR, (obstacle[0], obstacle[1], OBSTACLE_SIZE, OBSTACLE_SIZE))
        
        # 绘制HUD（分数）
        score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))
        
        if game_over:
            # 绘制游戏结束画面
            game_over_text = font.render("Game Over", True, TEXT_COLOR)
            score_final_text = font.render(f"Final Score: {score}", True, TEXT_COLOR)
            restart_text = small_font.render("Press R to Restart", True, TEXT_COLOR)
            
            # 居中显示
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            screen.blit(score_final_text, (SCREEN_WIDTH // 2 - score_final_text.get_width() // 2, SCREEN_HEIGHT // 2))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()