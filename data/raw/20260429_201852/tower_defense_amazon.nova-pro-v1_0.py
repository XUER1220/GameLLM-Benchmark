import pygame
import sys
import random
import time

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRID_SIZE = 32
COLS = 20
ROWS = 15
MAP_WIDTH = COLS * GRID_SIZE
MAP_HEIGHT = ROWS * GRID_SIZE
HUD_WIDTH = SCREEN_WIDTH - MAP_WIDTH

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

BASE_HEALTH = 20
INITIAL_GOLD = 180
WAVES = [
    [{"type": "normal", "count": 5}],
    [{"type": "fast", "count": 3}, {"type": "normal", "count": 4}],
    [{"type": "heavy", "count": 2}, {"type": "fast", "count": 2}, {"type": "normal", "count": 3}],
    [{"type": "heavy", "count": 3}, {"type": "fast", "count": 4}, {"type": "normal", "count": 5}],
    [{"type": "heavy", "count": 5}, {"type": "fast", "count": 5}, {"type": "normal", "count": 6}]
]
ENEMY_STATS = {
    "normal": {"health": 10, "speed": 2, "reward": 10},
    "fast": {"health": 5, "speed": 4, "reward": 5},
    "heavy": {"health": 20, "speed": 1, "reward": 15}
}
TOWER_STATS = {
    "arrow": {"cost": 50, "range": 120, "damage": 8, "rate": 0.8, "upgrade_cost": 35, "upgrades": 2},
    "cannon": {"cost": 80, "range": 105, "damage": 14, "rate": 1.2, "splash": 45, "upgrade_cost": 56, "upgrades": 2},
    "slow": {"cost": 70, "range": 110, "damage": 4, "rate": 1.0, "slow_duration": 2, "upgrade_cost": 49, "upgrades": 2}
}
PATH = [
    (0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7),
    (9, 7), (10, 7), (11, 7), (12, 7), (13, 7), (14, 7), (15, 7), (16, 7),
    (17, 7), (18, 7), (19, 7)
]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense Hard")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

base_health = BASE_HEALTH
gold = INITIAL_GOLD
current_wave = 0
wave_start_time = 0
enemies = []
towers = []
selected_tower = None
game_over = False
win = False

class Tower:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.stats = TOWER_STATS[type]
        self.range = self.stats["range"]
        self.damage = self.stats["damage"]
        self.rate = self.stats["rate"]
        self.last_shot = 0
        self.level = 0
        self.upgrades = self.stats["upgrades"]
        self.splash = self.stats.get("splash", 0)
        self.slow_duration = self.stats.get("slow_duration", 0)

    def upgrade(self):
        if self.level < self.upgrades:
            global gold
            cost = self.stats["upgrade_cost"]
            if gold >= cost:
                gold -= cost
                self.level += 1
                self.damage += self.damage * 0.1
                self.range += 10
                if self.splash > 0:
                    self.splash += 5

    def attack(self, enemies):
        if pygame.time.get_ticks() / 1000 - self.last_shot >= self.rate:
            targets = [e for e in enemies if ((e.x - self.x) ** 2 + (e.y - self.y) ** 2) ** 0.5 <= self.range]
            if targets:
                target = random.choice(targets)
                target.health -= self.damage
                if self.splash > 0:
                    for e in enemies:
                        if ((e.x - self.x) ** 2 + (e.y - self.y) ** 2) ** 0.5 <= self.range + self.splash:
                            e.health -= self.damage
                if self.slow_duration > 0:
                    target.slow_end_time = pygame.time.get_ticks() / 1000 + self.slow_duration
                self.last_shot = pygame.time.get_ticks() / 1000

class Enemy:
    def __init__(self, type):
        self.type = type
        self.stats = ENEMY_STATS[type]
        self.health = self.stats["health"]
        self.speed = self.stats["speed"]
        self.reward = self.stats["reward"]
        self.path_index = 0
        self.x, self.y = PATH[self.path_index]
        self.slow_end_time = 0

    def move(self):
        if self.path_index < len(PATH) - 1:
            target_x, target_y = PATH[self.path_index + 1]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance <= self.speed:
                self.x = target_x
                self.y = target_y
                self.path_index += 1
            else:
                self.x += dx / distance * self.speed
                self.y += dy / distance * self.speed
        if self.slow_end_time > pygame.time.get_ticks() / 1000:
            self.speed = 1
        else:
            self.speed = ENEMY_STATS[self.type]["speed"]

