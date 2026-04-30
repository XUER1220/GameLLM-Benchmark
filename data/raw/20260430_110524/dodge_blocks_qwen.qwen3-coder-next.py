import pygame
import random

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 60
PLAYER_Y = SCREEN_HEIGHT - 40
PLAYER_SPEED = 7
OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 40
OBSTACLE_SPEED_MIN = 4
OBSTACLE_SPEED_MAX = 8
OBSTACLE_SPAWN_RATE = 40
SCORE_PER_SECOND = 1
PLAYER_COLOR = (0, 255, 0)
OBSTACLE_COLOR = (255, 0, 0)
BG_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
HUD_BG_COLOR = (0, 0, 0)

# 初始化pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge Blocks Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

# 随机种子
random.seed(42)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(
            (SCREEN_WIDTH - PLAYER_WIDTH) // 2,  # 居中
            PLAYER_Y,
            PLAYER_WIDTH,
            PLAYER_HEIGHT
        )
        self.vel_x = 0
    
    def update(self):
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
        
        self.rect.x += self.vel_x
        # 边界处理
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
    
    def draw(self):
        pygame.draw.rect(screen, PLAYER_COLOR, self.rect)

class Obstacle:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH - OBSTACLE_WIDTH)
        self.y = -OBSTACLE_HEIGHT
        self.speed = random.randint(OBSTACLE_SPEED_MIN, OBSTACLE_SPEED_MAX)
        self.rect = pygame.Rect(self.x, self.y, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
    
    def update(self):
        self.y += self.speed
        self.rect.y = self.y
    
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT
    
    def draw(self):
        pygame.draw.rect(screen, OBSTACLE_COLOR, self.rect)

def main():
    player = Player()
    obstacles = []
    frame_count = 0
    score = 0
    start_time = pygame.time.get_ticks()
    game_over = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    # 重新开始游戏
                    player = Player()
                    obstacles.clear()
                    frame_count = 0
                    score = 0
                    start_time = pygame.time.get_ticks()
                    game_over = False
        
        if game_over:
            # 游戏结束画面
            screen.fill(BG_COLOR)
            game_over_text = font.render("GAME OVER", True, TEXT_COLOR)
            score_text = font.render(f"Final Score: {score}", True, TEXT_COLOR)
            restart_text = small_font.render("Press R to Restart", True, TEXT_COLOR)
            
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 80))
            pygame.display.flip()
            clock.tick(FPS)
            continue
        
        # 更新逻辑
        player.update()
        
        # 生成障碍物
        frame_count += 1
        if frame_count % OBSTACLE_SPAWN_RATE == 0:
            obstacles.append(Obstacle())
        
        # 更新障碍物并检测碰撞
        for obstacle in obstacles[:]:
            obstacle.update()
            if obstacle.is_off_screen():
                obstacles.remove(obstacle)
                continue
            
            if player.rect.colliderect(obstacle.rect):
                game_over = True
        
        # 计算存活时间并更新分数
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - start_time) // 1000
        score = elapsed_seconds * SCORE_PER_SECOND
        
        # 绘制
        screen.fill(BG_COLOR)
        
        # 绘制玩家和障碍物
        player.draw()
        for obstacle in obstacles:
            obstacle.draw()
        
        # 绘制HUD
        score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))
        
        # 键盘提示
        controls_hint = small_font.render("Controls: A/D or Left/Right to move | ESC: Exit | R: Restart", True, TEXT_COLOR)
        screen.blit(controls_hint, (10, SCREEN_HEIGHT - 30))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()