import pygame
import random

# 初始化pygame
pygame.init()

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 颜色定义
BACKGROUND_COLOR = (30, 30, 40)
PLAYER_COLOR = (70, 190, 255)
OBSTACLE_COLOR = (230, 80, 80)
TEXT_COLOR = (255, 255, 255)
HUD_COLOR = (100, 200, 100)

# 玩家属性
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 60
PLAYER_Y = SCREEN_HEIGHT - 40 - PLAYER_HEIGHT
PLAYER_SPEED = 7

# 障碍物属性
OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 40
OBSTACLE_SPAWN_RATE = 40  # 每40帧生成一个障碍物
OBSTACLE_MIN_SPEED = 4
OBSTACLE_MAX_SPEED = 8

# 重置随机种子
random.seed(42)

# 创建屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge Blocks Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

def main():
    running = True
    game_over = False
    score = 0
    frames = 0
    current_time = 0
    
    # 初始化玩家位置
    player_x = (SCREEN_WIDTH - PLAYER_WIDTH) // 2
    player_y = PLAYER_Y
    
    obstacles = []
    keys_pressed = set()
    
    while running:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    # 重新开始游戏
                    player_x = (SCREEN_WIDTH - PLAYER_WIDTH) // 2
                    player_y = PLAYER_Y
                    obstacles.clear()
                    score = 0
                    frames = 0
                    current_time = 0
                    game_over = False
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    keys_pressed.add("left")
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    keys_pressed.add("right")
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    keys_pressed.discard("left")
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    keys_pressed.discard("right")
        
        # 游戏逻辑更新
        if not game_over:
            # 更新玩家位置
            if "left" in keys_pressed and player_x > 0:
                player_x -= PLAYER_SPEED
            if "right" in keys_pressed and player_x < SCREEN_WIDTH - PLAYER_WIDTH:
                player_x += PLAYER_SPEED
            
            # 更新帧计数
            frames += 1
            
            # 每1秒（60帧）加1分
            if frames % FPS == 0:
                score += 1
            
            # 生成障碍物
            if frames % OBSTACLE_SPAWN_RATE == 0:
                obstacle_x = random.randint(0, SCREEN_WIDTH - OBSTACLE_WIDTH)
                obstacle_y = -OBSTACLE_HEIGHT
                obstacle_speed = random.randint(OBSTACLE_MIN_SPEED, OBSTACLE_MAX_SPEED)
                obstacles.append([obstacle_x, obstacle_y, obstacle_speed])
            
            # 更新障碍物位置并移除超出屏幕的障碍物
            i = len(obstacles) - 1
            while i >= 0:
                obstacle = obstacles[i]
                obstacle[1] += obstacle[2]
                if obstacle[1] > SCREEN_HEIGHT:
                    obstacles.pop(i)
                i -= 1
            
            # 碰撞检测
            player_rect = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
            for obstacle in obstacles:
                obstacle_rect = pygame.Rect(obstacle[0], obstacle[1], OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
                if player_rect.colliderect(obstacle_rect):
                    game_over = True
        
        # 绘制
        screen.fill(BACKGROUND_COLOR)
        
        # 绘制障碍物
        for obstacle in obstacles:
            pygame.draw.rect(screen, OBSTACLE_COLOR, (obstacle[0], obstacle[1], OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
        
        # 绘制玩家
        pygame.draw.rect(screen, PLAYER_COLOR, (player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT))
        
        # 绘制HUD
        score_text = font.render(f"Score: {score}", True, HUD_COLOR)
        screen.blit(score_text, (10, 10))
        
        # 游戏结束提示
        if game_over:
            game_over_text = font.render("GAME OVER", True, (255, 255, 255))
            score_end_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
            restart_text = small_font.render("Press R to Restart", True, (200, 200, 200))
            
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
            screen.blit(score_end_text, (SCREEN_WIDTH//2 - score_end_text.get_width()//2, SCREEN_HEIGHT//2))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()