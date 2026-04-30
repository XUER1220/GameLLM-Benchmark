import pygame
import random
import sys

pygame.init()
random.seed(42)

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
FPS = 60
MAP_WIDTH, MAP_HEIGHT = 21, 15
TILE_SIZE = 32
MAP_DISPLAY_WIDTH, MAP_DISPLAY_HEIGHT = MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE
PLAYER_COLOR = (0, 255, 0)
ENEMY_COLOR = (255, 0, 0)
WALL_COLOR = (128, 128, 128)
FLOOR_COLOR = (64, 64, 64)
POTION_COLOR = (0, 0, 255)
WEAPON_COLOR = (255, 255, 0)
EXIT_COLOR = (255, 255, 255)
HUD_COLOR = (255, 255, 255)
GAME_OVER_COLOR = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FONT = pygame.font.Font(None, 36)

class Player:
    def __init__(self):
        self.x, self.y = 1, 1
        self.hp = 20
        self.max_hp = 20
        self.atk = 5
        self.lv = 1
        self.exp = 0
        self.floor = 1

    def move(self, dx, dy, game_map):
        nx, ny = self.x + dx, self.y + dy
        if game_map[ny][nx]!= 1:
            self.x, self.y = nx, ny
            return True
        return False

    def attack(self, target):
        target.hp -= self.atk
        return target.hp <= 0

    def level_up(self):
        self.exp -= 10
        self.lv += 1
        self.max_hp += 5
        self.hp = self.max_hp
        self.atk += 1

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 8
        self.atk = 3

    def move(self, player, game_map):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = self.x + dx, self.y + dy
            if game_map[ny][nx]!= 1 and (nx, ny)!= (player.x, player.y):
                self.x, self.y = nx, ny
                return
            elif game_map[ny][nx]!= 1 and (nx, ny) == (player.x, player.y):
                if player.hp > 0:
                    player.hp -= self.atk
                if player.hp <= 0:
                    game_over()

class Item:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type

    def use(self, player):
        if self.type == "potion":
            player.hp = min(player.hp + 8, player.max_hp)
        elif self.type == "weapon":
            player.atk += 2

def generate_map():
    game_map = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    rooms = []
    for _ in range(6):
        w = random.randint(4, 6)
        h = random.randint(4, 6)
        x = random.randint(1, MAP_WIDTH - w - 1)
        y = random.randint(1, MAP_HEIGHT - h - 1)
        if any(any(game_map[yy][xx] for xx in range(x, x + w + 1) for yy in range(y, y + h + 1)):
               for rx, ry, rw, rh in rooms):
            continue
        for xx in range(x, x + w):
            for yy in range(y, y + h):
                game_map[yy][xx] = 1
        rooms.append((x, y, w, h))
    for i in range(len(rooms)):
        for j in range(i + 1, len(rooms)):
            rx1, ry1, rw1, rh1 = rooms[i]
            rx2, ry2, rw2, rh2 = rooms[j]
            cx1, cy1 = rx1 + rw1 // 2, ry1 + rh1 // 2
            cx2, cy2 = rx2 + rw2 // 2, ry2 + rh2 // 2
            while cx1!= cx2 or cy1!= cy2:
                if cx1 < cx2:
                    cx1 += 1
                elif cx1 > cx2:
                    cx1 -= 1
                elif cy1 < cy2:
                    cy1 += 1
                elif cy1 > cy2:
                    cy1 -= 1
                game_map[cy1][cx1] = 0
    return game_map

def place_items(game_map, player, enemies):
    items = []
    for _ in range(2):
        while True:
            x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
            if game_map[y][x] == 0 and (x, y)!= (player.x, player.y) and all((x, y)!= (e.x, e.y) for e in enemies):
                items.append(Item(x, y, "potion"))
                break
    while True:
        x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
        if game_map[y][x] == 0 and (x, y)!= (player.x, player.y) and all((x, y)!= (e.x, e.y) for e in enemies) and all((x, y)!= (i.x, i.y) for i in items):
            items.append(Item(x, y, "weapon"))
            break
    return items

def place_exit(game_map):
    while True:
        x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
        if game_map[y][x] == 0:
            return x, y

def place_player_and_enemies(game_map):
    player = Player()
    enemies = []
    for _ in range(4):
        while True:
            x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
            if game_map[y][x] == 0 and (x, y)!= (player.x, player.y):
                enemies.append(Enemy(x, y))
                break
    return player, enemies

