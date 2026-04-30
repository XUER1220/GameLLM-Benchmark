import pygame
import random
import sys
import math

# 固定常量
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
MAP_COLS, MAP_ROWS = 20, 15
CELL_SIZE = 32
MAP_WIDTH, MAP_HEIGHT = MAP_COLS * CELL_SIZE, MAP_ROWS * CELL_SIZE
HUD_WIDTH = WINDOW_WIDTH - MAP_WIDTH
FPS = 60
SEED = 42
random.seed(SEED)

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (192, 192, 192)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# 游戏常量
INITIAL_GOLD = 180
INITIAL_LIFE = 20
ENEMIES_PER_WAVE = [5, 8, 12, 15, 20]
BASE_SPAWN_INTERVAL = 1000  # 毫秒

# 塔类型定义
TOWER_TYPES = {
    'arrow': {'name': 'Arrow Tower', 'cost': 50, 'range': 120, 'damage': 8, 'fire_rate': 0.8, 'color': BLUE, 'type': 'single'},
    'cannon': {'name': 'Cannon Tower', 'cost': 80, 'range': 105, 'damage': 14, 'fire_rate': 1.2, 'color': GRAY, 'type': 'splash', 'splash_radius': 45},
    'slow': {'name': 'Slow Tower', 'cost': 70, 'range': 110, 'damage': 4, 'fire_rate': 1.0, 'color': PINK, 'type': 'slow', 'slow_duration': 2.0}
}

# 升级参数
UPGRADE_COST_RATIO = 0.7
MAX_UPGRADE_LEVEL = 2

# 敌人类别
class EnemyType:
    def __init__(self, name, hp, speed, reward, color, size):
        self.name = name
        self.hp = hp
        self.speed = speed
        self.reward = reward
        self.color = color
        self.size = size

ENEMY_TYPES = {
    'normal': EnemyType('Normal', 40, 1.5, 5, RED, 10),
    'fast': EnemyType('Fast', 20, 2.8, 7, YELLOW, 8),
    'tank': EnemyType('Tank', 100, 0.9, 12, BROWN, 14)
}

# 固定路径（20列x15行，每格32px，左上(0,0)，右下(640,480)）
# 路径点：从(0,7) -> (5,7) -> (5,3) -> (12,3) -> (12,10) -> (17,10) -> (19,10)
PATH_POINTS = [
    (0, 7), (5, 7), (5, 3), (12, 3), (12, 10), (17, 10), (19, 10)
]
PATH_WIDTH = CELL_SIZE // 3

class PathGrid:
    def __init__(self):
        self.path_set = set()
        self.generate_path()
    
    def generate_path(self):
        for i in range(len(PATH_POINTS) - 1):
            x1, y1 = PATH_POINTS[i]
            x2, y2 = PATH_POINTS[i+1]
            # 水平或垂直线段
            dx = 1 if x2 > x1 else -1 if x2 < x1 else 0
            dy = 1 if y2 > y1 else -1 if y2 < y1 else 0
            
            x, y = x1, y1
            while True:
                self.path_set.add((x, y))
                if x == x2 and y == y2:
                    break
                x += dx
                y += dy

path_grid = PathGrid()

