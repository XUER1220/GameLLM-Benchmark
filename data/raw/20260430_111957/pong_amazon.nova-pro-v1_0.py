import pygame
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
BALL_SIZE = 18
WINNING_SCORE = 7

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong Easy")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 74)

class Paddle:
    def __init__(self, x):
        self.rect = pygame.Rect(x, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = 7

    def move(self, direction):
        if direction == "up" and self.rect.top > 0:
            self.rect.y -= self.speed
        elif direction == "down" and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
        self.reset()

    def reset(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        random.seed(42)
        self.dx = random.choice([-5, 5])
        self.dy = random.choice([-5, 5])

    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.dy = -self.dy
        if self.rect.left <= 0:
            return "right"
        if self.rect.right >= SCREEN_WIDTH:
            return "left"
        return None

    def collide(self, paddle1, paddle2):
        if self.rect.colliderect(paddle1.rect) or self.rect.colliderect(paddle2.rect):
            self.dx = -self.dx

def draw_objects(paddle1, paddle2, ball, score_left, score_right, game_over, winner):
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (255, 255, 255), paddle1.rect)
    pygame.draw.rect(screen, (255, 255, 255), paddle2.rect)
    pygame.draw.ellipse(screen, (255, 255, 255), ball.rect)
    pygame.draw.aaline(screen, (255, 255, 255), (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))
    score_display_left = font.render(str(score_left), True, (255, 255, 255))
    score_display_right = font.render(str(score_right), True, (255, 255, 255))
    screen.blit(score_display_left, (SCREEN_WIDTH // 4 - score_display_left.get_width() // 2, 20))
    screen.blit(score_display_right, (3 * SCREEN_WIDTH // 4 - score_display_right.get_width() // 2, 20))
    if game_over:
        winner_text = font.render(f"{winner} wins!", True, (255, 255, 255))
        restart_text = font.render("Press R to Restart", True, (255, 255, 255))
        screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, SCREEN_HEIGHT // 2 - winner_text.get_height() // 2))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + winner_text.get_height() // 2))
    pygame.display.flip()

def main():
    paddle1 = Paddle(30)
    paddle2 = Paddle(SCREEN_WIDTH - 30 - PADDLE_WIDTH)
    ball = Ball()
    score_left = 0
    score_right = 0
    game_over = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    paddle1 = Paddle(30)
                    paddle2 = Paddle(SCREEN_WIDTH - 30 - PADDLE_WIDTH)
                    ball = Ball()
                    score_left = 0
                    score_right = 0
                    game_over = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            paddle1.move("up")
        if keys[pygame.K_s]:
            paddle1.move("down")
        if keys[pygame.K_UP]:
            paddle2.move("up")
        if keys[pygame.K_DOWN]:
            paddle2.move("down")

        if not game_over:
            ball.collide(paddle1, paddle2)
            scored = ball.move()
            if scored == "left":
                score_left += 1
                ball.reset()
            elif scored == "right":
                score_right += 1
                ball.reset()

            if score_left == WINNING_SCORE or score_right == WINNING_SCORE:
                game_over = True

        draw_objects(paddle1, paddle2, ball, score_left, score_right, game_over, "Left" if score_left == WINNING_SCORE else "Right")
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()