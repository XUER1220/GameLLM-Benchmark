import pygame
import random
import math

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_WIDTH = 20
GRID_HEIGHT = 15
TILE_SIZE = 32
MAP_WIDTH = GRID_WIDTH * TILE_SIZE
MAP_HEIGHT = GRID_HEIGHT * TILE_SIZE
HUD_WIDTH = SCREEN_WIDTH - MAP_WIDTH
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GROUND_COLOR = (90, 160, 90)
PATH_COLOR = (120, 80, 60)
ENTRANCE_COLOR = (200, 120, 80)
BASE_COLOR = (180, 60, 60)
HUD_BG = (40, 40, 60)
HUD_TEXT = (220, 220, 250)
TOWER_COLORS = [(30, 180, 30), (200, 100, 30), (100, 100, 220)]
ENEMY_COLORS = [(150, 150, 150), (220, 220, 100), (180, 80, 80)]
BULLET_COLOR = (255, 255, 200)
RANGE_COLOR = (255, 255, 255, 100)
SLOW_EFFECT_COLOR = (100, 150, 255)
WAVE_PREP_TIME = 3
INITIAL_COINS = 180
BASE_HEALTH = 20
TOWER_COSTS = [50, 80, 70]
TOWER_NAMES = ["Arrow Tower", "Cannon Tower", "Slow Tower"]
TOWER_RANGES = [120, 105, 110]
TOWER_DAMAGES = [8, 14, 4]
TOWER_RATES = [0.8, 1.2, 1.0]
TOWER_SPLASH = [0, 45, 0]
TOWER_SLOW = [0, 0, 2.0]
UPGRADE_COST_RATIO = 0.7
MAX_UPGRADE_LEVEL = 2
ENEMY_TYPES = [
    {"health": 20, "speed": 0.8, "reward": 10, "color": ENEMY_COLORS[0]},
    {"health": 15, "speed": 1.5, "reward": 15, "color": ENEMY_COLORS[1]},
    {"health": 50, "speed": 0.5, "reward": 25, "color": ENEMY_COLORS[2]}
]
WAVES = [
    [{"type": 0, "count": 5, "spawn_delay": 1.0}],
    [{"type": 0, "count": 8, "spawn_delay": 0.8}, {"type": 1, "count": 2, "spawn_delay": 1.5}],
    [{"type": 0, "count": 10, "spawn_delay": 0.7}, {"type": 1, "count": 5, "spawn_delay": 1.2}, {"type": 2, "count": 1, "spawn_delay": 3.0}],
    [{"type": 1, "count": 8, "spawn_delay": 0.6}, {"type": 2, "count": 3, "spawn_delay": 2.5}],
    [{"type": 0, "count": 12, "spawn_delay": 0.5}, {"type": 2, "count": 5, "spawn_delay": 2.0}]
]
PATH_POINTS = [(0, 7), (5, 7), (5, 3), (12, 3), (12, 10), (19, 10)]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense Hard")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 48)

