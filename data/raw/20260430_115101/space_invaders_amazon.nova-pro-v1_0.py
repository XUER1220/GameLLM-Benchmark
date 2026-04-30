import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 32
PLAYER_SPEED = 6
PLAYER_LIVES = 3
PLAYER_BULLET_WIDTH = 6
PLAYER_BULLET_HEIGHT = 16
PLAYER_BULLET_SPEED = 8
ENEMY_ROWS = 4
ENEMY_COLS = 8
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 30
ENEMY_SPEED = 1.2
ENEMY_BULLET_WIDTH = 6
ENEMY_BULLET_HEIGHT = 16
ENEMY_BULLET_SPEED = 4
ENEMY_FIRE_RATE = 300

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders Medium")
clock = pygame.time.Clock()

def draw_text(text, size, color, x, y):
    font = pygame.font.SysFont(None, size)
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH / 2
        self.rect.bottom = SCREEN_HEIGHT - 40

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_BULLET_WIDTH, PLAYER_BULLET_HEIGHT))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y

    def update(self):
        self.rect.y -= PLAYER_BULLET_SPEED
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((ENEMY_BULLET_WIDTH, ENEMY_BULLET_HEIGHT))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y

    def update(self):
        self.rect.y += ENEMY_BULLET_SPEED
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

def game():
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    
    player = Player()
    all_sprites.add(player)

    for row in range(ENEMY_ROWS):
        for col in range(ENEMY_COLS):
            enemy = Enemy(col * (ENEMY_WIDTH + 20) + 50, row * (ENEMY_HEIGHT + 20) + 50)
            all_sprites.add(enemy)
            enemies.add(enemy)

    score = 0
    player_lives = PLAYER_LIVES
    enemy_direction = 1
    last_enemy_fire = pygame.time.get_ticks()

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    bullet = PlayerBullet(player.rect.centerx, player.rect.top)
                    all_sprites.add(bullet)
                    player_bullets.add(bullet)

        all_sprites.update()

        hits = pygame.sprite.groupcollide(enemies, player_bullets, True, True)
        for hit in hits:
            score += 10
            if not enemies:
                running = False
                draw_text("You Win!", 64, WHITE, SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 - 32)
                draw_text("Press R to Restart", 32, WHITE, SCREEN_WIDTH / 2 - 140, SCREEN_HEIGHT / 2)
                pygame.display.update()
                wait_for_key()

        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        for hit in hits:
            player_lives -= 1
            if player_lives == 0:
                running = False
                draw_text("Game Over", 64, WHITE, SCREEN_WIDTH / 2 - 140, SCREEN_HEIGHT / 2 - 32)
                draw_text("Press R to Restart", 32, WHITE, SCREEN_WIDTH / 2 - 140, SCREEN_HEIGHT / 2)
                pygame.display.update()
                wait_for_key()

        if pygame.sprite.spritecollideany(player, enemies):
            running = False
            draw_text("Game Over", 64, WHITE, SCREEN_WIDTH / 2 - 140, SCREEN_HEIGHT / 2 - 32)
            draw_text("Press R to Restart", 32, WHITE, SCREEN_WIDTH / 2 - 140, SCREEN_HEIGHT / 2)
            pygame.display.update()
            wait_for_key()

        for enemy in enemies:
            if enemy.rect.bottom >= SCREEN_HEIGHT:
                running = False
                draw_text("Game Over", 64, WHITE, SCREEN_WIDTH / 2 - 140, SCREEN_HEIGHT / 2 - 32)
                draw_text("Press R to Restart", 32, WHITE, SCREEN_WIDTH / 2 - 140, SCREEN_HEIGHT / 2)
                pygame.display.update()
                wait_for_key()

        if pygame.time.get_ticks() - last_enemy_fire > ENEMY_FIRE_RATE:
            last_enemy_fire = pygame.time.get_ticks()
            if enemies:
                shooter = random.choice(enemies.sprites())
                bullet = EnemyBullet(shooter.rect.centerx, shooter.rect.bottom)
                all_sprites.add(bullet)
                enemy_bullets.add(bullet)

        for enemy in enemies:
            enemy.rect.x += ENEMY_SPEED * enemy_direction
            if enemy.rect.right >= SCREEN_WIDTH or enemy.rect.left <= 0:
                enemy_direction *= -1
                for e in enemies:
                    e.rect.y += 20
                break

        screen.fill(BLACK)
        all_sprites.draw(screen)
        draw_text("Score: " + str(score), 24, WHITE, 10, 10)
        draw_text("Lives: " + str(player_lives), 24, WHITE, 10, 40)
        pygame.display.update()

def wait_for_key():
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                waiting = False
                if event.key == pygame.K_r:
                    game()

game()