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
TILE_SIZE = 32
MAZE_DISPLAY_WIDTH = MAZE_WIDTH * TILE_SIZE
MAZE_DISPLAY_HEIGHT = MAZE_HEIGHT * TILE_SIZE
PLAYER_COLOR = (0, 255, 0)
WALL_COLOR = (0, 0, 0)
PATH_COLOR = (255, 255, 255)
EXIT_COLOR = (255, 215, 0)
HUD_COLOR = (255, 255, 255)
FONT_SIZE = 36

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze Runner Easy")
clock = pygame.time.Clock()
font = pygame.font.Font(None, FONT_SIZE)

def generate_maze():
    maze = [[1 for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)]
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    def is_valid(x, y):
        return 0 <= x < MAZE_HEIGHT and 0 <= y < MAZE_WIDTH
    
    def carve_path(x, y):
        maze[x][y] = 0
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2
            if is_valid(nx, ny) and maze[nx][ny] == 1:
                maze[x + dx][y + dy] = 0
                carve_path(nx, ny)
    
    carve_path(1, 1)
    maze[1][0] = 0
    maze[MAZE_HEIGHT - 2][MAZE_WIDTH - 1] = 0
    return maze

def draw_maze(maze):
    for y in range(MAZE_HEIGHT):
        for x in range(MAZE_WIDTH):
            color = WALL_COLOR if maze[y][x] == 1 else PATH_COLOR
            pygame.draw.rect(screen, color, (x * TILE_SIZE + (SCREEN_WIDTH - MAZE_DISPLAY_WIDTH) // 2,
                                             y * TILE_SIZE + (SCREEN_HEIGHT - MAZE_DISPLAY_HEIGHT) // 2,
                                             TILE_SIZE, TILE_SIZE))

def draw_player(player_pos):
    pygame.draw.rect(screen, PLAYER_COLOR, (player_pos[1] * TILE_SIZE + (SCREEN_WIDTH - MAZE_DISPLAY_WIDTH) // 2,
                                            player_pos[0] * TILE_SIZE + (SCREEN_HEIGHT - MAZE_DISPLAY_HEIGHT) // 2,
                                            TILE_SIZE, TILE_SIZE))

def draw_exit(maze):
    exit_x, exit_y = MAZE_HEIGHT - 2, MAZE_WIDTH - 1
    pygame.draw.rect(screen, EXIT_COLOR, (exit_y * TILE_SIZE + (SCREEN_WIDTH - MAZE_DISPLAY_WIDTH) // 2,
                                          exit_x * TILE_SIZE + (SCREEN_HEIGHT - MAZE_DISPLAY_HEIGHT) // 2,
                                          TILE_SIZE, TILE_SIZE))

def draw_hud(start_time):
    elapsed_time = int(time.time() - start_time)
    time_text = font.render(f"Time: {elapsed_time}s", True, HUD_COLOR)
    screen.blit(time_text, (20, 20))

def check_win(player_pos, maze):
    return player_pos == (MAZE_HEIGHT - 2, MAZE_WIDTH - 1)

def main():
    maze = generate_maze()
    player_pos = (1, 0)
    start_time = time.time()
    running = True
    win = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    maze = generate_maze()
                    player_pos = (1, 0)
                    start_time = time.time()
                    win = False

        if not win:
            keys = pygame.key.get_pressed()
            new_pos = player_pos
            if keys[pygame.K_UP] and player_pos[0] > 0 and maze[player_pos[0] - 1][player_pos[1]] == 0:
                new_pos = (player_pos[0] - 1, player_pos[1])
            if keys[pygame.K_DOWN] and player_pos[0] < MAZE_HEIGHT - 1 and maze[player_pos[0] + 1][player_pos[1]] == 0:
                new_pos = (player_pos[0] + 1, player_pos[1])
            if keys[pygame.K_LEFT] and player_pos[1] > 0 and maze[player_pos[0]][player_pos[1] - 1] == 0:
                new_pos = (player_pos[0], player_pos[1] - 1)
            if keys[pygame.K_RIGHT] and player_pos[1] < MAZE_WIDTH - 1 and maze[player_pos[0]][player_pos[1] + 1] == 0:
                new_pos = (player_pos[0], player_pos[1] + 1)

            if new_pos!= player_pos:
                player_pos = new_pos

            if check_win(player_pos, maze):
                win = True

        screen.fill((0, 0, 0))
        draw_maze(maze)
        draw_player(player_pos)
        draw_exit(maze)
        draw_hud(start_time)

        if win:
            elapsed_time = int(time.time() - start_time)
            win_text = font.render("You Win", True, HUD_COLOR)
            time_text = font.render(f"Time: {elapsed_time}s", True, HUD_COLOR)
            restart_text = font.render("Press R to Restart", True, HUD_COLOR)
            screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - win_text.get_height() // 2))
            screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, SCREEN_HEIGHT // 2))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()