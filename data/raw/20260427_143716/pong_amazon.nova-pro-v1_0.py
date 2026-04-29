import pygame
import random

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PADDLE_WIDTH, PADDLE_HEIGHT = 18, 100
BALL_SIZE = 18
BALL_SPEED_X, BALL_SPEED_Y = 5, 5
PADDLE_SPEED = 7
WINNING_SCORE = 7

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong Easy")
clock = pygame.time.Clock()

def draw_paddle(x, y):
    pygame.draw.rect(screen, WHITE, (x, y, PADDLE_WIDTH, PADDLE_HEIGHT))

def draw_ball(x, y):
    pygame.draw.rect(screen, WHITE, (x, y, BALL_SIZE, BALL_SIZE))

def draw_middle_line():
    pygame.draw.line(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)

def draw_score(left_score, right_score):
    font = pygame.font.Font(None, 36)
    left_text = font.render(f"{left_score}", True, WHITE)
    right_text = font.render(f"{right_score}", True, WHITE)
    screen.blit(left_text, (SCREEN_WIDTH // 4, 20))
    screen.blit(right_text, (3 * SCREEN_WIDTH // 4, 20))

def show_winner(winner):
    font = pygame.font.Font(None, 74)
    win_text = font.render(f"{winner} wins!", True, WHITE)
    screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - win_text.get_height() // 2))
    font = pygame.font.Font(None, 36)
    restart_text = font.render("Press R to Restart", True, WHITE)
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

def reset_ball():
    return SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, random.choice([-BALL_SPEED_X, BALL_SPEED_X]), BALL_SPEED_Y

def main():
    left_paddle_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
    right_paddle_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
    left_score = 0
    right_score = 0
    ball_x, ball_y, ball_speed_x, ball_speed_y = reset_ball()

    running = True
    game_over = False

    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    left_score = 0
                    right_score = 0
                    ball_x, ball_y, ball_speed_x, ball_speed_y = reset_ball()
                    game_over = False

        keys = pygame.key.get_pressed()
        if not game_over:
            if keys[pygame.K_w] and left_paddle_y > 0:
                left_paddle_y -= PADDLE_SPEED
            if keys[pygame.K_s] and left_paddle_y < SCREEN_HEIGHT - PADDLE_HEIGHT:
                left_paddle_y += PADDLE_SPEED
            if keys[pygame.K_UP] and right_paddle_y > 0:
                right_paddle_y -= PADDLE_SPEED
            if keys[pygame.K_DOWN] and right_paddle_y < SCREEN_HEIGHT - PADDLE_HEIGHT:
                right_paddle_y += PADDLE_SPEED

            ball_x += ball_speed_x
            ball_y += ball_speed_y

            if ball_y <= 0 or ball_y >= SCREEN_HEIGHT - BALL_SIZE:
                ball_speed_y = -ball_speed_y

            if (ball_x <= left_paddle_x + PADDLE_WIDTH and left_paddle_y < ball_y < left_paddle_y + PADDLE_HEIGHT or
                ball_x >= right_paddle_x and right_paddle_y < ball_y < right_paddle_y + PADDLE_HEIGHT):
                ball_speed_x = -ball_speed_x

            if ball_x <= 0:
                right_score += 1
                ball_x, ball_y, ball_speed_x, ball_speed_y = reset_ball()
            elif ball_x >= SCREEN_WIDTH - BALL_SIZE:
                left_score += 1
                ball_x, ball_y, ball_speed_x, ball_speed_y = reset_ball()

            if left_score == WINNING_SCORE or right_score == WINNING_SCORE:
                game_over = True

        draw_paddle(0, left_paddle_y)
        draw_paddle(SCREEN_WIDTH - PADDLE_WIDTH, right_paddle_y)
        draw_ball(ball_x, ball_y)
        draw_middle_line()
        draw_score(left_score, right_score)

        if game_over:
            if left_score == WINNING_SCORE:
                show_winner("Left")
            else:
                show_winner("Right")

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()