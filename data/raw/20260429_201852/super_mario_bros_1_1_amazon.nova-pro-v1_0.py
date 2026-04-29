import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WORLD_WIDTH = 3200
GRAVITY = 0.5
JUMP_SPEED = -12
MOVE_SPEED = 5

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GRAY = (169, 169, 169)
BLACK = (0, 0, 0)

PLAYER_SIZE = (32, 48)
COIN_SIZE = (18, 18)
ENEMY_SIZE = (32, 32)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario Bros 1-1 Medium")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface(PLAYER_SIZE)
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = SCREEN_HEIGHT - PLAYER_SIZE[1]
        self.vel_y = 0
        self.lives = 3
        self.score = 0
        self.coins = 0

    def update(self, platforms, coins, enemies, flag):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= MOVE_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += MOVE_SPEED
        if keys[pygame.K_SPACE] and self.vel_y == 0:
            self.vel_y = JUMP_SPEED

        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = 0

        self.rect.x = max(0, min(self.rect.x, WORLD_WIDTH - PLAYER_SIZE[0]))

        if pygame.sprite.spritecollide(self, coins, True):
            self.score += 100
            self.coins += 1

        if pygame.sprite.spritecollide(self, enemies, True):
            self.score += 200

        for enemy in enemies:
            if pygame.sprite.collide_rect(self, enemy):
                self.lives -= 1
                self.rect.x = max(0, self.rect.x - 100)
                self.vel_y = 0
                break

        if pygame.sprite.collide_rect(self, flag):
            return True

        if self.lives <= 0:
            return False

        return None

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
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface(ENEMY_SIZE)
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1

    def update(self):
        self.rect.x += self.direction * MOVE_SPEED
        if self.rect.right > WORLD_WIDTH or self.rect.left < 0:
            self.direction *= -1

class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((18, 96))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def draw_hud(player):
    lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
    score_text = font.render(f"Score: {player.score}", True, WHITE)
    coins_text = font.render(f"Coins: {player.coins}", True, WHITE)
    screen.blit(lives_text, (10, 10))
    screen.blit(score_text, (10, 50))
    screen.blit(coins_text, (10, 90))

def main():
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)

    platform_positions = [
        (0, SCREEN_HEIGHT - 50, 3200, 50, BROWN),
        (300, SCREEN_HEIGHT - 150, 100, 50, GRAY),
        (1000, SCREEN_HEIGHT - 150, 100, 50, GRAY),
        (1500, SCREEN_HEIGHT - 250, 100, 50, GRAY),
        (2000, SCREEN_HEIGHT - 150, 100, 50, GRAY),
    ]

    for pos in platform_positions:
        platform = Platform(*pos)
        platforms.add(platform)
        all_sprites.add(platform)

    coin_positions = [
        (50, SCREEN_HEIGHT - 100), (150, SCREEN_HEIGHT - 100), (250, SCREEN_HEIGHT - 100),
        (1100, SCREEN_HEIGHT - 200), (1200, SCREEN_HEIGHT - 200), (1300, SCREEN_HEIGHT - 200),
        (1600, SCREEN_HEIGHT - 200), (1700, SCREEN_HEIGHT - 200), (1800, SCREEN_HEIGHT - 200),
        (2100, SCREEN_HEIGHT - 200), (2200, SCREEN_HEIGHT - 200), (2300, SCREEN_HEIGHT - 200),
    ]

    for pos in coin_positions:
        coin = Coin(*pos)
        coins.add(coin)
        all_sprites.add(coin)

    enemy_positions = [
        (500, SCREEN_HEIGHT - 82), (1000, SCREEN_HEIGHT - 82), (1500, SCREEN_HEIGHT - 82),
    ]

    for pos in enemy_positions:
        enemy = Enemy(*pos)
        enemies.add(enemy)
        all_sprites.add(enemy)

    flag = Flag(3100, SCREEN_HEIGHT - 146)
    all_sprites.add(flag)

    running = True
    game_over = False
    win = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and (game_over or win):
                    main()

        screen.fill(BLACK)

        result = player.update(platforms, coins, enemies, flag)
        if result is not None:
            game_over = not result
            win = result

        for platform in platforms:
            screen.blit(platform.image, platform.rect)
        for coin in coins:
            screen.blit(coin.image, coin.rect)
        for enemy in enemies:
            enemy.update()
            screen.blit(enemy.image, enemy.rect)
        screen.blit(player.image, player.rect)
        screen.blit(flag.image, flag.rect)

        draw_hud(player)

        if game_over:
            game_over_text = font.render("Game Over", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
        elif win:
            win_text = font.render("You Win", True, WHITE)
            screen.blit(win_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 50))
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()