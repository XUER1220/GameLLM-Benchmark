import pygame
import random
import sys
import math
from enum import Enum

# 固定参数
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_COLS = 20
GRID_ROWS = 15
GRID_SIZE = 32
MAP_WIDTH = GRID_COLS * GRID_SIZE
MAP_HEIGHT = GRID_ROWS * GRID_SIZE
HUD_WIDTH = WINDOW_WIDTH - MAP_WIDTH
FPS = 60
PATH_POINTS = [(0, 1), (3, 1), (3, 6), (10, 6), (10, 2), (15, 2), (15, 10), (7, 10), (7, 14), (MAP_WIDTH // GRID_SIZE - 1, 14)]

random.seed(42)
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tower Defense Hard")
clock = pygame.time.Clock()

# 常量定义
INITIAL_GOLD = 180
INITIAL_LIFE = 20
MAX_LEVEL = 2
PREPARE_TIME = 3  # seconds

# 塔类型定义
TOWER_TYPES = {
    "arrow": {
        "name": "Arrow Tower",
        "cost": 50,
        "range": 120,
        "damage": 8,
        "fire_rate": 0.8,  # seconds
        "color": (0, 200, 100),
        "bullet_color": (255, 255, 0),
        "bullet_size": 3,
        "bullet_speed": 8,
        "projectile_type": "arrow",
        "upgrade_mult": 0.7
    },
    "cannon": {
        "name": "Cannon Tower",
        "cost": 80,
        "range": 105,
        "damage": 14,
        "fire_rate": 1.2,
        "splash_radius": 45,
        "color": (100, 100, 100),
        "bullet_color": (50, 50, 50),
        "bullet_size": 6,
        "bullet_speed": 6,
        "projectile_type": "splash",
        "upgrade_mult": 0.7
    },
    "slow": {
        "name": "Slow Tower",
        "cost": 70,
        "range": 110,
        "damage": 4,
        "fire_rate": 1.0,
        "slow_duration": 2.0,
        "color": (150, 100, 255),
        "bullet_color": (0, 255, 255),
        "bullet_size": 4,
        "bullet_speed": 7,
        "projectile_type": "slow",
        "upgrade_mult": 0.7
    }
}

# 敌人类型定义
ENEMY_TYPES = {
    "normal": {
        "speed": 1.0,
        "max_health": 50,
        "reward": 15,
        "color": (200, 50, 50),
        "radius": 10
    },
    "fast": {
        "speed": 2.0,
        "max_health": 30,
        "reward": 10,
        "color": (255, 180, 50),
        "radius": 8
    },
    "tank": {
        "speed": 0.6,
        "max_health": 120,
        "reward": 30,
        "color": (60, 60, 200),
        "radius": 12
    }
}

# 五波敌人配置
WAVE_CONFIG = [
    {"enemies": [("normal", 6)]},
    {"enemies": [("fast", 8), ("normal", 3)]},
    {"enemies": [("tank", 3), ("normal", 5), ("fast", 5)]},
    {"enemies": [("tank", 5), ("normal", 10), ("fast", 6)]},
    {"enemies": [("tank", 10), ("normal", 15), ("fast", 12)]}
]

class GameStates(Enum):
    PLAYING = 0
    PREPARE = 1
    GAME_OVER = 2
    VICTORY = 3

# 全局变量
def reset_game():
    global gold, life, current_wave, enemies, towers, projectiles, wave_active, wave_ready_time, enemy_spawn_queue, enemies_spawned, enemy_next_spawn_time, selected_tower_type, selected_tower, game_state
    gold = INITIAL_GOLD
    life = INITIAL_LIFE
    current_wave = 0
    enemies = []
    towers = []
    projectiles = []
    wave_active = False
    wave_ready_time = 0
    enemy_spawn_queue = []
    enemies_spawned = 0
    enemy_next_spawn_time = 0
    selected_tower_type = "arrow"
    selected_tower = None
    game_state = GameStates.PLAYING

reset_game()

# 精确计算路径点（像素坐标）
path_pixels = [(int(x * GRID_SIZE + GRID_SIZE/2), int(y * GRID_SIZE + GRID_SIZE/2)) for x, y in PATH_POINTS]
# 构建路径网格标记（True 表示路径或基地）
path_grid = [[False] * GRID_COLS for _ in range(GRID_ROWS)]
entry_point = (0, 1)
base_pos = (MAP_WIDTH // GRID_SIZE - 1, 14)

# 标记路径线段
for i in range(len(PATH_POINTS) - 1):
    x1, y1 = PATH_POINTS[i]
    x2, y2 = PATH_POINTS[i + 1]
    # 水平
    if y1 == y2:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < GRID_COLS and 0 <= y1 < GRID_ROWS:
                path_grid[y1][x] = True
    # 垂直
    elif x1 == x2:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= x1 < GRID_COLS and 0 <= y < GRID_ROWS:
                path_grid[y][x1] = True

# 标记基地
if 0 <= base_pos[0] < GRID_COLS and 0 <= base_pos[1] < GRID_ROWS:
    path_grid[base_pos[1]][base_pos[0]] = True

# 粗略路径中心线生成（用于敌人移动）
def get_next_path_point(pos):
    px, py = pos
    closest_point_index = 0
    min_dist = float('inf')
    for i, (px2, py2) in enumerate(path_pixels):
        dist = math.hypot(px2 - px, py2 - py)
        if dist < min_dist:
            min_dist = dist
            closest_point_index = i
    if closest_point_index < len(path_pixels) - 1:
        return path_pixels[closest_point_index + 1]
    else:
        return path_pixels[closest_point_index]  # 到达终点

class Enemy:
    def __init__(self, type_key):
        self.type_key = type_key
        self.speed = ENEMY_TYPES[type_key]["speed"] * 0.5  # 基础值调整
        self.max_health = ENEMY_TYPES[type_key]["max_health"]
        self.health = self.max_health
        self.reward = ENEMY_TYPES[type_key]["reward"]
        self.color = ENEMY_TYPES[type_key]["color"]
        self.radius = ENEMY_TYPES[type_key]["radius"]
        self.path_index = 0
        self.x, self.y = path_pixels[0]
        self.slow_timer = 0
        self.slow_multiplier = 1.0

    def update(self, dt):
        # 处理减速效果
        if self.slow_timer > 0:
            self.slow_timer -= dt
            self.slow_multiplier = 0.5
        else:
            self.slow_multiplier = 1.0
        
        # 移动
        if self.path_index < len(path_pixels) - 1:
            target = path_pixels[self.path_index + 1]
            dx = target[0] - self.x
            dy = target[1] - self.y
            dist = math.hypot(dx, dy)
            
            if dist <= 0:
                self.path_index += 1
                if self.path_index < len(path_pixels) - 1:
                    target = path_pixels[self.path_index + 1]
                    dx = target[0] - self.x
                    dy = target[1] - self.y
                    dist = math.hypot(dx, dy)
            
            move_dist = self.speed * self.slow_multiplier * dt * 60  # 60是fps参考值
            if move_dist >= dist:
                self.x, self.y = target
                self.path_index += 1
            else:
                self.x += (dx / dist) * move_dist
                self.y += (dy / dist) * move_dist
        else:
            global life
            life -= 1
            return True  # 达到基地
        return False  # 继续移动

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            global gold
            gold += self.reward

class Tower:
    def __init__(self, x, y, tower_type):
        self.x = x
        self.y = y
        self.tower_type = tower_type
        self.level = 1
        self.cooldown = 0
        # 特性复制
        self.range = TOWER_TYPES[tower_type]["range"]
        self.damage = TOWER_TYPES[tower_type]["damage"]
        self.fire_rate = TOWER_TYPES[tower_type]["fire_rate"]
        if self.tower_type == "cannon":
            self.splash_radius = TOWER_TYPES["cannon"]["splash_radius"]
        elif self.tower_type == "slow":
            self.slow_duration = TOWER_TYPES["slow"]["slow_duration"]
        self.color = TOWER_TYPES[tower_type]["color"]
        self.bullet_color = TOWER_TYPES[tower_type]["bullet_color"]
        self.projectile_type = TOWER_TYPES[tower_type]["projectile_type"]
        self.bullet_size = TOWER_TYPES[tower_type]["bullet_size"]
        self.bullet_speed = TOWER_TYPES[tower_type]["bullet_speed"]
        self.width = GRID_SIZE
        self.height = GRID_SIZE

    def upgrade(self):
        if self.level < MAX_LEVEL:
            self.level += 1
            self.damage *= 1.3
            self.range *= 1.15
            self.fire_rate *= 0.9
            if self.tower_type == "cannon":
                self.splash_radius *= 1.2
            elif self.tower_type == "slow":
                self.slow_duration *= 1.2

    def update(self, dt):
        if self.cooldown > 0:
            self.cooldown -= dt
        
        # 查找最近敌人
        target = self.find_target()
        if target:
            self.shoot(target)

    def find_target(self):
        min_dist = float('inf')
        target = None
        for enemy in enemies:
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist <= self.range and dist < min_dist:
                min_dist = dist
                target = enemy
        return target

    def shoot(self, target):
        if self.cooldown <= 0:
            projectiles.append(Projectile(self.x, self.y, target, self.tower_type, self.damage, 
                                         self.bullet_speed, self.projectile_type, self.splash_radius if hasattr(self, 'splash_radius') else 0, 
                                         self.slow_duration if hasattr(self, 'slow_duration') else 0))
            self.cooldown = self.fire_rate

class Projectile:
    def __init__(self, x, y, target, tower_type, damage, speed, projectile_type, splash_radius=0, slow_duration=0):
        self.x = x
        self.y = y
        self.target = target
        self.tower_type = tower_type
        self.damage = damage
        self.speed = speed
        self.projectile_type = projectile_type
        self.splash_radius = splash_radius
        self.slow_duration = slow_duration
        self.active = True
        self.color = TOWER_TYPES[tower_type]["bullet_color"]
        self.size = TOWER_TYPES[tower_type]["bullet_size"]

    def update(self, dt):
        if not self.active:
            return
        
        # 简单追踪目标当前位置
        if not self.target or self.target.health <= 0:
            self.active = False
            return
        
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        
        if dist < self.speed * dt * 60:  # 到达目标
            # 着陆效果
            if self.projectile_type == "arrow":
                self.target.take_damage(self.damage)
                self.active = False
            elif self.projectile_type == "splash":
                # 溅射伤害
                for enemy in enemies:
                    if not enemy.active:
                        continue
                    dist_to_splash = math.hypot(enemy.x - self.x, enemy.y - self.y)
                    if dist_to_splash <= self.splash_radius:
                        enemy.take_damage(self.damage)
                self.active = False
            elif self.projectile_type == "slow":
                self.target.take_damage(self.damage)
                self.target.slow_timer = self.slow_duration
                self.active = False
        else:
            # 移动
            move_dist = self.speed * dt * 60
            self.x += (dx / dist) * move_dist
            self.y += (dy / dist) * move_dist

def get_grid_coords(x, y):
    return x // GRID_SIZE, y // GRID_SIZE

def is_grid_valid(gx, gy):
    return (0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS)

def is_grid_path(gx, gy):
    return path_grid[gy][gx] if is_grid_valid(gx, gy) else False

def get_tower_at_grid(gx, gy):
    for tower in towers:
        if abs(tower.x - (gx * GRID_SIZE + GRID_SIZE/2)) < 1 and abs(tower.y - (gy * GRID_SIZE + GRID_SIZE/2)) < 1:
            return tower
    return None

def draw_path():
    # 绘制路径
    pygame.draw.lines(screen, (100, 100, 100), False, path_pixels, 20)
    # 入口和基地标记
    start_pos = path_pixels[0]
    end_pos = path_pixels[-1]
    pygame.draw.circle(screen, (50, 200, 50), start_pos, 10)
    pygame.draw.circle(screen, (200, 50, 50), end_pos, 14)
    
    # 绘制网格线（淡色）
    for x in range(0, MAP_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, MAP_HEIGHT))
    for y in range(0, MAP_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (MAP_WIDTH, y))

def draw_tower(tower):
    # 主体
    pygame.draw.rect(screen, tower.color, (
        tower.x - GRID_SIZE/2, tower.y - GRID_SIZE/2,
        GRID_SIZE, GRID_SIZE
    ))
    # 等级
    font = pygame.font.Font(None, 24)
    text = font.render(f"Lv.{tower.level}", True, (255, 255, 255))
    screen.blit(text, (tower.x - 10, tower.y - 5))

def draw_enemies():
    for enemy in enemies:
        if enemy.health <= 0:
            continue
        # 缓慢效果圆环
        if enemy.slow_timer > 0:
            pygame.draw.circle(screen, (0, 255, 255), (int(enemy.x), int(enemy.y)), enemy.radius + 2, 1)
        pygame.draw.circle(screen, enemy.color, (int(enemy.x), int(enemy.y)), enemy.radius)

def draw_projectiles():
    for projectile in projectiles:
        if not projectile.active:
            continue
        pygame.draw.circle(screen, projectile.color, (int(projectile.x), int(projectile.y)), projectile.size)

def draw_ui():
    # HUD面板
    panel_x = MAP_WIDTH
    panel_y = 0
    
    # 背景
    pygame.draw.rect(screen, (80, 80, 80), (panel_x, panel_y, HUD_WIDTH, WINDOW_HEIGHT))
    
    # 顶部信息
    font = pygame.font.Font(None, 32)
    life_text = font.render(f"Base HP: {life}", True, (255, 0, 0))
    gold_text = font.render(f"Gold: {gold}", True, (255, 215, 0))
    wave_text = font.render(f"Wave: {current_wave + 1}/{5}", True, (255, 255, 255))
    
    screen.blit(life_text, (panel_x + 10, 20))
    screen.blit(gold_text, (panel_x + 10, 55))
    screen.blit(wave_text, (panel_x + 10, 90))

    # 波次剩余
    if wave_active:
        remaining_text = font.render(f"Remaining: {len(enemies)}", True, (200, 200, 200))
    else:
        if game_state == GameStates.PLAYING or game_state == GameStates.PREPARE:
            remaining_text = font.render("Next Wave...", True, (200, 200, 200))
        else:
            remaining_text = font.render("", True, (200, 200, 200))
    screen.blit(remaining_text, (panel_x + 10, 125))

    # 建造选择区域
    build_y = 180
    pygame.draw.rect(screen, (50, 50, 50), (panel_x + 10, build_y, 140, 220))
    pygame.draw.rect(screen, (0, 0, 0), (panel_x + 10, build_y, 140, 220), 2)
    tower_text = font.render("Select Tower:", True, (255, 255, 255))
    screen.blit(tower_text, (panel_x + 15, build_y + 10))

    # 每个塔按钮
    y_offset = build_y + 50
    for idx, tower_key in enumerate(["arrow", "cannon", "slow"]):
        # 高亮选中
        color = (255, 255, 255) if selected_tower_type == tower_key else (100, 100, 100)
        border_color = (255, 255, 0) if selected_tower_type == tower_key else (50, 50, 50)
        
        # 绘制小方块代表
        pygame.draw.rect(screen, color, (panel_x + 20, y_offset + idx * 50, 40, 40))
        pygame.draw.rect(screen, border_color, (panel_x + 20, y_offset + idx * 50, 40, 40), 2)
        
        # 显示信息
        tower_info = TOWER_TYPES[tower_key]
        name_text = font.render(f"{tower_info['name']}", True, (255, 255, 255))
        cost_text = font.render(f"Cost: {tower_info['cost']}", True, (255, 255, 0))
        
        screen.blit(name_text, (panel_x + 70, y_offset + idx * 50))
        screen.blit(cost_text, (panel_x + 70, y_offset + idx * 50 + 20))

    # 升级信息
    upgrade_y = y_offset + 210
    pygame.draw.rect(screen, (50, 50, 50), (panel_x + 10, upgrade_y, 140, 40))
    if selected_tower:
        upgrade_cost = int(selected_tower_type_info(selected_tower.tower_type)["cost"] * selected_tower_type_info(selected_tower.tower_type)["upgrade_mult"] * (1.3 ** (selected_tower.level - 1)))
        upgrade_text = font.render(f"Upgrade (${upgrade_cost})", True, (255, 255, 0))
        screen.blit(upgrade_text, (panel_x + 15, upgrade_y + 5))
    else:
        upgrade_text = font.render("Select a tower", True, (150, 150, 150))
        screen.blit(upgrade_text, (panel_x + 20, upgrade_y + 10))

    # 绘制当前选中塔的射程
    if selected_tower:
        pygame.draw.circle(screen, (50, 255, 50), (int(selected_tower.x), int(selected_tower.y)), int(selected_tower.range), 1)

def selected_tower_type_info(tower_key):
    return TOWER_TYPES[tower_key]

def check_build(x, y):
    gx, gy = get_grid_coords(x, y)
    if not is_grid_valid(gx, gy):
        return False, "Out of bounds"
    if is_grid_path(gx, gy):
        return False, "On path"
    if get_tower_at_grid(gx, gy):
        return False, "Occupied"
    return True, ""

def upgrade_tower_if_possible():
    global gold, selected_tower
    if not selected_tower:
        return
    
    # 计算升级费用
    base_cost = TOWER_TYPES[selected_tower.tower_type]["cost"]
    upgrade_cost = int(base_cost * TOWER_TYPES[selected_tower.tower_type]["upgrade_mult"] * (1.3 ** (selected_tower.level - 1)))
    
    if gold >= upgrade_cost and selected_tower.level < MAX_LEVEL:
        gold -= upgrade_cost
        selected_tower.upgrade()

def draw_build_preview(mouse_x, mouse_y):
    gx, gy = get_grid_coords(mouse_x, mouse_y)
    if not is_grid_valid(gx, gy):
        return
    
    x, y = gx * GRID_SIZE + GRID_SIZE/2, gy * GRID_SIZE + GRID_SIZE/2
    
    can_build, reason = check_build(x - GRID_SIZE/2, y - GRID_SIZE/2)
    if can_build:
        # 建造区域预览
        tower_info = selected_tower_type_info(selected_tower_type)
        pygame.draw.circle(screen, (0, 255, 0, 60), (int(x), int(y)), int(tower_info["range"]), 1)
        pygame.draw.circle(screen, (0, 255, 0, 180), (int(x), int(y)), 5)
    else:
        pygame.draw.circle(screen, (255, 0, 0, 60), (int(x), int(y)), 5)

def draw_wave_preparation():
    if game_state == GameStates.PREPARE:
        remaining = max(0, wave_ready_time - pygame.time.get_ticks() / 1000)
        font = pygame.font.Font(None, 48)
        text = font.render(f"Wave {current_wave + 1} in {remaining:.1f}s", True, (255, 255, 255))
        screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, WINDOW_HEIGHT//2))

def draw_game_over_screen():
    if game_state == GameStates.GAME_OVER:
        font = pygame.font.Font(None, 72)
        text1 = font.render("Game Over", True, (255, 0, 0))
        screen.blit(text1, (WINDOW_WIDTH//2 - text1.get_width()//2, 200))
        
        font = pygame.font.Font(None, 36)
        text2 = font.render(f"Reached wave {current_wave + 1}", True, (255, 255, 255))
        text3 = font.render("Press R to Restart", True, (200, 200, 200))
        screen.blit(text2, (WINDOW_WIDTH//2 - text2.get_width()//2, 350))
        screen.blit(text3, (WINDOW_WIDTH//2 - text3.get_width()//2, 400))

def draw_victory_screen():
    if game_state == GameStates.VICTORY:
        font = pygame.font.Font(None, 72)
        text1 = font.render("You Win!", True, (0, 255, 0))
        screen.blit(text1, (WINDOW_WIDTH//2 - text1.get_width()//2, 200))
        
        font = pygame.font.Font(None, 36)
        text2 = font.render("All waves cleared", True, (255, 255, 255))
        text3 = font.render("Press R to Restart", True, (200, 200, 200))
        screen.blit(text2, (WINDOW_WIDTH//2 - text2.get_width()//2, 350))
        screen.blit(text3, (WINDOW_WIDTH//2 - text3.get_width()//2, 400))

def update_game_logic(dt):
    global enemies, projectiles, wave_active, enemy_spawn_queue, enemies_spawned, enemy_next_spawn_time, wave_ready_time, game_state, current_wave
    
    # 更新炮弹
    for p in projectiles:
        p.update(dt)
    projectiles = [p for p in projectiles if p.active]
    
    # 更新塔
    for tower in towers:
        tower.update(dt)
    
    # 更新敌人
    dead_enemies = []
    for e in enemies:
        if e.update(dt):
            dead_enemies.append(e)
        if e.health <= 0:
            dead_enemies.append(e)
    
    # 移除死掉的敌人
    for e in dead_enemies:
        if e in enemies:
            enemies.remove(e)
    
    # 波次逻辑
    if game_state == GameStates.PLAYING and not wave_active:
        # 准备时间后开始新一wave
        if current_wave < 5:
            setup_wave(current_wave)
    
    # 游戏结束条件
    if life <= 0:
        game_state = GameStates.GAME_OVER
    
    # 胜利条件
    if current_wave == 5 and len(enemies) == 0 and not wave_active and len(enemy_spawn_queue) == 0:
        if game_state != GameStates.VICTORY:
            game_state = GameStates.VICTORY

def setup_wave(wave_index):
    global wave_active, enemy_next_spawn_time, enemy_spawn_queue, enemies_spawned
    if wave_index < len(WAVE_CONFIG):
        # 设置敌人队列
        wave_config = WAVE_CONFIG[wave_index]
        enemy_spawn_queue = []
        for enemy_type, count in wave_config["enemies"]:
            enemy_spawn_queue.extend([enemy_type] * count)
        # 预设波次开始时间
        wave_active = True
        enemies_spawned = 0
        enemy_next_spawn_time = pygame.time.get_ticks() / 1000.0 + 1.5  # 第一波在1.5秒后开始生成

def spawn_enemies(dt):
    global enemy_next_spawn_time, enemies_spawned
    
    # 生成定时检查
    current_time = pygame.time.get_ticks() / 1000.0
    if current_time >= enemy_next_spawn_time and enemy_spawn_queue:
        enemy_type = enemy_spawn_queue.pop(0)
        enemies.append(Enemy(enemy_type))
        enemies_spawned += 1
        
        # 设置下一个生成时间（简单的指数间隔缩短）
        if enemy_spawn_queue:
            interval = max(0.2, 1.5 - enemies_spawned * 0.05) if len(enemy_spawn_queue) > 5 else 2.0
            enemy_next_spawn_time = current_time + interval
        else:
            enemy_next_spawn_time = float('inf')  # 本波次结束

def draw_selection_tower_range():
    global selected_tower
    if selected_tower:
        pygame.draw.circle(screen, (0, 200, 0), (int(selected_tower.x), int(selected_tower.y)), int(selected_tower.range), 2)

def main():
    global gold, life, current_wave, enemies, towers, projectiles, wave_active, wave_ready_time, enemy_spawn_queue, enemies_spawned, enemy_next_spawn_time, selected_tower_type, selected_tower, game_state
    
    mouse_x, mouse_y = 0, 0
    
    # 主循环
    while True:
        dt = clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # 键盘事件
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    reset_game()
                elif event.key == pygame.K_1:
                    selected_tower_type = "arrow"
                elif event.key == pygame.K_2:
                    selected_tower_type = "cannon"
                elif event.key == pygame.K_3:
                    selected_tower_type = "slow"
            
            # 鼠标点击事件
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键
                    mx, my = event.pos
                    if mx < MAP_WIDTH and my < MAP_HEIGHT:
                        gx, gy = get_grid_coords(mx, my)
                        if is_grid_valid(gx, gy) and not is_grid_path(gx, gy):
                            if not get_tower_at_grid(gx, gy):
                                # 建造检查
                                x, y = gx * GRID_SIZE + GRID_SIZE/2, gy * GRID_SIZE + GRID_SIZE/2
                                can_build, reason = check_build(x - GRID_SIZE/2, y - GRID_SIZE/2)
                                tower_info = selected_tower_type_info(selected_tower_type)
                                if can_build and gold >= tower_info["cost"]:
                                    gold -= tower_info["cost"]
                                    tower = Tower(x, y, selected_tower_type)
                                    towers.append(tower)
                            else:
                                # 点击已有塔
                                selected_tower = get_tower_at_grid(gx, gy)
                elif event.button == 3:  # 右键
                    mx, my = event.pos
                    if mx < MAP_WIDTH and my < MAP_HEIGHT:
                        gx, gy = get_grid_coords(mx, my)
                        if is_grid_valid(gx, gy):
                            selected_tower = get_tower_at_grid(gx, gy)
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos

        # 更新逻辑
        update_game_logic(dt)
        
        # 粒子生成逻辑
        spawn_enemies(dt)
        
        # 波次准备逻辑
        if game_state == GameStates.PREPARE:
            wave_ready_time -= dt
            if wave_ready_time <= 0:
                current_wave += 1
                wave_active = False
                setup_wave(current_wave)
        
        screen.fill((30, 30, 30))
        
        # 绘制地图
        draw_path()
        
        # 绘制实体
        draw_towers(towers)
        draw_enemies()
        draw_projectiles()
        draw_selection_tower_range()
        
        # UI
        draw_ui()
        
        # 构建预览
        if game_state == GameStates.PLAYING or game_state == GameStates.PREPARE:
            draw_build_preview(mouse_x, mouse_y)
        
        # 状态屏幕
        draw_wave_preparation()
        draw_game_over_screen()
        draw_victory_screen()
        
        pygame.display.flip()

def draw_towers(towers):
    for tower in towers:
        draw_tower(tower)

# 补充启动代码
main()