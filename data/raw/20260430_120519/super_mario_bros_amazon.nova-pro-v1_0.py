import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WORLD_WIDTH, WORLD_HEIGHT = 3200, 600
FPS = 60
PLAYER_SIZE = (32, 48)
COIN_SIZE = (18, 18)
ENEMY_SIZE = (32, 32)
GRAVITY = 0.5
JUMP_SPEED = -12
MOVE_SPEED = 5
PLAYER_LIVES = 3

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GREY = (128, 128, 128)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario Bros Medium")
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface(PLAYER_SIZE)
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = SCREEN_HEIGHT - PLAYER_SIZE[1]
        self.vel_y = 0

    def update(self, platforms, coins, enemies, flag_pole):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= MOVE_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += MOVE_SPEED
        if keys[pygame.K_SPACE] and self.rect.bottom >= SCREEN_HEIGHT:
            self.vel_y = JUMP_SPEED

        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        self.rect.x = max(0, min(self.rect.x, WORLD_WIDTH - PLAYER_SIZE[0]))

        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = 0

        if pygame.sprite.spritecollide(self, platforms, False):
            self.vel_y = 0
            self.rect.bottom = min([p.rect.top for p in pygame.sprite.spritecollide(self, platforms, False)])

        if pygame.sprite.spritecollide(self, coins, True):
            global score, coin_count
            score += 100
            coin_count += 1

        enemy_hit_list = pygame.sprite.spritecollide(self, enemies, False)
        for enemy in enemy_hit_list:
            if self.rect.bottom <= enemy.rect.top:
                enemy.kill()
                score += 200
            else:
                global lives
                lives -= 1
                self.rect.x = max(0, min(self.rect.x, WORLD_WIDTH - PLAYER_SIZE[0]))

        if pygame.sprite.collide_rect(self, flag_pole):
            return "win"
        return "continue"

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface(COIN_SIZE)
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface(ENEMY_SIZE)
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1

    def update(self, platforms):
        self.rect.x += self.move_direction * MOVE_SPEED
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for hit in hits:
            if self.move_direction > 0:
                self.rect.right = hit.rect.left
            else:
                self.rect.left = hit.rect.right
            self.move_direction *= -1

def create_level():
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    flag_pole = Platform(WORLD_WIDTH - 50, SCREEN_HEIGHT - 200, 50, 200, BLUE)

    platforms.add(Platform(0, SCREEN_HEIGHT - 50, WORLD_WIDTH, 50, BROWN))
    for x in range(0, 1000, 64):
        platforms.add(Platform(x, SCREEN_HEIGHT - 150, 64, 50, GREY))
    for x in range(1000, 1500, 64):
        platforms.add(Platform(x, SCREEN_HEIGHT - 300, 64, 50, GREY))
    platforms.add(Platform(2000, SCREEN_HEIGHT - 350, 64, 50, GREY))
    platforms.add(Platform(2200, SCREEN_HEIGHT - 350, 64, 50, GREY))
    for x in range(2500, 3000, 64):
        platforms.add(Platform(x, SCREEN_HEIGHT - 150, 64, 50, GREY))

    for _ in range(12):
        coins.add(Coin(random.randint(0, WORLD_WIDTH - COIN_SIZE[0]), random.randint(100, SCREEN_HEIGHT - 200)))

    for x in [500, 1200, 2000]:
        enemies.add(Enemy(x, SCREEN_HEIGHT - ENEMY_SIZE[1] - 50))

    return platforms, coins, enemies, flag_pole

def draw_hud(lives, score, coin_count):
    font = pygame.font.Font(None, 36)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    coin_text = font.render(f"Coins: {coin_count}", True, WHITE)
    screen.blit(lives_text, (10, 10))
    screen.blit(score_text, (10, 50))
    screen.blit(coin_text, (10, 90))

def game_over_screen(score):
    font = pygame.font.Font(None, 74)
    text = font.render("Game Over", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    restart_text = font.render("Press R to Restart", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

def win_screen(score):
    font = pygame.font.Font(None, 74)
    text = font.render("You Win", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    restart_text = font.render("Press R to Restart", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

def main():
    global score, coin_count, lives
    score = 0
    coin_count = 0
    lives = PLAYER_LIVES

    platforms, coins, enemies, flag_pole = create_level()
    all_sprites = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player, *platforms, *coins, *enemies, flag_pole)

    camera_offset_x = 0
    game_state = "playing"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r and game_state!= "playing":
                    main()

        if game_state == "playing":
            player.update(platforms, coins, enemies, flag_pole)
            for enemy in enemies:
                enemy.update(platforms)

            if lives <= 0:
                game_state = "game_over"
            elif player.rect.right >= WORLD_WIDTH:
                game_state = "win"

            camera_offset_x = max(0, min(player.rect.centerx - SCREEN_WIDTH // 2, WORLD_WIDTH - SCREEN_WIDTH))

        screen.fill((0, 0, 0))

        for platform in platforms:
            screen.blit(platform.image, (platform.rect.x - camera_offset_x, platform.rect.y))
        for coin in coins:
            screen.blit(coin.image, (coin.rect.x - camera_offset_x, coin.rect.y))
        for enemy in enemies:
            screen.blit(enemy.image, (enemy.rect.x - camera_offset_x, enemy.rect.y))
        screen.blit(player.image, (player.rect.x - camera_offset_x, player.rect.y))
        screen.blit(flag_pole.image, (flag_pole.rect.x - camera_offset_x, flag_pole.rect.y))

        draw_hud(lives, score, coin_count)

        if game_state == "game_over":
            game_over_screen(score)
        elif game_state == "win":
            win_screen(score)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()