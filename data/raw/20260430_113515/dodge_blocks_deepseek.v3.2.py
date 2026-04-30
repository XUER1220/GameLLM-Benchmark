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
GAME_FONT = None

# 颜色定义
BACKGROUND_COLOR = (20, 30, 50)
PLAYER_COLOR = (70, 200, 100)
OBSTACLE_COLOR = (220, 80, 60)
TEXT_COLOR = (240, 240, 240)
GAME_OVER_BG_COLOR = (0, 0, 0, 180)  # RGBA 半透明黑色

# 玩家常量
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 60
PLAYER_Y = SCREEN_HEIGHT - PLAYER_HEIGHT - 40
PLAYER_SPEED = 7

# 障碍物常量
OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 40
OBSTACLE_MIN_SPEED = 4
OBSTACLE_MAX_SPEED = 8
OBSTACLE_SPAWN_INTERVAL = 40

class Player:
    def __init__(self):
        self.rect = pygame.Rect(0, PLAYER_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.rect.centerx = SCREEN_WIDTH // 2

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - PLAYER_WIDTH))

    def draw(self, screen):
        pygame.draw.rect(screen, PLAYER_COLOR, self.rect)

class Obstacle:
    def __init__(self):
        self.width = OBSTACLE_WIDTH
        self.height = OBSTACLE_HEIGHT
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = -self.height
        self.speed = random.randint(OBSTACLE_MIN_SPEED, OBSTACLE_MAX_SPEED)

    def update(self):
        self.y += self.speed
        return self.y > SCREEN_HEIGHT

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        pygame.draw.rect(screen, OBSTACLE_COLOR, self.get_rect())

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dodge Blocks Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 32)
        self.small_font = pygame.font.SysFont("Arial", 24)
        self.reset_game()

    def reset_game(self):
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
                    self.reset_game()
        return pygame.key.get_pressed()

    def update(self, keys):
        if self.game_over:
            return

        self.frame_count += 1
        self.score = self.frame_count // FPS

        self.player.update(keys)

        self.spawn_timer += 1
        if self.spawn_timer >= OBSTACLE_SPAWN_INTERVAL:
            self.obstacles.append(Obstacle())
            self.spawn_timer = 0

        for obstacle in self.obstacles[:]:
            if obstacle.update():
                self.obstacles.remove(obstacle)
            elif self.player.rect.colliderect(obstacle.get_rect()):
                self.game_over = True

    def draw_hud(self):
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(GAME_OVER_BG_COLOR)
            self.screen.blit(overlay, (0, 0))
            game_over_text = self.font.render("Game Over", True, TEXT_COLOR)
            final_score_text = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            restart_text = self.small_font.render("Press R to Restart", True, TEXT_COLOR)
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 10))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.player.draw(self.screen)
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        self.draw_hud()
        pygame.display.flip()

    def run(self):
        while True:
            keys = self.handle_events()
            self.update(keys)
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()