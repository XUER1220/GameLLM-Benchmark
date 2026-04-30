import pygame
import sys
import random
import time

pygame.init()
random.seed(42)
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Tower Defense Hard")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

GRID_SIZE = 32
COLS = 20
ROWS = 15
MAP_WIDTH = COLS * GRID_SIZE
MAP_HEIGHT = ROWS * GRID_SIZE
HUD_WIDTH = 160

BASE_HEALTH = 20
INITIAL_GOLD = 180
WAVES = [
    {"enemies": [{"type": "normal", "count": 5}]},
    {"enemies": [{"type": "normal", "count": 7}]},
    {"enemies": [{"type": "normal", "count": 10}]},
    {"enemies": [{"type": "fast", "count": 5}, {"type": "armored", "count": 3}]},
    {"enemies": [{"type": "fast", "count": 7}, {"type": "armored", "count": 5}]}
]

TOWER_TYPES = {
    "arrow": {"cost": 50, "damage": 8, "range": 120, "rate": 0.8, "upgrade_cost": 35, "upgrades": {"damage": 2, "range": 10}},
    "cannon": {"cost": 80, "damage": 14, "range": 105, "rate": 1.2, "splash": 45, "upgrade_cost": 56, "upgrades": {"damage": 3, "range": 10}},
    "slow": {"cost": 70, "damage": 4, "range": 110, "rate": 1.0, "slow": 2, "upgrade_cost": 49, "upgrades": {"damage": 1, "range": 10}}
}

ENEMY_TYPES = {
    "normal": {"health": 10, "speed": 2, "reward": 10},
    "fast": {"health": 5, "speed": 4, "reward": 7},
    "armored": {"health": 20, "speed": 1, "reward": 15}
}

PATH = [(0, 7), (5, 7), (5, 0), (10, 0), (10, 5), (15, 5), (15, 10), (18, 10), (18, 14)]

class Tower:
    def __init__(self, x, y, tower_type):
        self.x = x
        self.y = y
        self.type = tower_type
        self.level = 1
        self.target = None
        self.last_shot = 0
        self.range = TOWER_TYPES[tower_type]["range"]
        self.damage = TOWER_TYPES[tower_type]["damage"]
        self.rate = TOWER_TYPES[tower_type]["rate"]
        self.upgrades = TOWER_TYPES[tower_type]["upgrades"]
        self.upgrade_cost = TOWER_TYPES[tower_type]["upgrade_cost"]
        self.splash = TOWER_TYPES[tower_type].get("splash", 0)
        self.slow_duration = TOWER_TYPES[tower_type].get("slow", 0)

    def upgrade(self):
        if self.level < 3 and game.gold >= self.upgrade_cost:
            self.level += 1
            game.gold -= self.upgrade_cost
            self.range += self.upgrades["range"]
            self.damage += self.upgrades["damage"]

    def attack(self, enemies):
        now = pygame.time.get_ticks() / 1000
        if now - self.last_shot >= self.rate:
            self.last_shot = now
            if self.splash > 0:
                hit_enemies = [e for e in enemies if ((e.x - self.x) ** 2 + (e.y - self.y) ** 2) ** 0.5 <= self.range + self.splash]
                for e in hit_enemies:
                    e.health -= self.damage
                    if self.slow_duration > 0:
                        e.slow_end_time = now + self.slow_duration
            else:
                self.target = min(enemies, key=lambda e: ((e.x - self.x) ** 2 + (e.y - self.y) ** 2) ** 0.5, default=None)
                if self.target and ((self.target.x - self.x) ** 2 + (self.target.y - self.y) ** 2) ** 0.5 <= self.range:
                    self.target.health -= self.damage
                    if self.slow_duration > 0:
                        self.target.slow_end_time = now + self.slow_duration

class Enemy:
    def __init__(self, enemy_type):
        self.type = enemy_type
        self.health = ENEMY_TYPES[enemy_type]["health"]
        self.speed = ENEMY_TYPES[enemy_type]["speed"]
        self.reward = ENEMY_TYPES[enemy_type]["reward"]
        self.path_index = 0
        self.x, self.y = PATH[self.path_index]
        self.slow_end_time = 0

    def move(self):
        if self.path_index < len(PATH) - 1:
            target_x, target_y = PATH[self.path_index + 1]
            dx = (target_x - self.x) * self.speed
            dy = (target_y - self.y) * self.speed
            if dx > 0:
                self.x = min(self.x + dx, target_x)
            elif dx < 0:
                self.x = max(self.x + dx, target_x)
            if dy > 0:
                self.y = min(self.y + dy, target_y)
            elif dy < 0:
                self.y = max(self.y + dy, target_y)
            if self.x == target_x and self.y == target_y:
                self.path_index += 1
        else:
            game.base_health -= 1
            game.enemies.remove(self)

