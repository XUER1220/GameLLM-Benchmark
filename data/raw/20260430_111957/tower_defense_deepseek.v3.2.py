import pygame
import random
import math

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_WIDTH = 20
GRID_HEIGHT = 15
TILE_SIZE = 32
MAP_WIDTH = TILE_SIZE * GRID_WIDTH
MAP_HEIGHT = TILE_SIZE * GRID_HEIGHT
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
GREEN = (80, 200, 80)
PATH_COLOR = (160, 140, 100)
ENTRY_COLOR = (100, 200, 255)
BASE_COLOR = (255, 100, 100)
HUD_BG = (40, 40, 80)
HUD_TEXT = (220, 220, 255)
TOWER1_COLOR = (50, 150, 255)   
TOWER2_COLOR = (255, 150, 50)   
TOWER3_COLOR = (180, 80, 200)   
ENEMY1_COLOR = (150, 150, 150)  
ENEMY2_COLOR = (120, 220, 120)  
ENEMY3_COLOR = (220, 120, 120)  
BULLET_COLOR = (255, 255, 100)  
SLOW_EFFECT_COLOR = (100, 150, 255)

INITIAL_COINS = 180
BASE_HEALTH = 20

TOWER_TYPES = 3
TOWER_NAMES = ["Arrow", "Cannon", "Slow"]
TOWER_COST = [50, 80, 70]
TOWER_DAMAGE = [8, 14, 4]
TOWER_RANGE = [120, 105, 110]
TOWER_FIRE_RATE = [0.8, 1.2, 1.0]
TOWER_COLORS = [TOWER1_COLOR, TOWER2_COLOR, TOWER3_COLOR]
UPGRADE_COST_MULT = 0.7
MAX_LEVEL = 3

ENEMY_TYPES = 3
ENEMY_NAMES = ["Normal", "Fast", "Tank"]
ENEMY_SPEED = [1.4, 2.2, 0.8]
ENEMY_HEALTH = [30, 20, 80]
ENEMY_REWARD = [15, 10, 40]
ENEMY_COLORS = [ENEMY1_COLOR, ENEMY2_COLOR, ENEMY3_COLOR]

WAVES = [
    ([(0, 8), (1, 0), (2, 12)]),
    ([(0, 10), (1, 5), (2, 2)]),
    ([(0, 12), (1, 8), (2, 4)]),
    ([(0, 8), (1, 12), (2, 6)]),
    ([(0, 6), (1, 10), (2, 8)])
]

PREPARE_TIME = 3

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense Hard")
CLOCK = pygame.time.Clock()

FONT_SMALL = pygame.font.SysFont(None, 24)
FONT_MEDIUM = pygame.font.SysFont(None, 32)
FONT_LARGE = pygame.font.SysFont(None, 48)

