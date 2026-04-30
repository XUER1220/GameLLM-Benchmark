import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SIZE = (32, 48)
COIN_SIZE = (18, 18)
ENEMY_SIZE = (32, 32)
GRAVITY = 0.5
JUMP_SPEED = -12
MOVE_SPEED = 5
WORLD_WIDTH = 3200
WORLD_HEIGHT = 600
PLAYER_LIVES = 3

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario Bros Medium")
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface(PLAYER_SIZE)
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = SCREEN_HEIGHT - self.rect.height
        self.vel_y = 0
        self.lives = PLAYER_LIVES
        self.score = 0
        self.coins = 0

    def update(self, platforms, coins, enemies, goal):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= MOVE_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += MOVE_SPEED
        if keys[pygame.K_SPACE] and self.rect.bottom == SCREEN_HEIGHT:
            self.vel_y = JUMP_SPEED

        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = 0

        if pygame.sprite.spritecollide(self, coins, True):
            self.coins += 1
            self.score += 100

        if pygame.sprite.spritecollide(self, enemies, True):
            self.score += 200

        if pygame.sprite.spritecollide(self, enemies, False):
            self.lives -= 1
            self.rect.x = max(0, min(self.rect.x, WORLD_WIDTH - self.rect.width))

        if pygame.sprite.spritecollide(self, goal, False):
            return "win"

        if self.rect.top > SCREEN_HEIGHT:
            self.lives -= 1
            self.rect.x = max(0, min(self.rect.x, WORLD_WIDTH - self.rect.width))
            self.rect.y = SCREEN_HEIGHT - self.rect.height
            self.vel_y = 0

        return "continue"

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface(COIN_SIZE)
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface(ENEMY_SIZE)
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1

    def update(self):
        self.rect.x += self.direction * MOVE_SPEED
        if self.rect.right >= WORLD_WIDTH or self.rect.left <= 0:
            self.direction *= -1

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def draw_hud(player):
    font = pygame.font.Font(None, 36)
    lives_text = font.render(f"Lives: {player.lives}", True, (255, 255, 255))
    score_text = font.render(f"Score: {player.score}", True, (255, 255, 255))
    coins_text = font.render(f"Coins: {player.coins}", True, (255, 255, 255))
    screen.blit(lives_text, (10, 10))
    screen.blit(score_text, (10, 50))
    screen.blit(coins_text, (10, 90))

def main():
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    goal = pygame.sprite.GroupSingle()

    platform_positions = [
        (0, SCREEN_HEIGHT - 50, 3200, 50, (0, 128, 0)),
        (100, SCREEN_HEIGHT - 150, 100, 50, (139, 69, 19)),
        (300, SCREEN_HEIGHT - 150, 100, 50, (139, 69, 19)),
        (600, SCREEN_HEIGHT - 150, 100, 50, (139, 69, 19)),
        (900, SCREEN_HEIGHT - 150, 100, 50, (139, 69, 19)),
        (1200, SCREEN_HEIGHT - 150, 100, 50, (139, 69, 19)),
        (1500, SCREEN_HEIGHT - 150, 100, 50, (139, 69, 19)),
        (1800, SCREEN_HEIGHT - 150, 100, 50, (139, 69, 19)),
        (2100, SCREEN_HEIGHT - 150, 100, 50, (139, 69, 19)),
        (2400, SCREEN_HEIGHT - 150, 100, 50, (139, 69, 19)),
        (2700, SCREEN_HEIGHT - 150, 100, 50, (139, 69, 19)),
        (3000, SCREEN_HEIGHT - 150, 100, 50, (139, 69, 19))
    ]

    for pos in platform_positions:
        platforms.add(Platform(*pos))

    coin_positions = [
        (50, SCREEN_HEIGHT - 100),
        (150, SCREEN_HEIGHT - 100),
        (250, SCREEN_HEIGHT - 100),
        (450, SCREEN_HEIGHT - 100),
        (550, SCREEN_HEIGHT - 100),
        (650, SCREEN_HEIGHT - 100),
        (850, SCREEN_HEIGHT - 100),
        (950, SCREEN_HEIGHT - 100),
        (1050, SCREEN_HEIGHT - 100),
        (1250, SCREEN_HEIGHT - 100),
        (1350, SCREEN_HEIGHT - 100),
        (1450, SCREEN_HEIGHT - 100)
    ]

    for pos in coin_positions:
        coins.add(Coin(*pos))

    enemy_positions = [
        (200, SCREEN_HEIGHT - 82),
        (700, SCREEN_HEIGHT - 82),
        (1000, SCREEN_HEIGHT - 82)
    ]

    for pos in enemy_positions:
        enemies.add(Enemy(*pos))

    goal.add(Goal(3100, SCREEN_HEIGHT - 150, 50, 150))

    player = Player()

    game_over = False
    game_win = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    main()

        if not game_over and not game_win:
            screen.fill((0, 0, 0))
            platforms.draw(screen)
            coins.draw(screen)
            enemies.update()
            enemies.draw(screen)
            goal.draw(screen)
            screen.blit(player.image, player.rect)

            result = player.update(platforms, coins, enemies, goal)
            if result == "win":
                game_win = True
            elif player.lives <= 0:
                game_over = True

            draw_hud(player)

            camera_x = max(0, min(player.rect.x - SCREEN_WIDTH // 2, WORLD_WIDTH - SCREEN_WIDTH))
            for platform in platforms:
                platform.rect.x = platform.rect_orig.x - camera_x
            for coin in coins:
                coin.rect.x = coin.rect_orig.x - camera_x
            for enemy in enemies:
                enemy.rect.x = enemy.rect_orig.x - camera_x
            goal.sprite.rect.x = goal.sprite.rect_orig.x - camera_x

        else:
            screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 74)
            if game_win:
                text = font.render("You Win", True, (255, 255, 255))
            else:
                text = font.render("Game Over", True, (255, 255, 255))
            score_text = font.render(f"Score: {player.score}", True, (255, 255, 255))
            restart_text = font.render("Press R to Restart", True, (255, 255, 255))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()