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
ENEMY_SPACING = 50
ENEMY_BULLET_SIZE = (6, 16)
PLAYER_SPEED = 6
BULLET_SPEED = 8
ENEMY_SPEED = 1.2
ENEMY_BULLET_SPEED = 4
ENEMY_DOWN_DIST = 20
ENEMY_BULLET_CHANCE = 0.005
PLAYER_LIVES = 3

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders Medium")
clock = pygame.time.Clock()

player_img = pygame.Surface(PLAYER_SIZE)
player_img.fill((0, 255, 0))
player_rect = player_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40 - PLAYER_SIZE[1] // 2))

enemy_img = pygame.Surface(ENEMY_SIZE)
enemy_img.fill((255, 0, 0))

bullet_img = pygame.Surface(PLAYER_BULLET_SIZE)
bullet_img.fill((255, 255, 0))

enemy_bullet_img = pygame.Surface(ENEMY_BULLET_SIZE)
enemy_bullet_img.fill((255, 165, 0))

def draw_hud(score, lives):
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    lives_text = font.render(f"Lives: {lives}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 50))

def game_over(score, win):
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 74)
    text = font.render("Game Over" if not win else "You Win", True, (255, 0, 0))
    screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)))
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
    text = font.render("Press R to Restart", True, (255, 255, 255))
    screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3)))
    pygame.display.flip()

def main():
    global player_rect
    player_rect = player_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40 - PLAYER_SIZE[1] // 2))
    player_bullets = []
    enemies = [[enemy_img.get_rect(topleft=((i * (ENEMY_SIZE[0] + ENEMY_SPACING)) + ENEMY_SPACING, (j * (ENEMY_SIZE[1] + ENEMY_SPACING)) + ENEMY_SPACING)) for i in range(ENEMY_COLS)] for j in range(ENEMY_ROWS)]
    enemy_bullets = []
    direction = 1
    score = 0
    lives = PLAYER_LIVES
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_rect.x -= PLAYER_SPEED
            if player_rect.left < 0:
                player_rect.left = 0
        if keys[pygame.K_RIGHT]:
            player_rect.x += PLAYER_SPEED
            if player_rect.right > SCREEN_WIDTH:
                player_rect.right = SCREEN_WIDTH
        if keys[pygame.K_SPACE]:
            player_bullets.append(bullet_img.get_rect(midbottom=player_rect.midtop))

        for bullet in player_bullets:
            bullet.y -= BULLET_SPEED
            if bullet.bottom < 0:
                player_bullets.remove(bullet)
            for row in enemies:
                for enemy in row:
                    if enemy and bullet.colliderect(enemy):
                        row[row.index(enemy)] = None
                        player_bullets.remove(bullet)
                        score += 10
                        break

        for row in enemies:
            for enemy in row:
                if enemy:
                    enemy.x += ENEMY_SPEED * direction
                    if enemy.right >= SCREEN_WIDTH or enemy.left <= 0:
                        direction *= -1
                        for e in [e for row in enemies for e in row if e]:
                            e.y += ENEMY_DOWN_DIST
                        break

        if random.random() < ENEMY_BULLET_CHANCE:
            for row in enemies:
                for enemy in row:
                    if enemy and random.random() < 0.1:
                        enemy_bullets.append(enemy_bullet_img.get_rect(midtop=enemy.midbottom))

        for bullet in enemy_bullets:
            bullet.y += ENEMY_BULLET_SPEED
            if bullet.top > SCREEN_HEIGHT:
                enemy_bullets.remove(bullet)
            if player_rect.colliderect(bullet):
                enemy_bullets.remove(bullet)
                lives -= 1
                if lives == 0:
                    game_over(score, False)
                    return

        if not any(enemy for row in enemies for enemy in row):
            game_over(score, True)
            return

        screen.fill((0, 0, 0))
        screen.blit(player_img, player_rect)
        for bullet in player_bullets:
            screen.blit(bullet_img, bullet)
        for row in enemies:
            for enemy in row:
                if enemy:
                    screen.blit(enemy_img, enemy)
        for bullet in enemy_bullets:
            screen.blit(enemy_bullet_img, bullet)
        draw_hud(score, lives)
        pygame.display.flip()
        clock.tick(FPS)

while True:
    main()