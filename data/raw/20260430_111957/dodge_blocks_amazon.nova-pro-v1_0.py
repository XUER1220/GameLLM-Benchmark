import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SIZE = 60
PLAYER_SPEED = 7
BLOCK_SIZE = 40
BLOCK_SPEED_MIN = 4
BLOCK_SPEED_MAX = 8
SPAWN_INTERVAL = 40

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

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
        self.rect.bottom = SCREEN_HEIGHT - 40

    def update(self, pressed_keys):
        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
        if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED
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
        self.speedy = random.randint(BLOCK_SPEED_MIN, BLOCK_SPEED_MAX)

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

def game():
    all_sprites = pygame.sprite.Group()
    blocks = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    score = 0
    spawn_timer = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()
        if pressed_keys[pygame.K_r]:
            game()

        all_sprites.update(pressed_keys)

        spawn_timer += 1
        if spawn_timer >= SPAWN_INTERVAL:
            spawn_timer = 0
            block = Block()
            all_sprites.add(block)
            blocks.add(block)

        hits = pygame.sprite.spritecollide(player, blocks, False)
        if hits:
            running = False

        screen.fill(BLACK)
        all_sprites.draw(screen)

        score += 1 / FPS
        draw_text(f"Score: {int(score)}", font, WHITE, screen, 10, 10)

        pygame.display.flip()
        clock.tick(FPS)

    draw_text("Game Over", font, WHITE, screen, (SCREEN_WIDTH - 180) // 2, SCREEN_HEIGHT // 3)
    draw_text(f"Score: {int(score)}", font, WHITE, screen, (SCREEN_WIDTH - 100) // 2, SCREEN_HEIGHT // 2)
    draw_text("Press R to Restart", font, WHITE, screen, (SCREEN_WIDTH - 240) // 2, SCREEN_HEIGHT // 2 + 50)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

game()