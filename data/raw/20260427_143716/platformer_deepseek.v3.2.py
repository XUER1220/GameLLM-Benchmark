import pygame
import random

pygame.init()

random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 56
PLAYER_COLOR = (0, 128, 255)
PLAYER_INITIAL_X = 100
PLAYER_INITIAL_Y = 500
PLAYER_SPEED = 5
PLAYER_JUMP_SPEED = -12
GRAVITY = 0.5

GROUND_COLOR = (100, 70, 30)
GROUND_RECT = pygame.Rect(0, 580, 800, 20)

PLATFORMS = [
    pygame.Rect(50, 500, 200, 20),     
    pygame.Rect(300, 400, 150, 20),   
    pygame.Rect(500, 350, 150, 20),   
    pygame.Rect(200, 300, 150, 20),   
    pygame.Rect(450, 250, 150, 20),   
    pygame.Rect(600, 200, 150, 20)    
]

PLATFORM_COLOR = (150, 120, 50)

ENEMY_WIDTH = 36
ENEMY_HEIGHT = 36
ENEMY_COLOR = (255, 50, 50)
ENEMIES = [
    {"rect": pygame.Rect(350, 364, ENEMY_WIDTH, ENEMY_HEIGHT), "start_x": 300, "end_x": 450, "speed": 2, "dir": 1},
    {"rect": pygame.Rect(520, 314, ENEMY_WIDTH, ENEMY_HEIGHT), "start_x": 500, "end_x": 650, "speed": 2.5, "dir": 1},
    {"rect": pygame.Rect(220, 264, ENEMY_WIDTH, ENEMY_HEIGHT), "start_x": 200, "end_x": 350, "speed": 1.8, "dir": 1}
]

COIN_SIZE = 20
COIN_COLOR = (255, 215, 0)
COINS = [
    pygame.Rect(120, 460, COIN_SIZE, COIN_SIZE),
    pygame.Rect(360, 360, COIN_SIZE, COIN_SIZE),
    pygame.Rect(560, 310, COIN_SIZE, COIN_SIZE),
    pygame.Rect(260, 260, COIN_SIZE, COIN_SIZE),
    pygame.Rect(500, 210, COIN_SIZE, COIN_SIZE)
]

FLAG_WIDTH = 30
FLAG_HEIGHT = 50
FLAG_COLOR = (50, 255, 50)
FLAG_RECT = pygame.Rect(700, 150, FLAG_WIDTH, FLAG_HEIGHT)

BG_COLOR = (30, 30,100)
TEXT_COLOR = (255, 255, 255)
HUD_COLOR = (200, 200, 200)
HUD_HEIGHT = 40

INITIAL_LIVES = 3
COIN_SCORE = 10

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer Hard")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(PLAYER_INITIAL_X, PLAYER_INITIAL_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.lives = INITIAL_LIVES
        self.score = 0
        self.won = False
        self.lost = False

    def handle_keys(self, keys):
        self.vx = 0
        if keys[pygame.K_LEFT]:
            self.vx = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.vx = PLAYER_SPEED
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = PLAYER_JUMP_SPEED
            self.on_ground = False

    def update(self, platforms, enemies, coins, flag):
        self.rect.x += self.vx
        self.handle_collision_x(platforms)
        self.vy += GRAVITY
        self.rect.y += self.vy
        self.on_ground = False
        self.handle_collision_y(platforms)

        if self.rect.bottom >= SCREEN_HEIGHT:
            self.lives = 0
            self.lost = True

        for enemy in enemies:
            if self.rect.colliderect(enemy["rect"]):
                self.lives -= 1
                if self.vx > 0:
                    self.rect.x -= 50
                elif self.vx < 0:
                    self.rect.x += 50
                else:
                    self.rect.x -= 30
                if self.lives <= 0:
                    self.lost = True
                    break

        for coin in coins[:]:
            if self.rect.colliderect(coin):
                coins.remove(coin)
                self.score += COIN_SCORE

        if self.rect.colliderect(flag) and not self.lost:
            self.won = True

    def handle_collision_x(self, platforms):
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vx > 0:
                    self.rect.right = plat.left
                elif self.vx < 0:
                    self.rect.left = plat.right

    def handle_collision_y(self, platforms):
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vy > 0:
                    self.rect.bottom = plat.top
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = plat.bottom
                    self.vy = 0

    def reset(self):
        self.rect = pygame.Rect(PLAYER_INITIAL_X, PLAYER_INITIAL_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.lives = INITIAL_LIVES
        self.score = 0
        self.won = False
        self.lost = False

def update_enemies(enemies):
    for e in enemies:
        e["rect"].x += e["speed"] * e["dir"]
        if e["rect"].x <= e["start_x"] or e["rect"].x + ENEMY_WIDTH >= e["end_x"]:
            e["dir"] *= -1

def draw_hud(player):
    pygame.draw.rect(screen, HUD_COLOR, (0, 0, SCREEN_WIDTH, HUD_HEIGHT))
    lives_text = font.render(f"Lives: {player.lives}", True, (0, 0, 0))
    score_text = font.render(f"Score: {player.score}", True, (0, 0, 0))
    screen.blit(lives_text, (20, 5))
    screen.blit(score_text, (200, 5))

def draw_message(text, y_offset=0):
    msg = font.render(text, True, TEXT_COLOR)
    msg_rect = msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + y_offset))
    screen.blit(msg, msg_rect)

def main():
    player = Player()
    platforms = [GROUND_RECT] + PLATFORMS
    enemies = ENEMIES.copy()
    coins = COINS.copy()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r and (player.won or player.lost):
                    player.reset()
                    enemies = ENEMIES.copy()
                    coins = COINS.copy()

        if not (player.won or player.lost):
            keys = pygame.key.get_pressed()
            player.handle_keys(keys)
            player.update(platforms, enemies, coins, FLAG_RECT)
            update_enemies(enemies)

        screen.fill(BG_COLOR)

        pygame.draw.rect(screen, GROUND_COLOR, GROUND_RECT)
        for plat in PLATFORMS:
            pygame.draw.rect(screen, PLATFORM_COLOR, plat)

        for coin in coins:
            pygame.draw.rect(screen, COIN_COLOR, coin)

        pygame.draw.rect(screen, FLAG_COLOR, FLAG_RECT)

        pygame.draw.rect(screen, PLAYER_COLOR, player.rect)

        for enemy in enemies:
            pygame.draw.rect(screen, ENEMY_COLOR, enemy["rect"])

        draw_hud(player)

        if player.won:
            draw_message("You Win! Press R to Restart", 40)
        elif player.lost:
            draw_message("Game Over! Press R to Restart", 40)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()