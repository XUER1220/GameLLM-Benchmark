import pygame
import random
import math
import sys

# 固定常量定义
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 32
MAP_COLS, MAP_ROWS = 20, 15
MAP_WIDTH, MAP_HEIGHT = GRID_SIZE * MAP_COLS, GRID_SIZE * MAP_ROWS
HUD_WIDTH = WIDTH - MAP_WIDTH
FPS = 60
SEED = 42
random.seed(SEED)

# 初始化 Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense Hard")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16, bold=True)
font_large = pygame.font.SysFont("Arial", 24, bold=True)
font_huge = pygame.font.SysFont("Arial", 36, bold=True)

# 颜色定义
COLORS = {
    "bg": (255, 255, 255),
    "path": (100, 100, 100),
    "path_line": (150, 150, 150),
    "grid": (200, 200, 200),
    "enemy_normal": (0, 190, 0),
    "enemy_fast": (0, 100, 255),
    "enemy_heavy": (180, 0, 0),
    "tower_arrow": (200, 180, 0),
    "tower_cannon": (100, 100, 200),
    "tower_slow": (0, 180, 180),
    "projectile_arrow": (255, 255, 255),
    "projectile_cannon": (255, 100, 0),
    "base": (200, 50, 50),
    "base entrance": (100, 200, 100),
    "tower_selected": (255, 255, 0),
    "hover_valid": (0, 255, 0, 100),
    "hover_invalid": (255, 0, 0, 100),
}

# 敌人类型定义
ENEMY_TYPES = {
    "normal": {
        "name": "Normal",
        "speed": 1.2,
        "hp": 40,
        "reward": 10,
        "radius": 10,
        "color": COLORS["enemy_normal"]
    },
    "fast": {
        "name": "Fast",
        "speed": 3.0,
        "hp": 20,
        "reward": 15,
        "radius": 8,
        "color": COLORS["enemy_fast"]
    },
    "heavy": {
        "name": "Heavy",
        "speed": 0.8,
        "hp": 80,
        "reward": 20,
        "radius": 12,
        "color": COLORS["enemy_heavy"]
    }
}

# 塔类型定义
TOWER_TYPES = {
    1: {
        "name": "Arrow",
        "cost": 50,
        "range": 120,
        "damage": 8,
        "fire_rate": 0.8,
        "color": COLORS["tower_arrow"],
        "projectile_speed": 8,
        "projectile_type": "arrow",
    },
    2: {
        "name": "Cannon",
        "cost": 80,
        "range": 105,
        "damage": 14,
        "fire_rate": 1.2,
        "splash_radius": 45,
        "color": COLORS["tower_cannon"],
        "projectile_speed": 6,
        "projectile_type": "cannon",
    },
    3: {
        "name": "Slow",
        "cost": 70,
        "range": 110,
        "damage": 4,
        "fire_rate": 1.0,
        "slow_duration": 2.0,
        "slow_factor": 0.5,
        "color": COLORS["tower_slow"],
        "projectile_speed": 7,
        "projectile_type": "slow",
    }
}

# 固定路径（关键点坐标，从左入口到右基地）
PATH_POINTS = [
    (0, 3), (6, 3), (6, 7), (12, 7), (12, 2), (18, 2), (18, 11),
    (10, 11), (10, 13), (15, 13), (15, 8), (19, 8)
]
PATH_GRID = []
# 预计算路径上的所有格子
for i in range(len(PATH_POINTS) - 1):
    x1, y1 = PATH_POINTS[i]
    x2, y2 = PATH_POINTS[i + 1]
    if x1 == x2:  # 垂直线
        for y in range(min(y1, y2), max(y1, y2) + 1):
            PATH_GRID.append((x1, y))
    elif y1 == y2:  # 水平线
        for x in range(min(x1, x2), max(x1, x2) + 1):
            PATH_GRID.append((x, y1))

# 基地位置和入口位置
BASE_POS = (MAP_WIDTH - GRID_SIZE * 2, MAP_HEIGHT - GRID_SIZE)
ENTRANCE_POS = (0, GRID_SIZE)

