import pygame
import random

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
BALL_SIZE = 18
WINNING_SCORE = 7

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong Easy")
clock = pygame.time.Clock()

def draw_paddle(x, y):
    pygame.draw.rect(screen, WHITE, (x, y, PADDLE_WIDTH, PADDLE_HEIGHT))

def draw_ball(x, y):
    pygame.draw.rect(screen, WHITE, (x, y, BALL_SIZE, BALL_SIZE))

def draw_score(left_score, right_score):
    font = pygame.font.Font(None, 74)
    left_text = font.render(str(left_score), 1, WHITE)
    right_text = font.render(str(right_score), 1, WHITE)
    screen.blit(left_text, (SCREEN_WIDTH // 4, 10))
    screen.blit(right_text, (3 * SCREEN_WIDTH // 4, 10))

def draw_middle_line():
    pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 2, 0, 4, SCREEN_HEIGHT))

def game_over_screen(winner):
    font = pygame.font.Font(None, 55)
    if winner == "left":
        text = font.render("Left Player Wins! Press R to Restart", True, WHITE)
    elif winner == "right":
        text = font.render("Right Player Wins! Press R to Restart", True, WHITE)
    else:
        text = font.render("Press R to Restart", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))

def reset_game():
    return 0, 0, SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, 5 if random.randint(0, 1) == 0 else -5, 5 if random.randint(0, 1) == 0 else -5

left_score, right_score, ball_x, ball_y, ball_vel_x, ball_vel_y = reset_game()
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
                left_score, right_score, ball_x, ball_y, ball_vel_x, ball_vel_y = reset_game()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        left_paddle_y = max(0, left_paddle_y - 7)
    if keys[pygame.K_s]:
        left_paddle_y = min(SCREEN_HEIGHT - PADDLE_HEIGHT, left_paddle_y + 7)
    if keys[pygame.K_UP]:
        right_paddle_y = max(0, right_paddle_y - 7)
    if keys[pygame.K_DOWN]:
        right_paddle_y = min(SCREEN_HEIGHT - PADDLE_HEIGHT, right_paddle_y + 7)

    ball_x += ball_vel_x
    ball_y += ball_vel_y

    if ball_y <= 0 or ball_y >= SCREEN_HEIGHT - BALL_SIZE:
        ball_vel_y = -ball_vel_y

    if (ball_x <= PADDLE_WIDTH and left_paddle_y < ball_y < left_paddle_y + PADDLE_HEIGHT or
        ball_x >= SCREEN_WIDTH - PADDLE_WIDTH - BALL_SIZE and right_paddle_y < ball_y < right_paddle_y + PADDLE_HEIGHT):
        ball_vel_x = -ball_vel_x

    if ball_x <= -BALL_SIZE:
        right_score += 1
        left_score, right_score, ball_x, ball_y, ball_vel_x, ball_vel_y = reset_game()
    elif ball_x >= SCREEN_WIDTH:
        left_score += 1
        left_score, right_score, ball_x, ball_y, ball_vel_x, ball_vel_y = reset_game()

    if left_score >= WINNING_SCORE or right_score >= WINNING_SCORE:
        running = False

    screen.fill(BLACK)
    draw_paddle(PADDLE_WIDTH, left_paddle_y)
    draw_paddle(SCREEN_WIDTH - 2 * PADDLE_WIDTH, right_paddle_y)
    draw_ball(ball_x, ball_y)
    draw_score(left_score, right_score)
    draw_middle_line()

    if left_score >= WINNING_SCORE or right_score >= WINNING_SCORE:
        game_over_screen("left" if left_score >= WINNING_SCORE else "right")
    else:
        game_over_screen(None)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()