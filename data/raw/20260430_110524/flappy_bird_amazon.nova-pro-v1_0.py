import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
BIRD_START_POS = (160, 300)
GRAVITY = 0.35
FLAP_STRENGTH = -7.5
PIPE_WIDTH = 80
PIPE_GAP = 170
PIPE_SPAWN_RATE = 90
PIPE_SPEED = 3
GROUND_HEIGHT = 50

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
        self.rect = pygame.Rect(BIRD_START_POS[0], BIRD_START_POS[1], BIRD_WIDTH, BIRD_HEIGHT)
        self.vel = 0

    def update(self):
        self.vel += GRAVITY
        self.rect.y += self.vel

    def flap(self):
        self.vel = FLAP_STRENGTH

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 255, 0), self.rect)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_center = random.randint(PIPE_GAP//2, SCREEN_HEIGHT - PIPE_GAP//2 - GROUND_HEIGHT)
        self.top_rect = pygame.Rect(x, -self.gap_center - PIPE_GAP//2, PIPE_WIDTH, self.gap_center)
        self.bottom_rect = pygame.Rect(x, self.gap_center + PIPE_GAP//2, PIPE_WIDTH, SCREEN_HEIGHT - self.gap_center - PIPE_GAP//2 - GROUND_HEIGHT)

    def update(self):
        self.top_rect.x -= PIPE_SPEED
        self.bottom_rect.x -= PIPE_SPEED

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 255, 0), self.top_rect)
        pygame.draw.rect(surface, (0, 255, 0), self.bottom_rect)

def reset_game():
    bird.rect.topleft = BIRD_START_POS
    bird.vel = 0
    pipes.clear()
    return 0

def main():
    global bird, pipes, score, frame_count
    bird = Bird()
    pipes = []
    score = 0
    frame_count = 0
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key in (pygame.K_SPACE, pygame.K_UP) and not game_over:
                    bird.flap()
                if event.key == pygame.K_r and game_over:
                    game_over = False
                    score = reset_game()

        screen.fill((135, 206, 235))

        if not game_over:
            bird.update()
            if frame_count % PIPE_SPAWN_RATE == 0:
                pipes.append(Pipe(SCREEN_WIDTH))
            for pipe in pipes:
                pipe.update()
                if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                    game_over = True
                if pipe.top_rect.right < 0:
                    pipes.remove(pipe)
                if pipe.top_rect.right < bird.rect.left and not pipe.passed:
                    pipe.passed = True
                    score += 1
            if bird.rect.top > SCREEN_HEIGHT - GROUND_HEIGHT or bird.rect.bottom < 0:
                game_over = True

            bird.draw(screen)
            for pipe in pipes:
                pipe.draw(screen)

            draw_text(str(score), font, (255, 255, 255), screen, SCREEN_WIDTH//2, 50)
        else:
            draw_text("Game Over", font, (255, 0, 0), screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50)
            draw_text(f"Score: {score}", font, (255, 0, 0), screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
            draw_text("Press R to Restart", font, (255, 0, 0), screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)

        pygame.draw.rect(screen, (0, 128, 0), (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        frame_count += 1
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()