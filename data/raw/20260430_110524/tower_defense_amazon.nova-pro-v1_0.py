import pygame
import sys
import random
import math

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
MAP_WIDTH, MAP_HEIGHT = 20, 15
TILE_SIZE = 32
MAP_AREA_WIDTH, MAP_AREA_HEIGHT = MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE
HUD_WIDTH = SCREEN_WIDTH - MAP_AREA_WIDTH
FPS = 60
BASE_HP = 20
INITIAL_GOLD = 180
WAVE_DELAY = 3000

BLACK, WHITE, GRAY, RED, GREEN, BLUE, YELLOW = (0, 0, 0), (255, 255, 255), (128, 128, 128), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)
TOWER_COLORS = {1: GREEN, 2: RED, 3: BLUE}
ENEMY_COLORS = {1: GRAY, 2: YELLOW, 3: RED}
PATH = [(0, 7), (5, 7), (5, 0), (10, 0), (10, 5), (15, 5), (15, 10), (12, 10), (12, 14)]

ARROW_TOWER_COST, CANNON_TOWER_COST, SLOW_TOWER_COST = 50, 80, 70
ARROW_TOWER_DAMAGE, CANNON_TOWER_DAMAGE, SLOW_TOWER_DAMAGE = 8, 14, 4
ARROW_TOWER_RANGE, CANNON_TOWER_RANGE, SLOW_TOWER_RANGE = 120, 105, 110
ARROW_TOWER_SPEED, CANNON_TOWER_SPEED, SLOW_TOWER_SPEED = 0.8, 1.2, 1.0
CANNON_SPLASH_RADIUS = 45
SLOW_DURATION = 2000
UPGRADE_COST_FACTOR = 0.7
TOWER_MAX_LEVEL = 2

ENEMY_TYPES = {
    1: {"hp": 10, "speed": 2, "reward": 10},
    2: {"hp": 5, "speed": 3, "reward": 5},
    3: {"hp": 20, "speed": 1.5, "reward": 15}
}

WAVES = [
    [{"type": 1, "count": 5}],
    [{"type": 1, "count": 10}],
    [{"type": 1, "count": 5}, {"type": 2, "count": 5}],
    [{"type": 1, "count": 3}, {"type": 2, "count": 7}, {"type": 3, "count": 2}],
    [{"type": 1, "count": 5}, {"type": 2, "count": 5}, {"type": 3, "count": 5}]
]

clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense Hard")

font = pygame.font.SysFont(None, 24)
large_font = pygame.font.SysFont(None, 48)

class Tower:
    def __init__(self, x, y, tower_type):
        self.x, self.y = x, y
        self.type = tower_type
        self.level = 1
        self.range = [ARROW_TOWER_RANGE, CANNON_TOWER_RANGE, SLOW_TOWER_RANGE][tower_type - 1]
        self.damage = [ARROW_TOWER_DAMAGE, CANNON_TOWER_DAMAGE, SLOW_TOWER_DAMAGE][tower_type - 1]
        self.speed = [ARROW_TOWER_SPEED, CANNON_TOWER_SPEED, SLOW_TOWER_SPEED][tower_type - 1]
        self.last_shot = pygame.time.get_ticks()
        self.target = None

    def upgrade(self):
        if self.level < TOWER_MAX_LEVEL:
            self.level += 1
            self.range += 10
            self.damage += 2
            self.speed -= 0.1

    def attack(self, enemies):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.speed * 1000:
            closest_enemy = min(enemies, key=lambda e: math.hypot(e.x - self.x * TILE_SIZE, e.y - self.y * TILE_SIZE), default=None)
            if closest_enemy and math.hypot(closest_enemy.x - self.x * TILE_SIZE, closest_enemy.y - self.y * TILE_SIZE) <= self.range:
                self.target = closest_enemy
                self.last_shot = now
                if self.type == 2:
                    for enemy in enemies:
                        if math.hypot(enemy.x - self.x * TILE_SIZE, enemy.y - self.y * TILE_SIZE) <= self.range + CANNON_SPLASH_RADIUS:
                            enemy.hp -= self.damage
                elif self.type == 3:
                    self.target.speed *= 0.5
                    pygame.time.set_timer(pygame.USEREVENT + self.target.id, SLOW_DURATION)
                else:
                    self.target.hp -= self.damage

class Enemy:
    next_id = 0

    def __init__(self, x, y, enemy_type):
        self.x, self.y = x, y
        self.type = enemy_type
        self.hp = ENEMY_TYPES[enemy_type]["hp"]
        self.speed = ENEMY_TYPES[enemy_type]["speed"]
        self.reward = ENEMY_TYPES[enemy_type]["reward"]
        self.path_index = 0
        self.id = Enemy.next_id
        Enemy.next_id += 1

    def move(self):
        if self.path_index < len(PATH) - 1:
            target_x, target_y = PATH[self.path_index + 1]
            tx, ty = target_x * TILE_SIZE, target_y * TILE_SIZE
            dx, dy = tx - self.x, ty - self.y
            distance = math.hypot(dx, dy)
            if distance <= self.speed:
                self.x, self.y = tx, ty
                self.path_index += 1
            else:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed

def draw_grid():
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, WHITE if (x, y) in PATH else GRAY, rect, 1)

