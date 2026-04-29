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
ORANGE = (255, 165, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roguelike Dungeon Hard")
clock = pygame.time.Clock()

class Entity:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, GREEN)
        self.hp = 20
        self.max_hp = 20
        self.atk = 5
        self.lv = 1
        self.exp = 0
        self.floor = 1

    def move(self, dx, dy):
        if 0 <= self.x + dx < MAP_WIDTH and 0 <= self.y + dy < MAP_HEIGHT and map[self.y + dy][self.x + dx]!= 'W':
            self.x += dx
            self.y += dy
            return True
        return False

    def attack_enemies(self, enemies):
        for enemy in enemies:
            if self.x == enemy.x and self.y == enemy.y:
                enemy.hp -= self.atk
                if enemy.hp <= 0:
                    enemies.remove(enemy)
                    self.exp += 5
                    if self.exp >= 10:
                        self.exp -= 10
                        self.lv += 1
                        self.max_hp += 5
                        self.hp = self.max_hp
                        self.atk += 1

class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, RED)
        self.hp = 8
        self.atk = 3

    def move_towards_player(self, player):
        if self.x < player.x:
            if self.move(1, 0):
                return
        elif self.x > player.x:
            if self.move(-1, 0):
                return
        if self.y < player.y:
            if self.move(0, 1):
                return
        elif self.y > player.y:
            if self.move(0, -1):
                return

    def move(self, dx, dy):
        if 0 <= self.x + dx < MAP_WIDTH and 0 <= self.y + dy < MAP_HEIGHT and map[self.y + dy][self.x + dx]!= 'W':
            self.x += dx
            self.y += dy
            return True
        return False

    def attack_player(self, player):
        if self.x == player.x and self.y == player.y:
            player.hp -= self.atk
            if player.hp <= 0:
                game_over()

class Item(Entity):
    def __init__(self, x, y, color, effect):
        super().__init__(x, y, color)
        self.effect = effect

    def apply_effect(self, player):
        if self.effect == 'heal':
            player.hp = min(player.hp + 8, player.max_hp)
        elif self.effect == 'atk_up':
            player.atk += 2

