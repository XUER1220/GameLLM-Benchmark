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
SPAWN_PIPE_EVENT = pygame.USEREVENT
SCORE_INCREMENT_EVENT = pygame.USEREVENT + 1
PIPE_SPAWN_INTERVAL = 90

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 55)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

class Bird:
    def __init__(self):
        self.x = 160
        self.y = 300
        self.velocity = 0
        self.rect = pygame.Rect(self.x, self.y, 40, 30)

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.topleft = (self.x, self.y)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, 400)
        self.top_rect = pygame.Rect(self.x, self.height - PIPE_GAP, PIPE_WIDTH, self.height)
        self.bottom_rect = pygame.Rect(self.x, self.height, PIPE_WIDTH, SCREEN_HEIGHT - self.height)

    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

def reset_game():
    bird.y = 300
    bird.velocity = 0
    bird.rect.topleft = (bird.x, bird.y)
    pipes.clear()
    pygame.time.set_timer(SPAWN_PIPE_EVENT, PIPE_SPAWN_INTERVAL)
    global score
    score = 0

bird = Bird()
pipes = []
score = 0
pygame.time.set_timer(SPAWN_PIPE_EVENT, PIPE_SPAWN_INTERVAL)

running = True
game_over = True

while running:
    screen.fill((135, 206, 235))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key in (pygame.K_SPACE, pygame.K_UP) and not game_over:
                bird.flap()
            elif event.key == pygame.K_r and game_over:
                reset_game()
                game_over = False
        elif event.type == SPAWN_PIPE_EVENT:
            pipes.append(Pipe(SCREEN_WIDTH))

    if not game_over:
        bird.update()

        new_pipes = []
        for pipe in pipes:
            pipe.update()
            if pipe.top_rect.right > 0:
                new_pipes.append(pipe)
            if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                game_over = True
        pipes = new_pipes

        if pipes and bird.rect.left > pipes[0].x + PIPE_WIDTH:
            score += 1
            pygame.time.set_timer(SCORE_INCREMENT_EVENT, 1000)

        if bird.rect.top < 0 or bird.rect.bottom > SCREEN_HEIGHT:
            game_over = True

    pygame.draw.rect(screen, (70, 130, 180), bird.rect)
    for pipe in pipes:
        pygame.draw.rect(screen, (34, 139, 34), pipe.top_rect)
        pygame.draw.rect(screen, (34, 139, 34), pipe.bottom_rect)

    draw_text(f"Score: {score}", font, (255, 255, 255), screen, 70, 30)
    
    if game_over:
        draw_text("Game Over", font, (255, 0, 0), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        draw_text(f"Final Score: {score}", font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text("Press R to Restart", font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()