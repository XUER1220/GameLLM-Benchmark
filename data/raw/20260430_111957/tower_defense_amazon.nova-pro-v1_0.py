import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 32
MAP_WIDTH = 20
MAP_HEIGHT = 15
BASE_HP = 20
STARTING_GOLD = 180
WAVE_INTERVAL = 3000
FONT = pygame.font.SysFont(None, 24)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

ARROW_TOWER_COST = 50
CANNON_TOWER_COST = 80
SLOW_TOWER_COST = 70

ARROW_TOWER_RANGE = 120
CANNON_TOWER_RANGE = 105
SLOW_TOWER_RANGE = 110

ARROW_TOWER_DAMAGE = 8
CANNON_TOWER_DAMAGE = 14
SLOW_TOWER_DAMAGE = 4

ARROW_TOWER_SPEED = 0.8
CANNON_TOWER_SPEED = 1.2
SLOW_TOWER_SPEED = 1.0

CANNON_TOWER_SPLASH = 45
SLOW_TOWER_DURATION = 2000

UPGRADE_COST_PERCENTAGE = 0.7
MAX_UPGRADES = 2

ENEMY_SPAWN_POINT = (0, 7)
BASE_POSITION = (19, 7)
PATH = [
    (0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7),
    (9, 7), (10, 7), (11, 7), (12, 7), (13, 7), (14, 7), (15, 7), (16, 7),
    (17, 7), (18, 7), (19, 7)
]

ENEMY_TYPES = {
    'normal': {'hp': 20,'speed': 2,'reward': 10},
    'fast': {'hp': 10,'speed': 4,'reward': 5},
    'tank': {'hp': 50,'speed': 1,'reward': 20}
}

WAVES = [
    [{'type': 'normal', 'count': 5}],
    [{'type': 'normal', 'count': 10}],
    [{'type': 'normal', 'count': 5}, {'type': 'fast', 'count': 5}],
    [{'type': 'normal', 'count': 5}, {'type': 'tank', 'count': 2}],
    [{'type': 'fast', 'count': 10}, {'type': 'tank', 'count': 3}]
]

class Tower:
    def __init__(self, x, y, tower_type):
        self.x = x
        self.y = y
        self.tower_type = tower_type
        self.level = 1
        self.range = {
            'arrow': ARROW_TOWER_RANGE,
            'cannon': CANNON_TOWER_RANGE,
           'slow': SLOW_TOWER_RANGE
        }[tower_type]
        self.damage = {
            'arrow': ARROW_TOWER_DAMAGE,
            'cannon': CANNON_TOWER_DAMAGE,
           'slow': SLOW_TOWER_DAMAGE
        }[tower_type]
        self.speed = {
            'arrow': ARROW_TOWER_SPEED,
            'cannon': CANNON_TOWER_SPEED,
           'slow': SLOW_TOWER_SPEED
        }[tower_type]
        self.splash = {
            'cannon': CANNON_TOWER_SPLASH,
           'slow': 0
        }[tower_type]
        self.last_shot = pygame.time.get_ticks()
        self.color = {
            'arrow': GREEN,
            'cannon': RED,
           'slow': BLUE
        }[tower_type]

    def upgrade(self):
        if self.level < MAX_UPGRADES:
            self.level += 1
            self.range *= 1.1
            self.damage *= 1.2
            self.speed *= 0.9

    def can_attack(self):
        return pygame.time.get_ticks() - self.last_shot >= self.speed * 1000

    def attack(self, enemies):
        if self.can_attack():
            target = min(enemies, key=lambda e: abs(e.x - self.x) + abs(e.y - self.y), default=None)
            if target and abs(target.x - self.x) + abs(target.y - self.y) <= self.range:
                target.hp -= self.damage
                self.last_shot = pygame.time.get_ticks()
                if self.tower_type =='slow':
                    target.slowed_until = pygame.time.get_ticks() + SLOW_TOWER_DURATION

