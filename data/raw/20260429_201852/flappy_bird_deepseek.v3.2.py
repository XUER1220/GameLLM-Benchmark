import pygame, random, sys

random.seed(42)

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.35
FLAP_STRENGTH = -7.5
PIPE_WIDTH = 80
PIPE_GAP = 170
PIPE_SPEED = 3
PIPE_FREQUENCY = 90
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
BIRD_START_X = 160
BIRD_START_Y = 300
GROUND_HEIGHT = 80

# 颜色
SKY_BLUE = (135, 206, 235)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 200, 50)
DARK_GREEN = (40, 180, 40)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
LIGHT_BROWN = (222, 184, 135)

class Bird:
    def __init__(self):
        self.x = BIRD_START_X
        self.y = BIRD_START_Y
        self.vel_y = 0
        self.rect = pygame.Rect(self.x - BIRD_WIDTH//2, self.y - BIRD_HEIGHT//2, BIRD_WIDTH, BIRD_HEIGHT)
        self.alive = True

    def flap(self):
        self.vel_y = FLAP_STRENGTH

    def update(self):
        self.vel_y += GRAVITY
        self.y += self.vel_y
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        pygame.draw.ellipse(screen, YELLOW, self.rect)
        pygame.draw.ellipse(screen, ORANGE, self.rect.inflate(-10, -10))
        # 眼睛
        eye_rect = pygame.Rect(self.rect.right - 15, self.rect.top + 8, 8, 8)
        pygame.draw.ellipse(screen, BLACK, eye_rect)
        # 喙
        beak_points = [(self.rect.right, self.rect.centery),
                       (self.rect.right + 15, self.rect.centery - 5),
                       (self.rect.right + 15, self.rect.centery + 5)]
        pygame.draw.polygon(screen, ORANGE, beak_points)

    def check_bounds(self):
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT - GROUND_HEIGHT:
            return True
        return False

class Pipe:
    def __init__(self, x):
        self.x = x
        self.passed = False
        self.height = random.randint(150, SCREEN_HEIGHT - GROUND_HEIGHT - 150 - PIPE_GAP)
        self.top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.height)
        self.bottom_rect = pygame.Rect(self.x, self.height + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT)

    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.top_rect)
        pygame.draw.rect(screen, DARK_GREEN, self.top_rect.inflate(10, 0))
        pygame.draw.rect(screen, GREEN, self.bottom_rect)
        pygame.draw.rect(screen, DARK_GREEN, self.bottom_rect.inflate(10, 0))

    def collide(self, bird_rect):
        return bird_rect.colliderect(self.top_rect) or bird_rect.colliderect(self.bottom_rect)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)
        self.reset_game()

    def reset_game(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.pipe_timer = 0

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_r:
                        self.reset_game()
                    if not self.game_over and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                        self.bird.flap()

            if not self.game_over:
                self.bird.update()
                if self.bird.check_bounds():
                    self.game_over = True

                self.pipe_timer += 1
                if self.pipe_timer > PIPE_FREQUENCY:
                    self.pipes.append(Pipe(SCREEN_WIDTH))
                    self.pipe_timer = 0

                for pipe in self.pipes[:]:
                    pipe.update()
                    if pipe.collide(self.bird.rect):
                        self.game_over = True
                    if pipe.x < -PIPE_WIDTH:
                        self.pipes.remove(pipe)
                    if not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.rect.left:
                        pipe.passed = True
                        self.score += 1

            self.screen.fill(SKY_BLUE)
            for pipe in self.pipes:
                pipe.draw(self.screen)
            pygame.draw.rect(self.screen, LIGHT_BROWN, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
            pygame.draw.rect(self.screen, BROWN, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, 10))
            self.bird.draw(self.screen)

            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))

            if self.game_over:
                game_over_text = self.font.render("Game Over", True, RED)
                restart_text = self.small_font.render("Press R to Restart", True, WHITE)
                final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
                self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
                self.screen.blit(final_score_text, (SCREEN_WIDTH//2 - final_score_text.get_width()//2, SCREEN_HEIGHT//2))
                self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 50))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()