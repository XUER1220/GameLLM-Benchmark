import pygame
import sys
import random

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
PLAYER_SIZE = (40, 56)
COIN_SIZE = (20, 20)
ENEMY_SIZE = (36, 36)
GRAVITY = 0.5
JUMP_STRENGTH = -12
MOVE_SPEED = 5
PLAYER_LIVES = 3

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer Hard")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface(PLAYER_SIZE)
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(bottomleft=(50, SCREEN_HEIGHT - 20))
        self.vel_y = 0

    def update(self, platforms, coins, enemies):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= MOVE_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += MOVE_SPEED
        if keys[pygame.K_SPACE] and pygame.sprite.spritecollideany(self, platforms):
            self.vel_y = JUMP_STRENGTH

        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        if self.rect.bottom > SCREEN_HEIGHT:
            self.kill()

        if pygame.sprite.spritecollide(self, platforms, False):
            self.vel_y = 0
            self.rect.bottom = min([p.rect.top for p in pygame.sprite.spritecollide(self, platforms, False)])

        for coin in pygame.sprite.spritecollide(self, coins, True):
            global score
            score += 10

        for enemy in pygame.sprite.spritecollide(self, enemies, False):
            global lives
            lives -= 1
            if self.rect.centerx < enemy.rect.centerx:
                self.rect.right = enemy.rect.left
            else:
                self.rect.left = enemy.rect.right

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface(COIN_SIZE)
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, range_x):
        super().__init__()
        self.image = pygame.Surface(ENEMY_SIZE)
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.range_x = range_x
        self.direction = 1

    def update(self):
        self.rect.x += self.direction
        if self.rect.right >= self.rect.x + self.range_x or self.rect.left <= self.rect.x - self.range_x:
            self.direction *= -1

class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 40))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(topleft=(x, y))

def draw_hud():
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(lives_text, (10, 10))
    screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))

def reset_game():
    global player, platforms, coins, enemies, flag, score, lives
    player = Player()
    platforms = pygame.sprite.Group([
        Platform(0, SCREEN_HEIGHT - 20, 800, 20),
        Platform(200, 400, 100, 20),
        Platform(500, 300, 100, 20),
        Platform(100, 200, 100, 20),
        Platform(600, 100, 100, 20)
    ])
    coins = pygame.sprite.Group([
        Coin(250, 390),
        Coin(550, 290),
        Coin(150, 190),
        Coin(650, 90),
        Coin(300, 450)
    ])
    enemies = pygame.sprite.Group([
        Enemy(250, 400, 50),
        Enemy(550, 310, 50),
        Enemy(150, 210, 50)
    ])
    flag = Flag(750, 50)
    score = 0
    lives = PLAYER_LIVES

reset_game()

running = True
game_over = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r and game_over:
                reset_game()
                game_over = False

    if not game_over:
        player.update(platforms, coins, enemies)
        enemies.update()

        if lives <= 0 or player.rect.bottom > SCREEN_HEIGHT:
            game_over = True
            game_over_text = font.render("Game Over! Press R to Restart", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2))

        if pygame.sprite.collide_rect(player, flag):
            game_over = True
            game_over_text = font.render("You Win! Press R to Restart", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2))

        screen.fill(BLACK)
        platforms.draw(screen)
        coins.draw(screen)
        enemies.draw(screen)
        flag.draw(screen)
        screen.blit(player.image, player.rect)
        draw_hud()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()