import pygame
import sys
import random
import math

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRID_SIZE = 32
MAP_WIDTH = 20
MAP_HEIGHT = 15
HUD_WIDTH = 160

WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
BLACK = (0, 0, 0)

BASE_HEALTH = 20
INITIAL_GOLD = 180
WAVES = [
    [{"type": "normal", "count": 5}],
    [{"type": "fast", "count": 5}],
    [{"type": "tank", "count": 3}],
    [{"type": "normal", "count": 7}, {"type": "fast", "count": 3}],
    [{"type": "tank", "count": 5}, {"type": "normal", "count": 5}]
]

ENEMY_TYPES = {
    "normal": {"health": 10, "speed": 2, "reward": 10},
    "fast": {"health": 5, "speed": 4, "reward": 5},
    "tank": {"health": 20, "speed": 1, "reward": 15}
}

TOWER_TYPES = {
    "arrow": {"cost": 50, "range": 120, "damage": 8, "rate": 0.8, "color": GREEN},
    "cannon": {"cost": 80, "range": 105, "damage": 14, "rate": 1.2, "splash": 45, "color": RED},
    "slow": {"cost": 70, "range": 110, "damage": 4, "rate": 1.0, "slow": 2, "color": BLUE}
}

UPGRADE_COST_RATIO = 0.7
MAX_UPGRADES = 2

PATH = [
    (0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
    (8, 7), (9, 7), (10, 7), (11, 7), (12, 7), (13, 7), (14, 7),
    (15, 7), (16, 7), (17, 7), (18, 7), (19, 7)
]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense Hard")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

base_health = BASE_HEALTH
gold = INITIAL_GOLD
wave_index = 0
wave_start_time = 0
enemies = []
towers = []
projectiles = []
selected_tower_type = None
game_over = False
game_won = False

def draw_grid():
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)
            if (x, y) in PATH:
                pygame.draw.rect(screen, YELLOW, rect)

def draw_path():
    for x, y in PATH:
        rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, YELLOW, rect)

