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
PLAYER_COLOR = (0, 255, 0)
ENEMY_COLOR = (255, 0, 0)
WALL_COLOR = (128, 128, 128)
FLOOR_COLOR = (96, 96, 96)
POTION_COLOR = (255, 165, 0)
WEAPON_COLOR = (255, 255, 0)
EXIT_COLOR = (0, 0, 255)
HUD_COLOR = (255, 255, 255)
FONT = pygame.font.Font(None, 36)

class Player:
    def __init__(self):
        self.x = MAP_WIDTH // 2
        self.y = MAP_HEIGHT // 2
        self.hp = 20
        self.max_hp = 20
        self.atk = 5
        self.lv = 1
        self.exp = 0
        self.floor = 1

    def move(self, dx, dy):
        new_x, new_y = self.x + dx, self.y + dy
        if 0 <= new_x < MAP_WIDTH and 0 <= new_y < MAP_HEIGHT and not (dungeon[new_y][new_x] == '#'):
            self.x, self.y = new_x, new_y
            if dungeon[new_y][new_x] == 'P':
                self.hp = min(self.hp + 8, self.max_hp)
                dungeon[new_y][new_x] = '.'
            elif dungeon[new_y][new_x] == 'W':
                self.atk += 2
                dungeon[new_y][new_x] = '.'
            elif dungeon[new_y][new_x] == 'E':
                self.floor += 1
                self.hp = self.max_hp
                generate_dungeon()
            return True
        return False

    def level_up(self):
        if self.exp >= 10:
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

    def move(self):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            new_x, new_y = self.x + dx, self.y + dy
            if 0 <= new_x < MAP_WIDTH and 0 <= new_y < MAP_HEIGHT and not (dungeon[new_y][new_x] == '#'):
                self.x, self.y = new_x, new_y
                break

    def attack(self, player):
        if abs(self.x - player.x) <= 1 and abs(self.y - player.y) <= 1:
            player.hp -= self.atk

def generate_dungeon():
    global dungeon, enemies, player
    dungeon = [['#' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    rooms = []
    for _ in range(6):
        w = random.randint(4, 6)
        h = random.randint(4, 6)
        x = random.randint(1, MAP_WIDTH - w - 1)
        y = random.randint(1, MAP_HEIGHT - h - 1)
        if not any(abs(x - rx) <= w + 2 and abs(y - ry) <= h + 2 for rx, ry, rw, rh in rooms):
            rooms.append((x, y, w, h))
            for i in range(w):
                for j in range(h):
                    dungeon[y + j][x + i] = '.'
    for i in range(len(rooms) - 1):
        connect_rooms(rooms[i], rooms[i + 1])
    place_objects()
    place_exit()
    place_player()
    place_enemies()

def connect_rooms(room1, room2):
    x1, y1, w1, h1 = room1
    x2, y2, w2, h2 = room2
    if random.random() < 0.5:
        for x in range(min(x1, x2), max(x1 + w1, x2 + w2)):
            dungeon[y1][x] = '.'
        for y in range(min(y1, y2), max(y1 + h1, y2 + h2)):
            dungeon[y][x2] = '.'
    else:
        for y in range(min(y1, y2), max(y1 + h1, y2 + h2)):
            dungeon[y][x1] = '.'
        for x in range(min(x1, x2), max(x1 + w1, x2 + w2)):
            dungeon[y2][x] = '.'

def place_objects():
    for _ in range(2):
        x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
        if dungeon[y][x] == '.':
            dungeon[y][x] = 'P'
    x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
    if dungeon[y][x] == '.':
        dungeon[y][x] = 'W'

def place_exit():
    x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
    if dungeon[y][x] == '.':
        dungeon[y][x] = 'E'

def place_player():
    global player
    player = Player()

def place_enemies():
    global enemies
    enemies = []
    for _ in range(4):
        x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
        if dungeon[y][x] == '.':
            enemies.append(Enemy(x, y))

def draw_dungeon():
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            rect = pygame.Rect(x * TILE_SIZE + (SCREEN_WIDTH - MAP_WIDTH * TILE_SIZE) // 2,
                               y * TILE_SIZE + (SCREEN_HEIGHT - MAP_HEIGHT * TILE_SIZE) // 2,
                               TILE_SIZE, TILE_SIZE)
            if dungeon[y][x] == '#':
                pygame.draw.rect(screen, WALL_COLOR, rect)
            elif dungeon[y][x] == '.':
                pygame.draw.rect(screen, FLOOR_COLOR, rect)
            elif dungeon[y][x] == 'P':
                pygame.draw.rect(screen, POTION_COLOR, rect)
            elif dungeon[y][x] == 'W':
                pygame.draw.rect(screen, WEAPON_COLOR, rect)
            elif dungeon[y][x] == 'E':
                pygame.draw.rect(screen, EXIT_COLOR, rect)

def draw_player():
    rect = pygame.Rect(player.x * TILE_SIZE + (SCREEN_WIDTH - MAP_WIDTH * TILE_SIZE) // 2,
                       player.y * TILE_SIZE + (SCREEN_HEIGHT - MAP_HEIGHT * TILE_SIZE) // 2,
                       TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(screen, PLAYER_COLOR, rect)

def draw_enemies():
    for enemy in enemies:
        rect = pygame.Rect(enemy.x * TILE_SIZE + (SCREEN_WIDTH - MAP_WIDTH * TILE_SIZE) // 2,
                           enemy.y * TILE_SIZE + (SCREEN_HEIGHT - MAP_HEIGHT * TILE_SIZE) // 2,
                           TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, ENEMY_COLOR, rect)

def draw_hud():
    text = f"HP: {player.hp}/{player.max_hp} ATK: {player.atk} LV: {player.lv} EXP: {player.exp} Floor: {player.floor}"
    text_surface = FONT.render(text, True, HUD_COLOR)
    screen.blit(text_surface, (10, 10))

def game_over():
    screen.fill((0, 0, 0))
    text_surface = FONT.render("Game Over! Press R to Restart", True, HUD_COLOR)
    screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, SCREEN_HEIGHT // 2 - text_surface.get_height() // 2))

def game_win():
    screen.fill((0, 0, 0))
    text_surface = FONT.render("You Win! Press R to Restart", True, HUD_COLOR)
    screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, SCREEN_HEIGHT // 2 - text_surface.get_height() // 2))

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roguelike Dungeon Hard")
clock = pygame.time.Clock()

generate_dungeon()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                generate_dungeon()
            elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                dx, dy = 0, 0
                if event.key == pygame.K_UP:
                    dy = -1
                elif event.key == pygame.K_DOWN:
                    dy = 1
                elif event.key == pygame.K_LEFT:
                    dx = -1
                elif event.key == pygame.K_RIGHT:
                    dx = 1
                if player.move(dx, dy):
                    for enemy in enemies:
                        enemy.move()
                        enemy.attack(player)
                        if enemy.hp <= 0:
                            enemies.remove(enemy)
                            player.exp += 5
                            player.level_up()
                    if player.hp <= 0:
                        game_over()
                        pygame.display.flip()
                        waiting = True
                        while waiting:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    waiting = False
                                    running = False
                                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                                    waiting = False
                    if player.floor > 1:
                        game_win()
                        pygame.display.flip()
                        waiting = True
                        while waiting:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    waiting = False
                                    running = False
                                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                                        waiting = False

    screen.fill((0, 0, 0))
    draw_dungeon()
    draw_player()
    draw_enemies()
    draw_hud()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()