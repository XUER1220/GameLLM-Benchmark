import pygame
import random
import math
import sys

# ===================== 常量定义 =====================
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# 地图设置
GRID_SIZE = 32
GRID_COLS = 20
GRID_ROWS = 15
MAP_WIDTH = GRID_COLS * GRID_SIZE  # 640
MAP_HEIGHT = GRID_ROWS * GRID_SIZE  # 480
HUD_WIDTH = WINDOW_WIDTH - MAP_WIDTH  # 160

# 随机种子
random.seed(42)

# 颜色常量
COLOR_BG = (20, 20, 30)
COLOR_GRID = (40, 40, 50)
COLOR_PATH = (130, 80, 40)
COLOR_PATH_BORDER = (160, 100, 60)
COLOR_BASE = (255, 40, 40)
COLOR_SPAWN = (40, 180, 255)
COLOR_ARROW_TOWER = (0, 180, 100)
COLOR_CANNON_TOWER = (80, 80, 200)
COLOR_SLOW_TOWER = (200, 200, 50)
COLOR_ENEMY_NORMAL = (200, 60, 60)
COLOR_ENEMY_FAST = (255, 180, 60)
COLOR_ENEMY_HEAVY = (60, 160, 200)
COLOR_TOWER_RANGE = (255, 255, 255, 100)
COLOR_TOWER_ATTACK = (255, 255, 0)
COLOR_HEALTH = (0, 200, 0)
COLOR_CURRENCY = (255, 215, 0)

# 塔类型定义
TOWERS = {
    'arrow': {
        'name': 'Arrow Tower',
        'cost': 50,
        'range': 120,
        'damage': 8,
        'rate': 0.8,
        'color': COLOR_ARROW_TOWER,
        'icon': 'A'
    },
    'cannon': {
        'name': 'Cannon Tower',
        'cost': 80,
        'range': 105,
        'damage': 14,
        'rate': 1.2,
        'splash': 45,
        'color': COLOR_CANNON_TOWER,
        'icon': 'C'
    },
    'slow': {
        'name': 'Slow Tower',
        'cost': 70,
        'range': 110,
        'damage': 4,
        'rate': 1.0,
        'slow': 2.0,
        'color': COLOR_SLOW_TOWER,
        'icon': 'S'
    }
}

# 敌人类别定义
ENEMIES = {
    'normal': {
        'name': 'Normal',
        'speed': 1.5,
        'max_health': 30,
        'reward': 15,
        'color': COLOR_ENEMY_NORMAL,
        'size': 14
    },
    'fast': {
        'name': 'Fast',
        'speed': 3.0,
        'max_health': 15,
        'reward': 10,
        'color': COLOR_ENEMY_FAST,
        'size': 10
    },
    'heavy': {
        'name': 'Heavy',
        'speed': 0.8,
        'max_health': 70,
        'reward': 25,
        'color': COLOR_ENEMY_HEAVY,
        'size': 18
    }
}

# 波次配置 (每波的敌人分布)
WAVES = [
    [('normal', 5)],
    [('normal', 8), ('fast', 3)],
    [('heavy', 3), ('normal', 6)],
    [('fast', 4), ('heavy', 4), ('normal', 2)],
    [('heavy', 5), ('fast', 8), ('normal', 10)]
]

# 游戏状态常量
STATE_PLAYING = 0
STATE_PREPARE = 1
STATE_END = 2

# 路径点（地图坐标系，32x32 网格坐标）
PATH_POINTS = [(0, 7), (5, 7), (5, 3), (12, 3), (12, 10), (19, 10)]
# 塔的初始升级费用比例
UPGRADE_COST_FACTOR = 0.7
MAX_UPGRADE_LEVEL = 2

# 初始化 Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tower Defense Hard")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)
font_large = pygame.font.SysFont("Arial", 32, bold=True)
font_small = pygame.font.SysFont("Arial", 14)


