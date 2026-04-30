import pygame
import random
import sys
import math

# 初始化 pygame
pygame.init()
random.seed(42)

# 常量定义
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 32
MAP_COLS, MAP_ROWS = 20, 15
MAP_WIDTH, MAP_HEIGHT = TILE_SIZE * MAP_COLS, TILE_SIZE * MAP_ROWS
HUD_WIDTH = WIDTH - MAP_WIDTH

FPS = 60

# 颜色
COLORS = {
    'background': (50, 100, 50),
    'path': (200, 180, 130),
    'path_border': (160, 140, 100),
    'base': (150, 0, 0),
    'spawn_point': (0, 150, 0),
    'arrow_tower': (0, 120, 215),
    'cannon_tower': (120, 0, 70),
    'slow_tower': (0, 180, 120),
    'enemy_normal': (255, 165, 0),
    'enemy_fast': (255, 69, 0),
    'enemy_heavy': (139, 0, 0),
    'bubble': (255, 255, 0, 80),
    'text': (255, 255, 255),
    'health_bar': (0, 255, 0),
    'gold': (255, 215, 0),
    'selected_tower': (0, 255, 0),
    'range_circle': (255, 255, 0, 80),
    'enemy_damage': (255, 0, 0),
    'slow_debuff': (0, 255, 255, 100),
}

# 塔定义
TOWER_TYPES = {
    1: {'name': 'Arrow', 'cost': 50, 'range': 120, 'damage': 8, 'fire_rate': 0.8, 'color': COLORS['arrow_tower'], 'bullet_color': (0, 0, 0)},
    2: {'name': 'Cannon', 'cost': 80, 'range': 105, 'damage': 14, 'fire_rate': 1.2, 'splash_radius': 45, 'color': COLORS['cannon_tower']},
    3: {'name': 'Slow', 'cost': 70, 'range': 110, 'damage': 4, 'fire_rate': 1.0, 'slow_duration': 2.0, 'color': COLORS['slow_tower']}
}

# 敌人定义
ENEMY_TYPES = {
    'normal': {'hp': 50, 'speed': 1.5, 'reward': 15, 'color': COLORS['enemy_normal'], 'radius': 10, 'armor': 1},
    'fast': {'hp': 30, 'speed': 3.5, 'reward': 10, 'color': COLORS['enemy_fast'], 'radius': 8, 'armor': 0},
    'heavy': {'hp': 120, 'speed': 0.8, 'reward': 25, 'color': COLORS['enemy_heavy'], 'radius': 12, 'armor': 0}
}

# 路径点（网格坐标）
PATH_POINTS = [(0, 2), (4, 2), (4, 8), (12, 8), (12, 4), (17, 4), (17, 12), (5, 12), (5, 14), (19, 14)]

# 波次定义（敌人列表）
WAVE_ENEMIES = [
    ['normal'] * 8,
    ['normal'] * 5 + ['fast'] * 8,
    ['normal'] * 5 + ['fast'] * 10 + ['heavy'] * 4,
    ['fast'] * 12 + ['heavy'] * 8,
    ['heavy'] * 8 + ['normal'] * 10 + ['fast'] * 10
]
WAVE_INTERVAL = 3.0  # 秒


