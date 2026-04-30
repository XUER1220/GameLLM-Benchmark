import pygame, sys, random
random.seed(42)

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

GRAVITY = 0.35
FLAP_STRENGTH = -7.5
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
BIRD_START_X = 160
BIRD_START_Y = 300

PIPE_WIDTH = 80
PIPE_GAP = 170
PIPE_SPEED = 3
PIPE_SPAWN_INTERVAL = 90
MIN_PIPE_GAP_CENTER = 150
MAX_PIPE_GAP_CENTER = SCREEN_HEIGHT - 150

GROUND_HEIGHT = 50

# 颜色
BACKGROUND = (135, 206, 235)
BIRD_COLOR = (255, 200, 0)
PIPE_COLOR = (0, 180, 0)
GROUND_COLOR = (222, 184, 135)
TEXT_COLOR = (30, 30, 30)
WHITE = (255, 255, 255)

class Bird:
    def __init__(self):
        self.x = BIRD_START_X
        self.y = BIRD_START_Y
        self.vel_y = 0
        self.rect = pygame.Rect(0, 0, BIRD_WIDTH, BIRD_HEIGHT)
        self.update_rect()
        self.alive = True

    def update_rect(self):
        self.rect.topleft = (self.x, self.y)

    def flap(self):
        self.vel_y = FLAP_STRENGTH

    def update(self):
        self.vel_y += GRAVITY
        self.y += self.vel_y
        self.update_rect()

    def draw(self, screen):
        pygame.draw.rect(screen, BIRD_COLOR, self.rect, border_radius=8)
        pygame.draw.rect(screen, (200, 150, 0), self.rect, width=3, border_radius=8)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_center = random.randint(MIN_PIPE_GAP_CENTER, MAX_PIPE_GAP_CENTER)
        self.top_pipe = pygame.Rect(self.x, 0, PIPE_WIDTH, self.gap_center - PIPE_GAP // 2)
        self.bottom_pipe = pygame.Rect(self.x, self.gap_center + PIPE_GAP // 2, PIPE_WIDTH, SCREEN_HEIGHT)
        self.passed = False
        self.scored = False

    def update(self):
        self.x -= PIPE_SPEED
        self.top_pipe.x = self.x
        self.bottom_pipe.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, PIPE_COLOR, self.top_pipe, border_radius=5)
        pygame.draw.rect(screen, PIPE_COLOR, self.bottom_pipe, border_radius=5)

    def collides_with(self, bird_rect):
        return self.top_pipe.colliderect(bird_rect) or self.bottom_pipe.colliderect(bird_rect)

class Ground:
    def __init__(self):
        self.rect = pygame.Rect(0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT)

    def draw(self, screen):
        pygame.draw.rect(screen, GROUND_COLOR, self.rect)
        pygame.draw.line(screen, (180, 140, 100), (0, SCREEN_HEIGHT - GROUND_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT), 4)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.reset_game()

    def reset_game(self):
        self.bird = Bird()
        self.pipes = []
        self.ground = Ground()
        self.score = 0
        self.game_over = False
        self.pipe_timer = 0
        self.last_pipe_x = SCREEN_WIDTH

    def spawn_pipe(self):
        new_x = self.last_pipe_x + PIPE_WIDTH + 100
        self.pipes.append(Pipe(new_x))
        self.last_pipe_x = new_x

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    self.reset_game()
                if not self.game_over and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                    self.bird.flap()

    def update(self):
        if self.game_over:
            return

        self.bird.update()

        # 边界检查
        if self.bird.y < 0 or self.bird.y + BIRD_HEIGHT > SCREEN_HEIGHT - GROUND_HEIGHT:
            self.game_over = True

        # 管道生成
        self.pipe_timer += 1
        if self.pipe_timer >= PIPE_SPAWN_INTERVAL:
            self.spawn_pipe()
            self.pipe_timer = 0

        # 管道更新与碰撞
        for pipe in self.pipes[:]:
            pipe.update()
            if pipe.collides_with(self.bird.rect):
                self.game_over = True

            if not pipe.scored and pipe.x + PIPE_WIDTH < self.bird.x:
                pipe.scored = True
                self.score += 1

            if pipe.x + PIPE_WIDTH < 0:
                self.pipes.remove(pipe)

    def draw(self):
        self.screen.fill(BACKGROUND)

        for pipe in self.pipes:
            pipe.draw(self.screen)

        self.ground.draw(self.screen)
        self.bird.draw(self.screen)

        # 分数
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (20, 20))

        # 游戏结束提示
        if self.game_over:
            game_over_text = self.font.render("Game Over", True, WHITE)
            final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.small_font.render("Press R to Restart, ESC to Quit", True, WHITE)
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

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