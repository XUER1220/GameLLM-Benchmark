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
PIPE_SPEED = 3
PIPE_WIDTH = 80
PIPE_GAP = 170
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
INITIAL_BIRD_X = 160
INITIAL_BIRD_Y = 300
SPAWN_PIPE_DISTANCE = 200
SCORE_INCREMENT_DISTANCE = PIPE_WIDTH + PIPE_GAP // 2

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird Easy')
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

class Bird:
    def __init__(self):
        self.rect = pygame.Rect(INITIAL_BIRD_X, INITIAL_BIRD_Y, BIRD_WIDTH, BIRD_HEIGHT)
        self.vel = 0

    def flap(self):
        self.vel = FLAP_STRENGTH

    def update(self):
        self.vel += GRAVITY
        self.rect.y += int(self.vel)

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 255, 0), self.rect)

class Pipe:
    def __init__(self, x):
        self.gap_center = random.randint(PIPE_GAP // 2, SCREEN_HEIGHT - PIPE_GAP // 2)
        self.top_rect = pygame.Rect(x, -self.gap_center + PIPE_GAP // 2, PIPE_WIDTH, self.gap_center)
        self.bottom_rect = pygame.Rect(x, self.gap_center + PIPE_GAP // 2, PIPE_WIDTH, SCREEN_HEIGHT - self.gap_center - PIPE_GAP // 2)

    def update(self):
        self.top_rect.x -= PIPE_SPEED
        self.bottom_rect.x -= PIPE_SPEED

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 255, 0), self.top_rect)
        pygame.draw.rect(surface, (0, 255, 0), self.bottom_rect)

def game():
    bird = Bird()
    pipes = []
    score = 0
    frame_count = 0
    game_over = False

    while True:
        screen.fill((0, 0, 139))
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
                if event.key == pygame.K_r:
                    return

        if not game_over:
            bird.update()
            if frame_count % 90 == 0:
                pipes.append(Pipe(SCREEN_WIDTH))
            for pipe in pipes:
                pipe.update()
                if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                    game_over = True
                if pipe.top_rect.right < bird.rect.left and not pipe.passed:
                    pipe.passed = True
                    score += 1
                if pipe.top_rect.right < 0:
                    pipes.remove(pipe)
            if bird.rect.top > SCREEN_HEIGHT or bird.rect.bottom < 0:
                game_over = True

        bird.draw(screen)
        for pipe in pipes:
            pipe.draw(screen)

        draw_text(f'Score: {score}', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, 50)
        if game_over:
            draw_text('Game Over', font, (255, 0, 0), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            draw_text(f'Score: {score}', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            draw_text('Press R to Restart', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)

        pygame.display.flip()
        frame_count += 1
        clock.tick(FPS)

while True:
    game()