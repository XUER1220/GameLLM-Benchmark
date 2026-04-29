import pygame
import random
import sys
import math

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
MAP_COLS = 21
MAP_ROWS = 15
PLAYER_START_X = 2
PLAYER_START_Y = 2
NUM_ROOMS = 6
NUM_ENEMIES = 4
NUM_POTIONS = 2
NUM_WEAPONS = 1

# 颜色定义
COLOR_WALL = (50, 50, 50)
COLOR_FLOOR = (30, 30, 30)
COLOR_PLAYER = (0, 255, 0)
COLOR_ENEMY = (255, 0, 0)
COLOR_POTION = (0, 255, 255)
COLOR_WEAPON = (255, 255, 0)
COLOR_EXIT = (128, 0, 128)
COLOR_HUD_BG = (40, 40, 40)
COLOR_TEXT = (255, 255, 255)

# 游戏参数
MAX_HP = 20
BASE_ATK = 5
BASE_XP_REQ = 10
EXP_PER_ENEMY = 5
POTION_HEAL = 8
WEAPON_DMG_BONUS = 2
ENEMY_HP = 8
ENEMY_ATK = 3
FPS = 60

# 层级参数
MAX_FLOORS = 5
ROOM_MIN_SIZE = 3
ROOM_MAX_SIZE = 7

class Room:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center_x = x + width // 2
        self.center_y = y + height // 2