def draw_path():
    for x, y in PATH:
        pygame.draw.rect(screen, YELLOW, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

def draw_hud(gold, base_hp, wave, enemies_left, selected_tower):
    pygame.draw.rect(screen, BLACK, (MAP_AREA_WIDTH, 0, HUD_WIDTH, SCREEN_HEIGHT))
    pygame.draw.rect(screen, WHITE, (MAP_AREA_WIDTH, 0, HUD_WIDTH, SCREEN_HEIGHT), 2)
    
    gold_text = font.render(f"Gold: {gold}", True, WHITE)
    base_hp_text = font.render(f"Base HP: {base_hp}", True, WHITE)
    wave_text = font.render(f"Wave: {wave}", True, WHITE)
    enemies_left_text = font.render(f"Enemies Left: {enemies_left}", True, WHITE)
    selected_tower_text = font.render(f"Selected Tower: {selected_tower}", True, WHITE)
    
    screen.blit(gold_text, (MAP_AREA_WIDTH + 10, 10))
    screen.blit(base_hp_text, (MAP_AREA_WIDTH + 10, 40))
    screen.blit(wave_text, (MAP_AREA_WIDTH + 10, 70))
    screen.blit(enemies_left_text, (MAP_AREA_WIDTH + 10, 100))
    screen.blit(selected_tower_text, (MAP_AREA_WIDTH + 10, 130))

def draw_towers(towers):
    for tower in towers:
        pygame.draw.rect(screen, TOWER_COLORS[tower.type], (tower.x * TILE_SIZE, tower.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.draw.circle(screen, (255, 255, 255), (tower.x * TILE_SIZE + TILE_SIZE // 2, tower.y * TILE_SIZE + TILE_SIZE // 2), tower.range // TILE_SIZE, 1)
        level_text = font.render(str(tower.level), True, WHITE)
        screen.blit(level_text, (tower.x * TILE_SIZE + TILE_SIZE // 3, tower.y * TILE_SIZE + TILE_SIZE // 3))

def draw_enemies(enemies):
    for enemy in enemies:
        pygame.draw.rect(screen, ENEMY_COLORS[enemy.type], (enemy.x, enemy.y, TILE_SIZE, TILE_SIZE))

def game_over(base_hp):
    if base_hp <= 0:
        over_text = large_font.render("Game Over", True, RED)
        screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2 - over_text.get_height() // 2))
        restart_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        return True
    return False

def you_win(wave):
    if wave > len(WAVES):
        win_text = large_font.render("You Win", True, GREEN)
        screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - win_text.get_height() // 2))
        restart_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        return True
    return False

def main():
    gold = INITIAL_GOLD
    base_hp = BASE_HP
    wave = 1
    enemies = []
    towers = []
    selected_tower = 1
    enemy_spawn_time = pygame.time.get_ticks()
    last_wave_time = pygame.time.get_ticks()
    game_running = True
    game_over_state = False

    while True:
        screen.fill(BLACK)
        draw_grid()
        draw_path()
        draw_hud(gold, base_hp, wave, len(enemies), selected_tower)
        draw_towers(towers)
        draw_enemies(enemies)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    main()
                    return
                if event.key == pygame.K_1:
                    selected_tower = 1
                if event.key == pygame.K_2:
                    selected_tower = 2
                if event.key == pygame.K_3:
                    selected_tower = 3
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over_state:
                x, y = event.pos
                if x < MAP_AREA_WIDTH:
                    grid_x, grid_y = x // TILE_SIZE, y // TILE_SIZE
                    if (grid_x, grid_y) not in PATH and not any(tower for tower in towers if tower.x == grid_x and tower.y == grid_y):
                        if event.button == 1:
                            if gold >= [ARROW_TOWER_COST, CANNON_TOWER_COST, SLOW_TOWER_COST][selected_tower - 1]:
                                gold -= [ARROW_TOWER_COST, CANNON_TOWER_COST, SLOW_TOWER_COST][selected_tower - 1]
                                towers.append(Tower(grid_x, grid_y, selected_tower))
                        elif event.button == 3:
                            for tower in towers:
                                if tower.x == grid_x and tower.y == grid_y:
                                    upgrade_cost = int([ARROW_TOWER_COST, CANNON_TOWER_COST, SLOW_TOWER_COST][selected_tower - 1] * UPGRADE_COST_FACTOR)
                                    if gold >= upgrade_cost and tower.level < TOWER_MAX_LEVEL:
                                        gold -= upgrade_cost
                                        tower.upgrade()
                                        break
            if event.type == pygame.USEREVENT:
                for tower in towers:
                    tower.attack(enemies)

        now = pygame.time.get_ticks()
        if not enemies and now - last_wave_time > WAVE_DELAY and wave <= len(WAVES):
            for enemy_wave in WAVES[wave - 1]:
                for _ in range(enemy_wave["count"]):
                    enemies.append(Enemy(PATH[0][0] * TILE_SIZE, PATH[0][1] * TILE_SIZE, enemy_wave["type"]))
            last_wave_time = now
            wave += 1

        for enemy in enemies[:]:
            enemy.move()
            if (enemy.x, enemy.y) == (PATH[-1][0] * TILE_SIZE, PATH[-1][1] * TILE_SIZE):
                base_hp -= 1
                enemies.remove(enemy)
            elif enemy.hp <= 0:
                gold += enemy.reward
                enemies.remove(enemy)

        if game_over(base_hp):
            game_over_state = True
        elif you_win(wave):
            game_over_state = True

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()