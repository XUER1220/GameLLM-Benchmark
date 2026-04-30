import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
PLAYER_SIZE = (60, 32)
PLAYER_BULLET_SIZE = (6, 16)
ENEMY_SIZE = (40, 30)
ENEMY_ROWS, ENEMY_COLS = 4, 8
ENEMY_SPEED = 1.2
ENEMY_BULLET_SPEED = 4
PLAYER_SPEED = 6
PLAYER_BULLET_SPEED = 8
PLAYER_LIVES = 3

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders Medium")
clock = pygame.time.Clock()

def draw_text(text, size, color, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface(PLAYER_SIZE)
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        self.speed = PLAYER_SPEED

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, is_player):
        super().__init__()
        self.image = pygame.Surface(PLAYER_BULLET_SIZE if is_player else ENEMY_BULLET_SIZE)
        self.image.fill(RED if is_player else BLUE)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = PLAYER_BULLET_SPEED if is_player else ENEMY_BULLET_SPEED
        self.is_player = is_player

    def update(self):
        if self.is_player:
            self.rect.y -= self.speed
        else:
            self.rect.y += self.speed

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface(ENEMY_SIZE)
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))

def main():
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)

    for row in range(ENEMY_ROWS):
        for col in range(ENEMY_COLS):
            enemy = Enemy(col * (ENEMY_SIZE[0] + 10) + 50, row * (ENEMY_SIZE[1] + 10) + 50)
            enemies.add(enemy)
            all_sprites.add(enemy)

    score = 0
    lives = PLAYER_LIVES
    direction = 1
    game_over = False
    victory = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE:
                    bullet = Bullet(player.rect.centerx, player.rect.top, True)
                    all_sprites.add(bullet)
                    bullets.add(bullet)

        keys = pygame.key.get_pressed()
        player.update(keys)

        if not game_over:
            all_sprites.update()

            if random.randint(0, 1000) < 10:
                enemy = random.choice(pygame.sprite.spritecollide(player, enemies, False))
                if enemy:
                    bullet = Bullet(enemy.rect.centerx, enemy.rect.bottom, False)
                    all_sprites.add(bullet)
                    bullets.add(bullet)

            hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
            for hit in hits:
                score += 10

            if enemies.sprites() and enemies.sprites()[-1].rect.bottom >= player.rect.top:
                game_over = True
                lives = 0

            if not enemies:
                victory = True
                game_over = True

            for bullet in bullets:
                if bullet.rect.bottom < 0 or bullet.rect.top > SCREEN_HEIGHT:
                    bullet.kill()

            hits = pygame.sprite.spritecollide(player, bullets, True)
            for hit in hits:
                if not hit.is_player:
                    lives -= 1
                    if lives == 0:
                        game_over = True

            for enemy in enemies:
                enemy.rect.x += direction * ENEMY_SPEED
                if enemy.rect.right >= SCREEN_WIDTH or enemy.rect.left <= 0:
                    direction *= -1
                    for e in enemies:
                        e.rect.y += 20

        screen.fill(BLACK)
        all_sprites.draw(screen)
        draw_text(f"Score: {score}", 24, WHITE, 10, 10)
        draw_text(f"Lives: {lives}", 24, WHITE, 10, 40)

        if game_over:
            if victory:
                draw_text("Victory!", 50, WHITE, SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 30)
            else:
                draw_text("Game Over", 50, WHITE, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 30)
            draw_text("Press R to Restart", 30, WHITE, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20)
            if keys[pygame.K_r]:
                main()
                return

        pygame.display.flip()
        clock.tick(FPS)

main()