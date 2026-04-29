import pygame
import sys
import random

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

BALL_SIZE = 16
PADDLE_WIDTH = 110
PADDLE_HEIGHT = 18
BRICK_ROWS = 5
BRICK_COLS = 8
BRICK_WIDTH = 84
BRICK_HEIGHT = 24
BRICK_PADDING_X = 10
BRICK_PADDING_Y = 10
BALL_INIT_SPEED_X = 4
BALL_INIT_SPEED_Y = -5
PADDLE_SPEED = 8
BALL_RESET_Y = SCREEN_HEIGHT - PADDLE_HEIGHT - 20
LIVES = 3
SCORE_PER_BRICK = 10

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Breakout Medium")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def reset_game():
    global paddle, ball, ball_speed_x, ball_speed_y, bricks, score, lives
    paddle = pygame.Rect(SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2, SCREEN_HEIGHT - PADDLE_HEIGHT - 10, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(paddle.centerx - BALL_SIZE // 2, paddle.top - BALL_SIZE, BALL_SIZE, BALL_SIZE)
    ball_speed_x = BALL_INIT_SPEED_X
    ball_speed_y = BALL_INIT_SPEED_Y
    bricks = [pygame.Rect(BRICK_PADDING_X + (BRICK_WIDTH + BRICK_PADDING_X) * (i % BRICK_COLS), BRICK_PADDING_Y + (BRICK_HEIGHT + BRICK_PADDING_Y) * (i // BRICK_COLS), BRICK_WIDTH, BRICK_HEIGHT) for i in range(BRICK_ROWS * BRICK_COLS)]
    score = 0
    lives = LIVES

def check_collisions():
    global ball_speed_x, ball_speed_y, score, lives
    if ball.colliderect(paddle):
        ball_speed_y = -BALL_INIT_SPEED_Y
    for brick in bricks[:]:
        if ball.colliderect(brick):
            ball_speed_y = -ball_speed_y
            bricks.remove(brick)
            score += SCORE_PER_BRICK
            break

def update_ball():
    global ball_speed_x, ball_speed_y, lives
    ball.x += ball_speed_x
    ball.y += ball_speed_y
    if ball.left <= 0 or ball.right >= SCREEN_WIDTH:
        ball_speed_x = -ball_speed_x
    if ball.top <= 0:
        ball_speed_y = -ball_speed_y
    if ball.bottom >= SCREEN_HEIGHT:
        lives -= 1
        if lives > 0:
            reset_ball()
        else:
            game_over()

def reset_ball():
    global ball_speed_x, ball_speed_y
    ball.centerx = paddle.centerx
    ball.bottom = paddle.top
    ball_speed_x = BALL_INIT_SPEED_X
    ball_speed_y = BALL_INIT_SPEED_Y

def game_over():
    global running
    screen.fill(BLACK)
    draw_text("Game Over! Press R to Restart", font, WHITE, screen, 200, SCREEN_HEIGHT // 2 - 50)
    draw_text(f"Final Score: {score}", font, WHITE, screen, 300, SCREEN_HEIGHT // 2)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_game()
                return

def game_win():
    global running
    screen.fill(BLACK)
    draw_text("You Win! Press R to Restart", font, WHITE, screen, 200, SCREEN_HEIGHT // 2 - 50)
    draw_text(f"Final Score: {score}", font, WHITE, screen, 300, SCREEN_HEIGHT // 2)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_game()
                return

reset_game()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.x -= PADDLE_SPEED
    if keys[pygame.K_RIGHT] and paddle.right < SCREEN_WIDTH:
        paddle.x += PADDLE_SPEED

    update_ball()
    check_collisions()

    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, paddle)
    pygame.draw.ellipse(screen, RED, ball)
    for brick in bricks:
        pygame.draw.rect(screen, GREEN, brick)
    draw_text(f"Score: {score}", font, WHITE, screen, 10, 10)
    draw_text(f"Lives: {lives}", font, WHITE, screen, 10, 50)

    if not bricks:
        game_win()
    if lives <= 0:
        game_over()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()