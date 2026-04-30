import pygame
import random
import sys

# 初始化随机种子
random.seed(42)

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 颜色常量
BACKGROUND_COLOR = (30, 30, 50)
PLAYER_COLOR = (70, 200, 100)
OBSTACLE_COLOR = (220, 80, 60)
TEXT_COLOR = (240, 240, 240)
GAME_OVER_BG_COLOR = (20, 20, 40, 200)  # 半透明背景

# 玩家常量
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 60
PLAYER_SPEED = 7
PLAYER_INIT_X = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
PLAYER_INIT_Y = SCREEN_HEIGHT - PLAYER_HEIGHT - 40

# 障碍物常量
OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 40
OBSTACLE_MIN_SPEED = 4
OBSTACLE_MAX_SPEED = 8
OBSTACLE_SPAWN_INTERVAL = 40  # 每40帧生成一个

# 游戏状态
class GameState:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.player_rect = pygame.Rect(PLAYER_INIT_X, PLAYER_INIT_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.obstacles = []
        self.game_over = False
        self.frame_count = 0
        self.score = 0
        self.last_spawn_frame = 0

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Dodge Blocks Easy")
    clock = pygame.time.Clock()
    
    # 初始化字体
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 28)
    
    # 游戏状态
    state = GameState()
    
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
                    state.reset()
        
        if not state.game_over:
            # 处理玩家输入
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                state.player_rect.x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                state.player_rect.x += PLAYER_SPEED
            
            # 限制玩家在屏幕内
            state.player_rect.x = max(0, min(state.player_rect.x, SCREEN_WIDTH - PLAYER_WIDTH))
            
            # 更新帧计数和分数
            state.frame_count += 1
            state.score = state.frame_count // FPS  # 每秒1分
            
            # 生成新障碍物
            if state.frame_count - state.last_spawn_frame >= OBSTACLE_SPAWN_INTERVAL:
                x = random.randint(0, SCREEN_WIDTH - OBSTACLE_WIDTH)
                speed = random.randint(OBSTACLE_MIN_SPEED, OBSTACLE_MAX_SPEED)
                state.obstacles.append({
                    'rect': pygame.Rect(x, -OBSTACLE_HEIGHT, OBSTACLE_WIDTH, OBSTACLE_HEIGHT),
                    'speed': speed
                })
                state.last_spawn_frame = state.frame_count
            
            # 更新障碍物位置
            new_obstacles = []
            for obstacle in state.obstacles:
                obstacle['rect'].y += obstacle['speed']
                
                # 只保留还在屏幕内的障碍物
                if obstacle['rect'].y < SCREEN_HEIGHT:
                    new_obstacles.append(obstacle)
                    
                    # 检测碰撞
                    if state.player_rect.colliderect(obstacle['rect']):
                        state.game_over = True
            state.obstacles = new_obstacles
        
        # 绘制
        screen.fill(BACKGROUND_COLOR)
        
        # 绘制玩家
        pygame.draw.rect(screen, PLAYER_COLOR, state.player_rect)
        
        # 绘制障碍物
        for obstacle in state.obstacles:
            pygame.draw.rect(screen, OBSTACLE_COLOR, obstacle['rect'])
        
        # 绘制HUD
        score_text = font.render(f"Score: {state.score}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))
        
        # 游戏结束画面
        if state.game_over:
            # 半透明覆盖层
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(GAME_OVER_BG_COLOR)
            screen.blit(overlay, (0, 0))
            
            # 游戏结束文本
            game_over_text = font.render("GAME OVER", True, TEXT_COLOR)
            final_score_text = font.render(f"Final Score: {state.score}", True, TEXT_COLOR)
            restart_text = small_font.render("Press R to Restart", True, TEXT_COLOR)
            
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 10))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()