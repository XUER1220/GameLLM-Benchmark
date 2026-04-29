import pygame
import sys
import random

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

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge Blocks Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill((0, 128, 255))
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 40

    def update(self, direction):
        if direction == "left":
            self.rect.x -= PLAYER_SPEED
        elif direction == "right":
            self.rect.x += PLAYER_SPEED
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

class Block(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - BLOCK_SIZE)
        self.rect.y = 0
        self.speed = random.randint(BLOCK_SPEED_MIN, BLOCK_SPEED_MAX)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

def game():
    all_sprites = pygame.sprite.Group()
    blocks = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    spawn_timer = 0
    score = 0
    start_ticks = pygame.time.get_ticks()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.update("left")
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.update("right")

        spawn_timer += 1
        if spawn_timer >= SPAWN_INTERVAL:
            block = Block()
            all_sprites.add(block)
            blocks.add(block)
            spawn_timer = 0

        all_sprites.update()

        hits = pygame.sprite.spritecollide(player, blocks, False)
        if hits:
            running = False

        screen.fill((0, 0, 0))
        all_sprites.draw(screen)

        score = (pygame.time.get_ticks() - start_ticks) // 1000
        draw_text(f"Score: {score}", font, (255, 255, 255), screen, 10, 10)

        pygame.display.flip()
        clock.tick(FPS)

    draw_text("Game Over", font, (255, 0, 0), screen, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 30)
    draw_text(f"Score: {score}", font, (255, 255, 255), screen, SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 20)
    draw_text("Press R to Restart", font, (255, 255, 255), screen, SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 50)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

game()