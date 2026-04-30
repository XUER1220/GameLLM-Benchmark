import pygame
import random

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
JUMP_SPEED = -12
MOVE_SPEED = 5

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

PLAYER_SIZE = (32, 48)
COIN_SIZE = (18, 18)
ENEMY_SIZE = (32, 32)
BRICK_SIZE = (32, 32)
PIPE_SIZE = (32, 64)
FLAG_SIZE = (16, 96)

WORLD_WIDTH = 3200
WORLD_HEIGHT = 600

player_img = pygame.Surface(PLAYER_SIZE)
player_img.fill(RED)
coin_img = pygame.Surface(COIN_SIZE)
coin_img.fill(YELLOW)
enemy_img = pygame.Surface(ENEMY_SIZE)
enemy_img.fill(BLACK)
brick_img = pygame.Surface(BRICK_SIZE)
brick_img.fill(BLUE)
pipe_img = pygame.Surface(PIPE_SIZE)
pipe_img.fill(GREEN)
flag_img = pygame.Surface(FLAG_SIZE)
flag_img.fill(WHITE)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario Bros Medium")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = WORLD_HEIGHT - self.rect.height
        self.vel_y = 0

    def update(self, keys, platforms, coins, enemies, flag):
        self.rect.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * MOVE_SPEED
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        if self.rect.bottom > WORLD_HEIGHT:
            self.rect.bottom = WORLD_HEIGHT
            self.vel_y = 0

        if keys[pygame.K_SPACE]:
            self.jump()

        self.check_collision(platforms)
        self.check_collision(coins, True)
        self.check_collision(enemies)
        self.check_flag(flag)

    def jump(self):
        self.vel_y = JUMP_SPEED

    def check_collision(self, sprites, collect=False):
        hit_list = pygame.sprite.spritecollide(self, sprites, collect)
        for hit in hit_list:
            if collect:
                global score, coins_collected
                score += 100
                coins_collected += 1
            else:
                if self.vel_y > 0:
                    self.rect.bottom = hit.rect.top
                    self.vel_y = 0

    def check_flag(self, flag):
        if self.rect.colliderect(flag.rect):
            game_won()

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
        self.image = coin_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_img
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
        self.image = flag_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def setup_game():
    global player, platforms, coins, enemies, flag, score, lives, coins_collected
    player = Player()
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    flag = Flag(WORLD_WIDTH - FLAG_SIZE[0], WORLD_HEIGHT - FLAG_SIZE[1])

    for x in range(0, WORLD_WIDTH, BRICK_SIZE[0]):
        platforms.add(Platform(x, WORLD_HEIGHT - BRICK_SIZE[1], BRICK_SIZE[0], BRICK_SIZE[1], BLUE))

    for _ in range(12):
        coins.add(Coin(random.randint(0, WORLD_WIDTH - COIN_SIZE[0]), random.randint(100, WORLD_HEIGHT - COIN_SIZE[1])))

    for _ in range(3):
        enemies.add(Enemy(random.randint(0, WORLD_WIDTH - ENEMY_SIZE[0]), WORLD_HEIGHT - ENEMY_SIZE[1]))

    platforms.add(Platform(400, 400, PIPE_SIZE[0], PIPE_SIZE[1], GREEN))
    platforms.add(Platform(800, 300, PIPE_SIZE[0], PIPE_SIZE[1], GREEN))
    platforms.add(Platform(1200, 200, PIPE_SIZE[0], PIPE_SIZE[1], GREEN))

    score = 0
    lives = 3
    coins_collected = 0

def draw_hud():
    screen.blit(font.render(f"Lives: {lives}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 40))
    screen.blit(font.render(f"Coins: {coins_collected}", True, WHITE), (10, 70))

def game_won():
    global running
    running = False
    end_game("You Win")

def game_over():
    global running
    running = False
    end_game("Game Over")

def end_game(message):
    screen.fill(BLACK)
    screen.blit(font.render(message, True, WHITE), (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 20))
    screen.blit(font.render(f"Score: {score}", True, WHITE), (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 20))
    screen.blit(font.render("Press R to Restart", True, WHITE), (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    setup_game()
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

setup_game()
running = True

while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    keys = pygame.key.get_pressed()

    screen.fill(BLACK)
    camera_x = max(0, min(player.rect.x - SCREEN_WIDTH // 2, WORLD_WIDTH - SCREEN_WIDTH))
    screen.blit(player.image, (player.rect.x - camera_x, player.rect.y))
    platforms.draw(screen)
    for platform in platforms:
        screen.blit(platform.image, (platform.rect.x - camera_x, platform.rect.y))
    coins.draw(screen)
    for coin in coins:
        screen.blit(coin.image, (coin.rect.x - camera_x, coin.rect.y))
    enemies.draw(screen)
    for enemy in enemies:
        screen.blit(enemy.image, (enemy.rect.x - camera_x, enemy.rect.y))
    screen.blit(flag.image, (flag.rect.x - camera_x, flag.rect.y))

    player.update(keys, platforms, coins, enemies, flag)
    enemies.update()

    draw_hud()

    pygame.display.flip()

    if lives <= 0:
        game_over()

pygame.quit()