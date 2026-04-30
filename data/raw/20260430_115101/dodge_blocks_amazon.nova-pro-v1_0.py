import pygame
import sys
import random
import time

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SIZE = 60
PLAYER_Y = SCREEN_HEIGHT - PLAYER_SIZE - 40
PLAYER_SPEED = 7
BLOCK_SIZE = 40
BLOCK_SPEED_MIN = 4
BLOCK_SPEED_MAX = 8
SPAWN_INTERVAL = 40

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge Blocks Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 55)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(GREEN)
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

class Block(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - BLOCK_SIZE)
        self.rect.y = 0
        self.speed_y = random.randint(BLOCK_SPEED_MIN, BLOCK_SPEED_MAX)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

def game():
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    all_sprites = pygame.sprite.Group()
    blocks = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)

    score = 0
    start_time = pygame.time.get_ticks()

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            elif event.type == pygame.USEREVENT:
                score = (pygame.time.get_ticks() - start_time) // 1000
            elif event.type == pygame.USEREVENT + 1:
                block = Block()
                all_sprites.add(block)
                blocks.add(block)

        all_sprites.update()

        hits = pygame.sprite.spritecollide(player, blocks, False)
        if hits:
            running = False

        screen.fill(BLACK)
        all_sprites.draw(screen)
        draw_text(f"Score: {score}", font, WHITE, screen, 10, 10)

        pygame.display.flip()

    draw_text("Game Over", font, WHITE, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50)
    draw_text(f"Final Score: {score}", font, WHITE, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
    draw_text("Press R to Restart", font, WHITE, screen, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                game()

game()