def generate_map():
    map = [['F' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    rooms = []
    for _ in range(6):
        room_w = random.randint(4, 6)
        room_h = random.randint(4, 6)
        room_x = random.randint(1, MAP_WIDTH - room_w - 1)
        room_y = random.randint(1, MAP_HEIGHT - room_h - 1)
        if not any(check_overlap(room_x, room_y, room_w, room_h, rx, ry, rw, rh) for rx, ry, rw, rh in rooms):
            rooms.append((room_x, room_y, room_w, room_h))
            for y in range(room_y, room_y + room_h):
                for x in range(room_x, room_x + room_w):
                    map[y][x] = 'F'
    for room_x, room_y, room_w, room_h in rooms:
        if random.random() < 0.5:
            connect_rooms(rooms, room_x, room_y, room_w, room_h)
    place_items_and_exit(map, rooms)
    return map

def check_overlap(rx1, ry1, rw1, rh1, rx2, ry2, rw2, rh2):
    return not (rx1 + rw1 <= rx2 or rx1 >= rx2 + rw2 or ry1 + rh1 <= ry2 or ry1 >= ry2 + rh2)

def connect_rooms(rooms, room_x, room_y, room_w, room_h):
    for _ in range(random.randint(1, 3)):
        target_room = random.choice(rooms)
        target_x, target_y, target_w, target_h = target_room
        if room_x < target_x:
            corridor_x = room_x + room_w
            corridor_y = random.randint(room_y, room_y + room_h - 1)
            target_corridor_x = target_x
            target_corridor_y = random.randint(target_y, target_y + target_h - 1)
        elif room_x > target_x:
            corridor_x = room_x
            corridor_y = random.randint(room_y, room_y + room_h - 1)
            target_corridor_x = target_x + target_w
            target_corridor_y = random.randint(target_y, target_y + target_h - 1)
        elif room_y < target_y:
            corridor_x = random.randint(room_x, room_x + room_w - 1)
            corridor_y = room_y + room_h
            target_corridor_x = random.randint(target_x, target_x + target_w - 1)
            target_corridor_y = target_y
        else:
            corridor_x = random.randint(room_x, room_x + room_w - 1)
            corridor_y = room_y
            target_corridor_x = random.randint(target_x, target_x + target_w - 1)
            target_corridor_y = target_y + target_h
        draw_corridor(corridor_x, corridor_y, target_corridor_x, target_corridor_y)

def draw_corridor(cx1, cy1, cx2, cy2):
    while cx1!= cx2 or cy1!= cy2:
        if cx1 < cx2:
            cx1 += 1
        elif cx1 > cx2:
            cx1 -= 1
        elif cy1 < cy2:
            cy1 += 1
        elif cy1 > cy2:
            cy1 -= 1
        map[cy1][cx1] = 'F'

def place_items_and_exit(map, rooms):
    for _ in range(2):
        place_item(map, rooms, 'heal')
    place_item(map, rooms, 'atk_up')
    place_exit(map, rooms)

def place_item(map, rooms, effect):
    room_x, room_y, room_w, room_h = random.choice(rooms)
    item_x = random.randint(room_x, room_x + room_w - 1)
    item_y = random.randint(room_y, room_y + room_h - 1)
    while map[item_y][item_x]!= 'F':
        item_x = random.randint(room_x, room_x + room_w - 1)
        item_y = random.randint(room_y, room_y + room_h - 1)
    map[item_y][item_x] = effect

def place_exit(map, rooms):
    room_x, room_y, room_w, room_h = random.choice(rooms)
    exit_x = random.randint(room_x, room_x + room_w - 1)
    exit_y = random.randint(room_y, room_y + room_h - 1)
    while map[exit_y][exit_x]!= 'F':
        exit_x = random.randint(room_x, room_x + room_w - 1)
        exit_y = random.randint(room_y, room_y + room_h - 1)
    map[exit_y][exit_x] = 'E'

def draw_map(map):
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if map[y][x] == 'W':
                pygame.draw.rect(screen, BLACK, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif map[y][x] == 'F':
                pygame.draw.rect(screen, WHITE, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif map[y][x] == 'E':
                pygame.draw.rect(screen, YELLOW, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif map[y][x] == 'heal':
                pygame.draw.rect(screen, BLUE, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif map[y][x] == 'atk_up':
                pygame.draw.rect(screen, ORANGE, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

def draw_hud(player):
    font = pygame.font.Font(None, 36)
    hp_text = font.render(f"HP: {player.hp}/{player.max_hp}", True, RED)
    atk_text = font.render(f"ATK: {player.atk}", True, RED)
    lv_text = font.render(f"LV: {player.lv}", True, RED)
    exp_text = font.render(f"EXP: {player.exp}", True, RED)
    floor_text = font.render(f"Floor: {player.floor}", True, RED)
    screen.blit(hp_text, (10, 10))
    screen.blit(atk_text, (10, 50))
    screen.blit(lv_text, (10, 90))
    screen.blit(exp_text, (10, 130))
    screen.blit(floor_text, (10, 170))

def game_over():
    global running
    font = pygame.font.Font(None, 74)
    text = font.render('Game Over', True, RED)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    restart_text = font.render('Press R to Restart', True, GREEN)
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def main():
    global map, player, enemies, items
    map = generate_map()
    player = Player(1, 1)
    enemies = [Enemy(random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)) for _ in range(4)]
    items = [Item(x, y, color, effect) for y, row in enumerate(map) for x, cell in enumerate(row) if cell in ['heal', 'atk_up']]

    running = True
    while running:
        screen.fill(BLACK)
        draw_map(map)
        player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        for item in items:
            item.draw(screen)
        draw_hud(player)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    main()
                if event.key == pygame.K_UP:
                    if player.move(0, -1):
                        for enemy in enemies:
                            enemy.move_towards_player(player)
                            enemy.attack_player(player)
                elif event.key == pygame.K_DOWN:
                    if player.move(0, 1):
                        for enemy in enemies:
                            enemy.move_towards_player(player)
                            enemy.attack_player(player)
                elif event.key == pygame.K_LEFT:
                    if player.move(-1, 0):
                        for enemy in enemies:
                            enemy.move_towards_player(player)
                            enemy.attack_player(player)
                elif event.key == pygame.K_RIGHT:
                    if player.move(1, 0):
                        for enemy in enemies:
                            enemy.move_towards_player(player)
                            enemy.attack_player(player)
        
        for item in items[:]:
            if item.x == player.x and item.y == player.y:
                item.apply_effect(player)
                items.remove(item)
        
        if map[player.y][player.x] == 'E':
            player.floor += 1
            main()
        
        pygame.display.flip()
        clock.tick(FPS)

main()