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
FONT = pygame.font.SysFont('Arial', 30)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong Easy")
clock = pygame.time.Clock()

def draw_paddle(paddle):
    pygame.draw.rect(screen, WHITE, paddle)

def draw_ball(ball):
    pygame.draw.rect(screen, WHITE, ball)

def draw_score(left_score, right_score):
    left_text = FONT.render(str(left_score), True, WHITE)
    right_text = FONT.render(str(right_score), True, WHITE)
    screen.blit(left_text, (SCREEN_WIDTH // 4, 20))
    screen.blit(right_text, (3 * SCREEN_WIDTH // 4, 20))

def draw_middle_line():
    pygame.draw.line(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)

def reset_game():
    return pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE), 0, 0

def main():
    left_paddle = pygame.Rect(50, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = pygame.Rect(SCREEN_WIDTH - 50 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball, left_score, right_score = reset_game()
    ball_dx, ball_dy = 5, 5
    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    left_paddle, right_paddle, ball, left_score, right_score = reset_game()
                    game_over = False

        keys = pygame.key.get_pressed()
        if not game_over:
            if keys[pygame.K_w] and left_paddle.top > 0:
                left_paddle.y -= 7
            if keys[pygame.K_s] and left_paddle.bottom < SCREEN_HEIGHT:
                left_paddle.y += 7
            if keys[pygame.K_UP] and right_paddle.top > 0:
                right_paddle.y -= 7
            if keys[pygame.K_DOWN] and right_paddle.bottom < SCREEN_HEIGHT:
                right_paddle.y += 7

            ball.x += ball_dx
            ball.y += ball_dy

            if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
                ball_dy = -ball_dy
            if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
                ball_dx = -ball_dx
            if ball.left <= 0:
                right_score += 1
                ball, left_score, right_score = reset_game()
            elif ball.right >= SCREEN_WIDTH:
                left_score += 1
                ball, left_score, right_score = reset_game()

            if left_score == 7 or right_score == 7:
                game_over = True

        screen.fill(BLACK)
        draw_paddle(left_paddle)
        draw_paddle(right_paddle)
        draw_ball(ball)
        draw_score(left_score, right_score)
        draw_middle_line()

        if game_over:
            winner_text = "Left Wins!" if left_score == 7 else "Right Wins!"
            winner_surface = FONT.render(winner_text, True, WHITE)
            screen.blit(winner_surface, (SCREEN_WIDTH // 2 - winner_surface.get_width() // 2, SCREEN_HEIGHT // 2 - winner_surface.get_height() // 2))
            restart_text = FONT.render("Press R to Restart", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()