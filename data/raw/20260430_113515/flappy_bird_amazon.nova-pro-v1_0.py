import pygame
import random

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BIRD_WIDTH, BIRD_HEIGHT = 40, 30
BIRD_X, BIRD_Y = 160, 300
GRAVITY = 0.35
FLAP_STRENGTH = -7.5
PIPE_WIDTH = 80
PIPE_GAP = 170
PIPE_SPEED = 3
SPAWN_PIPE_INTERVAL = 90
FONT = pygame.font.SysFont('Arial', 30)

class Bird:
    def __init__(self):
        self.rect = pygame.Rect(BIRD_X, BIRD_Y, BIRD_WIDTH, BIRD_HEIGHT)
        self.vel = 0

    def flap(self):
        self.vel = FLAP_STRENGTH

    def update(self):
        self.vel += GRAVITY
        self.rect.y += int(self.vel)

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 0), self.rect)

class Pipe:
    def __init__(self, x):
        gap_y = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - 100)
        self.top_rect = pygame.Rect(x, 0, PIPE_WIDTH, gap_y)
        self.bottom_rect = pygame.Rect(x, gap_y + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - (gap_y + PIPE_GAP))

    def update(self):
        self.top_rect.x -= PIPE_SPEED
        self.bottom_rect.x -= PIPE_SPEED

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 255, 0), self.top_rect)
        pygame.draw.rect(screen, (0, 255, 0), self.bottom_rect)

def draw_ground(screen):
    pygame.draw.rect(screen, (139, 69, 19), (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))

def game():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flappy Bird Easy")
    clock = pygame.time.Clock()
    bird = Bird()
    pipes = []
    score = 0
    last_pipe_time = 0
    game_over = False

    while True:
        screen.fill((135, 206, 235))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                if event.key in (pygame.K_SPACE, pygame.K_UP) and not game_over:
                    bird.flap()
                if event.key == pygame.K_r and game_over:
                    game()

        if not game_over:
            if pygame.time.get_ticks() - last_pipe_time > SPAWN_PIPE_INTERVAL:
                pipes.append(Pipe(SCREEN_WIDTH))
                last_pipe_time = pygame.time.get_ticks()

            bird.update()
            for pipe in pipes:
                pipe.update()
                if pipe.top_rect.right < 0:
                    pipes.remove(pipe)
                if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                    game_over = True
                if bird.rect.right > pipe.top_rect.left and not hasattr(pipe,'scored'):
                    score += 1
                    pipe.scored = True

            if bird.rect.top > SCREEN_HEIGHT or bird.rect.bottom < 0:
                game_over = True

        for pipe in pipes:
            pipe.draw(screen)

        bird.draw(screen)
        draw_ground(screen)

        score_text = FONT.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        if game_over:
            game_over_text = FONT.render("Game Over", True, (255, 0, 0))
            score_text = FONT.render(f"Score: {score}", True, (255, 0, 0))
            restart_text = FONT.render("Press R to Restart", True, (255, 0, 0))
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
            screen.blit(score_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(FPS)

game()