import pygame
import random
import math

pygame.init()
random.seed(42)

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_SIZE = 32
GRID_COLS, GRID_ROWS = 20, 15
MAP_WIDTH, MAP_HEIGHT = GRID_COLS * GRID_SIZE, GRID_ROWS * GRID_SIZE
HUD_WIDTH = 160
FPS = 60

# Colors
BACKGROUND = (30, 45, 30)
PATH_COLOR = (120, 80, 50)
GRASS_COLOR = (40, 120, 40)
ENTRY_COLOR = (200, 100, 100)
BASE_COLOR = (120, 40, 40)
HUD_BG = (20, 20, 30)
HUD_TEXT = (255, 255, 200)
TOWER_SELECT_BG = (40, 40, 60)
TOWER_SELECT_HIGHLIGHT = (80, 150, 250)
RED = (255, 80, 80)
GREEN = (80, 255, 80)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 100)
PURPLE = (200, 80, 200)
ORANGE = (255, 150, 50)
CYAN = (80, 220, 220)
WHITE = (255, 255, 255)
BLACK = (0, 0,104857600)

# Game constants
INITIAL_GOLD = 180
INITIAL_BASE_HP = 20
PREPARE_TIME = 3  # seconds between waves

# Tower constants
TOWER_TYPES = 3
ARROW_TOWER = 0
CANNON_TOWER = 1
SLOW_TOWER = 2
TOWER_NAMES = ["Arrow", "Cannon", "Slow"]
TOWER_COLORS = [GREEN, RED, BLUE]
TOWER_COSTS = [50, 80, 70]
TOWER_RANGES = [120, 105, 110]
TOWER_DAMAGES = [8, 14, 4]
TOWER_RATES = [0.8, 1.2, 1.0]  # seconds between shots
UPGRADE_COST_MULT = 0.7
MAX_UPGRADE = 2
UPGRADE_BONUS_RANGE = 15
UPGRADE_BONUS_DAMAGE_MULT = 1.5
CANNON_SPLASH_RADIUS = 45
SLOW_DURATION = 2.0  # seconds

# Enemy constants
ENEMY_TYPES = 3
NORMAL = 0
FAST = 1
ARMORED = 2
ENEMY_NAMES = ["Normal", "Fast", "Armored"]
ENEMY_COLORS = [(150, 150, 150), (200, 200, 100), (100, 100, 200)]
ENEMY_SPEEDS = [0.8, 1.6, 0.6]
ENEMY_HP = [30, 20, 60]
ENEMY_REWARDS = [15, 10, 25]

# Waves: list of (enemy_type, count, spawn_delay)
WAVES = [
    [(NORMAL, 8, 1.0)],
    [(NORMAL, 10, 0.9), (FAST, 5, 1.2)],
    [(NORMAL, 12, 0.8), (FAST, 8, 1.0), (ARMORED, 3, 2.0)],
    [(FAST, 15, 0.7), (ARMORED, 6, 1.5)],
    [(NORMAL, 20, 0.6), (FAST, 10, 0.8), (ARMORED, 10, 1.2)],
]

# Fixed path tiles (col, row) in grid coordinates
PATH_TILES = [
    (0, 7), (1, 7), (2, 7), (3, 7), (4, 7),
    (4, 8), (4, 9), (4, 10),
    (5, 10), (6, 10), (7, 10),
    (7, 9), (7, 8), (7, 7),
    (8, 7), (9, 7), (10, 7),
    (10, 8), (10, 9), (10, 10),
    (11, 10), (12, 10), (13, 10),
    (13, 9), (13, 8), (13, 7),
    (14, 7), (15, 7), (16, 7),
    (16, 8), (16, 9), (16, 10),
    (17, 10), (18, 10), (19, 10),
]
ENTRY_TILE = (0, 7)
BASE_TILE = (19, 10)

