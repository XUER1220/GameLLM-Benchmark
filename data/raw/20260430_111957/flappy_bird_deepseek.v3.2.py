import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = 0.35
FLAP_STRENGTH = -7.5
GROUND_HEIGHT = 100
PIPE_WIDTH = 80
PIPE_GAP = 170
PIPE_SPEED = 3
PIPE_SPAWN_INTERVAL = 90
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
BIRD_START_X = 160
BIRD_START_Y = 300
FPS = 60

COLORS = {
    "background": (135, 206, 250),
    "bird": (255, 255, 0),
    "pipe": (0, 160, 0),
    "ground": (222, 184, 135),
    "text": (255, 255, 255),
    "game_over_bg": (0, 0, 0, 180)
}

class Bird:
    def __init__(self):
        self.x = BIRD_START_X
        self.y = BIRD_START_Y
        self.velocity = 0
        self.width = BIRD_WIDTH
        self.height = BIRD_HEIGHT
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.y = self.y

    def draw(self, screen):
        pygame.draw.rect(screen, COLORS["bird"], self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

    def check_boundary(self):
        return self.y <= 0 or self.y + self.height >= SCREEN_HEIGHT - GROUND_HEIGHT

class PipePair:
    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(150, SCREEN_HEIGHT - GROUND_HEIGHT - 150)
        self.top_pipe = pygame.Rect(self.x, 0, PIPE_WIDTH, self.gap_y - PIPE_GAP // 2)
        self.bottom_pipe = pygame.Rect(self.x, self.gap_y + PIPE_GAP // 2, PIPE_WIDTH, SCREEN_HEIGHT)
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED
        self.top_pipe.x = self.x
        self.bottom_pipe.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, COLORS["pipe"], self.top_pipe)
        pygame.draw.rect(screen, COLORS["pipe"], self.bottom_pipe)
        pygame.draw.rect(screen, (0, 100, 0), self.top_pipe, 3)
        pygame.draw.rect(screen, (0, 100, 0), self.bottom_pipe, 3)

    def collide(self, bird_rect):
        return self.top_pipe.colliderect(bird_rect) or self.bottom_pipe.colliderect(bird_rect)

    def is_offscreen(self):
        return self.x + PIPE_WIDTH < 0

    def check_scored(self, bird_rect):
        if not self.passed and bird_rect.x > self.x + PIPE_WIDTH:
            self.passed = True
            return True
        return False

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird Easy")
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.frame_count = 0
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if not self.game_over and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                    self.bird.flap()
                if event.key == pygame.K_r:
                    self.reset()

    def update(self):
        if not self.game_over:
            self.bird.update()
            self.frame_count += 1

            if self.frame_count % PIPE_SPAWN_INTERVAL == 0:
                self.pipes.append(PipePair(SCREEN_WIDTH))

            for pipe in self.pipes[:]:
                pipe.update()
                if pipe.check_scored(self.bird.rect):
                    self.score += 1
                if pipe.collide(self.bird.rect):
                    self.game_over = True
                if pipe.is_offscreen():
                    self.pipes.remove(pipe)

            if self.bird.check_boundary():
                self.game_over = True

    def draw(self):
        self.screen.fill(COLORS["background"])

        for pipe in self.pipes:
            pipe.draw(self.screen)

        pygame.draw.rect(self.screen, COLORS["ground"], (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        pygame.draw.line(self.screen, (139, 69, 19), (0, SCREEN_HEIGHT - GROUND_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT), 3)

        self.bird.draw(self.screen)

        score_text = self.font.render(f"Score: {self.score}", True, COLORS["text"])
        self.screen.blit(score_text, (10, 10))

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font.render("Game Over", True, COLORS["text"])
            final_score_text = self.font.render(f"Final Score: {self.score}", True, COLORS["text"])
            restart_text = self.small_font.render("Press R to Restart", True, COLORS["text"])

            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()