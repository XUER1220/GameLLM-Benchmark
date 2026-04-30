import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
MAP_WIDTH = 21
MAP_HEIGHT = 15
TILE_SIZE = 32
MAP_DISPLAY_WIDTH = MAP_WIDTH * TILE_SIZE
MAP_DISPLAY_HEIGHT = MAP_HEIGHT * TILE_SIZE

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

PLAYER_COLOR = YELLOW
ENEMY_COLOR = RED
WALL_COLOR = BLACK
FLOOR_COLOR = WHITE
POTION_COLOR = GREEN
WEAPON_COLOR = BLUE
EXIT_COLOR = CYAN

PLAYER_HP = 20
PLAYER_ATK = 5
PLAYER_LV = 1
PLAYER_EXP = 0
PLAYER_FLOOR = 1

ENEMY_HP = 8
ENEMY_ATK = 3

EXP_TO_LEVEL_UP = 10
LEVEL_UP_HP_BONUS = 5
LEVEL_UP_ATK_BONUS = 1

NUM_ENEMIES = 4
NUM_POTIONS = 2
NUM_WEAPONS = 1

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roguelike Dungeon Hard")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

class Entity:
    def __init__(self, x, y, color, hp, atk):
        self.x = x
        self.y = y
        self.color = color
        self.hp = hp
        self.atk = atk

class Player(Entity):
    def __init__(self, x, y, color, hp, atk):
        super().__init__(x, y, color, hp, atk)

class Enemy(Entity):
    def __init__(self, x, y, color, hp, atk):
        super().__init__(x, y, color, hp, atk)

class Item:
    def __init__(self, x, y, color, effect):
        self.x = x
        self.y = y
        self.color = color
        self.effect = effect

