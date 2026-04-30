import pygame
import random

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SIZE = (32, 48)
COIN_SIZE = (18, 18)
ENEMY_SIZE = (32, 32)
WORLD_WIDTH = 3200

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface(PLAYER_SIZE)
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = SCREEN_HEIGHT - self.rect.height
        self.vel_y = 0
        self.lives = 3
        self.score = 0
        self.coins = 0

    def update(self, platforms, coins, enemies, flag_pole):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
        if keys[pygame.K_SPACE] and self.vel_y == 0:
            self.vel_y = -12

        self.vel_y += 0.5
        self.rect.y += int(self.vel_y)

        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = 0

        if pygame.sprite.spritecollide(self, platforms, False):
            self.vel_y = 0
            self.rect.bottom = min([p.rect.top for p in platforms if pygame.sprite.collide_rect(self, p)])

        collected_coins = pygame.sprite.spritecollide(self, coins, True)
        for coin in collected_coins:
            self.coins += 1
            self.score += 100

        enemy_collisions = pygame.sprite.spritecollide(self, enemies, False)
        for enemy in enemy_collisions:
            if self.rect.bottom <= enemy.rect.top:
                enemy.kill()
                self.score += 200
            else:
                self.lives -= 1
                self.rect.x = max([p.rect.right for p in platforms if p.rect.right < self.rect.x])

        if pygame.sprite.collide_rect(self, flag_pole):
            return "win"

        if self.rect.top > SCREEN_HEIGHT:
            self.lives -= 1
            self.rect.x = max([p.rect.right for p in platforms if p.rect.right < self.rect.x])
            self.rect.y = SCREEN_HEIGHT - self.rect.height
            self.vel_y = 0

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
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface(ENEMY_SIZE)
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1

    def update(self, platforms):
        self.rect.x += self.direction * 2
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
            self.direction *= -1

class FlagPole(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def draw_hud(player):
    lives_text = font.render(f"Lives: {player.lives}", True, (255, 255, 255))
    score_text = font.render(f"Score: {player.score}", True, (255, 255, 255))
    coins_text = font.render(f"Coins: {player.coins}", True, (255, 255, 255))
    screen.blit(lives_text, (10, 10))
    screen.blit(score_text, (10, 40))
    screen.blit(coins_text, (10, 70))

def create_world():
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    flag_pole = FlagPole(WORLD_WIDTH - 50, SCREEN_HEIGHT - 200, 20, 200)

    platforms.add(Platform(0, SCREEN_HEIGHT - 50, 3200, 50, (0, 128, 0)))
    for x in range(100, 800, 50):
        platforms.add(Platform(x, SCREEN_HEIGHT - 150, 50, 50, (139, 69, 19)))
    for x in range(900, 1500, 100):
        platforms.add(Platform(x, SCREEN_HEIGHT - 100, 50, 50, (139, 69, 19)))
    for x in range(1600, 2000, 100):
        platforms.add(Platform(x, SCREEN_HEIGHT - 200, 50, 100, (139, 69, 19)))
    platforms.add(Platform(2100, SCREEN_HEIGHT - 300, 50, 100, (139, 69, 19)))
    platforms.add(Platform(2200, SCREEN_HEIGHT - 350, 50, 100, (139, 69, 19)))
    platforms.add(Platform(2300, SCREEN_HEIGHT - 400, 50, 100, (139, 69, 19)))
    platforms.add(Platform(2400, SCREEN_HEIGHT - 450, 50, 100, (139, 69, 19)))
    platforms.add(Platform(2500, SCREEN_HEIGHT - 500, 50, 100, (139, 69, 19)))

    for x in range(100, 800, 100):
        coins.add(Coin(x + 10, SCREEN_HEIGHT - 170))
    for x in range(900, 1500, 200):
        coins.add(Coin(x + 10, SCREEN_HEIGHT - 120))
    for x in range(1600, 2000, 200):
        coins.add(Coin(x + 10, SCREEN_HEIGHT - 220))

    enemies.add(Enemy(300, SCREEN_HEIGHT - 82))
    enemies.add(Enemy(700, SCREEN_HEIGHT - 82))
    enemies.add(Enemy(1200, SCREEN_HEIGHT - 82))

    return platforms, coins, enemies, flag_pole

def main():
    player = Player()
    platforms, coins, enemies, flag_pole = create_world()
    all_sprites = pygame.sprite.Group(player, platforms, coins, enemies, flag_pole)
    running = True
    game_over = False
    win = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and (game_over or win):
                    player = Player()
                    platforms, coins, enemies, flag_pole = create_world()
                    all_sprites = pygame.sprite.Group(player, platforms, coins, enemies, flag_pole)
                    game_over = False
                    win = False

        if not game_over and not win:
            result = player.update(platforms, coins, enemies, flag_pole)
            if result == "win":
                win = True
            elif result == "continue" and player.lives == 0:
                game_over = True

        screen.fill((0, 0, 0))
        all_sprites.update()
        for entity in all_sprites:
            screen.blit(entity.image, entity.rect)

        draw_hud(player)

        if game_over:
            game_over_text = font.render("Game Over", True, (255, 0, 0))
            score_text = font.render(f"Score: {player.score}", True, (255, 255, 255))
            restart_text = font.render("Press R to Restart", True, (255, 255, 255))
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
            screen.blit(score_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50))
        elif win:
            win_text = font.render("You Win", True, (0, 255, 0))
            score_text = font.render(f"Score: {player.score}", True, (255, 255, 255))
            restart_text = font.render("Press R to Restart", True, (255, 255, 255))
            screen.blit(win_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
            screen.blit(score_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()