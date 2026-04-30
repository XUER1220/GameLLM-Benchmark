import pygame
import random

pygame.init()
random.seed(42)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
GRID_WIDTH = 30
GRID_HEIGHT = 24
GRID_SIZE = 20
BG_COLOR = (0, 0, 0)
GRID_COLOR = (50, 50, 50)
SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
FONT_COLOR = (255, 255, 255)
FONT_SIZE = 24

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snake Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, FONT_SIZE)

def draw_grid():
    for x in range(0, WINDOW_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, GRID_SIZE), (x, WINDOW_HEIGHT - GRID_SIZE))
    for y in range(GRID_SIZE, WINDOW_HEIGHT - GRID_SIZE, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (GRID_SIZE, y), (WINDOW_WIDTH - GRID_SIZE, y))

def draw_snake(snake):
    for segment in snake:
        pygame.draw.rect(screen, SNAKE_COLOR, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_food(food):
    pygame.draw.rect(screen, FOOD_COLOR, (food[0] * GRID_SIZE, food[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_hud(score):
    text = font.render(f"Score: {score}", True, FONT_COLOR)
    screen.blit(text, (10, 10))

def game_over(score):
    screen.fill(BG_COLOR)
    draw_grid()
    draw_hud(score)
    text = font.render("Game Over", True, FONT_COLOR)
    screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, WINDOW_HEIGHT // 2 - text.get_height() // 2))
    text = font.render(f"Score: {score}", True, FONT_COLOR)
    screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, WINDOW_HEIGHT // 2))
    text = font.render("Press R to Restart", True, FONT_COLOR)
    screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, WINDOW_HEIGHT // 2 + text.get_height()))
    pygame.display.update()

def generate_food(snake):
    while True:
        food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if food not in snake:
            return food

def main():
    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2 + i) for i in range(3)]
    direction = (1, 0)
    food = generate_food(snake)
    score = 0
    running = True
    game_over_flag = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over_flag:
                    main()
                    return
                elif event.key == pygame.K_UP and direction!= (0, 1):
                    direction = (0, -1)
                elif event.key == pygame.K_DOWN and direction!= (0, -1):
                    direction = (0, 1)
                elif event.key == pygame.K_LEFT and direction!= (1, 0):
                    direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction!= (-1, 0):
                    direction = (1, 0)

        if not game_over_flag:
            new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

            if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
                new_head in snake):
                game_over_flag = True
                game_over(score)
            else:
                snake.insert(0, new_head)

                if new_head == food:
                    score += 10
                    food = generate_food(snake)
                else:
                    snake.pop()

        screen.fill(BG_COLOR)
        draw_grid()
        draw_snake(snake)
        draw_food(food)
        draw_hud(score)
        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()