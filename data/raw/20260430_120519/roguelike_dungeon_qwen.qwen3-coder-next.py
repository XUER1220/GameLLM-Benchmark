import pygame
import random
import sys

# 常量定义
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
TILE_SIZE = 32
MAP_COLS, MAP_ROWS = 21, 15
MAP_WIDTH_PIXELS = MAP_COLS * TILE_SIZE  # 672
MAP_HEIGHT_PIXELS = MAP_ROWS * TILE_SIZE  # 480

# 颜色定义
COLOR_WALL = (64, 64, 64)
COLOR_FLOOR = (30, 30, 30)
COLOR_PLAYER = (0, 255, 127)
COLOR_ENEMY = (255, 50, 50)
COLOR_POTION = (0, 191, 255)
COLOR_WEAPON = (255, 215, 0)
COLOR_EXIT = (238, 201, 0)
COLOR_TEXT = (255, 255, 255)
COLOR_HUD_BG = (0, 0, 0)

# 游戏参数
MAX_ROOMS = 6
MIN_ROOM_SIZE = 4
MAX_ROOM_SIZE = 8
NUM_ENEMIES = 4
NUM_POTIONS = 2
NUM_WEAPONS = 1

# 玩家初始属性
PLAYER_MAX_HP = 20
PLAYER_ATK = 5
PLAYER_LV = 1
PLAYER_EXP = 0
PLAYER_HP_GROWTH = 5
PLAYER_ATK_GROWTH = 1
PLAYER_EXP_REQ = 10
PLAYER_XP_PER_ENEMY = 5
POTION_heal = 8
WEAPON_ATK_GROWTH = 2

# 初始化Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Roguelike Dungeon Hard")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

class Room:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.center_x = x + w // 2
        self.center_y = y + h // 2

    def intersects(self, other):
        return self.x < other.x + other.w and self.x + self.w > other.x and \
               self.y < other.y + other.h and self.y + self.h > other.y