def draw_map(game_map, player, enemies, items, exit_pos):
    screen.fill(BLACK)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if game_map[y][x] == 1:
                pygame.draw.rect(screen, WALL_COLOR, (x * TILE_SIZE + (WINDOW_WIDTH - MAP_DISPLAY_WIDTH) // 2, y * TILE_SIZE + (WINDOW_HEIGHT - MAP_DISPLAY_HEIGHT) // 2, TILE_SIZE, TILE_SIZE))
            else:
                pygame.draw.rect(screen, FLOOR_COLOR, (x * TILE_SIZE + (WINDOW_WIDTH - MAP_DISPLAY_WIDTH) // 2, y * TILE_SIZE + (WINDOW_HEIGHT - MAP_DISPLAY_HEIGHT) // 2, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, PLAYER_COLOR, (player.x * TILE_SIZE + (WINDOW_WIDTH - MAP_DISPLAY_WIDTH) // 2, player.y * TILE_SIZE + (WINDOW_HEIGHT - MAP_DISPLAY_HEIGHT) // 2, TILE_SIZE, TILE_SIZE))
    for enemy in enemies:
        pygame.draw.rect(screen, ENEMY_COLOR, (enemy.x * TILE_SIZE + (WINDOW_WIDTH - MAP_DISPLAY_WIDTH) // 2, enemy.y * TILE_SIZE + (WINDOW_HEIGHT - MAP_DISPLAY_HEIGHT) // 2, TILE_SIZE, TILE_SIZE))
    for item in items:
        if item.type == "potion":
            pygame.draw.rect(screen, POTION_COLOR, (item.x * TILE_SIZE + (WINDOW_WIDTH - MAP_DISPLAY_WIDTH) // 2, item.y * TILE_SIZE + (WINDOW_HEIGHT - MAP_DISPLAY_HEIGHT) // 2, TILE_SIZE, TILE_SIZE))
        elif item.type == "weapon":
            pygame.draw.rect(screen, WEAPON_COLOR, (item.x * TILE_SIZE + (WINDOW_WIDTH - MAP_DISPLAY_WIDTH) // 2, item.y * TILE_SIZE + (WINDOW_HEIGHT - MAP_DISPLAY_HEIGHT) // 2, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, EXIT_COLOR, (exit_pos[0] * TILE_SIZE + (WINDOW_WIDTH - MAP_DISPLAY_WIDTH) // 2, exit_pos[1] * TILE_SIZE + (WINDOW_HEIGHT - MAP_DISPLAY_HEIGHT) // 2, TILE_SIZE, TILE_SIZE))
    draw_hud(player)

def draw_hud(player):
    hp_text = FONT.render(f"HP: {player.hp}/{player.max_hp}", True, HUD_COLOR)
    atk_text = FONT.render(f"ATK: {player.atk}", True, HUD_COLOR)
    lv_text = FONT.render(f"LV: {player.lv}", True, HUD_COLOR)
    exp_text = FONT.render(f"EXP: {player.exp}", True, HUD_COLOR)
    floor_text = FONT.render(f"Floor: {player.floor}", True, HUD_COLOR)
    screen.blit(hp_text, (10, 10))
    screen.blit(atk_text, (10, 40))
    screen.blit(lv_text, (10, 70))
    screen.blit(exp_text, (10, 100))
    screen.blit(floor_text, (10, 130))

def game_over():
    global running
    screen.fill(BLACK)
    game_over_text = FONT.render("Game Over", True, GAME_OVER_COLOR)
    restart_text = FONT.render("Press R to Restart", True, HUD_COLOR)
    screen.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, WINDOW_HEIGHT // 2 - game_over_text.get_height() // 2))
    screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2 + 40))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def main():
    global running
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Roguelike Dungeon Hard")
    clock = pygame.time.Clock()

    while True:
        game_map = generate_map()
        player, enemies = place_player_and_enemies(game_map)
        items = place_items(game_map, player, enemies)
        exit_pos = place_exit(game_map)
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        running = False
                        break
                    elif event.key == pygame.K_UP:
                        if player.move(0, -1, game_map):
                            for enemy in enemies:
                                enemy.move(player, game_map)
                    elif event.key == pygame.K_DOWN:
                        if player.move(0, 1, game_map):
                            for enemy in enemies:
                                enemy.move(player, game_map)
                    elif event.key == pygame.K_LEFT:
                        if player.move(-1, 0, game_map):
                            for enemy in enemies:
                                enemy.move(player, game_map)
                    elif event.key == pygame.K_RIGHT:
                        if player.move(1, 0, game_map):
                            for enemy in enemies:
                                enemy.move(player, game_map)

            if player.hp <= 0:
                game_over()
                continue

            if (player.x, player.y) == exit_pos:
                player.floor += 1
                continue

            for item in items[:]:
                if (player.x, player.y) == (item.x, item.y):
                    item.use(player)
                    items.remove(item)

            for enemy in enemies[:]:
                if player.attack(enemy):
                    player.exp += 5
                    if player.exp >= 10:
                        player.level_up()
                    enemies.remove(enemy)

            draw_map(game_map, player, enemies, items, exit_pos)
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    main()