class Tower:
    def __init__(self, x, y, type_key):
        self.grid_x = x
        self.grid_y = y
        self.x = x * GRID_SIZE + GRID_SIZE // 2
        self.y = y * GRID_SIZE + GRID_SIZE // 2
        self.type_key = type_key
        self.info = TOWERS[type_key]
        self.cost = self.info['cost']
        self.level = 1
        self.range = self.info['range']
        self.damage = self.info['damage']
        self.rate = self.info['rate']
        self.last_attack_time = 0.0
        self.color = self.info['color']
        self.splash = self.info.get('splash', 0)
        self.slow = self.info.get('slow', 0)
        self.icon = self.info['icon']

    def upgrade(self):
        if self.level < MAX_UPGRADE_LEVEL:
            upgrade_cost = int(self.cost * UPGRADE_COST_FACTOR)
            self.level += 1
            self.damage = int(self.damage * 1.25)
            self.range = int(self.range * 1.1)
            self.rate = max(0.1, self.rate * 0.9)
            return upgrade_cost
        return 0

    def update(self, current_time, enemies, projectiles):
        if current_time - self.last_attack_time >= self.rate * 1000:
            target = self.find_target(enemies)
            if target:
                self.attack(target, current_time, projectiles)
                self.last_attack_time = current_time

    def find_target(self, enemies):
        # 选取最近的敌人
        if not enemies:
            return None
        nearest_enemy = None
        min_dist = float('inf')
        for enemy in enemies:
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist <= self.range and dist < min_dist:
                min_dist = dist
                nearest_enemy = enemy
        return nearest_enemy

    def attack(self, target, current_time, projectiles):
        projectiles.append(Projectile(self.x, self.y, target, self))


class Projectile:
    def __init__(self, x, y, target, tower):
        self.x = x
        self.y = y
        self.target = target
        self.tower = tower
        self.speed = 6.0
        self.hit = False
        self.duration = 1000  # ms
        self.start_time = pygame.time.get_ticks()

    def update(self, current_time, enemies):
        if self.hit or current_time - self.start_time > self.duration:
            return False
        if not self.target or self.target.dead:
            return False
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        if dist < self.speed:
            self.hit = True
            self.apply_effect()
            return True
        theta = math.atan2(dy, dx)
        self.x += math.cos(theta) * self.speed
        self.y += math.sin(theta) * self.speed
        return True

    def apply_effect(self):
        if self.tower.type_key == 'arrow':
            self.target.take_damage(self.tower.damage)
        elif self.tower.type_key == 'cannon':
            splash_r = self.tower.splash
            damage = self.tower.damage
            for enemy in enemies:
                dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
                if dist <= splash_r:
                    enemy.take_damage(damage)
        elif self.tower.type_key == 'slow':
            self.target.take_damage(self.tower.damage)
            self.target.apply_slow(self.tower.slow)


