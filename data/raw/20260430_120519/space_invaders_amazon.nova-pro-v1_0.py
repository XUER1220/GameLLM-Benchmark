import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
PLAYER_SIZE = (60, 32)
BULLET_SIZE = (6, 16)
ENEMY_SIZE = (40, 30)
ENEMY_ROWS, ENEMY_COLS = 4, 8
PLAYER_BULLET_SPEED = 8
ENEMY_BULLET_SPEED = 4
ENEMY_MOVE_SPEED = 1.2
ENEMY_DOWN_SPEED = 20
ENEMY_SHOOT_CHANCE = 0.005
PLAYER_LIVES = 3
PLAYER_SPEED = 6

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2 - PLAYER_SIZE[0] // 2, SCREEN_HEIGHT - PLAYER_SIZE[1] - 40, *PLAYER_SIZE)
        self.color = (0, 128, 255)
    
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)

class Bullet:
    def __init__(self, x, y, is_enemy=False):
        self.rect = pygame.Rect(x, y, *BULLET_SIZE)
        self.color = (255, 0, 0) if is_enemy else (255, 255, 0)
        self.speed = -PLAYER_BULLET_SPEED if not is_enemy else ENEMY_BULLET_SPEED
    
    def move(self):
        self.rect.y += self.speed
    
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, *ENEMY_SIZE)
        self.color = (255, 0, 0)
    
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)

def create_enemies():
    enemies = []
    for row in range(ENEMY_ROWS):
        for col in range(ENEMY_COLS):
            enemy = Enemy(col * (ENEMY_SIZE[0] + 20) + 50, row * (ENEMY_SIZE[1] + 20) + 50)
            enemies.append(enemy)
    return enemies

def main():
    player = Player()
    bullets = []
    enemies = create_enemies()
    enemy_direction = 1
    score = 0
    lives = PLAYER_LIVES
    game_over = False

    def reset_game():
        nonlocal bullets, enemies, enemy_direction, score, lives, game_over
        bullets = []
        enemies = create_enemies()
        enemy_direction = 1
        score = 0
        lives = PLAYER_LIVES
        game_over = False

    while True:
        screen.fill((0, 0, 0))
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

        keys = pygame.key.get_pressed()
        if not game_over:
            if keys[pygame.K_LEFT] and player.rect.left > 0:
                player.rect.x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] and player.rect.right < SCREEN_WIDTH:
                player.rect.x += PLAYER_SPEED
            if keys[pygame.K_SPACE]:
                bullets.append(Bullet(player.rect.centerx - BULLET_SIZE[0] // 2, player.rect.top))

        if not game_over:
            for bullet in bullets:
                bullet.move()
                if bullet.rect.bottom < 0:
                    bullets.remove(bullet)
                else:
                    for enemy in enemies:
                        if bullet.rect.colliderect(enemy.rect):
                            bullets.remove(bullet)
                            enemies.remove(enemy)
                            score += 10
                            break

            for enemy in enemies:
                if random.random() < ENEMY_SHOOT_CHANCE:
                    bullets.append(Bullet(enemy.rect.centerx - BULLET_SIZE[0] // 2, enemy.rect.bottom, is_enemy=True))

            for bullet in bullets:
                if bullet.rect.top > SCREEN_HEIGHT:
                    bullets.remove(bullet)
                elif bullet.rect.colliderect(player.rect):
                    bullets.remove(bullet)
                    lives -= 1
                    if lives == 0:
                        game_over = True

            if enemies:
                for enemy in enemies:
                    enemy.rect.x += enemy_direction * ENEMY_MOVE_SPEED
                if (enemy_direction == 1 and enemies[-1].rect.right >= SCREEN_WIDTH) or \
                   (enemy_direction == -1 and enemies[0].rect.left <= 0):
                    enemy_direction *= -1
                    for enemy in enemies:
                        enemy.rect.y += ENEMY_DOWN_SPEED
                        if enemy.rect.bottom > player.rect.top:
                            game_over = True
            else:
                game_over = True

        player.draw()
        for bullet in bullets:
            bullet.draw()
        for enemy in enemies:
            enemy.draw()

        score_text = font.render(f'Score: {score}', True, (255, 255, 255))
        lives_text = font.render(f'Lives: {lives}', True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 40))

        if game_over:
            if not enemies:
                result_text = font.render('You Win!', True, (0, 255, 0))
            else:
                result_text = font.render('Game Over', True, (255, 0, 0))
            screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, SCREEN_HEIGHT // 2 - result_text.get_height() // 2))
            restart_text = font.render('Press R to Restart', True, (255, 255, 255))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 30))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()