class Path:
    def __init__(self, points, tile_size=TILE_SIZE):
        self.tile_size = tile_size
        self.points = []
        for x, y in points:
            self.points.append(pygame.Vector2(x * tile_size + tile_size // 2, y * tile_size + tile_size // 2))
        self.rects = []
        self.generate_path_rects()

    def generate_path_rects(self):
        # 将路径转换为网格上的矩形，用于判断位置是否在路径上
        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            start_col, start_row = int(p1.x) // self.tile_size, int(p1.y) // self.tile_size
            end_col, end_row = int(p2.x) // self.tile_size, int(p2.y) // self.tile_size

            # 水平
            if start_row == end_row:
                for col in range(min(start_col, end_col), max(start_col, end_col) + 1):
                    self.rects.append(pygame.Rect(col * self.tile_size, start_row * self.tile_size, self.tile_size, self.tile_size))
            # 垂直
            elif start_col == end_col:
                for row in range(min(start_row, end_row), max(start_row, end_row) + 1):
                    self.rects.append(pygame.Rect(start_col * self.tile_size, row * self.tile_size, self.tile_size, self.tile_size))

    def get_tile_rect(self, grid_x, grid_y):
        return pygame.Rect(grid_x * self.tile_size, grid_y * self.tile_size, self.tile_size, self.tile_size)

    def draw(self, surface):
        # 绘制路径
        for rect in self.rects:
            pygame.draw.rect(surface, COLORS['path'], rect)
            pygame.draw.rect(surface, COLORS['path_border'], rect, 2)


class Enemy:
    def __init__(self, type_key, path: Path, spawn_time):
        self.path = path
        self.index = 0
        self.progress = 0.0
        self.type = type_key
        self.stats = ENEMY_TYPES[type_key].copy()
        self.hp = self.stats['hp']
        self.max_hp = self.hp
        self.speed = self.stats['speed'] / FPS
        self.reward = self.stats['reward']
        self.color = self.stats['color']
        self.radius = self.stats['radius']

        # 减速效果
        self.slow_multipliers = []
        self.base_speed = self.speed
        self.slow_timer = 0

        # 生成时间
        self.spawn_time = spawn_time
        self.active = True

    def update(self, dt):
        # 应用减速
        if self.slow_multipliers:
            max_slow = max(self.slow_multipliers)
            self.speed = self.base_speed * max_slow
        else:
            self.speed = self.base_speed

        # 更新位置
        if len(self.path.points) > 1:
            if self.index < len(self.path.points) - 1:
                current_pos = self.path.points[self.index]
                target_pos = self.path.points[self.index + 1]
                dist = (target_pos - current_pos).length()
                step = self.speed * dt

                if self.progress + step >= dist:
                    # 进入下一段路径
                    self.progress = 0.0
                    self.index += 1
                else:
                    # 移动
                    direction = (target_pos - current_pos).normalize()
                    current_pos += direction * step
                    self.progress += step
                    self.path.points[self.index] = current_pos

    def deal_damage(self, damage):
        self.hp -= damage

    def apply_slow(self, duration):
        self.slow_multipliers.append(0.5)
        self.slow_timer = min(self.slow_timer, duration)

    def clean_slow(self, dt):
        if self.slow_multipliers and dt < 1 / FPS * 2:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slow_multipliers.clear()
                self.speed = self.base_speed
                self.slow_timer = 0

    def reached_end(self):
        return self.index >= len(self.path.points) - 1

    def draw(self, surface):
        pos = self.path.points[self.index]
        # 绘制敌人
        pygame.draw.circle(surface, self.color, (int(pos.x), int(pos.y)), self.radius)
        # 绘制血条
        bar_width = 24
        bar_height = 3
        hp_ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, (0, 0, 0), (int(pos.x - bar_width // 2), int(pos.y - self.radius - 8), bar_width, bar_height))
        pygame.draw.rect(surface, COLORS['health_bar'], (int(pos.x - bar_width // 2), int(pos.y - self.radius - 8), bar_width * hp_ratio, bar_height))


class Projectile:
    def __init__(self, start_pos, target_pos, tower_type, damage, splash_radius=None, slow_duration=0):
        self.pos = pygame.Vector2(start_pos)
        self.target_pos = pygame.Vector2(target_pos)
        self.speed = 5
        self.damage = damage
        self.splash_radius = splash_radius
        self.slow_duration = slow_duration
        self.tower_type = tower_type
        self.active = True

        # 简单跟踪逻辑
        if target_pos:
            self.direction = (target_pos - self.pos).normalize()
        else:
            self.active = False

        self.color = TOWER_TYPES[tower_type].get('bullet_color', (0, 0, 0))

    def update(self, dt):
        if self.active and self.target_pos:
            speed = self.speed * (dt / 1000) * FPS
            self.pos += self.direction * speed
            dist = (self.target_pos - self.pos).length()
            if dist <= speed:
                self.active = False
                return self.target_pos
        return None

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), 4)


class Tower:
    def __init__(self, grid_x, grid_y, tower_type):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.type = tower_type
        self.stats = TOWER_TYPES[tower_type].copy()
        self.level = 1
        self.cost = self.stats['cost']
        self.damage = self.stats['damage']
        self.range = self.stats['range']
        self.fire_rate = self.stats['fire_rate']
        self.last_fired = 0.0
        self.total_fire_rate = self.fire_rate
        self.splash_radius = self.stats.get('splash_radius', 0)
        self.slow_duration = self.stats.get('slow_duration', 0)
        self.color = self.stats.get('color', COLORS['arrow_tower'])
        self.bullet_color = self.stats.get('bullet_color', (0, 0, 0))

    def upgrade(self):
        if self.level < 2:
            cost = int(self.cost * 0.7)
            self.level += 1
            # 每级提升伤害15%，射程+10%
            self.damage = int(self.damage * 1.15)
            self.range = int(self.range * 1.1)
            return cost
        return 0

    def can_fire(self, current_time):
        return current_time - self.last_fired >= self.fire_rate

    def fire(self, enemies, projectiles, current_time):
        if not self.can_fire(current_time):
            return projectiles.append(None) if not projectiles else None

        target = self.find_target(enemies)
        if target:
            self.last_fired = current_time
            center_x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
            center_y = self.grid_y * TILE_SIZE + TILE_SIZE // 2
            projectiles.append(Projectile(
                (center_x, center_y),
                (target.path.points[target.index].x, target.path.points[target.index].y),
                self.type,
                self.damage,
                self.splash_radius if self.type == 2 else None,
                self.slow_duration if self.type == 3 else 0
            ))

    def find_target(self, enemies):
        # 优先攻击路径上最接近基地的敌人
        valid_targets = []
        for enemy in enemies:
            if self.in_range(enemy):
                valid_targets.append(enemy)
        if valid_targets:
            # 选择路径索引最大的敌人（最接近基地）
            return max(valid_targets, key=lambda e: e.index)
        return None

    def in_range(self, enemy):
        enemy_pos = enemy.path.points[enemy.index]
        center_x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
        center_y = self.grid_y * TILE_SIZE + TILE_SIZE // 2
        dist = math.hypot(enemy_pos.x - center_x, enemy_pos.y - center_y)
        return dist <= self.range

    def draw_range(self, surface, selection=False):
        center_x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
        center_y = self.grid_y * TILE_SIZE + TILE_SIZE // 2
        range_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(range_surf, COLORS['range_circle'], (center_x, center_y), int(self.range))
        surface.blit(range_surf, (0, 0))

    def draw(self, surface):
        center_x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
        center_y = self.grid_y * TILE_SIZE + TILE_SIZE // 2

        # 绘制塔身
        pygame.draw.rect(surface, self.color, 
                         (center_x - TILE_SIZE // 3, center_y - TILE_SIZE // 3, TILE_SIZE // 1.5, TILE_SIZE // 1.5))
        
        # 绘制等级
        font = pygame.font.SysFont(None, 16)
        level_surf = font.render(f"Lv.{self.level}", True, (255,255,255))
        surface.blit(level_surf, (center_x - 10, center_y + 5))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tower Defense Hard")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 48)

        self.map = Path(PATH_POINTS)
        self.base_pos = pygame.Vector2(19 * TILE_SIZE + TILE_SIZE // 2, 14 * TILE_SIZE + TILE_SIZE // 2)
        self.spawn_pos = pygame.Vector2(0 * TILE_SIZE + TILE_SIZE // 2, 2 * TILE_SIZE + TILE_SIZE // 2)

        self.enemies = []
        self.projectiles = []
        self.buildings = []
        self.wave_number = 0
        self.wave_enemies = []
        self.wave_spawned = 0
        self.wave_complete = False
        self.wave_timer = 0
        self.wave_cooldown = 0

        self.money = 180
        self.lives = 20
        self.game_over = False
        self.victory = False

        self.selected_tower = 1
        self.hover_grid_x, self.hover_grid_y = -1, -1
        self.mouse_button_down = False

        # 设置波次
        self.wave_number = 1
        self.prepare_wave()

    def prepare_wave(self):
        if self.wave_number <= len(WAVE_ENEMIES):
            self.wave_enemies = WAVE_ENEMIES[self.wave_number - 1].copy()
            self.wave_spawned = 0
            self.wave_complete = False
            self.wave_cooldown = WAVE_INTERVAL
        else:
            self.game_over = True
            self.victory = True

    def spawn_enemy(self):
        if self.wave_enemies and not self.wave_complete:
            enemy_type = self.wave_enemies[0]
            enemy = Enemy(enemy_type, self.map, 0)
            self.enemies.append(enemy)
            self.wave_enemies.pop(0)
            self.wave_spawned += 1

            # 检查本波是否完成生成
            if not self.wave_enemies:
                self.wave_complete = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:
                    # 重新开始游戏
                    self.__init__()
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    self.selected_tower = int(event.key - pygame.K_0)
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                if x < MAP_WIDTH and y < MAP_HEIGHT:
                    self.hover_grid_x = x // TILE_SIZE
                    self.hover_grid_y = y // TILE_SIZE
                else:
                    self.hover_grid_x, self.hover_grid_y = -1, -1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x < MAP_WIDTH and y < MAP_HEIGHT:
                    grid_x, grid_y = x // TILE_SIZE, y // TILE_SIZE
                    if event.button == 1:  # 左键：建造
                        if self.can_build(grid_x, grid_y):
                            self.build_tower(grid_x, grid_y)
                    elif event.button == 3:  # 右键：升级
                        self.try_upgrade(grid_x, grid_y)

        return True

    def can_build(self, grid_x, grid_y):
        if grid_x < 0 or grid_x >= MAP_COLS or grid_y < 0 or grid_y >= MAP_ROWS:
            return False
        # 检查是否在路径上
        if any(rect.collidepoint((grid_x * TILE_SIZE + TILE_SIZE // 2, grid_y * TILE_SIZE + TILE_SIZE // 2)) for rect in self.map.rects):
            return False
        # 检查已有建筑
        for tower in self.buildings:
            if tower.grid_x == grid_x and tower.grid_y == grid_y:
                return False
        # 基地位置不能建
        if grid_x == 19 and grid_y == 14:
            return False
        # 入口附近不能建（简单定义：网格(0,2)附近）
        if grid_x == 0 and grid_y == 2:
            return False
        return True

    def build_tower(self, grid_x, grid_y):
        tower_type = self.selected_tower
        cost = TOWER_TYPES[tower_type]['cost']
        if self.money >= cost:
            self.money -= cost
            self.buildings.append(Tower(grid_x, grid_y, tower_type))

    def try_upgrade(self, grid_x, grid_y):
        for tower in self.buildings:
            if tower.grid_x == grid_x and tower.grid_y == grid_y:
                if tower.level < 2:
                    upgrade_cost = int(tower.cost * 0.7)
                    if self.money >= upgrade_cost:
                        self.money -= upgrade_cost
                        tower.upgrade()
                break

    def update(self):
        if self.game_over:
            return

        dt = self.clock.tick(FPS)
        current_time = pygame.time.get_ticks() / 1000.0

        # 波次管理
        if self.wave_complete:
            if self.wave_cooldown > 0:
                self.wave_cooldown -= dt / 1000
            else:
                self.wave_number += 1
                if self.wave_number > len(WAVE_ENEMIES):
                    self.game_over = True
                    self.victory = True
                else:
                    self.prepare_wave()
        elif len(self.enemies) == 0:
            # 如果没有敌人且波次未完成，准备下一波
            if self.wave_complete and self.wave_cooldown <= 0:
                self.wave_number += 1
                if self.wave_number <= len(WAVE_ENEMIES):
                    self.prepare_wave()

        # 生成敌人
        if not self.wave_complete and self.wave_cooldown <= 0:
            self.spawn_enemy()

        # 更新敌方单位
        for enemy in self.enemies[:]:
            enemy.update(dt)
            # 检查是否到达基地
            if enemy.reached_end():
                self.lives -= 1
                enemy.active = False
                self.enemies.remove(enemy)
            if enemy.hp <= 0:
                self.money += enemy.reward
                enemy.active = False
                self.enemies.remove(enemy)

        # 更新炮弹
        for projectile in self.projectiles[:]:
            hit_pos = projectile.update(dt)
            if hit_pos:
                # 处理命中
                projectiles_to_remove = []
                for enemy in self.enemies:
                    enemy_pos = enemy.path.points[enemy.index]
                    dist = math.hypot(enemy_pos.x - hit_pos.x, enemy_pos.y - hit_pos.y)
                    if dist <= projectile.splash_radius if projectile.splash_radius else dist <= 15:
                        enemy.deal_damage(projectile.damage)
                        if projectile.slow_duration > 0:
                            enemy.apply_slow(projectile.slow_duration)
                        if dist <= 20:
                            enemy.deal_damage(0)  # 仅用于标记打击效果
                self.projectiles.remove(projectile)

        # 塔攻击
        for tower in self.buildings:
            tower.fire(self.enemies, self.projectiles, current_time)

        # 清理减速效果
        for enemy in self.enemies:
            enemy.clean_slow(dt / 1000)

        # 检查游戏结束
        if self.lives <= 0:
            self.game_over = True

    def draw(self):
        self.screen.fill(COLORS['background'])

        # 绘制地图
        self.map.draw(self.screen)

        # 基地
        pygame.draw.rect(self.screen, COLORS['base'], 
                        (19 * TILE_SIZE, 14 * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(self.screen, (0, 0, 0), 
                        (19 * TILE_SIZE, 14 * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)

        # 入口
        pygame.draw.rect(self.screen, COLORS['spawn_point'], 
                         (0 * TILE_SIZE, 2 * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(self.screen, (0, 0, 0), 
                         (0 * TILE_SIZE, 2 * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)

        # 绘制基地生命（右上角）
        lives_text = self.font.render(f"Lives: {max(0, self.lives)}", True, COLORS['health_bar'])
        self.screen.blit(lives_text, (MAP_WIDTH + 20, 20))

        # 绘制金币
        gold_text = self.font.render(f"Gold: {self.money}", True, COLORS['gold'])
        self.screen.blit(gold_text, (MAP_WIDTH + 20, 50))

        # 波次信息
        wave_text = self.font.render(f"Wave: {self.wave_number}/{len(WAVE_ENEMIES)}", True, COLORS['text'])
        self.screen.blit(wave_text, (MAP_WIDTH + 20, 80))

        # 剩余敌人
        remaining_text = self.font.render(f"Enemies: {len(self.enemies)}", True, COLORS['text'])
        self.screen.blit(remaining_text, (MAP_WIDTH + 20, 110))

        # 当前选中塔信息
        if self.selected_tower in TOWER_TYPES:
            type_data = TOWER_TYPES[self.selected_tower]
            sel_text = self.font.render(f"Selected: {type_data['name']} Tower", True, type_data['color'])
            self.screen.blit(sel_text, (MAP_WIDTH + 20, 150))
            cost_text = self.font.render(f"Cost: {type_data['cost']}", True, COLORS['text'])
            self.screen.blit(cost_text, (MAP_WIDTH + 20, 180))

        # 塔
        for tower in self.buildings:
            tower.draw(self.screen)

        # 简单准星显示选中塔的范围
        if 0 <= self.hover_grid_x < MAP_COLS and 0 <= self.hover_grid_y < MAP_ROWS:
            if any(t.grid_x == self.hover_grid_x and t.grid_y == self.hover_grid_y for t in self.buildings):
                for t in self.buildings:
                    if t.grid_x == self.hover_grid_x and t.grid_y == self.hover_grid_y:
                        t.draw_range(self.screen, True)

        # 炮弹
        for projectile in self.projectiles:
            if projectile and projectile.active:
                projectile.draw(self.screen)

        # 敌人
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # 提示（如果可以建造）
        if 0 <= self.hover_grid_x < MAP_COLS and 0 <= self.hover_grid_y < MAP_ROWS:
            if self.can_build(self.hover_grid_x, self.hover_grid_y):
                # 预览位置
                preview_rect = pygame.Rect(
                    self.hover_grid_x * TILE_SIZE, 
                    self.hover_grid_y * TILE_SIZE, 
                    TILE_SIZE, TILE_SIZE
                )
                pygame.draw.rect(self.screen, (0, 255, 0, 50), preview_rect)
            else:
                # 不可建造
                if self.map.rects and any(rect.collidepoint((self.hover_grid_x * TILE_SIZE + TILE_SIZE // 2, self.hover_grid_y * TILE_SIZE + TILE_SIZE // 2)) for rect in self.map.rects):
                    # 在路径上
                    pass
                else:
                    # 其他不可建造位置
                    pass

        # 显示消息（胜利/失败）
        if self.game_over:
            if self.victory:
                msg = self.big_font.render("YOU WIN!", True, (0, 255, 0))
                sub_msg = self.font.render(f"Final Wave: {self.wave_number}", True, COLORS['text'])
            else:
                msg = self.big_font.render("GAME OVER", True, (255, 0, 0))
                sub_msg = self.font.render(f"Final Wave: {self.wave_number}", True, COLORS['text'])
            
            rect = msg.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
            sub_rect = sub_msg.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
            
            # 半透明背景
            bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(bg, (0, 0, 0, 180), (0, 0, WIDTH, HEIGHT))
            self.screen.blit(bg, (0, 0))
            
            self.screen.blit(msg, rect)
            self.screen.blit(sub_msg, sub_rect)
            
            restart_text = self.font.render("Press R to Restart", True, COLORS['text'])
            restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))
            self.screen.blit(restart_text, restart_rect)

        # 提示
        hint_text = self.font.render("Build Tower (LMB) / Upgrade (RMB)", True, COLORS['text'])
        self.screen.blit(hint_text, (MAP_WIDTH + 20, 220))
        hint_keys = self.font.render("Keys: [1] Arrow | [2] Cannon | [3] Slow | [ESC] Exit | [R] Restart", True, COLORS['text'])
        self.screen.blit(hint_keys, (MAP_WIDTH + 20, 250))

        pygame.display.flip()

    def run(self):
        while self.handle_events():
            self.update()
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()