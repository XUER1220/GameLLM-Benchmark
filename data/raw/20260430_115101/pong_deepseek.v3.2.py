import pygame
import random
import sys

random.seed(42)

WIDTH = 800
HEIGHT = 600
FPS = 60

BACKGROUND_COLOR = (10, 10, 30)
PADDLE_COLOR = (220, 220, 220)
BALL_COLOR = (255, 105, 97)
LINE_COLOR = (40, 40, 70)
TEXT_COLOR = (200, 200, 220)
HIGHLIGHT_COLOR = (255, 255, 255)

PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
BALL_SIZE = 18
PADDLE_SPEED = 7
BALL_SPEED_X = 5
BALL_SPEED_Y = 5
WIN_SCORE = 7

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 32)

left_paddle = pygame.Rect(30, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
right_paddle = pygame.Rect(WIDTH - 30 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)

ball_speed_x = BALL_SPEED_X if random.choice([True, False]) else -BALL_SPEED_X
ball_speed_y = BALL_SPEED_Y
left_score = 0
right_score = 0
game_active = True
winner = None

def reset_ball():
    global ball_speed_x, ball_speed_y
    ball.center = (WIDTH//2, HEIGHT//2)
    ball_speed_x = BALL_SPEED_X if random.choice([True, False]) else -BALL_SPEED_X
    ball_speed_y = BALL_SPEED_Y

def restart_game():
    global left_score, right_score, game_active, winner
    left_score = 0
    right_score = 0
    game_active = True
    winner = None
    reset_ball()
    left_paddle.centery = HEIGHT//2
    right_paddle.centery = HEIGHT//2

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_r:
                restart_game()

    keys = pygame.key.get_pressed()
    if game_active:
        if keys[pygame.K_w] and left_paddle.top > 0:
            left_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
            left_paddle.y += PADDLE_SPEED
        if keys[pygame.K_UP] and right_paddle.top > 0:
            right_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_DOWN] and right_paddle.bottom < HEIGHT:
            right_paddle.y += PADDLE_SPEED

        ball.x += ball_speed_x
        ball.y += ball_speed_y

        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_speed_y = -ball_speed_y

        if ball.colliderect(left_paddle) and ball_speed_x < 0:
            ball_speed_x = abs(ball_speed_x)
            offset = (ball.centery - left_paddle.centery) / (PADDLE_HEIGHT//2)
            ball_speed_y = offset * 5
        if ball.colliderect(right_paddle) and ball_speed_x > 0:
            ball_speed_x = -abs(ball_speed_x)
            offset = (ball.centery - right_paddle.centery) / (PADDLE_HEIGHT//2)
            ball_speed_y = offset * 5

        if ball.left <= 0:
            right_score += 1
            if right_score >= WIN_SCORE:
                game_active = False
                winner = "Right"
            else:
                reset_ball()
        if ball.right >= WIDTH:
            left_score += 1
            if left_score >= WIN_SCORE:
                game_active = False
                winner = "Left"
            else:
                reset_ball()

    screen.fill(BACKGROUND_COLOR)
    pygame.draw.rect(screen, PADDLE_COLOR, left_paddle)
    pygame.draw.rect(screen, PADDLE_COLOR, right_paddle)
    pygame.draw.rect(screen, BALL_COLOR, ball)
    pygame.draw.line(screen, LINE_COLOR, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)

    left_text = font.render(str(left_score), True, TEXT_COLOR)
    right_text = font.render(str(right_score), True, TEXT_COLOR)
    screen.blit(left_text, (WIDTH//4 - left_text.get_width()//2, 20))
    screen.blit(right_text, (3*WIDTH//4 - right_text.get_width()//2, 20))

    if not game_active and winner:
        win_text = font.render(f"{winner} Player Wins!", True, HIGHLIGHT_COLOR)
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 50))
        restart_text = small_font.render("Press R to Restart", True, TEXT_COLOR)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))

    pygame.display.flip()
    clock.tick(FPS)