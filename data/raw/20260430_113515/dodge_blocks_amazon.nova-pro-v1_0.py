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
PLAYER_COLOR = (0, 128, 255)
BLOCK_SIZE = 40
BLOCK_COLOR = (255, 0, 0)
BACKGROUND_COLOR = (0, 0, 0)
HUD_COLOR = (255, 255, 255)
FONT = pygame.font.SysFont(None, 36)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge Blocks Easy")
clock = pygame.time.Clock()

def draw_hud(score):
    score_text = FONT.render(f"Score: {score}", True, HUD_COLOR)
    screen.blit(score_text, (10, 10))

def draw_game_over(score):
    game_over_text = FONT.render("Game Over", True, HUD_COLOR)
    score_text = FONT.render(f"Score: {score}", True, HUD_COLOR)
    restart_text = FONT.render("Press R to Restart", True, HUD_COLOR)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50))

def main():
    player_rect = pygame.Rect(SCREEN_WIDTH // 2 - PLAYER_SIZE // 2, SCREEN_HEIGHT - PLAYER_SIZE - 40, PLAYER_SIZE, PLAYER_SIZE)
    blocks = []
    score = 0
    start_time = time.time()
    game_over = False

    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        score = int(elapsed_time)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r and game_over:
                    main()

        keys = pygame.key.get_pressed()
        if not game_over:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_rect.x -= 7
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_rect.x += 7

            player_rect.x = max(0, min(player_rect.x, SCREEN_WIDTH - PLAYER_SIZE))

            if len(blocks) < 1 and random.randint(1, 40) == 1:
                block_x = random.randint(0, SCREEN_WIDTH - BLOCK_SIZE)
                block_rect = pygame.Rect(block_x, 0, BLOCK_SIZE, BLOCK_SIZE)
                blocks.append((block_rect, random.randint(4, 8)))

            for block, speed in blocks[:]:
                block.y += speed
                if block.y > SCREEN_HEIGHT:
                    blocks.remove((block, speed))
                if block.colliderect(player_rect):
                    game_over = True

        screen.fill(BACKGROUND_COLOR)
        if not game_over:
            pygame.draw.rect(screen, PLAYER_COLOR, player_rect)
            for block, _ in blocks:
                pygame.draw.rect(screen, BLOCK_COLOR, block)
            draw_hud(score)
        else:
            draw_game_over(score)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()