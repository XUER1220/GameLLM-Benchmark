import pygame
import random
import math

# 初始化
pygame.init()
random.seed(42)

# 窗口尺寸
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 32
GRID_COLS = 20
GRID_ROWS = 15
MAP_WIDTH = GRID_COLS * GRID_SIZE
MAP_HEIGHT = GRID_ROWS * GRID_SIZE
HUD_WIDTH = SCREEN_WIDTH - MAP_WIDTH
FPS = 60

# 颜色
COLOR_GROUND = (100, 180, 100)
COLOR_PATH = (150, 120, 80)
COLOR_ENTRY = (200, 80, 80)
COLOR_BASE = (80, 80, 200)
COLOR_GRID = (50, 50, 50)
COLOR_HUD_BG = (30, 30, 40)
COLOR_HUD_TEXT = (220, 220, 220)
COLOR_SELECTED = (255, 255, 100)
COLOR_RANGE = (255, 255, 255, 100)
COLOR_ARROW_TOWER = (70, 130, 180)
COLOR_CANNON_TOWER = (180, 70, 70)
COLOR_SLOW_TOWER = (180, 70, 180)
COLOR_ENEMY_NORMAL = (200, 200, 100)
COLOR_ENEMY_FAST = (100, 200, 200)
COLOR_ENEMY_HEAVY = (150, 100, 100)
COLOR_PROJECTILE_ARROW = (220, 220, 220)
COLOR_PROJECTILE_CANNON = (255, 165, 0)
COLOR_PROJECTILE_SLOW = (180, 100, 255)
COLOR_EFFECT_SPLASH = (255, 200, 50)
COLOR_SLOW_EFFECT = (100, 150, 255)

# 游戏常量
INITIAL_COINS = 180
INITIAL_LIVES = 20
TOWER_COST = {"arrow": 50, "cannon": 80, "slow": 70}
UPGRADE_COST_RATIO = 0.7
MAX_UPGRADE_LEVEL = 2
PREPARE_TIME = 3  # 秒
WAVE_COUNT = 5

# 敌人波次定义
WAVE_DATA = [
    {"normal": 5, "fast": 2, "heavy": 0},
    {"normal": 8, "fast": 3, "heavy": 1},
    {"normal": 10, "fast": 5, "heavy": 2},
    {"normal": 12, "fast": 6, "heavy": 3},
    {"normal": 15, "fast": 8, "heavy": 5}
]

# 敌人属性
ENEMY_STATS = {
    "normal": {"speed": 0.8, "health": 30, "reward": 10},
    "fast": {"speed": 1.5, "health": 15, "reward": 15},
    "heavy": {"speed": 0.5, "health": 80, "reward": 25}
}

# 塔属性
TOWER_STATS = {
    "arrow": {"range": 120, "damage": 8, "cooldown": 0.8},
    "cannon": {"range": 105, "damage": 14, "cooldown": 1.2, "splash": 45},
    "slow": {"range": 110, "damage": 4, "cooldown": 1.0, "slow_duration": 2.0}
}

# 固定路径点（网格坐标）
PATH_POINTS = [
    (0, 7), (5, 7), (5, 3), (10, 3), (10, 10), (15, 10), (15, 5), (19, 5)
]

