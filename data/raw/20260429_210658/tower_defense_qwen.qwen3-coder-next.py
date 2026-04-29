import pygame
import random
import sys

# 常量定义
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 32
MAP_COLS, MAP_ROWS = 20, 15
MAP_WIDTH, MAP_HEIGHT = TILE_SIZE * MAP_COLS, TILE_SIZE * MAP_ROWS
HUD_WIDTH = WIDTH - MAP_WIDTH

# 颜色
BG_COLOR = (34, 45, 50)
PATH_COLOR = (160, 120, 70)
ENTRY_COLOR = (200, 180, 100)
BASE_COLOR = (150, 30, 30)
ARROW_TOWER_COLOR = (50, 150, 200)
CANNON_TOWER_COLOR = (200, 100, 50)
SLOW_TOWER_COLOR = (50, 200, 150)
GRASS_COLOR = (60, 80, 60)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
TEXT_COLOR = (255, 255, 255)

# 塔类型常量
TOWER_ARROW = "Arrow"
TOWER_CANNON = "Cannon"
TOWER_SLOW = "Slow"

# 敌人类别
ENEMY_REGULAR = "Regular"
ENEMY_FAST = "Fast"
ENEMY_HEAVY = "Heavy"

# 随机种子
random.seed(42)

# 初始化Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense Hard")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
small_font = pygame.font.SysFont(None, 20)

# 定义塔参数
TOWER_STATS = {
    TOWER_ARROW: {
        "cost": 50,
        "range": 120,
        "damage": 8,
        "fire_rate": 0.8,
        "color": ARROW_TOWER_COLOR
    },
    TOWER_CANNON: {
        "cost": 80,
        "range": 105,
        "damage": 14,
        "fire_rate": 1.2,
        "splash_radius": 45,
        "color": CANNON_TOWER_COLOR
    },
    TOWER_SLOW: {
        "cost": 70,
        "range": 110,
        "damage": 4,
        "fire_rate": 1.0,
        "slow_duration": 2,
        "color": SLOW_TOWER_COLOR
    }
}

# 定义敌人参数
ENEMY_STATS = {
    ENEMY_REGULAR: {
        "hp": 40,
        "speed": 1.0,
        "reward": 12
    },
    ENEMY_FAST: {
        "hp": 20,
        "speed": 2.0,
        "reward": 8
    },
    ENEMY_HEAVY: {
        "hp": 100,
        "speed": 0.6,
        "reward": 20
    }
}

# 固定路径点（20列 x 15行，坐标转换为像素)
PATH_POINTS = [
    (0, 2), (3, 2), (3, 7), (8, 7), (8, 3),
    (12, 3), (12, 9), (16, 9), (16, 6), (18, 6), (18, 12), (19, 12)
]
PATH_POINTS_PIXEL = [(px * TILE_SIZE, py * TILE_SIZE) for px, py in PATH_POINTS]

# 路径格子集合（用于判断建塔合法性）
path_tiles = set()
for i in range(len(PATH_POINTS) - 1):
    x1, y1 = PATH_POINTS[i]
    x2, y2 = PATH_POINTS[i + 1]
    dx, dy = x2 - x1, y2 - y1
    steps = max(abs(dx), abs(dy))
    for t in range(steps + 1):
        t_prog = t / steps if steps > 0 else 0
        px = round(x1 + dx * t_prog)
        py = round(y1 + dy * t_prog)
        path_tiles.add((px, py))

# 入口格子
entry_tile = PATH_POINTS[0]

# 基地格子
base_tile = PATH_POINTS[-1]

# 波次配置（固定）
WAVE_ENEMIES = [
    [(ENEMY_REGULAR, 8), (ENEMY_FAST, 4)],
    [(ENEMY_REGULAR, 10), (ENEMY_FAST, 6), (ENEMY_HEAVY, 2)],
    [(ENEMY_REGULAR, 12), (ENEMY_FAST, 8), (ENEMY_HEAVY, 4)],
    [(ENEMY_REGULAR, 15), (ENEMY_FAST, 10), (ENEMY_HEAVY, 6)],
    [(ENEMY_REGULAR, 20), (ENEMY_FAST, 12), (ENEMY_HEAVY, 8)]
]

WAVE_INTERVAL = 3  # 波次间隔秒数

