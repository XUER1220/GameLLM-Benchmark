import pygame
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
PADDLE_SPEED = 7
BALL_SIZE = 18
BALL_INITIAL_SPEED = 5
WINNING_SCORE = 7

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong Easy")
clock = pygame.time.Clock()

random.seed(42)

def draw_paddle(x, y):
    pygame.draw.rect(screen, WHITE, (x, y, PADDLE_WIDTH, PADDLE_HEIGHT))

def draw_ball(x, y):
    pygame.draw.rect(screen, WHITE, (x, y, BALL_SIZE, BALL_SIZE))

def draw_score(left_score, right_score):
    font = pygame.font.Font(None, 36)
    left_text = font.render(str(left_score), True, WHITE)
    right_text = font.render(str(right_score), True, WHITE)
    screen.blit(left_text, (SCREEN_WIDTH // 4, 20))
    screen.blit(right_text, (3 * SCREEN_WIDTH // 4, 20))

def draw_center_line():
    pygame.draw.line(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)

def reset_game():
    return 0, 0, SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_INITIAL_SPEED * (random.choice([-1, 1])), BALL_INITIAL_SPEED * (random.choice([-1, 1]))

def game_over_screen(winner):
    font = pygame.font.Font(None, 74)
    text = font.render(f"{winner} wins!", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    font = pygame.font.Font(None, 36)
    text = font.render("Press R to Restart", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

left_score, right_score, ball_x, ball_y, ball_dx, ball_dy = reset_game()
left_paddle_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
right_paddle_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                left_score, right_score, ball_x, ball_y, ball_dx, ball_dy = reset_game()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and left_paddle_y > 0:
        left_paddle_y -= PADDLE_SPEED
    if keys[pygame.K_s] and left_paddle_y < SCREEN_HEIGHT - PADDLE_HEIGHT:
        left_paddle_y += PADDLE_SPEED
    if keys[pygame.K_UP] and right_paddle_y > 0:
        right_paddle_y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and right_paddle_y < SCREEN_HEIGHT - PADDLE_HEIGHT:
        right_paddle_y += PADDLE_SPEED

    ball_x += ball_dx
    ball_y += ball_dy

    if ball_y <= 0 or ball_y >= SCREEN_HEIGHT - BALL_SIZE:
        ball_dy *= -1
    if (ball_x <= PADDLE_WIDTH and left_paddle_y < ball_y < left_paddle_y + PADDLE_HEIGHT) or (ball_x >= SCREEN_WIDTH - PADDLE_WIDTH - BALL_SIZE and right_paddle_y < ball_y < right_paddle_y + PADDLE_HEIGHT):
        ball_dx *= -1
    if ball_x <= 0:
        right_score += 1
        left_score, right_score, ball_x, ball_y, ball_dx, ball_dy = reset_game()
    elif ball_x >= SCREEN_WIDTH - BALL_SIZE:
        left_score += 1
        left_score, right_score, ball_x, ball_y, ball_dx, ball_dy = reset_game()

    screen.fill(BLACK)
    draw_paddle(PADDLE_WIDTH, left_paddle_y)
    draw_paddle(SCREEN_WIDTH - 2 * PADDLE_WIDTH, right_paddle_y)
    draw_ball(ball_x, ball_y)
    draw_center_line()
    draw_score(left_score, right_score)

    if left_score >= WINNING_SCORE:
        game_over_screen("Left")
    elif right_score >= WINNING_SCORE:
        game_over_screen("Right")

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()