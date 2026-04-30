import pygame
import random

pygame.init()
random.seed(42)

# ========== CONSTANTS ==========
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
GRID_SIZE = 24
MAZE_COLS, MAZE_ROWS = 19, 21
MAZE_WIDTH, MAZE_HEIGHT = MAZE_COLS * GRID_SIZE, MAZE_ROWS * GRID_SIZE
MAZE_OFFSET_X = (SCREEN_WIDTH - MAZE_WIDTH) // 2 - 80
MAZE_OFFSET_Y = (SCREEN_HEIGHT - MAZE_HEIGHT) // 2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WALL_COLOR = (33, 33, 222)
PATH_COLOR = BLACK
DOT_COLOR = (255, 255, 150)
ENERGY_DOT_COLOR = (255, 200, 100)
PLAYER_COLOR = (255, 255, 0)
GHOST_COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 255),  # Cyan
    (255, 182, 255),# Pink
    (255, 182, 85)  # Orange
]
HUD_BG_COLOR = (50, 50, 80)
HUD_TEXT_COLOR = (220, 220, 255)
FLEE_COLOR = (0, 0, 255)
FRUIT_COLOR = (255, 0, 255)

# Game parameters
PLAYER_SPEED = 3
GHOST_SPEED = 2
ENERGY_DURATION = 6 * FPS
LIVES = 3
DOT_SCORE = 10
ENERGY_SCORE = 50
GHOST_SCORE = 200

# Maze definition (W=Wall, .=Dot, E=Energy, P=Player start, G=Ghost start,  =empty path)
MAZE = [
    "WWWWWWWWWWWWWWWWWWW",
    "W.........W.........W",
    "W.WWW.WWW.W.WWW.WWW.W",
    "WEWWW.WWW.W.WWW.WWWE",
    "W.........W.........W",
    "W.WW.WWWWWWWWWWW.WW.W",
    "W...W...W   W...W...W",
    "WWW.WWW.W   W.WWW.WWW",
    "   W.........P.........W",
    "WWW.WWW.WWWWWW.WWW.WWW",
    "W.........W.........W",
    "W.WWW.WWW.W.WWW.WWW.W",
    "WE...W.....G.....W..E",
    "WWW.W.WWWWWWWWWW.W.WWW",
    "W.....W.........W.....W",
    "W.WWWWWWWW.WWWWWWWW.W",
    "W.....................W",
    "WWWWWWWWWWWWWWWWWWW"
]

# ========== GLOBAL VARIABLES ==========
player_pos = [0, 0]
player_dir = [0, 0]
player_next_dir = [0, 0]
lives = LIVES
score = 0
dots_eaten = 0
total_dots = 0
energy_timer = 0
game_over = False
game_win = False
ghosts = []
dots = []
walls = []
energy_dots = []

