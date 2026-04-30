import pygame
import random
import sys

pygame.init()
random.seed(42)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
GRID_COLS = 30
GRID_ROWS = 24
GRID_SIZE = 20
GRID_WIDTH = GRID_COLS * GRID_SIZE
GRID_HEIGHT = GRID_ROWS * GRID_SIZE
SNAKE_INIT_LENGTH = 3
SNAKE_SPEED = 10

BACKGROUND_COLOR = (0, 0, 0)
GRID_COLOR = (50, 50, 50)
SNAKE_HEAD_COLOR = (0, 255, 0)
SNAKE_BODY_COLOR = (0, 200, 0)
FOOD_COLOR = (255, 0, 0)
TEXT_COLOR = (255, 255, 255)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snake Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

def draw_grid():
    for x in range(0, GRID_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x + GRID_OFFSET_X, GRID_OFFSET_Y), (x + GRID_OFFSET_X, GRID_OFFSET_Y + GRID_HEIGHT))
    for y in range(0, GRID_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (GRID_OFFSET_X, y + GRID_OFFSET_Y), (GRID_OFFSET_X + GRID_WIDTH, y + GRID_OFFSET_Y))

def draw_snake(snake):
    pygame.draw.rect(screen, SNAKE_HEAD_COLOR, (snake[0][0] * GRID_SIZE + GRID_OFFSET_X, snake[0][1] * GRID_SIZE + GRID_OFFSET_Y, GRID_SIZE, GRID_SIZE))
    for segment in snake[1:]:
        pygame.draw.rect(screen, SNAKE_BODY_COLOR, (segment[0] * GRID_SIZE + GRID_OFFSET_X, segment[1] * GRID_SIZE + GRID_OFFSET_Y, GRID_SIZE, GRID_SIZE))

def draw_food(food):
    pygame.draw.rect(screen, FOOD_COLOR, (food[0] * GRID_SIZE + GRID_OFFSET_X, food[1] * GRID_SIZE + GRID_OFFSET_Y, GRID_SIZE, GRID_SIZE))

def draw_text(text, x, y):
    screen.blit(font.render(text, True, TEXT_COLOR), (x, y))

def game_over_screen(score):
    screen.fill(BACKGROUND_COLOR)
    draw_text(f"Game Over", GRID_OFFSET_X + GRID_WIDTH // 2 - 60, GRID_OFFSET_Y // 2 - 20)
    draw_text(f"Score: {score}", GRID_OFFSET_X + GRID_WIDTH // 2 - 40, GRID_OFFSET_Y // 2 + 20)
    draw_text("Press R to Restart", GRID_OFFSET_X + GRID_WIDTH // 2 - 100, GRID_OFFSET_Y // 2 + 60)
    pygame.display.flip()

def generate_food(snake):
    while True:
        food = (random.randint(0, GRID_COLS - 1), random.randint(0, GRID_ROWS - 1))
        if food not in snake:
            return food

def check_collision(snake):
    head = snake[0]
    if (head[0] < 0 or head[0] >= GRID_COLS or head[1] < 0 or head[1] >= GRID_ROWS or head in snake[1:]):
        return True
    return False

def main():
    global GRID_OFFSET_X, GRID_OFFSET_Y
    GRID_OFFSET_X = (WINDOW_WIDTH - GRID_WIDTH) // 2
    GRID_OFFSET_Y = (WINDOW_HEIGHT - GRID_HEIGHT) // 2

    snake = [((GRID_COLS // 2), (GRID_ROWS // 2) + i) for i in range(SNAKE_INIT_LENGTH)]
    direction = (1, 0)
    food = generate_food(snake)
    score = 0

    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_grid()
        draw_snake(snake)
        draw_food(food)
        draw_text(f"Score: {score}", 10, 10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    main()
                if event.key == pygame.K_UP and direction!= (0, 1):
                    direction = (0, -1)
                if event.key == pygame.K_DOWN and direction!= (0, -1):
                    direction = (0, 1)
                if event.key == pygame.K_LEFT and direction!= (1, 0):
                    direction = (-1, 0)
                if event.key == pygame.K_RIGHT and direction!= (-1, 0):
                    direction = (1, 0)

        new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        snake.insert(0, new_head)

        if check_collision(snake):
            game_over_screen(score)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    main()
            pygame.time.wait(2000)
            running = False

        if snake[0] == food:
            score += 10
            food = generate_food(snake)
        else:
            snake.pop()

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()