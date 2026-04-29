import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
PLAYER_WIDTH, PLAYER_HEIGHT = 60, 32
PLAYER_SPEED = 6
PLAYER_BULLET_SPEED = 8
ENEMY_WIDTH, ENEMY_HEIGHT = 40, 30
ENEMY_ROWS, ENEMY_COLS = 4, 8
ENEMY_MOVE_SPEED = 1.2
ENEMY_BULLET_SPEED = 3
ENEMY_DOWN_MOVE = 20
ENEMY_SHOOT_CHANCE = 0.005
PLAYER_LIVES = 3

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders Medium")
clock = pygame.time.Clock()

player_image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
player_image.fill((0, 255, 0))
player_rect = player_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - PLAYER_HEIGHT - 40))

enemy_image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
enemy_image.fill((255, 0, 0))

bullet_image = pygame.Surface((6, 16))
bullet_image.fill((255, 255, 0))

enemies = [[enemy_image.get_rect(topleft=(x * (ENEMY_WIDTH + 10) + 50, y * (ENEMY_HEIGHT + 10) + 50))
            for x in range(ENEMY_COLS)] for y in range(ENEMY_ROWS)]

player_bullets = []
enemy_bullets = []

def draw_text(text, size, color, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def reset_game():
    global player_rect, enemies, player_bullets, enemy_bullets, score, lives
    player_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - PLAYER_HEIGHT - 40)
    enemies = [[enemy_image.get_rect(topleft=(x * (ENEMY_WIDTH + 10) + 50, y * (ENEMY_HEIGHT + 10) + 50))
               for x in range(ENEMY_COLS)] for y in range(ENEMY_ROWS)]
    player_bullets = []
    enemy_bullets = []
    score = 0
    lives = PLAYER_LIVES

reset_game()

score = 0
lives = PLAYER_LIVES
move_direction = 1
game_over = False

while True:
    screen.fill((0, 0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
                game_over = False
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    keys = pygame.key.get_pressed()
    if not game_over:
        if keys[pygame.K_LEFT] and player_rect.left > 0:
            player_rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and player_rect.right < SCREEN_WIDTH:
            player_rect.x += PLAYER_SPEED
        if keys[pygame.K_SPACE]:
            player_bullets.append(bullet_image.get_rect(midbottom=player_rect.midtop))
    
    if not game_over:
        for row in enemies:
            for enemy in row:
                enemy.x += ENEMY_MOVE_SPEED * move_direction
                if enemy.right >= SCREEN_WIDTH or enemy.left <= 0:
                    move_direction *= -1
                    for e in row:
                        e.y += ENEMY_DOWN_MOVE
                    break
                if random.random() < ENEMY_SHOOT_CHANCE:
                    enemy_bullets.append(bullet_image.get_rect(midtop=enemy.midbottom))

        for bullet in player_bullets:
            bullet.y -= PLAYER_BULLET_SPEED
            if bullet.bottom < 0:
                player_bullets.remove(bullet)
            else:
                for row in enemies:
                    for enemy in row:
                        if enemy.colliderect(bullet):
                            player_bullets.remove(bullet)
                            row.remove(enemy)
                            score += 10
                            break

        for bullet in enemy_bullets:
            bullet.y += ENEMY_BULLET_SPEED
            if bullet.top > SCREEN_HEIGHT:
                enemy_bullets.remove(bullet)
            elif player_rect.colliderect(bullet):
                enemy_bullets.remove(bullet)
                lives -= 1
                if lives == 0:
                    game_over = True

        if not enemies:
            game_over = True
            draw_text("You Win!", 50, (0, 255, 0), SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50)
        elif any(enemy.bottom >= player_rect.top for row in enemies for enemy in row):
            game_over = True
            draw_text("Game Over", 50, (255, 0, 0), SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 50)
        
        if game_over:
            draw_text("Press R to Restart", 30, (255, 255, 255), SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 20)

    screen.blit(player_image, player_rect)
    for row in enemies:
        for enemy in row:
            screen.blit(enemy_image, enemy)
    for bullet in player_bullets:
        screen.blit(bullet_image, bullet)
    for bullet in enemy_bullets:
        screen.blit(bullet_image, bullet)
    
    draw_text(f"Score: {score}", 24, (255, 255, 255), 10, 10)
    draw_text(f"Lives: {lives}", 24, (255, 255, 255), 10, 40)

    pygame.display.flip()
    clock.tick(FPS)