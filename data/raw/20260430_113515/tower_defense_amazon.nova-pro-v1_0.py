import pygame
import sys
import random
import math

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
MAP_WIDTH, MAP_HEIGHT = 20, 15
TILE_SIZE = 32
HUD_WIDTH = 160
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (150, 150, 150)
PATH_COLOR = (100, 100, 100)
GROUND_COLOR = (50, 50, 50)
BASE_COLOR = (200, 50, 50)
ARROW_TOWER_COLOR = (100, 200, 100)
CANNON_TOWER_COLOR = (100, 100, 200)
SLOW_TOWER_COLOR = (200, 100, 200)
ENEMY_COLORS = [RED, GREEN, BLUE]
ARROW_COLOR = (200, 200, 50)
CANNON_SPLASH_COLOR = (50, 200, 200)
SLOW_EFFECT_COLOR = (100, 100, 200)

ARROW_TOWER_COST = 50
CANNON_TOWER_COST = 80
SLOW_TOWER_COST = 70
ARROW_TOWER_DAMAGE = 8
CANNON_TOWER_DAMAGE = 14
SLOW_TOWER_DAMAGE = 4
ARROW_TOWER_RANGE = 120
CANNON_TOWER_RANGE = 105
SLOW_TOWER_RANGE = 110
ARROW_TOWER_SPEED = 0.8
CANNON_TOWER_SPEED = 1.2
SLOW_TOWER_SPEED = 1.0
CANNON_SPLASH_RADIUS = 45
SLOW_DURATION = 2.0
BASE_HEALTH = 20
INITIAL_GOLD = 180

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense Hard")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

path = [
    (0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7),
    (10, 7), (11, 7), (12, 7), (13, 7), (14, 7), (15, 7), (16, 7), (17, 7), (18, 7), (19, 7)
]

waves = [
    [{"type": 0, "health": 10, "speed": 1, "reward": 10} for _ in range(5)],
    [{"type": 0, "health": 15, "speed": 1, "reward": 15} for _ in range(5)] +
    [{"type": 1, "health": 10, "speed": 2, "reward": 10} for _ in range(3)],
    [{"type": 0, "health": 20, "speed": 1, "reward": 20} for _ in range(5)] +
    [{"type": 2, "health": 30, "speed": 0.5, "reward": 30} for _ in range(2)],
    [{"type": 1, "health": 15, "speed": 2, "reward": 15} for _ in range(5)] +
    [{"type": 2, "health": 30, "speed": 0.5, "reward": 30} for _ in range(3)],
    [{"type": 2, "health": 40, "speed": 0.5, "reward": 40} for _ in range(5)] +
    [{"type": 0, "health": 20, "speed": 1, "reward": 20} for _ in range(5)]
]

class Tower:
    def __init__(self, x, y, tower_type):
        self.x, self.y = x, y
        self.type = tower_type
        self.level = 1
        self.range = {
            0: ARROW_TOWER_RANGE,
            1: CANNON_TOWER_RANGE,
            2: SLOW_TOWER_RANGE
        }[tower_type]
        self.damage = {
            0: ARROW_TOWER_DAMAGE,
            1: CANNON_TOWER_DAMAGE,
            2: SLOW_TOWER_DAMAGE
        }[tower_type]
        self.attack_speed = {
            0: ARROW_TOWER_SPEED,
            1: CANNON_TOWER_SPEED,
            2: SLOW_TOWER_SPEED
        }[tower_type]
        self.last_attack_time = pygame.time.get_ticks()

    def can_upgrade(self):
        return self.level < 3 and gold >= {
            0: ARROW_TOWER_COST * 0.7,
            1: CANNON_TOWER_COST * 0.7,
            2: SLOW_TOWER_COST * 0.7
        }[self.type] * self.level

    def upgrade(self):
        if self.can_upgrade():
            global gold
            gold -= {
                0: ARROW_TOWER_COST * 0.7,
                1: CANNON_TOWER_COST * 0.7,
                2: SLOW_TOWER_COST * 0.7
            }[self.type] * self.level
            self.level += 1
            self.range += 10
            self.damage += 2
            self.attack_speed *= 0.9

    def attack(self, enemies):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.attack_speed * 1000:
            target = min(enemies, key=lambda e: math.hypot(e.x - self.x * TILE_SIZE, e.y - self.y * TILE_SIZE), default=None)
            if target and math.hypot(target.x - self.x * TILE_SIZE, target.y - self.y * TILE_SIZE) <= self.range:
                self.last_attack_time = current_time
                target.health -= self.damage
                if self.type == 1:
                    for e in enemies:
                        if math.hypot(e.x - target.x, e.y - target.y) <= CANNON_SPLASH_RADIUS:
                            e.health -= self.damage * 0.5
                elif self.type == 2:
                    target.slowed_until = current_time + SLOW_DURATION * 1000

