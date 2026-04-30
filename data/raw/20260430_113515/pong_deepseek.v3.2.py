import pygame
import sys
import random

random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)

PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
PADDLE_SPEED = 7
BALL_SIZE = 18
BALL_SPEED_X = 5
BALL_SPEED_Y = 5

WIN_SCORE = 7

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = PADDLE_SPEED

    def move(self, dy):
        self.rect.y += dy
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
        self.reset()

    def reset(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.dx = BALL_SPEED_X if random.choice([True, False]) else -BALL_SPEED_X
        self.dy = BALL_SPEED_Y if random.choice([True, False]) else -BALL_SPEED_Y

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.dy = -self.dy

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pong Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 36)
        self.reset_game()

    def reset_game(self):
        self.left_paddle = Paddle(30, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.right_paddle = Paddle(SCREEN_WIDTH - 30 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ball = Ball()
        self.left_score = 0
        self.right_score = 0
        self.winner = None
        self.game_active = True

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

        if not self.game_active:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.left_paddle.move(-PADDLE_SPEED)
        if keys[pygame.K_s]:
            self.left_paddle.move(PADDLE_SPEED)
        if keys[pygame.K_UP]:
            self.right_paddle.move(-PADDLE_SPEED)
        if keys[pygame.K_DOWN]:
            self.right_paddle.move(PADDLE_SPEED)

    def update(self):
        if not self.game_active:
            return

        self.ball.update()

        if self.ball.rect.colliderect(self.left_paddle.rect):
            self.ball.dx = abs(self.ball.dx)
            self.ball.rect.left = self.left_paddle.rect.right
        elif self.ball.rect.colliderect(self.right_paddle.rect):
            self.ball.dx = -abs(self.ball.dx)
            self.ball.rect.right = self.right_paddle.rect.left

        if self.ball.rect.left <= 0:
            self.right_score += 1
            self.check_winner()
            self.ball.reset()
        elif self.ball.rect.right >= SCREEN_WIDTH:
            self.left_score += 1
            self.check_winner()
            self.ball.reset()

    def check_winner(self):
        if self.left_score >= WIN_SCORE:
            self.winner = "Left Player"
            self.game_active = False
        elif self.right_score >= WIN_SCORE:
            self.winner = "Right Player"
            self.game_active = False

    def draw(self):
        self.screen.fill(BLACK)

        pygame.draw.line(self.screen, GRAY, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)

        self.left_paddle.draw(self.screen)
        self.right_paddle.draw(self.screen)
        self.ball.draw(self.screen)

        left_score_text = self.font.render(str(self.left_score), True, WHITE)
        right_score_text = self.font.render(str(self.right_score), True, WHITE)
        self.screen.blit(left_score_text, (SCREEN_WIDTH // 4, 20))
        self.screen.blit(right_score_text, (3 * SCREEN_WIDTH // 4 - right_score_text.get_width(), 20))

        if self.winner:
            win_text = self.font.render(f"{self.winner} Wins!", True, WHITE)
            self.screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            restart_text = self.small_font.render("Press R to Restart", True, WHITE)
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