import pygame
import random

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
PADDLE_WIDTH, PADDLE_HEIGHT = 18, 100
BALL_SIZE = 18
WINNING_SCORE = 7

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong Easy")
clock = pygame.time.Clock()

def draw_paddle(paddle):
    pygame.draw.rect(screen, WHITE, paddle)

def draw_ball(ball):
    pygame.draw.rect(screen, WHITE, ball)

def draw_score(left_score, right_score):
    font = pygame.font.Font(None, 74)
    left_text = font.render(str(left_score), True, WHITE)
    right_text = font.render(str(right_score), True, WHITE)
    screen.blit(left_text, (300, 10))
    screen.blit(right_text, (470, 10))

def reset_ball():
    ball.x = SCREEN_WIDTH // 2 - BALL_SIZE // 2
    ball.y = SCREEN_HEIGHT // 2 - BALL_SIZE // 2
    ball_dx = 5 if random.randint(0, 1) == 0 else -5
    ball_dy = random.randint(-5, 5)
    return ball_dx, ball_dy

def check_collision(paddle, ball, dx):
    if ball.colliderect(paddle):
        return -dx
    return dx

def game_over(left_score, right_score):
    font = pygame.font.Font(None, 54)
    if left_score >= WINNING_SCORE:
        text = font.render("Left Wins! Press R to Restart", True, WHITE)
    elif right_score >= WINNING_SCORE:
        text = font.render("Right Wins! Press R to Restart", True, WHITE)
    else:
        return False, text
    return True, text

left_paddle = pygame.Rect(50, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
right_paddle = pygame.Rect(SCREEN_WIDTH - 50 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
ball_dx, ball_dy = reset_ball()
left_score = right_score = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                left_score = right_score = 0
                ball_dx, ball_dy = reset_ball()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        left_paddle.y -= 7
    if keys[pygame.K_s]:
        left_paddle.y += 7
    if keys[pygame.K_UP]:
        right_paddle.y -= 7
    if keys[pygame.K_DOWN]:
        right_paddle.y += 7

    left_paddle.y = max(0, min(left_paddle.y, SCREEN_HEIGHT - PADDLE_HEIGHT))
    right_paddle.y = max(0, min(right_paddle.y, SCREEN_HEIGHT - PADDLE_HEIGHT))

    ball.x += ball_dx
    ball.y += ball_dy

    if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
        ball_dy = -ball_dy
    ball_dx = check_collision(left_paddle, ball, ball_dx)
    ball_dx = check_collision(right_paddle, ball, ball_dx)

    if ball.left <= 0:
        right_score += 1
        ball_dx, ball_dy = reset_ball()
    elif ball.right >= SCREEN_WIDTH:
        left_score += 1
        ball_dx, ball_dy = reset_ball()

    screen.fill(BLACK)
    pygame.draw.line(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)
    draw_paddle(left_paddle)
    draw_paddle(right_paddle)
    draw_ball(ball)
    draw_score(left_score, right_score)

    if game_over_flag, text := game_over(left_score, right_score):
        screen.blit(text, (100, SCREEN_HEIGHT // 2))
        if game_over_flag:
            pygame.display.update()
            pygame.time.delay(2000)
            continue

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()