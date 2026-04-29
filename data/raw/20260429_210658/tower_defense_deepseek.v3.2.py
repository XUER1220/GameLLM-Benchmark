import pygame
import random
import math

pygame.init()

# 固定参数
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 地图参数
TILE_SIZE = 32
MAP_COLS = 20
MAP_ROWS = 15
MAP_WIDTH = MAP_COLS * TILE_SIZE  # 640
MAP_HEIGHT = MAP_ROWS * TILE_SIZE  # 480
HUD_WIDTH = SCREEN_WIDTH - MAP_WIDTH  # 160

# 颜色
COLORS = {
    "background": (30, 30, 40),
    "grid": (60, 60, 70),
    "path": (140, 110, 80),
    "ground": (70, 100, 60),
    "entrance": (200, 150, 50),
    "base": (180, 70, 70),
    "hud_bg": (40, 40, 50),
    "hud_text": (240, 240, 240),
    "highlight": (255, 255, 150),
    "range": (255, 255, 255, 100),
    "btn_bg": (50, 120, 180),
    "btn_hover": (70, 140, 220),
    "arrow_tower": (100, 200, 100),
    "cannon_tower": (200, 100, 100),
    "slow_tower": (100, 150, 220),
    "enemy_normal": (180, 100, 120),
    "enemy_fast": (120, 180, 100),
    "enemy_tank": (120, 120, 180),
    "projectile_arrow": (50, 220, 50),
    "projectile_cannon": (220, 80, 50),
    "projectile_slow": (100, 150, 240),
    "wave_text": (255, 200, 50),
    "win": (50, 220, 100),
    "lose": (220, 70, 70)
}

# 游戏参数
INITIAL_GOLD = 180
BASE_HEALTH = 20
PREPARE_TIME = 3  # 秒
WAVE_COUNT = 5
random.seed(42)

# 塔参数
TOWER_TYPES = {
    "arrow": {"name": "Arrow Tower", "cost": 50, "range": 120, "damage": 8, "cooldown": 0.8, "color": COLORS["arrow_tower"], "projectile_color": COLORS["projectile_arrow"], "radius": 0},
    "cannon": {"name": "Cannon Tower", "cost": 80, "range": 105, "damage": 14, "cooldown": 1.2, "color": COLORS["cannon_tower"], "projectile_color": COLORS["projectile_cannon"], "radius": 45},
    "slow": {"name": "Slow Tower", "cost": 70, "range": 110, "damage": 4, "cooldown": 1.0, "color": COLORS["slow_tower"], "projectile_color": COLORS["projectile_slow"], "radius": 0}
}
UPGRADE_COST_RATIO = 0.7
MAX_LEVEL = 3  # 基础1级 + 2次升级

# 敌人参数
ENEMY_TYPES = {
    "normal": {"health": 30, "speed": 0.8, "gold": 10, "color": COLORS["enemy_normal"]},
    "fast": {"health": 15, "speed": 1.6, "gold": 8, "color": COLORS["enemy_fast"]},
    "tank": {"health": 60, "speed": 0.5, "gold": 25, "color": COLORS["enemy_tank"]}
}