# 游戏状态变量
game_state = "playing"  # 'playing', 'win', 'lose'
money = 180
lives = 20
current_wave = 0
wave_remaining = 0
wave_spawned = 0
wave_next_time = 0
selected_tower_type = TOWER_ARROW
last_enemy_spawn_time = 0
enemies = []
towers = []
projectiles = []
selected_towers = set()  # 被选中的塔
show_ranges = False

class Enemy:
    def __init__(self, enemy_type):
        stats = ENEMY_STATS[enemy_type]
        self.type = enemy_type
        self.hp = stats["hp"]
        self.max_hp = stats["hp"]
        self.speed = stats["speed"]
        self.reward = stats["reward"]
        self.path_index = 0
        self.pixel_pos = list(PATH_POINTS_PIXEL[0])
        # 移动进度（从 0 到 1）
        self.progress = 0.0
        self.slow_timer = 0
        self.slow_multiplier = 1.0
        self.radius = TILE_SIZE // 2 - 4
        self.dead = False
        self.reached_base = False

    def update(self):
        if self.dead or self.reached_base:
            return

        # 处理减速效果
        if self.slow_timer > 0:
            self.slow_timer -= 1 / 60
            if self.slow_timer <= 0:
                self.slow_multiplier = 1.0

        # 移动
        current_pos = PATH_POINTS_PIXEL[self.path_index]
        next_pos = PATH_POINTS_PIXEL[self.path_index + 1] if self.path_index + 1 < len(PATH_POINTS_PIXEL) else None
        if next_pos is None:
            self.reached_base = True
            return

        dx = next_pos[0] - current_pos[0]
        dy = next_pos[1] - current_pos[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5
        speed_actual = self.speed * self.slow_multiplier

        if self.progress < 1.0:
            step = speed_actual / TILE_SIZE
            self.progress += step
            self.pixel_pos[0] = current_pos[0] + dx * self.progress
            self.pixel_pos[1] = current_pos[1] + dy * self.progress
            if self.progress >= 1.0:
                self.path_index += 1
                self.progress = 0.0
        else:
            self.path_index += 1
            self.progress = 0.0

        # 检查是否到达基地
        if self.path_index >= len(PATH_POINTS_PIXEL) - 1:
            self.reached_base = True

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.dead = True
            return True  # 被击杀
        return False

    def apply_slow(self, slow_duration):
        self.slow_multiplier = 0.5
        self.slow_timer = slow_duration

    def draw(self, surface):
        if self.dead or self.reached_base:
            return
        pygame.draw.circle(surface, self._get_color(), (int(self.pixel_pos[0] + TILE_SIZE/2), int(self.pixel_pos[1] + TILE_SIZE/2)), int(self.radius))
        # 生命条
        bar_width = TILE_SIZE
        if self.max_hp > 0:
            hp_bar = int((self.hp / self.max_hp) * bar_width)
            if hp_bar > 0:
                pygame.draw.rect(surface, GREEN, (self.pixel_pos[0], self.pixel_pos[1], hp_bar, 4))
                if hp_bar < bar_width:
                    pygame.draw.rect(surface, RED, (self.pixel_pos[0] + hp_bar, self.pixel_pos[1], bar_width - hp_bar, 4))

    def _get_color(self):
        if self.type == ENEMY_REGULAR:
            return (200, 50, 50)
        elif self.type == ENEMY_FAST:
            return (255, 255, 50)
        else:  # HEAVY
            return (100, 100, 255)


class Tower:
    def __init__(self, x, y, tower_type):
        self.x = x
        self.y = y
        self.tower_type = tower_type
        self.level = 1
        self.stats = TOWER_STATS[tower_type].copy()
        self.last_fire_time = 0
        self.angle = 0
        # 确保范围等与当前等级一致（每次升级增加一定数值）
        self.max_level = 2

    def upgrade(self):
        if self.level < self.max_level:
            self.level += 1
            # 增强属性
            self.stats["damage"] = int(self.stats["damage"] * 1.2)
            self.stats["range"] = int(self.stats["range"] * 1.1)
            # 基础射程/伤害升级幅度
            if self.tower_type == TOWER_CANNON:
                self.stats["splash_radius"] = int(self.stats["splash_radius"] * 1.1)
            # 重置火控 timer
            self.last_fire_time = pygame.time.get_ticks()
            return True
        return False

    def can_afford_upgrade(self):
        # 升级花费为原始价格的 70%
        base_cost = TOWER_STATS[self.tower_type]["cost"]
        return base_cost * 7 // 10

    def get_cost(self):
        return self.stats.get("cost", TOWER_STATS[self.tower_type]["cost"])

    def update(self, enemies, current_time):
        candidates = []
        for enemy in enemies:
            if enemy.dead or enemy.reached_base:
                continue
            # 计算距离
            ex = enemy.pixel_pos[0] + TILE_SIZE // 2
            ey = enemy.pixel_pos[1] + TILE_SIZE // 2
            tx = self.x + TILE_SIZE // 2
            ty = self.y + TILE_SIZE // 2
            dx, dy = ex - tx, ey - ty
            dist = (dx * dx + dy * dy) ** 0.5
            if dist <= self.stats["range"]:
                candidates.append((dist, ex, ey, enemy))

        if candidates:
            # 优先最近敌人
            candidates.sort(key=lambda x: x[0])
            target = candidates[0]
            target_enemy = target[3]

            # 检查是否可发射
            fire_rate = self.stats["fire_rate"]
            if fire_rate <= 0:
                fire_rate = 0.01
            if current_time - self.last_fire_time >= fire_rate * 1000:
                self.fire(target, current_time)
                self.last_fire_time = current_time

    def fire(self, target, current_time):
        target_dist, tx, ty, target_enemy = target
        px = self.x + TILE_SIZE // 2
        py = self.y + TILE_SIZE // 2

        if self.tower_type == TOWER_ARROW:
            # 塔箭：单体直接命中
            projectiles.append(ArrowProjectile(px, py, (tx, ty), self.stats["damage"]))
        elif self.tower_type == TOWER_CANNON:
            # 塔炮：落点溅射
            projectiles.append(CannonProjectile(px, py, (tx, ty), self.stats["damage"], self.stats["splash_radius"]))
        elif self.tower_type == TOWER_SLOW:
            # 塔减速：子弹缓慢射击并施加减速
            projectiles.append(SlowProjectile(px, py, (tx, ty), self.stats["damage"], self.stats["slow_duration"]))

    def draw(self, surface):
        cx = self.x + TILE_SIZE // 2
        cy = self.y + TILE_SIZE // 2
        # 塔基座
        pygame.draw.rect(surface, self.stats["color"], (self.x + 4, self.y + 4, TILE_SIZE - 8, TILE_SIZE - 8))
        # 等级文字
        if self.level > 1:
            level_text = font.render("Lv" + str(self.level), True, (255, 255, 255))
            surface.blit(level_text, (self.x + 4, self.y + TILE_SIZE - 16))

    def draw_range(self, surface):
        if self.level < 2:
            range_val = self.stats["range"]
        else:
            # 最大等级时使用增强后的值（近似）
            stats_base = TOWER_STATS[self.tower_type]
            range_val = int(self.stats["range"] * 1.1)
        pygame.draw.circle(surface, (*self.stats["color"], 60), (self.x + TILE_SIZE // 2, self.y + TILE_SIZE // 2), range_val, 2)


class Projectile:
    def __init__(self, x, y, target, damage):
        self.x, self.y = x, y
        self.target_x, self.target_y = target
        self.damage = damage
        self.speed = 8
        self.active = True
        self.radius = 3
        self.color = (255, 255, 0)

    def update(self, enemies):
        if not self.active:
            return
        dx, dy = self.target_x - self.x, self.target_y - self.y
        distance = (dx * dx + dy * dy) ** 0.5
        if distance <= self.speed:
            self.active = False
            self.on_hit(enemies)
        else:
            step = self.speed / distance
            self.x += dx * step
            self.y += dy * step

    def on_hit(self, enemies):
        pass

    def draw(self, surface):
        if not self.active:
            return
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)


class ArrowProjectile(Projectile):
    def __init__(self, x, y, target, damage):
        super().__init__(x, y, target, damage)

    def on_hit(self, enemies):
        closest = None
        min_dist = float('inf')
        for e in enemies:
            if e.dead or e.reached_base:
                continue
            ex = e.pixel_pos[0] + TILE_SIZE // 2
            ey = e.pixel_pos[1] + TILE_SIZE // 2
            dist = ((ex - self.x) ** 2 + (ey - self.y) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest = e
        if closest and min_dist < TILE_SIZE:
            closest.take_damage(self.damage)


class CannonProjectile(Projectile):
    def __init__(self, x, y, target, damage, splash_radius):
        super().__init__(x, y, target, damage)
        self.splash_radius = splash_radius
        self.color = (200, 50, 50)

    def on_hit(self, enemies):
        hit_x, hit_y = self.x, self.y
        splash_rad = self.splash_radius
        for e in enemies:
            if e.dead or e.reached_base:
                continue
            ex = e.pixel_pos[0] + TILE_SIZE // 2
            ey = e.pixel_pos[1] + TILE_SIZE // 2
            if (ex - hit_x) ** 2 + (ey - hit_y) ** 2 <= splash_rad ** 2:
                e.take_damage(self.damage)


class SlowProjectile(Projectile):
    def __init__(self, x, y, target, damage, slow_duration):
        super().__init__(x, y, target, damage)
        self.slow_duration = slow_duration
        self.color = (50, 200, 200)

    def on_hit(self, enemies):
        # 所有相邻敌人减速
        hit_x, hit_y = self.x, self.y
        hit_rad = 15
        for e in enemies:
            if e.dead or e.reached_base:
                continue
            ex = e.pixel_pos[0] + TILE_SIZE // 2
            ey = e.pixel_pos[1] + TILE_SIZE // 2
            if (ex - hit_x) ** 2 + (ey - hit_y) ** 2 <= hit_rad ** 2:
                e.take_damage(self.damage)
                e.apply_slow(self.slow_duration)


def draw_map():
    # 绘制背景
    screen.fill(BG_COLOR)

    # 绘制路径
    if PATH_POINTS_PIXEL:
        points = PATH_POINTS_PIXEL
        if len(points) >= 2:
            for i in range(len(points) - 1):
                pygame.draw.line(screen, PATH_COLOR, points[i], points[i + 1], TILE_SIZE)

    # 绘制入口和基地
    entry_px = (entry_tile[0] * TILE_SIZE, entry_tile[1] * TILE_SIZE)
    pygame.draw.rect(screen, ENTRY_COLOR, (*entry_px, TILE_SIZE, TILE_SIZE))

    base_px = (base_tile[0] * TILE_SIZE, base_tile[1] * TILE_SIZE)
    pygame.draw.rect(screen, BASE_COLOR, (*base_px, TILE_SIZE, TILE_SIZE))

    # 绘制其他格子（草地）
    for x in range(MAP_COLS):
        for y in range(MAP_ROWS):
            if (x, y) not in path_tiles:
                px = x * TILE_SIZE
                py = y * TILE_SIZE
                pygame.draw.rect(screen, GRASS_COLOR, (px, py, TILE_SIZE, TILE_SIZE), 1)

    # 绘制网格辅助线（可选）
    for x in range(0, MAP_WIDTH, TILE_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, MAP_HEIGHT))
    for y in range(0, MAP_HEIGHT, TILE_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (MAP_WIDTH, y))


def draw_hud():
    hud_x = MAP_WIDTH + 8
    hud_y = 20

    # 基础统计
    lives_text = font.render(f"Lives: {lives}", True, TEXT_COLOR)
    money_text = font.render(f"Gold: {money}", True, TEXT_COLOR)
    wave_text = font.render(f"Wave: {current_wave + 1}/5", True, TEXT_COLOR)
    enemies_text = font.render(f"Remaining Enemies: {sum(1 for e in enemies if not e.dead and not e.reached_base)}", True, TEXT_COLOR)
    screen.blit(lives_text, (hud_x, hud_y))
    screen.blit(money_text, (hud_x, hud_y + 30))
    screen.blit(wave_text, (hud_x, hud_y + 60))
    screen.blit(enemies_text, (hud_x, hud_y + 90))

    # 选择塔面板
    if game_state == "playing":
        select_text = font.render("Select Tower:", True, TEXT_COLOR)
        screen.blit(select_text, (hud_x, hud_y + 140))

        tower_types = [TOWER_ARROW, TOWER_CANNON, TOWER_SLOW]
        colors = {"Arrow": ARROW_TOWER_COLOR, "Cannon": CANNON_TOWER_COLOR, "Slow": SLOW_TOWER_COLOR}
        height_offset = 170
        for i, ttype in enumerate(tower_types):
            color = colors[ttype]
            y = hud_y + height_offset + i * 30
            # 窗口边框
            pygame.draw.rect(screen, color, (hud_x - 5, y - 5, 150, 25), 1 if selected_tower_type == ttype else 0)
            # 颜色块
            pygame.draw.rect(screen, color, (hud_x + 5, y, 20, 20))
            # 名称和价格
            name = font.render(f"{ttype} ({TOWER_STATS[ttype]['cost']}g)", True, TEXT_COLOR)
            screen.blit(name, (hud_x + 30, y + 5))

        # 键位提示
        keys_text = font.render("1-3: Select Towers", True, TEXT_COLOR)
        screen.blit(keys_text, (hud_x, hud_y + height_offset + 100))

        upgrade_text = font.render("R: Restart | ESC: Exit", True, TEXT_COLOR)
        screen.blit(upgrade_text, (hud_x, HEIGHT - 40))

    if game_state in ("win", "lose"):
        screen.fill((0, 0, 0, 180))
        if game_state == "win":
            end_text = font.render("YOU WIN!", True, (100, 255, 100))
        else:
            end_text = font.render("GAME OVER", True, (255, 100, 100))
        screen.blit(end_text, (WIDTH // 2 - 70, HEIGHT // 2 - 30))
        wave_end_text = font.render(f"Wave Reached: {current_wave + 1}", True, TEXT_COLOR)
        screen.blit(wave_end_text, (WIDTH // 2 - 100, HEIGHT // 2))
        restart_text = font.render("Press 'R' to Restart", True, YELLOW)
        screen.blit(restart_text, (WIDTH // 2 - 110, HEIGHT // 2 + 30))


def show_tower_selection():
    # 在底部显示塔类型提示
    pass


def spawn_wave():
    global wave_remaining, wave_next_time, wave_spawned
    if current_wave >= 5:
        return

    wave_def = WAVE_ENEMIES[current_wave]
    # 合并敌人类别
    enemies_list = []
    for enemy_type, count in wave_def:
        enemies_list.extend([enemy_type] * count)

    wave_remaining = len(enemies_list)
    wave_spawned = 0

    # 计算下波时间
    wave_next_time = pygame.time.get_ticks() / 1000 + WAVE_INTERVAL


def start_next_wave():
    global wave_remaining, wave_next_time, wave_spawned, current_wave
    if current_wave >= 5:
        return
    current_wave += 1
    spawn_wave()


def handle_input():
    global money, game_state, selected_tower_type
    keys = pygame.key.get_pressed()
    if keys[pygame.K_r]:
        reset_game()
    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()

    if keys[pygame.K_1]:
        selected_tower_type = TOWER_ARROW
    elif keys[pygame.K_2]:
        selected_tower_type = TOWER_CANNON
    elif keys[pygame.K_3]:
        selected_tower_type = TOWER_SLOW


def reset_game():
    global game_state, money, lives, current_wave, wave_remaining, wave_next_time, wave_spawned, enemies, towers, projectiles
    game_state = "playing"
    money = 180
    lives = 20
    current_wave = 0
    wave_remaining = 0
    wave_spawned = 0
    wave_next_time = pygame.time.get_ticks() / 1000 + WAVE_INTERVAL
    enemies = []
    towers = []
    projectiles = []
    spawn_wave()


def main():
    global money, lives, current_wave, wave_remaining, wave_spawned, wave_next_time, game_state
    global enemies, towers, projectiles, selected_towers

    reset_game()

    running = True
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state != "playing":
                    continue

                mx, my = pygame.mouse.get_pos()
                # 只处理地图内
                if mx < MAP_WIDTH and my < MAP_HEIGHT:
                    col = mx // TILE_SIZE
                    row = my // TILE_SIZE

                    if event.button == 1:  # 左键：建造塔或选中塔
                        if (col, row) in path_tiles or (col, row) == entry_tile or (col, row) == base_tile:
                            continue  # 路径、入口、基地不能建造
                        if any(t.x // TILE_SIZE == col and t.y // TILE_SIZE == row for t in towers):
                            # 已有塔：选中并显示升级UI（这里暂不实现升级拖拽，直接升级）
                            tower = next(t for t in towers if t.x // TILE_SIZE == col and t.y // TILE_SIZE == row)
                            if tower in selected_towers:
                                # 取消选中
                                selected_towers.discard(tower)
                            else:
                                selected_towers.add(tower)
                        else:
                            # 建造新塔
                            if money >= TOWER_STATS[selected_tower_type]["cost"]:
                                money -= TOWER_STATS[selected_tower_type]["cost"]
                                new_tower = Tower(col * TILE_SIZE, row * TILE_SIZE, selected_tower_type)
                                towers.append(new_tower)

                    elif event.button == 3:  # 右键：升级选中的塔
                        for tower in list(selected_towers):
                            if tower.level < tower.max_level:
                                upgrade_cost = tower.can_afford_upgrade()
                                if money >= upgrade_cost:
                                    money -= upgrade_cost
                                    tower.upgrade()
                                    selected_towers.discard(tower)

        handle_input()

        # 游戏逻辑
        if game_state == "playing":
            current_time = pygame.time.get_ticks() / 1000
            # 波次生成控制
            if wave_remaining > 0:
                if current_time >= wave_next_time:
                    # 生成敌人
                    if wave_remaining > 0:
                        # 取当前波配置，尝试生成
                        enemies_def = WAVE_ENEMIES[current_wave]
                        # 简化：轮流生成类型
                        enemy_types = []
                        for t, n in enemies_def:
                            enemy_types.extend([t] * n)
                        if wave_spawned < len(enemy_types):
                            etype = enemy_types[wave_spawned]
                            enemies.append(Enemy(etype))
                            wave_spawned += 1
                            # 递减
                            wave_remaining -= 1
                            # 间隔生成时间
                            wave_next_time = current_time + max(0.1, 1.0 / (wave_remaining + 1))

            # 更新敌人
            for enemy in enemies[:]:
                enemy.update()
                if enemy.dead:
                    money += enemy.reward
                    enemies.remove(enemy)
                elif enemy.reached_base:
                    lives -= 1
                    enemies.remove(enemy)

            # 检查游戏结束
            if lives <= 0:
                game_state = "lose"

            if game_state == "playing" and current_wave == 4 and wave_remaining == 0 and len([e for e in enemies if not e.dead]) == 0:
                game_state = "win"

            # 所有塔更新 + 投射物更新
            for tower in towers:
                tower.update(enemies, pygame.time.get_ticks())

            for proj in projectiles[:]:
                proj.update(enemies)
                if not proj.active:
                    projectiles.remove(proj)

            # 清除尸体和已移除的敌人
            enemies = [e for e in enemies if not e.dead and not e.reached_base]

        # 绘制
        draw_map()

        # 画塔
        for tower in towers:
            tower.draw(screen)

        # 绘制投射物
        for proj in projectiles:
            proj.draw(screen)

        # 选中的塔（用于升级/显示）
        for tower in selected_towers:
            # 高亮显示
            rect = pygame.Rect(tower.x, tower.y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (255, 255, 0), rect, 2)

        # 绘制敌人
        for enemy in enemies:
            enemy.draw(screen)

        # HUD
        draw_hud()

        # 鼠标悬停时显示可建造位置
        mx, my = pygame.mouse.get_pos()
        if game_state == "playing" and mx < MAP_WIDTH:
            col = mx // TILE_SIZE
            row = my // TILE_SIZE
            hover_tile = (col, row)

            # 预览建造塔
            if hover_tile not in path_tiles and hover_tile != entry_tile and hover_tile != base_tile:
                can_build = True
                if any(t.x // TILE_SIZE == col and t.y // TILE_SIZE == row for t in towers):
                    can_build = False

                # 如果可以建，画半透明方块
                if can_build and money >= TOWER_STATS[selected_tower_type]["cost"]:
                    alpha = 60
                    color = (*TOWER_STATS[selected_tower_type]["color"], alpha)
                    s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    s.fill(color)
                    screen.blit(s, (col * TILE_SIZE, row * TILE_SIZE))

                # 选中塔的升级预览
                for t in selected_towers:
                    if t.x // TILE_SIZE == col and t.y // TILE_SIZE == row:
                        rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        pygame.draw.rect(screen, (255, 255, 0), rect, 2)

        # 游戏结束处理
        if game_state == "lose":
            draw_hud()  # 确保文字清晰

        # 刷新显示
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()