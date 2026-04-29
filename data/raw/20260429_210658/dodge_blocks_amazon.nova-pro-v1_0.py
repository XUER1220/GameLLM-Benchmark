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
BLOCK_SPAWN_INTERVAL = 40
FONT = pygame.font.SysFont(None, 36)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (0, 128, 255)
BLOCK_COLOR = (255, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge Blocks Easy")
clock = pygame.time.Clock()

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
        self.image.fill(BLOCK_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - BLOCK_SIZE)
        self.rect.y = 0
        self.speed = random.randint(4, 8)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

def game():
    all_sprites = pygame.sprite.Group()
    blocks = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    score = 0
    last_block_time = pygame.time.get_ticks()
    running = True
    game_over = False

    while running:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    game()

        if not game_over:
            if current_time - last_block_time > BLOCK_SPAWN_INTERVAL:
                block = Block()
                all_sprites.add(block)
                blocks.add(block)
                last_block_time = current_time
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player.update("left")
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player.update("right")
            all_sprites.update()
            hits = pygame.sprite.spritecollide(player, blocks, False)
            if hits:
                game_over = True
            score = (current_time // 1000)

        screen.fill(BLACK)
        all_sprites.draw(screen)
        draw_text(f"Score: {score}", FONT, WHITE, screen, 10, 10)
        if game_over:
            draw_text("Game Over", FONT, WHITE, screen, SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 - 30)
            draw_text(f"Final Score: {score}", FONT, WHITE, screen, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 10)
            draw_text("Press R to Restart", FONT, WHITE, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

game()