class Enemy:
    def __init__(self, wave_info):
        self.type = wave_info["type"]
        self.health = wave_info["health"]
        self.speed = wave_info["speed"]
        self.reward = wave_info["reward"]
        self.path_index = 0
        self.x, self.y = path[0]
        self.slowed_until = 0

    def move(self):
        if self.path_index < len(path) - 1:
            target_x, target_y = path[self.path_index + 1]
            dx = target_x * TILE_SIZE - self.x
            dy = target_y * TILE_SIZE - self.y
            distance = math.hypot(dx, dy)
            if distance <= self.speed * (1 if pygame.time.get_ticks() >= self.slowed_until else 0.5):
                self.x = target_x * TILE_SIZE
                self.y = target_y * TILE_SIZE
                self.path_index += 1
            else:
                self.x += dx / distance * self.speed * (1 if pygame.time.get_ticks() >= self.slowed_until else 0.5)
                self.y += dy / distance * self.speed * (1 if pygame.time.get_ticks() >= self.slowed_until else 0.5)

def draw_grid():
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, GROUND_COLOR, rect)
            if (x, y) in path:
                pygame.draw.rect(screen, PATH_COLOR, rect)
            elif (x, y) == (0, 7):
                pygame.draw.rect(screen, BASE_COLOR, rect)
    for tower in towers:
        pygame.draw.rect(screen, {
            0: ARROW_TOWER_COLOR,
            1: CANNON_TOWER_COLOR,
            2: SLOW_TOWER_COLOR
        }[tower.type], (tower.x * TILE_SIZE, tower.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.draw.circle(screen, LIGHT_GRAY, (tower.x * TILE_SIZE + TILE_SIZE // 2, tower.y * TILE_SIZE + TILE_SIZE // 2), tower.range, 1)
        text = font.render(str(tower.level), True, WHITE)
        screen.blit(text, (tower.x * TILE_SIZE + TILE_SIZE // 2 - text.get_width() // 2, tower.y * TILE_SIZE + TILE_SIZE // 2 - text.get_height() // 2))

def draw_hud():
    pygame.draw.rect(screen, GRAY, (MAP_WIDTH * TILE_SIZE, 0, HUD_WIDTH, SCREEN_HEIGHT))
    pygame.draw.rect(screen, WHITE, (MAP_WIDTH * TILE_SIZE + 10, 10, HUD_WIDTH - 20, SCREEN_HEIGHT - 20), 2)
    text = font.render(f"Gold: {gold}", True, WHITE)
    screen.blit(text, (MAP_WIDTH * TILE_SIZE + 10, 10))
    text = font.render(f"Base Health: {base_health}", True, WHITE)
    screen.blit(text, (MAP_WIDTH * TILE_SIZE + 10, 40))
    text = font.render(f"Wave: {wave_index + 1}", True, WHITE)
    screen.blit(text, (MAP_WIDTH * TILE_SIZE + 10, 70))
    text = font.render(f"Enemies Left: {len(enemies)}", True, WHITE)
    screen.blit(text, (MAP_WIDTH * TILE_SIZE + 10, 100))
    text = font.render(f"Selected Tower: {'Arrow' if selected_tower == 0 else 'Cannon' if selected_tower == 1 else 'Slow'}", True, WHITE)
    screen.blit(text, (MAP_WIDTH * TILE_SIZE + 10, 130))
    for i, tower_type in enumerate([0, 1, 2]):
        pygame.draw.rect(screen, {
            0: ARROW_TOWER_COLOR,
            1: CANNON_TOWER_COLOR,
            2: SLOW_TOWER_COLOR
        }[tower_type], (MAP_WIDTH * TILE_SIZE + 10, 160 + i * 40, 30, 30))
        text = font.render(f"${{
            0: ARROW_TOWER_COST,
            1: CANNON_TOWER_COST,
            2: SLOW_TOWER_COST
        }[tower_type]}", True, WHITE)
        screen.blit(text, (MAP_WIDTH * TILE_SIZE + 50, 170 + i * 40))

def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(screen, ENEMY_COLORS[enemy.type], (enemy.x, enemy.y, TILE_SIZE, TILE_SIZE))

def draw_game_over(text):
    text = font.render(text, True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    text = font.render("Press R to Restart", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + text.get_height()))

def reset_game():
    global gold, base_health, wave_index, enemies, towers, game_over, selected_tower
    gold = INITIAL_GOLD
    base_health = BASE_HEALTH
    wave_index = 0
    enemies = []
    towers = []
    game_over = False
    selected_tower = 0

reset_game()

gold = INITIAL_GOLD
base_health = BASE_HEALTH
wave_index = 0
enemies = []
towers = []
game_over = False
selected_tower = 0

running = True
while running:
    screen.fill(BLACK)
    draw_grid()
    draw_hud()
    draw_enemies()

    current_time = pygame.time.get_ticks()
    if not game_over and base_health > 0 and wave_index < len(waves):
        if not enemies and current_time >= next_wave_time:
            enemies = [Enemy(enemy_info) for enemy_info in waves[wave_index]]
            next_wave_time = current_time + 3000
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        reset_game()
                    elif event.key == pygame.K_1:
                        selected_tower = 0
                    elif event.key == pygame.K_2:
                        selected_tower = 1
                    elif event.key == pygame.K_3:
                        selected_tower = 2
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    grid_x, grid_y = x // TILE_SIZE, y // TILE_SIZE
                    if 0 <= grid_x < MAP_WIDTH and 0 <= grid_y < MAP_HEIGHT and (grid_x, grid_y) not in path and (grid_x, grid_y)!= (0, 7) and not any(tower for tower in towers if tower.x == grid_x and tower.y == grid_y):
                        if event.button == 1 and gold >= {
                            0: ARROW_TOWER_COST,
                            1: CANNON_TOWER_COST,
                            2: SLOW_TOWER_COST
                        }[selected_tower]:
                            gold -= {
                                0: ARROW_TOWER_COST,
                                1: CANNON_TOWER_COST,
                                2: SLOW_TOWER_COST
                            }[selected_tower]
                            towers.append(Tower(grid_x, grid_y, selected_tower))
                        elif event.button == 3:
                            for tower in towers:
                                if tower.x == grid_x and tower.y == grid_y:
                                    tower.upgrade()
                                    break

            for tower in towers:
                tower.attack(enemies)

            for enemy in enemies[:]:
                enemy.move()
                if (enemy.x, enemy.y) == (0 * TILE_SIZE, 7 * TILE_SIZE):
                    base_health -= 1
                    enemies.remove(enemy)
                elif enemy.health <= 0:
                    gold += enemy.reward
                    enemies.remove(enemy)

            if not enemies:
                wave_index += 1
                next_wave_time = current_time + 3000

    if base_health <= 0:
        draw_game_over("Game Over")