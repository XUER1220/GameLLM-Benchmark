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
PLAYER_BULLET_WIDTH = 6
PLAYER_BULLET_HEIGHT = 16
PLAYER_BULLET_SPEED = 8
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 30
ENEMY_ROWS = 4
ENEMY_COLS = 8
ENEMY_SPEED = 1.2
ENEMY_BULLET_WIDTH = 6
ENEMY_BULLET_HEIGHT = 16
ENEMY_BULLET_SPEED = 4
ENEMY_SHOOT_CHANCE = 0.005
PLAYER_LIVES = 3
BACKGROUND_COLOR = (0, 0, 0)
PLAYER_COLOR = (0, 255, 0)
ENEMY_COLOR = (255, 0, 0)
PLAYER_BULLET_COLOR = (0, 255, 255)
ENEMY_BULLET_COLOR = (255, 255, 0)
FONT_COLOR = (255, 255, 255)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders Medium")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, SCREEN_HEIGHT - PLAYER_HEIGHT - 40, PLAYER_WIDTH, PLAYER_HEIGHT)
    
    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += PLAYER_SPEED

class Bullet:
    def __init__(self, x, y, is_player_bullet=True):
        self.rect = pygame.Rect(x, y, PLAYER_BULLET_WIDTH, PLAYER_BULLET_HEIGHT if is_player_bullet else ENEMY_BULLET_HEIGHT)
        self.is_player_bullet = is_player_bullet
    
    def update(self):
        if self.is_player_bullet:
            self.rect.y -= PLAYER_BULLET_SPEED
        else:
            self.rect.y += ENEMY_BULLET_SPEED

def draw_hud(score, lives):
    score_text = font.render(f"Score: {score}", True, FONT_COLOR)
    lives_text = font.render(f"Lives: {lives}", True, FONT_COLOR)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 10, 10))

def game_over_screen(score, win):
    screen.fill(BACKGROUND_COLOR)
    result_text = font.render(f"{'Win' if win else 'Lose'}! Score: {score}", True, FONT_COLOR)
    restart_text = font.render("Press R to Restart", True, FONT_COLOR)
    screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, SCREEN_HEIGHT // 2 - result_text.get_height() // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
    pygame.display.flip()

def main():
    player = Player()
    bullets = []
    enemies = [[pygame.Rect(x * (ENEMY_WIDTH + 10) + 50, y * (ENEMY_HEIGHT + 10) + 50, ENEMY_WIDTH, ENEMY_HEIGHT) for x in range(ENEMY_COLS)] for y in range(ENEMY_ROWS)]
    enemy_bullets = []
    direction = 1
    score = 0
    lives = PLAYER_LIVES
    game_over = False
    win = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if not game_over:
            if keys[pygame.K_SPACE]:
                bullets.append(Bullet(player.rect.centerx - PLAYER_BULLET_WIDTH // 2, player.rect.top))

            player.update(keys)

            for bullet in bullets[:]:
                bullet.update()
                if bullet.rect.bottom < 0:
                    bullets.remove(bullet)
                for row in enemies:
                    for enemy in row[:]:
                        if bullet.rect.colliderect(enemy):
                            bullets.remove(bullet)
                            row.remove(enemy)
                            score += 10
                            break

            for row in enemies:
                for enemy in row:
                    if random.random() < ENEMY_SHOOT_CHANCE:
                        enemy_bullets.append(Bullet(enemy.centerx - ENEMY_BULLET_WIDTH // 2, enemy.bottom, False))
            
            for bullet in enemy_bullets[:]:
                bullet.update()
                if bullet.rect.top > SCREEN_HEIGHT:
                    enemy_bullets.remove(bullet)
                if bullet.rect.colliderect(player.rect):
                    enemy_bullets.remove(bullet)
                    lives -= 1
                    if lives == 0:
                        game_over = True

            for row in enemies:
                for enemy in row:
                    if enemy.bottom >= player.rect.top:
                        game_over = True

            if len(enemies) == 0:
                win = True
                game_over = True

            for row in enemies:
                for enemy in row:
                    enemy.x += ENEMY_SPEED * direction
                if any(enemy.right >= SCREEN_WIDTH for enemy in row) or any(enemy.left <= 0 for enemy in row):
                    direction *= -1
                    for enemy in row:
                        enemy.y += 20

        if game_over:
            game_over_screen(score, win)
            if keys[pygame.K_r]:
                main()
                return
            if keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()

        screen.fill(BACKGROUND_COLOR)
        pygame.draw.rect(screen, PLAYER_COLOR, player.rect)
        for bullet in bullets:
            pygame.draw.rect(screen, PLAYER_BULLET_COLOR, bullet.rect)
        for row in enemies:
            for enemy in row:
                pygame.draw.rect(screen, ENEMY_COLOR, enemy)
        for bullet in enemy_bullets:
            pygame.draw.rect(screen, ENEMY_BULLET_COLOR, bullet.rect)
        draw_hud(score, lives)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()