PATH_GRIDS = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7), (11, 7), (12, 7), (13, 7), (14, 7), (15, 7), (16, 7), (17, 7), (18, 7), (19, 7)]
ENTRY_POS = (0 * TILE_SIZE + TILE_SIZE // 2, 7 * TILE_SIZE + TILE_SIZE // 2)
BASE_POS = (19 * TILE_SIZE + TILE_SIZE // 2, 7 * TILE_SIZE + TILE_SIZE // 2)

PATH_POINTS = [
    ENTRY_POS,
    (3 * TILE_SIZE + TILE_SIZE // 2, 7 * TILE_SIZE + TILE_SIZE // 2),
    (3 * TILE_SIZE + TILE_SIZE // 2, 3 * TILE_SIZE + TILE_SIZE // 2),
    (8 * TILE_SIZE + TILE_SIZE // 2, 3 * TILE_SIZE + TILE_SIZE // 2),
    (8 * TILE_SIZE + TILE_SIZE // 2, 11 * TILE_SIZE + TILE_SIZE // 2),
    (13 * TILE_SIZE + TILE_SIZE // 2, 11 * TILE_SIZE + TILE_SIZE // 2),
    (13 * TILE_SIZE + TILE_SIZE // 2, 7 * TILE_SIZE + TILE_SIZE // 2),
    BASE_POS
]

class Enemy:
    def __init__(self, etype):
        self.type = etype
        self.max_health = ENEMY_HEALTH[etype]
        self.health = self.max_health
        self.speed = ENEMY_SPEED[etype]
        self.reward = ENEMY_REWARD[etype]
        self.color = ENEMY_COLORS[etype]
        self.pos = list(PATH_POINTS[0])
        self.path_index = 0
        self.target_point = PATH_POINTS[1]
        self.radius = 10
        self.slowed_timer = 0
        self.slow_factor = 1.0

    def update(self):
        if self.slowed_timer > 0:
            self.slowed_timer -= 1/60
            speed = self.speed * 0.4
        else:
            speed = self.speed
        dx = self.target_point[0] - self.pos[0]
        dy = self.target_point[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist < speed:
            self.pos = list(self.target_point)
            self.path_index += 1
            if self.path_index >= len(PATH_POINTS):
                return False
            self.target_point = PATH_POINTS[self.path_index]
        else:
            self.pos[0] += dx / dist * speed
            self.pos[1] += dy / dist * speed
        return True

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)
        health_width = 30
        health_ratio = self.health / self.max_health
        pygame.draw.rect(surface, (255,0,0), (int(self.pos[0])-health_width//2, int(self.pos[1])-self.radius-8, health_width, 4))
        pygame.draw.rect(surface, (0,255,0), (int(self.pos[0])-health_width//2, int(self.pos[1])-self.radius-8, int(health_width*health_ratio), 4))
        if self.slowed_timer > 0:
            pygame.draw.circle(surface, SLOW_EFFECT_COLOR, (int(self.pos[0]), int(self.pos[1])), self.radius+2, 2)

    def hit(self, damage):
        self.health -= damage
        return self.health <= 0

    def slow(self, duration):
        self.slowed_timer = duration

class Bullet:
    def __init__(self, start, target, damage, splash=0, slow=False):
        self.pos = list(start)
        self.target = target
        self.damage = damage
        self.splash = splash
        self.slow = slow
        self.speed = 8.0
        self.active = True

    def update(self):
        dx = self.target.pos[0] - self.pos[0]
        dy = self.target.pos[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist < self.speed:
            self.active = False
            return True
        self.pos[0] += dx / dist * self.speed
        self.pos[1] += dy / dist * self.speed
        return False

    def draw(self, surface):
        pygame.draw.circle(surface, BULLET_COLOR, (int(self.pos[0]), int(self.pos[1])), 4)

class Tower:
    def __init__(self, tilex, tiley, ttype):
        self.grid = (tilex, tiley)
        self.pos = (tilex * TILE_SIZE + TILE_SIZE//2, tiley * TILE_SIZE + TILE_SIZE//2)
        self.type = ttype
        self.level = 1
        self.range = TOWER_RANGE[ttype]
        self.damage = TOWER_DAMAGE[ttype]
        self.fire_rate = TOWER_FIRE_RATE[ttype]
        self.fire_timer = 0.0
        self.target = None
        self.bullets = []
        self.color = TOWER_COLORS[ttype]
        self.splash = 0
        self.slow_duration = 0
        if ttype == 1:
            self.splash = 45
        elif ttype == 2:
            self.slow_duration = 2.0

    def update(self, enemies):
        self.fire_timer -= 1/60
        if self.fire_timer <= 0:
            self.target = None
            closest = None
            min_dist = self.range
            for e in enemies:
                dist = math.hypot(e.pos[0]-self.pos[0], e.pos[1]-self.pos[1])
                if dist < min_dist:
                    min_dist = dist
                    closest = e
            if closest:
                self.target = closest
                self.fire_timer = self.fire_rate
                self.bullets.append(Bullet(self.pos, self.target, self.damage, self.splash, self.slow_duration>0))
        new_bullets = []
        for b in self.bullets:
            hit = b.update()
            if hit:
                splashed = []
                if b.splash > 0:
                    for e in enemies:
                        if e is b.target: continue
                        d = math.hypot(e.pos[0]-b.target.pos[0], e.pos[1]-b.target.pos[1])
                        if d <= b.splash:
                            splashed.append(e)
                if b.target.hit(b.damage):
                    enemies.remove(b.target)
                for e in splashed:
                    if e.hit(int(b.damage*0.5)):
                        if e in enemies:
                            enemies.remove(e)
                if b.slow:
                    b.target.slow(self.slow_duration)
            else:
                new_bullets.append(b)
        self.bullets = new_bullets

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.grid[0]*TILE_SIZE+4, self.grid[1]*TILE_SIZE+4, TILE_SIZE-8, TILE_SIZE-8))
        level_text = FONT_SMALL.render(str(self.level), True, WHITE)
        surface.blit(level_text, (self.pos[0]-5, self.pos[1]-8))
        for b in self.bullets:
            b.draw(surface)

    def upgrade(self):
        if self.level >= MAX_LEVEL:
            return False
        self.level += 1
        self.damage = int(self.damage * 1.6)
        self.range = int(self.range * 1.2)
        return True

    def get_upgrade_cost(self):
        return int(TOWER_COST[self.type] * UPGRADE_COST_MULT)

class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.base_health = BASE_HEALTH
        self.coins = INITIAL_COINS
        self.current_wave = 0
        self.wave_enemies = []
        self.enemies = []
        self.towers = []
        self.selected_tower_type = 0
        self.wave_timer = 0.0
        self.wave_spawn_index = 0
        self.wave_spawn_timer = 0.0
        self.game_over = False
        self.victory = False
        self.prepare_mode = True
        self.prepare_timer = PREPARE_TIME
        self.spawn_wave_enemies()

    def spawn_wave_enemies(self):
        self.wave_enemies.clear()
        if self.current_wave >= len(WAVES):
            return
        wave_data = WAVES[self.current_wave]
        for etype, count in wave_data:
            for i in range(count):
                self.wave_enemies.append(etype)
        self.wave_spawn_index = 0
        self.wave_spawn_timer = 0.0

    def can_build_at(self, gridx, gridy):
        if gridx < 0 or gridx >= GRID_WIDTH or gridy < 0 or gridy >= GRID_HEIGHT:
            return False
        if (gridx, gridy) in PATH_GRIDS:
            return False
        for t in self.towers:
            if t.grid == (gridx, gridy):
                return False
        if gridx == 0 and gridy == 7:
            return False
        if gridx == 19 and gridy == 7:
            return False
        return True

    def build_tower(self, gridx, gridy):
        if not self.can_build_at(gridx, gridy):
            return False
        cost = TOWER_COST[self.selected_tower_type]
        if self.coins < cost:
            return False
        self.towers.append(Tower(gridx, gridy, self.selected_tower_type))
        self.coins -= cost
        return True

    def upgrade_tower(self, gridx, gridy):
        for t in self.towers:
            if t.grid == (gridx, gridy):
                cost = t.get_upgrade_cost()
                if self.coins >= cost and t.level < MAX_LEVEL:
                    t.upgrade()
                    self.coins -= cost
                    return True
        return False

    def update(self):
        if self.game_over:
            return
        if self.prepare_mode:
            self.prepare_timer -= 1/60
            if self.prepare_timer <= 0:
                self.prepare_mode = False
                self.prepare_timer = PREPARE_TIME
            return
        if self.wave_spawn_index < len(self.wave_enemies):
            self.wave_spawn_timer -= 1/60
            if self.wave_spawn_timer <= 0:
                etype = self.wave_enemies[self.wave_spawn_index]
                self.enemies.append(Enemy(etype))
                self.wave_spawn_index += 1
                self.wave_spawn_timer = 0.8
        for t in self.towers:
            t.update(self.enemies)
        to_remove = []
        for e in self.enemies:
            if not e.update():
                to_remove.append(e)
        for e in to_remove:
            self.enemies.remove(e)
            self.base_health -= 1
            if self.base_health <= 0:
                self.game_over = True
        if len(self.wave_enemies) == self.wave_spawn_index and len(self.enemies) == 0:
            self.current_wave += 1
            if self.current_wave >= len(WAVES):
                self.victory = True
                self.game_over = True
            else:
                self.prepare_mode = True
                self.spawn_wave_enemies()

    def draw(self):
        SCREEN.fill(BLACK)
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if (x, y) == (0, 7):
                    pygame.draw.rect(SCREEN, ENTRY_COLOR, rect)
                elif (x, y) == (19, 7):
                    pygame.draw.rect(SCREEN, BASE_COLOR, rect)
                elif (x, y) in PATH_GRIDS:
                    pygame.draw.rect(SCREEN, PATH_COLOR, rect)
                else:
                    pygame.draw.rect(SCREEN, GRAY, rect, 1)
        for i in range(len(PATH_POINTS)-1):
            pygame.draw.line(SCREEN, (200,180,120), PATH_POINTS[i], PATH_POINTS[i+1], 3)
        for e in self.enemies:
            e.draw(SCREEN)
        for t in self.towers:
            t.draw(SCREEN)
        hud_rect = pygame.Rect(MAP_WIDTH, 0, SCREEN_WIDTH-MAP_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(SCREEN, HUD_BG, hud_rect)
        y_offset = 20
        health_text = FONT_MEDIUM.render(f"Base: {self.base_health}", True, HUD_TEXT)
        SCREEN.blit(health_text, (MAP_WIDTH+20, y_offset))
        y_offset += 40
        coins_text = FONT_MEDIUM.render(f"Coins: {self.coins}", True, HUD_TEXT)
        SCREEN.blit(coins_text, (MAP_WIDTH+20, y_offset))
        y_offset += 40
        wave_text = FONT_MEDIUM.render(f"Wave: {self.current_wave+1}/{len(WAVES)}", True, HUD_TEXT)
        SCREEN.blit(wave_text, (MAP_WIDTH+20, y_offset))
        y_offset += 40
        enemies_text = FONT_MEDIUM.render(f"Enemies: {len(self.enemies)}", True, HUD_TEXT)
        SCREEN.blit(enemies_text, (MAP_WIDTH+20, y_offset))
        y_offset += 40
        selected_text = FONT_MEDIUM.render(f"Selected:", True, HUD_TEXT)
        SCREEN.blit(selected_text, (MAP_WIDTH+20, y_offset))
        y_offset += 30
        tower_name = TOWER_NAMES[self.selected_tower_type]
        cost = TOWER_COST[self.selected_tower_type]
        tower_text = FONT_SMALL.render(f"{tower_name} (${cost})", True, TOWER_COLORS[self.selected_tower_type])
        SCREEN.blit(tower_text, (MAP_WIDTH+20, y_offset))
        y_offset += 60
        for i in range(TOWER_TYPES):
            rect = pygame.Rect(MAP_WIDTH+20, y_offset + i*60, 120, 50)
            pygame.draw.rect(SCREEN, TOWER_COLORS[i], rect, 2)
            name_text = FONT_SMALL.render(TOWER_NAMES[i], True, TOWER_COLORS[i])
            SCREEN.blit(name_text, (MAP_WIDTH+30, y_offset + i*60 + 5))
            cost_text = FONT_SMALL.render(f"Cost: ${TOWER_COST[i]}", True, HUD_TEXT)
            SCREEN.blit(cost_text, (MAP_WIDTH+30, y_offset + i*60 + 25))
        y_offset += TOWER_TYPES*60 + 20
        keys_text = FONT_SMALL.render("1/2/3: Select Tower", True, HUD_TEXT)
        SCREEN.blit(keys_text, (MAP_WIDTH+20, y_offset))
        y_offset += 25
        build_text = FONT_SMALL.render("Click: Build Tower", True, HUD_TEXT)
        SCREEN.blit(build_text, (MAP_WIDTH+20, y_offset))
        y_offset += 25
        upgrade_text = FONT_SMALL.render("Right Click: Upgrade", True, HUD_TEXT)
        SCREEN.blit(upgrade_text, (MAP_WIDTH+20, y_offset))
        y_offset += 25
        restart_text = FONT_SMALL.render("R: Restart", True, HUD_TEXT)
        SCREEN.blit(restart_text, (MAP_WIDTH+20, y_offset))
        y_offset += 25
        esc_text = FONT_SMALL.render("ESC: Quit", True, HUD_TEXT)
        SCREEN.blit(esc_text, (MAP_WIDTH+20, y_offset))
        mx, my = pygame.mouse.get_pos()
        if mx < MAP_WIDTH:
            gx = mx // TILE_SIZE
            gy = my // TILE_SIZE
            if self.can_build_at(gx, gy):
                rect = pygame.Rect(gx*TILE_SIZE, gy*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(SCREEN, (255,255,255), rect, 2)
                tower_pos = (gx*TILE_SIZE+TILE_SIZE//2, gy*TILE_SIZE+TILE_SIZE//2)
                pygame.draw.circle(SCREEN, (255,255,255,100), tower_pos, TOWER_RANGE[self.selected_tower_type], 1)
        if self.prepare_mode and self.prepare_timer > 0:
            prep_text = FONT_LARGE.render(f"Prepare: {int(self.prepare_timer)+1}", True, (255,255,100))
            SCREEN.blit(prep_text, (SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2-30))
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,200))
            SCREEN.blit(overlay, (0,0))
            if self.victory:
                end_text = FONT_LARGE.render("You Win!", True, (100,255,100))
            else:
                end_text = FONT_LARGE.render("Game Over", True, (255,100,100))
            SCREEN.blit(end_text, (SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2-50))
            wave_text = FONT_MEDIUM.render(f"Wave: {self.current_wave+1}", True, WHITE)
            SCREEN.blit(wave_text, (SCREEN_WIDTH//2-70, SCREEN_HEIGHT//2+10))
            restart_text = FONT_MEDIUM.render("Press R to Restart", True, WHITE)
            SCREEN.blit(restart_text, (SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2+60))

    def run(self):
        running = True
        while running:
            CLOCK.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        idx = event.key - pygame.K_1
                        if idx < TOWER_TYPES:
                            self.selected_tower_type = idx
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_over:
                        continue
                    mx, my = pygame.mouse.get_pos()
                    if mx < MAP_WIDTH:
                        gx = mx // TILE_SIZE
                        gy = my // TILE_SIZE
                        if event.button == 1:
                            self.build_tower(gx, gy)
                        elif event.button == 3:
                            self.upgrade_tower(gx, gy)
            self.update()
            self.draw()
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()