def generate_map(seed):
    random.seed(seed)
    # 初始化地图为墙
    map_data = [[1 for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
    
    # 生成房间
    rooms = []
    attempts = 0
    while len(rooms) < NUM_ROOMS and attempts < 100:
        room_w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        room_h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        room_x = random.randint(1, MAP_COLS - room_w - 1)
        room_y = random.randint(1, MAP_ROWS - room_h - 1)
        
        # 检查重叠
        overlap = False
        for r in rooms:
            if (room_x <= r.x + r.width + 1 and room_x + room_w + 1 >= r.x and
                room_y <= r.y + r.height + 1 and room_y + room_h + 1 >= r.y):
                overlap = True
                break
        
        if not overlap:
            new_room = Room(room_x, room_y, room_w, room_h)
            rooms.append(new_room)
            for y in range(room_y, room_y + room_h):
                for x in range(room_x, room_x + room_w):
                    map_data[y][x] = 0
        attempts += 1
    
    # 连接房间
    for i in range(1, len(rooms)):
        r1 = rooms[i-1]
        r2 = rooms[i]
        
        # 随机选择水平走廊先行还是垂直走廊先行
        if random.random() > 0.5:
            # 水平然后垂直
            x1 = r1.center_x
            x2 = r2.center_x
            y = r1.center_y
            
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 <= x < MAP_COLS and 0 <= y < MAP_ROWS:
                    map_data[y][x] = 0
            
            y1 = r1.center_y
            y2 = r2.center_y
            x = r2.center_x
            
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if 0 <= x < MAP_COLS and 0 <= y < MAP_ROWS:
                    map_data[y][x] = 0
        else:
            # 垂直然后水平
            y1 = r1.center_y
            y2 = r2.center_y
            x = r1.center_x
            
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if 0 <= x < MAP_COLS and 0 <= y < MAP_ROWS:
                    map_data[y][x] = 0
            
            x1 = r1.center_x
            x2 = r2.center_x
            y = r2.center_y
            
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 <= x < MAP_COLS and 0 <= y < MAP_ROWS:
                    map_data[y][x] = 0
    
    return map_data, rooms

def get_empty_tile(map_data, rooms, exclude_rooms=None):
    while True:
        # 随机选一个房间（排除 exclude_rooms）
        if exclude_rooms:
            valid_rooms = [r for i, r in enumerate(rooms) if i not in exclude_rooms]
        else:
            valid_rooms = rooms
        if not valid_rooms:
            valid_rooms = rooms
        
        room = random.choice(valid_rooms)
        x = random.randint(room.x, room.x + room.width - 1)
        y = random.randint(room.y, room.y + room.height - 1)
        
        if map_data[y][x] == 0:
            return x, y

def spawn_entities(map_data, rooms):
    entities = []
    exits = []
    items = []
    
    # 玩家位置
    player_x, player_y = get_empty_tile(map_data, rooms, [])
    
    # 出口
    exit_x, exit_y = get_empty_tile(map_data, rooms, [])
    exits.append((exit_x, exit_y))
    
    # 敌人
    for _ in range(NUM_ENEMIES):
        enemy_x, enemy_y = get_empty_tile(map_data, rooms, [])
        entities.append({"type": "enemy", "x": enemy_x, "y": enemy_y, "hp": ENEMY_HP, "atk": ENEMY_ATK})
    
    # 药水
    for _ in range(NUM_POTIONS):
        potion_x, potion_y = get_empty_tile(map_data, rooms, [])
        items.append({"type": "potion", "x": potion_x, "y": potion_y})
    
    # 武器
    weapon_x, weapon_y = get_empty_tile(map_data, rooms, [])
    items.append({"type": "weapon", "x": weapon_x, "y": weapon_y})
    
    return player_x, player_y, entities, exits, items

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Roguelike Dungeon Hard")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 18)
        
        self.reset_game()
    
    def reset_game(self):
        self.floor = 1
        self.map_data, self.rooms = generate_map(42)
        self.player_x, self.player_y, self.enemies, self.exits, self.items = spawn_entities(self.map_data, self.rooms)
        
        self.player = {
            "x": self.player_x,
            "y": self.player_y,
            "hp": MAX_HP,
            "max_hp": MAX_HP,
            "atk": BASE_ATK,
            "lvl": 1,
            "xp": 0,
            "xp_req": BASE_XP_REQ
        }
        
        self.game_state = "PLAYING"
        self.message = ""
        self.game_over_reason = ""
    
    def get_neighbors(self, x, y):
        return [
            (x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)
        ]
    
    def is_valid_move(self, x, y):
        return (0 <= x < MAP_COLS and 0 <= y < MAP_ROWS and 
                self.map_data[y][x] == 0 and 
                (x != self.player_x or y != self.player_y) and
                not any(e["x"] == x and e["y"] == y for e in self.enemies))
    
    def move_player(self, dx, dy):
        if self.game_state != "PLAYING":
            return
        
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        
        if self.is_valid_move(new_x, new_y):
            # 检查物品
            for item in self.items[:]:
                if item["x"] == new_x and item["y"] == new_y:
                    if item["type"] == "potion":
                        self.player["hp"] = min(self.player["hp"] + POTION_HEAL, self.player["max_hp"])
                        self.items.remove(item)
                    elif item["type"] == "weapon":
                        self.player["atk"] += WEAPON_DMG_BONUS
                        self.items.remove(item)
            
            # 检查出口
            for exit_pos in self.exits:
                if exit_pos[0] == new_x and exit_pos[1] == new_y:
                    self.next_floor()
                    return
            
            self.player_x = new_x
            self.player_y = new_y
            self.enemies_turn()
    
    def enemies_turn(self):
        for enemy in self.enemies[:]:
            # 检查敌人是否死亡
            if enemy["hp"] <= 0:
                self.enemies.remove(enemy)
                self.player["xp"] += EXP_PER_ENEMY
                self.check_level_up()
                continue
            
            # 玩家和敌人距离
            dx = abs(enemy["x"] - self.player_x)
            dy = abs(enemy["y"] - self.player_y)
            
            if dx + dy == 1:  # 相邻，攻击玩家
                self.player["hp"] -= max(1, enemy["atk"])
                if self.player["hp"] <= 0:
                    self.game_over()
                    return
            elif dx + dy <= 3:  # 范围内移动
                # 简单 AI：优先沿长轴移动，避开墙壁
                move_x, move_y = enemy["x"], enemy["y"]
                if dx > dy:
                    if self.player_x > enemy["x"] and self.is_valid_move(enemy["x"] + 1, enemy["y"]):
                        move_x = enemy["x"] + 1
                    elif self.player_x < enemy["x"] and self.is_valid_move(enemy["x"] - 1, enemy["y"]):
                        move_x = enemy["x"] - 1
                    else:
                        if self.player_y > enemy["y"] and self.is_valid_move(enemy["x"], enemy["y"] + 1):
                            move_y = enemy["y"] + 1
                        elif self.player_y < enemy["y"] and self.is_valid_move(enemy["x"], enemy["y"] - 1):
                            move_y = enemy["y"] - 1
                else:
                    if self.player_y > enemy["y"] and self.is_valid_move(enemy["x"], enemy["y"] + 1):
                        move_y = enemy["y"] + 1
                    elif self.player_y < enemy["y"] and self.is_valid_move(enemy["x"], enemy["y"] - 1):
                        move_y = enemy["y"] - 1
                    else:
                        if self.player_x > enemy["x"] and self.is_valid_move(enemy["x"] + 1, enemy["y"]):
                            move_x = enemy["x"] + 1
                        elif self.player_x < enemy["x"] and self.is_valid_move(enemy["x"] - 1, enemy["y"]):
                            move_x = enemy["x"] - 1
                
                enemy["x"], enemy["y"] = move_x, move_y
    
    def check_level_up(self):
        if self.player["xp"] >= self.player["xp_req"]:
            self.player["lvl"] += 1
            self.player["xp"] -= self.player["xp_req"]
            self.player["xp_req"] = int(self.player["xp_req"] * 1.2)
            self.player["max_hp"] += 5
            self.player["hp"] = self.player["max_hp"]
            self.player["atk"] += 1
    
    def next_floor(self):
        self.floor += 1
        self.map_data, self.rooms = generate_map(42 + self.floor)
        self.player_x, self.player_y, self.enemies, self.exits, self.items = spawn_entities(self.map_data, self.rooms)
        self.game_state = "PLAYING"
    
    def game_over(self):
        self.game_state = "GAME_OVER"
        self.game_over_reason = "You died!"
    
    def draw_hud(self):
        # HUD 背景
        hud_height = 70
        hud_rect = pygame.Rect(0, 0, SCREEN_WIDTH, hud_height)
        pygame.draw.rect(self.screen, COLOR_HUD_BG, hud_rect)
        
        # 玩家状态
        texts = [
            f"HP: {self.player['hp']}/{self.player['max_hp']}",
            f"ATK: {self.player['atk']}",
            f"LV: {self.player['lvl']}",
            f"EXP: {self.player['xp']}/{self.player['xp_req']}",
            f"Floor: {self.floor}"
        ]
        
        for i, text in enumerate(texts):
            text_surface = self.font.render(text, True, COLOR_TEXT)
            self.screen.blit(text_surface, (10 + i * 140, 15))
        
        # 消息
        if self.message:
            msg_surface = self.small_font.render(self.message, True, (255, 255, 0))
            self.screen.blit(msg_surface, (10, 45))
    
    def draw_map(self):
        map_width = MAP_COLS * TILE_SIZE
        map_height = MAP_ROWS * TILE_SIZE
        offset_x = (SCREEN_WIDTH - map_width) // 2
        offset_y = (SCREEN_HEIGHT - map_height) // 2
        
        # 绘制地图背景
        bg_rect = pygame.Rect(offset_x, offset_y, map_width, map_height)
        pygame.draw.rect(self.screen, (20, 20, 20), bg_rect)
        
        # 绘制房间和走廊
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                if self.map_data[y][x] == 1:
                    color = COLOR_WALL
                else:
                    color = COLOR_FLOOR
                rect = pygame.Rect(
                    offset_x + x * TILE_SIZE,
                    offset_y + y * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )
                pygame.draw.rect(self.screen, color, rect)
        
        # 绘制出口
        for ex, ey in self.exits:
            rect = pygame.Rect(
                offset_x + ex * TILE_SIZE,
                offset_y + ey * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )
            pygame.draw.rect(self.screen, COLOR_EXIT, rect)
            # 绘制箭头指示
            exit_text = self.small_font.render("EXIT", True, (255, 255, 255))
            self.screen.blit(exit_text, (rect.centerx - 15, rect.centery - 10))
        
        # 绘制物品
        for item in self.items:
            rect = pygame.Rect(
                offset_x + item["x"] * TILE_SIZE,
                offset_y + item["y"] * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )
            color = COLOR_POTION if item["type"] == "potion" else COLOR_WEAPON
            pygame.draw.circle(self.screen, color, rect.center, 8)
        
        # 绘制敌人
        for enemy in self.enemies:
            rect = pygame.Rect(
                offset_x + enemy["x"] * TILE_SIZE,
                offset_y + enemy["y"] * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )
            pygame.draw.circle(self.screen, COLOR_ENEMY, rect.center, 10)
        
        # 绘制玩家
        player_rect = pygame.Rect(
            offset_x + self.player_x * TILE_SIZE,
            offset_y + self.player_y * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE
        )
        pygame.draw.circle(self.screen, COLOR_PLAYER, player_rect.center, 10)
    
    def draw_game_over(self):
        # 黑色背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # 游戏结束文本
        if self.game_over_reason:
            text = self.font.render(self.game_over_reason, True, (255, 0, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(text, text_rect)
        
        restart_text = self.font.render("Press R to Restart", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_r and self.game_state != "PLAYING":
                        self.reset_game()
                    elif self.game_state == "PLAYING":
                        if event.key == pygame.K_UP:
                            self.move_player(0, -1)
                        elif event.key == pygame.K_DOWN:
                            self.move_player(0, 1)
                        elif event.key == pygame.K_LEFT:
                            self.move_player(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move_player(1, 0)
            
            # 绘制
            self.screen.fill((0, 0, 0))
            
            if self.game_state == "PLAYING":
                self.draw_map()
                self.draw_hud()
            else:
                self.draw_game_over()
            
            # 更新显示
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.run()