import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BIRD_SIZE = (40, 30)
BIRD_INIT_POS = (160, 300)
GRAVITY = 0.35
FLAP_STRENGTH = -7.5
PIPE_WIDTH = 80
PIPE_GAP = 170
PIPE_SPAWN_INTERVAL = 90
PIPE_SPEED = 3
GROUND_HEIGHT = 20

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird Easy")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

class Bird:
    def __init__(self):
        self.rect = pygame.Rect(BIRD_INIT_POS, BIRD_SIZE)
        self.velocity = 0

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.rect.y += int(self.velocity)

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 255, 0), self.rect)

class Pipe:
    def __init__(self, x):
        gap_center = random.randint(100, SCREEN_HEIGHT - 100)
        self.top_rect = pygame.Rect(x, 0, PIPE_WIDTH, gap_center - PIPE_GAP // 2)
        self.bottom_rect = pygame.Rect(x, gap_center + PIPE_GAP // 2, PIPE_WIDTH, SCREEN_HEIGHT - (gap_center + PIPE_GAP // 2))
        self.passed = False

    def update(self):
        self.top_rect.x -= PIPE_SPEED
        self.bottom_rect.x -= PIPE_SPEED

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 255, 0), self.top_rect)
        pygame.draw.rect(surface, (0, 255, 0), self.bottom_rect)

def draw_ground(surface):
    pygame.draw.rect(surface, (139, 69, 19), (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))

def draw_hud(surface, score):
    text = font.render(f"Score: {score}", True, (255, 255, 255))
    surface.blit(text, (10, 10))

def game_over_screen(surface, score):
    game_over_text = font.render("Game Over", True, (255, 0, 0))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    restart_text = font.render("Press R to Restart", True, (255, 255, 255))
    surface.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
    surface.blit(score_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2))
    surface.blit(restart_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50))

def main():
    bird = Bird()
    pipes = []
    score = 0
    frame_count = 0
    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    bird.flap()
                elif event.key == pygame.K_r and game_over:
                    bird = Bird()
                    pipes.clear()
                    score = 0
                    frame_count = 0
                    game_over = False

        if not game_over:
            bird.update()
            frame_count += 1

            if frame_count % PIPE_SPAWN_INTERVAL == 0:
                pipes.append(Pipe(SCREEN_WIDTH))

            for pipe in pipes:
                pipe.update()
                if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                    game_over = True
                if not pipe.passed and bird.rect.right > pipe.top_rect.right:
                    pipe.passed = True
                    score += 1

            if bird.rect.top < 0 or bird.rect.bottom > SCREEN_HEIGHT:
                game_over = True

            pipes = [pipe for pipe in pipes if pipe.top_rect.right > 0]

        screen.fill((0, 0, 139))
        draw_ground(screen)
        bird.draw(screen)
        for pipe in pipes:
            pipe.draw(screen)
        draw_hud(screen, score)

        if game_over:
            game_over_screen(screen, score)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()