class Enemy:
    def __init__(self, type_key, wave):
        self.type_key = type_key
        self.info = ENEMIES[type_key]
        self.speed = self.info['speed']
        self.health = self.info['max_health']
        self.max_health = self.info['max_health']
        self.reward = self.info['reward']
        self.color = self.info['color']
        self.size = self.info['size']
        self.dead = False
        self.path_index = 0
        self.x, self.y = self.get_path_position(0)
        self.slow_duration = 0
        self.slow_factor = 1.0
        self.slow_remaining = 0
        self.wave = wave

    def get_path_position(self, index):
        if index >= len(PATH_POINTS) - 1:
            return PATH_POINTS[-1]
        x1, y1 = PATH_POINTS[index]
        x2, y2 = PATH_POINTS[index + 1]
        ratio = (index - self.path_index) if self.path_index == index else 0
        cx = (x1 + x2) // 2 * GRID_SIZE + GRID_SIZE // 2
        cy = (y1 + y2) // 2 * GRID_SIZE + GRID_SIZE // 2
        return cx, cy

    def update(self, dt):
        if self.dead:
            return

        # 处理减速
        if self.slow_duration > 0:
            self.slow_duration -= dt / 1000.0
            if self.slow_duration <= 0:
                self.slow_factor = 1.0

        current_speed = self.speed * self.slow_factor

        # 移动
        current_x, current_y = self.x, self.y
        if self.path_index < len(PATH_POINTS) - 1:
            next_point = PATH_POINTS[self.path_index + 1]
            next_x = next_point[0] * GRID_SIZE + GRID_SIZE // 2
            next_y = next_point[1] * GRID_SIZE + GRID_SIZE // 2

            dx = next_x - current_x
            dy = next_y - current_y
            dist = math.hypot(dx, dy)

            if dist <= current_speed:
                self.path_index += 1
                self.x = next_x
                self.y = next_y
            else:
                angle = math.atan2(dy, dx)
                self.x += math.cos(angle) * current_speed
                self.y += math.sin(angle) * current_speed

        # 检查是否到达基地
        if self.path_index >= len(PATH_POINTS) - 1:
            self.dead = True
            return 'end'

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.dead = True

    def apply_slow(self, duration):
        if self.slow_duration <= 0:
            self.slow_factor = 0.5
        self.slow_duration = duration

    def get_health_bar_rect(self):
        bar_width = 24
        bar_height = 4
        x = self.x - bar_width // 2
        y = self.y - self.size - 8
        return (x, y, bar_width, bar_height)

    def draw(self, screen):
        if not self.dead:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
            # 血条
            hp_bar = self.get_health_bar_rect()
            hp_ratio = self.health / self.max_health
           pygame.draw.rect(screen, (100, 0, 0), (hp_bar[0] - 1, hp_bar[1] - 1, hp_bar[2] + 2, hp_bar[3] + 2))
            pygame.draw.rect(screen, (0, 150, 0), (hp_bar[0], hp_bar[1], int(hp_bar[2] * hp_ratio), hp_bar[3]))


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.grid = [[None for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]
        self.path_set = set()
        self.base_pos = (PATH_POINTS[-1][0] * GRID_SIZE + GRID_SIZE // 2, PATH_POINTS[-1][1] * GRID_SIZE + GRID_SIZE // 2)

        # 填充路径格子
        for i in range(len(PATH_POINTS) - 1):
            x1, y1 = PATH_POINTS[i]
            x2, y2 = PATH_POINTS[i + 1]
            dx = 1 if x2 > x1 else -1 if x2 < x1 else 0
            dy = 1 if y2 > y1 else -1 if y2 < y1 else 0
            x, y = x1, y1
            while True:
                self.path_set.add((x, y))
                if x == x2 and y == y2:
                    break
                if x != x2:
                    x += dx
                if y != y2:
                    y += dy

        self.enemies = []
        self.towers = []
        self.projectiles = []
        self.money = 180
        self.lives = 20
        self.wave = 0
        self.wave_state = STATE_PLAYING
        self.wave_time = 0.0
        self.wave_preparation_time = 0
        self.game_over = False
        self.wave_end_time = 0.0
        self.selected_tower = 'arrow'
        self.mouse_grid = (-1, -1)
        self.selected_upgrade_tower = None

    def spawn_wave(self):
        if self.wave >= len(WAVES):
            return
        wave_enemies = WAVES[self.wave]
        total = 0
        for _, count in wave_enemies:
            total += count
        enemy_queue = []
        for type_key, count in wave_enemies:
            enemy_queue.extend([type_key] * count)
        random.shuffle(enemy_queue)
        spawn_time = 2000  # 每个敌人生成间隔
        self.wave_total_enemies = total
        self.wave_spawned = 0
        self.wave_killed = 0
        self.enemy_queue = enemy_queue
        self.spawn_timer = 0
        self.spawn_interval = 2000

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return 'quit'
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'quit'
                elif event.key == pygame.K_r:
                    self.reset()
                    self.wave_state = STATE_PLAYING
                    self.wave_time = 0.0
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                if mx < MAP_WIDTH and my < MAP_HEIGHT:
                    gx = mx // GRID_SIZE
                    gy = my // GRID_SIZE
                    if 0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS:
                        self.mouse_grid = (gx, gy)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if mx < MAP_WIDTH and my < MAP_HEIGHT:
                    gx = mx // GRID_SIZE
                    gy = my // GRID_SIZE
                    if 0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS:
                        if event.button == 1:  # 左键建造
                            if self.grid[gx][gy] is None and (gx, gy) not in self.path_set:
                                if self.money >= TOWERS[self.selected_tower]['cost']:
                                    self.build_tower(gx, gy)
                        elif event.button == 3:  # 右键升级
                            if self.grid[gx][gy] is not None:
                                self.try_upgrade_tower(gx, gy)
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    keys = ['arrow', 'cannon', 'slow']
                    idx = event.key - pygame.K_1
                    if 0 <= idx < 3:
                        self.selected_tower = keys[idx]

    def build_tower(self, gx, gy):
        cost = TOWERS[self.selected_tower]['cost']
        if self.money >= cost:
            self.money -= cost
            self.grid[gx][gy] = Tower(gx, gy, self.selected_tower)
            self.towers.append(self.grid[gx][gy])

    def try_upgrade_tower(self, gx, gy):
        tower = self.grid[gx][gy]
        if tower and tower.level < MAX_UPGRADE_LEVEL:
            cost = int(tower.cost * UPGRADE_COST_FACTOR)
            if self.money >= cost:
                self.money -= cost
                upgraded_cost = tower.upgrade()
                self.money = max(0, self.money + upgraded_cost)  # 实际上升级不退款，但逻辑中已扣除

    def update(self, dt, current_time):
        if self.game_over:
            return

        if self.wave_state == STATE_PREPARE:
            self.wave_preparation_time -= dt / 1000.0
            if self.wave_preparation_time <= 0:
                self.wave_state = STATE_PLAYING
                self.spawn_wave()
            return

        if self.wave_state == STATE_END:
            if current_time - self.wave_end_time > 2000:
                self.wave += 1
                if self.wave >= len(WAVES):
                    # 胜利
                    self.game_over = True
                    self.win = True
                else:
                    self.wave_state = STATE_PLAYING
                    self.spawn_wave()
            return

        # 波次生成逻辑
        if self.wave_state == STATE_PLAYING:
            if self.wave == 0 and self.wave_time == 0:
                self.spawn_wave()
            if self.wave > 0 and self.wave_time == 0:
                self.wave_time = current_time

            if self.enemy_queue and self.spawn_timer > self.spawn_interval:
                type_key = self.enemy_queue.pop(0)
                enemy = Enemy(type_key, self.wave)
                self.enemies.append(enemy)
                self.wave_spawned += 1
                self.spawn_timer = 0
            else:
                self.spawn_timer += dt

            # 检查是否生成完毕
            if not self.enemy_queue and self.wave_spawned > 0 and self.wave_killed >= self.wave_spawned:
                if not self.wave_end_time:
                    self.wave_end_time = current_time
                    self.wave_state = STATE_END
                else:
                    self.wave_state = STATE_END
                return

        # 敌人更新
        new_enemies = []
        for enemy in self.enemies:
            result = enemy.update(dt)
            if result == 'end':
                self.lives -= 1
                self.enemies.remove(enemy)
                continue
            if enemy.dead:
                self.money += enemy.reward
                self.enemies.remove(enemy)
                self.wave_killed += 1
                continue
            new_enemies.append(enemy)
        self.enemies = new_enemies

        if self.lives <= 0:
            self.game_over = True
            self.win = False

        # 塔更新
        for tower in self.towers:
            tower.update(current_time, self.enemies, self.projectiles)

        # 箭矢更新
        new_projectiles = []
        for proj in self.projectiles:
            if proj.update(current_time, self.enemies):
                new_projectiles.append(proj)
        self.projectiles = new_projectiles

    def draw_map(self, screen):
        # 绘制网格背景
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, COLOR_GRID if (x, y) not in self.path_set else COLOR_PATH, rect, 0)

        # 绘制路径（边框增强）
        for gx, gy in self.path_set:
            rect = pygame.Rect(gx * GRID_SIZE, gy * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, COLOR_PATH_BORDER, rect, 2)

        # 绘制入口和基地
        spawn_x, spawn_y = PATH_POINTS[0]
        pygame.draw.rect(screen, COLOR_SPAWN, (spawn_x * GRID_SIZE, spawn_y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        base_x, base_y = PATH_POINTS[-1]
        pygame.draw.rect(screen, COLOR_BASE, (base_x * GRID_SIZE, base_y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        # 基地图标（十字）
        cx, cy = base_x * GRID_SIZE + GRID_SIZE // 2, base_y * GRID_SIZE + GRID_SIZE // 2
        pygame.draw.line(screen, (255, 255, 255), (cx - 5, cy - 10), (cx + 5, cy - 10), 2)
        pygame.draw.line(screen, (255, 255, 255), (cx - 10, cy - 5), (cx - 10, cy + 5), 2)
        pygame.draw.line(screen, (255, 255, 255), (cx + 5, cy - 10), (cx + 5, cy + 5), 2)

    def draw_towers(self, screen, mouse_gx, mouse_gy):
        # 绘制塔
        for tower in self.towers:
            pygame.draw.circle(screen, tower.color, (int(tower.x), int(tower.y)), GRID_SIZE // 2 - 4)
            # 显示等级
            level_text = font_small.render(f"Lv{tower.level}", True, (255, 255, 255))
            text_rect = level_text.get_rect(center=(tower.x, tower.y + 6))
            screen.blit(level_text, text_rect)

        # 绘制塔的射程（悬停效果）
        if mouse_gx >= 0 and mouse_gx < GRID_COLS and mouse_gy >= 0 and mouse_gy < GRID_ROWS:
            if (mouse_gx, mouse_gy) not in self.path_set and self.grid[mouse_gx][mouse_gy] is None:
                cx = mouse_gx * GRID_SIZE + GRID_SIZE // 2
                cy = mouse_gy * GRID_SIZE + GRID_SIZE // 2
                range_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                pygame.draw.circle(range_surface, COLOR_TOWER_RANGE, (cx, cy), TOWERS[self.selected_tower]['range'])
                screen.blit(range_surface, (0, 0))

        # 绘制被选中升级的塔的射程
        if self.selected_upgrade_tower:
            tower = self.selected_upgrade_tower
            range_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(range_surface, (255, 255, 255, 150), (int(tower.x), int(tower.y)), tower.range, 2)
            screen.blit(range_surface, (0, 0))

    def draw_enemies(self, screen):
        for enemy in self.enemies:
            enemy.draw(screen)

    def draw_projectiles(self, screen):
        for proj in self.projectiles:
            if not proj.hit:
                pygame.draw.line(screen, COLOR_TOWER_ATTACK, (proj.x, proj.y),
                                 (proj.target.x, proj.target.y), 2)

    def draw_hud(self, screen):
        # HUD 区域（右侧 160px）
        hud_rect = pygame.Rect(MAP_WIDTH, 0, HUD_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(screen, (30, 30, 45), hud_rect)

        y = 20
        # 游戏信息
        lines = [
            ("Money:", self.money),
            ("Lives:", self.lives),
            ("Wave:", self.wave + 1 if self.wave < len(WAVES) else f"{len(WAVES)} (Final)"),
        ]
        for text, value in lines:
            label = font.render(text, True, (255, 255, 255))
            screen.blit(label, (MAP_WIDTH + 10, y))
            value_text = font.render(str(value), True, (255, 215, 0))
            screen.blit(value_text, (MAP_WIDTH + 100, y))
            y += 25

        # 波次状态
        if self.wave_state == STATE_PREPARE:
            prepare_text = f"Next Wave in {max(0, self.wave_preparation_time):.1f}s"
            label = font.render(prepare_text, True, (255, 0, 255))
            screen.blit(label, (MAP_WIDTH + 10, y + 25))
        elif self.wave_state == STATE_END:
            label = font.render("Wave Complete!", True, (0, 255, 0))
            screen.blit(label, (MAP_WIDTH + 10, y + 25))

        y += 5

        # 塔建造面板
        y += 25
        label = font.render("Select Tower:", True, (200, 200, 200))
        screen.blit(label, (MAP_WIDTH + 10, y))

        for idx, key in enumerate('arrow', 'cannon', 'slow'):
            info = TOWERS[key]
            y += 40
            color = COLOR_TOWER_RANGE if self.selected_tower == key else (100, 100, 100)
            pygame.draw.rect(screen, info['color'], (MAP_WIDTH + 10, y, 20, 20))
            label = font.render(f"{info['name']} (Key {idx + 1})", True, (255, 255, 255))
            screen.blit(label, (MAP_WIDTH + 40, y))
            cost_label = font.render(f"Cost: {info['cost']}", True, (255, 215, 0))
            screen.blit(cost_label, (MAP_WIDTH + 40, y + 18))

        # 说明信息
        y += 50
        instructions = [
            "Left Click: Build",
            "Right Click: Upgrade",
            "Key R: Restart",
            "Key ESC: Quit"
        ]
        for inst in instructions:
            label = font_small.render(inst, True, (180, 180, 180))
            screen.blit(label, (MAP_WIDTH + 10, y))
            y += 18

        # 胜利/失败信息
        if self.game_over:
            win_lose_text = "YOU WIN!" if self.win else "GAME OVER"
            text = font_large.render(win_lose_text, True, (255, 255, 0))
            rect = text.get_rect(center=(MAP_WIDTH + HUD_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
            screen.blit(text, rect)
            restart_text = font.render("Press R to Restart", True, (255, 255, 255))
            rect = restart_text.get_rect(center=(MAP_WIDTH + HUD_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
            screen.blit(restart_text, rect)

        # 当前选中鼠标位置塔的射程（单击）
        if self.selected_upgrade_tower and self.selected_upgrade_tower.level < MAX_UPGRADE_LEVEL:
            upgrade_text = font.render(f"Upgrade ({int(self.selected_upgrade_tower.cost * UPGRADE_COST_FACTOR)} G)",
                                       True, (0, 255, 0))
            screen.blit(upgrade_text, (MAP_WIDTH + 10, WINDOW_HEIGHT - 50))

    def draw(self, screen):
        screen.fill(COLOR_BG)
        self.draw_map(screen)
        self.draw_towers(screen, self.mouse_grid[0], self.mouse_grid[1])
        self.draw_enemies(screen)
        self.draw_projectiles(screen)
        self.draw_hud(screen)
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            events = pygame.event.get()
            result = self.handle_input(events)
            if result == 'quit':
                running = False

            current_time = pygame.time.get_ticks()
            dt = clock.tick(FPS)
            self.update(dt, current_time)
            self.draw(screen)

        pygame.quit()
        sys.exit()


# 主程序入口
if __name__ == "__main__":
    game = Game()
    game.run()