# 游戏主类
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tower Defense Hard")
        self.font = pygame.font.SysFont(None, 20)
        self.small_font = pygame.font.SysFont(None, 16)
        
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.gold = INITIAL_GOLD
        self.life = INITIAL_LIFE
        self.wave = 0
        self.game_over = False
        self.victory = False
        self.wave_state = 'waiting'  # waiting, active, building, victory
        self.wave_build_time = 0
        self.last_spawn_time = 0
        self.current wave_index = 0
        
        self.enemies = []
        self.towers = []
        self.projectiles = []
        self.particles = []
        self.slow_effects = []
        
        self.selected_tower = 'arrow'
        self.hover_grid = (-1, -1)
        self.path_grid = path_grid
        
        # 入口和基地位置
        self.entry_pos = (0, 7)
        self.base_pos = (19, 10)
        
        # 波次设置
        self.max_wave = 5
        self.enemies_remaining = 0
        self.enemies_to_spawn = 0
        self.spawn_queue = []
        self.spawn_timer = 0
        
        # 初始化波次数据
        self.reset_wave()

    def reset_wave(self):
        if self.wave == 0:
            self.enemies_remaining = 0
            self.enemies_to_spawn = ENEMIES_PER_WAVE[0]
            self.spawn_queue = [random.choice(['normal', 'fast']) for _ in range(self.enemies_to_spawn)]
        else:
            base_count = ENEMIES_PER_WAVE[self.wave]
            self.enemies_remaining = 0
            self.enemies_to_spawn = base_count
            self.spawn_queue = []
            
            # 现实性分布：normal占60%，fast 25%，tank 15%
            for i in range(base_count):
                rand_val = random.random()
                if rand_val < 0.60:
                    self.spawn_queue.append('normal')
                elif rand_val < 0.85:
                    self.spawn_queue.append('fast')
                else:
                    self.spawn_queue.append('tank')
        
        self.current wave_index = 0
        self.wave_state = 'building'

    def start_next_wave(self):
        self.wave += 1
        if self.wave >= self.max_wave:
            self.victory = True
            self.game_over = True
            return
        
        self.wave_state = 'building'
        self.reset_wave()

    def spawn_enemy(self):
        if self.current wave_index < len(self.spawn_queue):
            enemy_type_key = self.spawn_queue[self.current wave_index]
            enemy_type = ENEMY_TYPES[enemy_type_key]
            
            # 从路径起点生成
            x, y = PATH_POINTS[0]
            px, py = x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2
            
            enemy = Enemy(px, py, enemy_type)
            self.enemies.append(enemy)
            self.enemies_remaining += 1
            self.current wave_index += 1

    def get_tower_placeable(self, grid_x, grid_y):
        if grid_x < 0 or grid_x >= MAP_COLS or grid_y < 0 or grid_y >= MAP_ROWS:
            return False
        if (grid_x, grid_y) in self.path_grid.path_set:
            return False
        if grid_x == self.base_pos[0] and grid_y == self.base_pos[1]:
            return False
        # 入口格子
        if grid_x == self.entry_pos[0] and grid_y == self.entry_pos[1]:
            return False
        
        # 检查是否有塔
        for t in self.towers:
            if grid_x == t.grid_x and grid_y == t.grid_y:
                return False
        return True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r and self.game_over:
                    self.reset()
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    keys = ['arrow', 'cannon', 'slow']
                    idx = int(event.unicode) - 1
                    if 0 <= idx < len(keys):
                        self.selected_tower = keys[idx]
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                if mx < MAP_WIDTH:
                    self.hover_grid = (mx // CELL_SIZE, my // CELL_SIZE)
                else:
                    self.hover_grid = (-1, -1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if mx < MAP_WIDTH:
                    gx, gy = mx // CELL_SIZE, my // CELL_SIZE
                    if event.button == 1:  # 左键：建造
                        self.build_tower(gx, gy)
                    elif event.button == 3:  # 右键：升级
                        self.upgrade_tower(gx, gy)
        return True

    def build_tower(self, gx, gy):
        if not self.get_tower_placeable(gx, gy) or self.game_over or self.wave_state == 'building':
            return
        
        tower_data = TOWER_TYPES[self.selected_tower]
        if self.gold >= tower_data['cost']:
            self.gold -= tower_data['cost']
            self.towers.append(Tower(gx, gy, self.selected_tower, tower_data))

    def upgrade_tower(self, gx, gy):
        for t in self.towers:
            if t.grid_x == gx and t.grid_y == gy:
                if t.level < MAX_UPGRADE_LEVEL:
                    upgrade_cost = int(TOWER_TYPES[t.type]['cost'] * UPGRADE_COST_RATIO)
                    if self.gold >= upgrade_cost:
                        self.gold -= upgrade_cost
                        t.level += 1
                        if t.type == 'arrow':
                            t.damage += 4
                            t.range += 10
                        elif t.type == 'cannon':
                            t.damage += 6
                            t.range += 10
                        elif t.type == 'slow':
                            t.damage += 2
                            t.range += 10

    def update(self):
        if self.game_over:
            return
        
        # 检查波次生成
        if self.wave_state == 'building':
            if self.current wave_index >= len(self.spawn_queue):
                self.wave_state = 'active'
                self.enemies_remaining = len(self.enemies)
            else:
                if pygame.time.get_ticks() - self.spawn_timer >= 500:  # 每0.5秒生成一个
                    self.spawn_enemy()
                    self.spawn_timer = pygame.time.get_ticks()
        
        # 波次胜利检查
        if self.wave_state == 'active' and self.enemies_remaining <= 0:
            if self.wave < self.max_wave - 1:
                # 3秒后下一波
                if not hasattr(self, 'wave_end_time'):
                    self.wave_end_time = pygame.time.get_ticks()
                elif pygame.time.get_ticks() - self.wave_end_time >= 3000:
                    del self.wave_end_time
                    self.start_next_wave()
            else:
                self.victory = True
                self.game_over = True
        
        # 升级塔属性
        current_time = pygame.time.get_ticks() / 1000.0
        for t in self.towers:
            if current_time - t.last_fire_time >= t.fire_rate:
                t.fire(current_time, self.enemies, self.projectiles)
        # 更新敌人位置
        for enemy in self.enemies[:]:
            enemy.update(current_time)
            if enemy.reached_base:
                self.life -= 1
                enemy.reached_base = False
                self.enemies.remove(enemy)
                self.enemies_remaining -= 1
                if self.life <= 0:
                    self.game_over = True
            elif enemy.dead:
                self.gold += enemy.reward
                self.enemies.remove(enemy)
                self.enemies_remaining -= 1
            elif enemy.active:
                enemy.draw(self.screen)
        
        # 更新炮弹
        for p in self.projectiles[:]:
            p.update()
            if not p.active:
                if hasattr(p, 'splash_radius'):
                    self.create_explosion(p.x, p.y, p.splash_radius)
                self.projectiles.remove(p)
            elif p.active:
                p.draw(self.screen)
        
        # 更新效果
        for effect in self.slow_effects[:]:
            if current_time >= effect.expiry_time:
                self.slow_effects.remove(effect)
        
        # 更新粒子
        self.particles = [p for p in self.particles if current_time < p.expiry_time and not p.remove]

    def create_explosion(self, x, y, splash_radius):
        # 简单视觉效果
        for i in range(10):
            angle = random.random() * math.pi * 2
            speed = random.uniform(2, 5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append(Particle(x, y, vx, vy, CYAN, 30))
        
        # 实际伤害
        damage = TOWER_TYPES['cannon']['damage']
        for enemy in self.enemies:
            dist = math.sqrt((enemy.x - x)**2 + (enemy.y - y)**2)
            if dist <= splash_radius:
                if enemy.active:
                    enemy.take_damage(damage, self.slow_effects)
                    # 确定击中效果
                    self.particles.append(Particle(enemy.x, enemy.y, 0, 0, RED, 20))

    def draw(self):
        # 清屏
        self.screen.fill((30, 30, 30))
        
        # 绘制地图
        self.draw_map()
        
        # 绘制塔
        for t in self.towers:
            t.draw(self.screen)
        
        # 绘制敌人
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # 绘制炮弹
        for p in self.projectiles:
            p.draw(self.screen)
        
        # 绘制粒子
        for p in self.particles:
            p.draw(self.screen)
        
        # 绘制HUD
        self.draw_hud()
        
        pygame.display.flip()

    def draw_map(self):
        # 地面
        for x in range(MAP_COLS):
            for y in range(MAP_ROWS):
                color = GREEN if (x+y) % 2 == 0 else LIGHT_GREEN if (x+y) % 2 == 1 else GREEN
                light_green = (150, 200, 150)
                pygame.draw.rect(self.screen, light_green if (x+y)%2==1 else GREEN, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
        # 路径
        for gx, gy in self.path_grid.path_set:
            pygame.draw.rect(self.screen, BROWN, (gx*CELL_SIZE, gy*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
        # 入口
        x, y = self.entry_pos
        pygame.draw.rect(self.screen, DARK_GREEN, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
        # 基地
        x, y = self.base_pos
        pygame.draw.rect(self.screen, RED, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.circle(self.screen, BLACK, (x*CELL_SIZE+16, y*CELL_SIZE+16), 8)
        
        # 悬停高亮
        if self.hover_grid != (-1, -1):
            x, y = self.hover_grid
            if 0 <= x < MAP_COLS and 0 <= y < MAP_ROWS:
                if self.get_tower_placeable(x, y):
                    pygame.draw.rect(self.screen, BLUE, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)
                else:
                    pygame.draw.rect(self.screen, RED, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)

    def draw_hud(self):
        # HUD背景
        hud_rect = pygame.Rect(MAP_WIDTH, 0, HUD_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, (80, 80, 80), hud_rect)
        
        # 绘制塔类型选择器
        y_offset = 20
        for i, tower_type in enumerate(TOWER_TYPES.keys()):
            font_color = DARK_GREEN if self.selected_tower == tower_type else BLACK
            color = TOWER_TYPES[tower_type]['color']
            font = self.small_font
            text = font.render(f"{['1','2','3'][i]} {TOWER_TYPES[tower_type]['name']}", True, font_color)
            self.screen.blit(text, (MAP_WIDTH + 10, y_offset))
            y_offset += 40
            
            # 价格
            cost = font.render(f"Cost: ${TOWER_TYPES[tower_type]['cost']}", True, font_color)
            self.screen.blit(cost, (MAP_WIDTH + 10, y_offset))
            y_offset += 20
        
        # 当前塔信息
        y_offset += 20
        font = self.small_font
        current_tower = TOWER_TYPES.get(self.selected_tower, {})
        if current_tower:
            info = font.render(f"Range: {current_tower['range']}", True, BLACK)
            self.screen.blit(info, (MAP_WIDTH + 10, y_offset))
            y_offset += 20
            info = font.render(f"Damage: {current_tower['damage']}", True, BLACK)
            self.screen.blit(info, (MAP_WIDTH + 10, y_offset))
            y_offset += 20
            info = font.render(f"Fire Rate: {current_tower['fire_rate']}s", True, BLACK)
            self.screen.blit(info, (MAP_WIDTH + 10, y_offset))
        
        # 游戏状态
        y_offset += 40
        gold_text = self.font.render(f"Gold: ${self.gold}", True, YELLOW)
        self.screen.blit(gold_text, (MAP_WIDTH + 10, y_offset))
        y_offset += 25
        
        life_text = self.font.render(f"Life: {self.life}", True, RED)
        self.screen.blit(life_text, (MAP_WIDTH + 10, y_offset))
        y_offset += 25
        
        wave_text = self.font.render(f"Wave: {self.wave+1}/{self.max_wave}", True, WHITE)
        self.screen.blit(wave_text, (MAP_WIDTH + 10, y_offset))
        
        if self.wave_state == 'building':
            enemies_left = len(self.spawn_queue) - self.current wave_index
            wave_info = self.font.render(f"Enemies left to spawn: {enemies_left}", True, WHITE)
            self.screen.blit(wave_info, (MAP_WIDTH + 10, y_offset + 25))
        else:
            wave_info = self.font.render(f"Enemies remaining: {self.enemies_remaining}", True, WHITE)
            self.screen.blit(wave_info, (MAP_WIDTH + 10, y_offset + 25))
        
        # 射程指示（如果当前悬停位置正确）
        if (0 <= self.hover_grid[0] < MAP_COLS and 0 <= self.hover_grid[1] < MAP_ROWS and 
            self.get_tower_placeable(self.hover_grid[0], self.hover_grid[1])):
            x, y = self.hover_grid
            cx = x * CELL_SIZE + CELL_SIZE // 2
            cy = y * CELL_SIZE + CELL_SIZE // 2
            tower_data = TOWER_TYPES[self.selected_tower]
            pygame.draw.circle(self.screen, WHITE, (cx, cy), tower_data['range'], 1)
        
        # 放置塔的射程
        for t in self.towers:
            x = t.grid_x * CELL_SIZE + CELL_SIZE // 2
            y = t.grid_y * CELL_SIZE + CELL_SIZE // 2
            color = BLUE if t.type == 'arrow' else GRAY if t.type == 'cannon' else PINK
            pygame.draw.circle(self.screen, color, (x, y), int(t.range), 1)
            # 展示等级
            level_text = self.small_font.render(f"Lv.{t.level}", True, WHITE)
            self.screen.blit(level_text, (x - 5, y - 5))
        
        # 游戏结束信息
        if self.game_over:
            if self.victory:
                text = self.font.render("You Win!", True, YELLOW)
            else:
                text = self.font.render("Game Over", True, RED)
            
            rect = text.get_rect(center=(MAP_WIDTH + HUD_WIDTH//2, 200))
            self.screen.blit(text, rect)
            
            wave_text = self.font.render(f"Final Wave: {self.wave + 1}", True, WHITE)
            self.screen.blit(wave_text, wave_text.get_rect(center=(MAP_WIDTH + HUD_WIDTH//2, 230)))
            
            restart_text = self.font.render("Press R to Restart", True, WHITE)
            self.screen.blit(restart_text, restart_text.get_rect(center=(MAP_WIDTH + HUD_WIDTH//2, 260)))

# 粒子系统
class Particle:
    def __init__(self, x, y, vx, vy, color, duration):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.start_time = pygame.time.get_ticks() / 1000.0
        self.expiry_time = self.start_time + duration / 1000.0
        self.remove = False
        
    def update(self):
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time > self.expiry_time:
            self.remove = True
        self.x += self.vx
        self.y += self.vy
    
    def draw(self, screen):
        current_time = pygame.time.get_ticks() / 1000.0
        alpha = max(0, 255 * (self.expiry_time - current_time) / (self.expiry_time - self.start_time))
        temp_color = (*self.color[:3], int(alpha)) if len(self.color) < 3 else self.color
        pygame.draw.circle(screen, temp_color[:3] if len(temp_color) >= 3 else temp_color, 
                         (int(self.x), int(self.y)), 3)

# 护盾效果
class SlowEffect:
    def __init__(self, enemy, duration):
        self.enemy = enemy
        self.expiry_time = pygame.time.get_ticks() / 1000.0 + duration

# 塔类
class Tower:
    def __init__(self, grid_x, grid_y, tower_type, data):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.type = tower_type
        self.level = 1
        self.damage = data['damage']
        self.range = data['range']
        self.fire_rate = data['fire_rate']
        self.last_fire_time = 0.0
        self.color = data['color']
        self.tower_type_data = data
        
        # 计算中心位置
        self.x = grid_x * CELL_SIZE + CELL_SIZE // 2
        self.y = grid_y * CELL_SIZE + CELL_SIZE // 2
    
    def fire(self, current_time, enemies, projectiles):
        # 搜索范围内最近的敌人
        target = None
        min_dist = float('inf')
        
        for enemy in enemies:
            dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
            if dist <= self.range and enemy.active:
                if dist < min_dist:
                    min_dist = dist
                    target = enemy
        
        if target:
            self.last_fire_time = current_time
            
            # 创建子弹
            if self.type == 'arrow':
                projectiles.append(Arrow(self.x, self.y, target))
            elif self.type == 'cannon':
                # 有延迟效果
                projectiles.append(Cannonball(self.x, self.y, target, self.damage, self.range // 2))
            elif self.type == 'slow':
                projectiles.append(SlowProjectile(self.x, self.y, target, self.damage))

# 敌人类
class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.hp = enemy_type.hp
        self.base_speed = enemy_type.speed
        self.speed = enemy_type.speed
        self.reward = enemy_type.reward
        self.color = enemy_type.color
        self.radius = enemy_type.size
        
        self.path_index = 0
        self.grid_x, self.grid_y = PATH_POINTS[0]
        self.active = True
        self.dead = False
        self.reached_base = False
        
        self.current_path = self.get_path()
    
    def get_path(self):
        path = []
        for point in PATH_POINTS:
            px, py = point
            # 转换为中心坐标
            path.append((px * CELL_SIZE + CELL_SIZE // 2, py * CELL_SIZE + CELL_SIZE // 2))
        return path
    
    def update(self, current_time):
        if not self.active or self.dead:
            return
        
        # 检查是否被减速
        if hasattr(self, 'slow_timer'):
            self.slow_timer -= 1/60.0  # 简化
            if self.slow_timer <= 0:
                delattr(self, 'slow_timer')
                self.speed = self.base_speed
        
        if self.path_index < len(self.current_path) - 1:
            # 获取下一个目标点
            target_x, target_y = self.current_path[self.path_index + 1]
            
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.sqrt(dx**2 + dy**2)
            
            # 移动
            if dist <= self.speed:
                self.x = target_x
                self.y = target_y
                self.path_index += 1
            else:
                move_x = (dx / dist) * self.speed
                move_y = (dy / dist) * self.speed
                self.x += move_x
                self.y += move_y
            
            # 检查是否到达基地
            if self.path_index == len(self.current_path) - 1:
                dist_to_base = math.sqrt((self.x - self.current_path[-1][0])**2 + (self.y - self.current_path[-1][1])**2)
                if dist_to_base < 5:
                    self.reached_base = True
                    self.active = False
        else:
            self.reached_base = True
            self.active = False
    
    def take_damage(self, damage, slowffects=None):
        if not self.active:
            return
        
        self.hp -= damage
        
        if self.hp <= 0:
            self.dead = True
            self.active = False
        elif hasattr(self, 'slow_timer') and slowffects is not None:
            # 防止重复减速
            pass
        else:
            # 简单减速处理
            self.speed = self.base_speed / 2
            self.slow_timer = 2.0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        if hasattr(self, 'slow_timer'):
            pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), self.radius+2, 2)

# 箭矢类
class Arrow:
    def __init__(self, x, y, target):
        self.x = x
        self.y = y
        self.target = target
        self.speed = 8
        self.active = True
        self.color = BLUE
        self.damage = TOWER_TYPES['arrow']['damage']
    
    def update(self):
        if not self.active:
            return
        
        # 飞向目标
        if self.target and self.target.active:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
        else:
            self.active = False
            return
        
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist <= self.speed:
            self.active = False
            self.target.take_damage(self.damage)
        else:
            move_x = (dx / dist) * self.speed
            move_y = (dy / dist) * self.speed
            self.x += move_x
            self.y += move_y
    
    def draw(self, screen):
        pygame.draw.line(screen, self.color, (self.x, self.y), (self.target.x, self.target.y), 3)

# 炮弹类
class Cannonball:
    def __init__(self, x, y, target, damage, splash_radius):
        self.x = x
        self.y = y
        self.target = target
        self.speed = 6
        self.damage = damage
        self.splash_radius = splash_radius
        self.active = True
        self.color = BLACK
    
    def update(self):
        if not self.active:
            return
        
        # 飞向目标
        if self.target and self.target.active:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
        else:
            self.active = False
            return
        
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist <= self.speed:
            self.active = False
            # 略过实际命中检测，直接进入溅射
        else:
            move_x = (dx / dist) * self.speed
            move_y = (dy / dist) * self.speed
            self.x += move_x
            self.y += move_y
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 4)

# 减速炮弹类
class SlowProjectile:
    def __init__(self, x, y, target, damage):
        self.x = x
        self.y = y
        self.target = target
        self.speed = 5
        self.damage = damage
        self.active = True
        self.color = CYAN
    
    def update(self):
        if not self.active:
            return
        
        # 飞向目标
        if self.target and self.target.active:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
        else:
            self.active = False
            return
        
        dist = math.sqrt(dx**2 + dy**2]
        
        if dist <= self.speed:
            self.active = False
            # 减速敌人
            self.target.take_damage(self.damage)
        else:
            move_x = (dx / dist) * self.speed
            move_y = (dy / dist) * self.speed
            self.x += move_x
            self.y += move_y
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 3)

# 运行游戏
def main():
    game = Game()
    
    while True:
        if not game.handle_events():
            break
        
        game.update()
        
        game.draw()
        
        game.clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()