import pygame
import random
import sys

# 初始化
pygame.init()
random.seed(42)

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

PLAYER_WIDTH = 60
PLAYER_HEIGHT = 60
PLAYER_SPEED = 7
PLAYER_Y = SCREEN_HEIGHT - PLAYER_HEIGHT - 40
PLAYER_INIT_X = (SCREEN_WIDTH - PLAYER_WIDTH) // 2

OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 40
OBSTACLE_MIN_SPEED = 4
OBSTACLE_MAX_SPEED = 8
OBSTACLE_SPAWN_INTERVAL = 40

# 颜色
BG_COLOR = (30, 30, 50)
PLAYER_COLOR = (100, 200, 255)
OBSTACLE_COLOR = (255, 100, 100)
TEXT_COLOR = (255, 255, 255)
HUD_COLOR = (200, 200, 200)
GAME_OVER_BG = (0, 0, 0, 180)  # 半透明黑色

# 创建窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge Blocks Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(PLAYER_INIT_X, PLAYER_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
    
    def move(self, dx):
        self.rect.x += dx
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - PLAYER_WIDTH))
    
    def draw(self):
        pygame.draw.rect(screen, PLAYER_COLOR, self.rect)

class Obstacle:
    def __init__(self, x, speed):
        self.rect = pygame.Rect(x, -OBSTACLE_HEIGHT, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
        self.speed = speed
    
    def update(self):
        self.rect.y += self.speed
        return self.rect.y > SCREEN_HEIGHT
    
    def draw(self):
        pygame.draw.rect(screen, OBSTACLE_COLOR, self.rect)

class Game:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.player = Player()
        self.obstacles = []
        self.game_over = False
        self.score = 0
        self.frame_count = 0
        self.spawn_timer = 0
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r and self.game_over:
                    self.reset()
    
    def update(self):
        if self.game_over:
            return
        
        self.frame_count += 1
        # 每帧增加分数（60帧约1秒加1分）
        self.score = self.frame_count // FPS
        
        # 生成障碍物
        self.spawn_timer += 1
        if self.spawn_timer >= OBSTACLE_SPAWN_INTERVAL:
            self.spawn_timer = 0
            x = random.randint(0, SCREEN_WIDTH - OBSTACLE_WIDTH)
            speed = random.randint(OBSTACLE_MIN_SPEED, OBSTACLE_MAX_SPEED)
            self.obstacles.append(Obstacle(x, speed))
        
        # 更新障碍物
        self.obstacles = [obs for obs in self.obstacles if not obs.update()]
        
        # 碰撞检测
        for obs in self.obstacles:
            if self.player.rect.colliderect(obs.rect):
                self.game_over = True
                break
    
    def draw(self):
        screen.fill(BG_COLOR)
        
        # 绘制障碍物
        for obs in self.obstacles:
            obs.draw()
        
        # 绘制玩家
        self.player.draw()
        
        # 绘制HUD
        score_text = font.render(f"Score: {self.score}", True, HUD_COLOR)
        screen.blit(score_text, (10, 10))
        
        # 游戏结束画面
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(GAME_OVER_BG)
            screen.blit(overlay, (0, 0))
            
            game_over_text = font.render("Game Over", True, TEXT_COLOR)
            score_text = font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            restart_text = font.render("Press R to Restart", True, TEXT_COLOR)
            
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
            screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 - 20))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
    
    def run(self):
        while True:
            self.handle_events()
            
            # 玩家移动
            keys = pygame.key.get_pressed()
            dx = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += PLAYER_SPEED
            self.player.move(dx)
            
            self.update()
            self.draw()
            
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()