class Game:
    def __init__(self):
        self.base_health = BASE_HEALTH
        self.gold = INITIAL_GOLD
        self.wave_index = 0
        self.enemies = []
        self.towers = []
        self.selected_tower_type = None
        self.game_over = False
        self.wave_start_time = 0
        self.next_enemy_time = 0
        self.enemy_interval = 1000

    def start_wave(self):
        if self.wave_index < len(WAVES):
            wave = WAVES[self.wave_index]
            for enemy_info in wave["enemies"]:
                for _ in range(enemy_info["count"]):
                    self.enemies.append(Enemy(enemy_info["type"]))
            self.wave_start_time = pygame.time.get_ticks()
            self.next_enemy_time = self.wave_start_time + self.enemy_interval
            self.wave_index += 1

    def check_game_over(self):
        if self.base_health <= 0:
            self.game_over = True
        elif self.wave_index == len(WAVES) and not self.enemies:
            self.game_over = "win"

    def draw(self):
        screen.fill(GRAY)
        for y in range(ROWS):
            for x in range(COLS):
                if (x, y) in PATH:
                    pygame.draw.rect(screen, YELLOW, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                else:
                    pygame.draw.rect(screen, WHITE, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, RED, (MAP_WIDTH, MAP_HEIGHT, GRID_SIZE, GRID_SIZE))  # Base
        pygame.draw.rect(screen, GREEN, (0, 7 * GRID_SIZE, GRID_SIZE, GRID_SIZE))  # Entrance

        for tower in self.towers:
            if tower.type == "arrow":
                color = BLUE
            elif tower.type == "cannon":
                color = PURPLE
            elif tower.type == "slow":
                color = ORANGE
            pygame.draw.rect(screen, color, (tower.x * GRID_SIZE, tower.y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            if self.selected_tower_type == tower.type:
                pygame.draw.circle(screen, GREEN, (tower.x * GRID_SIZE + GRID_SIZE // 2, tower.y * GRID_SIZE + GRID_SIZE // 2), tower.range, 1)

        for enemy in self.enemies:
            if enemy.type == "normal":
                color = RED
            elif enemy.type == "fast":
                color = GREEN
            elif enemy.type == "armored":
                color = BLUE
            pygame.draw.rect(screen, color, (enemy.x * GRID_SIZE, enemy.y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        pygame.draw.rect(screen, BLACK, (MAP_WIDTH, 0, HUD_WIDTH, MAP_HEIGHT))
        health_text = font.render(f"Base Health: {self.base_health}", True, WHITE)
        gold_text = font.render(f"Gold: {self.gold}", True, WHITE)
        wave_text = font.render(f"Wave: {self.wave_index}", True, WHITE)
        enemies_left_text = font.render(f"Enemies Left: {len(self.enemies)}", True, WHITE)
        selected_tower_text = font.render(f"Selected Tower: {self.selected_tower_type.capitalize() if self.selected_tower_type else 'None'}", True, WHITE)
        screen.blit(health_text, (MAP_WIDTH + 10, 10))
        screen.blit(gold_text, (MAP_WIDTH + 10, 50))
        screen.blit(wave_text, (MAP_WIDTH + 10, 90))
        screen.blit(enemies_left_text, (MAP_WIDTH + 10, 130))
        screen.blit(selected_tower_text, (MAP_WIDTH + 10, 170))

        if self.game_over:
            if self.game_over == "win":
                end_text = font.render("You Win", True, WHITE)
            else:
                end_text = font.render("Game Over", True, WHITE)
            screen.blit(end_text, (MAP_WIDTH + 10, 210))
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(restart_text, (MAP_WIDTH + 10, 250))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.__init__()
                        self.run()
                    elif event.key == pygame.K_1:
                        self.selected_tower_type = "arrow"
                    elif event.key == pygame.K_2:
                        self.selected_tower_type = "cannon"
                    elif event.key == pygame.K_3:
                        self.selected_tower_type = "slow"
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    x, y = event.pos
                    if x < MAP_WIDTH and y < MAP_HEIGHT:
                        grid_x, grid_y = x // GRID_SIZE, y // GRID_SIZE
                        if (grid_x, grid_y) not in PATH and (grid_x, grid_y)!= (19, 14) and not any(tower for tower in self.towers if tower.x == grid_x and tower.y == grid_y):
                            if event.button == 1 and self.selected_tower_type and self.gold >= TOWER_TYPES[self.selected_tower_type]["cost"]:
                                self.towers.append(Tower(grid_x, grid_y, self.selected_tower_type))
                                self.gold -= TOWER_TYPES[self.selected_tower_type]["cost"]
                            elif event.button == 3:
                                for tower in self.towers:
                                    if tower.x == grid_x and tower.y == grid_y:
                                        tower.upgrade()
                                        break

            now = pygame.time.get_ticks()
            if not self.game_over and now - self.wave_start_time > 3000 and not self.enemies:
                self.start_wave()

            if not self.game_over:
                for tower in self.towers:
                    tower.attack(self.enemies)

                for enemy in self.enemies:
                    enemy.move()

                if now > self.next_enemy_time and self.wave_index < len(WAVES):
                    if self.enemies.count(Enemy) < WAVES[self.wave_index]["enemies"][0]["count"]:
                        self.enemies.append(Enemy(WAVES[self.wave_index]["enemies"][0]["type"]))
                        self.next_enemy_time = now + self.enemy_interval

                self.enemies = [e for e in self.enemies if e.health > 0]

            self.check_game_over()
            self.draw()
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()

game = Game()
game.run()