import pygame
import random
import math

# 初始化
pygame.init()

# 固定常量
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
GRID_COLS, GRID_ROWS = 20, 15
CELL_SIZE = 32
MAP_WIDTH, MAP_HEIGHT = GRID_COLS * CELL_SIZE, GRID_ROWS * CELL_SIZE  # 640x480
HUD_WIDTH = WINDOW_WIDTH - MAP_WIDTH  # 160
FPS = 60

# 颜色常量
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_GREEN = (0, 100, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
BROWN = (139, 69, 19)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# 塔类型定义
TOWER_TYPES = {
    1: {"name": "Arrow", "cost": 50, "upgrade_cost": 35, "range": 120, "damage": 8,
        "fire_rate": 0.8, "color": BLUE, "type": "single", "upgrade_level": 0},
    2: {"name": "Cannon", "cost": 80, "upgrade_cost": 56, "range": 105, "damage": 14,
        "fire_rate": 1.2, "splash": 45, "color": BROWN, "type": "splash", "upgrade_level": 0},
    3: {"name": "Slow", "cost": 70, "upgrade_cost": 49, "range": 110, "damage": 4,
        "fire_rate": 1.0, "slow_duration": 2.0, "slow_factor": 0.5, "color": PURPLE, "type": "slow", "upgrade_level": 0}
}

# 敌人类型定义
ENEMY_TYPES = {
    "normal": {"speed": 1.5, "hp": 30, "reward": 15, "color": GREEN, "size": 12},
    "fast": {"speed": 2.5, "hp": 18, "reward": 12, "color": CYAN, "size": 10},
    "heavy": {"speed": 1.0, "hp": 60, "reward": 20, "color": RED, "size": 16}
}

# 固定路径（20列x15行网格）
PATH_POINTS = [(0, 7), (3, 7), (3, 3), (8, 3), (8, 10), (15, 10), (15, 4), (19, 4)]
PATH_GRID = []
for i in range(len(PATH_POINTS) - 1):
    x1, y1 = PATH_POINTS[i]
    x2, y2 = PATH_POINTS[i + 1]
    if x1 == x2:  # vertical
        for y in range(min(y1, y2), max(y1, y2) + 1):
            PATH_GRID.append((x1, y))
    else:  # horizontal
        for x in range(min(x1, x2), max(x1, x2) + 1):
            PATH_GRID.append((x, y1))
PATH_GRID = list(dict.fromkeys(PATH_GRID))  # remove duplicates while preserving order

# 基地位置
BASE_POS = (19, 4)

# 波次定义
WAVES = [
    (15, "normal"),
    (25, "fast"),
    (10, "heavy"),
    (20, "normal"), (10, "fast"),
    (10, "normal"), (8, "heavy"), (15, "fast")
]

# 游戏状态常量
GAME_RUNNING = 0
GAME_PAUSED = 1
GAME_OVER = 2
VICTORY = 3

# 全局状态变量
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Tower Defense Hard")


def get_pos_grid(pos):
    """将像素坐标转换为网格坐标"""
    x, y = pos
    return x // CELL_SIZE, y // CELL_SIZE


def get_center_grid(grid_x, grid_y):
    """获取网格中心像素坐标"""
    return grid_x * CELL_SIZE + CELL_SIZE // 2, grid_y * CELL_SIZE + CELL_SIZE // 2


class Enemy:
    def __init__(self, enemy_type):
        self.type = enemy_type
        stats = ENEMY_TYPES[enemy_type]
        self.speed = stats["speed"]
        self.base_speed = stats["speed"]
        self.max_hp = stats["hp"]
        self.hp = self.max_hp
        self.reward = stats["reward"]
        self.color = stats["color"]
        self.size = stats["size"]
        self.path_index = 0
        self.x, self.y = get_center_grid(PATH_POINTS[0][0], PATH_POINTS[0][1])
        self.path_direction = 1
        self.slow_effect_time = 0
        self.slow_factor = 1.0
        self.dead = False

    def update(self, dt):
        if self.dead:
            return

        # 处理减速效果
        if self.slow_effect_time > 0:
            self.slow_effect_time -= dt
            self.slow_factor = ENEMY_TYPES[self.type]["speed"] / self.base_speed * 0.5
            if self.slow_effect_time <= 0:
                self.slow_factor = 1.0

        # 移动到下一个路径点
        if self.path_index < len(PATH_POINTS) - 1:
            curr_x, curr_y = PATH_POINTS[self.path_index]
            next_x, next_y = PATH_POINTS[self.path_index + 1]
            target_x, target_y = get_center_grid(next_x, next_y)

            # 当前位置
            curr_center = get_center_grid(curr_x, curr_y)

            # 计算方向向量
            dx = target_x - curr_center[0]
            dy = target_y - curr_center[1]
            distance = math.sqrt(dx * dx + dy * dy)

            if distance > self.speed * self.slow_factor * dt * 60:
                angle = math.atan2(dy, dx)
                self.x += math.cos(angle) * self.speed * self.slow_factor * dt * 60
                self.y += math.sin(angle) * self.speed * self.slow_factor * dt * 60
            else:
                self.x = target_x
                self.y = target_y
                self.path_index += 1
        else:
            self.dead = True

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.dead = True
            return self.reward
        return 0

    def apply_slow(self, slow_duration):
        self.slow_effect_time = slow_duration

    def draw(self, surface):
        if self.dead:
            return
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        # HP条
        hp_bar_width = self.size * 2
        hp_ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, RED, (int(self.x - self.size), int(self.y - self.size - 5), hp_bar_width, 4))
        pygame.draw.rect(surface, GREEN, (int(self.x - self.size), int(self.y - self.size - 5), hp_bar_width * hp_ratio, 4))


