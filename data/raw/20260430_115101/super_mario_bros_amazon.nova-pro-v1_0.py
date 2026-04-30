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
PLAYER_LIVES = 3

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GRAY = (169, 169, 169)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario Bros Medium")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface(PLAYER_SIZE)
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 400
        self.change_y = 0
        self.on_ground = False
        self.lives = PLAYER_LIVES
        self.score = 0
        self.coins = 0

    def update(self):
        self.change_y += GRAVITY
        self.rect.y += self.change_y

        if self.rect.y > SCREEN_HEIGHT:
            self.rect.y = SCREEN_HEIGHT
            self.change_y = 0
            self.on_ground = True
            self.lives -= 1
            self.rect.x = 0
            self.rect.y = 400

        if self.rect.y < 0:
            self.rect.y = 0
            self.change_y = 0

        if self.rect.colliderect(flag_pole.rect):
            self.lives = 0
            self.score = 9999

    def jump(self):
        if self.on_ground:
            self.change_y = JUMP_SPEED
            self.on_ground = False

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
        self.change_x = MOVE_SPEED

    def update(self):
        self.rect.x += self.change_x
        if self.rect.right > 3200 or self.rect.left < 0:
            self.change_x = -self.change_x

class FlagPole(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 100))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
coins = pygame.sprite.Group()
enemies = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

for p in [(0, 550, 3200, 50, BROWN), (100, 450, 100, 50, GRAY), (300, 400, 100, 50, GRAY),
          (500, 350, 100, 50, GRAY), (700, 500, 100, 50, GRAY), (900, 450, 100, 50, GRAY),
          (1100, 400, 100, 50, GRAY), (1300, 350, 100, 50, GRAY), (1500, 500, 100, 50, GRAY),
          (1700, 450, 100, 50, GRAY), (1900, 400, 100, 50, GRAY), (2100, 350, 100, 50, GRAY)]:
    platform = Platform(*p)
    platforms.add(platform)
    all_sprites.add(platform)

for c in [(200, 420), (400, 370), (600, 420), (800, 370), (1000, 420), (1200, 370),
          (1400, 420), (1600, 370), (1800, 420), (2000, 370), (2200, 420), (2400, 370)]:
    coin = Coin(*c)
    coins.add(coin)
    all_sprites.add(coin)

for e in [(300, 400), (700, 400), (1100, 400)]:
    enemy = Enemy(*e)
    enemies.add(enemy)
    all_sprites.add(enemy)

flag_pole = FlagPole(3150, 450)
all_sprites.add(flag_pole)

def game_over():
    screen.fill(BLACK)
    text = font.render(f"Game Over\nScore: {player.score}\nPress R to Restart", True, WHITE)
    screen.blit(text, (300, 250))
    pygame.display.flip()

def you_win():
    screen.fill(BLACK)
    text = font.render(f"You Win\nScore: {player.score}\nPress R to Restart", True, WHITE)
    screen.blit(text, (300, 250))
    pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                player.rect.x = 0
                player.rect.y = 400
                player.lives = PLAYER_LIVES
                player.score = 0
                player.coins = 0
                for enemy in enemies:
                    enemy.rect.x = random.randint(0, 3000)
                for coin in coins:
                    coin.rect.x = random.randint(0, 3000)
                screen.fill(BLACK)
            elif event.key == pygame.K_SPACE and player.on_ground:
                player.jump()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.rect.x -= MOVE_SPEED
    if keys[pygame.K_RIGHT]:
        player.rect.x += MOVE_SPEED

    all_sprites.update()

    hits = pygame.sprite.spritecollide(player, platforms, False)
    if hits:
        if player.change_y > 0:
            player.rect.bottom = hits[0].rect.top
            player.on_ground = True
            player.change_y = 0

    hits = pygame.sprite.spritecollide(player, coins, True)
    for hit in hits:
        player.score += 100
        player.coins += 1

    hits = pygame.sprite.spritecollide(player, enemies, True)
    for hit in hits:
        if player.rect.bottom < hit.rect.centery:
            player.score += 200
        else:
            player.lives -= 1
            player.rect.x = max(0, player.rect.x - 100)

    if player.lives <= 0:
        game_over()
        pygame.time.wait(2000)
        running = False

    if player.score == 9999:
        you_win()
        pygame.time.wait(2000)
        running = False

    screen.fill(BLACK)
    for platform in platforms:
        screen.blit(platform.image, platform.rect)
    for coin in coins:
        screen.blit(coin.image, coin.rect)
    for enemy in enemies:
        screen.blit(enemy.image, enemy.rect)
    screen.blit(player.image, player.rect)
    screen.blit(flag_pole.image, flag_pole.rect)

    lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
    score_text = font.render(f"Score: {player.score}", True, WHITE)
    coins_text = font.render(f"Coins: {player.coins}", True, WHITE)
    screen.blit(lives_text, (10, 10))
    screen.blit(score_text, (10, 50))
    screen.blit(coins_text, (10, 90))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()