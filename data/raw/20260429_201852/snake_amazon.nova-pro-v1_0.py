import pygame
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
COLS = 30
ROWS = 24
FPS = 60
SNAKE_SPEED = 10

BG_COLOR = (255, 255, 255)
GRID_COLOR = (200, 200, 200)
SNAKE_HEAD_COLOR = (0, 255, 0)
SNAKE_BODY_COLOR = (0, 200, 0)
FOOD_COLOR = (255, 0, 0)
TEXT_COLOR = (0, 0, 0)

pygame.init()
random.seed(42)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

def draw_grid():
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, GRID_SIZE), (x, SCREEN_HEIGHT - GRID_SIZE))
    for y in range(GRID_SIZE, SCREEN_HEIGHT - GRID_SIZE, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (GRID_SIZE, y), (SCREEN_WIDTH - GRID_SIZE, y))

def draw_snake(snake):
    for i, segment in enumerate(snake):
        color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_BODY_COLOR
        pygame.draw.rect(screen, color, (segment[0] * GRID_SIZE + GRID_SIZE, segment[1] * GRID_SIZE + GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_food(food):
    pygame.draw.rect(screen, FOOD_COLOR, (food[0] * GRID_SIZE + GRID_SIZE, food[1] * GRID_SIZE + GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_hud(score):
    text = font.render(f"Score: {score}", True, TEXT_COLOR)
    screen.blit(text, (10, 10))

def draw_game_over(score):
    text1 = font.render("Game Over", True, TEXT_COLOR)
    text2 = font.render(f"Score: {score}", True, TEXT_COLOR)
    text3 = font.render("Press R to Restart", True, TEXT_COLOR)
    screen.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2, SCREEN_HEIGHT // 2 - text1.get_height() // 2))
    screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(text3, (SCREEN_WIDTH // 2 - text3.get_width() // 2, SCREEN_HEIGHT // 2 + text3.get_height()))

def generate_food(snake):
    while True:
        food = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if food not in snake:
            return food

def main():
    running = True
    game_over = False
    direction = (1, 0)
    snake = [(COLS // 2, ROWS // 2 + i) for i in range(3)]
    food = generate_food(snake)
    score = 0

    while running:
        screen.fill(BG_COLOR)
        draw_grid()
        draw_snake(snake)
        draw_food(food)
        draw_hud(score)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    game_over = False
                    direction = (1, 0)
                    snake = [(COLS // 2, ROWS // 2 + i) for i in range(3)]
                    food = generate_food(snake)
                    score = 0
                elif not game_over:
                    if event.key == pygame.K_LEFT and direction!= (1, 0):
                        direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and direction!= (-1, 0):
                        direction = (1, 0)
                    elif event.key == pygame.K_UP and direction!= (0, 1):
                        direction = (0, -1)
                    elif event.key == pygame.K_DOWN and direction!= (0, -1):
                        direction = (0, 1)

        if not game_over:
            new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
            if (new_head[0] < 0 or new_head[0] >= COLS or new_head[1] < 0 or new_head[1] >= ROWS or new_head in snake):
                game_over = True
            else:
                snake.insert(0, new_head)
                if new_head == food:
                    score += 10
                    food = generate_food(snake)
                else:
                    snake.pop()

        if game_over:
            draw_game_over(score)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()