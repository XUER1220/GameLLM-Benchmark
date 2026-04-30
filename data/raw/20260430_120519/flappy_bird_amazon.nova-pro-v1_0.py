import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.35
FLAP_STRENGTH = -7.5
PIPE_VELOCITY = 3
PIPE_WIDTH = 80
PIPE_GAP = 170
SPAWN_PIPE_FRAMES = 90
BIRD_SIZE = (40, 30)
BIRD_POS = (160, 300)
PIPE_SPAWN_HEIGHT_RANGE = (150, 400)

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird Easy")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

def draw_bird(x, y):
    pygame.draw.rect(screen, YELLOW, (x, y, BIRD_SIZE[0], BIRD_SIZE[1]))

def draw_pipe(x, height):
    pygame.draw.rect(screen, GREEN, (x, 0, PIPE_WIDTH, height))
    pygame.draw.rect(screen, GREEN, (x, height + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - height - PIPE_GAP))

def game_over_screen(score):
    screen.fill(BLACK)
    text = font.render(f"Game Over\nScore: {score}\nPress R to Restart", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))

def main():
    running = True
    game_over = False
    score = 0

    bird_x, bird_y = BIRD_POS
    bird_velocity = 0
    pipes = []
    frame_count = 0

    while running:
        screen.fill(BLUE)
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_SPACE, pygame.K_UP) and not game_over:
                    bird_velocity = FLAP_STRENGTH
                elif event.key == pygame.K_r and game_over:
                    game_over = False
                    score = 0
                    bird_x, bird_y = BIRD_POS
                    bird_velocity = 0
                    pipes = []
                    frame_count = 0

        if not game_over:
            bird_velocity += GRAVITY
            bird_y += bird_velocity

            if frame_count % SPAWN_PIPE_FRAMES == 0:
                height = random.randint(*PIPE_SPAWN_HEIGHT_RANGE)
                pipes.append((SCREEN_WIDTH, height))

            for pipe in pipes[:]:
                pipe_x, height = pipe
                pipe_x -= PIPE_VELOCITY
                draw_pipe(pipe_x, height)
                if pipe_x + PIPE_WIDTH < 0:
                    pipes.remove(pipe)
                elif bird_x < pipe_x + PIPE_WIDTH < bird_x + BIRD_SIZE[0] and (bird_y < height or bird_y + BIRD_SIZE[1] > height + PIPE_GAP):
                    game_over = True
                elif bird_x + BIRD_SIZE[0] > pipe_x + PIPE_WIDTH and pipe not in [p for p in pipes if p[0] < 0]:
                    score += 1
                    pipes.remove(pipe)

            if bird_y > SCREEN_HEIGHT or bird_y + BIRD_SIZE[1] < 0:
                game_over = True

            draw_bird(bird_x, bird_y)
            text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(text, (10, 10))
        else:
            game_over_screen(score)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()