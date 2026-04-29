import pygame
import sys
import random
import time

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
MAZE_WIDTH = 21
MAZE_HEIGHT = 15
CELL_SIZE = 32
MAZE_OFFSET_X = (SCREEN_WIDTH - MAZE_WIDTH * CELL_SIZE) // 2
MAZE_OFFSET_Y = (SCREEN_HEIGHT - MAZE_HEIGHT * CELL_SIZE) // 2

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze Runner Easy")
clock = pygame.time.Clock()

def generate_maze():
    maze = [[1] * MAZE_WIDTH for _ in range(MAZE_HEIGHT)]
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    def is_valid(x, y):
        return 0 < x < MAZE_WIDTH - 1 and 0 < y < MAZE_HEIGHT - 1
    
    def carve_path(x, y):
        maze[y][x] = 0
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2
            if is_valid(nx, ny) and maze[ny][nx] == 1:
                maze[y + dy][x + dx] = 0
                carve_path(nx, ny)
    
    carve_path(1, 1)
    maze[0][1] = 0
    maze[MAZE_HEIGHT - 1][MAZE_WIDTH - 2] = 0
    return maze

def draw_maze(maze):
    for y in range(MAZE_HEIGHT):
        for x in range(MAZE_WIDTH):
            if maze[y][x] == 1:
                pygame.draw.rect(screen, BLACK, (MAZE_OFFSET_X + x * CELL_SIZE, MAZE_OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            else:
                pygame.draw.rect(screen, WHITE, (MAZE_OFFSET_X + x * CELL_SIZE, MAZE_OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_player(player_pos):
    pygame.draw.rect(screen, GREEN, (MAZE_OFFSET_X + player_pos[0] * CELL_SIZE, MAZE_OFFSET_Y + player_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_exit(exit_pos):
    pygame.draw.rect(screen, RED, (MAZE_OFFSET_X + exit_pos[0] * CELL_SIZE, MAZE_OFFSET_Y + exit_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_hud(start_time, game_over):
    if game_over:
        font = pygame.font.Font(None, 74)
        text = font.render("You Win", True, YELLOW)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2 - 50))
        elapsed_time = int(time.time() - start_time)
        text = font.render(f"Time: {elapsed_time}s", True, YELLOW)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
        text = font.render("Press R to Restart", True, YELLOW)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2 + 50))
    else:
        font = pygame.font.Font(None, 36)
        elapsed_time = int(time.time() - start_time)
        text = font.render(f"Time: {elapsed_time}s", True, YELLOW)
        screen.blit(text, (10, 10))

def game_loop():
    maze = generate_maze()
    player_pos = [1, 0]
    exit_pos = [MAZE_WIDTH - 2, MAZE_HEIGHT - 1]
    start_time = time.time()
    game_over = False

    while True:
        screen.fill(BLUE)
        draw_maze(maze)
        draw_player(player_pos)
        draw_exit(exit_pos)
        draw_hud(start_time, game_over)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r and game_over:
                    return game_loop()
                if not game_over:
                    if event.key == pygame.K_UP and maze[player_pos[1] - 1][player_pos[0]] == 0:
                        player_pos[1] -= 1
                    if event.key == pygame.K_DOWN and maze[player_pos[1] + 1][player_pos[0]] == 0:
                        player_pos[1] += 1
                    if event.key == pygame.K_LEFT and maze[player_pos[1]][player_pos[0] - 1] == 0:
                        player_pos[0] -= 1
                    if event.key == pygame.K_RIGHT and maze[player_pos[1]][player_pos[0] + 1] == 0:
                        player_pos[0] += 1
        
        if player_pos == exit_pos:
            game_over = True
        
        pygame.display.flip()
        clock.tick(FPS)

game_loop()