def draw_map(player, enemies, items):
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if (x, y) == (player.x, player.y):
                pygame.draw.rect(screen, player.color, (SCREEN_WIDTH//2 - MAP_DISPLAY_WIDTH//2 + x * TILE_SIZE, SCREEN_HEIGHT//2 - MAP_DISPLAY_HEIGHT//2 + y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif any(enemy.x == x and enemy.y == y for enemy in enemies):
                pygame.draw.rect(screen, ENEMY_COLOR, (SCREEN_WIDTH//2 - MAP_DISPLAY_WIDTH//2 + x * TILE_SIZE, SCREEN_HEIGHT//2 - MAP_DISPLAY_HEIGHT//2 + y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif any(item.x == x and item.y == y for item in items):
                item = next(item for item in items if item.x == x and item.y == y)
                pygame.draw.rect(screen, item.color, (SCREEN_WIDTH//2 - MAP_DISPLAY_WIDTH//2 + x * TILE_SIZE, SCREEN_HEIGHT//2 - MAP_DISPLAY_HEIGHT//2 + y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            else:
                pygame.draw.rect(screen, WALL_COLOR, (SCREEN_WIDTH//2 - MAP_DISPLAY_WIDTH//2 + x * TILE_SIZE, SCREEN_HEIGHT//2 - MAP_DISPLAY_HEIGHT//2 + y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

def draw_hud(player):
    hp_text = font.render(f"HP: {player.hp}", True, BLACK)
    atk_text = font.render(f"ATK: {player.atk}", True, BLACK)
    lv_text = font.render(f"LV: {player.lv}", True, BLACK)
    exp_text = font.render(f"EXP: {player.exp}/{EXP_TO_LEVEL_UP}", True, BLACK)
    floor_text = font.render(f"Floor: {player.floor}", True, BLACK)
    screen.blit(hp_text, (10, 10))
    screen.blit(atk_text, (10, 50))
    screen.blit(lv_text, (10, 90))
    screen.blit(exp_text, (10, 130))
    screen.blit(floor_text, (10, 170))

def generate_dungeon():
    rooms = []
    corridors = []
    for _ in range(6):
        w = random.randint(4, 6)
        h = random.randint(4, 6)
        x = random.randint(1, MAP_WIDTH - w - 1)
        y = random.randint(1, MAP_HEIGHT - h - 1)
        room = (x, y, w, h)
        rooms.append(room)
        if rooms:
            prev_room = rooms[-2]
            corridors.append(((prev_room[0] + prev_room[2] // 2, prev_room[1] + prev_room[3] // 2), (x + w // 2, y + h // 2)))
    dungeon = [[1 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    for room in rooms:
        for dy in range(room[3]):
            for dx in range(room[2]):
                dungeon[room[1] + dy][room[0] + dx] = 0
    for (sx, sy), (ex, ey) in corridors:
        if sx == ex:
            for y in range(min(sy, ey), max(sy, ey) + 1):
                dungeon[y][sx] = 0
        else:
            for x in range(min(sx, ex), max(sx, ex) + 1):
                dungeon[sy][x] = 0
    return dungeon

def place_entities(dungeon, player, enemies, items):
    room_centers = []
    for room in rooms:
        room_centers.append((room[0] + room[2] // 2, room[1] + room[3] // 2))
    player_pos = random.choice(room_centers)
    player.x, player.y = player_pos
    for _ in range(NUM_ENEMIES):
        enemy_pos = random.choice(room_centers)
        while enemy_pos == player_pos or any(enemy.x == enemy_pos[0] and enemy.y == enemy_pos[1] for enemy in enemies):
            enemy_pos = random.choice(room_centers)
        enemies.append(Enemy(enemy_pos[0], enemy_pos[1], ENEMY_COLOR, ENEMY_HP, ENEMY_ATK))
    for _ in range(NUM_POTIONS):
        item_pos = random.choice(room_centers)
        while any(entity.x == item_pos[0] and entity.y == item_pos[1] for entity in enemies + [player] + items):
            item_pos = random.choice(room_centers)
        items.append(Item(item_pos[0], item_pos[1], POTION_COLOR, 8))
    for _ in range(NUM_WEAPONS):
        item_pos = random.choice(room_centers)
        while any(entity.x == item_pos[0] and entity.y == item_pos[1] for entity in enemies + [player] + items):
            item_pos = random.choice(room_centers)
        items.append(Item(item_pos[0], item_pos[1], WEAPON_COLOR, 2))
    exit_pos = random.choice(room_centers)
    while any(entity.x == exit_pos[0] and entity.y == exit_pos[1] for entity in enemies + [player] + items):
        exit_pos = random.choice(room_centers)
    items.append(Item(exit_pos[0], exit_pos[1], EXIT_COLOR, None))

def player_move(player, dx, dy, dungeon):
    new_x, new_y = player.x + dx, player.y + dy
    if 0 <= new_x < MAP_WIDTH and 0 <= new_y < MAP_HEIGHT and dungeon[new_y][new_x] == 0:
        player.x, player.y = new_x, new_y

def enemy_move(enemy, player, dungeon):
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    random.shuffle(directions)
    for dx, dy in directions:
        new_x, new_y = enemy.x + dx, enemy.y + dy
        if 0 <= new_x < MAP_WIDTH and 0 <= new_y < MAP_HEIGHT and dungeon[new_y][new_x] == 0:
            enemy.x, enemy.y = new_x, new_y
            break

def check_collisions(player, enemies, items):
    for enemy in enemies:
        if player.x == enemy.x and player.y == enemy.y:
            player.hp -= enemy.atk
            if player.hp <= 0:
                return "Game Over"
            enemy.hp -= player.atk
            if enemy.hp <= 0:
                enemies.remove(enemy)
                player.exp += 5
                if player.exp >= EXP_TO_LEVEL_UP:
                    player.lv += 1
                    player.exp -= EXP_TO_LEVEL_UP
                    player.hp += LEVEL_UP_HP_BONUS
                    player.atk += LEVEL_UP_ATK_BONUS
    for item in items:
        if player.x == item.x and player.y == item.y:
            if item.color == POTION_COLOR:
                player.hp = min(player.hp + item.effect, PLAYER_HP + LEVEL_UP_HP_BONUS * (player.lv - 1))
            elif item.color == WEAPON_COLOR:
                player.atk += item.effect
            elif item.color == EXIT_COLOR:
                return "Next Level"
            items.remove(item)
    return None

def game_loop():
    global rooms
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    return "Restart"
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player_move(player, 0, -1, dungeon)
        elif keys[pygame.K_DOWN]:
            player_move(player, 0, 1, dungeon)
        elif keys[pygame.K_LEFT]:
            player_move(player, -1, 0, dungeon)
        elif keys[pygame.K_RIGHT]:
            player_move(player, 1, 0, dungeon)
        
        for enemy in enemies:
            enemy_move(enemy, player, dungeon)
        
        result = check_collisions(player, enemies, items)
        if result:
            if result == "Game Over":
                running = False
                return "Game Over"
            elif result == "Next Level":
                player.floor += 1
                dungeon = generate_dungeon()
                place_entities(dungeon, player, enemies, items)
        
        screen.fill(BLACK)
        draw_map(player, enemies, items)
        draw_hud(player)
        pygame.display.flip()
        clock.tick(FPS)

    return "Game Over"

def main():
    global player, enemies, items, dungeon, rooms
    while True:
        player = Player(0, 0, PLAYER_COLOR, PLAYER_HP, PLAYER_ATK)
        enemies = []
        items = []
        dungeon = generate_dungeon()
        rooms = []
        place_entities(dungeon, player, enemies, items)
        
        result = game_loop()
        
        if result == "Game Over":
            screen.fill(BLACK)
            game_over_text = font.render("Game Over", True, WHITE)
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            pygame.display.flip()
            
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            break
        elif result == "Restart":
            continue

if __name__ == "__main__":
    main()