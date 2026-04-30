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
PIPE_SPAWN_INTERVAL = 90
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
BIRD_START_X = 160
BIRD_START_Y = 300
GROUND_HEIGHT = 100

BACKGROUND_COLOR = (135, 206, 235)
GROUND_COLOR = (222, 184, 135)
BIRD_COLOR = (255, 255, 0)
PIPE_COLOR = (50, 205, 50)
TEXT_COLOR = (255, 255, 255)
GAME_OVER_BG_COLOR = (0, 0, 0, 180)

class Bird:
    def __init__(self):
        self.x = BIRD_START_X
        self.y = BIRD_START_Y
        self.vel_y = 0
        self.width = BIRD_WIDTH
        self.height = BIRD_HEIGHT
        self.alive = True

    def flap(self):
        self.vel_y = FLAP_STRENGTH

    def update(self):
        if not self.alive:
            return
        self.vel_y += GRAVITY
        self.y += self.vel_y

    def draw(self, screen):
        pygame.draw.rect(screen, BIRD_COLOR, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 2)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Pipe:
    def __init__(self, x, gap_y):
        self.x = x
        self.gap_y = gap_y
        self.width = PIPE_WIDTH
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self, screen):
        top_pipe_height = self.gap_y - PIPE_GAP // 2
        bottom_pipe_top = self.gap_y + PIPE_GAP // 2
        pygame.draw.rect(screen, PIPE_COLOR, (self.x, 0, self.width, top_pipe_height))
        pygame.draw.rect(screen, PIPE_COLOR, (self.x, bottom_pipe_top, self.width, SCREEN_HEIGHT - bottom_pipe_top))
        pygame.draw.rect(screen, (0, 100, 0), (self.x, 0, self.width, top_pipe_height), 3)
        pygame.draw.rect(screen, (0, 100, 0), (self.x, bottom_pipe_top, self.width, SCREEN_HEIGHT - bottom_pipe_top), 3)

    def get_top_rect(self):
        return pygame.Rect(self.x, 0, self.width, self.gap_y - PIPE_GAP // 2)

    def get_bottom_rect(self):
        bottom_top = self.gap_y + PIPE_GAP // 2
        return pygame.Rect(self.x, bottom_top, self.width, SCREEN_HEIGHT - bottom_top)

def draw_ground(screen):
    pygame.draw.rect(screen, GROUND_COLOR, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
    pygame.draw.line(screen, (139, 115, 85), (0, SCREEN_HEIGHT - GROUND_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT), 3)

def draw_hud(screen, score, font):
    score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
    screen.blit(score_text, (10, 10))
    title_text = font.render("Flappy Bird Easy", True, TEXT_COLOR)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 10))

def draw_game_over(screen, score, font):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(GAME_OVER_BG_COLOR)
    screen.blit(overlay, (0, 0))
    game_over_text = font.render("Game Over", True, TEXT_COLOR)
    final_score_text = font.render(f"Final Score: {score}", True, TEXT_COLOR)
    restart_text = font.render("Press R to Restart", True, TEXT_COLOR)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
    screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flappy Bird Easy")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    def reset_game():
        nonlocal bird, pipes, score, frame_count, game_over
        bird = Bird()
        pipes = []
        score = 0
        frame_count = 0
        game_over = False

    reset_game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if not game_over and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                    bird.flap()
                if game_over and event.key == pygame.K_r:
                    reset_game()

        if not game_over:
            bird.update()
            frame_count += 1

            if frame_count % PIPE_SPAWN_INTERVAL == 20:
                gap_y = random.randint(100 + PIPE_GAP // 2, SCREEN_HEIGHT - GROUND_HEIGHT - 100 - PIPE_GAP // 2)
                pipes.append(Pipe(SCREEN_WIDTH, gap_y))

            for pipe in pipes[:]:
                pipe.update()
                if pipe.x + pipe.width < 0:
                    pipes.remove(pipe)

            bird_rect = bird.get_rect()
            if bird_rect.top <= 0 or bird_rect.bottom >= SCREEN_HEIGHT - GROUND_HEIGHT:
                game_over = True

            for pipe in pipes:
                if bird_rect.colliderect(pipe.get_top_rect()) or bird_rect.colliderect(pipe.get_bottom_rect()):
                    game_over = True
                if not pipe.passed and pipe.x + pipe.width < bird.x:
                    pipe.passed = True
                    score += 1

        screen.fill(BACKGROUND_COLOR)
        for pipe in pipes:
            pipe.draw(screen)
        draw_ground(screen)
        bird.draw(screen)
        draw_hud(screen, score, font)

        if game_over:
            draw_game_over(screen, score, font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()