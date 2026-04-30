import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRID_SIZE = 20
COLUMNS = 30
ROWS = 24
SNAKE_SPEED = 10

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Easy")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 36)

def draw_grid():
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, WHITE, (x, GRID_SIZE), (x, SCREEN_HEIGHT - GRID_SIZE))
    for y in range(GRID_SIZE, SCREEN_HEIGHT - GRID_SIZE, GRID_SIZE):
        pygame.draw.line(screen, WHITE, (GRID_SIZE, y), (SCREEN_WIDTH - GRID_SIZE, y))

def draw_snake(snake):
    for segment in snake:
        pygame.draw.rect(screen, GREEN, pygame.Rect(segment[0], segment[1], GRID_SIZE, GRID_SIZE))

def draw_food(food):
    pygame.draw.rect(screen, RED, pygame.Rect(food[0], food[1], GRID_SIZE, GRID_SIZE))

def draw_hud(score):
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))

def generate_food(snake):
    while True:
        food = (random.randint(0, COLUMNS - 1) * GRID_SIZE, random.randint(0, ROWS - 1) * GRID_SIZE)
        if food not in snake:
            return food

def game_over(score):
    screen.fill(BLACK)
    screen.blit(font.render("Game Over", True, RED), (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
    screen.blit(font.render(f"Score: {score}", True, WHITE), (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2))
    screen.blit(font.render("Press R to Restart", True, YELLOW), (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50))
    pygame.display.update()

def main():
    snake = [(COLUMNS // 2 * GRID_SIZE, ROWS // 2 * GRID_SIZE),
            ((COLUMNS // 2 - 1) * GRID_SIZE, ROWS // 2 * GRID_SIZE),
            ((COLUMNS // 2 - 2) * GRID_SIZE, ROWS // 2 * GRID_SIZE)]
    direction = (1, 0)
    score = 0
    food = generate_food(snake)
    running = True
    game_restart = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game_restart = True
                elif event.key == pygame.K_UP and direction!= (0, 1):
                    direction = (0, -1)
                elif event.key == pygame.K_DOWN and direction!= (0, -1):
                    direction = (0, 1)
                elif event.key == pygame.K_LEFT and direction!= (1, 0):
                    direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction!= (-1, 0):
                    direction = (1, 0)

        if game_restart:
            snake = [(COLUMNS // 2 * GRID_SIZE, ROWS // 2 * GRID_SIZE),
                      ((COLUMNS // 2 - 1) * GRID_SIZE, ROWS // 2 * GRID_SIZE),
                      ((COLUMNS // 2 - 2) * GRID_SIZE, ROWS // 2 * GRID_SIZE)]
            direction = (1, 0)
            score = 0
            food = generate_food(snake)
            game_restart = False

        new_head = (snake[0][0] + direction[0] * GRID_SIZE, snake[0][1] + direction[1] * GRID_SIZE)
        snake.insert(0, new_head)

        if (new_head[0] < GRID_SIZE or new_head[0] >= SCREEN_WIDTH - GRID_SIZE or
            new_head[1] < GRID_SIZE or new_head[1] >= SCREEN_HEIGHT - GRID_SIZE or
            new_head in snake[1:]):
            game_over(score)
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            main()
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()

        if new_head == food:
            score += 10
            food = generate_food(snake)
        else:
            snake.pop()

        screen.fill(BLACK)
        draw_grid()
        draw_snake(snake)
        draw_food(food)
        draw_hud(score)
        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()