# 固定路径点 (基于格子坐标，从入口到基地)
PATH_POINTS = [
    (0, 7),   # 入口（左侧中间）
    (5, 7),
    (5, 3),
    (15, 3),
    (15, 11),
    (10, 11),
    (10, 7),
    (19, 7)   # 基地（右侧中间）
]

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Defense Hard")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 48)
        self.reset()

    def reset(self):
        self.gold = INITIAL_GOLD
        self.base_health = BASE_HEALTH
        self.wave = 0
        self.enemies = []
        self.towers = []
        self.projectiles = []
        self.selected_tower_type = "arrow"
        self.wave_timer = 0
        self.wave_in_progress = False
        self.spawn_index = 0
        self.wave_enemies_left = 0
        self.game_over = False
        self.victory = False
        self.hover_tile = None
        self.path_mask = self.create_path_mask()
        self.generate_wave_data()

    def create_path_mask(self):
        mask = [[False for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
        for i in range(len(PATH_POINTS)-1):
            x1, y1 = PATH_POINTS[i]
            x2, y2 = PATH_POINTS[i+1]
            steps = max(abs(x2-x1), abs(y2-y1))
            for s in range(steps+1):
                t = s / max(steps, 1)
                x = int(x1 + (x2-x1)*t)
                y = int(y1 + (y2-y1)*t)
                if 0 <= x < MAP_COLS and 0 <= y < MAP_ROWS:
                    mask[y][x] = True
        return mask

    def generate_wave_data(self):
        self.waves = []
        for i in range(WAVE_COUNT):
            wave_num = i+1
            count = 5 + wave_num*2
            types = []
            for j in range(count):
                if wave_num >= 4 and j % 5 == 0:
                    types.append("tank")
                elif wave_num >= 2 and j % 3 == 0:
                    types.append("fast")
                else:
                    types.append("normal")
            self.waves.append(types)

    def can_build_at(self, grid_x, grid_y):
        if not (0 <= grid_x < MAP_COLS and 0 <= grid_y < MAP_ROWS):
            return False
        if self.path_mask[grid_y][grid_x]:
            return False
        for tower in self.towers:
            if tower.grid_x == grid_x and tower.grid_y == grid_y:
                return False
        # 检查是否在入口或基地附近
        entrance = PATH_POINTS[0]
        base = PATH_POINTS[-1]
        if (grid_x == entrance[0] and grid_y == entrance[1]) or (grid_x == base[0] and grid_y == base[1]):
            return False
        return True

    def start_next_wave(self):
        if self.wave >= WAVE_COUNT:
            return
        self.wave += 1
        self.wave_in_progress = True
        self.spawn_index = 0
        self.wave_enemies_left = len(self.waves[self.wave-1])
        self.wave_timer = 0

    def spawn_enemy(self):
        if self.spawn_index >= len(self.waves[self.wave-1]):
            return
        enemy_type = self.waves[self.wave-1][self.spawn_index]
        self.enemies.append(Enemy(enemy_type, PATH_POINTS))
        self.spawn_index += 1

    def update(self, dt):
        if self.game_over:
            return

        # 波次逻辑
        if not self.wave_in_progress and self.wave < WAVE_COUNT:
            self.wave_timer += dt
            if self.wave_timer >= PREPARE_TIME:
                self.start_next_wave()
        elif self.wave_in_progress:
            self.wave_timer += dt
            if self.spawn_index < len(self.waves[self.wave-1]) and self.wave_timer >= self.spawn_index * 0.8:
                self.spawn_enemy()
            if not self.enemies and self.spawn_index >= len(self.waves[self.wave-1]):
                self.wave_in_progress = False
                self.wave_timer = 0
                if self.wave >= WAVE_COUNT:
                    self.victory = True
                    self.game_over = True

        # 更新敌人
        for enemy in self.enemies[:]:
            enemy.update(dt)
            if enemy.reached_base:
                self.base_health -= 1
                self.enemies.remove(enemy)
                if self.base_health <= 0:
                    self.game_over = True
                    self.victory = False

        # 更新炮塔
        for tower in self.towers:
            tower.update(dt, self.enemies, self.projectiles)

        # 更新弹道
        for proj in self.projectiles[:]:
            proj.update(dt)
            if proj.reached_target:
                if proj.target in self.enemies:
                    proj.target.health -= proj.damage
                    if proj.target.health <= 0:
                        self.gold += proj.target.gold
                        if proj.target in self.enemies:
                            self.enemies.remove(proj.target)
                if proj.slow_time > 0 and proj.target in self.enemies:
                    proj.target.slow(proj.slow_time)
                if proj.splash_radius > 0:
                    for enemy in self.enemies[:]:
                        if enemy != proj.target:
                            dist = math.hypot(enemy.x - proj.x, enemy.y - proj.y)
                            if dist <= proj.splash_radius:
                                enemy.health -= proj.damage * 0.5
                                if enemy.health <= 0:
                                    self.gold += enemy.gold
                                    if enemy in self.enemies:
                                        self.enemies.remove(enemy)
                self.projectiles.remove(proj)

    def draw(self):
        self.screen.fill(COLORS["background"])

        # 绘制地图网格和地面
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                color = COLORS["path"] if self.path_mask[y][x] else COLORS["ground"]
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, COLORS["grid"], rect, 1)

        # 绘制路径线
        path_pixel = [(x*TILE_SIZE + TILE_SIZE//2, y*TILE_SIZE + TILE_SIZE//2) for (x,y) in PATH_POINTS]
        if len(path_pixel) >= 2:
            pygame.draw.lines(self.screen, (200, 180, 120), False, path_pixel, 4)

        # 绘制入口和基地
        entrance = PATH_POINTS[0]
        base = PATH_POINTS[-1]
        pygame.draw.rect(self.screen, COLORS["entrance"], (entrance[0]*TILE_SIZE, entrance[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(self.screen, COLORS["base"], (base[0]*TILE_SIZE, base[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(self.screen, (255,255,255), (entrance[0]*TILE_SIZE, entrance[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)
        pygame.draw.rect(self.screen, (255,255,255), (base[0]*TILE_SIZE, base[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)

        # 绘制炮塔
        for tower in self.towers:
            tower.draw(self.screen)

        # 绘制弹道
        for proj in self.projectiles:
            proj.draw(self.screen)

        # 绘制敌人
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # 绘制鼠标悬停的建塔位置和射程
        if self.hover_tile and self.can_build_at(self.hover_tile[0], self.hover_tile[1]):
            x, y = self.hover_tile
            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.screen, COLORS["highlight"], rect, 3)
            tower_data = TOWER_TYPES[self.selected_tower_type]
            range_radius = tower_data["range"]
            range_surf = pygame.Surface((range_radius*2, range_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(range_surf, COLORS["range"], (range_radius, range_radius), range_radius, 2)
            self.screen.blit(range_surf, (x*TILE_SIZE + TILE_SIZE//2 - range_radius, y*TILE_SIZE + TILE_SIZE//2 - range_radius))

        # HUD背景
        pygame.draw.rect(self.screen, COLORS["hud_bg"], (MAP_WIDTH, 0, HUD_WIDTH, SCREEN_HEIGHT))

        # HUD文字
        texts = [
            f"Base: {self.base_health}/{BASE_HEALTH}",
            f"Gold: {self.gold}",
            f"Wave: {self.wave}/{WAVE_COUNT}",
            f"Enemies: {len(self.enemies)}",
            f"Selected: {TOWER_TYPES[self.selected_tower_type]['name']}",
            f"Cost: {TOWER_TYPES[self.selected_tower_type]['cost']}"
        ]
        if not self.wave_in_progress and self.wave < WAVE_COUNT:
            texts.append(f"Next wave in: {PREPARE_TIME - int(self.wave_timer)}")
        for i, text in enumerate(texts):
            surf = self.font.render(text, True, COLORS["hud_text"])
            self.screen.blit(surf, (MAP_WIDTH + 10, 20 + i*30))

        # 塔选择按钮
        types = ["arrow", "cannon", "slow"]
        for i, ttype in enumerate(types):
            rect = pygame.Rect(MAP_WIDTH + 20, 200 + i*60, 120, 40)
            color = COLORS["btn_hover"] if self.selected_tower_type == ttype else COLORS["btn_bg"]
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            pygame.draw.rect(self.screen, (255,255,255), rect, 2, border_radius=5)
            name = self.font.render(TOWER_TYPES[ttype]["name"], True, COLORS["hud_text"])
            cost = self.font.render(f"${TOWER_TYPES[ttype]['cost']}", True, COLORS["hud_text"])
            self.screen.blit(name, (rect.x + 10, rect.y + 5))
            self.screen.blit(cost, (rect.x + 10, rect.y + 25))

        # 游戏结束画面
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,150))
            self.screen.blit(overlay, (0,0))
            if self.victory:
                text = self.big_font.render("YOU WIN!", True, COLORS["win"])
            else:
                text = self.big_font.render("GAME OVER", True, COLORS["lose"])
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            wave_text = self.font.render(f"Wave reached: {self.wave}/{WAVE_COUNT}", True, COLORS["hud_text"])
            self.screen.blit(wave_text, (SCREEN_WIDTH//2 - wave_text.get_width()//2, SCREEN_HEIGHT//2 + 10))
            restart_text = self.font.render("Press R to Restart", True, COLORS["hud_text"])
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 50))

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r:
                    self.reset()
                if event.key == pygame.K_1:
                    self.selected_tower_type = "arrow"
                if event.key == pygame.K_2:
                    self.selected_tower_type = "cannon"
                if event.key == pygame.K_3:
                    self.selected_tower_type = "slow"
            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                if mx < MAP_WIDTH:
                    self.hover_tile = (mx // TILE_SIZE, my // TILE_SIZE)
                else:
                    self.hover_tile = None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键建塔
                    if self.hover_tile and self.can_build_at(self.hover_tile[0], self.hover_tile[1]):
                        cost = TOWER_TYPES[self.selected_tower_type]["cost"]
                        if self.gold >= cost:
                            self.towers.append(Tower(self.selected_tower_type, self.hover_tile[0], self.hover_tile[1]))
                            self.gold -= cost
                elif event.button == 3:  # 右键升级
                    if self.hover_tile:
                        for tower in self.towers:
                            if tower.grid_x == self.hover_tile[0] and tower.grid_y == self.hover_tile[1]:
                                upgrade_cost = int(TOWER_TYPES[tower.ttype]["cost"] * UPGRADE_COST_RATIO)
                                if tower.level < MAX_LEVEL and self.gold >= upgrade_cost:
                                    tower.upgrade()
                                    self.gold -= upgrade_cost
        return True

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            running = self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()

class Tower:
    def __init__(self, ttype, grid_x, grid_y):
        self.ttype = ttype
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x * TILE_SIZE + TILE_SIZE//2
        self.y = grid_y * TILE_SIZE + TILE_SIZE//2
        self.level = 1
        self.cooldown_timer = 0
        self.data = TOWER_TYPES[ttype].copy()
        self.range = self.data["range"]
        self.damage = self.data["damage"]
        self.cooldown = self.data["cooldown"]
        self.color = self.data["color"]
        self.projectile_color = self.data["projectile_color"]
        self.splash_radius = self.data["radius"]

    def upgrade(self):
        if self.level < MAX_LEVEL:
            self.level += 1
            self.range = int(self.range * 1.3)
            self.damage = int(self.damage * 1.5)
            self.cooldown = max(0.3, self.cooldown * 0.9)

    def update(self, dt, enemies, projectiles):
        self.cooldown_timer -= dt
        if self.cooldown_timer > 0:
            return

        # 寻找目标
        target = None
        min_dist = float('inf')
        for enemy in enemies:
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist <= self.range and dist < min_dist:
                min_dist = dist
                target = enemy

        if target:
            self.cooldown_timer = self.cooldown
            slow_time = 2.0 if self.ttype == "slow" else 0
            proj = Projectile(self.x, self.y, target, self.damage, self.projectile_color, self.splash_radius, slow_time)
            projectiles.append(proj)

    def draw(self, screen):
        # 塔身
        radius = TILE_SIZE//2 - 2
        pygame.draw.circle(screen, self.color, (self.x, self.y), radius)
        pygame.draw.circle(screen, (255,255,255), (self.x, self.y), radius, 2)
        # 等级标记
        level_text = pygame.font.SysFont(None, 20).render(str(self.level), True, (255,255,255))
        screen.blit(level_text, (self.x - level_text.get_width()//2, self.y - level_text.get_height()//2))
        # 塔顶方向指示
        angle = pygame.time.get_ticks() * 0.002 % (2*math.pi)
        end_x = self.x + math.cos(angle) * radius*0.8
        end_y = self.y + math.sin(angle) * radius*0.8
        pygame.draw.line(screen, (255,255,200), (self.x, self.y), (end_x, end_y), 3)

class Enemy:
    def __init__(self, etype, path_points):
        self.etype = etype
        self.data = ENEMY_TYPES[etype].copy()
        self.health = self.data["health"]
        self.max_health = self.health
        self.speed = self.data["speed"]
        self.base_speed = self.speed
        self.gold = self.data["gold"]
        self.color = self.data["color"]
        self.path_points = [(x*TILE_SIZE + TILE_SIZE//2, y*TILE_SIZE + TILE_SIZE//2) for (x,y) in path_points]
        self.path_index = 0
        self.x, self.y = self.path_points[0]
        self.reached_base = False
        self.slow_timer = 0

    def slow(self, duration):
        self.slow_timer = duration
        self.speed = self.base_speed * 0.4

    def update(self, dt):
        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.speed = self.base_speed

        if self.path_index >= len(self.path_points)-1:
            self.reached_base = True
            return

        target_x, target_y = self.path_points[self.path_index+1]
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist < self.speed * dt * TILE_SIZE:
            self.path_index += 1
            if self.path_index >= len(self.path_points)-1:
                self.reached_base = True
                return
            target_x, target_y = self.path_points[self.path_index+1]
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.hypot(dx, dy)
        if dist > 0:
            self.x += dx / dist * self.speed * dt * TILE_SIZE
            self.y += dy / dist * self.speed * dt * TILE_SIZE

    def draw(self, screen):
        radius = TILE_SIZE//3
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), radius)
        pygame.draw.circle(screen, (255,255,255), (int(self.x), int(self.y)), radius, 2)
        # 血条
        bar_width = TILE_SIZE
        bar_height = 4
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (100,100,100), (self.x - bar_width//2, self.y - radius - 8, bar_width, bar_height))
        pygame.draw.rect(screen, (50,220,80), (self.x - bar_width//2, self.y - radius - 8, int(bar_width * health_ratio), bar_height))

class Projectile:
    def __init__(self, x, y, target, damage, color, splash_radius=0, slow_time=0):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.color = color
        self.speed = 8.0
        self.reached_target = False
        self.splash_radius = splash_radius
        self.slow_time = slow_time

    def update(self, dt):
        if self.reached_target or not self.target:
            self.reached_target = True
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        if dist < self.speed * dt * TILE_SIZE:
            self.reached_target = True
            return
        self.x += dx / dist * self.speed * dt * TILE_SIZE
        self.y += dy / dist * self.speed * dt * TILE_SIZE

    def draw(self, screen):
        radius = 4
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), radius)
        pygame.draw.circle(screen, (255,255,255), (int(self.x), int(self.y)), radius, 1)

if __name__ == "__main__":
    game = Game()
    game.run()