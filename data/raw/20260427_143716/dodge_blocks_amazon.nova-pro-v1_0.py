import pygame
import sys
import random

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SIZE = 60
PLAYER_Y = SCREEN_HEIGHT - PLAYER_SIZE - 40
PLAYER_SPEED = 7
OBSTACLE_SIZE = 40
OBSTACLE_SPAWN_RATE = 40
OBSTACLE_SPEED_RANGE = (4, 8)
BACKGROUND_COLOR = (0, 0, 0)
PLAYER_COLOR = (0, 255, 0)
OBSTACLE_COLOR = (255, 0, 0)
HUD_COLOR = (255, 255, 255)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge Blocks Easy")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.y = PLAYER_Y
        self.speed_x = 0

    def update(self):
        self.speed_x = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.speed_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.speed_x = PLAYER_SPEED
        self.rect.x += self.speed_x
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((OBSTACLE_SIZE, OBSTACLE_SIZE))
        self.image.fill(OBSTACLE_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - OBSTACLE_SIZE)
        self.rect.y = 0
        self.speed_y = random.randint(*OBSTACLE_SPEED_RANGE)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

def game():
    player = Player()
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    all_sprites.add(player)

    score = 0
    last_obstacle = pygame.time.get_ticks()
    running = True
    game_over = False

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    return True

        if not game_over:
            current_time = pygame.time.get_ticks()
            if current_time - last_obstacle > OBSTACLE_SPAWN_RATE:
                obstacle = Obstacle()
                all_sprites.add(obstacle)
                obstacles.add(obstacle)
                last_obstacle = current_time
                score = (current_time // 1000)

            all_sprites.update()

            hits = pygame.sprite.spritecollide(player, obstacles, False)
            if hits:
                game_over = True

        screen.fill(BACKGROUND_COLOR)
        all_sprites.draw(screen)
        draw_text(f'Score: {score}', font, HUD_COLOR, screen, 10, 10)

        if game_over:
            draw_text('Game Over', font, HUD_COLOR, screen, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 30)
            draw_text(f'Final Score: {score}', font, HUD_COLOR, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 10)
            draw_text('Press R to Restart', font, HUD_COLOR, screen, SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 50)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

while True:
    if not game():
        break