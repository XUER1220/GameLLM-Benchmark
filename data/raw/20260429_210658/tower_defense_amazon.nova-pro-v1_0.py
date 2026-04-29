import pygame
import sys
import random
import math

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BASE_HP = 20
INITIAL_GOLD = 180
TILE_SIZE = 32
MAP_WIDTH = 20
MAP_HEIGHT = 15
HUD_WIDTH = 160
GRID_WIDTH = MAP_WIDTH * TILE_SIZE
GRID_HEIGHT = MAP_HEIGHT * TILE_SIZE
PATH = [(0, 7), (5, 7), (5, 3), (10, 3), (10, 8), (14, 8), (14, 5), (19, 5)]
ENEMY_WAVES = [
    {'enemies': [{'type': 'normal', 'count': 5}]},
    {'enemies': [{'type': 'normal', 'count': 7}, {'type': 'fast', 'count': 2}]},
    {'enemies': [{'type': 'normal', 'count': 5}, {'type': 'tank', 'count': 2}]},
    {'enemies': [{'type': 'fast', 'count': 10}]},
    {'enemies': [{'type': 'tank', 'count': 5}, {'type': 'fast', 'count': 5}]}
]
TOWER_TYPES = {
    'arrow': {'cost': 50, 'damage': 8, 'range': 120, 'rate': 0.8, 'upgrade_cost': 35, 'upgrade_damage': 2, 'upgrade_range': 10},
    'cannon': {'cost': 80, 'damage': 14, 'range': 105, 'rate': 1.2,'splash': 45, 'upgrade_cost': 56, 'upgrade_damage': 3, 'upgrade_range': 10},
   'slow': {'cost': 70, 'damage': 4, 'range': 110, 'rate': 1.0,'slow': 2, 'upgrade_cost': 49, 'upgrade_damage': 1, 'upgrade_range': 10}
}

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Defense Hard")
        self.clock = pygame.time.Clock()
        self.base_hp = BASE_HP
        self.gold = INITIAL_GOLD
        self.current_wave = 0
        self.enemies = []
        self.towers = []
        self.projectiles = []
        self.selected_tower_type = 'arrow'
        self.wave_start_time = 0
        self.game_over = False
        self.win = False
        self.font = pygame.font.SysFont(None, 24)
        self.load_images()

    def load_images(self):
        self.ground_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.ground_img.fill((102, 51, 0))
        self.path_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.path_img.fill((102, 102, 102))
        self.base_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.base_img.fill((255, 0, 0))
        self.arrow_tower_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.arrow_tower_img.fill((0, 255, 0))
        self.cannon_tower_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.cannon_tower_img.fill((0, 0, 255))
        self.slow_tower_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.slow_tower_img.fill((255, 255, 0))
        self.normal_enemy_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.normal_enemy_img.fill((0, 204, 0))
        self.fast_enemy_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.fast_enemy_img.fill((0, 102, 204))
        self.tank_enemy_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.tank_enemy_img.fill((51, 0, 102))
        self.projectile_img = pygame.Surface((5, 5))
        self.projectile_img.fill((255, 255, 255))

    def draw_grid(self):
        for x in range(0, GRID_WIDTH, TILE_SIZE):
            for y in range(0, GRID_HEIGHT, TILE_SIZE):
                if (x // TILE_SIZE, y // TILE_SIZE) in PATH:
                    self.screen.blit(self.path_img, (x, y))
                else:
                    self.screen.blit(self.ground_img, (x, y))

    def draw_base(self):
        self.screen.blit(self.base_img, (GRID_WIDTH, GRID_HEIGHT // 2 * TILE_SIZE))

    def draw_towers(self):
        for tower in self.towers:
            if tower['type'] == 'arrow':
                self.screen.blit(self.arrow_tower_img, (tower['x'], tower['y']))
            elif tower['type'] == 'cannon':
                self.screen.blit(self.cannon_tower_img, (tower['x'], tower['y']))
            elif tower['type'] =='slow':
                self.screen.blit(self.slow_tower_img, (tower['x'], tower['y']))

    def draw_enemies(self):
        for enemy in self.enemies:
            if enemy['type'] == 'normal':
                self.screen.blit(self.normal_enemy_img, (enemy['x'], enemy['y']))
            elif enemy['type'] == 'fast':
                self.screen.blit(self.fast_enemy_img, (enemy['x'], enemy['y']))
            elif enemy['type'] == 'tank':
                self.screen.blit(self.tank_enemy_img, (enemy['x'], enemy['y']))

    def draw_projectiles(self):
        for projectile in self.projectiles:
            self.screen.blit(self.projectile_img, (projectile['x'], projectile['y']))

    def draw_hud(self):
        pygame.draw.rect(self.screen, (0, 0, 0), (GRID_WIDTH, 0, HUD_WIDTH, SCREEN_HEIGHT))
        base_hp_text = self.font.render(f"Base HP: {self.base_hp}", True, (255, 255, 255))
        gold_text = self.font.render(f"Gold: {self.gold}", True, (255, 255, 255))
        wave_text = self.font.render(f"Wave: {self.current_wave}", True, (255, 255, 255))
        enemies_left_text = self.font.render(f"Enemies Left: {sum(e['count'] for es in ENEMY_WAVES[self.current_wave]['enemies'] for e in es.values())}", True, (255, 255, 255))
        selected_tower_text = self.font.render(f"Selected Tower: {self.selected_tower_type.capitalize()}", True, (255, 255, 255))
        self.screen.blit(base_hp_text, (GRID_WIDTH + 10, 10))
        self.screen.blit(gold_text, (GRID_WIDTH + 10, 40))
        self.screen.blit(wave_text, (GRID_WIDTH + 10, 70))
        self.screen.blit(enemies_left_text, (GRID_WIDTH + 10, 100))
        self.screen.blit(selected_tower_text, (GRID_WIDTH + 10, 130))

    def draw_game_over(self):
        if self.win:
            game_over_text = self.font.render("You Win", True, (0, 255, 0))
        else:
            game_over_text = self.font.render("Game Over", True, (255, 0, 0))
        wave_text = self.font.render(f"Final Wave: {self.current_wave}", True, (255, 255, 255))
        restart_text = self.font.render("Press R to Restart", True, (255, 255, 255))
        self.screen.blit(game_over_text, (GRID_WIDTH // 2 - 50, GRID_HEIGHT // 2 - 30))
        self.screen.blit(wave_text, (GRID_WIDTH // 2 - 50, GRID_HEIGHT // 2))
        self.screen.blit(restart_text, (GRID_WIDTH // 2 - 100, GRID_HEIGHT // 2 + 30))

    def check_collision(self, rect1, rect2):
        return rect1.colliderect(rect2)

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def spawn_enemies(self):
        if self.current_wave < len(ENEMY_WAVES):
            wave = ENEMY_WAVES[self.current_wave]
            for enemy_type in wave['enemies']:
                for _ in range(enemy_type['count']):
                    if enemy_type['type'] == 'normal':
                        self.enemies.append({'type': 'normal', 'x': 0, 'y': PATH[0][1] * TILE_SIZE, 'hp': 10,'speed': 2,'reward': 10})
                    elif enemy_type['type'] == 'fast':
                        self.enemies.append({'type': 'fast', 'x': 0, 'y': PATH[0][1] * TILE_SIZE, 'hp': 5, 'speed': 4,'reward': 5})
                    elif enemy_type['type'] == 'tank':
                        self.enemies.append({'type': 'tank', 'x': 0, 'y': PATH[0][1] * TILE_SIZE, 'hp': 20,'speed': 1,'reward': 15})

    def move_enemies(self):
        for enemy in self.enemies:
            if PATH:
                target_x, target_y = PATH[0]
                if enemy['x'] == target_x * TILE_SIZE and enemy['y'] == target_y * TILE_SIZE:
                    PATH.pop(0)
                    if PATH:
                        target_x, target_y = PATH[0]
                else:
                    if enemy['x'] < target_x * TILE_SIZE:
                        enemy['x'] += enemy['speed']
                    elif enemy['x'] > target_x * TILE_SIZE:
                        enemy['x'] -= enemy['speed']
                    if enemy['y'] < target_y * TILE_SIZE:
                        enemy['y'] += enemy['speed']
                    elif enemy['y'] > target_y * TILE_SIZE:
                        enemy['y'] -= enemy['speed']
            else:
                self.base_hp -= 1
                self.enemies.remove(enemy)

    def check_enemy_at_base(self):
        for enemy in self.enemies:
            if enemy['x'] >= GRID_WIDTH and enemy['y'] == GRID_HEIGHT // 2 * TILE_SIZE:
                self.base_hp -= 1
                self.enemies.remove(enemy)

    def handle_tower_attack(self):
        for tower in self.towers:
            closest_enemy = None
            closest_distance = float('inf')
            for enemy in self.enemies:
                distance = self.distance(tower['x'] + TILE_SIZE // 2, tower['y'] + TILE_SIZE // 2, enemy['x'] + TILE_SIZE // 2, enemy['y'] + TILE_SIZE // 2)
                if distance < closest_distance and distance <= TOWER_TYPES[tower['type']]['range']:
                    closest_enemy = enemy
                    closest_distance = distance
            if closest_enemy:
                if pygame.time.get_ticks() - tower['last_shot'] > TOWER_TYPES[tower['type']]['rate'] * 1000:
                    self.projectiles.append({'x': tower['x'] + TILE_SIZE // 2, 'y': tower['y'] + TILE_SIZE // 2, 'target': closest_enemy, 'type': tower['type']})
                    tower['last_shot'] = pygame.time.get_ticks()
                    if tower['type'] == 'cannon':
                        for e in self.enemies:
                            if self.distance(tower['x'] + TILE_SIZE // 2, tower['y'] + TILE_SIZE // 2, e['x'] + TILE_SIZE // 2, e['y'] + TILE_SIZE // 2) <= TOWER_TYPES[tower['type']]['range'] + TOWER_TYPES[tower['type']]['splash']:
                                e['hp'] -= TOWER_TYPES[tower['type']]['damage']

    def move_projectiles(self):
        for projectile in self.projectiles:
            target = projectile['target']
            if target in self.enemies:
                dx = target['x'] + TILE_SIZE // 2 - projectile['x']
                dy = target['y'] + TILE_SIZE // 2 - projectile['y']
                distance = math.sqrt(dx ** 2 + dy ** 2)
                if distance!= 0:
                    projectile['x'] += dx / distance * 5
                    projectile['y'] += dy / distance * 5
                    if self.check_collision(pygame.Rect(projectile['x'], projectile['y'], 5, 5), pygame.Rect(target['x'], target['y'], TILE_SIZE, TILE_SIZE)):
                        if projectile['type'] == 'arrow':
                            target['hp'] -= TOWER_TYPES['arrow']['damage']
                        elif projectile['type'] =='slow':
                            target['hp'] -= TOWER_TYPES['slow']['damage']
                            target['speed'] *= 0.5
                            pygame.time.set_timer(pygame.USEREVENT + 1, 2000)
                        self.projectiles.remove(projectile)
            else:
                self.projectiles.remove(projectile)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    self.__init__()
                elif event.key == pygame.K_1:
                    self.selected_tower_type = 'arrow'
                elif event.key == pygame.K_2:
                    self.selected_tower_type = 'cannon'
                elif event.key == pygame.K_3:
                    self.selected_tower_type = 'slow'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x < GRID_WIDTH and y < GRID_HEIGHT:
                    grid_x, grid_y = x // TILE_SIZE, y // TILE_SIZE
                    if (grid_x, grid_y) not in PATH and not any(tower for tower in self.towers if tower['x'] == grid_x * TILE_SIZE and tower['