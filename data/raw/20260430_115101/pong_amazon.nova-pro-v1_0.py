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
    screen.blit(left_text, (SCREEN_WIDTH//4, SCREEN_HEIGHT//3))
    screen.blit(right_text, (3*SCREEN_WIDTH//4, SCREEN_HEIGHT//3))

def draw_middle_line():
    pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH//2 - 2, 0, 4, SCREEN_HEIGHT))

def reset_ball():
    return SCREEN_WIDTH//2 - BALL_SIZE//2, SCREEN_HEIGHT//2 - BALL_SIZE//2, random.choice([-5, 5]), random.choice([-5, 5])

def game():
    left_paddle_y = SCREEN_HEIGHT//2 - PADDLE_HEIGHT//2
    right_paddle_y = SCREEN_HEIGHT//2 - PADDLE_HEIGHT//2
    ball_x, ball_y, ball_x_speed, ball_y_speed = reset_ball()
    left_score = 0
    right_score = 0

    running = True
    while running:
        screen.fill(BLACK)
        draw_paddle(0, left_paddle_y)
        draw_paddle(SCREEN_WIDTH - PADDLE_WIDTH, right_paddle_y)
        draw_ball(ball_x, ball_y)
        draw_middle_line()
        draw_score(left_score, right_score)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            left_paddle_y = max(0, left_paddle_y - 7)
        if keys[pygame.K_s]:
            left_paddle_y = min(SCREEN_HEIGHT - PADDLE_HEIGHT, left_paddle_y + 7)
        if keys[pygame.K_UP]:
            right_paddle_y = max(0, right_paddle_y - 7)
        if keys[pygame.K_DOWN]:
            right_paddle_y = min(SCREEN_HEIGHT - PADDLE_HEIGHT, right_paddle_y + 7)

        ball_x += ball_x_speed
        ball_y += ball_y_speed

        if ball_y <= 0 or ball_y >= SCREEN_HEIGHT - BALL_SIZE:
            ball_y_speed = -ball_y_speed

        if (ball_x <= PADDLE_WIDTH and left_paddle_y < ball_y < left_paddle_y + PADDLE_HEIGHT or
            ball_x >= SCREEN_WIDTH - 2*PADDLE_WIDTH and right_paddle_y < ball_y < right_paddle_y + PADDLE_HEIGHT):
            ball_x_speed = -ball_x_speed

        if ball_x <= 0:
            right_score += 1
            ball_x, ball_y, ball_x_speed, ball_y_speed = reset_ball()
        elif ball_x >= SCREEN_WIDTH - BALL_SIZE:
            left_score += 1
            ball_x, ball_y, ball_x_speed, ball_y_speed = reset_ball()

        if left_score == 7 or right_score == 7:
            running = False

        pygame.display.flip()
        clock.tick(FPS)

    if left_score == 7:
        draw_score(left_score, right_score)
        font = pygame.font.Font(None, 36)
        text = font.render("Left Player Wins! Press R to Restart", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//4, SCREEN_HEIGHT//2))
    elif right_score == 7:
        draw_score(left_score, right_score)
        font = pygame.font.Font(None, 36)
        text = font.render("Right Player Wins! Press R to Restart", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//4, SCREEN_HEIGHT//2))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
        pygame.display.flip()
        clock.tick(FPS)

game()