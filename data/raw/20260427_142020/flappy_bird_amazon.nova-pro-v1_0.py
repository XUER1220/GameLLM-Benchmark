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
SPAWN_PIPE_EVENT = pygame.USEREVENT
pygame.time.set_timer(SPAWN_PIPE_EVENT, 900)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird Easy")
clock = pygame.time.Clock()

BIRD_SIZE = (40, 30)
BIRD_COLOR = (255, 255, 0)
BIRD_START_POS = (160, 300)

PIPE_COLOR = (0, 255, 0)
GROUND_COLOR = (139, 69, 19)
BACKGROUND_COLOR = (0, 191, 255)
TEXT_COLOR = (255, 255, 255)

font = pygame.font.Font(None, 36)

class Bird:
    def __init__(self):
        self.rect = pygame.Rect(BIRD_START_POS[0], BIRD_START_POS[1], *BIRD_SIZE)
        self.velocity = 0

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.rect.y += int(self.velocity)

    def draw(self, screen):
        pygame.draw.rect(screen, BIRD_COLOR, self.rect)

class Pipe:
    def __init__(self, x):
        gap_start = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - 100)
        self.top_rect = pygame.Rect(x, -PIPE_GAP - gap_start, PIPE_WIDTH, gap_start)
        self.bottom_rect = pygame.Rect(x, gap_start + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - gap_start - PIPE_GAP)
        self.passed = False

    def update(self):
        self.top_rect.x -= PIPE_VELOCITY
        self.bottom_rect.x -= PIPE_VELOCITY

    def draw(self, screen):
        pygame.draw.rect(screen, PIPE_COLOR, self.top_rect)
        pygame.draw.rect(screen, PIPE_COLOR, self.bottom_rect)

def draw_ground(screen):
    pygame.draw.rect(screen, GROUND_COLOR, (0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))

def draw_text(screen, text, pos, size=36):
    font = pygame.font.Font(None, size)
    render = font.render(text, True, TEXT_COLOR)
    screen.blit(render, pos)

def game_over(score):
    draw_text(screen, f"Game Over\nScore: {score}\nPress R to Restart", (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50), 36)
    pygame.display.flip()

def main():
    bird = Bird()
    pipes = []
    score = 0
    running = True
    game_over_flag = False

    while running:
        screen.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    bird.flap()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r and game_over_flag:
                    return main()
            if event.type == SPAWN_PIPE_EVENT:
                pipes.append(Pipe(SCREEN_WIDTH))

        if not game_over_flag:
            bird.update()
            for pipe in pipes:
                pipe.update()
                if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                    game_over_flag = True
                if not pipe.passed and bird.rect.right > pipe.top_rect.right:
                    pipe.passed = True
                    score += 1
            if bird.rect.top > SCREEN_HEIGHT - 20 or bird.rect.bottom < 0:
                game_over_flag = True

            bird.draw(screen)
            for pipe in pipes:
                pipe.draw(screen)

            draw_ground(screen)
            draw_text(screen, f"Score: {score}", (10, 10))
        else:
            game_over(score)

        pipes = [pipe for pipe in pipes if pipe.top_rect.right > 0]

        clock.tick(FPS)
        pygame.display.flip()

if __name__ == "__main__":
    main()