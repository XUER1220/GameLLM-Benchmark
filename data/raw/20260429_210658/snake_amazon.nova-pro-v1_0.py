import pygame
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_WIDTH = 30
GRID_HEIGHT = 24
GRID_SIZE = 20
FPS = 60

BACKGROUND_COLOR = (255, 255, 255)
GRID_COLOR = (200, 200, 200)
SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
TEXT_COLOR = (0, 0, 0)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Snake Easy')
clock = pygame.time.Clock()
random.seed(42)

def draw_grid():
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, GRID_SIZE * 2), (x, SCREEN_HEIGHT - GRID_SIZE * 2))
    for y in range(GRID_SIZE * 2, SCREEN_HEIGHT - GRID_SIZE * 2, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (GRID_SIZE, y), (SCREEN_WIDTH - GRID_SIZE, y))

def draw_snake(snake):
    for segment in snake:
        pygame.draw.rect(screen, SNAKE_COLOR, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_food(food):
    pygame.draw.rect(screen, FOOD_COLOR, (food[0] * GRID_SIZE, food[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_hud(score):
    font = pygame.font.SysFont(None, 30)
    text = font.render(f'Score: {score}', True, TEXT_COLOR)
    screen.blit(text, (10, 10))

def draw_game_over(score):
    font = pygame.font.SysFont(None, 50)
    text = font.render('Game Over', True, TEXT_COLOR)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    text = font.render(f'Score: {score}', True, TEXT_COLOR)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
    text = font.render('Press R to Restart', True, TEXT_COLOR)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

def generate_food(snake):
    while True:
        food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if food not in snake:
            return food

def main():
    running = True
    game_over = False
    direction = (1, 0)
    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2 + i) for i in range(3)]
    food = generate_food(snake)
    score = 0

    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_grid()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    main()
                    return
                elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    new_direction = (0, -1) if event.key == pygame.K_UP else (0, 1) if event.key == pygame.K_DOWN else (-1, 0) if event.key == pygame.K_LEFT else (1, 0)
                    if (new_direction[0], new_direction[1])!= (-direction[0], -direction[1]):
                        direction = new_direction

        if not game_over:
            new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

            if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or new_head in snake):
                game_over = True
            else:
                snake.insert(0, new_head)
                if new_head == food:
                    score += 10
                    food = generate_food(snake)
                else:
                    snake.pop()

        draw_snake(snake)
        draw_food(food)
        draw_hud(score)
        if game_over:
            draw_game_over(score)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == '__main__':
    main()