class Enemy:
    def __init__(self, enemy_type):
        self.type = enemy_type
        self.health = ENEMY_TYPES[enemy_type]["health"]
        self.max_health = self.health
        self.speed = ENEMY_TYPES[enemy_type]["speed"]
        self.reward = ENEMY_TYPES[enemy_type]["reward"]
        self.color = ENEMY_TYPES[enemy_type]["color"]
        self.path_index = 0
        self.pos = [PATH_POINTS[0][0] * TILE_SIZE + TILE_SIZE // 2, PATH_POINTS[0][1] * TILE_SIZE + TILE_SIZE // 2]
        self.slow_timer = 0

    def update(self, dt):
        if self.slow_timer > 0:
            actual_speed = self.speed * 0.4
            self.slow_timer -= dt
        else:
            actual_speed = self.speed
        target = PATH_POINTS[self.path_index + 1] if self.path_index + 1 < len(PATH_POINTS) else None
        if target:
            tx = target[0] * TILE_SIZE + TILE_SIZE // 2
            ty = target[1] * TILE_SIZE + TILE_SIZE // 2
            dx = tx - self.pos[0]
            dy = ty - self.pos[1]
            dist = math.hypot(dx, dy)
            if dist < actual_speed * dt:
                self.path_index += 1
                self.pos[0] = tx
                self.pos[1] = ty
            else:
                self.pos[0] += dx / dist * actual_speed * dt
                self.pos[1] += dy / dist * actual_speed * dt
        return self.path_index >= len(PATH_POINTS) - 1

    def draw(self, surface):
        radius = TILE_SIZE // 2 - 2
        pygame.draw.circle(surface, self.color, (int(self.pos[0]), int(self.pos[1])), radius)
        pygame.draw.circle(surface, BLACK, (int(self.pos[0]), int(self.pos[1])), radius, 1)
        if self.health < self.max_health:
            bar_width = 30
            bar_height = 4
            health_ratio = self.health / self.max_health
            pygame.draw.rect(surface, (255, 50, 50), (self.pos[0] - bar_width // 2, self.pos[1] - radius - 8, bar_width, bar_height))
            pygame.draw.rect(surface, (50, 255, 50), (self.pos[0] - bar_width // 2, self.pos[1] - radius - 8, int(bar_width * health_ratio), bar_height))

class Tower:
    def __init__(self, tower_type, grid_x, grid_y):
        self.type = tower_type
        self.level = 0
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x * TILE_SIZE + TILE_SIZE // 2
        self.y = grid_y * TILE_SIZE + TILE_SIZE // 2
        self.range = TOWER_RANGES[tower_type]
        self.damage = TOWER_DAMAGES[tower_type]
        self.fire_rate = TOWER_RATES[tower_type]
        self.splash = TOWER_SPLASH[tower_type]
        self.slow_duration = TOWER_SLOW[tower_type]
        self.fire_timer = 0
        self.target = None
        self.bullets = []

    def update(self, dt, enemies):
        self.fire_timer -= dt
        self.target = None
        if self.fire_timer <= 0:
            best_dist = self.range
            for e in enemies:
                dx = e.pos[0] - self.x
                dy = e.pos[1] - self.y
                dist = math.hypot(dx, dy)
                if dist < best_dist:
                    best_dist = dist
                    self.target = e
            if self.target:
                self.fire_timer = self.fire_rate
                self.bullets.append([self.x, self.y, self.target, 500])
        new_bullets = []
        for b in self.bullets:
            bx, by, target, speed = b
            if target.health <= 0:
                continue
            dx = target.pos[0] - bx
            dy = target.pos[1] - by
            dist = math.hypot(dx, dy)
            if dist < speed * dt:
                if self.splash > 0:
                    for e in enemies:
                        edx = e.pos[0] - target.pos[0]
                        edy = e.pos[1] - target.pos[1]
                        if math.hypot(edx, edy) <= self.splash:
                            e.health -= self.damage
                            if self.slow_duration > 0:
                                e.slow_timer = self.slow_duration
                else:
                    target.health -= self.damage
                    if self.slow_duration > 0:
                        target.slow_timer = self.slow_duration
            else:
                bx += dx / dist * speed * dt
                by += dy / dist * speed * dt
                new_bullets.append([bx, by, target, speed])
        self.bullets = new_bullets

    def draw(self, surface):
        color = TOWER_COLORS[self.type]
        radius = TILE_SIZE // 2 - 2
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), radius)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), radius, 1)
        if self.level > 0:
            level_text = font.render(str(self.level), True, WHITE)
            surface.blit(level_text, (self.x - level_text.get_width() // 2, self.y - level_text.get_height() // 2))
        for b in self.bullets:
            pygame.draw.circle(surface, BULLET_COLOR, (int(b[0]), int(b[1])), 3)

    def upgrade(self):
        if self.level < MAX_UPGRADE_LEVEL:
            self.level += 1
            self.range *= 1.2
            self.damage *= 1.4
            self.fire_rate *= 0.9
            if self.splash > 0:
                self.splash *= 1.3

    def get_upgrade_cost(self):
        return int(TOWER_COSTS[self.type] * UPGRADE_COST_RATIO)

class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.coins = INITIAL_COINS
        self.base_health = BASE_HEALTH
        self.wave_index = 0
        self.wave_timer = WAVE_PREP_TIME
        self.spawn_timers = []
        self.enemies = []
        self.towers = []
        self.selected_tower_type = 0
        self.game_state = "playing"
        self.wave_enemies_total = 0
        self.wave_enemies_spawned = 0
        self.wave_enemies_defeated = 0
        self.prepare_next_wave()

    def prepare_next_wave(self):
        if self.wave_index >= len(WAVES):
            self.game_state = "win"
            return
        wave_data = WAVES[self.wave_index]
        self.spawn_timers = []
        self.wave_enemies_total = sum(g["count"] for g in wave_data)
        self.wave_enemies_spawned = 0
        self.wave_enemies_defeated = 0
        for group in wave_data:
            for i in range(group["count"]):
                self.spawn_timers.append((group["type"], i * group["spawn_delay"]))

    def update(self, dt):
        if self.game_state != "playing":
            return
        if self.base_health <= 0:
            self.game_state = "lose"
            return
        self.wave_timer -= dt
        if self.wave_timer > 0:
            return
        if self.wave_enemies_spawned < len(self.spawn_timers):
            for i, (enemy_type, delay) in enumerate(self.spawn_timers):
                if delay <= 0 and delay is not None:
                    self.enemies.append(Enemy(enemy_type))
                    self.spawn_timers[i] = (enemy_type, None)
                    self.wave_enemies_spawned += 1
                elif delay is not None:
                    self.spawn_timers[i] = (enemy_type, delay - dt)
        new_enemies = []
        for e in self.enemies:
            reached = e.update(dt)
            if reached:
                self.base_health -= 1
            elif e.health > 0:
                new_enemies.append(e)
            else:
                self.coins += e.reward
                self.wave_enemies_defeated += 1
        self.enemies = new_enemies
        for t in self.towers:
            t.update(dt, self.enemies)
        if self.wave_enemies_spawned >= len(self.spawn_timers) and len(self.enemies) == 0:
            if self.wave_index < len(WAVES) - 1:
                self.wave_index += 1
                self.wave_timer = WAVE_PREP_TIME
                self.prepare_next_wave()
            else:
                if self.base_health > 0:
                    self.game_state = "win"

    def draw(self, surface):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = GROUND_COLOR
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if self.is_path(x, y):
                    color = PATH_COLOR
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, BLACK, rect, 1)
        pygame.draw.rect(surface, ENTRANCE_COLOR, (0, 7 * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(surface, BASE_COLOR, ((GRID_WIDTH - 1) * TILE_SIZE, 10 * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        for i in range(len(PATH_POINTS) - 1):
            start = (PATH_POINTS[i][0] * TILE_SIZE + TILE_SIZE // 2, PATH_POINTS[i][1] * TILE_SIZE + TILE_SIZE // 2)
            end = (PATH_POINTS[i + 1][0] * TILE_SIZE + TILE_SIZE // 2, PATH_POINTS[i + 1][1] * TILE_SIZE + TILE_SIZE // 2)
            pygame.draw.line(surface, (200, 200, 100), start, end, 4)
        for e in self.enemies:
            e.draw(surface)
        for t in self.towers:
            t.draw(surface)
        pygame.draw.rect(surface, HUD_BG, (MAP_WIDTH, 0, HUD_WIDTH, SCREEN_HEIGHT))
        y_offset = 10
        texts = [
            f"Base Health: {self.base_health}",
            f"Coins: {self.coins}",
            f"Wave: {self.wave_index + 1}/{len(WAVES)}",
            f"Enemies Left: {self.wave_enemies_total - self.wave_enemies_defeated}",
            f"Selected: {TOWER_NAMES[self.selected_tower_type]}",
            f"Cost: {TOWER_COSTS[self.selected_tower_type]}"
        ]
        for text in texts:
            rendered = font.render(text, True, HUD_TEXT)
            surface.blit(rendered, (MAP_WIDTH + 10, y_offset))
            y_offset += 30
        y_offset += 10
        for i in range(3):
            color = TOWER_COLORS[i]
            pygame.draw.rect(surface, color, (MAP_WIDTH + 10, y_offset, 20, 20))
            pygame.draw.rect(surface, BLACK, (MAP_WIDTH + 10, y_offset, 20, 20), 1)
            info = font.render(f"{i + 1}: {TOWER_NAMES[i]}", True, HUD_TEXT)
            surface.blit(info, (MAP_WIDTH + 40, y_offset))
            y_offset += 30
        if self.game_state == "win":
            win_text = big_font.render("You Win!", True, (50, 255, 100))
            surface.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            restart_text = font.render("Press R to Restart", True, HUD_TEXT)
            surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        elif self.game_state == "lose":
            lose_text = big_font.render("Game Over", True, (255, 50, 50))
            surface.blit(lose_text, (SCREEN_WIDTH // 2 - lose_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            restart_text = font.render("Press R to Restart", True, HUD_TEXT)
            surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

    def is_path(self, grid_x, grid_y):
        for point in PATH_POINTS:
            if point[0] == grid_x and point[1] == grid_y:
                return True
        return False

    def can_build_tower(self, grid_x, grid_y):
        if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y < 0 or grid_y >= GRID_HEIGHT:
            return False
        if self.is_path(grid_x, grid_y):
            return False
        if (grid_x == 0 and grid_y == 7) or (grid_x == GRID_WIDTH - 1 and grid_y == 10):
            return False
        for t in self.towers:
            if t.grid_x == grid_x and t.grid_y == grid_y:
                return False
        return True

    def build_tower(self, grid_x, grid_y):
        if not self.can_build_tower(grid_x, grid_y):
            return False
        cost = TOWER_COSTS[self.selected_tower_type]
        if self.coins >= cost:
            self.towers.append(Tower(self.selected_tower_type, grid_x, grid_y))
            self.coins -= cost
            return True
        return False

    def upgrade_tower(self, grid_x, grid_y):
        for t in self.towers:
            if t.grid_x == grid_x and t.grid_y == grid_y:
                cost = t.get_upgrade_cost()
                if self.coins >= cost and t.level < MAX_UPGRADE_LEVEL:
                    t.upgrade()
                    self.coins -= cost
                    return True
        return False

def main():
    game = Game()
    running = True
    mouse_held = False
    show_range = False
    range_pos = None
    while running:
        dt = clock.tick(FPS) / 1000.0
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
                if event.button == 1:
                    mouse_held = True
                    pos = pygame.mouse.get_pos()
                    if pos[0] < MAP_WIDTH and pos[1] < MAP_HEIGHT:
                        grid_x = pos[0] // TILE_SIZE
                        grid_y = pos[1] // TILE_SIZE
                        game.build_tower(grid_x, grid_y)
                elif event.button == 3:
                    pos = pygame.mouse.get_pos()
                    if pos[0] < MAP_WIDTH and pos[1] < MAP_HEIGHT:
                        grid_x = pos[0] // TILE_SIZE
                        grid_y = pos[1] // TILE_SIZE
                        game.upgrade_tower(grid_x, grid_y)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_held = False
        mouse_pos = pygame.mouse.get_pos()
        show_range = mouse_pos[0] < MAP_WIDTH and mouse_pos[1] < MAP_HEIGHT
        if show_range:
            range_pos = (mouse_pos[0], mouse_pos[1])
        game.update(dt)
        screen.fill(BLACK)
        game.draw(screen)
        if show_range and range_pos:
            range_surf = pygame.Surface((TOWER_RANGES[game.selected_tower_type] * 2, TOWER_RANGES[game.selected_tower_type] * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surf, RANGE_COLOR, (TOWER_RANGES[game.selected_tower_type], TOWER_RANGES[game.selected_tower_type]), TOWER_RANGES[game.selected_tower_type])
            screen.blit(range_surf, (range_pos[0] - TOWER_RANGES[game.selected_tower_type], range_pos[1] - TOWER_RANGES[game.selected_tower_type]))
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()