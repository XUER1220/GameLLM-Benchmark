import pygame
import random
import sys

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
PADDLE_SPEED = 7

BALL_SIZE = 18
BALL_INITIAL_SPEED_X = 5
BALL_INITIAL_SPEED_Y = 5

WIN_SCORE = 7

BG_COLOR = (15, 15, 30)
LINE_COLOR = (100, 100, 150)
PADDLE_COLOR = (220, 220, 255)
BALL_COLOR = (255, 255, 200)
TEXT_COLOR = (230, 230, 230)
SCORE_COLOR = (180, 250, 180)
WIN_COLOR = (255, 200, 100)

random.seed(42)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 32)

class Paddle:
    def __init__(self, x, up_key, down_key):
        self.rect = pygame.Rect(x - PADDLE_WIDTH // 2, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.up_key = up_key
        self.down_key = down_key
        self.speed = PADDLE_SPEED

    def move(self, keys):
        if keys[self.up_key] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[self.down_key] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed

    def draw(self):
        pygame.draw.rect(screen, PADDLE_COLOR, self.rect, border_radius=4)

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
        self.reset()

    def reset(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed_x = BALL_INITIAL_SPEED_X * random.choice([-1, 1])
        self.speed_y = BALL_INITIAL_SPEED_Y * random.choice([-1, 1])

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.speed_y *= -1
            self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - BALL_SIZE))

    def draw(self):
        pygame.draw.ellipse(screen, BALL_COLOR, self.rect)

def draw_center_line():
    for y in range(0, SCREEN_HEIGHT, 30):
        pygame.draw.rect(screen, LINE_COLOR, (SCREEN_WIDTH // 2 - 1, y, 2, 15))

def draw_scores(left_score, right_score):
    left_text = font.render(str(left_score), True, SCORE_COLOR)
    right_text = font.render(str(right_score), True, SCORE_COLOR)
    screen.blit(left_text, (SCREEN_WIDTH // 4 - left_text.get_width() // 2, 20))
    screen.blit(right_text, (SCREEN_WIDTH * 3 // 4 - right_text.get_width() // 2, 20))

def draw_winner(winner_text):
    win_surf = font.render(winner_text, True, WIN_COLOR)
    screen.blit(win_surf, (SCREEN_WIDTH // 2 - win_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
    restart_surf = small_font.render("Press R to Restart", True, TEXT_COLOR)
    screen.blit(restart_surf, (SCREEN_WIDTH // 2 - restart_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 30))

def main():
    left_paddle = Paddle(30, pygame.K_w, pygame.K_s)
    right_paddle = Paddle(SCREEN_WIDTH - 30, pygame.K_UP, pygame.K_DOWN)
    ball = Ball()

    left_score = 0
    right_score = 0
    game_over = False
    winner = ""

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r and game_over:
                    left_score = 0
                    right_score = 0
                    game_over = False
                    ball.reset()
                    left_paddle.rect.centery = SCREEN_HEIGHT // 2
                    right_paddle.rect.centery = SCREEN_HEIGHT // 2

        keys = pygame.key.get_pressed()

        if not game_over:
            left_paddle.move(keys)
            right_paddle.move(keys)

            ball.update()

            if ball.rect.colliderect(left_paddle.rect) and ball.speed_x < 0:
                ball.speed_x *= -1
                ball.rect.left = left_paddle.rect.right
            if ball.rect.colliderect(right_paddle.rect) and ball.speed_x > 0:
                ball.speed_x *= -1
                ball.rect.right = right_paddle.rect.left

            if ball.rect.left <= 0:
                right_score += 1
                ball.reset()
            if ball.rect.right >= SCREEN_WIDTH:
                left_score += 1
                ball.reset()

            if left_score >= WIN_SCORE:
                game_over = True
                winner = "Left Player Wins!"
            if right_score >= WIN_SCORE:
                game_over = True
                winner = "Right Player Wins!"

        screen.fill(BG_COLOR)
        draw_center_line()
        left_paddle.draw()
        right_paddle.draw()
        ball.draw()
        draw_scores(left_score, right_score)

        if game_over:
            draw_winner(winner)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()