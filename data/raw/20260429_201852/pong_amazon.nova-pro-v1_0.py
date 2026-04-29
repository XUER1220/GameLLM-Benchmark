import pygame
import random

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
PADDLE_WIDTH, PADDLE_HEIGHT = 18, 100
BALL_SIZE = 18
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong Easy")
clock = pygame.time.Clock()

def draw_objects(left_paddle, right_paddle, ball, left_score, right_score):
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, left_paddle)
    pygame.draw.rect(screen, WHITE, right_paddle)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.aaline(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))
    font = pygame.font.Font(None, 36)
    left_text = font.render(str(left_score), True, WHITE)
    right_text = font.render(str(right_score), True, WHITE)
    screen.blit(left_text, (SCREEN_WIDTH // 4, 20))
    screen.blit(right_text, (3 * SCREEN_WIDTH // 4, 20))

def main():
    left_paddle = pygame.Rect(50, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = pygame.Rect(SCREEN_WIDTH - 50 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
    ball_dx, ball_dy = 5, 5
    left_score, right_score = 0, 0
    game_running, ball_in_play = True, False

    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                if event.key == pygame.K_r:
                    left_score, right_score = 0, 0
                    ball_in_play = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            left_paddle.y -= 7
        if keys[pygame.K_s]:
            left_paddle.y += 7
        if keys[pygame.K_UP]:
            right_paddle.y -= 7
        if keys[pygame.K_DOWN]:
            right_paddle.y += 7

        if not ball_in_play:
            if keys[pygame.K_SPACE]:
                ball_in_play = True
                ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                ball_dx, ball_dy = 5, 5
                direction = random.choice([-1, 1])
                ball_dx *= direction
        else:
            ball.x += ball_dx
            ball.y += ball_dy

        if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
            ball_dy *= -1
        if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
            ball_dx *= -1
        if ball.left <= 0:
            right_score += 1
            ball_in_play = False
        elif ball.right >= SCREEN_WIDTH:
            left_score += 1
            ball_in_play = False

        if left_score == 7 or right_score == 7:
            game_running = False

        left_paddle.y = max(0, min(left_paddle.y, SCREEN_HEIGHT - PADDLE_HEIGHT))
        right_paddle.y = max(0, min(right_paddle.y, SCREEN_HEIGHT - PADDLE_HEIGHT))

        draw_objects(left_paddle, right_paddle, ball, left_score, right_score)
        if not game_running:
            font = pygame.font.Font(None, 36)
            text = font.render("Press R to Restart", True, RED)
            screen.blit(text, (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()