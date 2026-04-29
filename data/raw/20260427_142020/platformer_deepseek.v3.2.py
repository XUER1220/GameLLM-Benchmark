import pygame
import random
import sys

random.seed(42)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 56
PLAYER_SPEED = 5
PLAYER_JUMP_SPEED = -12
GRAVITY = 0.5

GROUND_PLATFORM_Y = 550
GROUND_PLATFORM_HEIGHT = 50

PLATFORM_COLOR = (0, 128, 0)
ENEMY_COLOR = (220, 20, 60)
COIN_COLOR = (255, 215, 0)
FLAG_COLOR = (173, 216, 230)
PLAYER_COLOR = (70, 130, 180)
BACKGROUND_COLOR = (30, 30, 50)
HUD_COLOR = (255, 255, 255)
GAME_OVER_COLOR = (255, 0, 0)
GAME_WIN_COLOR = (0, 255, 0)

ENEMY_WIDTH = 36
ENEMY_HEIGHT = 36
ENEMY_SPEED = 2

COIN_SIZE = 20

PLATFORMS = [
    {"rect": pygame.Rect(0, GROUND_PLATFORM_Y, WINDOW_WIDTH, GROUND_PLATFORM_HEIGHT)},
    {"rect": pygame.Rect(100, 400, 200, 20)},
    {"rect": pygame.Rect(350, 320, 150, 20)},
    {"rect": pygame.Rect(150, 250, 180, 20)},
    {"rect": pygame.Rect(500, 220, 150, 20)},
    {"rect": pygame.Rect(300, 150, 120, 20)}
]

COINS = [
    {"rect": pygame.Rect(120, 360, COIN_SIZE, COIN_SIZE)},
    {"rect": pygame.Rect(200, 360, COIN_SIZE, COIN_SIZE)},
    {"rect": pygame.Rect(380, 280, COIN_SIZE, COIN_SIZE)},
    {"rect": pygame.Rect(550, 180, COIN_SIZE, COIN_SIZE)},
    {"rect": pygame.Rect(350, 110, COIN_SIZE, COIN_SIZE)}
]

ENEMIES = [
    {"rect": pygame.Rect(200, 350, ENEMY_WIDTH, ENEMY_HEIGHT), "move_range": [150, 250], "direction": 1},
    {"rect": pygame.Rect(500, 180, ENEMY_WIDTH, ENEMY_HEIGHT), "move_range": [480, 580], "direction": 1},
    {"rect": pygame.Rect(320, 50, ENEMY_WIDTH, ENEMY_HEIGHT), "move_range": [300, 380], "direction": 1}
]

FLAG_RECT = pygame.Rect(700, 80, 30, 60)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, GROUND_PLATFORM_Y - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_y = 0
        self.vel_x = 0
        self.jumping = False
        self.lives = 3
        self.score = 0
        self.on_ground = False

    def update(self, platforms):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        self.on_ground = False
        for pf in platforms:
            if self.rect.colliderect(pf):
                if self.vel_y > 0:
                    self.rect.bottom = pf.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = pf.bottom
                    self.vel_y = 0

        self.rect.x += self.vel_x
        for pf in platforms:
            if self.rect.colliderect(pf):
                if self.vel_x > 0:
                    self.rect.right = pf.left
                elif self.vel_x < 0:
                    self.rect.left = pf.right

        if self.rect.y > WINDOW_HEIGHT:
            self.lives = 0

    def jump(self):
        if self.on_ground:
            self.vel_y = PLAYER_JUMP_SPEED
            self.jumping = True
            self.on_ground = False

class Enemy:
    def __init__(self, rect, move_range):
        self.rect = rect.copy()
        self.move_range = move_range
        self.direction = 1

    def update(self):
        self.rect.x += ENEMY_SPEED * self.direction
        if self.rect.x <= self.move_range[0]:
            self.direction = 1
        elif self.rect.x + ENEMY_WIDTH >= self.move_range[1]:
            self.direction = -1

def draw_text(surface, text, size, x, y, color):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Platformer Hard")
    clock = pygame.time.Clock()

    player = Player()
    enemies = [Enemy(e["rect"], e["move_range"]) for e in ENEMIES]
    coins = COINS.copy()
    platforms = [p["rect"] for p in PLATFORMS]

    game_over = False
    game_win = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    player = Player()
                    enemies = [Enemy(e["rect"], e["move_range"]) for e in ENEMIES]
                    coins = COINS.copy()
                    game_over = False
                    game_win = False
                if not game_over and not game_win and event.key == pygame.K_SPACE:
                    player.jump()

        if not game_over and not game_win:
            keys = pygame.key.get_pressed()
            player.vel_x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * PLAYER_SPEED
            player.update(platforms)

            for enemy in enemies:
                enemy.update()

            for coin in coins[:]:
                if player.rect.colliderect(coin["rect"]):
                    coins.remove(coin)
                    player.score += 10

            for enemy in enemies:
                if player.rect.colliderect(enemy.rect):
                    player.lives -= 1
                    player.rect.x -= 30 * enemy.direction
                    if player.rect.x < 0:
                        player.rect.x = 0
                    if player.lives <= 0:
                        game_over = True

            if player.lives <= 0:
                game_over = True

            if player.rect.colliderect(FLAG_RECT):
                game_win = True

        screen.fill(BACKGROUND_COLOR)

        for pf in platforms:
            pygame.draw.rect(screen, PLATFORM_COLOR, pf)

        pygame.draw.rect(screen, FLAG_COLOR, FLAG_RECT)
        pygame.draw.polygon(screen, (255, 255, 255),
                            [(FLAG_RECT.right, FLAG_RECT.top),
                             (FLAG_RECT.right + 10, FLAG_RECT.top + 20),
                             (FLAG_RECT.right, FLAG_RECT.top + 40)])

        for coin in coins:
            pygame.draw.rect(screen, COIN_COLOR, coin["rect"])
            pygame.draw.circle(screen, (200, 180, 0),
                               (coin["rect"].centerx, coin["rect"].centery),
                               COIN_SIZE // 2)

        for enemy in enemies:
            pygame.draw.rect(screen, ENEMY_COLOR, enemy.rect)
            pygame.draw.circle(screen, (139, 0, 0),
                               (enemy.rect.centerx, enemy.rect.centery),
                               ENEMY_WIDTH // 3)

        pygame.draw.rect(screen, PLAYER_COLOR, player.rect)
        pygame.draw.circle(screen, (50, 100, 150),
                           (player.rect.centerx, player.rect.centery - 10),
                           PLAYER_WIDTH // 3)

        draw_text(screen, f"Lives: {player.lives}", 36, 100, 10, HUD_COLOR)
        draw_text(screen, f"Score: {player.score}", 36, 700, 10, HUD_COLOR)

        if game_over:
            draw_text(screen, "GAME OVER", 72, WINDOW_WIDTH // 2, 200, GAME_OVER_COLOR)
            draw_text(screen, "Press R to Restart", 48, WINDOW_WIDTH // 2, 300, HUD_COLOR)
        elif game_win:
            draw_text(screen, "VICTORY!", 72, WINDOW_WIDTH // 2, 200, GAME_WIN_COLOR)
            draw_text(screen, "Press R to Restart", 48, WINDOW_WIDTH // 2, 300, HUD_COLOR)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()