class Tower:
    def __init__(self, x, y, tower_type):
        self.grid_x = x
        self.grid_y = y
        self.center_x, self.center_y = get_center_grid(x, y)
        self.tower_type = tower_type
        self.level = 1
        self.last_fire_time = 0
        self.firing = False
        self.range = TOWER_TYPES[tower_type]["range"]
        self.damage = TOWER_TYPES[tower_type]["damage"]
        self.fire_rate = TOWER_TYPES[tower_type]["fire_rate"]
        self.color = TOWER_TYPES[tower_type]["color"]
        self.type = TOWER_TYPES[tower_type]["type"]
        if self.type == "splash":
            self.splash_radius = TOWER_TYPES[tower_type]["splash"]
        if self.type == "slow":
            self.slow_duration = TOWER_TYPES[tower_type]["slow_duration"]

    def upgrade(self):
        if self.level < 2:
            self.level += 1
            base_range = TOWER_TYPES[self.tower_type]["range"]
            base_damage = TOWER_TYPES[self.tower_type]["damage"]
            self.range = base_range + 10 * (self.level - 1)
            self.damage = base_damage + 2 * (self.level - 1)
            if self.tower_type == 2:  # Cannon
                self.splash_radius = TOWER_TYPES[2]["splash"] + 5 * (self.level - 1)

    def fire(self, current_time, enemies, projectiles, towers_update):
        if current_time - self.last_fire_time < self.fire_rate:
            return False

        target = None
        # 选择最靠近基地的目标
        min_dist_to_base = float('inf')
        for enemy in enemies:
            if enemy.dead:
                continue
            dx = enemy.x - self.center_x
            dy = enemy.y - self.center_y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist <= self.range:
                dist_to_base = math.sqrt((enemy.x - get_center_grid(*BASE_POS)[0]) ** 2 +
                                         (enemy.y - get_center_grid(*BASE_POS)[1]) ** 2)
                if dist_to_base < min_dist_to_base:
                    min_dist_to_base = dist_to_base
                    target = enemy

        if target:
            self.last_fire_time = current_time
            self.firing = True
            projectiles.append(Projectile(self.center_x, self.center_y, target, self))
            return True
        else:
            self.firing = False
            return False

    def draw(self, surface):
        if self.level == 1:
            base_color = self.color
        else:
            base_color = (min(255, self.color[0] + 50), min(255, self.color[1] + 50), min(255, self.color[2] + 50))
        pygame.draw.rect(surface, base_color, (self.center_x - CELL_SIZE // 3, self.center_y - CELL_SIZE // 3, 2 * CELL_SIZE // 3, 2 * CELL_SIZE // 3))
        pygame.draw.rect(surface, BLACK, (self.center_x - CELL_SIZE // 3, self.center_y - CELL_SIZE // 3, 2 * CELL_SIZE // 3, 2 * CELL_SIZE // 3), 2)
        # 显示等级
        font = pygame.font.SysFont(None, 16)
        level_text = font.render(f"Lv{self.level}", True, WHITE)
        surface.blit(level_text, (self.center_x - level_text.get_width() // 2, self.center_y - level_text.get_height() // 2))
        # 发射状态指示
        if self.firing:
            pygame.draw.circle(surface, WHITE, (self.center_x, self.center_y), 5, 0)


class Projectile:
    def __init__(self, x, y, target, tower):
        self.x = x
        self.y = y
        self.target = target
        self.tower = tower
        self.speed = 6  # 简单固定速度
        self.active = True
        self.hit = False
        self.color = WHITE if tower.tower_type == 1 else (139, 69, 19)  # Cannon is brown

    def update(self, dt):
        if not self.active:
            return

        # 如果目标已死，直接销毁
        if self.target.dead:
            self.active = False
            return

        # 计算到目标的距离
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < self.speed:
            self.x = self.target.x
            self.y = self.target.y
            self.hit = True
        else:
            angle = math.atan2(dy, dx)
            self.x += math.cos(angle) * self.speed
            self.y += math.sin(angle) * self.speed

    def apply_effect(self):
        if self.tower.type == "single":
            return self.tower.damage
        elif self.tower.type == "splash":
            return self.tower.damage
        elif self.tower.type == "slow":
            return self.tower.damage
        return 0

    def draw(self, surface):
        if self.active:
            if self.tower.tower_type == 1:  # Arrow
                pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 3)
                pygame.draw.line(surface, WHITE, (self.x, self.y), (self.target.x, self.target.y), 1)
            elif self.tower.tower_type == 2:  # Cannon
                pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), 4)
            elif self.tower.tower_type == 3:  # Slow
                pygame.draw.circle(surface, PURPLE, (int(self.x), int(self.y)), 2)


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.gold = 180
        self.lives = 20
        self.wave_number = 1
        self.enemies = []
        self.towers = []
        self.projectiles = []
        self.wave_enemies_remaining = 0
        self.wave_queue = []
        self.wave_active = False
        self.wave_interval_time = 0
        self.wave_interval_ready = True
        self.last_wave_time = 0
        self.game_state = GAME_RUNNING
        self.wave_over = False
        self.selected_tower = 1  # 1: Arrow, 2: Cannon, 3: Slow
        self.hovered_cell = None
        self.mouse_x, self.mouse_y = 0, 0
        self.font = pygame.font.SysFont(None, 20)
        random.seed(42)

    def start_wave(self):
        if self.wave_number <= len(WAVES):
            wave_data = WAVES[self.wave_number - 1]
            if isinstance(wave_data, tuple):
                # 处理单一波次，如第一、二、三波
                count, type_name = wave_data, "normal"
                self.wave_queue = [type_name] * count
            else:
                # 处理多敌人波次，如第四、五波
                enemies_to_add = []
                for data in wave_data:
                    count, type_name = data
                    enemies_to_add.extend([type_name] * count)
                self.wave_queue = enemies_to_add
            self.wave_enemies_remaining = len(self.wave_queue)
            self.wave_active = True
            self.wave_over = False
        else:
            self.game_state = VICTORY

    def spawn_enemy(self):
        if self.wave_queue and self.wave_enemies_remaining > 0:
            enemy_type = self.wave_queue.pop(0)
            self.enemies.append(Enemy(enemy_type))
            self.wave_enemies_remaining -= 1

    def update(self, dt):
        if self.game_state == GAME_OVER or self.game_state == VICTORY:
            return

        if self.wave_interval_ready and not self.wave_active:
            self.wave_interval_time += dt
            if self.wave_interval_time >= 3:
                self.wave_interval_time = 0
                self.wave_active = True
                self.wave_interval_ready = False
                self.start_wave()

        if self.wave_active and self.wave_over:
            self.wave_interval_ready = True
            if self.wave_number < len(WAVES):
                self.wave_number += 1
            self.wave_active = False
            self.wave_over = False
            return

        # 生成敌人
        if self.wave_active and len(self.enemies) < len(WAVES[self.wave_number - 1]) if isinstance(WAVES[self.wave_number - 1], tuple) else sum(x[0] for x in WAVES[self.wave_number - 1]):
            self.spawn_enemy()

        # 更新敌人
        for enemy in self.enemies[:]:
            enemy.update(dt)
            if enemy.dead:
                # 检查是否到达基地
                if enemy.path_index >= len(PATH_POINTS) - 1:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_state = GAME_OVER
                else:
                    # 获得奖励
                    gold_reward = enemy.take_damage(0)  # 检查是否死亡
                    if gold_reward > 0:
                        self.gold += gold_reward
                self.enemies.remove(enemy)

        # 检查本波次是否结束
        if self.wave_active and not self.wave_queue and self.wave_enemies_remaining <= 0 and not any(not e.dead for e in self.enemies):
            self.wave_over = True

        # 检查是否全部波次结束
        if self.wave_number > len(WAVES) and self.game_state != VICTORY and self.lives > 0 and not self.enemies:
            self.game_state = VICTORY

        # 升级塔逻辑处理（右键）
        if self.mouse_x < MAP_WIDTH and self.mouse_y < MAP_HEIGHT:
            grid_x = self.mouse_x // CELL_SIZE
            grid_y = self.mouse_y // CELL_SIZE
            for tower in self.towers:
                if tower.grid_x == grid_x and tower.grid_y == grid_y:
                    if self.right_click_down:
                        if self.gold >= TOWER_TYPES[tower.tower_type]["upgrade_cost"] and tower.level < 2:
                            self.gold -= TOWER_TYPES[tower.tower_type]["upgrade_cost"]
                            tower.upgrade()

        # 建造塔逻辑（左键）
        if self.mouse_x < MAP_WIDTH and self.mouse_y < MAP_HEIGHT:
            grid_x = self.mouse_x // CELL_SIZE
            grid_y = self.mouse_y // CELL_SIZE
            if self.left_click_down and self.game_state == GAME_RUNNING:
                if not any(t.grid_x == grid_x and t.grid_y == grid_y for t in self.towers):
                    if (grid_x, grid_y) not in PATH_GRID and (grid_x, grid_y) != BASE_POS:
                        tower_type = self.selected_tower
                        if self.gold >= TOWER_TYPES[tower_type]["cost"]:
                            self.gold -= TOWER_TYPES[tower_type]["cost"]
                            self.towers.append(Tower(grid_x, grid_y, tower_type))
                self.left_click_down = False

        # 更新塔
        current_time = 0
        for tower in self.towers:
            tower.fire(current_time, self.enemies, self.projectiles, None)

        # 更新弹道
        for proj in self.projectiles[:]:
            proj.update(dt)
            if proj.active and proj.hit:
                if proj.tower.type == "splash":
                    for enemy in self.enemies:
                        dx = enemy.x - proj.x
                        dy = enemy.y - proj.y
                        dist = math.sqrt(dx * dx + dy * dy)
                        if dist <= proj.tower.splash_radius:
                            reward = enemy.take_damage(proj.tower.damage)
                            if reward > 0:
                                self.gold += reward
                elif proj.tower.type == "slow":
                    reward = proj.target.take_damage(proj.tower.damage)
                    if reward > 0:
                        self.gold += reward
                    proj.target.apply_slow(proj.tower.slow_duration)
                else:  # single
                    reward = proj.target.take_damage(proj.tower.damage)
                    if reward > 0:
                        self.gold += reward
                proj.active = False
            elif not proj.active:
                self.projectiles.remove(proj)

        # 重置点击状态
        self.left_click_down = False
        self.right_click_down = False

    def draw(self, surface):
        # 绘制背景
        surface.fill(LIGHT_GRAY)

        # 绘制地图区域
        map_area = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)
        pygame.draw.rect(surface, DARK_GREEN, map_area)

        # 绘制网格
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                grid_rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, (60, 120, 60), grid_rect, 1)

        # 绘制路径
        for (gx, gy) in PATH_GRID:
            pygame.draw.rect(surface, GRAY, pygame.Rect(gx * CELL_SIZE, gy * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            if (gx, gy) == PATH_POINTS[0]:
                pygame.draw.rect(surface, BLUE, pygame.Rect(gx * CELL_SIZE, gy * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif (gx, gy) == BASE_POS:
                pygame.draw.rect(surface, BROWN, pygame.Rect(gx * CELL_SIZE, gy * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # 绘制基地
        bx, by = BASE_POS
        base_rect = pygame.Rect(bx * CELL_SIZE, by * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, BLACK, base_rect)
        font = pygame.font.SysFont(None, 24)
        base_text = font.render("BASE", True, WHITE)
        surface.blit(base_text, (bx * CELL_SIZE + (CELL_SIZE - base_text.get_width()) // 2,
                                 by * CELL_SIZE + (CELL_SIZE - base_text.get_height()) // 2))

        # 绘制塔
        for tower in self.towers:
            tower.draw(surface)

        # 绘制敌人
        for enemy in self.enemies:
            enemy.draw(surface)

        # 绘制弹道
        for proj in self.projectiles:
            proj.draw(surface)

        # 绘制HUD
        hud_rect = pygame.Rect(MAP_WIDTH, 0, HUD_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(surface, LIGHT_GRAY, hud_rect)

        # 绘制HUD元素
        text_color = BLACK
        font = pygame.font.SysFont(None, 22)
        small_font = pygame.font.SysFont(None, 18)

        hud_text = [
            f"Gold: {self.gold}",
            f"Lives: {self.lives}",
            f"Wave: {self.wave_number}",
            f"Enemies: {len(self.enemies)}"
        ]
        y_start = 10
        for text in hud_text:
            render = font.render(text, True, text_color)
            surface.blit(render, (MAP_WIDTH + 10, y_start))
            y_start += 30

        # 塔选择面板
        y_start += 20
        render = small_font.render("Select Tower:", True, text_color)
        surface.blit(render, (MAP_WIDTH + 10, y_start))
        y_start += 25

        tower_info = [
            ("1: Arrow", 1),
            ("2: Cannon", 2),
            ("3: Slow", 3)
        ]
        for name, idx in tower_info:
            color = BLUE if idx == 1 else (BROWN if idx == 2 else PURPLE)
            if idx == self.selected_tower:
                pygame.draw.rect(surface, WHITE, (MAP_WIDTH + 10, y_start - 2, 140, 22))
            render = small_font.render(name, True, color)
            surface.blit(render, (MAP_WIDTH + 15, y_start))
            y_start += 25

        # 塔详细信息面板
        y_start += 15
        render = small_font.render("Selected:", True, text_color)
        surface.blit(render, (MAP_WIDTH + 10, y_start))
        y_start += 20

        selected = self.selected_tower
        if selected:
            info = TOWER_TYPES[selected]
            details = [
                f"Name: {info['name']}",
                f"Cost: {info['cost']}",
                f"Range: {info['range']}",
                f"Damage: {info['damage']}",
                f"Speed: {info['fire_rate']}"
            ]
            if info['type'] == 'splash':
                details.insert(4, f"Splash: {info['splash']}")
            elif info['type'] == 'slow':
                details[3] = f"Slow Duration: {info['slow_duration']}s"
            for detail in details:
                render = small_font.render(detail, True, text_color)
                surface.blit(render, (MAP_WIDTH + 10, y_start))
                y_start += 20

        # 游戏结束或胜利信息
        if self.game_state == GAME_OVER:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(RED)
            surface.blit(overlay, (0, 0))
            font = pygame.font.SysFont(None, 48)
            game_over_text = font.render("GAME OVER", True, WHITE)
            wave_text = small_font.render(f"Wave Reached: {self.wave_number}", True, WHITE)
            restart_text = small_font.render("Press R to Restart", True, WHITE)
            surface.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, 250))
            surface.blit(wave_text, (WINDOW_WIDTH // 2 - wave_text.get_width() // 2, 310))
            surface.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, 350))
        elif self.game_state == VICTORY:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(GREEN)
            surface.blit(overlay, (0, 0))
            font = pygame.font.SysFont(None, 48)
            victory_text = font.render("YOU WIN!", True, WHITE)
            wave_text = small_font.render(f"Final Wave: {self.wave_number}", True, WHITE)
            restart_text = small_font.render("Press R to Restart", True, WHITE)
            surface.blit(victory_text, (WINDOW_WIDTH // 2 - victory_text.get_width() // 2, 250))
            surface.blit(wave_text, (WINDOW_WIDTH // 2 - wave_text.get_width() // 2, 310))
            surface.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, 350))

        # 绘制悬停指示器
        if self.mouse_x < MAP_WIDTH and self.mouse_y < MAP_HEIGHT:
            mx = (self.mouse_x // CELL_SIZE) * CELL_SIZE
            my = (self.mouse_y // CELL_SIZE) * CELL_SIZE
            hovered_cell = (mx, my)
            pygame.draw.rect(surface, (200, 200, 255, 128), (mx, my, CELL_SIZE, CELL_SIZE), 2)

        # 显示射程框（仅在鼠标悬停时）
        if self.hovered_cell and self.selected_tower:
            grid_x, grid_y = self.hovered_cell
            center_xy = get_center_grid(grid_x, grid_y)
            tower_info = TOWER_TYPES[self.selected_tower]
            range_circle = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(range_circle, (255, 255, 255, 60), center_xy, tower_info["range"])
            surface.blit(range_circle, (0, 0))
            # 简单验证：如果位置无效，则显示红色边框
            grid_x = self.mouse_x // CELL_SIZE
            grid_y = self.mouse_y // CELL_SIZE
            if (grid_x, grid_y) in PATH_GRID or (grid_x, grid_y) == BASE_POS or \
                    any(t.grid_x == grid_x and t.grid_y == grid_y for t in self.towers):
                pygame.draw.rect(surface, RED, (grid_x * CELL_SIZE, grid_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)
            else:
                pygame.draw.rect(surface, GREEN, (grid_x * CELL_SIZE, grid_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)

    def run(self):
        self.left_click_down = False
        self.right_click_down = False
        running = True

        while running:
            dt = clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEMOTION:
                    self.mouse_x, self.mouse_y = event.pos
                    grid_x = self.mouse_x // CELL_SIZE
                    grid_y = self.mouse_y // CELL_SIZE
                    if 0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS:
                        self.hovered_cell = (grid_x, grid_y)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.left_click_down = True
                    elif event.button == 3:  # Right click
                        self.right_click_down = True

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        self.selected_tower = int(event.key - pygame.K_0)

            self.update(dt)
            self.draw(screen)
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()