import pygame
import random
import sys
import math

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
PACMAN_SPEED = 3
GHOST_SPEED = 2
POWER_DURATION = 6000
LIFE_COUNT = 3
TILE_SIZE = 24

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
RED = (255, 0, 0)

MAZE = [
    "###########################",
    "#          #              #",
    "## ####### ### ####### # #",
    "#     #         #     # #",
    "# ####### ### #######   #",
    "#     #     #     #    ##",
    "# ####### ### ####### ###",
    "#   #   #   #   #   #  #",
    "### ####### ### ####### #",
    "#   #   #   #   #   #  #",
    "# ####### ### ####### ###",
    "#   #     #     #   #  #",
    "### ####### ### ####### #",
    "#  #     #     #    #  #",
    "#  ########### ####### #",
    "#                      #",
    "#########################",
]

PACMAN_START = (1, 20)
GHOST_STARTS = [(7, 11), (8, 11), (9, 11), (10, 11)]
PELLET_POSITIONS = [(i, j) for i in range(1, 19) for j in range(1, 21) if MAZE[j][i] == ' ' and (i, j) not in GHOST_STARTS]
POWER_PELLET_POSITIONS = [(4, 4), (14, 4), (4, 16), (14, 16)]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

def draw_maze():
    for y, row in enumerate(MAZE):
        for x, col in enumerate(row):
            if col == '#':
                pygame.draw.rect(screen, WHITE, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif col == ' ' and (x, y) in PELLET_POSITIONS:
                pygame.draw.circle(screen, WHITE, (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2), TILE_SIZE // 10)
            elif col =='' and (x, y) in POWER_PELLET_POSITIONS:
                pygame.draw.circle(screen, CYAN, (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2), TILE_SIZE // 5)

def draw_pacman(pos):
    pygame.draw.circle(screen, YELLOW, (pos[0] * TILE_SIZE + TILE_SIZE // 2, pos[1] * TILE_SIZE + TILE_SIZE // 2), TILE_SIZE // 2)

def draw_ghosts(ghosts):
    ghost_colors = [RED, PINK, CYAN, ORANGE]
    for i, ghost in enumerate(ghosts):
        pygame.draw.rect(screen, ghost_colors[i], (ghost[0] * TILE_SIZE, ghost[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))

def draw_hud(score, lives, pellets_left):
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    pellets_text = font.render(f"Pellets: {pellets_left}", True, WHITE)
    screen.blit(score_text, (500, 20))
    screen.blit(lives_text, (500, 60))
    screen.blit(pellets_text, (500, 100))

def game_over_screen(score):
    game_over_text = font.render("Game Over", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    restart_text = font.render("Press R to Restart", True, WHITE)
    screen.blit(game_over_text, (200, 250))
    screen.blit(score_text, (200, 300))
    screen.blit(restart_text, (200, 350))

def win_screen(score):
    win_text = font.render("You Win", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    restart_text = font.render("Press R to Restart", True, WHITE)
    screen.blit(win_text, (200, 250))
    screen.blit(score_text, (200, 300))
    screen.blit(restart_text, (200, 350))

def reset_game():
    return {
        "pacman_pos": list(PACMAN_START),
        "pacman_direction": (0, 0),
        "ghosts": [list(start) for start in GHOST_STARTS],
        "ghost_directions": [(0, 0)] * 4,
        "score": 0,
        "lives": LIFE_COUNT,
        "pellets_left": len(PELLET_POSITIONS),
        "power_active": False,
        "power_timer": 0,
        "game_over": False,
        "game_won": False,
    }

def check_collisions(game_state):
    pacman_pos = tuple(game_state["pacman_pos"])
    if pacman_pos in PELLET_POSITIONS:
        PELLET_POSITIONS.remove(pacman_pos)
        game_state["score"] += 10
        game_state["pellets_left"] -= 1
    if pacman_pos in POWER_PELLET_POSITIONS:
        POWER_PELLET_POSITIONS.remove(pacman_pos)
        game_state["score"] += 50
        game_state["power_active"] = True
        game_state["power_timer"] = pygame.time.get_ticks()
    
    for i, ghost_pos in enumerate(game_state["ghosts"]):
        if tuple(ghost_pos) == pacman_pos:
            if game_state["power_active"]:
                game_state["ghosts"][i] = list(GHOST_STARTS[i])
                game_state["score"] += 200
            else:
                game_state["lives"] -= 1
                game_state["pacman_pos"] = list(PACMAN_START)
                game_state["ghosts"] = [list(start) for start in GHOST_STARTS]

    if game_state["pellets_left"] == 0:
        game_state["game_won"] = True
    if game_state["lives"] == 0:
        game_state["game_over"] = True

def move_pacman(game_state):
    direction = game_state["pacman_direction"]
    new_pos = [game_state["pacman_pos"][0] + direction[0], game_state["pacman_pos"][1] + direction[1]]
    if MAZE[new_pos[1]][new_pos[0]]!= '#':
        game_state["pacman_pos"] = new_pos

def move_ghosts(game_state):
    for i, ghost in enumerate(game_state["ghosts"]):
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        possible_moves = []
        for d in directions:
            new_pos = [ghost[0] + d[0], ghost[1] + d[1]]
            if MAZE[new_pos[1]][new_pos[0]]!= '#':
                possible_moves.append(d)
        
        target = game_state["pacman_pos"]
        best_move = None
        best_dist = float('inf')
        for move in possible_moves:
            new_pos = [ghost[0] + move[0], ghost[1] + move[1]]
            dist = abs(new_pos[0] - target[0]) + abs(new_pos[1] - target[1])
            if dist < best_dist:
                best_dist = dist
                best_move = move
        
        if best_move:
            game_state["ghosts"][i][0] += best_move[0]
            game_state["ghosts"][i][1] += best_move[1]

game_state = reset_game()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                game_state = reset_game()
            elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                if event.key == pygame.K_UP and MAZE[game_state["pacman_pos"][1] - 1][game_state["pacman_pos"][0]]!= '#':
                    game_state["pacman_direction"] = (0, -1)
                elif event.key == pygame.K_DOWN and MAZE[game_state["pacman_pos"][1] + 1][game_state["pacman_pos"][0]]!= '#':
                    game_state["pacman_direction"] = (0, 1)
                elif event.key == pygame.K_LEFT and MAZE[game_state["pacman_pos"][1]][game_state["pacman_pos"][0] - 1]!= '#':
                    game_state["pacman_direction"] = (-1, 0)
                elif event.key == pygame.K_RIGHT and MAZE[game_state["pacman_pos"][1]][game_state["pacman_pos"][0] + 1]!= '#':
                    game_state["pacman_direction"] = (1, 0)
    
    if not game_state["game_over"] and not game_state["game_won"]:
        move_pacman(game_state)
        move_ghosts(game_state)
        check_collisions(game_state)
        
        if game_state["power_active"] and pygame.time.get_ticks() - game_state["power_timer"] > POWER_DURATION:
            game_state["power_active"] = False

    screen.fill(BLACK)
    draw_maze()
    draw_pacman(game_state["pacman_pos"])
    draw_ghosts(game_state["ghosts"])
    draw_hud(game_state["score"], game_state["lives"], game_state["pellets_left"])

    if game_state["game_over"]:
        game_over_screen(game_state["score"])
    elif game_state["game_won"]:
        win_screen(game_state["score"])

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()