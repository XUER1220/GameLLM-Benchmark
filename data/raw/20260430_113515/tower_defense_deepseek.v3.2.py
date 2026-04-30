import pygame
import random
import math

pygame.init()
random.seed(42)

# 窗口和游戏常量
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
TILE_SIZE = 32
GRID_COLS, GRID_ROWS = 20, 15
MAP_WIDTH, MAP_HEIGHT = GRID_COLS * TILE_SIZE, GRID_ROWS * TILE_SIZE
HUD_WIDTH = SCREEN_WIDTH - MAP_WIDTH

# 颜色定义
COLOR_BG = (40, 44, 52)
COLOR_GROUND = (60, 70, 90)
COLOR_PATH = (128, 96, 77)
COLOR_ENTRY = (100, 200, 100)
COLOR_BASE = (200, 100, 100)
COLOR_HUD_BG = (30, 33, 40)
COLOR_HUD_TEXT = (220, 220, 220)
COLOR_UI_BORDER = (70, 130, 180)
COLOR_TOWER_SLOT = (50, 55, 65)
COLOR_ARROW_TOWER = (86, 156, 214)
COLOR_CANNON_TOWER = (220, 163, 57)
COLOR_SLOW_TOWER = (152, 118, 170)
COLOR_ENEMY_NORMAL = (220, 100, 100)
COLOR_ENEMY_FAST = (100, 180, 220)
COLOR_ENEMY_HEAVY = (180, 180, 100)
COLOR_PROJECTILE_ARROW = (200, 200, 240)
COLOR_PROJECTILE_CANNON = (240, 160, 60)
COLOR_PROJECTILE_SLOW = (180, 140, 220)
COLOR_SELECTED = (255, 255, 100)
COLOR_RANGE_INDICATOR = (255, 255, 255, 80)

# 游戏参数
INITIAL_GOLD = 180
BASE_HEALTH = 20
PREPARE_TIME = 3  # 秒
WAVE_COUNT = 5

# 塔常数
TOWER_TYPES = {
    1: {"name": "Arrow Tower", "cost": 50, "range": 120, "damage": 8, "cooldown": 0.8, "color": COLOR_ARROW_TOWER, "projectile_color": COLOR_PROJECTILE_ARROW},
    2: {"name": "Cannon Tower", "cost": 80, "range": 105, "damage": 14, "cooldown": 1.2, "color": COLOR_CANNON_TOWER, "projectile_color": COLOR_PROJECTILE_CANNON, "splash": 45},
    3: {"name": "Slow Tower", "cost": 70, "range": 110, "damage": 4, "cooldown": 1.0, "color": COLOR_SLOW_TOWER, "projectile_color": COLOR_PROJECTILE_SLOW, "slow_duration": 2.0}
}
UPGRADE_COST_MULTIPLIER = 0.7
MAX_UPGRADE_LEVEL = 2
UPGRADE_BONUS_RANGE = 15
UPGRADE_BONUS_DAMAGE_MULT = 1.5

# 敌人常数
ENEMY_TYPES = [
    {"name": "Normal", "health": 30, "speed": 0.8, "gold": 15, "color": COLOR_ENEMY_NORMAL},
    {"name": "Fast", "health": 18, "speed": 1.6, "gold": 10, "color": COLOR_ENEMY_FAST},
    {"name": "Heavy", "health": 80, "speed": 0.5, "gold": 30, "color": COLOR_ENEMY_HEAVY}
]

# 波次定义 (数量, 类型索引) 类型: 0=Normal, 1=Fast, 2=Heavy
WAVE_DEFINITIONS = [
    [(10, 0)],
    [(8, 0), (6, 1)],
    [(12, 0), (4, 2)],
    [(6, 1), (10, 2)],
    [(5, 0), (8, 1), (7, 2)]
]

