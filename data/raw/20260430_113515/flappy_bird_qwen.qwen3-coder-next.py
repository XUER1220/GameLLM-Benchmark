import pygame
import sys
import random

# Fixed constants
WIDTH, HEIGHT = 800, 600
FPS = 60
BIRD_WIDTH, BIRD_HEIGHT = 40, 30
BIRD_X, BIRD_Y_INIT = 160, 300
GRAVITY = 0.35
FLAP_STRENGTH = -7.5
PIPE_WIDTH = 80
PIPE_GAP = 170
PIPE_SPEED = 3
PIPE_SPAWN_FRAMES = 90
RANDOM_SEED = 42

# Colors
SKY_COLOR = (135, 206, 235)
GROUND_COLOR = (75, 75, 75)
BIRD_COLOR = (255, 215, 0)
PIPE_COLOR = (34, 139, 34)
PIPE_BORDER_COLOR = (0, 100, 0)
TEXT_COLOR = (255, 255, 255)
HIGH_SCORE_BG_COLOR = (0, 0, 0, 128)

class Bird:
    def __init__(self):
        self.rect = pygame.Rect(BIRD_X, BIRD_Y_INIT, BIRD_WIDTH, BIRD_HEIGHT)
        self.velocity = 0

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.rect.y += self.velocity

    def draw(self, screen):
        pygame.draw.rect(screen, BIRD_COLOR, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.passed = False
        # Randomize pipe opening center within reasonable bounds
        min_y = 100
        max_y = HEIGHT - 150 - PIPE_GAP
        center_y = random.randint(min_y, max_y)
        self.top_rect = pygame.Rect(x, 0, PIPE_WIDTH, center_y)
        self.bottom_rect = pygame.Rect(x, center_y + PIPE_GAP, PIPE_WIDTH, HEIGHT - (center_y + PIPE_GAP))

    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x -= PIPE_SPEED
        self.bottom_rect.x -= PIPE_SPEED

    def draw(self, screen):
        # Top pipe
        pygame.draw.rect(screen, PIPE_COLOR, self.top_rect)
        pygame.draw.rect(screen, PIPE_BORDER_COLOR, self.top_rect, 3)
        # Bottom pipe
        pygame.draw.rect(screen, PIPE_COLOR, self.bottom_rect)
        pygame.draw.rect(screen, PIPE_BORDER_COLOR, self.bottom_rect, 3)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Flappy Bird Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.reset_game()

    def reset_game(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.frames = 0
        self.game_state = "START"  # START, PLAYING, GAMEOVER
        self.last_pipe_frame = -PIPE_SPAWN_FRAMES // 2  # Ensure first pipe comes quickly
        random.seed(RANDOM_SEED)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r or event.key == pygame.K_R:
                    self.reset_game()
                elif self.game_state == "START" and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                    self.game_state = "PLAYING"
                    self.bird.flap()
                elif self.game_state == "PLAYING" and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                    self.bird.flap()
                elif self.game_state == "GAMEOVER" and (event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_r or event.key == pygame.K_R):
                    self.reset_game()

    def update(self):
        if self.game_state == "PLAYING":
            # Update bird
            self.bird.update()

            # Check collision with ground or ceiling
            if self.bird.rect.bottom >= HEIGHT - 50 or self.bird.rect.top <= 0:
                self.game_state = "GAMEOVER"

            # Update pipes
            for pipe in self.pipes[:]:
                pipe.update()

                # Remove pipes that moved off screen
                if pipe.x + PIPE_WIDTH < 0:
                    self.pipes.remove(pipe)

                # Score counting
                if not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.rect.left:
                    pipe.passed = True
                    self.score += 1

                # Check collision
                if (self.bird.rect.colliderect(pipe.top_rect) or 
                    self.bird.rect.colliderect(pipe.bottom_rect)):
                    self.game_state = "GAMEOVER"

            # Spawn pipes
            self.frames += 1
            if self.frames - self.last_pipe_frame >= PIPE_SPAWN_FRAMES:
                self.pipes.append(Pipe(WIDTH))
                self.last_pipe_frame = self.frames

            # Game over if bird hit ground
            if self.bird.rect.bottom >= HEIGHT - 50:
                self.game_state = "GAMEOVER"

    def draw(self):
        self.screen.fill(SKY_COLOR)

        # Draw ground
        ground_height = 50
        pygame.draw.rect(self.screen, GROUND_COLOR, (0, HEIGHT - ground_height, WIDTH, ground_height))
        pygame.draw.line(self.screen, (200, 200, 200), (0, HEIGHT - ground_height), (WIDTH, HEIGHT - ground_height), 2)

        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)

        # Draw bird
        self.bird.draw(self.screen)

        # HUD
        self.draw_hud()

        # Special states
        if self.game_state == "START":
            self.show_text("Flappy Bird Easy", (WIDTH // 2, HEIGHT // 2 - 60), self.font, True)
            self.show_text("Press SPACE or UP to Start", (WIDTH // 2, HEIGHT // 2), self.small_font, True)
        elif self.game_state == "GAMEOVER":
            self.show_text("Game Over", (WIDTH // 2, HEIGHT // 2 - 60), self.font, True)
            self.show_text(f"Score: {self.score}", (WIDTH // 2, HEIGHT // 2), self.small_font, True)
            self.show_text("Press R or SPACE to Restart", (WIDTH // 2, HEIGHT // 2 + 60), self.small_font, True)

        pygame.display.flip()

    def draw_hud(self):
        score_surface = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        score_rect = score_surface.get_rect(center=(WIDTH // 2, 50))
        self.screen.blit(score_surface, score_rect)

        if self.game_state == "PLAYING":
            pass
        elif self.game_state == "START":
            pass
        elif self.game_state == "GAMEOVER":
            pass

    def show_text(self, text, center, font, centered=True):
        text_surface = font.render(text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=center if centered else (center[0], center[1]))
        self.screen.blit(text_surface, text_rect)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()