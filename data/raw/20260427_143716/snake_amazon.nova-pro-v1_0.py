import pygame
import random

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_WIDTH, GRID_HEIGHT = 30, 24
CELL_SIZE = 20
GRID_AREA_WIDTH, GRID_AREA_HEIGHT = GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE
FPS = 60
SNAKE_SPEED = 10

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Easy")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 36)

def draw_grid():
    for x in range(0, GRID_AREA_WIDTH, CELL_SIZE):
        for y in range(0, GRID_AREA_HEIGHT, CELL_SIZE):
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, WHITE, rect, 1)

def draw_snake(snake):
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))

def draw_food(food):
    pygame.draw.rect(screen, RED, (food[0], food[1], CELL_SIZE, CELL_SIZE))

def draw_hud(score):
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))

def generate_food(snake):
    while True:
        food = (random.randint(0, GRID_WIDTH - 1) * CELL_SIZE, random.randint(0, GRID_HEIGHT - 1) * CELL_SIZE)
        if food not in snake:
            return food

def game_over(score):
    screen.fill(BLACK)
    text = font.render("Game Over", True, RED)
    score_text = font.render(f"Score: {score}", True, WHITE)
    restart_text = font.render("Press R to Restart", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    pygame.display.update()

def main():
    running = True
    game_over_flag = False
    score = 0

    snake = [(GRID_WIDTH // 2 * CELL_SIZE, GRID_HEIGHT // 2 * CELL_SIZE),
            ((GRID_WIDTH // 2 - 1) * CELL_SIZE, GRID_HEIGHT // 2 * CELL_SIZE),
            ((GRID_WIDTH // 2 - 2) * CELL_SIZE, GRID_HEIGHT // 2 * CELL_SIZE)]
    direction = (1, 0)
    food = generate_food(snake)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over_flag:
                    snake = [(GRID_WIDTH // 2 * CELL_SIZE, GRID_HEIGHT // 2 * CELL_SIZE),
                             ((GRID_WIDTH // 2 - 1) * CELL_SIZE, GRID_HEIGHT // 2 * CELL_SIZE),
                             ((GRID_WIDTH // 2 - 2) * CELL_SIZE, GRID_HEIGHT // 2 * CELL_SIZE)]
                    direction = (1, 0)
                    food = generate_food(snake)
                    score = 0
                    game_over_flag = False
                elif not game_over_flag:
                    if event.key == pygame.K_UP and direction!= (0, 1):
                        direction = (0, -1)
                    elif event.key == pygame.K_DOWN and direction!= (0, -1):
                        direction = (0, 1)
                    elif event.key == pygame.K_LEFT and direction!= (1, 0):
                        direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and direction!= (-1, 0):
                        direction = (1, 0)

        if not game_over_flag:
            new_head = (snake[0][0] + direction[0] * CELL_SIZE, snake[0][1] + direction[1] * CELL_SIZE)
            snake.insert(0, new_head)

            if new_head == food:
                score += 10
                food = generate_food(snake)
            else:
                snake.pop()

            if (new_head[0] < 0 or new_head[0] >= GRID_AREA_WIDTH or
                new_head[1] < 0 or new_head[1] >= GRID_AREA_HEIGHT or
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

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()