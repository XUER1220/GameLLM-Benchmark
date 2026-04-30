import pygame
import random

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_WIDTH, GRID_HEIGHT = 30, 24
CELL_SIZE = 20
GRID_AREA_WIDTH, GRID_AREA_HEIGHT = GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE
GRID_X, GRID_Y = (SCREEN_WIDTH - GRID_AREA_WIDTH) // 2, (SCREEN_HEIGHT - GRID_AREA_HEIGHT) // 2
FPS = 60
SNAKE_SPEED = 10

BACKGROUND_COLOR = (255, 255, 255)
GRID_COLOR = (200, 200, 200)
SNAKE_HEAD_COLOR = (0, 255, 0)
SNAKE_BODY_COLOR = (0, 200, 0)
FOOD_COLOR = (255, 0, 0)
TEXT_COLOR = (0, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

def draw_grid():
    for x in range(GRID_X, GRID_X + GRID_AREA_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, GRID_Y), (x, GRID_Y + GRID_AREA_HEIGHT))
    for y in range(GRID_Y, GRID_Y + GRID_AREA_HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (GRID_X, y), (GRID_X + GRID_AREA_WIDTH, y))

def draw_snake(snake):
    for segment in snake:
        pygame.draw.rect(screen, SNAKE_BODY_COLOR if segment!= snake[0] else SNAKE_HEAD_COLOR, (segment[0] * CELL_SIZE + GRID_X, segment[1] * CELL_SIZE + GRID_Y, CELL_SIZE, CELL_SIZE))

def draw_food(food):
    pygame.draw.rect(screen, FOOD_COLOR, (food[0] * CELL_SIZE + GRID_X, food[1] * CELL_SIZE + GRID_Y, CELL_SIZE, CELL_SIZE))

def draw_text(text, position):
    rendered_text = font.render(text, True, TEXT_COLOR)
    screen.blit(rendered_text, position)

def generate_food(snake):
    while True:
        food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if food not in snake:
            return food

def game_over(score):
    draw_text(f"Game Over - Score: {score}", (GRID_X, GRID_Y - 50))
    draw_text("Press R to Restart", (GRID_X, GRID_Y - 20))

def main():
    running = True
    game_started = False
    score = 0

    while running:
        if not game_started:
            snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2 + i) for i in range(3)]
            direction = (1, 0)
            food = generate_food(snake)
            score = 0
            game_started = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game_started = False
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                    dx, dy = direction
                    new_direction = (
                        (-dx, 0) if event.key == pygame.K_LEFT else
                        (dx, 0) if event.key == pygame.K_RIGHT else
                        (0, -dy) if event.key == pygame.K_UP else
                        (0, dy) if event.key == pygame.K_DOWN else
                        (0, 0)
                    )
                    if (new_direction[0], new_direction[1])!= (-dx, -dy):
                        direction = new_direction

        if game_started:
            x, y = snake[0]
            dx, dy = direction
            new_head = ((x + dx) % GRID_WIDTH, (y + dy) % GRID_HEIGHT)

            if new_head in snake[1:]:
                game_started = False
                game_over(score)
            else:
                snake.insert(0, new_head)
                if new_head == food:
                    score += 10
                    food = generate_food(snake)
                else:
                    snake.pop()

        screen.fill(BACKGROUND_COLOR)
        draw_grid()
        if game_started:
            draw_snake(snake)
            draw_food(food)
            draw_text(f"Score: {score}", (GRID_X, GRID_Y - 30))
        else:
            game_over(score)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()