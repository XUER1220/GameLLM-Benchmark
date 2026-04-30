import pygame
import random
import sys

# 初始化
random.seed(42)
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Roguelike Dungeon Hard")
clock = pygame.time.Clock()
FPS = 60

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (200, 50, 200)
CYAN = (0, 200, 200)
GRAY = (100, 100, 100)
DARK_GREEN = (0, 150, 0)
BROWN = (150, 75, 0)

# 游戏常量
TILE_SIZE = 32
MAP_COLS, MAP_ROWS = 21, 15
MAP_WIDTH, MAP_HEIGHT = MAP_COLS * TILE_SIZE, MAP_ROWS * TILE_SIZE
MAP_X = (WIDTH - MAP_WIDTH) // 2
MAP_Y = (HEIGHT - MAP_HEIGHT) // 2 + 20

# 玩家初始属性
PLAYER_HP = 20
PLAYER_ATK = 5
PLAYER_LV = 1
PLAYER_EXP = 0
PLAYER_FLOOR = 1
PLAYER_SPEED = 1

# 敌人属性
ENEMY_COUNT = 4
ENEMY_HP = 8
ENEMY_ATK = 3

# 道具
POTION_COUNT = 2
WEAPON_COUNT = 1
POTION_HEAL = 8
WEAPON_BONUS = 2

# 经验
EXP_PER_KILL = 5
EXP_TO_LEVEL = 10

# 方向
DIRECTIONS = {
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0)
}

# 生成房间
def generate_rooms():
    rooms = []
    attempts = 50
    for _ in range(attempts):
        w = random.randint(4, 7)
        h = random.randint(4, 6)
        x = random.randint(1, MAP_COLS - w - 1)
        y = random.randint(1, MAP_ROWS - h - 1)
        new_room = pygame.Rect(x, y, w, h)
        overlap = False
        for room in rooms:
            if new_room.inflate(2, 2).colliderect(room):
                overlap = True
                break
        if not overlap:
            rooms.append(new_room)
        if len(rooms) >= 6:
            break
    return rooms

# 连接房间
def connect_rooms(rooms, map_grid):
    for i in range(len(rooms) - 1):
        r1 = rooms[i]
        r2 = rooms[i + 1]
        x1, y1 = r1.centerx, r1.centery
        x2, y2 = r2.centerx, r2.centery
        if random.random() < 0.5:
            # 先水平再垂直
            for x in range(min(x1, x2), max(x1, x2) + 1):
                map_grid[y1][x] = 0
            for y in range(min(y1, y2), max(y1, y2) + 1):
                map_grid[y][x2] = 0
        else:
            # 先垂直再水平
            for y in range(min(y1, y2), max(y1, y2) + 1):
                map_grid[y][x1] = 0
            for x in range(min(x1, x2), max(x1, x2) + 1):
                map_grid[y2][x] = 0