# 波次配置
WAVE_CONFIG = [
    [{"type": "normal", "count": 5, "interval": 1.5}],
    [{"type": "normal", "count": 8, "interval": 1.2}, {"type": "fast", "count": 3, "interval": 1.5}],
    [{"type": "heavy", "count": 3, "interval": 2.0}, {"type": "fast", "count": 6, "interval": 1.2}],
    [{"type": "normal", "count": 5, "interval": 1.0}, {"type": "fast", "count": 8, "interval": 0.8}, {"type": "heavy", "count": 3, "interval": 1.8}],
    [{"type": "heavy", "count": 6, "interval": 1.2}, {"type": "fast", "count": 10, "interval": 0.7}],
]


class Enemy:
    def __init__(self, enemy_type_key, wave):
        config = ENEMY_TYPES[enemy_type_key].copy()
        self.type_key = enemy_type_key
        self.name = config["name"]
        self.base_speed = config["speed"] * (1 + 0.15 * wave)  # 每波增强15%
        self.speed = self.base_speed
        self.max_hp = config["hp"] * (1 + 0.1 * wave)
        self.hp = self.max_hp
        self.reward = int(config["reward"] * (1 + 0.1 * wave))
        self.radius = config["radius"]
        self.color = config["color"]
        self.pos = (PATH_POINTS[0][0] * GRID_SIZE + GRID_SIZE // 2, 
                    PATH_POINTS[0][1] * GRID_SIZE + GRID_SIZE // 2)
        self.path_index = 0
        self.slow_timer = 0.0
        self.slow_factor = 1.0
        self.slow_duration = 0.0

    def update(self, dt):
        # 应用减速效果
        if self.slow_timer > 0:
            self.slow_timer -= dt
            self.speed = self.base_speed * self.slow_factor
        else:
            self.speed = self.base_speed
            self.slow_factor = 1.0

        # 移动
        if self.path_index < len(PATH_POINTS) - 1:
            target_x = PATH_POINTS[self.path_index + 1][0] * GRID_SIZE + GRID_SIZE // 2
            target_y = PATH_POINTS[self.path_index + 1][1] * GRID_SIZE + GRID_SIZE // 2
            
            current_x, current_y = self.pos
            dx, dy = target_x - current_x, target_y - current_y
            distance = math.hypot(dx, dy)
            
            if distance > self.speed * dt:
                # 移动
                if distance > 0:
                    self.pos = (
                        current_x + dx / distance * self.speed * dt,
                        current_y + dy / distance * self.speed * dt
                    )
            else:
                # 到达关键点
                self.pos = (target_x, target_y)
                self.path_index += 1

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)
        # 血条
        bar_width = 20
        height = 3
        hp_pct = self.hp / self.max_hp
        pygame.draw.rect(screen, (255, 0, 0), 
                         (int(self.pos[0] - bar_width // 2), int(self.pos[1] - self.radius - 10), bar_width, height))
        pygame.draw.rect(screen, (0, 255, 0), 
                         (int(self.pos[0] - bar_width // 2), int(self.pos[1] - self.radius - 10), 
                          max(0, bar_width * hp_pct), height))

    def take_damage(self, damage):
        self.hp -= damage


class Projectile:
    def __init__(self, start, target, tower_type_key):
        config = TOWER_TYPES[tower_type_key]
        self.pos = start
        self.target_pos = target.pos  # 存储目标当前位置
        self.target = target
        self.speed = config["projectile_speed"]
        self.damage = config["damage"]
        self.projectile_type = config["projectile_type"]
        self.splash_radius = config.get("splash_radius", 0)
        self.effect_duration = config.get("slow_duration", 0)
        self.effect_factor = config.get("slow_factor", 1.0)

        # 计算方向
        dx = target.pos[0] - start[0]
        dy = target.pos[1] - start[1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.velocity = (dx / dist * self.speed, dy / dist * self.speed)
        else:
            self.velocity = (0, 0)

    def update(self, dt):
        self.pos = (self.pos[0] + self.velocity[0] * dt, self.pos[1] + self.velocity[1] * dt)

    def draw(self, screen):
        if self.projectile_type == "arrow":
            pygame.draw.line(screen, COLORS["projectile_arrow"], 
                             (int(self.pos[0]), int(self.pos[1])), 
                             (int(self.pos[0] - self.velocity[0] * 0.5), 
                              int(self.pos[1] - self.velocity[1] * 0.5)), 2)
        elif self.projectile_type == "cannon":
            pygame.draw.circle(screen, COLORS["projectile_cannon"], 
                               (int(self.pos[0]), int(self.pos[1])), 4)
        elif self.projectile_type == "slow":
            pygame.draw.line(screen, COLORS["tower_slow"], 
                             (int(self.pos[0]), int(self.pos[1])), 
                             (int(self.pos[0] - self.velocity[0] * 0.5), 
                              int(self.pos[1] - self.velocity[1] * 0.5)), 3)

    def check_hit(self):
        if self.target is None:
            return False
        
        # 更新目标位置（可能已移动）
        dx = self.target.pos[0] - self.pos[0]
        dy = self.target.pos[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        
        if dist <= self.target.radius + 5:  # 命中判定半径
            if self.projectile_type == "arrow":
                self.target.take_damage(self.damage)
                return True
            elif self.projectile_type == "cannon":
                # 溅射伤害
                enemies_hit = []
                for enemy in game.enemies:
                    enemy_dist = math.hypot(enemy.pos[0] - self.pos[0], enemy.pos[1] - self.pos[1])
                    if enemy_dist <= self.splash_radius:
                        enemies_hit.append(enemy)
                for enemy in enemies_hit:
                    enemy.take_damage(self.damage)
                return True
            elif self.projectile_type == "slow":
                if self.effect_duration > 0 and self.effect_factor < 1.0:
                    self.target.slow_timer = self.effect_duration
                    self.target.slow_factor = self.effect_factor
                    self.target.take_damage(self.damage)
                    return True
        return False


class Tower:
    def __init__(self, grid_x, grid_y, tower_type_key):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x * GRID_SIZE + GRID_SIZE // 2
        self.y = grid_y * GRID_SIZE + GRID_SIZE // 2
        self.level = 1
        self.type_key = tower_type_key
        config = TOWER_TYPES[tower_type_key].copy()
        self.name = config["name"]
        self.range = config["range"]
        self.damage = config["damage"]
        self.fire_rate = config["fire_rate"]
        self.splash_radius = config.get("splash_radius", 0)
        self.effect_duration = config.get("slow_duration", 0)
        self.effect_factor = config.get("slow_factor", 1.0)
        self.cooldown = 0.0
        self.total_cost = config["cost"]

    @property
    def update_range(self):
        return self.range + 5 * (self.level - 1)

    @property
    def update_damage(self):
        return self.damage * (1 + 0.4 * (self.level - 1))

    def update(self, dt):
        self.cooldown -= dt

    def can_attack(self):
        return self.cooldown <= 0

    def find_target(self):
        target = None
        min_dist = float('inf')
        for enemy in game.enemies:
            dist = math.hypot(enemy.pos[0] - self.x, enemy.pos[1] - self.y)
            if dist <= self.update_range and dist < min_dist:
                # 选择最近的敌人
                target = enemy
                min_dist = dist
        return target

    def fire(self, dt):
        target = self.find_target()
        if target is not None:
            self.cooldown = self.fire_rate
            game.projectiles.append(Projectile((self.x, self.y), target, self.type_key))

    def upgrade(self):
        if self.level < 2:
            upgrade_cost = int(self.total_cost * 0.7)
            if game.currency >= upgrade_cost:
                game.currency -= upgrade_cost
                self.level += 1
                self.damage *= 1.4
                self.range += 5
                if self.type_key == 2:  # Cannon tower
                    self.splash_radius += 10

    def draw(self, screen, selected=False):
        # 绘制基础塔身
        pygame.draw.rect(screen, self.color, 
                         (int(self.x - GRID_SIZE // 3), int(self.y - GRID_SIZE // 3),
                          int(GRID_SIZE // 1.5), int(GRID_SIZE // 1.5)))
        
        # 等级标记
        level_text = font.render(str(self.level), True, (255, 255, 255))
        screen.blit(level_text, (int(self.x - level_text.get_width() // 2), int(self.y - level_text.get_height() // 2)))

        # 选择边框
        if selected:
            pygame.draw.rect(screen, (255, 255, 0), 
                             (self.x - GRID_SIZE // 2 - 2, self.y - GRID_SIZE // 2 - 2,
                              GRID_SIZE + 4, GRID_SIZE + 4), 2)

    @property
    def color(self):
        return TOWER_TYPES[self.type_key]["color"]

    @property
    def upgrade_cost(self):
        return int(self.total_cost * 0.7)


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.currency = 180
        self.base_hp = 20
        self.enemies = []
        self.projectiles = []
        self.towers = []
        self.built_grid = [[0] * MAP_ROWS for _ in range(MAP_COLS)]
        self.towers_with_upgrade = set()
        self.selected_tower_type = 1
        self.game_state = "playing"  # playing, wave_wait, won, lost
        self.current_wave = 0
        self.wave_enemies_remaining = []
        self.wave_generation_time = 0.0
        self.wave_generation_next = 0.0
        self.wave_cooldown_time = 3.0
        self.last_time = pygame.time.get_ticks()
        
        # 确保路径格子不可建塔
        for x, y in PATH_GRID:
            if 0 <= x < MAP_COLS and 0 <= y < MAP_ROWS:
                self.built_grid[x][y] = 1

        # 标记基地不可建塔
        base_x, base_y = self.get_grid_pos(BASE_POS)
        self.built_grid[base_x][base_y] = 1

    def get_grid_pos(self, screen_pos):
        x = int(screen_pos[0] // GRID_SIZE)
        y = int(screen_pos[1] // GRID_SIZE)
        return x, y

    def update(self, dt):
        if self.game_state != "playing":
            for enemy in self.enemies:
                enemy.update(dt)
            for projectile in self.projectiles:
                projectile.update(dt)
            return

        # 更新塔
        for tower in self.towers:
            tower.update(dt)
            if tower.can_attack():
                tower.fire(dt)

        # 更新敌人
        for enemy in self.enemies[:]:
            enemy.update(dt)
            if enemy.hp <= 0:
                self.currency += enemy.reward
                self.enemies.remove(enemy)
                continue
            # 检查是否到达基地
            if enemy.path_index >= len(PATH_POINTS) - 1:
                self.base_hp -= 1
                self.enemies.remove(enemy)
                if self.base_hp <= 0:
                    self.game_state = "lost"

        # 处理子弹
        for projectile in self.projectiles[:]:
            projectile.update(dt)
            if projectile.check_hit():
                self.projectiles.remove(projectile)

        # 波次生成逻辑
        if self.game_state == "playing":
            if self.wave_enemies_remaining:
                self.wave_generation_time += dt
                if self.wave_generation_time >= self.wave_generation_next:
                    if self.wave_enemies_remaining:
                        enemy_cfg = self.wave_enemies_remaining.pop(0)
                        enemy = Enemy(enemy_cfg["type"], self.current_wave)
                        self.enemies.append(enemy)
                        self.wave_generation_time = 0
                        if self.wave_enemies_remaining:
                            self.wave_generation_next = self.wave_enemies_remaining[0].get("interval", 1.5)
                        else:
                            self.wave_generation_next = 1000000  # 禁用定时器
            else:
                # 检查是否当前波全部敌人生成完
                if len(self.enemies) == 0 and self.game_state == "playing":
                    self.current_wave += 1
                    if self.current_wave >= 5:
                        self.game_state = "won"
                    else:
                        self.game_state = "wave_wait"
                        self.wave_cooldown_time = 3.0
                        # 下一波敌人配置
                        self.wave_enemies_remaining = WAVE_CONFIG[self.current_wave].copy()
                        self.wave_generation_next = self.wave_enemies_remaining[0].get("interval", 1.5)
        elif self.game_state == "wave_wait":
            self.wave_cooldown_time -= dt
            if self.wave_cooldown_time <= 0:
                self.game_state = "playing"
                self.wave_enemies_remaining = WAVE_CONFIG[self.current_wave].copy()
                self.wave_generation_next = self.wave_enemies_remaining[0].get("interval", 1.5)

    def draw(self, screen):
        # 背景
        screen.fill(COLORS["bg"])

        # 绘制地图网格
        for x in range(MAP_COLS):
            for y in range(MAP_ROWS):
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, COLORS["grid"], rect, 1)

        # 绘制路径（带线条）
        if len(PATH_POINTS) > 1:
            path_points_scaled = [(p[0] * GRID_SIZE + GRID_SIZE // 2, p[1] * GRID_SIZE + GRID_SIZE // 2) 
                                  for p in PATH_POINTS]
            pygame.draw.lines(screen, COLORS["path_line"], False, path_points_scaled, 16)
        
        # 绘制基地和入口
        pygame.draw.rect(screen, COLORS["base"], 
                         (BASE_POS[0], BASE_POS[1], GRID_SIZE * 2, GRID_SIZE * 2))
        pygame.draw.rect(screen, COLORS["base entrance"],
                         (ENTRANCE_POS[0], ENTRANCE_POS[1], GRID_SIZE, GRID_SIZE))
        
        # 绘制敌人
        for enemy in self.enemies:
            enemy.draw(screen)

        # 绘制塔
        for tower in self.towers:
            tower.draw(screen)

        # 绘制子弹
        for projectile in self.projectiles:
            projectile.draw(screen)

        # 绘制 HUD 区域
        hud_rect = pygame.Rect(MAP_WIDTH, 0, HUD_WIDTH, HEIGHT)
        pygame.draw.rect(screen, (220, 220, 220), hud_rect)
        
        # 塔选择
        tower_names = ["Arrow (1)", "Cannon (2)", "Slow (3)"]
        tower_costs = [50, 80, 70]
        for i in range(3):
            rect = pygame.Rect(MAP_WIDTH + 20, 30 + i * 80, 120, 60)
            pygame.draw.rect(screen, COLORS[f"tower_{TOWER_TYPES[i+1]['name'].lower()}"], 
                            rect, 2 if i + 1 == self.selected_tower_type else 1)
            name_text = font.render(f"{tower_names[i]} - ${tower_costs[i]}", True, (0, 0, 0))
            screen.blit(name_text, (rect.x + 5, rect.y + 5))
            desc = font.render("Level: 1", True, (100, 100, 100))
            screen.blit(desc, (rect.x + 5, rect.y + 35))

        # 游戏状态信息
        currency_text = font_large.render(f"Coins: ${self.currency}", True, (0, 0, 0))
        screen.blit(currency_text, (MAP_WIDTH + 20, 300))

        wave_text = font_large.render(f"Wave: {self.current_wave + 1}/5", True, (0, 0, 0))
        screen.blit(wave_text, (MAP_WIDTH + 20, 330))

        base_text = font_large.render(f"Base HP: {self.base_hp}", True, (255, 0, 0) if self.base_hp <= 5 else (0, 0, 0))
        screen.blit(base_text, (MAP_WIDTH + 20, 360))

        enemies_remaining = len(self.enemies)
        wave_enemies_remaining = len(self.wave_enemies_remaining) if self.game_state in ["playing", "wave_wait"] else 0
        if self.game_state == "wave_wait":
            enemies_text = font_large.render(f"Wave Complete: Next in {self.wave_cooldown_time:.1f}s", True, (0, 0, 0))
        else:
            enemies_text = font_large.render(f"Enemies: {enemies_remaining} + {wave_enemies_remaining}", True, (0, 0, 0))
        screen.blit(enemies_text, (MAP_WIDTH + 20, 390))

        # 塔信息
        if self.selected_tower_type:
            tower_info = TOWER_TYPES[self.selected_tower_type]
            info = f"Range: {int(tower_info['range'])} | Dmg: {int(tower_info['damage'])}"
            info_text = font.render(info, True, (0, 0, 0))
            screen.blit(info_text, (MAP_WIDTH + 20, 450))
        
        # 游戏结束信息
        if self.game_state in ["won", "lost"]:
            if self.game_state == "won":
                win_text = font_huge.render("YOU WIN!", True, (0, 255, 0))
            else:
                win_text = font_huge.render("GAME OVER", True, (255, 0, 0))
            screen.blit(win_text, (MAP_WIDTH + 20, 500))
            restart_text = font.render("Press R to Restart", True, (0, 0, 0))
            screen.blit(restart_text, (MAP_WIDTH + 20, 550))

        # 鼠标悬停：显示选中塔的位置和可建造区域
        if self.game_state == "playing":
            mouse_pos = pygame.mouse.get_pos()
            grid_x, grid_y = self.get_grid_pos(mouse_pos)
            if 0 <= grid_x < MAP_COLS and 0 <= grid_y < MAP_ROWS:
                is_path = (grid_x, grid_y) in PATH_GRID
                is_base = (grid_x * GRID_SIZE, grid_y * GRID_SIZE) == (BASE_POS[0], BASE_POS[1])
                has_tower = self.built_grid[grid_x][grid_y] == 2
                can_build = not is_path and not is_base and not has_tower and self.currency >= TOWER_TYPES[self.selected_tower_type]["cost"]
                
                color = COLORS["hover_valid"] if can_build else COLORS["hover_invalid"]
                rect = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                rect.fill(color)
                screen.blit(rect, (grid_x * GRID_SIZE, grid_y * GRID_SIZE))

                # 显示塔的射程
                if self.towers:
                    # 显示当前选择塔类型的射程
                    tower = TOWER_TYPES[self.selected_tower_type]
                    range_rect = pygame.Surface((tower["range"] * 2, tower["range"] * 2), pygame.SRCALPHA)
                    pygame.draw.circle(range_rect, (0, 255, 0, 80), 
                                       (int(tower["range"]), int(tower["range"])), 
                                       int(tower["range"]))
                    range_x = grid_x * GRID_SIZE + GRID_SIZE // 2
                    range_y = grid_y * GRID_SIZE + GRID_SIZE // 2
                    screen.blit(range_rect, (range_x - tower["range"], range_y - tower["range"]))

        # 当前选定塔位置的选中框（用于升级）
        grid_x, grid_y = self.get_grid_pos(pygame.mouse.get_pos())
        for tower in self.towers:
            if tower.grid_x == grid_x and tower.grid_y == grid_y:
                pygame.draw.rect(screen, (0, 255, 0), 
                                (tower.x - GRID_SIZE // 2 - 2, tower.y - GRID_SIZE // 2 - 2,
                                 GRID_SIZE + 4, GRID_SIZE + 4), 3)
                upgrade_cost = tower.upgrade_cost
                upgrade_text = font.render(f"Upgrade: ${upgrade_cost}", True, (0, 0, 0))
                screen.blit(upgrade_text, (tower.x - GRID_SIZE // 2, tower.y + GRID_SIZE // 2))


def main():
    game = Game()
    running = True
    selected_tower_type = 1
    selected_tower_to_upgrade = None

    while running:
        dt = clock.tick(FPS) / 1000.0
        current_mouse_pos = pygame.mouse.get_pos()
        grid_x, grid_y = game.get_grid_pos(current_mouse_pos)
        current_tower = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game.reset()
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    keys = {pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3}
                    selected_tower_type = keys[event.key]
                    game.selected_tower_type = selected_tower_type
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 0 <= grid_x < MAP_COLS and 0 <= grid_y < MAP_ROWS:
                    # 检查是否有塔
                    if game.built_grid[grid_x][grid_y] == 2:
                        for tower in game.towers:
                            if tower.grid_x == grid_x and tower.grid_y == grid_y:
                                # 升级逻辑
                                if game.currency >= tower.upgrade_cost:
                                    tower.upgrade()
                                break
                    else:
                        # 建造逻辑
                        is_path = (grid_x, grid_y) in PATH_GRID
                        is_base = (grid_x * GRID_SIZE, grid_y * GRID_SIZE) == (BASE_POS[0], BASE_POS[1])
                        tower_cost = TOWER_TYPES[selected_tower_type]["cost"]
                        if not is_path and not is_base and game.currency >= tower_cost:
                            game.towers.append(Tower(grid_x, grid_y, selected_tower_type))
                            game.currency -= tower_cost
                            game.built_grid[grid_x][grid_x] = 2  # 注意：此处应为 grid_y
                            game.built_grid[grid_x][grid_y] = 2  # 修正：标记为有塔

        # 更新游戏逻辑
        game.update(dt)

        # 清屏并重绘
        screen.fill((255, 255, 255))
        game.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()