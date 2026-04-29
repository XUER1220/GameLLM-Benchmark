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
BIRD_SIZE = (40, 30)
BIRD_POS = (160, 300)
SPAWN_PIPE_FRAMES = 90
FONT = pygame.font.Font(None, 48)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird Easy')
clock = pygame.time.Clock()

class Bird:
    def __init__(self):
        self.rect = pygame.Rect(BIRD_POS, BIRD_SIZE)
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
        self.gap_center = random.randint(100, SCREEN_HEIGHT - 100)
        self.top_rect = pygame.Rect(x, -self.gap_center + PIPE_GAP // 2, PIPE_WIDTH, self.gap_center)
        self.bottom_rect = pygame.Rect(x, self.gap_center + PIPE_GAP // 2, PIPE_WIDTH, SCREEN_HEIGHT - self.gap_center - PIPE_GAP // 2)

    def update(self):
        self.top_rect.x -= PIPE_VELOCITY
        self.bottom_rect.x -= PIPE_VELOCITY

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 255, 0), self.top_rect)
        pygame.draw.rect(surface, (0, 255, 0), self.bottom_rect)

def draw_background(surface):
    surface.fill((135, 206, 235))
    pygame.draw.rect(surface, (139, 69, 19), (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))

def draw_hud(surface, score):
    text = FONT.render(f'Score: {score}', True, (255, 255, 255))
    surface.blit(text, (10, 10))

def game_over_screen(surface, score):
    surface.fill((0, 0, 0))
    game_over_text = FONT.render('Game Over', True, (255, 0, 0))
    score_text = FONT.render(f'Score: {score}', True, (255, 255, 255))
    restart_text = FONT.render('Press R to Restart', True, (255, 255, 255))
    surface.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3))
    surface.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 1.5))

def main():
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
                    return

        if not game_over:
            bird.update()
            frame_count += 1

            if frame_count % SPAWN_PIPE_FRAMES == 0:
                pipes.append(Pipe(SCREEN_WIDTH))

            for pipe in pipes:
                pipe.update()
                if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                    game_over = True
                if pipe.top_rect.right < 0:
                    pipes.remove(pipe)
                if not pipe.top_rect.right < 0 and pipe.top_rect.left < bird.rect.right < pipe.top_rect.right:
                    score += 1

            if bird.rect.top > SCREEN_HEIGHT or bird.rect.bottom < 0:
                game_over = True

        draw_background(screen)
        if not game_over:
            for pipe in pipes:
                pipe.draw(screen)
            bird.draw(screen)
            draw_hud(screen, score)
        else:
            game_over_screen(screen, score)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    while True:
        main()