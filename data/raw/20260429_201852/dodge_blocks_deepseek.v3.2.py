import pygame
import random
import sys

# 初始化
pygame.init()
random.seed(42)

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SIZE = 60
PLAYER_SPEED = 7
OBSTACLE_SIZE = 40
OBSTACLE_SPAWN_RATE = 40
OBSTACLE_MIN_SPEED = 4
OBSTACLE_MAX_SPEED = 8
PLAYER_BOTTOM_MARGIN = 40

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 100)
BLUE = (50, 100, 255)
PURPLE = (200, 100, 255)
YELLOW = (255, 255, 50)

# 初始化屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge Blocks Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - PLAYER_BOTTOM_MARGIN
        self.color = GREEN
    
    def move(self, dx):
        self.rect.x += dx
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
    
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)

class Obstacle:
    def __init__(self, x, speed):
        self.rect = pygame.Rect(x, -OBSTACLE_SIZE, OBSTACLE_SIZE, OBSTACLE_SIZE)
        self.speed = speed
        self.color = RED
    
    def update(self):
        self.rect.y += self.speed
    
    def is_offscreen(self):
        return self.rect.top > SCREEN_HEIGHT
    
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)

class Game:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.player = Player()
        self.obstacles = []
        self.frame_count = 0
        self.score = 0
        self.game_over = False
    
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
        
        if not self.game_over:
            keys = pygame.key.get_pressed()
            dx = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += PLAYER_SPEED
            self.player.move(dx)
    
    def update(self):
        if self.game_over:
            return
        
        self.frame_count += 1
        self.score = self.frame_count // FPS
        
        # 生成障碍物
        if self.frame_count % OBSTACLE_SPAWN_RATE == 0:
            x = random.randint(0, SCREEN_WIDTH - OBSTACLE_SIZE)
            speed = random.randint(OBSTACLE_MIN_SPEED, OBSTACLE_MAX_SPEED)
            self.obstacles.append(Obstacle(x, speed))
        
        # 更新障碍物
        for obstacle in self.obstacles[:]:
            obstacle.update()
            if obstacle.is_offscreen():
                self.obstacles.remove(obstacle)
            elif obstacle.rect.colliderect(self.player.rect):
                self.game_over = True
    
    def draw(self):
        screen.fill(BLACK)
        
        # 绘制玩家
        self.player.draw()
        
        # 绘制障碍物
        for obstacle in self.obstacles:
            obstacle.draw()
        
        # 绘制HUD
        score_text = font.render(f"Score: {self.score}", True, YELLOW)
        screen.blit(score_text, (10, 10))
        
        if self.game_over:
            # 半透明覆盖层
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            # 游戏结束文本
            game_over_text = font.render("GAME OVER", True, WHITE)
            score_final_text = font.render(f"Final Score: {self.score}", True, YELLOW)
            restart_text = font.render("Press R to Restart", True, GREEN)
            
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            screen.blit(score_final_text, (SCREEN_WIDTH // 2 - score_final_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        
        # 绘制边框
        pygame.draw.rect(screen, BLUE, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 4)
        
        pygame.display.flip()
    
    def run(self):
        self.handle_events()
        self.update()
        self.draw()

def main():
    game = Game()
    while True:
        game.run()
        clock.tick(FPS)

if __name__ == "__main__":
    main()