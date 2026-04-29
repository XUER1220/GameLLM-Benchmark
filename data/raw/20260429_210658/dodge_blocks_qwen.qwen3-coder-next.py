import pygame
import random
import sys

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SIZE = (60, 60)
PLAYER_Y = SCREEN_HEIGHT - 40
PLAYER_SPEED = 7
OBSTACLE_SIZE = (40, 40)
OBSTACLE_SPEED_MIN = 4
OBSTACLE_SPEED_MAX = 8
OBSTACLE_SPAWN_RATE = 40  # 帧数
SCORE_PER_SECOND = 1

# 颜色定义
BACKGROUND_COLOR = (30, 30, 50)
PLAYER_COLOR = (0, 200, 100)
OBSTACLE_COLOR = (200, 50, 50)
TEXT_COLOR = (255, 255, 255)
GAME_OVER_COLOR = (255, 100, 100)

# 初始化
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge Blocks Easy")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 28)

def main():
    # 固定随机种子
    random.seed(42)
    
    # 游戏状态变量
    running = True
    game_over = False
    frame_count = 0
    score = 0
    
    # 玩家位置
    player_x = (SCREEN_WIDTH - PLAYER_SIZE[0]) // 2
    player_y = PLAYER_Y
    
    # 障碍物列表
    obstacles = []
    
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    # 重新开始游戏
                    player_x = (SCREEN_WIDTH - PLAYER_SIZE[0]) // 2
                    obstacles.clear()
                    score = 0
                    frame_count = 0
                    game_over = False
                elif event.key == pygame.K_r and not game_over:
                    # 若游戏中误触 R，则重置
                    player_x = (SCREEN_WIDTH - PLAYER_SIZE[0]) // 2
                    obstacles.clear()
                    score = 0
                    frame_count = 0
        
        if game_over:
            # 绘制游戏结束画面
            screen.fill(BACKGROUND_COLOR)
            
            # Game Over 文本
            game_over_text = game_over_font.render("GAME OVER", True, GAME_OVER_COLOR)
            screen.blit(game_over_text, game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60)))
            
            # 最终分数
            final_score_text = small_font.render(f"Final Score: {score}", True, TEXT_COLOR)
            screen.blit(final_score_text, final_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
            
            # 重新开始命令
            restart_text = small_font.render("Press R to Restart", True, TEXT_COLOR)
            screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60)))
            
            # 退出命令
            exit_text = small_font.render("Press ESC to Quit", True, TEXT_COLOR)
            screen.blit(exit_text, exit_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50)))
        else:
            # 处理玩家移动
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_x += PLAYER_SPEED
            
            # 边界检查
            player_x = max(0, min(player_x, SCREEN_WIDTH - PLAYER_SIZE[0]))
            
            # 生成障碍物
            if frame_count % OBSTACLE_SPAWN_RATE == 0:
                obstacle_x = random.randint(0, SCREEN_WIDTH - OBSTACLE_SIZE[0])
                obstacle_speed = random.randint(OBSTACLE_SPEED_MIN, OBSTACLE_SPEED_MAX)
                obstacles.append([obstacle_x, -OBSTACLE_SIZE[1], obstacle_speed])
            
            # 更新障碍物位置
            for i in range(len(obstacles) - 1, -1, -1):
                obstacle = obstacles[i]
                obstacle[1] += obstacle[2]  # 更新y坐标
                
                # 移除超出屏幕的障碍物
                if obstacle[1] > SCREEN_HEIGHT:
                    obstacles.pop(i)
            
            # 更新帧计数和分数
            frame_count += 1
            if frame_count % FPS == 0:
                score += SCORE_PER_SECOND
            
            # 碰撞检测
            player_rect = pygame.Rect(player_x, player_y, PLAYER_SIZE[0], PLAYER_SIZE[1])
            for obstacle in obstacles:
                obstacle_rect = pygame.Rect(obstacle[0], obstacle[1], OBSTACLE_SIZE[0], OBSTACLE_SIZE[1])
                if player_rect.colliderect(obstacle_rect):
                    game_over = True
            
            # 绘制画面
            screen.fill(BACKGROUND_COLOR)
            
            # 绘制玩家
            pygame.draw.rect(screen, PLAYER_COLOR, (player_x, player_y, PLAYER_SIZE[0], PLAYER_SIZE[1]))
            
            # 绘制障碍物
            for obstacle in obstacles:
                pygame.draw.rect(screen, OBSTACLE_COLOR, (obstacle[0], obstacle[1], OBSTACLE_SIZE[0], OBSTACLE_SIZE[1]))
            
            # 绘制HUD：分数
            score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
            screen.blit(score_text, (10, 10))
            
            # 群体说明（简单提示）
            hint_text = small_font.render("Use Arrow Keys or A/D to Move", True, TEXT_COLOR)
            screen.blit(hint_text, (SCREEN_WIDTH - hint_text.get_width() - 10, 10))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()