class Enemy:
    def __init__(self, enemy_type, waypoints):
        self.type = enemy_type
        stats = ENEMY_STATS[enemy_type]
        self.speed = stats["speed"]
        self.max_health = stats["health"]
        self.health = self.max_health
        self.reward = stats["reward"]
        self.waypoints = waypoints
        self.current_wp = 0
        self.pos = [waypoints[0][0] * GRID_SIZE + GRID_SIZE//2,
                    waypoints[0][1] * GRID_SIZE + GRID_SIZE//2]
        self.radius = 10
        self.slow_timer = 0

    def move(self, dt):
        if self.slow_timer > 0:
            speed = self.speed * 0.5
            self.slow_timer -= dt
        else:
            speed = self.speed
        if self.current_wp >= len(self.waypoints)-1:
            return True  # 到达基地
        target = self.waypoints[self.current_wp+1]
        target_px = (target[0] * GRID_SIZE + GRID_SIZE//2,
                     target[1] * GRID_SIZE + GRID_SIZE//2)
        dx = target_px[0] - self.pos[0]
        dy = target_px[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist < speed * dt * 60:
            self.current_wp += 1
            if self.current_wp >= len(self.waypoints)-1:
                return True
        else:
            self.pos[0] += (dx / dist) * speed * dt * 60
            self.pos[1] += (dy / dist) * speed * dt * 60
        return False

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

    def apply_slow(self, duration):
        self.slow_timer = duration

    def draw(self, screen):
        color = COLOR_ENEMY_NORMAL if self.type == "normal" else \
                COLOR_ENEMY_FAST if self.type == "fast" else COLOR_ENEMY_HEAVY
        pygame.draw.circle(screen, color, (int(self.pos[0]), int(self.pos[1])), self.radius)
        # 血条
        bar_width = 30
        bar_height = 4
        x = int(self.pos[0] - bar_width//2)
        y = int(self.pos[1] - self.radius - 8)
        pygame.draw.rect(screen, (200, 0, 0), (x, y, bar_width, bar_height))
        fill = int((self.health / self.max_health) * bar_width)
        pygame.draw.rect(screen, (0, 200, 0), (x, y, fill, bar_height))
        # 减速效果
        if self.slow_timer > 0:
            pygame.draw.circle(screen, COLOR_SLOW_EFFECT, (int(self.pos[0]), int(self.pos[1])), self.radius+2, 2)

class Tower:
    def __init__(self, tower_type, grid_x, grid_y):
        self.type = tower_type
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.px_x = grid_x * GRID_SIZE + GRID_SIZE//2
        self.px_y = grid_y * GRID_SIZE + GRID_SIZE//2
        self.level = 0
        self.cooldown = 0
        self.target = None
        self.projectiles = []

    def update(self, dt, enemies):
        self.cooldown = max(0, self.cooldown - dt)
        if self.cooldown <= 0:
            self.find_target(enemies)
            if self.target:
                self.shoot()
                self.cooldown = TOWER_STATS[self.type]["cooldown"]
        self.update_projectiles(dt)

    def find_target(self, enemies):
        best = None
        best_dist = float('inf')
        range_sq = (self.get_range() ** 2)
        for e in enemies:
            dx = e.pos[0] - self.px_x
            dy = e.pos[1] - self.px_y
            dist_sq = dx*dx + dy*dy
            if dist_sq <= range_sq:
                # 选择最接近基地的敌人
                wp_index = e.current_wp
                if wp_index > best_dist or best is None:
                    best_dist = wp_index
                    best = e
        self.target = best

    def shoot(self):
        if self.target:
            if self.type == "arrow":
                self.projectiles.append({
                    "type": "arrow",
                    "x": self.px_x,
                    "y": self.px_y,
                    "target": self.target,
                    "damage": self.get_damage()
                })
            elif self.type == "cannon":
                self.projectiles.append({
                    "type": "cannon",
                    "x": self.px_x,
                    "y": self.px_y,
                    "target": self.target,
                    "damage": self.get_damage(),
                    "splash": TOWER_STATS["cannon"]["splash"]
                })
            elif self.type == "slow":
                self.projectiles.append({
                    "type": "slow",
                    "x": self.px_x,
                    "y": self.px_y,
                    "target": self.target,
                    "damage": self.get_damage(),
                    "slow_duration": TOWER_STATS["slow"]["slow_duration"]
                })

    def update_projectiles(self, dt):
        speed = 300 * dt
        to_remove = []
        for i, p in enumerate(self.projectiles):
            tx = p["target"].pos[0]
            ty = p["target"].pos[1]
            dx = tx - p["x"]
            dy = ty - p["y"]
            dist = math.hypot(dx, dy)
            if dist < speed:
                # 命中
                if p["type"] == "arrow":
                    if p["target"].take_damage(p["damage"]):
                        self.target = None
                elif p["type"] == "cannon":
                    p["target"].take_damage(p["damage"])
                    splash = p["splash"]
                    for e in enemies:
                        if e is not p["target"]:
                            dx2 = e.pos[0] - tx
                            dy2 = e.pos[1] - ty
                            if math.hypot(dx2, dy2) <= splash:
                                e.take_damage(p["damage"] // 2)
                elif p["type"] == "slow":
                    p["target"].take_damage(p["damage"])
                    p["target"].apply_slow(p["slow_duration"])
                to_remove.append(i)
            else:
                p["x"] += (dx / dist) * speed
                p["y"] += (dy / dist) * speed
        for i in reversed(to_remove):
            self.projectiles.pop(i)

    def get_range(self):
        base = TOWER_STATS[self.type]["range"]
        return base + self.level * 10

    def get_damage(self):
        base = TOWER_STATS[self.type]["damage"]
        return base + self.level * 5

    def upgrade_cost(self):
        return int(TOWER_COST[self.type] * UPGRADE_COST_RATIO)

    def draw(self, screen, show_range=False):
        color = COLOR_ARROW_TOWER if self.type == "arrow" else \
                COLOR_CANNON_TOWER if self.type == "cannon" else COLOR_SLOW_TOWER
        pygame.draw.rect(screen, color,
                         (self.grid_x * GRID_SIZE + 2,
                          self.grid_y * GRID_SIZE + 2,
                          GRID_SIZE - 4, GRID_SIZE - 4))
        # 等级显示
        font = pygame.font.SysFont(None, 20)
        level_text = font.render(str(self.level+1), True, (255, 255, 255))
        screen.blit(level_text, (self.grid_x * GRID_SIZE + GRID_SIZE//2 - 5,
                                 self.grid_y * GRID_SIZE + GRID_SIZE//2 - 10))
        # 射程
        if show_range:
            s = pygame.Surface((self.get_range()*2, self.get_range()*2), pygame.SRCALPHA)
            pygame.draw.circle(s, COLOR_RANGE, (self.get_range(), self.get_range()), self.get_range())
            screen.blit(s, (self.px_x - self.get_range(), self.px_y - self.get_range()), special_flags=pygame.BLEND_ALPHA_SDL2)

    def draw_projectiles(self, screen):
        for p in self.projectiles:
            color = COLOR_PROJECTILE_ARROW if p["type"] == "arrow" else \
                    COLOR_PROJECTILE_CANNON if p["type"] == "cannon" else COLOR_PROJECTILE_SLOW
            radius = 4 if p["type"] == "arrow" else 6 if p["type"] == "cannon" else 5
            pygame.draw.circle(screen, color, (int(p["x"]), int(p["y"])), radius)

def generate_waypoints():
    # 将网格路径点转换为像素点列表
    points = [(x * GRID_SIZE + GRID_SIZE//2, y * GRID_SIZE + GRID_SIZE//2) for x, y in PATH_POINTS]
    return points

def is_path_or_base(grid_x, grid_y):
    # 检查是否在路径上
    for i in range(len(PATH_POINTS)-1):
        x1, y1 = PATH_POINTS[i]
        x2, y2 = PATH_POINTS[i+1]
        if x1 == x2:
            if grid_x == x1 and min(y1, y2) <= grid_y <= max(y1, y2):
                return True
        elif y1 == y2:
            if grid_y == y1 and min(x1, x2) <= grid_x <= max(x1, x2):
                return True
    # 检查是否在基地
    if grid_x == GRID_COLS-1 and grid_y == PATH_POINTS[-1][1]:
        return True
    # 检查是否在入口
    if grid_x == 0 and grid_y == PATH_POINTS[0][1]:
        return True
    return False

def draw_map(screen):
    # 地面
    screen.fill(COLOR_GROUND, (0, 0, MAP_WIDTH, MAP_HEIGHT))
    # 路径
    for i in range(len(PATH_POINTS)-1):
        x1, y1 = PATH_POINTS[i]
        x2, y2 = PATH_POINTS[i+1]
        if x1 == x2:
            pygame.draw.rect(screen, COLOR_PATH,
                             (x1 * GRID_SIZE, min(y1, y2) * GRID_SIZE,
                              GRID_SIZE, (abs(y2 - y1) + 1) * GRID_SIZE))
        elif y1 == y2:
            pygame.draw.rect(screen, COLOR_PATH,
                             (min(x1, x2) * GRID_SIZE, y1 * GRID_SIZE,
                              (abs(x2 - x1) + 1) * GRID_SIZE, GRID_SIZE))
    # 入口
    entry_x, entry_y = PATH_POINTS[0]
    pygame.draw.rect(screen, COLOR_ENTRY,
                     (entry_x * GRID_SIZE, entry_y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
    # 基地
    base_x, base_y = PATH_POINTS[-1]
    pygame.draw.rect(screen, COLOR_BASE,
                     (base_x * GRID_SIZE, base_y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
    # 网格线
    for x in range(GRID_COLS + 1):
        pygame.draw.line(screen, COLOR_GRID, (x * GRID_SIZE, 0), (x * GRID_SIZE, MAP_HEIGHT))
    for y in range(GRID_ROWS + 1):
        pygame.draw.line(screen, COLOR_GRID, (0, y * GRID_SIZE), (MAP_WIDTH, y * GRID_SIZE))

def draw_hud(screen, coins, lives, wave, enemies_left, selected_tower, game_over, win):
    hud_rect = pygame.Rect(MAP_WIDTH, 0, HUD_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, COLOR_HUD_BG, hud_rect)
    font = pygame.font.SysFont(None, 28)
    small_font = pygame.font.SysFont(None, 22)
    y = 20
    # 金币
    coins_text = font.render(f"Coins: {coins}", True, COLOR_HUD_TEXT)
    screen.blit(coins_text, (MAP_WIDTH + 20, y)); y += 40
    # 生命
    lives_text = font.render(f"Lives: {lives}", True, COLOR_HUD_TEXT)
    screen.blit(lives_text, (MAP_WIDTH + 20, y)); y += 40
    # 波次
    wave_text = font.render(f"Wave: {wave}/{WAVE_COUNT}", True, COLOR_HUD_TEXT)
    screen.blit(wave_text, (MAP_WIDTH + 20, y)); y += 40
    # 剩余敌人
    enemies_text = font.render(f"Enemies: {enemies_left}", True, COLOR_HUD_TEXT)
    screen.blit(enemies_text, (MAP_WIDTH + 20, y)); y += 40
    # 选中的塔
    if selected_tower:
        tower_name = {"arrow": "Arrow Tower", "cannon": "Cannon Tower", "slow": "Slow Tower"}[selected_tower]
        selected_text = font.render(f"Selected: {tower_name}", True, COLOR_HUD_TEXT)
        screen.blit(selected_text, (MAP_WIDTH + 20, y)); y += 40
        cost_text = small_font.render(f"Cost: {TOWER_COST[selected_tower]}", True, COLOR_HUD_TEXT)
        screen.blit(cost_text, (MAP_WIDTH + 20, y)); y += 30
        if selected_tower == "arrow":
            desc = "Single target"
        elif selected_tower == "cannon":
            desc = "Splash damage"
        else:
            desc = "Slows enemies"
        desc_text = small_font.render(desc, True, COLOR_HUD_TEXT)
        screen.blit(desc_text, (MAP_WIDTH + 20, y)); y += 30
    else:
        none_text = font.render("Selected: None", True, COLOR_HUD_TEXT)
        screen.blit(none_text, (MAP_WIDTH + 20, y)); y += 40
    # 控制提示
    y += 20
    controls = [
        "1: Arrow Tower",
        "2: Cannon Tower",
        "3: Slow Tower",
        "L-Click: Build",
        "R-Click: Upgrade",
        "R: Restart",
        "ESC: Quit"
    ]
    for c in controls:
        c_text = small_font.render(c, True, COLOR_HUD_TEXT)
        screen.blit(c_text, (MAP_WIDTH + 20, y)); y += 25
    # 游戏结束信息
    if game_over:
        y = SCREEN_HEIGHT - 120
        if win:
            result_text = font.render("You Win!", True, (0, 255, 0))
        else:
            result_text = font.render("Game Over", True, (255, 0, 0))
        screen.blit(result_text, (MAP_WIDTH + 20, y)); y += 40
        restart_text = small_font.render("Press R to Restart", True, COLOR_HUD_TEXT)
        screen.blit(restart_text, (MAP_WIDTH + 20, y))

def spawn_wave(wave_index):
    enemies = []
    data = WAVE_DATA[wave_index]
    for etype, count in data.items():
        for _ in range(count):
            enemies.append(Enemy(etype, PATH_POINTS))
    return enemies

# 主游戏类
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Defense Hard")
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.coins = INITIAL_COINS
        self.lives = INITIAL_LIVES
        self.wave = 0
        self.enemies = []
        self.towers = []
        self.selected_tower = "arrow"
        self.game_over = False
        self.win = False
        self.wave_finished = True
        self.prepare_timer = PREPARE_TIME
        self.spawned_this_wave = False

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
                    elif event.key == pygame.K_1:
                        self.selected_tower = "arrow"
                    elif event.key == pygame.K_2:
                        self.selected_tower = "cannon"
                    elif event.key == pygame.K_3:
                        self.selected_tower = "slow"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if mx < MAP_WIDTH and my < MAP_HEIGHT and not self.game_over:
                        grid_x = mx // GRID_SIZE
                        grid_y = my // GRID_SIZE
                        if event.button == 1:  # 左键建塔
                            if not is_path_or_base(grid_x, grid_y):
                                # 检查位置是否空闲
                                occupied = False
                                for t in self.towers:
                                    if t.grid_x == grid_x and t.grid_y == grid_y:
                                        occupied = True
                                        break
                                if not occupied and self.coins >= TOWER_COST[self.selected_tower]:
                                    self.towers.append(Tower(self.selected_tower, grid_x, grid_y))
                                    self.coins -= TOWER_COST[self.selected_tower]
                        elif event.button == 3:  # 右键升级
                            for t in self.towers:
                                if t.grid_x == grid_x and t.grid_y == grid_y and t.level < MAX_UPGRADE_LEVEL:
                                    cost = t.upgrade_cost()
                                    if self.coins >= cost:
                                        t.level += 1
                                        self.coins -= cost
                                    break

            if not self.game_over:
                self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def update(self, dt):
        # 波次逻辑
        if self.wave_finished:
            self.prepare_timer -= dt
            if self.prepare_timer <= 0:
                if self.wave < WAVE_COUNT:
                    self.enemies = spawn_wave(self.wave)
                    self.spawned_this_wave = True
                    self.wave_finished = False
                    self.wave += 1
                else:
                    self.game_over = True
                    self.win = True
        else:
            # 更新敌人
            to_remove = []
            for e in self.enemies:
                if e.move(dt):
                    self.lives -= 1
                    to_remove.append(e)
                elif e.health <= 0:
                    self.coins += e.reward
                    to_remove.append(e)
            for e in to_remove:
                self.enemies.remove(e)
            # 检查波次结束
            if len(self.enemies) == 0 and self.spawned_this_wave:
                self.wave_finished = True
                self.prepare_timer = PREPARE_TIME
                self.spawned_this_wave = False
                if self.wave >= WAVE_COUNT and not self.enemies:
                    self.game_over = True
                    self.win = self.lives > 0
            # 更新塔
            for t in self.towers:
                t.update(dt, self.enemies)
        # 检查游戏失败
        if self.lives <= 0:
            self.game_over = True
            self.win = False

    def draw(self):
        self.screen.fill((0, 0, 0))
        draw_map(self.screen)
        # 绘制塔
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hover_grid_x = mouse_x // GRID_SIZE if mouse_x < MAP_WIDTH else -1
        hover_grid_y = mouse_y // GRID_SIZE if mouse_y < MAP_HEIGHT else -1
        for t in self.towers:
            show = (hover_grid_x == t.grid_x and hover_grid_y == t.grid_y)
            t.draw(self.screen, show)
            t.draw_projectiles(self.screen)
        # 绘制敌人
        for e in self.enemies:
            e.draw(self.screen)
        # 绘制HUD
        enemies_left = len(self.enemies) if not self.wave_finished else 0
        draw_hud(self.screen, self.coins, self.lives, self.wave, enemies_left,
                 self.selected_tower, self.game_over, self.win)
        # 准备倒计时
        if self.wave_finished and self.prepare_timer > 0 and not self.game_over:
            font = pygame.font.SysFont(None, 48)
            timer_text = font.render(f"Next wave in: {int(self.prepare_timer)}", True, (255, 255, 255))
            self.screen.blit(timer_text, (MAP_WIDTH//2 - 100, MAP_HEIGHT//2))

if __name__ == "__main__":
    game = Game()
    game.run()