# ========== HELPER FUNCTIONS ==========
def init_game():
    global player_pos, player_dir, player_next_dir, lives, score, dots_eaten, total_dots
    global energy_timer, game_over, game_win, ghosts, dots, walls, energy_dots

    player_pos = [MAZE_COLS // 2 * GRID_SIZE, 15 * GRID_SIZE]
    player_dir = [0, 0]
    player_next_dir = [0, 0]
    lives = LIVES
    score = 0
    dots_eaten = 0
    total_dots = 0
    energy_timer = 0
    game_over = False
    game_win = False

    ghosts.clear()
    dots.clear()
    walls.clear()
    energy_dots.clear()

    ghost_start_positions = []

    for y, row in enumerate(MAZE):
        for x, ch in enumerate(row):
            rect = pygame.Rect(
                MAZE_OFFSET_X + x * GRID_SIZE,
                MAZE_OFFSET_Y + y * GRID_SIZE,
                GRID_SIZE, GRID_SIZE
            )
            if ch == 'W':
                walls.append(rect)
            elif ch == '.':
                dots.append(rect)
                total_dots += 1
            elif ch == 'E':
                energy_dots.append(rect)
                total_dots += 1
            elif ch == 'P':
                player_pos = [rect.x + GRID_SIZE // 2, rect.y + GRID_SIZE // 2]
            elif ch == 'G':
                ghost_start_positions.append((rect.x + GRID_SIZE // 2, rect.y + GRID_SIZE // 2))

    for i in range(4):
        if i < len(ghost_start_positions):
            ghosts.append({
                'pos': list(ghost_start_positions[i]),
                'dir': [0, 0],
                'color': GHOST_COLORS[i],
                'flee': False,
                'eaten': False,
                'respawn_timer': 0
            })

def check_wall_collision(pos, dir):
    test_rect = pygame.Rect(pos[0] - GRID_SIZE//2, pos[1] - GRID_SIZE//2, GRID_SIZE, GRID_SIZE)
    if dir[0] > 0:
        test_rect.x += PLAYER_SPEED
    elif dir[0] < 0:
        test_rect.x -= PLAYER_SPEED
    if dir[1] > 0:
        test_rect.y += PLAYER_SPEED
    elif dir[1] < 0:
        test_rect.y -= PLAYER_SPEED
    for wall in walls:
        if test_rect.colliderect(wall):
            return True
    return False

def move_player():
    global player_dir
    if player_next_dir != [0, 0]:
        temp_pos = player_pos.copy()
        if player_next_dir[0] > 0:
            temp_pos[0] += PLAYER_SPEED
        elif player_next_dir[0] < 0:
            temp_pos[0] -= PLAYER_SPEED
        elif player_next_dir[1] > 0:
            temp_pos[1] += PLAYER_SPEED
        elif player_next_dir[1] < 0:
            temp_pos[1] -= PLAYER_SPEED
        test_rect = pygame.Rect(temp_pos[0] - GRID_SIZE//2, temp_pos[1] - GRID_SIZE//2, GRID_SIZE, GRID_SIZE)
        collided = any(test_rect.colliderect(wall) for wall in walls)
        if not collided:
            player_dir = player_next_dir[:]
    if player_dir != [0, 0] and not check_wall_collision(player_pos, player_dir):
        player_pos[0] += player_dir[0] * PLAYER_SPEED
        player_pos[1] += player_dir[1] * PLAYER_SPEED
        # Tunnel wrap
        if player_pos[0] < MAZE_OFFSET_X - GRID_SIZE//2:
            player_pos[0] = MAZE_OFFSET_X + MAZE_WIDTH - GRID_SIZE//2
        elif player_pos[0] > MAZE_OFFSET_X + MAZE_WIDTH - GRID_SIZE//2:
            player_pos[0] = MAZE_OFFSET_X - GRID_SIZE//2

def move_ghosts():
    for ghost in ghosts:
        if ghost['eaten']:
            if ghost['respawn_timer'] > 0:
                ghost['respawn_timer'] -= 1
            else:
                ghost['eaten'] = False
                ghost['flee'] = False
                ghost['pos'] = [MAZE_OFFSET_X + (MAZE_COLS // 2) * GRID_SIZE, MAZE_OFFSET_Y + 9 * GRID_SIZE]
            continue

        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        valid_dirs = []
        for dx, dy in directions:
            test_pos = [ghost['pos'][0] + dx * GHOST_SPEED, ghost['pos'][1] + dy * GHOST_SPEED]
            test_rect = pygame.Rect(test_pos[0] - GRID_SIZE//2, test_pos[1] - GRID_SIZE//2, GRID_SIZE, GRID_SIZE)
            if not any(test_rect.colliderect(wall) for wall in walls):
                valid_dirs.append((dx, dy))
        if not valid_dirs:
            continue

        if ghost['flee']:
            chosen = random.choice(valid_dirs)
        else:
            # Simple chase: move towards player
            best_dir = None
            min_dist = float('inf')
            for dx, dy in valid_dirs:
                new_x = ghost['pos'][0] + dx * GHOST_SPEED
                new_y = ghost['pos'][1] + dy * GHOST_SPEED
                dist = (new_x - player_pos[0])**2 + (new_y - player_pos[1])**2
                if dist < min_dist:
                    min_dist = dist
                    best_dir = (dx, dy)
            chosen = best_dir if best_dir else valid_dirs[0]

        ghost['dir'] = list(chosen)
        ghost['pos'][0] += ghost['dir'][0] * GHOST_SPEED
        ghost['pos'][1] += ghost['dir'][1] * GHOST_SPEED

        # Tunnel wrap
        if ghost['pos'][0] < MAZE_OFFSET_X - GRID_SIZE//2:
            ghost['pos'][0] = MAZE_OFFSET_X + MAZE_WIDTH - GRID_SIZE//2
        elif ghost['pos'][0] > MAZE_OFFSET_X + MAZE_WIDTH - GRID_SIZE//2:
            ghost['pos'][0] = MAZE_OFFSET_X - GRID_SIZE//2

def check_dots():
    global score, dots_eaten, energy_timer
    player_rect = pygame.Rect(player_pos[0] - 8, player_pos[1] - 8, 16, 16)
    for dot in list(dots):
        if player_rect.colliderect(dot):
            dots.remove(dot)
            score += DOT_SCORE
            dots_eaten += 1
    for edot in list(energy_dots):
        if player_rect.colliderect(edot):
            energy_dots.remove(edot)
            score += ENERGY_SCORE
            dots_eaten += 1
            energy_timer = ENERGY_DURATION
            for ghost in ghosts:
                ghost['flee'] = True

def check_ghost_collision():
    global lives, score, game_over
    player_rect = pygame.Rect(player_pos[0] - 10, player_pos[1] - 10, 20, 20)
    for ghost in ghosts:
        if ghost['eaten']:
            continue
        ghost_rect = pygame.Rect(ghost['pos'][0] - 12, ghost['pos'][1] - 12, 24, 24)
        if player_rect.colliderect(ghost_rect):
            if energy_timer > 0:
                ghost['eaten'] = True
                ghost['flee'] = False
                ghost['respawn_timer'] = 3 * FPS
                score += GHOST_SCORE
            else:
                lives -= 1
                if lives <= 0:
                    game_over = True
                else:
                    # Reset positions
                    player_pos[0] = MAZE_OFFSET_X + (MAZE_COLS // 2) * GRID_SIZE
                    player_pos[1] = MAZE_OFFSET_Y + 15 * GRID_SIZE
                    player_dir[0] = player_dir[1] = 0
                    player_next_dir[0] = player_next_dir[1] = 0
                    for i, ghost_obj in enumerate(ghosts):
                        ghost_obj['pos'] = [MAZE_OFFSET_X + (MAZE_COLS // 2) * GRID_SIZE, MAZE_OFFSET_Y + 9 * GRID_SIZE]
                        ghost_obj['eaten'] = False
                        ghost_obj['flee'] = False
                break

def update_game():
    global energy_timer, game_win
    if game_over or game_win:
        return
    move_player()
    move_ghosts()
    check_dots()
    check_ghost_collision()
    if energy_timer > 0:
        energy_timer -= 1
        if energy_timer == 0:
            for ghost in ghosts:
                ghost['flee'] = False
    if dots_eaten >= total_dots:
        game_win = True

def draw_hud(screen, font):
    hud_rect = pygame.Rect(MAZE_OFFSET_X + MAZE_WIDTH + 10, MAZE_OFFSET_Y, 200, MAZE_HEIGHT)
    pygame.draw.rect(screen, HUD_BG_COLOR, hud_rect)

    lines = [
        f"SCORE: {score}",
        f"LIVES: {lives}",
        f"DOTS: {dots_eaten}/{total_dots}",
        f"ENERGY: {energy_timer//FPS}s" if energy_timer > 0 else ""
    ]
    for i, line in enumerate(lines):
        text = font.render(line, True, HUD_TEXT_COLOR)
        screen.blit(text, (hud_rect.x + 20, hud_rect.y + 40 + i * 40))

    if game_over:
        text = font.render("GAME OVER", True, (255, 50, 50))
        screen.blit(text, (hud_rect.x + 20, hud_rect.y + 200))
        text = font.render("Press R to Restart", True, HUD_TEXT_COLOR)
        screen.blit(text, (hud_rect.x + 20, hud_rect.y + 250))
    elif game_win:
        text = font.render("YOU WIN!", True, (50, 255, 50))
        screen.blit(text, (hud_rect.x + 20, hud_rect.y + 200))
        text = font.render("Press R to Restart", True, HUD_TEXT_COLOR)
        screen.blit(text, (hud_rect.x + 20, hud_rect.y + 250))

def draw_game(screen):
    screen.fill(BLACK)
    # Draw walls
    for wall in walls:
        pygame.draw.rect(screen, WALL_COLOR, wall)
    # Draw dots
    for dot in dots:
        pygame.draw.circle(screen, DOT_COLOR, dot.center, 4)
    for edot in energy_dots:
        pygame.draw.circle(screen, ENERGY_DOT_COLOR, edot.center, 8)
    # Draw ghosts
    for ghost in ghosts:
        color = FLEE_COLOR if ghost['flee'] else ghost['color']
        if not ghost['eaten']:
            pygame.draw.circle(screen, color, (int(ghost['pos'][0]), int(ghost['pos'][1])), 12)
    # Draw player
    pygame.draw.circle(screen, PLAYER_COLOR, (int(player_pos[0]), int(player_pos[1])), 12)

# ========== MAIN GAME LOOP ==========
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pac-Man Medium")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    init_game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    init_game()
                elif not game_over and not game_win:
                    if event.key == pygame.K_UP:
                        player_next_dir = [0, -1]
                    elif event.key == pygame.K_DOWN:
                        player_next_dir = [0, 1]
                    elif event.key == pygame.K_LEFT:
                        player_next_dir = [-1, 0]
                    elif event.key == pygame.K_RIGHT:
                        player_next_dir = [1,137183]
                        player_next_dir = [1, 0]

        update_game()
        draw_game(screen)
        draw_hud(screen, font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()