# Convert grid to pixel positions (center)
def grid_to_pixel(col, row):
    return (col * GRID_SIZE + GRID_SIZE // 2, row * GRID_SIZE + GRID_SIZE // 2)

# Precompute path points (pixel centers) for enemies to follow
PATH_POINTS = [grid_to_pixel(col, row) for col, row in PATH_TILES]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Tower Defense Hard")

class Enemy:
    def __init__(self, enemy_type):
        self.type = enemy_type
        self.pos = list(PATH_POINTS[0])
        self.target_index = 1
        self.speed = ENEMY_SPEEDS[enemy_type]
        self.max_hp = ENEMY_HP[enemy_type]
        self.hp = self.max_hp
        self.reward = ENEMY_REWARDS[enemy_type]
        self.slow_timer = 0.0
        self.alive = True
        self.reached_base = False

    def update(self, dt):
        if self.reached_base or not self.alive:
            return
        effective_speed = self.speed
        if self.slow_timer > 0:
            effective_speed *= 0.4
            self.slow_timer -= dt
        target = PATH_POINTS[self.target_index]
        dx = target[0] - self.pos[0]
        dy = target[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist < effective_speed * dt * 60:
            self.pos = list(target)
            self.target_index += 1
            if self.target_index >= len(PATH_POINTS):
                self.reached_base = True
        else:
            self.pos[0] += dx / dist * effective_speed * dt * 60
            self.pos[1] += dy / dist * effective_speed * dt * 60

    def draw(self, screen):
        if not self.alive:
            return
        radius = 12
        pygame.draw.circle(screen, ENEMY_COLORS[self.type], (int(self.pos[0]), int(self.pos[1])), radius)
        # HP bar
        bar_width = 30
        bar_height = 4
        x = int(self.pos[0] - bar_width // 2)
        y = int(self.pos[1] - radius - 8)
        pygame.draw.rect(screen, RED, (x, y, bar_width, bar_height))
        green_width = int(bar_width * self.hp / self.max_hp)
        pygame.draw.rect(screen, GREEN, (x, y, green_width, bar_height))
        if self.slow_timer > 0:
            pygame.draw.circle(screen, CYAN, (int(self.pos[0]), int(self.pos[1])), radius, 2)

    def take_damage(self, damage, is_slow=False):
        self.hp -= damage
        if is_slow:
            self.slow_timer = SLOW_DURATION
        if self.hp <= 0:
            self.alive = False
            return self.reward
        return 0

class Tower:
    def __init__(self, tower_type, col, row):
        self.type = tower_type
        self.col = col
        self.row = row
        self.x, self.y = grid_to_pixel(col, row)
        self.level = 0
        self.cooldown = 0.0
        self.range = TOWER_RANGES[tower_type]
        self.damage = TOWER_DAMAGES[tower_type]
        self.rate = TOWER_RATES[tower_type]
        self.projectiles = []
        
    def upgrade(self):
        if self.level < MAX_UPGRADE:
            self.level += 1
            self.range += UPGRADE_BONUS_RANGE
            self.damage = int(self.damage * UPGRADE_BONUS_DAMAGE_MULT)

    def update(self, dt, enemies):
        self.cooldown -= dt
        if self.cooldown > 0:
            return
        target = None
        best_dist = float('inf')
        for enemy in enemies:
            if enemy.alive and not enemy.reached_base:
                dist = math.hypot(enemy.pos[0] - self.x, enemy.pos[1] - self.y)
                if dist <= self.range and dist < best_dist:
                    best_dist = dist
                    target = enemy
        if target:
            self.cooldown = self.rate
            if self.type == CANNON_TOWER:
                # splash damage
                splash_enemies = []
                for enemy in enemies:
                    if enemy.alive and not enemy.reached_base:
                        dist = math.hypot(enemy.pos[0] - target.pos[0], enemy.pos[1] - target.pos[1])
                        if dist <= CANNON_SPLASH_RADIUS:
                            splash_enemies.append(enemy)
                for enemy in splash_enemies:
                    reward = enemy.take_damage(self.damage)
                    if reward:
                        return reward
            else:
                reward = target.take_damage(self.damage, is_slow=(self.type == SLOW_TOWER))
                if reward:
                    return reward
            # create projectile visual
            self.projectiles.append([list([self.x, self.y]), list(target.pos), 0.0])
        return 0

    def draw(self, screen):
        radius = 14
        color = TOWER_COLORS[self.type]
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), radius, 2)
        # draw level indicator
        if self.level > 0:
            font = pygame.font.Font(None, 20)
            level_text = font.render(str(self.level), True, YELLOW)
            screen.blit(level_text, (int(self.x) - 5, int(self.y) - 25))
        # draw projectiles
        for proj in self.projectiles[:]:
            start, end, t = proj
            t += 0.05
            if t >= 1.0:
                self.projectiles.remove(proj)
                continue
            px = start[0] + (end[0] - start[0]) * t
            py = start[1] + (end[1] - start[1]) * t
            proj[2] = t
            if self.type == ARROW_TOWER:
                pygame.draw.line(screen, GREEN, (int(start[0]), int(start[1])), (int(px), int(py)), 3)
                pygame.draw.circle(screen, YELLOW, (int(px), int(py)), 4)
            elif self.type == CANNON_TOWER:
                pygame.draw.circle(screen, ORANGE, (int(px), int(py)), 6)
            else:
                pygame.draw.line(screen, CYAN, (int(start[0]), int(start[1])), (int(px), int(py)), 2)

class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.gold = INITIAL_GOLD
        self.base_hp = INITIAL_BASE_HP
        self.wave = 0
        self.wave_enemies = []
        self.enemies = []
        self.towers = []
        self.selected_tower_type = ARROW_TOWER
        self.game_over = False
        self.victory = False
        self.prepare_timer = PREPARE_TIME
        self.spawn_timer = 0.0
        self.spawn_index = 0
        self.wave_spawn_list = []

    def can_build_tower(self, col, row):
        if not (0 <= col < GRID_COLS and 0 <= row < GRID_ROWS):
            return False
        if (col, row) in PATH_TILES:
            return False
        if (col, row) == ENTRY_TILE or (col, row) == BASE_TILE:
            return False
        for tower in self.towers:
            if tower.col == col and tower.row == row:
                return False
        return True

    def build_tower(self, col, row):
        if not self.can_build_tower(col, row):
            return False
        cost = TOWER_COSTS[self.selected_tower_type]
        if self.gold < cost:
            return False
        self.gold -= cost
        self.towers.append(Tower(self.selected_tower_type, col, row))
        return True

    def upgrade_tower(self, col, row):
        for tower in self.towers:
            if tower.col == col and tower.row == row and tower.level < MAX_UPGRADE:
                cost = int(TOWER_COSTS[tower.type] * UPGRADE_COST_MULT)
                if self.gold >= cost:
                    self.gold -= cost
                    tower.upgrade()
                    return True
        return False

    def start_wave(self):
        if self.wave >= len(WAVES):
            return
        self.wave_spawn_list = []
        for enemy_type, count, spawn_delay in WAVES[self.wave]:
            for _ in range(count):
                self.wave_spawn_list.append((enemy_type, spawn_delay))
        self.spawn_index = 0
        self.spawn_timer = 0.0

    def update(self, dt):
        if self.game_over:
            return
        # wave progression
        if self.wave >= len(WAVES):
            if not self.enemies and all(e.reached_base or not e.alive for e in self.wave_enemies):
                self.victory = True
                self.game_over = True
            return
        if self.prepare_timer > 0:
            self.prepare_timer -= dt
            if self.prepare_timer <= 0:
                self.start_wave()
        else:
            # spawning enemies
            if self.spawn_index < len(self.wave_spawn_list):
                self.spawn_timer -= dt
                if self.spawn_timer <= 0:
                    enemy_type, next_delay = self.wave_spawn_list[self.spawn_index]
                    self.enemies.append(Enemy(enemy_type))
                    self.wave_enemies.append(self.enemies[-1])
                    self.spawn_index += 1
                    self.spawn_timer = next_delay
            # update enemies
            for enemy in self.enemies[:]:
                enemy.update(dt)
                if enemy.reached_base:
                    self.base_hp -= 1
                    self.enemies.remove(enemy)
                    if self.base_hp <= 0:
                        self.game_over = True
                        self.victory = False
                elif not enemy.alive:
                    self.enemies.remove(enemy)
            # update towers
            for tower in self.towers:
                reward = tower.update(dt, self.enemies)
                self.gold += reward
            # check wave finished
            if not self.enemies and self.spawn_index >= len(self.wave_spawn_list):
                if self.wave < len(WAVES) - 1:
                    self.wave += 1
                    self.prepare_timer = PREPARE_TIME
                else:
                    self.wave += 1  # move past last wave

    def draw(self, screen):
        screen.fill(BACKGROUND)
        # draw map grid
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS):
                rect = (col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, GRASS_COLOR, rect, 0)
                pygame.draw.rect(screen, (60, 80, 60), rect, 1)
        # draw path
        for col, row in PATH_TILES:
            rect = (col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, PATH_COLOR, rect)
            pygame.draw.rect(screen, (90, 60, 30), rect, 1)
        # draw entry
        ex, ey = grid_to_pixel(*ENTRY_TILE)
        pygame.draw.circle(screen, ENTRY_COLOR, (ex, ey), 20)
        # draw base
        bx, by = grid_to_pixel(*BASE_TILE)
        pygame.draw.circle(screen, BASE_COLOR, (bx, by), 24)
        # draw towers
        for tower in self.towers:
            tower.draw(screen)
        # draw enemies
        for enemy in self.enemies:
            enemy.draw(screen)
        # draw HUD background
        pygame.draw.rect(screen, HUD_BG, (MAP_WIDTH, 0, HUD_WIDTH, SCREEN_HEIGHT))
        # draw tower selection
        tower_x = MAP_WIDTH + 10
        for i in range(TOWER_TYPES):
            ty = 20 + i * 80
            color = TOWER_COLORS[i]
            if self.selected_tower_type == i:
                pygame.draw.rect(screen, TOWER_SELECT_HIGHLIGHT, (tower_x - 5, ty - 5, HUD_WIDTH - 10, 70), 3)
            pygame.draw.rect(screen, TOWER_SELECT_BG, (tower_x, ty, HUD_WIDTH - 20, 60))
            pygame.draw.circle(screen, color, (tower_x + 30, ty + 30), 20)
            font = pygame.font.Font(None, 24)
            name_text = font.render(TOWER_NAMES[i], True, HUD_TEXT)
            screen.blit(name_text, (tower_x + 60, ty + 10))
            cost_text = font.render(f"${TOWER_COSTS[i]}", True, YELLOW)
            screen.blit(cost_text, (tower_x + 60, ty + 35))
        # draw game stats
        font = pygame.font.Font(None, 28)
        stats_y = 300
        screen.blit(font.render(f"Gold: {self.gold}", True, YELLOW), (MAP_WIDTH + 10, stats_y))
        screen.blit(font.render(f"Base HP: {self.base_hp}", True, RED if self.base_hp < 10 else GREEN), (MAP_WIDTH + 10, stats_y + 40))
        screen.blit(font.render(f"Wave: {self.wave+1}/{len(WAVES)}", True, CYAN), (MAP_WIDTH + 10, stats_y + 80))
        screen.blit(font.render(f"Enemies: {len(self.enemies)}", True, PURPLE), (MAP_WIDTH + 10, stats_y + 120))
        screen.blit(font.render(f"Selected:", True, WHITE), (MAP_WIDTH + 10, stats_y + 160))
        screen.blit(font.render(TOWER_NAMES[self.selected_tower_type], True, TOWER_COLORS[self.selected_tower_type]), (MAP_WIDTH + 10, stats_y + 190))
        # draw prepare timer
        if self.prepare_timer > 0:
            font = pygame.font.Font(None, 36)
            timer_text = font.render(f"Next wave: {int(self.prepare_timer)+1}", True, ORANGE)
            screen.blit(timer_text, (MAP_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
        # draw game over message
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0,1558544000, 150))
            screen.blit(overlay, (0, 0))
            font = pygame.font.Font(None, 64)
            if self.victory:
                msg = font.render("YOU WIN!", True, GREEN)
            else:
                msg = font.render("GAME OVER", True, RED)
            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            font = pygame.font.Font(None, 36)
            restart_msg = font.render("Press R to Restart", True, YELLOW)
            screen.blit(restart_msg, (SCREEN_WIDTH // 2 - restart_msg.get_width() // 2, SCREEN_HEIGHT // 2 + 30))
            wave_msg = font.render(f"Wave reached: {min(self.wave+1, len(WAVES))}", True, CYAN)
            screen.blit(wave_msg, (SCREEN_WIDTH // 2 - wave_msg.get_width() // 2, SCREEN_HEIGHT // 2 + 80))
        # draw range preview on hover
        mouse_pos = pygame.mouse.get_pos()
        col = mouse_pos[0] // GRID_SIZE
        row = mouse_pos[1] // GRID_SIZE
        if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
            if self.can_build_tower(col, row):
                pygame.draw.rect(screen, (255, 255, 255, 100), (col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE), 2)
                tx, ty = grid_to_pixel(col, row)
                pygame.draw.circle(screen, (255, 255, 255, 50), (tx, ty), TOWER_RANGES[self.selected_tower_type], 1)

def main():
    game = Game()
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game.reset()
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    game.selected_tower_type = event.key - pygame.K_1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game.game_over:
                    continue
                mx, my = pygame.mouse.get_pos()
                if mx < MAP_WIDTH:
                    col = mx // GRID_SIZE
                    row = my // GRID_SIZE
                    if event.button == 1:  # left click: build
                        game.build_tower(col, row)
                    elif event.button == 3:  # right click: upgrade
                        game.upgrade_tower(col, row)
        # update
        game.update(dt)
        # draw
        game.draw(screen)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()