class Game:
    def __init__(self):
        random.seed(42)
        self.floor = 1
        self.game_over = False
        self.won = False
        self.player = None
        self.enemies = []
        self.items = []
        self.exit_pos = None
        self.map_data = []
        self.init_game()

    def init_game(self):
        self.generate_map()
        self.spawn_entities()
        self.update_hud()

    def generate_map(self):
        # 初始化地图全为墙
        self.map_data = [[1] * MAP_COLS for _ in range(MAP_ROWS)]
        rooms = []
        room_centers = []
        
        # 生成房间
        min_attempts = MAX_ROOMS * 5
        attempts = 0
        while len(rooms) < MAX_ROOMS and attempts < min_attempts:
            attempts += 1
            w = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
            h = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
            x = random.randint(1, MAP_COLS - w - 1)
            y = random.randint(1, MAP_ROWS - h - 1)
            new_room = Room(x, y, w, h)
            
            failed = False
            for other in rooms:
                if new_room.intersects(other):
                    failed = True
                    break
            
            if not failed:
                rooms.append(new_room)
                room_centers.append((new_room.center_x, new_room.center_y))
                # 切除房间区域
                for i in range(y, y + h):
                    for j in range(x, x + w):
                        self.map_data[i][j] = 0
        
        # 如果房间数不足，补充房间
        while len(rooms) < 3:
            w = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
            h = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
            x = random.randint(1, MAP_COLS - w - 1)
            y = random.randint(1, MAP_ROWS - h - 1)
            new_room = Room(x, y, w, h)
            failed = False
            for other in rooms:
                if new_room.intersects(other):
                    failed = True
                    break
            if not failed:
                rooms.append(new_room)
                room_centers.append((new_room.center_x, new_room.center_y))
                for i in range(y, y + h):
                    for j in range(x, x + w):
                        self.map_data[i][j] = 0
        
        # 连接房间（按顺序连接）
        for i in range(len(rooms) - 1):
            x1, y1 = rooms[i].center_x, rooms[i].center_y
            x2, y2 = rooms[i + 1].center_x, rooms[i + 1].center_y
            
            # 先水平后垂直挖掘
            if random.random() < 0.5:
                self.create_h_tunnel(x1, x2, y1)
                self.create_v_tunnel(y1, y2, x2)
            else:
                self.create_v_tunnel(y1, y2, x1)
                self.create_h_tunnel(x1, x2, y2)
        
        # 确保地图至少有一个出口
        self.exit_pos = room_centers[-1][:]

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.map_data[y][x] = 0

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.map_data[y][x] = 0

    def spawn_entities(self):
        # 放置玩家在第一个房间中心
        first_room = self.get_room_containing_tile(1, 1)
        if first_room is None:
            # 如果无法确定房间，就用 (2,2)
            player_pos = (2, 2)
        else:
            player_pos = (first_room.center_x, first_room.center_y)
        
        self.player = {
            "x": player_pos[0],
            "y": player_pos[1],
            "hp": PLAYER_MAX_HP,
            "max_hp": PLAYER_MAX_HP,
            "atk": PLAYER_ATK,
            "lv": PLAYER_LV,
            "exp": PLAYER_EXP,
            "next_lv_exp": PLAYER_EXP_REQ
        }
        
        # 放置敌人
        self.enemies = []
        enemies_spawned = 0
        attempts = 0
        while enemies_spawned < NUM_ENEMIES and attempts < 200:
            attempts += 1
            x = random.randint(1, MAP_COLS - 2)
            y = random.randint(1, MAP_ROWS - 2)
            if self.map_data[y][x] == 0 and (x, y) != (self.player["x"], self.player["y"]) and \
               not any(e["x"] == x and e["y"] == y for e in self.enemies):
                self.enemies.append({
                    "x": x,
                    "y": y,
                    "hp": 8,
                    "atk": 3,
                    "dead": False
                })
                enemies_spawned += 1
        
        # 放置药水
        items_spawned = 0
        attempts = 0
        while items_spawned < NUM_POTIONS and attempts < 200:
            attempts += 1
            x = random.randint(1, MAP_COLS - 2)
            y = random.randint(1, MAP_ROWS - 2)
            if self.map_data[y][x] == 0 and (x, y) != (self.player["x"], self.player["y"]) and \
               not any(e["x"] == x and e["y"] == y for e in self.enemies if not e["dead"]) and \
               not any(item["x"] == x and item["y"] == y and item["type"] != "weapon" for item in self.items):
                self.items.append({
                    "x": x,
                    "y": y,
                    "type": "potion",
                    "collected": False
                })
                items_spawned += 1
        
        # 放置武器
        attempts = 0
        while attempts < 200:
            attempts += 1
            x = random.randint(1, MAP_COLS - 2)
            y = random.randint(1, MAP_ROWS - 2)
            if self.map_data[y][x] == 0 and (x, y) != (self.player["x"], self.player["y"]) and \
               not any(e["x"] == x and e["y"] == y for e in self.enemies if not e["dead"]) and \
               not any(item["x"] == x and item["y"] == y and item["type"] == "weapon" for item in self.items):
                self.items.append({
                    "x": x,
                    "y": y,
                    "type": "weapon",
                    "collected": False
                })
                break
        
        # 设置出口
        attempts = 0
        last_room = rooms[-1]
        while attempts < 200:
            attempts += 1
            # 尝试把出口放在最后一个房间的某个位置
            x = random.randint(last_room.x, last_room.x + last_room.w - 1)
            y = random.randint(last_room.y, last_room.y + last_room.h - 1)
            if self.map_data[y][x] == 0 and (x, y) != (self.player["x"], self.player["y"]) and \
               not any(e["x"] == x and e["y"] == y for e in self.enemies if not e["dead"]) and \
               not any(item["x"] == x and item["y"] == y for item in self.items):
                self.exit_pos = (x, y)
                break
        else:
            # 如果找不到合适位置，则找第一个空位
            for y in range(1, MAP_ROWS - 1):
                for x in range(1, MAP_COLS - 1):
                    if self.map_data[y][x] == 0 and (x, y) != (self.player["x"], self.player["y"]) and \
                       not any(e["x"] == x and e["y"] == y for e in self.enemies if not e["dead"]) and \
                       not any(item["x"] == x and item["y"] == y for item in self.items):
                        self.exit_pos = (x, y)
                        break
                if self.exit_pos is not None:
                    break

    def get_room_containing_tile(self, x, y):
        for room in self.rooms:
            if room.x <= x < room.x + room.w and room.y <= y < room.y + room.h:
                return room
        return None

    def update_hud(self):
        pass  # 目前仅用于保持结构完整

    def move_player(self, dx, dy):
        if self.game_over or self.won:
            return
        
        new_x = self.player["x"] + dx
        new_y = self.player["y"] + dy
        
        # 检查边界和墙
        if new_x < 0 or new_x >= MAP_COLS or new_y < 0 or new_y >= MAP_ROWS or self.map_data[new_y][new_x] == 1:
            return
        
        # 检查敌人阻挡
        enemy_index = None
        for idx, enemy in enumerate(self.enemies):
            if not enemy["dead"] and enemy["x"] == new_x and enemy["y"] == new_y:
                enemy_index = idx
                break
        
        if enemy_index is not None:
            self.player_attack(enemy_index)
        else:
            self.player["x"] = new_x
            self.player["y"] = new_y
            self.handle_item_pickup()
            self.move_enemies()

    def player_attack(self, enemy_index):
        enemy = self.enemies[enemy_index]
        if enemy["dead"]:
            return
        damage = self.player["atk"]
        enemy["hp"] -= damage
        if enemy["hp"] <= 0:
            enemy["dead"] = True
            self.player["exp"] += PLAYER_XP_PER_ENEMY
            self.check_level_up()
        self.move_enemies()

    def handle_item_pickup(self):
        for item in self.items:
            if not item["collected"] and item["x"] == self.player["x"] and item["y"] == self.player["y"]:
                item["collected"] = True
                if item["type"] == "potion":
                    self.player["hp"] = min(self.player["hp"] + POTION_heal, self.player["max_hp"])
                elif item["type"] == "weapon":
                    self.player["atk"] += WEAPON_ATK_GROWTH
        
        if self.player["x"] == self.exit_pos[0] and self.player["y"] == self.exit_pos[1]:
            self.next_floor()

    def check_level_up(self):
        if self.player["exp"] >= self.player["next_lv_exp"]:
            self.player["lv"] += 1
            self.player["max_hp"] += PLAYER_HP_GROWTH
            self.player["hp"] = self.player["max_hp"]
            self.player["atk"] += PLAYER_ATK_GROWTH
            self.player["exp"] = 0
            self.player["next_lv_exp"] = int(self.player["next_lv_exp"] * 1.2)

    def move_enemies(self):
        for enemy in self.enemies:
            if enemy["dead"]:
                continue
            dx = self.player["x"] - enemy["x"]
            dy = self.player["y"] - enemy["y"]
            move_x, move_y = 0, 0
            
            # 距离很近直接攻击
            if abs(dx) + abs(dy) <= 1:
                self.enemy_attack(enemy)
            else:
                # 简单移动逻辑：优先修正较大距离的轴
                if abs(dx) > abs(dy):
                    move_x = 1 if dx > 0 else -1
                else:
                    move_y = 1 if dy > 0 else -1
                
                new_x = enemy["x"] + move_x
                new_y = enemy["y"] + move_y
                
                # 检查是否可以移动
                if 0 <= new_x < MAP_COLS and 0 <= new_y < MAP_ROWS and \
                   self.map_data[new_y][new_x] == 0 and \
                   not any(e["x"] == new_x and e["y"] == new_y and not e["dead"] for e in self.enemies if e != enemy) and \
                   not (new_x == self.player["x"] and new_y == self.player["y"]):
                    enemy["x"] = new_x
                    enemy["y"] = new_y
                else:
                    # 尝试另一个方向
                    if move_x != 0:
                        move_x = 0
                        move_y = 1 if dy > 0 else -1
                    else:
                        move_x = 1 if dx > 0 else -1
                        move_y = 0
                    
                    new_x = enemy["x"] + move_x
                    new_y = enemy["y"] + move_y
                    if 0 <= new_x < MAP_COLS and 0 <= new_y < MAP_ROWS and \
                       self.map_data[new_y][new_x] == 0 and \
                       not any(e["x"] == new_x and e["y"] == new_y and not e["dead"] for e in self.enemies if e != enemy) and \
                       not (new_x == self.player["x"] and new_y == self.player["y"]):
                        enemy["x"] = new_x
                        enemy["y"] = new_y

    def enemy_attack(self, enemy):
        damage = enemy["atk"]
        self.player["hp"] -= damage
        if self.player["hp"] <= 0:
            self.player["hp"] = 0
            self.game_over = True

    def next_floor(self):
        self.floor += 1
        self.generate_map()
    
    def draw(self):
        screen.fill(COLOR_HUD_BG)
        
        # 计算地图绘制偏移
        map_x = (WINDOW_WIDTH - MAP_WIDTH_PIXELS) // 2
        map_y = (WINDOW_HEIGHT - MAP_HEIGHT_PIXELS) // 2
        
        # 绘制地图
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                if self.map_data[y][x] == 1:
                    pygame.draw.rect(screen, COLOR_WALL,
                                     (map_x + x * TILE_SIZE, map_y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                else:
                    pygame.draw.rect(screen, COLOR_FLOOR,
                                     (map_x + x * TILE_SIZE, map_y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                    # 地面稍微点缀
                    if (x + y) % 7 == 0:
                        pygame.draw.rect(screen, (50, 50, 50),
                                         (map_x + x * TILE_SIZE + 8, map_y + y * TILE_SIZE + 8, 4, 4))
        
        # 绘制物品
        for item in self.items:
            if not item["collected"]:
                if item["type"] == "potion":
                    pygame.draw.circle(screen, COLOR_POTION,
                                       (map_x + item["x"] * TILE_SIZE + TILE_SIZE // 2,
                                        map_y + item["y"] * TILE_SIZE + TILE_SIZE // 2),
                                       TILE_SIZE // 4)
                elif item["type"] == "weapon":
                    pygame.draw.rect(screen, COLOR_WEAPON,
                                     (map_x + item["x"] * TILE_SIZE + 8,
                                      map_y + item["y"] * TILE_SIZE + 8, TILE_SIZE - 16, TILE_SIZE - 16))
        
        # 绘制出口
        if self.exit_pos:
            pygame.draw.rect(screen, COLOR_EXIT,
                             (map_x + self.exit_pos[0] * TILE_SIZE + 4,
                              map_y + self.exit_pos[1] * TILE_SIZE + 4, TILE_SIZE - 8, TILE_SIZE - 8))
        
        # 绘制敌人
        for enemy in self.enemies:
            if not enemy["dead"]:
                pygame.draw.rect(screen, COLOR_ENEMY,
                                 (map_x + enemy["x"] * TILE_SIZE + 2,
                                  map_y + enemy["y"] * TILE_SIZE + 2, TILE_SIZE - 4, TILE_SIZE - 4))
        
        # 绘制玩家
        pygame.draw.rect(screen, COLOR_PLAYER,
                         (map_x + self.player["x"] * TILE_SIZE,
                          map_y + self.player["y"] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        
        # HUD区域
        hud_y = map_y + MAP_HEIGHT_PIXELS + 10
        hud_text = [
            f"HP: {self.player['hp']}/{self.player['max_hp']}",
            f"ATK: {self.player['atk']}",
            f"LV: {self.player['lv']}",
            f"EXP: {self.player['exp']}/{self.player['next_lv_exp']}",
            f"Floor: {self.floor}",
        ]
        
        for i, line in enumerate(hud_text):
            text = font.render(line, True, COLOR_TEXT)
            screen.blit(text, (10, hud_y + i * 30))
        
        # 消息和状态显示
        status_y = hud_y + len(hud_text) * 30 + 10
        
        if self.game_over:
            text = font.render("GAME OVER - Press R to Restart", True, (255, 0, 0))
            center_x = (WINDOW_WIDTH - text.get_width()) // 2
            screen.blit(text, (center_x, status_y))
        elif self.won:
            text = font.render("YOU WON! - Press R to Restart", True, (0, 255, 0))
            center_x = (WINDOW_WIDTH - text.get_width()) // 2
            screen.blit(text, (center_x, status_y))
        
        # 提示信息
        if not self.game_over and not self.won:
            tip = font.render("Arrow Keys: Move/R:Restart/ESC:Quit", True, (200, 200, 200))
            screen.blit(tip, (10, status_y))
        
        pygame.display.flip()

# 主逻辑
game = Game()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r and (game.game_over or game.won):
                game = Game()
            elif not game.game_over and not game.won:
                if event.key == pygame.K_UP:
                    game.move_player(0, -1)
                elif event.key == pygame.K_DOWN:
                    game.move_player(0, 1)
                elif event.key == pygame.K_LEFT:
                    game.move_player(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    game.move_player(1, 0)
    
    game.draw()
    clock.tick(60)

pygame.quit()
sys.exit()