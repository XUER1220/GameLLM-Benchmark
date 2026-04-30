import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SIZE = 60
PLAYER_COLOR = (0, 255, 0)
PLAYER_SPEED = 7
PLAYER_INIT_POS = (SCREEN_WIDTH // 2 - PLAYER_SIZE // 2, SCREEN_HEIGHT - PLAYER_SIZE - 40)
BLOCK_SIZE = 40
BLOCK_COLOR = (255, 0, 0)
BLOCK_SPAWN_INTERVAL = 40
BLOCK_SPEED_RANGE = (4, 8)
BG_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
FONT_SIZE = 30

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge Blocks Easy")
clock = pygame.time.Clock()
font = pygame.font.Font(None, FONT_SIZE)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.topleft = PLAYER_INIT_POS
        self.speed = PLAYER_SPEED

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - PLAYER_SIZE))

class Block(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.image.fill(BLOCK_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - BLOCK_SIZE)
        self.rect.y = 0
        self.speed = random.randint(*BLOCK_SPEED_RANGE)

    def update(self):
        self.rect.y += self.speed

def main():
    player = Player()
    blocks = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    spawn_timer = 0
    score = 0
    start_ticks = pygame.time.get_ticks()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False
            sys.exit()
        if keys[pygame.K_r]:
            main()

        player.update(keys)

        spawn_timer += 1
        if spawn_timer >= BLOCK_SPAWN_INTERVAL:
            spawn_timer = 0
            block = Block()
            all_sprites.add(block)
            blocks.add(block)

        blocks.update()
        all_sprites.update()

        for block in blocks:
            if block.rect.y > SCREEN_HEIGHT:
                block.kill()
            if pygame.sprite.collide_rect(player, block):
                running = False

        score = (pygame.time.get_ticks() - start_ticks) // 1000

        screen.fill(BG_COLOR)
        all_sprites.draw(screen)
        draw_text(f"Score: {score}", font, TEXT_COLOR, screen, 10, 10)

        pygame.display.flip()
        clock.tick(FPS)

    draw_text("Game Over", font, TEXT_COLOR, screen, SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 30)
    draw_text(f"Score: {score}", font, TEXT_COLOR, screen, SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2)
    draw_text("Press R to Restart", font, TEXT_COLOR, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 30)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                if event.key == pygame.K_ESCAPE:
                    sys.exit()

if __name__ == "__main__":
    main()