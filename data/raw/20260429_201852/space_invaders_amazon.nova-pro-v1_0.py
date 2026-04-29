import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PLAYER_WIDTH, PLAYER_HEIGHT = 60, 32
ENEMY_WIDTH, ENEMY_HEIGHT = 40, 30
BULLET_WIDTH, BULLET_HEIGHT = 6, 16
ENEMY_ROWS, ENEMY_COLS = 4, 8
ENEMY_SPACING_X, ENEMY_SPACING_Y = 50, 50
ENEMY_SPEED = 1.2
PLAYER_SPEED = 6
BULLET_SPEED = 8
ENEMY_BULLET_SPEED = 4
PLAYER_LIVES = 3
ENEMY_BULLET_CHANCE = 0.005

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders Medium")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - PLAYER_HEIGHT - 40))

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - PLAYER_WIDTH))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y -= BULLET_SPEED

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y += ENEMY_BULLET_SPEED

def reset_game():
    global player, bullets, enemies, enemy_bullets, score, player_lives
    player = Player()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    score = 0
    player_lives = PLAYER_LIVES
    for row in range(ENEMY_ROWS):
        for col in range(ENEMY_COLS):
            enemy = Enemy(col * (ENEMY_WIDTH + ENEMY_SPACING_X) + 50, row * (ENEMY_HEIGHT + ENEMY_SPACING_Y) + 50)
            enemies.add(enemy)

def main():
    global player, bullets, enemies, enemy_bullets, score, player_lives
    reset_game()
    direction = 1
    game_over = False

    while True:
        screen.fill(BLACK)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r and game_over:
                    reset_game()
                    game_over = False

        if not game_over:
            if keys[pygame.K_SPACE]:
                bullet = Bullet(player.rect.centerx, player.rect.top)
                bullets.add(bullet)

            player.update(keys)
            bullets.update()
            enemies.update()

            for enemy in enemies:
                enemy.rect.x += direction * ENEMY_SPEED
                if enemy.rect.right >= SCREEN_WIDTH or enemy.rect.left <= 0:
                    direction *= -1
                    for e in enemies:
                        e.rect.y += 20
                    break

            if random.random() < ENEMY_BULLET_CHANCE and enemies:
                enemy = random.choice(enemies.sprites())
                enemy_bullet = EnemyBullet(enemy.rect.centerx, enemy.rect.bottom)
                enemy_bullets.add(enemy_bullet)

            enemy_bullets.update()

            for bullet in bullets:
                if bullet.rect.bottom < 0:
                    bullet.kill()

            for enemy_bullet in enemy_bullets:
                if enemy_bullet.rect.top > SCREEN_HEIGHT:
                    enemy_bullet.kill()

            hit_enemies = pygame.sprite.groupcollide(bullets, enemies, True, True)
            for hit in hit_enemies:
                score += 10

            hit_player = pygame.sprite.spritecollide(player, enemy_bullets, True)
            for h in hit_player:
                player_lives -= 1

            if player_lives <= 0 or any(enemy.rect.bottom >= player.rect.top for enemy in enemies):
                game_over = True

            if len(enemies) == 0:
                game_over = True

        screen.blit(player.image, player.rect)
        bullets.draw(screen)
        enemies.draw(screen)
        enemy_bullets.draw(screen)

        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {player_lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))

        if game_over:
            if len(enemies) == 0:
                result_text = font.render("You Win!", True, GREEN)
            else:
                result_text = font.render("Game Over", True, RED)
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 30))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()