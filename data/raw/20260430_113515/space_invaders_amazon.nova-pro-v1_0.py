import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
PLAYER_WIDTH, PLAYER_HEIGHT = 60, 32
PLAYER_BULLET_WIDTH, PLAYER_BULLET_HEIGHT = 6, 16
ENEMY_WIDTH, ENEMY_HEIGHT = 40, 30
ENEMY_ROWS, ENEMY_COLS = 4, 8
ENEMY_SPEED = 1.2
ENEMY_DOWN_MOVE = 20
ENEMY_BULLET_WIDTH, ENEMY_BULLET_HEIGHT = 6, 16

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders Medium")
clock = pygame.time.Clock()

def draw_text(surface, text, size, color, x, y):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

class Player:
    def __init__(self):
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 40
        self.speed = 6
        self.lives = 3

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def shoot(self):
        bullet = pygame.Rect(self.rect.centerx - PLAYER_BULLET_WIDTH // 2, self.rect.top, PLAYER_BULLET_WIDTH, PLAYER_BULLET_HEIGHT)
        return bullet

class Enemy:
    def __init__(self, x, y):
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def shoot(self):
        if random.randint(1, 500) == 1:
            bullet = pygame.Rect(self.rect.centerx - ENEMY_BULLET_WIDTH // 2, self.rect.bottom, ENEMY_BULLET_WIDTH, ENEMY_BULLET_HEIGHT)
            return bullet
        return None

def main():
    player = Player()
    enemies = [[Enemy(x * (ENEMY_WIDTH + 10) + 50, y * (ENEMY_HEIGHT + 10) + 50) for y in range(ENEMY_ROWS)] for x in range(ENEMY_COLS)]
    bullets = []
    enemy_bullets = []
    direction = 1
    score = 0

    running = True
    game_over = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                if game_over:
                    main()

        keys = pygame.key.get_pressed()
        if not game_over:
            player.update(keys)
            if keys[pygame.K_SPACE]:
                bullets.append(player.shoot())

            for row in enemies:
                for enemy in row:
                    if random.randint(1, 500) == 1:
                        enemy_bullet = enemy.shoot()
                        if enemy_bullet:
                            enemy_bullets.append(enemy_bullet)

            for bullet in bullets:
                bullet.y -= 8
                if bullet.y <= 0:
                    bullets.remove(bullet)
                else:
                    for row in enemies:
                        for enemy in row:
                            if bullet.colliderect(enemy.rect):
                                bullets.remove(bullet)
                                row.remove(enemy)
                                score += 10
                                break

            for enemy_bullet in enemy_bullets:
                enemy_bullet.y += 8
                if enemy_bullet.y >= SCREEN_HEIGHT:
                    enemy_bullets.remove(enemy_bullet)
                elif enemy_bullet.colliderect(player.rect):
                    enemy_bullets.remove(enemy_bullet)
                    player.lives -= 1
                    if player.lives == 0:
                        game_over = True

            for row in enemies:
                for enemy in row:
                    enemy.rect.x += direction * ENEMY_SPEED
                    if enemy.rect.right >= SCREEN_WIDTH:
                        direction = -1
                        for row in enemies:
                            for enemy in row:
                                enemy.rect.y += ENEMY_DOWN_MOVE
                    elif enemy.rect.left <= 0:
                        direction = 1
                        for row in enemies:
                            for enemy in row:
                                enemy.rect.y += ENEMY_DOWN_MOVE

            if len(enemies) == 0:
                game_over = True
                draw_text(screen, "You Win!", 74, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            elif any(enemy.rect.bottom >= player.rect.top for row in enemies for enemy in row):
                game_over = True
                draw_text(screen, "You Lose!", 74, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        screen.fill(BLACK)
        if not game_over:
            screen.blit(player.image, player.rect)
            for row in enemies:
                for enemy in row:
                    screen.blit(enemy.image, enemy.rect)
            for bullet in bullets:
                pygame.draw.rect(screen, GREEN, bullet)
            for enemy_bullet in enemy_bullets:
                pygame.draw.rect(screen, RED, enemy_bullet)
        draw_text(screen, f"Score: {score}", 24, WHITE, SCREEN_WIDTH // 2, 10)
        draw_text(screen, f"Lives: {player.lives}", 24, WHITE, SCREEN_WIDTH - 50, 10)
        if game_over:
            draw_text(screen, "Press R to Restart", 24, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()