# 生成地图
def generate_map(floor):
    map_grid = [[1 for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
    rooms = generate_rooms()
    for room in rooms:
        for y in range(room.top, room.bottom):
            for x in range(room.left, room.right):
                map_grid[y][x] = 0
    connect_rooms(rooms, map_grid)
    # 确保边缘为墙
    for y in range(MAP_ROWS):
        map_grid[y][0] = 1
        map_grid[y][MAP_COLS - 1] = 1
    for x in range(MAP_COLS):
        map_grid[0][x] = 1
        map_grid[MAP_ROWS - 1][x] = 1
    return map_grid, rooms

# 放置实体
def place_entities(rooms, floor):
    positions = []
    # 玩家放在第一个房间
    player_room = rooms[0]
    player_pos = (player_room.centerx, player_room.centery)
    positions.append(('player', player_pos))
    # 出口放在最后一个房间
    exit_room = rooms[-1]
    exit_pos = (exit_room.centerx, exit_room.centery)
    positions.append(('exit', exit_pos))
    # 敌人在空地上
    enemy_count = ENEMY_COUNT + floor - 1
    placed = 0
    attempts = 0
    while placed < enemy_count and attempts < 200:
        room = random.choice(rooms)
        x = random.randint(room.left, room.right - 1)
        y = random.randint(room.top, room.bottom - 1)
        if (x, y) != player_pos and (x, y) != exit_pos:
            occupied = False
            for typ, pos in positions:
                if pos == (x, y):
                    occupied = True
                    break
            if not occupied:
                positions.append(('enemy', (x, y)))
                placed += 1
        attempts += 1
    # 药水
    for _ in range(POTION_COUNT):
        placed_potion = False
        attempts = 0
        while not placed_potion and attempts < 100:
            room = random.choice(rooms)
            x = random.randint(room.left, room.right - 1)
            y = random.randint(room.top, room.bottom - 1)
            occupied = False
            for typ, pos in positions:
                if pos == (x, y):
                    occupied = True
                    break
            if not occupied:
                positions.append(('potion', (x, y)))
                placed_potion = True
            attempts += 1
    # 武器
    placed_weapon = False
    attempts = 0
    while not placed_weapon and attempts < 100:
        room = random.choice(rooms)
        x = random.randint(room.left, room.right - 1)
        y = random.randint(room.top, room.bottom - 1)
        occupied = False
        for typ, pos in positions:
            if pos == (x, y):
                occupied = True
                break
        if not occupied:
            positions.append(('weapon', (x, y)))
            placed_weapon = True
        attempts += 1
    return positions

# 游戏类
class Game:
    def __init__(self):
        self.floor = PLAYER_FLOOR
        self.map_grid, self.rooms = generate_map(self.floor)
        self.entities = place_entities(self.rooms, self.floor)
        self.player = None
        self.enemies = []
        self.potions = []
        self.weapons = []
        self.exit = None
        self.parse_entities()
        self.game_over = False
        self.victory = False

    def parse_entities(self):
        for typ, pos in self.entities:
            if typ == 'player':
                self.player = Player(pos[0], pos[1])
            elif typ == 'enemy':
                self.enemies.append(Enemy(pos[0], pos[1]))
            elif typ == 'potion':
                self.potions.append(Potion(pos[0], pos[1]))
            elif typ == 'weapon':
                self.weapons.append(Weapon(pos[0], pos[1]))
            elif typ == 'exit':
                self.exit = Exit(pos[0], pos[1])

    def reset(self):
        self.__init__()

    def move_player(self, dx, dy):
        if self.game_over:
            return
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        if self.map_grid[new_y][new_x] == 1:
            return
        for enemy in self.enemies:
            if enemy.x == new_x and enemy.y == new_y:
                return
        if self.exit and self.exit.x == new_x and self.exit.y == new_y:
            self.next_floor()
            return
        for potion in self.potions[:]:
            if potion.x == new_x and potion.y == new_y:
                self.player.hp = min(self.player.max_hp, self.player.hp + POTION_HEAL)
                self.potions.remove(potion)
                break
        for weapon in self.weapons[:]:
            if weapon.x == new_x and weapon.y == new_y:
                self.player.atk += WEAPON_BONUS
                self.weapons.remove(weapon)
                break
        self.player.x = new_x
        self.player.y = new_y
        # 敌人回合
        for enemy in self.enemies[:]:
            enemy.move_towards(self.player, self.map_grid)
            if abs(enemy.x - self.player.x) + abs(enemy.y - self.player.y) == 1:
                self.player.hp -= enemy.atk
                if self.player.hp <= 0:
                    self.game_over = True
            # 敌人可能被玩家踩到而攻击
            if enemy.x == self.player.x and enemy.y == self.player.y:
                self.player.hp -= enemy.atk
                if self.player.hp <= 0:
                    self.game_over = True
        # 检查玩家是否站在敌人位置攻击
        for enemy in self.enemies[:]:
            if enemy.x == self.player.x and enemy.y == self.player.y:
                enemy.hp -= self.player.atk
                if enemy.hp <= 0:
                    self.enemies.remove(enemy)
                    self.player.exp += EXP_PER_KILL
                    if self.player.exp >= EXP_TO_LEVEL:
                        self.player.level_up()

    def next_floor(self):
        self.floor += 1
        self.map_grid, self.rooms = generate_map(self.floor)
        self.entities = place_entities(self.rooms, self.floor)
        self.enemies.clear()
        self.potions.clear()
        self.weapons.clear()
        self.exit = None
        self.parse_entities()
        if self.floor > 2:
            self.victory = True
            self.game_over = True

    def draw(self, screen):
        # 绘制地图
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                rect = pygame.Rect(MAP_X + x * TILE_SIZE, MAP_Y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if self.map_grid[y][x] == 1:
                    pygame.draw.rect(screen, GRAY, rect)
                    pygame.draw.rect(screen, BLACK, rect, 1)
                else:
                    pygame.draw.rect(screen, DARK_GREEN, rect)
                    pygame.draw.rect(screen, BLACK, rect, 1)
        # 绘制出口
        if self.exit:
            rect = pygame.Rect(MAP_X + self.exit.x * TILE_SIZE, MAP_Y + self.exit.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, CYAN, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
        # 绘制药水
        for potion in self.potions:
            rect = pygame.Rect(MAP_X + potion.x * TILE_SIZE, MAP_Y + potion.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, GREEN, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
        # 绘制武器
        for weapon in self.weapons:
            rect = pygame.Rect(MAP_X + weapon.x * TILE_SIZE, MAP_Y + weapon.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, BROWN, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
        # 绘制敌人
        for enemy in self.enemies:
            rect = pygame.Rect(MAP_X + enemy.x * TILE_SIZE, MAP_Y + enemy.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, RED, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
        # 绘制玩家
        rect = pygame.Rect(MAP_X + self.player.x * TILE_SIZE, MAP_Y + self.player.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, BLUE, rect)
        pygame.draw.rect(screen, BLACK, rect, 1)
        # 绘制HUD
        self.draw_hud(screen)

    def draw_hud(self, screen):
        font = pygame.font.SysFont(None, 28)
        info = [
            f"Floor: {self.floor}",
            f"HP: {self.player.hp}/{self.player.max_hp}",
            f"ATK: {self.player.atk}",
            f"LV: {self.player.lv}",
            f"EXP: {self.player.exp}/{EXP_TO_LEVEL}"
        ]
        for i, text in enumerate(info):
            surf = font.render(text, True, WHITE)
            screen.blit(surf, (10, 10 + i * 25))
        if self.game_over:
            if self.victory:
                msg = "Victory! Press R to Restart"
            else:
                msg = "Game Over! Press R to Restart"
            surf = font.render(msg, True, YELLOW)
            screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, HEIGHT - 40))

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_hp = PLAYER_HP
        self.hp = self.max_hp
        self.atk = PLAYER_ATK
        self.lv = PLAYER_LV
        self.exp = PLAYER_EXP

    def level_up(self):
        self.lv += 1
        self.exp -= EXP_TO_LEVEL
        self.max_hp += 5
        self.hp = self.max_hp
        self.atk += 1
        if self.exp >= EXP_TO_LEVEL:
            self.level_up()

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = ENEMY_HP
        self.atk = ENEMY_ATK

    def move_towards(self, player, map_grid):
        dx = dy = 0
        if abs(self.x - player.x) > abs(self.y - player.y):
            if self.x < player.x:
                dx = 1
            elif self.x > player.x:
                dx = -1
        else:
            if self.y < player.y:
                dy = 1
            elif self.y > player.y:
                dy = -1
        new_x = self.x + dx
        new_y = self.y + dy
        if map_grid[new_y][new_x] == 0:
            # 检查是否与其他敌人重叠
            self.x = new_x
            self.y = new_y

class Potion:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Weapon:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Exit:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def main():
    game = Game()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game.reset()
                elif event.key in DIRECTIONS:
                    dx, dy = DIRECTIONS[event.key]
                    game.move_player(dx, dy)

        screen.fill(BLACK)
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()