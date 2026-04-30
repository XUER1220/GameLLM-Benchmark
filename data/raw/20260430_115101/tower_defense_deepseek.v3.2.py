import pygame
import random
import math
pygame.init()
random.seed(42)

WIDTH, HEIGHT = 800, 600
GRID_WIDTH, GRID_HEIGHT = 20, 15
TILE_SIZE = 32
MAP_WIDTH, MAP_HEIGHT = GRID_WIDTH * TILE_SIZE, GRID_HEIGHT * TILE_SIZE
HUD_WIDTH = WIDTH - MAP_WIDTH
FPS = 60
BG_COLOR = (30, 30, 40)
PATH_COLOR = (100, 80, 50)
GRASS_COLOR = (60, 120, 60)
HUD_BG_COLOR = (50, 50, 70)
TEXT_COLOR = (220, 220, 220)
RED = (220, 70, 70)
GREEN = (70, 220, 70)
BLUE = (70, 130, 220)
YELLOW = (220, 220, 70)
PURPLE = (180, 70, 220)
CYAN = (70, 220, 220)
ENTRY_COLOR = (200, 150, 100)
BASE_COLOR = (200, 100, 100)

INITIAL_GOLD = 180
BASE_HEALTH = 20
PATH = [
    (0, 7), (4, 7), (4, 3), (11, 3), (11, 10), (15, 10), (15, 5), (19, 5)
]
PATH_PIXELS = [(x * TILE_SIZE + TILE_SIZE//2, y * TILE_SIZE + TILE_SIZE//2) for x, y in PATH]
BASE_POS = (19, 5)
ENTRY_POS = (0, 7)

TOWER_TYPES = {
    1: {"name": "Arrow Tower", "cost": 50, "range": 120, "damage": 8, "cooldown": 0.8, "color": GREEN, "projectile_color": GREEN, "splash": 0},
    2: {"name": "Cannon Tower", "cost": 80, "range": 105, "damage": 14, "cooldown": 1.2, "color": RED, "projectile_color": YELLOW, "splash": 45},
    3: {"name": "Slow Tower", "cost": 70, "range": 110, "damage": 4, "cooldown": 1.0, "color": CYAN, "projectile_color": BLUE, "splash": 0}
}
UPGRADE_COST_MULT = 0.7
MAX_LEVEL = 2
UPGRADE_STATS_MULT = 1.5

WAVES = [
    {"count": 8, "spawn_delay": 1.0, "enemy_type_dist": [("normal", 1.0)]},
    {"count": 10, "spawn_delay": 0.9, "enemy_type_dist": [("normal", 0.7), ("fast", 0.3)]},
    {"count": 12, "spawn_delay": 0.8, "enemy_type_dist": [("normal", 0.5), ("fast", 0.3), ("tank", 0.2)]},
    {"count": 15, "spawn_delay": 0.7, "enemy_type_dist": [("normal", 0.4), ("fast", 0.3), ("tank", 0.3)]},
    {"count": 18, "spawn_delay": 0.6, "enemy_type_dist": [("normal", 0.3), ("fast", 0.3), ("tank", 0.4)]}
]
ENEMY_STATS = {
    "normal": {"speed": 1.2, "health": 20, "reward": 15, "color": (200, 200, 200)},
    "fast": {"speed": 2.5, "health": 10, "reward": 10, "color": (70, 200, 200)},
    "tank": {"speed": 0.8, "health": 50, "reward": 30, "color": (200, 100, 100)}
}
SLOW_DURATION = 2.0

class Enemy:
    def __init__(self, enemy_type, wave_strength):
        self.type = enemy_type
        stats = ENEMY_STATS[enemy_type]
        self.speed = stats["speed"]
        self.max_health = int(stats["health"] * wave_strength)
        self.health = self.max_health
        self.reward = stats["reward"]
        self.color = stats["color"]
        self.path_index = 0
        self.pos = list(PATH_PIXELS[0])
        self.slow_timer = 0
        self.angle = 0

    def update(self, dt):
        if self.slow_timer > 0:
            actual_speed = self.speed * 0.4
            self.slow_timer = max(0, self.slow_timer - dt)
        else:
            actual_speed = self.speed
        target = PATH_PIXELS[self.path_index]
        dx = target[0] - self.pos[0]
        dy = target[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist < actual_speed * dt * TILE_SIZE:
            self.pos = list(target)
            self.path_index += 1
            if self.path_index >= len(PATH_PIXELS):
                return True  
        else:
            self.pos[0] += (dx / dist) * actual_speed * dt * TILE_SIZE
            self.pos[1] += (dy / dist) * actual_speed * dt * TILE_SIZE
            self.angle = math.atan2(dy, dx)
        return False

    def draw(self, screen):
        radius = TILE_SIZE // 2 - 2
        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), radius)
        health_width = int((self.health / self.max_health) * (radius * 2 - 4))
        pygame.draw.rect(screen, GREEN, (int(self.pos[0]) - radius + 2, int(self.pos[1]) - radius - 6, radius * 2 - 4, 4))
        pygame.draw.rect(screen, RED, (int(self.pos[0]) - radius + 2, int(self.pos[1]) - radius - 6, health_width, 4))
        if self.slow_timer > 0:
            pygame.draw.circle(screen, BLUE, (int(self.pos[0]), int(self.pos[1])), radius, 2)

    def is_dead(self):
        return self.health <= 0

class Tower:
    def __init__(self, grid_x, grid_y, tower_type):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x * TILE_SIZE + TILE_SIZE // 2
        self.y = grid_y * TILE_SIZE + TILE_SIZE // 2
        self.type = tower_type
        self.stats = TOWER_TYPES[tower_type].copy()
        self.level = 1
        self.cooldown_timer = 0
        self.target = None
        self.projectiles = []
        self.attack_sound = None

    def update(self, dt, enemies):
        self.cooldown_timer = max(0, self.cooldown_timer - dt)
        if self.cooldown_timer > 0:
            return
        if not self.target or self.target.is_dead():
            self.target = self.find_target(enemies)
        if self.target:
            self.fire()

    def find_target(self, enemies):
        best = None
        best_dist = float('inf')
        for e in enemies:
            if e.is_dead():
                continue
            dx = e.pos[0] - self.x
            dy = e.pos[1] - self.y
            dist = math.hypot(dx, dy)
            if dist <= self.stats["range"] and dist < best_dist:
                best_dist = dist
                best = e
        return best

    def fire(self):
        if not self.target:
            return
        self.cooldown_timer = self.stats["cooldown"]
        self.projectiles.append({
            "x": self.x,
            "y": self.y,
            "target": self.target,
            "color": self.stats["projectile_color"],
            "speed": 5.0,
            "splash": self.stats["splash"]
        })

    def update_projectiles(self, dt, enemies):
        for p in self.projectiles[:]:
            if p["target"].is_dead():
                self.projectiles.remove(p)
                continue
            tx = p["target"].pos[0]
            ty = p["target"].pos[1]
            dx = tx - p["x"]
            dy = ty - p["y"]
            dist = math.hypot(dx, dy)
            if dist < p["speed"] * dt * TILE_SIZE:
                p["x"] = tx
                p["y"] = ty
            else:
                p["x"] += (dx / dist) * p["speed"] * dt * TILE_SIZE
                p["y"] += (dy / dist) * p["speed"] * dt * TILE_SIZE
            if dist < TILE_SIZE // 2:
                damage = self.stats["damage"]
                if p["splash"] > 0:
                    for e in enemies[:]:
                        edx = e.pos[0] - tx
                        edy = e.pos[1] - ty
                        if math.hypot(edx, edy) <= p["splash"]:
                            e.health -= damage
                else:
                    p["target"].health -= damage
                if self.type == 3:
                    p["target"].slow_timer = SLOW_DURATION
                self.projectiles.remove(p)

    def draw(self, screen):
        radius = TILE_SIZE // 2 - 2
        pygame.draw.circle(screen, self.stats["color"], (int(self.x), int(self.y)), radius)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), radius, 2)
        if self.level > 1:
            font = pygame.font.Font(None, 20)
            level_text = font.render(str(self.level), True, TEXT_COLOR)
            screen.blit(level_text, (int(self.x) - 5, int(self.y) - 10))

    def draw_range(self, screen):
        pygame.draw.circle(screen, (255, 255, 255, 100), (int(self.x), int(self.y)), self.stats["range"], 1)

    def upgrade(self):
        if self.level >= MAX_LEVEL:
            return False
        self.level += 1
        self.stats["damage"] = int(self.stats["damage"] * UPGRADE_STATS_MULT)
        self.stats["range"] = int(self.stats["range"] * 1.2)
        return True

    def get_upgrade_cost(self):
        return int(self.stats["cost"] * UPGRADE_COST_MULT)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tower Defense Hard")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.reset()

    def reset(self):
        self.gold = INITIAL_GOLD
        self.base_health = BASE_HEALTH
        self.wave_index = 0
        self.wave_timer = 0
        self.spawned_count = 0
        self.enemies = []
        self.towers = []
        self.selected_tower_type = 1
        self.projectiles = []
        self.game_over = False
        self.win = False
        self.wave_started = False
        self.wave_prep_time = 3.0
        self.wave_strength = 1.0 + self.wave_index * 0.2

    def can_build_at(self, grid_x, grid_y):
        if not (0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT):
            return False
        for (px, py) in PATH:
            if grid_x == px and grid_y == py:
                return False
        if grid_x == BASE_POS[0] and grid_y == BASE_POS[1]:
            return False
        if grid_x == ENTRY_POS[0] and grid_y == ENTRY_POS[1]:
            return False
        for tower in self.towers:
            if tower.grid_x == grid_x and tower.grid_y == grid_y:
                return False
        return True

    def spawn_enemy(self):
        if self.spawned_count >= WAVES[self.wave_index]["count"]:
            return
        dist = WAVES[self.wave_index]["enemy_type_dist"]
        r = random.random()
        cum = 0
        enemy_type = "normal"
        for et, prob in dist:
            cum += prob
            if r <= cum:
                enemy_type = et
                break
        self.enemies.append(Enemy(enemy_type, self.wave_strength))
        self.spawned_count += 1

    def update(self, dt):
        if self.game_over:
            return
        if not self.wave_started:
            self.wave_prep_time -= dt
            if self.wave_prep_time <= 0:
                self.wave_started = True
                self.wave_timer = 0
                self.spawned_count = 0
                self.wave_strength = 1.0 + self.wave_index * 0.2
            return
        if self.spawned_count < WAVES[self.wave_index]["count"]:
            self.wave_timer += dt
            if self.wave_timer >= WAVES[self.wave_index]["spawn_delay"]:
                self.spawn_enemy()
                self.wave_timer = 0
        for enemy in self.enemies[:]:
            if enemy.update(dt):
                self.base_health -= 1
                self.enemies.remove(enemy)
            if enemy.is_dead():
                self.gold += enemy.reward
                self.enemies.remove(enemy)
        for tower in self.towers:
            tower.update(dt, self.enemies)
            tower.update_projectiles(dt, self.enemies)
        if self.base_health <= 0:
            self.game_over = True
            self.win = False
            return
        if self.wave_started and len(self.enemies) == 0 and self.spawned_count >= WAVES[self.wave_index]["count"]:
            self.wave_index += 1
            if self.wave_index >= len(WAVES):
                self.game_over = True
                self.win = True
            else:
                self.wave_started = False
                self.wave_prep_time = 3.0

    def draw_map(self):
        self.screen.fill(BG_COLOR)
        pygame.draw.rect(self.screen, GRASS_COLOR, (0, 0, MAP_WIDTH, MAP_HEIGHT))
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                rect = (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, GRASS_COLOR, rect, 1)
        for i in range(len(PATH_PIXELS) - 1):
            pygame.draw.line(self.screen, PATH_COLOR, PATH_PIXELS[i], PATH_PIXELS[i+1], 10)
        for (px, py) in PATH:
            rect = (px * TILE_SIZE, py * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.screen, PATH_COLOR, rect)
        pygame.draw.circle(self.screen, ENTRY_COLOR, (PATH_PIXELS[0][0], PATH_PIXELS[0][1]), TILE_SIZE//2)
        pygame.draw.circle(self.screen, BASE_COLOR, (PATH_PIXELS[-1][0], PATH_PIXELS[-1][1]), TILE_SIZE//2)
        for tower in self.towers:
            tower.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for tower in self.towers:
            for proj in tower.projectiles:
                pygame.draw.circle(self.screen, proj["color"], (int(proj["x"]), int(proj["y"])), 4)

    def draw_hud(self):
        hud_x = MAP_WIDTH
        pygame.draw.rect(self.screen, HUD_BG_COLOR, (hud_x, 0, HUD_WIDTH, HEIGHT))
        y = 20
        title = self.font.render("TOWER DEFENSE", True, TEXT_COLOR)
        self.screen.blit(title, (hud_x + HUD_WIDTH//2 - title.get_width()//2, y))
        y += 40
        health_text = self.font.render(f"Base HP: {self.base_health}", True, GREEN)
        self.screen.blit(health_text, (hud_x + 10, y))
        y += 35
        gold_text = self.font.render(f"Gold: {self.gold}", True, YELLOW)
        self.screen.blit(gold_text, (hud_x + 10, y))
        y += 35
        wave_text = self.font.render(f"Wave: {self.wave_index+1}/{len(WAVES)}", True, CYAN)
        self.screen.blit(wave_text, (hud_x + 10, y))
        y += 35
        enemies_text = self.font.render(f"Enemies: {len(self.enemies)}", True, RED)
        self.screen.blit(enemies_text, (hud_x + 10, y))
        y += 50
        selected = TOWER_TYPES[self.selected_tower_type]
        tower_text = self.font.render(f"Selected:", True, TEXT_COLOR)
        self.screen.blit(tower_text, (hud_x + 10, y))
        y += 30
        tower_name = self.small_font.render(f"{selected['name']}", True, selected['color'])
        self.screen.blit(tower_name, (hud_x + 10, y))
        y += 25
        tower_cost = self.small_font.render(f"Cost: {selected['cost']}", True, TEXT_COLOR)
        self.screen.blit(tower_cost, (hud_x + 10, y))
        y += 25
        tower_stats = self.small_font.render(f"Dmg:{selected['damage']} Rng:{selected['range']}", True, TEXT_COLOR)
        self.screen.blit(tower_stats, (hud_x + 10, y))
        y += 40
        controls = [
            "Controls:",
            "1/2/3 - Select Tower",
            "Left Click - Build",
            "Right Click - Upgrade",
            "R - Restart",
            "ESC - Quit"
        ]
        for line in controls:
            text = self.small_font.render(line, True, TEXT_COLOR)
            self.screen.blit(text, (hud_x + 10, y))
            y += 25
        if not self.wave_started and not self.game_over:
            prep_text = self.font.render(f"Next wave in: {int(self.wave_prep_time)+1}", True, YELLOW)
            self.screen.blit(prep_text, (hud_x + 10, HEIGHT - 100))
        if self.game_over:
            result = "YOU WIN!" if self.win else "GAME OVER"
            color = GREEN if self.win else RED
            result_text = self.font.render(result, True, color)
            self.screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2 - 30))
            restart_text = self.font.render("Press R to Restart", True, YELLOW)
            self.screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))

    def draw_mouse_overlay(self):
        mx, my = pygame.mouse.get_pos()
        if mx < MAP_WIDTH:
            grid_x = mx // TILE_SIZE
            grid_y = my // TILE_SIZE
            if self.can_build_at(grid_x, grid_y):
                rect = (grid_x * TILE_SIZE, grid_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, (255, 255, 255, 100), rect, 3)
                tower_type = self.selected_tower_type
                range_circle = TOWER_TYPES[tower_type]["range"]
                pygame.draw.circle(self.screen, (255, 255, 255, 80), (mx, my), range_circle, 1)
            for tower in self.towers:
                dx = tower.x - mx
                dy = tower.y - my
                if math.hypot(dx, dy) < TILE_SIZE//2:
                    tower.draw_range(self.screen)
                    break

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        self.selected_tower_type = event.key - pygame.K_0
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    mx, my = pygame.mouse.get_pos()
                    if mx < MAP_WIDTH:
                        grid_x = mx // TILE_SIZE
                        grid_y = my // TILE_SIZE
                        if event.button == 1:
                            if self.can_build_at(grid_x, grid_y):
                                cost = TOWER_TYPES[self.selected_tower_type]["cost"]
                                if self.gold >= cost:
                                    self.towers.append(Tower(grid_x, grid_y, self.selected_tower_type))
                                    self.gold -= cost
                        elif event.button == 3:
                            for tower in self.towers:
                                if tower.grid_x == grid_x and tower.grid_y == grid_y:
                                    upgrade_cost = tower.get_upgrade_cost()
                                    if self.gold >= upgrade_cost and tower.level < MAX_LEVEL:
                                        if tower.upgrade():
                                            self.gold -= upgrade_cost
                                    break
            self.update(dt)
            self.draw_map()
            self.draw_hud()
            if not self.game_over:
                self.draw_mouse_overlay()
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()