def draw_base():
    base_rect = pygame.Rect(MAP_WIDTH * GRID_SIZE, 7 * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(screen, RED, base_rect)

def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(screen, enemy["color"], pygame.Rect(enemy["x"] * GRID_SIZE, enemy["y"] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_towers():
    for tower in towers:
        pygame.draw.rect(screen, tower["color"], pygame.Rect(tower["x"] * GRID_SIZE, tower["y"] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        if 'range' in tower:
            pygame.draw.circle(screen, (255, 255, 255, 50), ((tower["x"] + 0.5) * GRID_SIZE, (tower["y"] + 0.5) * GRID_SIZE), tower["range"], 1)

def draw_projectiles():
    for projectile in projectiles:
        pygame.draw.circle(screen, projectile["color"], (projectile["x"], projectile["y"]), 5)

def draw_hud():
    pygame.draw.rect(screen, BLACK, pygame.Rect(MAP_WIDTH * GRID_SIZE, 0, HUD_WIDTH, SCREEN_HEIGHT))
    base_health_text = font.render(f"Base Health: {base_health}", True, WHITE)
    gold_text = font.render(f"Gold: {gold}", True, WHITE)
    wave_text = font.render(f"Wave: {wave_index + 1}", True, WHITE)
    enemies_left_text = font.render(f"Enemies Left: {sum(wave['count'] for wave in WAVES[wave_index]) - len(enemies)}", True, WHITE)
    selected_tower_text = font.render(f"Selected Tower: {selected_tower_type.capitalize() if selected_tower_type else 'None'}", True, WHITE)

    screen.blit(base_health_text, (MAP_WIDTH * GRID_SIZE + 10, 10))
    screen.blit(gold_text, (MAP_WIDTH * GRID_SIZE + 10, 40))
    screen.blit(wave_text, (MAP_WIDTH * GRID_SIZE + 10, 70))
    screen.blit(enemies_left_text, (MAP_WIDTH * GRID_SIZE + 10, 100))
    screen.blit(selected_tower_text, (MAP_WIDTH * GRID_SIZE + 10, 130))

    if game_over:
        game_over_text = font.render("Game Over", True, RED)
        screen.blit(game_over_text, (MAP_WIDTH * GRID_SIZE + 50, SCREEN_HEIGHT // 2 - 30))
        restart_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(restart_text, (MAP_WIDTH * GRID_SIZE + 30, SCREEN_HEIGHT // 2))
    elif game_won:
        game_won_text = font.render("You Win", True, GREEN)
        screen.blit(game_won_text, (MAP_WIDTH * GRID_SIZE + 50, SCREEN_HEIGHT // 2 - 30))
        restart_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(restart_text, (MAP_WIDTH * GRID_SIZE + 30, SCREEN_HEIGHT // 2))

def distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

def is_on_path(x, y):
    return (x, y) in PATH

def is_valid_placement(x, y):
    return not is_on_path(x, y) and (x, y) not in [(tower["x"], tower["y"]) for tower in towers] and x!= MAP_WIDTH - 1 and y!= 7

def place_tower(x, y, tower_type):
    global gold
    tower = TOWER_TYPES[tower_type].copy()
    tower["x"] = x
    tower["y"] = y
    tower["color"] = TOWER_TYPES[tower_type]["color"]
    tower["target"] = None
    tower["last_shot"] = 0
    tower["level"] = 1
    towers.append(tower)
    gold -= TOWER_TYPES[tower_type]["cost"]

def upgrade_tower(tower):
    global gold
    if tower["level"] < MAX_UPGRADES:
        upgrade_cost = int(TOWER_TYPES[tower["type"]]["cost"] * UPGRADE_COST_RATIO)
        if gold >= upgrade_cost:
            gold -= upgrade_cost
            tower["level"] += 1
            tower["damage"] += TOWER_TYPES[tower["type"]]["damage"] // 2
            tower["range"] += 10

def spawn_enemy(enemy_type, count):
    for _ in range(count):
        enemy = ENEMY_TYPES[enemy_type].copy()
        enemy["x"] = 0
        enemy["y"] = 7
        enemy["path_index"] = 0
        enemy["color"] = CYAN if enemy_type == "normal" else MAGENTA if enemy_type == "fast" else RED
        enemies.append(enemy)

def move_enemies():
    for enemy in enemies:
        if enemy["path_index"] < len(PATH) - 1:
            tx, ty = PATH[enemy["path_index"]]
            nx, ny = PATH[enemy["path_index"] + 1]
            direction = (nx - tx, ny - ty)
            length = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
            enemy["x"] += direction[0] / length * enemy["speed"]
            enemy["y"] += direction[1] / length * enemy["speed"]
            if int(enemy["x"]) == nx and int(enemy["y"]) == ny:
                enemy["x"] = nx
                enemy["y"] = ny
                enemy["path_index"] += 1
        else:
            global base_health
            base_health -= 1
            enemies.remove(enemy)

def check_tower_targets():
    for tower in towers:
        closest_enemy = None
        closest_distance = float('inf')
        for enemy in enemies:
            distance_to_enemy = distance((tower["x"], tower["y"]), (enemy["x"], enemy["y"]))
            if distance_to_enemy <= tower["range"]:
                if distance_to_enemy < closest_distance:
                    closest_enemy = enemy
                    closest_distance = distance_to_enemy
        tower["target"] = closest_enemy

def shoot_projectiles():
    current_time = pygame.time.get_ticks() / 1000
    for tower in towers:
        if tower["target"] and current_time - tower["last_shot"] > tower["rate"]:
            projectile = {
                "x": tower["x"] * GRID_SIZE + GRID_SIZE // 2,
                "y": tower["y"] * GRID_SIZE + GRID_SIZE // 2,
                "target": tower["target"],
                "color": tower["color"],
                "damage": tower["damage"]
            }
            projectiles.append(projectile)
            tower["last_shot"] = current_time

def move_projectiles():
    for projectile in projectiles:
        direction = (projectile["target"]["x"] - projectile["x"], projectile["target"]["y"] - projectile["y"])
        length = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
        projectile["x"] += direction[0] / length * 10
        projectile["y"] += direction[1] / length * 10
        if distance((projectile["x"], projectile["y"]), (projectile["target"]["x"] * GRID_SIZE + GRID_SIZE // 2, projectile["target"]["y"] * GRID_SIZE + GRID_SIZE // 2)) < GRID_SIZE // 2:
            projectile["target"]["health"] -= projectile["damage"]
            global gold
            gold += projectile["target"]["reward"]
            if projectile["target"]["health"] <= 0:
                enemies.remove(projectile["target"])
            projectiles.remove(projectile)

def check_game_status():
    global game_over, game_won
    if base_health <= 0:
        game_over = True
    if wave_index == len(WAVES) - 1 and not enemies:
        game_won = True

def reset_game():
    global base_health, gold, wave_index, enemies, towers, projectiles, game_over, game_won, wave_start_time
    base_health = BASE_HEALTH
    gold = INITIAL_GOLD
    wave_index = 0
    enemies = []
    towers = []
    projectiles = []
    game_over = False
    game_won = False
    wave_start_time = pygame.time.get_ticks()

running = True
while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                reset_game()
            elif event.key == pygame.K_1:
                selected_tower_type = "arrow"
            elif event.key == pygame.K_2:
                selected_tower_type = "cannon"
            elif event.key == pygame.K_3:
                selected_tower_type = "slow"
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_over and not game_won:
            x, y = event.pos
            grid_x = x // GRID_SIZE
            grid_y = y // GRID_SIZE
            if event.button == 1 and selected_tower_type and is_valid_placement(grid_x, grid_y):
                place_tower(grid_x, grid_y, selected_tower_type)
            elif event.button == 3:
                for tower in towers:
                    if distance((grid_x, grid_y), (tower["x"], tower["y"])) <= 1:
                        upgrade_tower(tower)
                        break

    screen.fill(BLACK)
    draw_grid()
    draw_path()
    draw_base()
    draw_enemies()
    draw_towers()
    draw_projectiles()
    draw_hud()

    if not game_over and not game_won:
        if current_time - wave_start_time > 3000 and not enemies:
            wave_start_time = current_time
            wave_index += 1
            if wave_index < len(WAVES):
                for wave in WAVES[wave_index]:
                    spawn_enemy(wave["type"], wave["count"])

        move_enemies()
        check_tower_targets()
        shoot_projectiles()
        move_projectiles()
        check_game_status()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()