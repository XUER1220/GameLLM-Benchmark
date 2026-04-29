import pygame
import random

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_WIDTH, GRID_HEIGHT = 30, 24
CELL_SIZE = 20
GRID_START_X = (SCREEN_WIDTH - GRID_WIDTH * CELL_SIZE) // 2
GRID_START_Y = (SCREEN_HEIGHT - GRID_HEIGHT * CELL_SIZE) // 2
FPS = 60
SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
BACKGROUND_COLOR = (0, 0, 0)
GRID_COLOR = (50, 50, 50)
TEXT_COLOR = (255, 255, 255)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

def draw_grid():
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            rect = pygame.Rect(GRID_START_X + x * CELL_SIZE, GRID_START_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)

def draw_snake(snake):
    for segment in snake:
        pygame.draw.rect(screen, SNAKE_COLOR, (segment[0] * CELL_SIZE + GRID_START_X, segment[1] * CELL_SIZE + GRID_START_Y, CELL_SIZE, CELL_SIZE))

def draw_food(food):
    pygame.draw.rect(screen, FOOD_COLOR, (food[0] * CELL_SIZE + GRID_START_X, food[1] * CELL_SIZE + GRID_START_Y, CELL_SIZE, CELL_SIZE))

def draw_text(text, position):
    rendered_text = font.render(text, True, TEXT_COLOR)
    screen.blit(rendered_text, position)

def generate_food(snake):
    while True:
        food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if food not in snake:
            return food

def game_over(score):
    draw_text(f"Game Over - Score: {score}", (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 30))
    draw_text("Press R to Restart", (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 30))

def main():
    running = True
    game_started = False
    score = 0
    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2 + 1), (GRID_WIDTH // 2, GRID_HEIGHT // 2), (GRID_WIDTH // 2, GRID_HEIGHT // 2 - 1)]
    direction = (1, 0)
    food = generate_food(snake)

    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_grid()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2 + 1), (GRID_WIDTH // 2, GRID_HEIGHT // 2), (GRID_WIDTH // 2, GRID_HEIGHT // 2 - 1)]
                    direction = (1, 0)
                    score = 0
                    food = generate_food(snake)
                    game_started = True
                elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT) and game_started:
                    if (event.key == pygame.K_UP and direction!= (0, 1)) or \
                       (event.key == pygame.K_DOWN and direction!= (0, -1)) or \
                       (event.key == pygame.K_LEFT and direction!= (1, 0)) or \
                       (event.key == pygame.K_RIGHT and direction!= (-1, 0)):
                        if event.key == pygame.K_UP:
                            direction = (0, -1)
                        elif event.key == pygame.K_DOWN:
                            direction = (0, 1)
                        elif event.key == pygame.K_LEFT:
                            direction = (-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            direction = (1, 0)

        if game_started:
            new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

            if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
                new_head in snake):
                game_started = False
                game_over(score)
            else:
                snake.insert(0, new_head)

                if new_head == food:
                    score += 10
                    food = generate_food(snake)
                else:
                    snake.pop()

        draw_snake(snake)
        draw_food(food)
        draw_text(f"Score: {score}", (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()