class Enemy:
    def __init__(self, enemy_type):
        self.x, self.y = ENEMY_SPAWN_POINT
        self.path_index = 0
        self.hp = ENEMY_TYPES[enemy_type]['hp']
        self.speed = ENEMY_TYPES[enemy_type]['speed']
        self.reward = ENEMY_TYPES[enemy_type]['reward']
        self.slowed_until = 0
        self.color = {
            'normal': RED,
            'fast': YELLOW,
            'tank': PURPLE
        }[enemy_type]

    def move(self):
        if self.path_index < len(PATH) - 1:
            target_x, target_y = PATH[self.path_index + 1]
            dx = (target_x - self.x) * self.speed
            dy = (target_y - self.y) * self.speed
            self.x += dx
            self.y += dy
            if abs(self.x - target_x) < abs(dx) and abs(self.y - target_y) < abs(dy):
                self.x = target_x
                self.y = target_y
                self.path_index += 1

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Defense Hard")
        self.clock = pygame.time.Clock()
        self.base_hp = BASE_HP
        self.gold = STARTING_GOLD
        self.wave = 0
        self.enemies = []
        self.towers = []
        self.selected_tower = None
        self.game_over = False
        self.win = False
        self.last_enemy_spawn = pygame.time.get_ticks()
        self.next_wave_time = pygame.time.get_ticks() + WAVE_INTERVAL
        self.font = FONT

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

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
                    self.run()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x < 640:
                    grid_x, grid_y = x // TILE_SIZE, y // TILE_SIZE
                    if (grid_x, grid_y) not in PATH and (grid_x, grid_y)!= BASE_POSITION:
                        if event.button == 1:  # Left click to build
                            if self.selected_tower:
                                cost = {
                                    'arrow': ARROW_TOWER_COST,
                                    'cannon': CANNON_TOWER_COST,
                                   'slow': SLOW_TOWER_COST
                                }[self.selected_tower]
                                if self.gold >= cost:
                                    self.towers.append(Tower(grid_x, grid_y, self.selected_tower))
                                    self.gold -= cost
                        elif event.button == 3:  # Right click to upgrade
                            for tower in self.towers:
                                if (tower.x, tower.y) == (grid_x, grid_y):
                                    upgrade_cost = int(cost * UPGRADE_COST_PERCENTAGE)
                                    if self.gold >= upgrade_cost and tower.level < MAX_UPGRADES:
                                        tower.upgrade()
                                        self.gold -= upgrade_cost
                elif x >= 640 and y < 480:
                    self.selected_tower = {
                        1: 'arrow',
                        2: 'cannon',
                        3:'slow'
                    }.get(y // 160, None)

    def update(self):
        if not self.game_over and not self.win:
            current_time = pygame.time.get_ticks()
            if current_time >= self.next_wave_time and not self.enemies:
                self.start_new_wave()
            if current_time - self.last_enemy_spawn > 1000 / (2 + self.wave):
                self.spawn_enemy()
            self.move_enemies()
            self.attack_enemies()
            self.remove_dead_enemies()

    def draw(self):
        self.screen.fill(GRAY)
        self.draw_map()
        self.draw_towers()
        self.draw_enemies()
        self.draw_hud()
        if self.game_over:
            self.draw_game_over()
        elif self.win:
            self.draw_win()
        pygame.display.flip()

    def draw_map(self):
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if (x, y) in PATH:
                    pygame.draw.rect(self.screen, WHITE, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                elif (x, y) == BASE_POSITION:
                    pygame.draw.rect(self.screen, CYAN, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                else:
                    pygame.draw.rect(self.screen, BLACK, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    def draw_towers(self):
        for tower in self.towers:
            pygame.draw.circle(self.screen, tower.color, (tower.x * TILE_SIZE + TILE_SIZE // 2, tower.y * TILE_SIZE + TILE_SIZE // 2), TILE_SIZE // 2)
            pygame.draw.circle(self.screen, WHITE, (tower.x * TILE_SIZE + TILE_SIZE // 2, tower.y * TILE_SIZE + TILE_SIZE // 2), tower.range, 1)
            level_text = self.font.render(str(tower.level), True, WHITE)
            self.screen.blit(level_text, (tower.x * TILE_SIZE + TILE_SIZE // 2 - 5, tower.y * TILE_SIZE + TILE_SIZE // 2 - 10))

    def draw_enemies(self):
        for enemy in self.enemies:
            pygame.draw.circle(self.screen, enemy.color, (enemy.x * TILE_SIZE + TILE_SIZE // 2, enemy.y * TILE_SIZE + TILE_SIZE // 2), TILE_SIZE // 2)
            hp_text = self.font.render(str(enemy.hp), True, WHITE)
            self.screen.blit(hp_text, (enemy.x * TILE_SIZE + TILE_SIZE // 2 - 5, enemy.y * TILE_SIZE + TILE_SIZE // 2 - 10))

    def draw_hud(self):
        pygame.draw.rect(self.screen, WHITE, (640, 0, 160, 480))
        base_hp_text = self.font.render(f"Base HP: {self.base_hp}", True, BLACK)
        gold_text = self.font.render(f"Gold: {self.gold}", True, BLACK)
        wave_text = self.font.render(f"Wave: {self.wave}", True, BLACK)
        enemies_left_text = self.font.render(f"Enemies Left: {len(self.enemies)}", True, BLACK)
        self.screen.blit(base_hp_text, (650, 10))
        self.screen.blit(gold_text, (650, 30))
        self.screen.blit(wave_text, (650, 50))
        self.screen.blit(enemies_left_text, (650, 70))
        if self.selected_tower:
            tower_text = self.font.render(f"Selected: {self.selected_tower.capitalize()} Tower", True, BLACK)
            self.screen.blit(tower_text, (650, 90))

    def draw_game_over(self):
        game_over_text = self.font.render("Game Over", True, RED)
        wave_text = self.font.render(f"Wave Reached: {self.wave}", True, RED)
        restart_text = self.font.render("Press R to Restart", True, RED)
        self.screen.blit(game_over_text, (650, 150))
        self.screen.blit(wave_text, (650, 170))
        self.screen.blit(restart_text, (650, 190))

    def draw_win(self):
        win_text = self.font.render("You Win", True, GREEN)
        wave_text = self.font.render(f"Waves Completed: {self.wave}", True, GREEN)
        restart_text = self.font.render("Press R to Restart", True, GREEN)
        self.screen.blit(win_text, (650, 150))
        self.screen.blit(wave_text, (650, 170))
        self.screen.blit(restart_text, (650, 190))

    def start_new_wave(self):
        self.wave += 1
        if self.wave > len(WAVES):
            self.win = True
            return
        self.next_wave_time = pygame.time.get_ticks() + WAVE_INTERVAL

    def spawn_enemy(self):
        if self.wave < len(WAVES):
            wave = WAVES[self.wave]
            for enemy_info in wave:
                for _ in range(enemy_info['count']):
                    self.enemies.append(Enemy(enemy_info['type']))
                    self.last_enemy_spawn = pygame.time.get_ticks()

    def move_enemies(self):
        for enemy in self.enemies:
            if pygame.time.get_ticks() > enemy.slowed_until:
                enemy.move()
            if (enemy.x, enemy.y) == BASE_POSITION:
                self.base_hp -= 1
                self.enemies.remove(enemy)
                if self.base_hp <= 0:
                    self.game_over = True

    def attack_enemies(self):
        for tower in self.towers:
            tower.attack(self.enemies)

    def remove_dead_enemies(self):
        self.enemies = [enemy for enemy in self.enemies if enemy.hp > 0]
        for enemy in self.enemies:
            if enemy.hp <= 0:
                self.gold += enemy.reward
                self.enemies.remove(enemy)

if __name__ == "__main__":
    game = Game()
    game.run()