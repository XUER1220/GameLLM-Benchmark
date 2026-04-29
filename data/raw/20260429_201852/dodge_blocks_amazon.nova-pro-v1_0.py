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
PLAYER_BOTTOM_OFFSET = 40
BLOCK_SIZE = 40
BLOCK_COLOR = (255, 0, 0)
BLOCK_MIN_SPEED = 4
BLOCK_MAX_SPEED = 8
BLOCK_SPAWN_RATE = 40
BACKGROUND_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
FONT = pygame.font.SysFont(None, 36)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge Blocks Easy")
clock = pygame.time.Clock()

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def game():
    player_rect = pygame.Rect(SCREEN_WIDTH // 2 - PLAYER_SIZE // 2, SCREEN_HEIGHT - PLAYER_SIZE - PLAYER_BOTTOM_OFFSET, PLAYER_SIZE, PLAYER_SIZE)
    blocks = []
    score = 0
    last_block_time = 0

    running = True
    game_over = False
    while running:
        current_time = pygame.time.get_ticks()
        screen.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    game()

        keys = pygame.key.get_pressed()
        if not game_over:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_rect.x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_rect.x += PLAYER_SPEED

            player_rect.x = max(0, min(player_rect.x, SCREEN_WIDTH - PLAYER_SIZE))

            if current_time - last_block_time > 1000 / BLOCK_SPAWN_RATE:
                last_block_time = current_time
                block_speed = random.randint(BLOCK_MIN_SPEED, BLOCK_MAX_SPEED)
                block_rect = pygame.Rect(random.randint(0, SCREEN_WIDTH - BLOCK_SIZE), 0 - BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                blocks.append((block_rect, block_speed))

            for block in blocks:
                block[0].y += block[1]
                if block[0].y > SCREEN_HEIGHT:
                    blocks.remove(block)
                elif block[0].colliderect(player_rect):
                    game_over = True

            score = current_time // 1000

        pygame.draw.rect(screen, PLAYER_COLOR, player_rect)
        for block in blocks:
            pygame.draw.rect(screen, BLOCK_COLOR, block[0])

        draw_text(f"Score: {score}", FONT, TEXT_COLOR, screen, 10, 10)
        if game_over:
            draw_text("Game Over", FONT, TEXT_COLOR, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50)
            draw_text(f"Final Score: {score}", FONT, TEXT_COLOR, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
            draw_text("Press R to Restart", FONT, TEXT_COLOR, screen, SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 50)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

game()