# 路径定义（网格坐标，从入口到基地折线）
PATH_POINTS = [
    (0, 4), (6, 4), (6, 8), (12, 8), (12, 2), (18, 2), (19, 2)  # 最后一点为基地前列
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
        self.selected_tower_type = 1
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.wave_index = 0
        self.wave_enemies_left = 0
        self.wave_spawned = False
        self.game_over = False
        self.victory = False
        self.prepare_timer = PREPARE_TIME
        self.buildable_map = self.generate_buildable_map()
        self.entry_pos = self.grid_to_pixel(PATH_POINTS[0])
        self.base_pos = self.grid_to_pixel(PATH_POINTS[-1])
        self.path_pixel_points = [self.grid_to_pixel(p) for p in PATH_POINTS]

    def generate_buildable_map(self):
        # 标记所有路径格子为不可建造
        buildable = [[True for _ in range(GRID_ROWS)] for __ in range(GRID_COLS)]
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                if self.is_path_grid(x, y):
                    buildable[x][y] = False
        # 入口和基地格子
        ex, ey = PATH_POINTS[0]
        bx, by = PATH_POINTS[-1]
        buildable[ex][ey] = False
        buildable[bx][by] = False
        return buildable

    def is_path_grid(self, gx, gy):
        # 检查网格是否在路径线段上（简化版：检查网格中心点到所有线段的距离）
        for i in range(len(PATH_POINTS)-1):
            p1 = self.grid_to_pixel(PATH_POINTS[i])
            p2 = self.grid_to_pixel(PATH_POINTS[i+1])
            center = (gx * TILE_SIZE + TILE_SIZE//2, gy * TILE_SIZE + TILE_SIZE//2)
            if self.point_segment_distance(center, p1, p2) < TILE_SIZE/2:
                return True
        return False

    def point_segment_distance(self, p, a, b):
        # 计算点p到线段ab的距离
        ap = (p[0]-a[0], p[1]-a[1])
        ab = (b[0]-a[0], b[1]-a[1])
        dot = ap[0]*ab[0] + ap[1]*ab[1]
        ab_len_sq = ab[0]**2 + ab[1]**2
        if ab_len_sq == 0:
            return math.dist(p, a)
        t = max(0, min(1, dot / ab_len_sq))
        closest = (a[0] + t*ab[0], a[1] + t*ab[1])
        return math.dist(p, closest)

    def grid_to_pixel(self, grid_pos):
        return (grid_pos[0] * TILE_SIZE + TILE_SIZE//2, grid_pos[1] * TILE_SIZE + TILE_SIZE//2)

    def pixel_to_grid(self, pixel_pos):
        return (pixel_pos[0] // TILE_SIZE, pixel_pos[1] // TILE_SIZE)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        self.selected_tower_type = int(event.unicode)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_over:
                        continue
                    mx, my = pygame.mouse.get_pos()
                    if mx < MAP_WIDTH:
                        gx, gy = self.pixel_to_grid((mx, my))
                        if 0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS:
                            if event.button == 1:  # 左键建塔
                                self.build_tower(gx, gy)
                            elif event.button == 3:  # 右键升级
                                self.upgrade_tower(gx, gy)
            if not self.game_over:
                self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def build_tower(self, gx, gy):
        if not self.buildable_map[gx][gy]:
            return
        for t in self.towers:
            if t.grid_x == gx and t.grid_y == gy:
                return
        tower_info = TOWER_TYPES[self.selected_tower_type]
        if self.gold >= tower_info["cost"]:
            self.towers.append(Tower(gx, gy, self.selected_tower_type))
            self.gold -= tower_info["cost"]
            self.buildable_map[gx][gy] = False

    def upgrade_tower(self, gx, gy):
        for t in self.towers:
            if t.grid_x == gx and t.grid_y == gy and t.level < MAX_UPGRADE_LEVEL:
                cost = int(TOWER_TYPES[t.type]["cost"] * UPGRADE_COST_MULTIPLIER)
                if self.gold >= cost:
                    t.upgrade()
                    self.gold -= cost
                break

    def start_wave(self):
        if self.wave_spawned or self.wave_index >= WAVE_COUNT:
            return
        self.wave_enemies_left = 0
        for count, etype in WAVE_DEFINITIONS[self.wave_index]:
            for _ in range(count):
                self.enemies.append(Enemy(etype, self.path_pixel_points))
                self.wave_enemies_left += 1
        self.wave_spawned = True

    def update(self, dt):
        if self.wave_index >= WAVE_COUNT:
            if not self.enemies:
                self.victory = True
                self.game_over = True
            return
        if not self.wave_spawned:
            self.prepare_timer -= dt
            if self.prepare_timer <= 0:
                self.start_wave()
                self.prepare_timer = PREPARE_TIME
        # 更新敌人
        for enemy in self.enemies[:]:
            enemy.update(dt)
            if enemy.reached_base:
                self.base_health -= 1
                self.enemies.remove(enemy)
                if self.base_health <= 0:
                    self.game_over = True
        # 更新塔
        for tower in self.towers:
            tower.update(dt, self.enemies, self.projectiles)
        # 更新炮弹
        for proj in self.projectiles[:]:
            proj.update(dt, self.enemies)
            if proj.hit or proj.lifetime <= 0:
                self.projectiles.remove(proj)
        # 检查波次结束
        if self.wave_spawned and not self.enemies:
            self.wave_index += 1
            self.wave_spawned = False
            if self.wave_index >= WAVE_COUNT:
                return

    def draw(self):
        self.screen.fill(COLOR_BG)
        # 绘制地图背景
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if self.buildable_map[x][y]:
                    pygame.draw.rect(self.screen, COLOR_GROUND, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_PATH, rect)
        # 绘制路径线
        for i in range(len(self.path_pixel_points)-1):
            pygame.draw.line(self.screen, (200, 150, 120), self.path_pixel_points[i], self.path_pixel_points[i+1], 4)
        # 绘制入口和基地
        pygame.draw.circle(self.screen, COLOR_ENTRY, self.entry_pos, TILE_SIZE//2)
        pygame.draw.circle(self.screen, COLOR_BASE, self.base_pos, TILE_SIZE//2)
        # 绘制塔
        for tower in self.towers:
            tower.draw(self.screen)
        # 绘制敌人
        for enemy in self.enemies:
            enemy.draw(self.screen)
        # 绘制炮弹
        for proj in self.projectiles:
            proj.draw(self.screen)
        # 绘制鼠标悬停范围指示
        mx, my = pygame.mouse.get_pos()
        if mx < MAP_WIDTH:
            gx, gy = self.pixel_to_grid((mx, my))
            if 0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS and self.buildable_map[gx][gy]:
                pygame.draw.rect(self.screen, COLOR_UI_BORDER, (gx*TILE_SIZE, gy*TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)
                tower_info = TOWER_TYPES[self.selected_tower_type]
                range_pix = tower_info["range"]
                surf = pygame.Surface((range_pix*2, range_pix*2), pygame.SRCALPHA)
                pygame.draw.circle(surf, COLOR_RANGE_INDICATOR, (range_pix, range_pix), range_pix)
                self.screen.blit(surf, (mx-range_pix, my-range_pix))
        # 绘制HUD面板
        hud_rect = pygame.Rect(MAP_WIDTH, 0, HUD_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_HUD_BG, hud_rect)
        pygame.draw.line(self.screen, COLOR_UI_BORDER, (MAP_WIDTH, 0), (MAP_WIDTH, SCREEN_HEIGHT), 2)
        # 文字信息
        y_offset = 20
        lines = [
            f"Base HP: {self.base_health}/{BASE_HEALTH}",
            f"Gold: {self.gold}",
            f"Wave: {self.wave_index+1}/{WAVE_COUNT}",
            f"Enemies: {len(self.enemies)}",
            f"Selected: {TOWER_TYPES[self.selected_tower_type]['name']}",
            f"Cost: {TOWER_TYPES[self.selected_tower_type]['cost']}",
            "",
            "Controls:",
            "1/2/3: Select Tower",
            "L-Click: Build",
            "R-Click: Upgrade",
            "R: Restart",
            "ESC: Quit"
        ]
        for line in lines:
            text = self.font.render(line, True, COLOR_HUD_TEXT)
            self.screen.blit(text, (MAP_WIDTH + 10, y_offset))
            y_offset += 30
        # 绘制塔选择按钮
        for i in (1,2,3):
            rect = pygame.Rect(MAP_WIDTH + 20, 400 + (i-1)*50, HUD_WIDTH - 40, 40)
            color = TOWER_TYPES[i]["color"]
            if self.selected_tower_type == i:
                pygame.draw.rect(self.screen, COLOR_SELECTED, rect, 3)
            pygame.draw.rect(self.screen, color, rect)
            text = self.font.render(f"{i}: {TOWER_TYPES[i]['name']}", True, (255,255,255))
            self.screen.blit(text, (rect.x+5, rect.centery - text.get_height()//2))
        # 准备时间或游戏结束提示
        if not self.wave_spawned and self.wave_index < WAVE_COUNT:
            text = self.big_font.render(f"Next Wave in {int(self.prepare_timer)+1}", True, (255,255,100))
            self.screen.blit(text, (MAP_WIDTH//2 - text.get_width()//2, 20))
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            self.screen.blit(overlay, (0,0))
            if self.victory:
                text = self.big_font.render("YOU WIN!", True, (100,255,100))
            else:
                text = self.big_font.render("GAME OVER", True, (255,100,100))
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 60))
            text2 = self.font.render(f"Wave: {self.wave_index}/{WAVE_COUNT}", True, COLOR_HUD_TEXT)
            self.screen.blit(text2, (SCREEN_WIDTH//2 - text2.get_width()//2, SCREEN_HEIGHT//2))
            text3 = self.font.render("Press R to Restart", True, COLOR_HUD_TEXT)
            self.screen.blit(text3, (SCREEN_WIDTH//2 - text3.get_width()//2, SCREEN_HEIGHT//2 + 60))

class Tower:
    def __init__(self, grid_x, grid_y, tower_type):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.type = tower_type
        self.level = 0
        info = TOWER_TYPES[tower_type]
        self.range = info["range"]
        self.damage = info["damage"]
        self.cooldown = info["cooldown"]
        self.color = info["color"]
        self.projectile_color = info["projectile_color"]
        self.splash = info.get("splash", 0)
        self.slow_duration = info.get("slow_duration", 0)
        self.x = grid_x * TILE_SIZE + TILE_SIZE//2
        self.y = grid_y * TILE_SIZE + TILE_SIZE//2
        self.target = None
        self.fire_timer = 0

    def upgrade(self):
        if self.level >= MAX_UPGRADE_LEVEL:
            return
        self.level += 1
        self.range += UPGRADE_BONUS_RANGE
        self.damage = int(self.damage * UPGRADE_BONUS_DAMAGE_MULT)

    def update(self, dt, enemies, projectiles):
        self.fire_timer -= dt
        if self.fire_timer > 0:
            return
        # 寻找目标
        self.target = None
        closest_dist = self.range
        for enemy in enemies:
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist <= self.range and dist < closest_dist:
                closest_dist = dist
                self.target = enemy
        if self.target:
            self.fire_timer = self.cooldown
            projectiles.append(Projectile(self, self.target))

    def draw(self, screen):
        radius = TILE_SIZE//2 - 2
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), radius)
        if self.level > 0:
            level_text = pygame.font.SysFont(None, 18).render(str(self.level), True, (255,255,255))
            screen.blit(level_text, (int(self.x - level_text.get_width()//2), int(self.y - level_text.get_height()//2)))
        # 如果正在瞄准，画一条线
        if self.target and self.fire_timer > self.cooldown*0.9:
            pygame.draw.line(screen, self.color, (self.x, self.y), (self.target.x, self.target.y), 2)

class Enemy:
    def __init__(self, type_index, path_points):
        self.type_index = type_index
        info = ENEMY_TYPES[type_index]
        self.max_health = info["health"]
        self.health = self.max_health
        self.speed = info["speed"]
        self.gold = info["gold"]
        self.color = info["color"]
        self.slow_timer = 0
        self.path_points = path_points[:]
        self.path_index = 0
        self.x, self.y = self.path_points[0]
        self.reached_base = False

    def update(self, dt):
        if self.slow_timer > 0:
            self.slow_timer -= dt
            effective_speed = self.speed * 0.4
        else:
            effective_speed = self.speed
        target_x, target_y = self.path_points[self.path_index + 1]
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < effective_speed * dt * 60:
            self.x = target_x
            self.y = target_y
            self.path_index += 1
            if self.path_index >= len(self.path_points) - 1:
                self.reached_base = True
        else:
            self.x += dx / dist * effective_speed * dt * 60
            self.y += dy / dist * effective_speed * dt * 60

    def draw(self, screen):
        radius = TILE_SIZE//3
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), radius)
        # 生命条
        bar_width = TILE_SIZE
        bar_height = 4
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (100,100,100), (self.x - bar_width//2, self.y - radius - 8, bar_width, bar_height))
        pygame.draw.rect(screen, (100,255,100), (self.x - bar_width//2, self.y - radius - 8, int(bar_width * health_ratio), bar_height))

class Projectile:
    def __init__(self, tower, target):
        self.tower = tower
        self.target = target
        self.x = tower.x
        self.y = tower.y
        self.speed = 300
        self.color = tower.projectile_color
        self.damage = tower.damage
        self.splash = tower.splash
        self.slow_duration = tower.slow_duration
        self.hit = False
        self.lifetime = 5.0

    def update(self, dt, enemies):
        self.lifetime -= dt
        if self.hit or self.target.health <= 0:
            self.hit = True
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < self.speed * dt:
            self.hit = True
            self.target.health -= self.damage
            if self.target.health <= 0:
                game.gold += self.target.gold
                if game.wave_spawned:
                    game.wave_enemies_left -= 1
            if self.slow_duration > 0:
                self.target.slow_timer = self.slow_duration
            if self.splash > 0:
                for enemy in enemies:
                    if enemy is self.target:
                        continue
                    edx = enemy.x - self.x
                    edy = enemy.y - self.y
                    if math.sqrt(edx*edx + edy*edy) <= self.splash:
                        enemy.health -= self.damage // 2
                        if enemy.health <= 0:
                            game.gold += enemy.gold
                            if game.wave_spawned:
                                game.wave_enemies_left -= 1
            return
        self.x += dx / dist * self.speed * dt
        self.y += dy / dist * self.speed * dt

    def draw(self, screen):
        radius = 4 if self.splash == 0 else 6
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), radius)
        if not self.hit and self.target:
            pygame.draw.line(screen, self.color, (self.x, self.y), (self.target.x, self.target.y), 1)

if __name__ == "__main__":
    game = Game()
    game.run()