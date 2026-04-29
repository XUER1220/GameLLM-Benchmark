import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SIZE = (32, 48)
COIN_SIZE = (18, 18)
ENEMY_SIZE = (32, 32)
GRAVITY = 0.5
JUMP_SPEED = -12
PLAYER_SPEED = 5
INITIAL_LIVES = 3

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GRAY = (105, 105, 105)
CYAN = (0, 255, 255)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface(PLAYER_SIZE)
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = SCREEN_HEIGHT - PLAYER_SIZE[1]
        self.vel_y = 0
        self.on_ground = True

    def update(self, platforms, coins, enemies, goal):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = JUMP_SPEED
            self.on_ground = False

        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = 0
            self.on_ground = True

        self.rect.x = max(0, min(self.rect.x, 3200 - PLAYER_SIZE[0]))

        self.check_collision(platforms)
        self.check_collision(coins, True)
        self.check_collision(enemies)
        self.check_goal(goal)

    def check_collision(self, sprites, is_coin=False):
        collided_sprites = pygame.sprite.spritecollide(self, sprites, is_coin)
        for sprite in collided_sprites:
            if is_coin:
                global score, coins_collected
                score += 100
                coins_collected += 1
            else:
                if self.vel_y > 0:
                    self.rect.bottom = sprite.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = sprite.rect.bottom
                    self.vel_y = 0
                if isinstance(sprite, Enemy):
                    if self.rect.bottom <= sprite.rect.top + 10:
                        sprite.kill()
                        global score
                        score += 200
                    else:
                        global lives
                        lives -= 1
                        self.rect.x = max(0, self.rect.x - 100)

    def check_goal(self, goal):
        if pygame.sprite.collide_rect(self, goal):
            pygame.time.wait(1000)
            global running, game_won
            running = False
            game_won = True

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, is_breakable=False):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GRAY if is_breakable else BROWN)
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
        self.direction = 1

    def update(self):
        self.rect.x += self.direction * PLAYER_SPEED
        if self.rect.right >= 3200 or self.rect.left <= 0:
            self.direction *= -1

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 96))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def create_level():
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    goal = Goal(3000, SCREEN_HEIGHT - 96)

    platforms.add(Platform(0, SCREEN_HEIGHT - PLAYER_SIZE[1], 800, PLAYER_SIZE[1]))
    platforms.add(Platform(800, SCREEN_HEIGHT - PLAYER_SIZE[1] - 100, 400, PLAYER_SIZE[1]))
    platforms.add(Platform(1200, SCREEN_HEIGHT - PLAYER_SIZE[1] - 200, 400, PLAYER_SIZE[1]))
    platforms.add(Platform(1600, SCREEN_HEIGHT - PLAYER_SIZE[1] - 300, 400, PLAYER_SIZE[1]))
    platforms.add(Platform(2000, SCREEN_HEIGHT - PLAYER_SIZE[1] - 100, 400, PLAYER_SIZE[1]))
    platforms.add(Platform(2400, SCREEN_HEIGHT - PLAYER_SIZE[1], 800, PLAYER_SIZE[1]))

    for i in range(12):
        coins.add(Coin(random.randint(100, 3000), random.randint(100, SCREEN_HEIGHT - COIN_SIZE[1])))

    for i in range(3):
        enemies.add(Enemy(random.randint(100, 3000), SCREEN_HEIGHT - ENEMY_SIZE[1]))

    return platforms, coins, enemies, goal

def draw_hud(screen, lives, score, coins_collected):
    font = pygame.font.Font(None, 36)
    lives_text = font.render(f'Lives: {lives}', True, WHITE)
    score_text = font.render(f'Score: {score}', True, WHITE)
    coins_text = font.render(f'Coins: {coins_collected}', True, WHITE)
    screen.blit(lives_text, (10, 10))
    screen.blit(score_text, (10, 50))
    screen.blit(coins_text, (10, 90))

def game_over_screen(screen, score):
    font = pygame.font.Font(None, 74)
    text = font.render('Game Over', True, WHITE)
    score_text = font.render(f'Score: {score}', True, WHITE)
    restart_text = font.render('Press R to Restart', True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

def game_won_screen(screen, score):
    font = pygame.font.Font(None, 74)
    text = font.render('You Win', True, WHITE)
    score_text = font.render(f'Score: {score}', True, WHITE)
    restart_text = font.render('Press R to Restart', True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

def main():
    global running, game_won, lives, score, coins_collected
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Super Mario Bros 1-1 Medium")
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)

    platforms, coins, enemies, goal = create_level()
    all_sprites.add(platforms)
    all_sprites.add(coins)
    all_sprites.add(enemies)
    all_sprites.add(goal)

    lives = INITIAL_LIVES
    score = 0
    coins_collected = 0
    game_won = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                main()

        screen.fill(BLACK)
        all_sprites.update()
        all_sprites.draw(screen)
        draw_hud(screen, lives, score, coins_collected)

        if lives <= 0:
            game_over_screen(screen, score)
            pygame.display.flip()
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        main()

        if game_won:
            game_won_screen(screen, score)
            pygame.display.flip()
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        main()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()