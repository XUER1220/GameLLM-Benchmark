import pygame
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
BALL_SIZE = 18
PADDLE_SPEED = 7
BALL_INIT_SPEED_X = 5
BALL_INIT_SPEED_Y = 5
WINNING_SCORE = 7
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
BLUE = (66, 135, 245)
RED = (245, 66, 66)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong Easy")
clock = pygame.time.Clock()

random.seed(42)

class Paddle:
    def __init__(self, x, up_key, down_key):
        self.rect = pygame.Rect(x - PADDLE_WIDTH // 2, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2,
                                 PADDLE_WIDTH, PADDLE_HEIGHT)
        self.up_key = up_key
        self.down_key = down_key
        self.speed = PADDLE_SPEED

    def move(self, dy):
        self.rect.y += dy
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=8)

class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2,
                                 SCREEN_HEIGHT // 2 - BALL_SIZE // 2,
                                 BALL_SIZE, BALL_SIZE)
        self.speed_x = BALL_INIT_SPEED_X * (1 if random.random() < 0.5 else -1)
        self.speed_y = BALL_INIT_SPEED_Y * (1 if random.random() < 0.5 else -1)

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.speed_y = -self.speed_y

    def draw(self):
        pygame.draw.ellipse(screen, WHITE, self.rect)

    def check_paddle_collision(self, paddle):
        if self.rect.colliderect(paddle.rect):
            if abs(self.rect.right - paddle.rect.left) < abs(self.speed_x) or \
               abs(self.rect.left - paddle.rect.right) < abs(self.speed_x):
                self.speed_x = -self.speed_x
                offset = (self.rect.centery - paddle.rect.centery) / (PADDLE_HEIGHT / 2)
                self.speed_y += offset * 2
                self.speed_y = max(min(self.speed_y, 6), -6)

class Game:
    def __init__(self):
        self.left_paddle = Paddle(30, pygame.K_w, pygame.K_s)
        self.right_paddle = Paddle(SCREEN_WIDTH - 30, pygame.K_UP, pygame.K_DOWN)
        self.ball = Ball()
        self.left_score = 0
        self.right_score = 0
        self.winner = None
        self.font = pygame.font.SysFont("Arial", 64)
        self.small_font = pygame.font.SysFont("Arial", 28)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r and self.winner:
                    self.__init__()
        return True

    def update(self):
        if self.winner:
            return

        keys = pygame.key.get_pressed()
        if keys[self.left_paddle.up_key]:
            self.left_paddle.move(-self.left_paddle.speed)
        if keys[self.left_paddle.down_key]:
            self.left_paddle.move(self.left_paddle.speed)
        if keys[self.right_paddle.up_key]:
            self.right_paddle.move(-self.right_paddle.speed)
        if keys[self.right_paddle.down_key]:
            self.right_paddle.move(self.right_paddle.speed)

        self.ball.update()
        self.ball.check_paddle_collision(self.left_paddle)
        self.ball.check_paddle_collision(self.right_paddle)

        if self.ball.rect.left <= 0:
            self.right_score += 1
            self.check_winner()
            self.ball.reset()
        elif self.ball.rect.right >= SCREEN_WIDTH:
            self.left_score += 1
            self.check_winner()
            self.ball.reset()

    def check_winner(self):
        if self.left_score >= WINNING_SCORE:
            self.winner = "Left Player"
        elif self.right_score >= WINNING_SCORE:
            self.winner = "Right Player"

    def draw(self):
        screen.fill(BLACK)

        for y in range(30, SCREEN_HEIGHT, 40):
            pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH // 2 - comprise-line_width, y, 10, 20))

        self.left_paddle.draw()
        self.right_paddle.draw()
        self.ball.draw()

        left_score_surf = self.font.render(str(self.left_score), True, BLUE)
        right_score_surf = self.font.render(str(self.right_score), True, RED)
        screen.blit(left_score_surf, (SCREEN_WIDTH // 4 - left_score_surf.get_width() // 2, 30))
        screen.blit(right_score_surf, (3 * SCREEN_WIDTH // 4 - right_score_surf.get_width() // 2, 30))

        if self.winner:
            win_text = f"{self.winner} Wins!"
            win_surf = self.font.render(win_text, True, WHITE)
            screen.blit(win_surf, (SCREEN_WIDTH // 2 - win_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            restart_surf = self.small_font.render("Press R to Restart", True, GRAY)
            screen.blit(restart_surf, (SCREEN_WIDTH // 2 - restart_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 30))

        pygame.display.flip()

def main():
    game = Game()
    running = True
    while running:
        running = game.handle_events()
        game.update()
        game.draw()
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    main()