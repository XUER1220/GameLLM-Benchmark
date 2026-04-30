import pygame
import random

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_COLUMNS = 30
GRID_ROWS = 24
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Snake Easy')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

def draw_grid():
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        for y in range(120, SCREEN_HEIGHT, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)

def draw_snake(snake):
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (segment[0], segment[1], GRID_SIZE, GRID_SIZE))

def draw_food(food):
    pygame.draw.rect(screen, RED, (food[0], food[1], GRID_SIZE, GRID_SIZE))

def draw_hud(score):
    text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(text, (10, 10))

def game_over(score):
    screen.fill(BLACK)
    text = font.render('Game Over', True, WHITE)
    score_text = font.render(f'Score: {score}', True, WHITE)
    restart_text = font.render('Press R to Restart', True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

def new_food(snake):
    while True:
        food = (random.randint(0, GRID_COLUMNS - 1) * GRID_SIZE, random.randint(0, GRID_ROWS - 1) * GRID_SIZE + 120)
        if food not in snake:
            return food

def main():
    running = True
    game_over_flag = False
    direction = (GRID_SIZE, 0)
    snake = [(GRID_COLUMNS // 2 * GRID_SIZE, GRID_ROWS // 2 * GRID_SIZE + 120),
             (GRID_COLUMNS // 2 * GRID_SIZE - GRID_SIZE, GRID_ROWS // 2 * GRID_SIZE + 120),
             (GRID_COLUMNS // 2 * GRID_SIZE - 2 * GRID_SIZE, GRID_ROWS // 2 * GRID_SIZE + 120)]
    food = new_food(snake)
    score = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over_flag:
                    snake = [(GRID_COLUMNS // 2 * GRID_SIZE, GRID_ROWS // 2 * GRID_SIZE + 120),
                             (GRID_COLUMNS // 2 * GRID_SIZE - GRID_SIZE, GRID_ROWS // 2 * GRID_SIZE + 120),
                             (GRID_COLUMNS // 2 * GRID_SIZE - 2 * GRID_SIZE, GRID_ROWS // 2 * GRID_SIZE + 120)]
                    food = new_food(snake)
                    score = 0
                    game_over_flag = False
                elif not game_over_flag:
                    if event.key == pygame.K_LEFT and direction!= (GRID_SIZE, 0):
                        direction = (-GRID_SIZE, 0)
                    elif event.key == pygame.K_RIGHT and direction!= (-GRID_SIZE, 0):
                        direction = (GRID_SIZE, 0)
                    elif event.key == pygame.K_UP and direction!= (0, GRID_SIZE):
                        direction = (0, -GRID_SIZE)
                    elif event.key == pygame.K_DOWN and direction!= (0, -GRID_SIZE):
                        direction = (0, GRID_SIZE)

        if not game_over_flag:
            new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
            snake.insert(0, new_head)

            if new_head == food:
                score += 10
                food = new_food(snake)
            else:
                snake.pop()

            if (new_head[0] < 0 or new_head[0] >= GRID_COLUMNS * GRID_SIZE or
                new_head[1] < 120 or new_head[1] >= GRID_ROWS * GRID_SIZE + 120 or
                new_head in snake[1:]):
                game_over_flag = True

        screen.fill(BLACK)
        draw_grid()
        if not game_over_flag:
            draw_snake(snake)
            draw_food(food)
            draw_hud(score)
        else:
            game_over(score)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == '__main__':
    main()