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
ENEMY_BULLET_SIZE = (6, 16)
PLAYER_LIVES = 3
ENEMY_SPEED = 1.2
ENEMY_BULLET_SPEED = 4
PLAYER_BULLET_SPEED = 8
ENEMY_DOWN_MOVE = 20
ENEMY_SHOOT_CHANCE = 0.005

BLACK, WHITE, RED, GREEN = (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders Medium")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface(PLAYER_SIZE)
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= 6
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += 6

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, is_player_bullet=True):
        super().__init__()
        self.image = pygame.Surface(PLAYER_BULLET_SIZE if is_player_bullet else ENEMY_BULLET_SIZE)
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.is_player_bullet = is_player_bullet
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        if self.is_player_bullet:
            self.rect.y -= PLAYER_BULLET_SPEED
            if self.rect.bottom < 0:
                self.kill()
        else:
            self.rect.y += ENEMY_BULLET_SPEED
            if self.rect.top > SCREEN_HEIGHT:
                self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface(ENEMY_SIZE)
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

def main():
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    
    for row in range(ENEMY_ROWS):
        for col in range(ENEMY_COLS):
            enemy = Enemy(col * (ENEMY_SIZE[0] + 20) + 50, row * (ENEMY_SIZE[1] + 20) + 50)
            all_sprites.add(enemy)
            enemies.add(enemy)
    
    direction = 1
    score = 0
    lives = PLAYER_LIVES
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
                main()
        
        keys = pygame.key.get_pressed()
        if not game_over:
            player.update(keys)
            if keys[pygame.K_SPACE]:
                bullet = Bullet(player.rect.centerx, player.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)

            for enemy in enemies:
                if random.random() < ENEMY_SHOOT_CHANCE:
                    bullet = Bullet(enemy.rect.centerx, enemy.rect.bottom, False)
                    all_sprites.add(bullet)
                    bullets.add(bullet)

            all_sprites.update()

            hits = pygame.sprite.groupcollide(enemies, bullets, True, True, pygame.sprite.collide_mask)
            for hit in hits:
                score += 10

            enemy_hits = pygame.sprite.spritecollide(player, bullets, True, pygame.sprite.collide_mask)
            for hit in enemy_hits:
                if not hit.is_player_bullet:
                    lives -= 1

            if not enemies:
                game_over = True
                text = font.render("You Win! Press R to Restart", True, WHITE)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(text, text_rect)

            if lives == 0:
                game_over = True
                text = font.render("Game Over! Press R to Restart", True, WHITE)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(text, text_rect)

            if pygame.sprite.spritecollideany(player, enemies, pygame.sprite.collide_mask):
                game_over = True
                text = font.render("Game Over! Press R to Restart", True, WHITE)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(text, text_rect)

            for enemy in enemies:
                enemy.rect.x += ENEMY_SPEED * direction
                if enemy.rect.right >= SCREEN_WIDTH or enemy.rect.left <= 0:
                    direction *= -1
                    for e in enemies:
                        e.rect.y += ENEMY_DOWN_MOVE
                    break

            screen.fill(BLACK)
            all_sprites.draw(screen)
            score_text = font.render(f"Score: {score}", True, WHITE)
            lives_text = font.render(f"Lives: {lives}", True, WHITE)
            screen.blit(score_text, (10, 10))
            screen.blit(lives_text, (10, 40))
        else:
            if keys[pygame.K_r]:
                main()

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()