def draw_grid():
    for x in range(0, MAP_WIDTH, GRID_SIZE):
        for y in range(0, MAP_HEIGHT, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)
            if (x // GRID_SIZE, y // GRID_SIZE) in PATH:
                pygame.draw.rect(screen, YELLOW, rect)

def draw_path():
    for point in PATH:
        pygame.draw.rect(screen, ORANGE, (point[0] * GRID_SIZE, point[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_base():
    pygame.draw.rect(screen, RED, (MAP_WIDTH, MAP_HEIGHT // 2 * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_hud():
    pygame.draw.rect(screen, BLACK, (MAP_WIDTH, 0, HUD_WIDTH, SCREEN_HEIGHT))
    pygame.draw.rect(screen, WHITE, (MAP_WIDTH + 10, 10, HUD_WIDTH - 20, SCREEN_HEIGHT - 20))
    health_text = font.render(f"Base Health: {base_health}", True, RED)
    gold_text = font.render(f"Gold: {gold}", True, YELLOW)
    wave_text = font.render(f"Wave: {current_wave + 1}", True, WHITE)
    enemies_left_text = font.render(f"Enemies Left: {sum(e['count'] for e in WAVES[current_wave])}", True, WHITE)
    selected_tower_text = font.render(f"Selected Tower: {selected_tower}", True, WHITE)
    screen.blit(health_text, (MAP_WIDTH + 20, 20))
    screen.blit(gold_text, (MAP_WIDTH + 20, 50))
    screen.blit(wave_text, (MAP_WIDTH + 20, 80))
    screen.blit(enemies_left_text, (MAP_WIDTH + 20, 110))
    screen.blit(selected_tower_text, (MAP_WIDTH + 20, 140))

def draw_towers():
    for tower in towers:
        color = GREEN if tower.type == "arrow" else BLUE if tower.type == "cannon" else PURPLE
        pygame.draw.rect(screen, color, (tower.x * GRID_SIZE, tower.y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        pygame.draw.circle(screen, CYAN, (tower.x * GRID_SIZE + GRID_SIZE // 2, tower.y * GRID_SIZE + GRID_SIZE // 2), tower.range)
        level_text = font.render(f"Lv{tower.level + 1}", True, WHITE)
        screen.blit(level_text, (tower.x * GRID_SIZE + GRID_SIZE // 2 - 10, tower.y * GRID_SIZE + GRID_SIZE // 2 - 10))

def draw_enemies():
    for enemy in enemies:
        color = GREEN if enemy.type == "normal" else RED if enemy.type == "fast" else BLUE
        pygame.draw.rect(screen, color, (enemy.x * GRID_SIZE, enemy.y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        health_text = font.render(str(enemy.health), True, WHITE)
        screen.blit(health_text, (enemy.x * GRID_SIZE + GRID_SIZE // 2 - 10, enemy.y * GRID_SIZE + GRID_SIZE // 2 - 10))

def spawn_enemies():
    global current_wave, wave_start_time
    if current_wave < len(WAVES):
        wave = WAVES[current_wave]
        for enemy_type in wave:
            for _ in range(enemy_type["count"]):
                enemies.append(Enemy(enemy_type["type"]))
        current_wave += 1
        wave_start_time = pygame.time.get_ticks() / 1000

def check_game_over():
    global game_over, win
    if base_health <= 0:
        game_over = True
    if current_wave >= len(WAVES) and not enemies:
        win = True

def draw_game_over():
    if game_over:
        game_over_text = font.render("Game Over", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 30))
        restart_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2))
    elif win:
        win_text = font.render("You Win", True, GREEN)
        screen.blit(win_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 30))
        restart_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2))

def reset_game():
    global base_health, gold, current_wave, enemies, towers, game_over, win
    base_health = BASE_HEALTH
    gold = INITIAL_GOLD
    current_wave = 0
    enemies = []
    towers = []
    game_over = False
    win = False

running = True
while running:
    screen.fill(BLACK)
    draw_grid()
    draw_path()
    draw_base()
    draw_hud()
    draw_towers()
    draw_enemies()

    if not game_over and not win:
        if current_wave < len(WAVES) and (pygame.time.get_ticks() / 1000 - wave_start_time) > 3:
            spawn_enemies()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    reset_game()
                elif event.key == pygame.K_1:
                    selected_tower = "arrow"
                elif event.key == pygame.K_2:
                    selected_tower = "cannon"
                elif event.key == pygame.K_3:
                    selected_tower = "slow"
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over and not win:
                x, y = event.pos
                if x < MAP_WIDTH and y < MAP_HEIGHT:
                    grid_x, grid_y = x // GRID_SIZE, y // GRID_SIZE
                    if (grid_x, grid_y) not in PATH and (grid_x, grid_y)!= PATH[-1] and (grid_x, grid_y)!= PATH[0] and not any(tower for tower in towers if tower.x == grid_x and tower.y == grid_y):
                        if event.button == 1 and selected_tower and gold >= TOWER_STATS[selected_tower]["cost"]:
                            towers.append(Tower(grid_x, grid_y, selected_tower))
                            gold -= TOWER_STATS[selected_tower]["cost"]
                        elif event.button == 3:
                            for tower in towers:
                                if tower.x == grid_x and tower.y == grid_y:
                                    tower.upgrade()
                                    break

        for tower in towers:
            tower.attack(enemies)

        for enemy in enemies[:]:
            enemy.move()
            if (enemy.x, enemy.y) == PATH[-1]:
                base_health -= 1
                enemies.remove(enemy)
            elif enemy.health <= 0:
                gold += ENEMY_STATS[enemy.type]["reward"]
                enemies.remove(enemy)

        check_game_over()

    draw_game_over()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()