import pygame
import random

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
PIPE_FREQ = 90
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
BIRD_START_X = 160
BIRD_START_Y = 300
GROUND_HEIGHT = 80
PIPE_MIN_Y = 100
PIPE_MAX_Y = SCREEN_HEIGHT - GROUND_HEIGHT - PIPE_GAP - 100

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SKY_BLUE = (135, 206, 235)
GROUND_COLOR = (222, 184, 135)
BIRD_COLOR = (255, 200, 0)
PIPE_COLOR = (0, 180, 0)
RED = (255, 50, 50)
TEXT_COLOR = (30, 30, 30)

class Bird:
    def __init__(self):
        self.x = BIRD_START_X
        self.y = BIRD_START_Y
        self.vx = 0
        self.vy = 0
        self.rect = pygame.Rect(0, 0, BIRD_WIDTH, BIRD_HEIGHT)

    def jump(self):
        self.vy = FLAP_STRENGTH

    def update(self):
        self.vy += GRAVITY
        self.y += self.vy
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        pygame.draw.ellipse(screen, BIRD_COLOR, self.rect)
        pygame.draw.ellipse(screen, BLACK, self.rect, 2)

    def check_boundary(self):
        return self.y - BIRD_HEIGHT//2 < 0 or self.y + BIRD_HEIGHT//2 > SCREEN_HEIGHT - GROUND_HEIGHT

class PipePair:
    def __init__(self, x):
        self.x = x
        self.center_y = random.randint(PIPE_MIN_Y, PIPE_MAX_Y)
        self.top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.center_y - PIPE_GAP//2)
        self.bottom_rect = pygame.Rect(self.x, self.center_y + PIPE_GAP//2, PIPE_WIDTH, SCREEN_HEIGHT)
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, PIPE_COLOR, self.top_rect)
        pygame.draw.rect(screen, PIPE_COLOR, self.bottom_rect)
        pygame.draw.rect(screen, BLACK, self.top_rect, 2)
        pygame.draw.rect(screen, BLACK, self.bottom_rect, 2)

    def offscreen(self):
        return self.x + PIPE_WIDTH < 0

    def collides_with(self, bird_rect):
        return self.top_rect.colliderect(bird_rect) or self.bottom_rect.colliderect(bird_rect)

def draw_ground(screen):
    pygame.draw.rect(screen, GROUND_COLOR, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
    pygame.draw.line(screen, BLACK, (0, SCREEN_HEIGHT - GROUND_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT), 2)

def draw_text(screen, text, size, y_offset, color=TEXT_COLOR):
    font = pygame.font.SysFont(None, size)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + y_offset))
    screen.blit(surf, rect)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flappy Bird Easy")
    clock = pygame.time.Clock()

    def init_game():
        bird = Bird()
        pipes = []
        score = 0
        frame_count = 0
        game_over = False
        return bird, pipes, score, frame_count, game_over

    bird, pipes, score, frame_count, game_over = init_game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    bird, pipes, score, frame_count, game_over = init_game()
                if not game_over and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                    bird.jump()

        if not game_over:
            bird.update()
            if bird.check_boundary():
                game_over = True

            frame_count += 1
            if frame_count % PIPE_FREQ == 20:
                pipes.append(PipePair(SCREEN_WIDTH))

            for pipe in pipes[:]:
                pipe.update()
                if pipe.collides_with(bird.rect):
                    game_over = True
                if not pipe.passed and pipe.x + PIPE_WIDTH < bird.x:
                    pipe.passed = True
                    score += 1
                if pipe.offscreen():
                    pipes.remove(pipe)

        screen.fill(SKY_BLUE)
        for pipe in pipes:
            pipe.draw(screen)
        draw_ground(screen)
        bird.draw(screen)

        score_font = pygame.font.SysFont(None, 48)
        score_surf = score_font.render(str(score), True, TEXT_COLOR)
        screen.blit(score_surf, (30, 30))

        if game_over:
            draw_text(screen, "Game Over", 64, -80, RED)
            draw_text(screen, f"Score: {score}", 48, -10)
            draw_text(screen, "Press R to Restart", 36, 60)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()