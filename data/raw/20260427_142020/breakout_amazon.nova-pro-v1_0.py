import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
PADDLE_WIDTH, PADDLE_HEIGHT = 110, 18
BALL_SIZE = 16
BRICK_ROWS, BRICK_COLS = 5, 8
BRICK_WIDTH, BRICK_HEIGHT = 84, 24
BRICK_GAP = 10
BALL_SPEED_X, BALL_SPEED_Y = 4, -5
PADDLE_SPEED = 8
LIVES = 3
SCORE_PER_BRICK = 10

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Breakout Medium")
clock = pygame.time.Clock()

def draw_text(text, size, color, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def reset_game():
    global paddle, ball, bricks, score, lives
    paddle = pygame.Rect(SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2, SCREEN_HEIGHT - PADDLE_HEIGHT - 10, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(paddle.centerx - BALL_SIZE // 2, paddle.top - BALL_SIZE, BALL_SIZE, BALL_SIZE)
    ball_dx, ball_dy = BALL_SPEED_X, BALL_SPEED_Y
    bricks = [[pygame.Rect(x * (BRICK_WIDTH + BRICK_GAP), y * (BRICK_HEIGHT + BRICK_GAP), BRICK_WIDTH, BRICK_HEIGHT) for x in range(BRICK_COLS)] for y in range(BRICK_ROWS)]
    score = 0
    lives = LIVES

reset_game()

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
                reset_game()
                game_over = False
    
    if not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle.left > 0:
            paddle.x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT] and paddle.right < SCREEN_WIDTH:
            paddle.x += PADDLE_SPEED
        
        ball.x += ball_dx
        ball.y += ball_dy
        
        if ball.left <= 0 or ball.right >= SCREEN_WIDTH:
            ball_dx = -ball_dx
        if ball.top <= 0:
            ball_dy = -ball_dy
        if ball.bottom >= SCREEN_HEIGHT:
            lives -= 1
            if lives > 0:
                ball.x, ball.y = paddle.centerx - BALL_SIZE // 2, paddle.top - BALL_SIZE
            else:
                game_over = True
        
        if ball.colliderect(paddle):
            ball_dy = -ball_dy
        
        for row in bricks:
            for brick in row:
                if ball.colliderect(brick):
                    ball_dy = -ball_dy
                    score += SCORE_PER_BRICK
                    row.remove(brick)
                    break
        
        if not any(bricks):
            game_over = True
    
    pygame.draw.rect(screen, WHITE, paddle)
    pygame.draw.ellipse(screen, WHITE, ball)
    
    for row in bricks:
        for brick in row:
            pygame.draw.rect(screen, GREEN, brick)
    
    draw_text(f"Score: {score}", 36, WHITE, 10, 10)
    draw_text(f"Lives: {lives}", 36, WHITE, SCREEN_WIDTH - 150, 10)
    
    if game_over:
        if lives > 0:
            draw_text("You Win!", 72, RED, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50)
        else:
            draw_text("Game Over!", 72, RED, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50)
        draw_text("Press R to Restart", 36, RED, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 20)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()