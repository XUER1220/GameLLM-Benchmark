import pygame
import random

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong Easy")
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 55)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
PADDLE_SPEED = 7
BALL_SIZE = 18
BALL_SPEED_X = 5
BALL_SPEED_Y = 5
WINNING_SCORE = 7

def draw_objects(left_paddle, right_paddle, ball, left_score, right_score):
    SCREEN.fill(BLACK)
    pygame.draw.rect(SCREEN, WHITE, left_paddle)
    pygame.draw.rect(SCREEN, WHITE, right_paddle)
    pygame.draw.ellipse(SCREEN, WHITE, ball)
    pygame.draw.aaline(SCREEN, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))
    left_score_text = FONT.render(str(left_score), True, WHITE)
    right_score_text = FONT.render(str(right_score), True, WHITE)
    SCREEN.blit(left_score_text, (SCREEN_WIDTH // 4 - 30, 20))
    SCREEN.blit(right_score_text, (3 * SCREEN_WIDTH // 4 - 30, 20))

def move_paddles(left_paddle, right_paddle, keys):
    if keys[pygame.K_w] and left_paddle.top > 0:
        left_paddle.move_ip(0, -PADDLE_SPEED)
    if keys[pygame.K_s] and left_paddle.bottom < SCREEN_HEIGHT:
        left_paddle.move_ip(0, PADDLE_SPEED)
    if keys[pygame.K_UP] and right_paddle.top > 0:
        right_paddle.move_ip(0, -PADDLE_SPEED)
    if keys[pygame.K_DOWN] and right_paddle.bottom < SCREEN_HEIGHT:
        right_paddle.move_ip(0, PADDLE_SPEED)

def move_ball(ball, direction_x, direction_y):
    ball.move_ip(direction_x * BALL_SPEED_X, direction_y * BALL_SPEED_Y)
    if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
        return 1
    return 0

def check_collision(left_paddle, right_paddle, ball, direction_x):
    if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
        return -direction_x
    return direction_x

def game():
    left_paddle = pygame.Rect(50, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = pygame.Rect(SCREEN_WIDTH - 50 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
    left_score = 0
    right_score = 0
    direction_x = random.choice([-1, 1])
    direction_y = random.choice([-1, 1])
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False
        if keys[pygame.K_r]:
            return
        move_paddles(left_paddle, right_paddle, keys)
        direction_y = move_ball(ball, direction_x, direction_y)
        direction_x = check_collision(left_paddle, right_paddle, ball, direction_x)
        if ball.left <= 0:
            right_score += 1
            ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            direction_x = 1
        elif ball.right >= SCREEN_WIDTH:
            left_score += 1
            ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            direction_x = -1
        if left_score == WINNING_SCORE or right_score == WINNING_SCORE:
            draw_objects(left_paddle, right_paddle, ball, left_score, right_score)
            winner_text = FONT.render("Left Wins!" if left_score == WINNING_SCORE else "Right Wins!", True, WHITE)
            SCREEN.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            restart_text = FONT.render("Press R to Restart", True, WHITE)
            SCREEN.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            pygame.display.flip()
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        return
        draw_objects(left_paddle, right_paddle, ball, left_score, right_score)
        pygame.display.flip()
        CLOCK.tick(60)

while True:
    game()
pygame.quit()