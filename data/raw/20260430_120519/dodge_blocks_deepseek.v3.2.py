import pygame
import random
import sys

# 固定参数
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 60
PLAYER_INIT_Y = SCREEN_HEIGHT - PLAYER_HEIGHT - 40
PLAYER_SPEED = 7
OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 40
OBSTACLE_MIN_SPEED = 4
OBSTACLE_MAX_SPEED = 8
OBSTACLE_SPAWN_INTERVAL = 40

# 颜色
COLOR_BG = (20, 30, 50)
COLOR_PLAYER = (80, 180, 255)
COLOR_OBSTACLE = (255, 100, 80)
COLOR_TEXT = (240, 240, 240)
COLOR_OVERLAY_BG = (20, 20, 40, 200)
COLOR_HUD = (200, 230, 255)

# 随机种子
random.seed(42)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = PLAYER_INIT_Y
        
    def move(self, dx):
        self.rect.x += dx
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, SCREEN_WIDTH)
    
    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_PLAYER, self.rect, border_radius=8)

class Obstacle:
    def __init__(self, x):
        self.rect = pygame.Rect(x, -OBSTACLE_HEIGHT, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
        self.speed = random.uniform(OBSTACLE_MIN_SPEED, OBSTACLE_MAX_SPEED)
        
    def update(self):
        self.rect.y += self.speed
        
    def off_screen(self):
        return self.rect.top > SCREEN_HEIGHT
        
    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_OBSTACLE, self.rect, border_radius=6)
        
    def collides_with(self, player_rect):
        return self.rect.colliderect(player_rect)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dodge Blocks Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)
        self.large_font = pygame.font.SysFont(None, 48)
        self.reset_game()
        
    def reset_game(self):
        self.player = Player()
        self.obstacles = []
        self.frames_alive = 0
        self.game_over = False
        self.spawn_timer = 0
        
    def spawn_obstacle(self):
        x = random.randint(0, SCREEN_WIDTH - OBSTACLE_WIDTH)
        self.obstacles.append(Obstacle(x))
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if self.game_over and event.key == pygame.K_r:
                    self.reset_game()
        
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
            
        self.frames_alive += 1
        self.spawn_timer += 1
        
        if self.spawn_timer >= OBSTACLE_SPAWN_INTERVAL:
            self.spawn_obstacle()
            self.spawn_timer = 0
            
        for obs in self.obstacles[:]:
            obs.update()
            if obs.off_screen():
                self.obstacles.remove(obs)
            elif obs.collides_with(self.player.rect):
                self.game_over = True
                break
                
    def draw(self):
        self.screen.fill(COLOR_BG)
        
        # 障碍物
        for obs in self.obstacles:
            obs.draw(self.screen)
            
        # 玩家
        self.player.draw(self.screen)
        
        # HUD
        score = self.frames_alive // FPS
        score_text = self.font.render(f"Time: {score} s", True, COLOR_HUD)
        self.screen.blit(score_text, (10, 10))
        
        if self.game_over:
            # 半透明覆盖层
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(COLOR_OVERLAY_BG)
            self.screen.blit(overlay, (0, 0))
            
            # 游戏结束文本
            game_over_text = self.large_font.render("GAME OVER", True, COLOR_TEXT)
            score_text = self.font.render(f"Survival Time: {score} seconds", True, COLOR_TEXT)
            restart_text = self.small_font.render("Press R to Restart", True, COLOR_TEXT)
            
            # 居中显示
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
            
        pygame.display.flip()
        
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()