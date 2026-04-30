import pygame
import random
import sys

# 固定参数
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_COLS = 21
GRID_ROWS = 15
GRID_SIZE = 32
MAP_WIDTH_PX = GRID_COLS * GRID_SIZE  # 672
MAP_HEIGHT_PX = GRID_ROWS * GRID_SIZE  # 480
MAP_X_OFFSET = (SCREEN_WIDTH - MAP_WIDTH_PX) // 2
MAP_Y_OFFSET = (SCREEN_HEIGHT - MAP_HEIGHT_PX) // 2

FPS = 60
SEED = 42

# 颜色定义
COLOR_WALL = (64, 64, 64)
COLOR_FLOOR = (192, 192, 192)
COLOR_PLAYER = (0, 0, 255)
COLOR_ENEMY = (255, 0, 0)
COLOR_POTION = (0, 255, 0)
COLOR_WEAPON = (255, 165, 0)
COLOR_EXIT = (0, 255, 255)

# 游戏常量
PLAYER_BASE_HP = 20
PLAYER_BASE_ATK = 5
PLAYER_BASE_LV = 1
PLAYER_BASE_EXP = 0
PLAYER_EXP_LIMIT = 10
PLAYER_LV_HP_GAIN = 5
PLAYER_LV_ATK_GAIN = 1

ENEMY_COUNT = 4
ENEMY_BASE_HP = 8
ENEMY_BASE_ATK = 3
ENEMY_EXP_GIVEN = 5

POTION_COUNT = 2
POTION_HP_HEAL = 8

WEAPON_COUNT = 1
WEAPON_ATK_GAIN = 2

# 游戏状态
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Roguelike Dungeon Hard")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)
        self.reset_game()

    def reset_game(self):
        random.seed(SEED)
        self.floor = 1
        self.player = {
            "x": 0,
            "y": 0,
            "hp": PLAYER_BASE_HP,
            "max_hp": PLAYER_BASE_HP,
            "atk": PLAYER_BASE_ATK,
            "lv": PLAYER_BASE_LV,
            "exp": PLAYER_BASE_EXP,
        }
        self.map_data = []
        self.enemies = []
        self.items = []
        self.exit_loc = None
        self.game_over = False
        self.victory = False
        self.message = ""
        self.generate_level()

    def generate_level(self):
        # 初始化地图（全墙壁）
        self.map_data = [[1] * GRID_COLS for _ in range(GRID_ROWS)]

        # 房间生成（6个房间）
        rooms = []
        room_count = 6
        for _ in range(room_count):
            w = random.randint(3, 7)
            h = random.randint(3, 5)
            x = random.randint(1, GRID_COLS - w - 1)
            y = random.randint(1, GRID_ROWS - h - 1)
            # 避免重叠太多：检查与已有房间重叠面积（简化为不完全重叠即可）
            overlap = False
            for r in rooms:
                if abs(r["x"] - x) < (r["w"] + w) and abs(r["y"] - y) < (r["h"] + h):
                    overlap = True
                    break
            if not overlap:
                rooms.append({"x": x, "y": y, "w": w, "h": h})

        # 切除房间区域为地板
        for room in rooms:
            for y in range(room["y"], room["y"] + room["h"]):
                for x in range(room["x"], room["x"] + room["w"]):
                    self.map_data[y][x] = 0

        # 构建连接路径：按房间顺序用走廊连接相邻房间中心
        centers = []
        for room in rooms:
            cx = room["x"] + room["w"] // 2
            cy = room["y"] + room["h"] // 2
            centers.append((cx, cy))

        for i in range(len(centers) - 1):
            x1, y1 = centers[i]
            x2, y2 = centers[i + 1]
            # 水平走廊
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.map_data[y1][x] = 0
            # 垂直走廊
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.map_data[y][x2] = 0

        # 确定玩家出生位置：第一个房间中心
        if rooms:
            start_room = rooms[0]
            self.player["x"] = start_room["x"] + start_room["w"] // 2
            self.player["y"] = start_room["y"] + start_room["h"] // 2
        else:
            self.player["x"] = 1
            self.player["y"] = 1

        # 生成敌人（4个）
        self.enemies = []
        enemy_positions = []
        attempts = 0
        while len(self.enemies) < ENEMY_COUNT and attempts < 100:
            attempts += 1
            x = random.randint(1, GRID_COLS - 2)
            y = random.randint(1, GRID_ROWS - 2)
            # 保证是地板且不是玩家位置且不与已有敌人重叠
            if self.map_data[y][x] == 0 and (x != self.player["x"] or y != self.player["y"]):
                exists = any(e["x"] == x and e["y"] == y for e in self.enemies)
                if not exists:
                    enemy_positions.append((x, y))
                    self.enemies.append({
                        "x": x,
                        "y": y,
                        "hp": ENEMY_BASE_HP,
                        "atk": ENEMY_BASE_ATK,
                    })

        # 生成药水（2个）
        self.items = []
        attempts = 0
        while len([i for i in self.items if i["type"] == "potion"]) < POTION_COUNT and attempts < 100:
            attempts += 1
            x = random.randint(1, GRID_COLS - 2)
            y = random.randint(1, GRID_ROWS - 2)
            if self.map_data[y][x] == 0 and not (x == self.player["x"] and y == self.player["y"]):
                exists = any(e["x"] == x and e["y"] == y for e in self.enemies)
                exists = exists or any(i["x"] == x and i["y"] == y for i in self.items)
                if not exists:
                    self.items.append({"x": x, "y": y, "type": "potion"})

        # 生成武器（1个）
        attempts = 0
        while len([i for i in self.items if i["type"] == "weapon"]) < WEAPON_COUNT and attempts < 100:
            attempts += 1
            x = random.randint(1, GRID_COLS - 2)
            y = random.randint(1, GRID_ROWS - 2)
            if self.map_data[y][x] == 0 and not (x == self.player["x"] and y == self.player["y"]):
                exists = any(e["x"] == x and e["y"] == y for e in self.enemies)
                exists = exists or any(i["x"] == x and i["y"] == y for i in self.items)
                if not exists:
                    self.items.append({"x": x, "y": y, "type": "weapon"})

        # 出口位置：最后一个房间中心或随机空地（确保不与敌人/物品/玩家重叠）
        if rooms:
            exit_room = rooms[-1]
            x = exit_room["x"] + exit_room["w"] // 2
            y = exit_room["y"] + exit_room["h"] // 2
        else:
            # fallback
            x = GRID_COLS - 2
            y = GRID_ROWS - 2

        # 确保出口位置合法（地板且空闲）
        attempts = 0
        while self.map_data[y][x] != 0 or (x == self.player["x"] and y == self.player["y"]) or \
              any(e["x"] == x and e["y"] == y for e in self.enemies) or \
              any(i["x"] == x and i["y"] == y for i in self.items):
            attempts += 1
            if attempts > 500:
                # 强制找一个空地
                while True:
                    x = random.randint(1, GRID_COLS - 2)
                    y = random.randint(1, GRID_ROWS - 2)
                    if self.map_data[y][x] == 0:
                        break
            else:
                x = random.randint(1, GRID_COLS - 2)
                y = random.randint(1, GRID_ROWS - 2)

        self.exit_loc = (x, y)

    def update_enemies(self):
        # 回合制：所有敌人逐一行动
        for enemy in self.enemies:
            # 与玩家相邻则攻击
            if abs(enemy["x"] - self.player["x"]) + abs(enemy["y"] - self.player["y"]) == 1:
                self.player["hp"] -= enemy["atk"]
                continue

            # 否则尝试向玩家移动一格（曼哈顿距离）
            dx = self.player["x"] - enemy["x"]
            dy = self.player["y"] - enemy["y"]
            new_x, new_y = enemy["x"], enemy["y"]

            # 优先水平/垂直移动
            move_options = []
            if dx > 0:
                move_options.append((1, 0))
            elif dx < 0:
                move_options.append((-1, 0))
            if dy > 0:
                move_options.append((0, 1))
            elif dy < 0:
                move_options.append((0, -1))

            # 若无法直接朝向玩家，则随机合法移动
            if not move_options:
                move_options = [(0, 1), (0, -1), (1, 0), (-1, 0)]

            random.shuffle(move_options)
            for dx2, dy2 in move_options:
                nx, ny = enemy["x"] + dx2, enemy["y"] + dy2
                if self.map_data[ny][nx] == 0:
                    # 检查是否踩玩家或敌人
                    if not (nx == self.player["x"] and ny == self.player["y"]):
                        occupied_by_other = any(e["x"] == nx and e["y"] == ny for e in self.enemies if e is not enemy)
                        if not occupied_by_other:
                            if dx2 != 0 or dy2 != 0:  # 仅更新位置
                                enemy["x"] = nx
                                enemy["y"] = ny
                            break

    def move_player(self, dx, dy):
        if self.game_over or self.victory:
            return

        new_x = self.player["x"] + dx
        new_y = self.player["y"] + dy

        # 边界检查与墙壁检查
        if 0 <= new_x < GRID_COLS and 0 <= new_y < GRID_ROWS and self.map_data[new_y][new_x] == 0:
            # 遇敌人则攻击
           enemy_hit = None
            for enemy in self.enemies:
                if enemy["x"] == new_x and enemy["y"] == new_y:
                    enemy_hit = enemy
                    break

            if enemy_hit:
                # 玩家攻击敌人
                enemy_hit["hp"] -= self.player["atk"]
                if enemy_hit["hp"] <= 0:
                    self.enemies.remove(enemy_hit)
                    self.player["exp"] += ENEMY_EXP_GIVEN
                    self.check_level_up()
                self.update_enemies()
                return

            # 移动玩家
            self.player["x"] = new_x
            self.player["y"] = new_y

            # 检查拾取物品
            for i, item in enumerate(self.items):
                if item["x"] == new_x and item["y"] == new_y:
                    if item["type"] == "potion":
                        self.player["hp"] = min(self.player["max_hp"], self.player["hp"] + POTION_HP_HEAL)
                    elif item["type"] == "weapon":
                        self.player["atk"] += WEAPON_ATK_GAIN
                    self.items.pop(i)
                    break

            # 检查是否到达出口
            if new_x == self.exit_loc[0] and new_y == self.exit_loc[1]:
                self.floor += 1
                if self.floor > 2:
                    self.victory = True
                    self.message = f"Victory! You cleared {self.floor - 1} floors."
                else:
                    self.generate_level()
                return

            # 敌人行动
            self.update_enemies()

        # 检查玩家是否死亡
        if self.player["hp"] <= 0:
            self.player["hp"] = 0
            self.game_over = True

    def check_level_up(self):
        if self.player["exp"] >= PLAYER_EXP_LIMIT:
            self.player["lv"] += 1
            self.player["max_hp"] += PLAYER_LV_HP_GAIN
            self.player["hp"] = self.player["max_hp"]
            self.player["atk"] += PLAYER_LV_ATK_GAIN
            self.player["exp"] = 0

    def draw(self):
        self.screen.fill((0, 0, 0))

        # 绘制地图
        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                rect = (MAP_X_OFFSET + x * GRID_SIZE, MAP_Y_OFFSET + y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                if self.map_data[y][x] == 1:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_FLOOR, rect)

        # 绘制出口
        ex, ey = self.exit_loc
        rect = (MAP_X_OFFSET + ex * GRID_SIZE + 4, MAP_Y_OFFSET + ey * GRID_SIZE + 4, GRID_SIZE - 8, GRID_SIZE - 8)
        pygame.draw.rect(self.screen, COLOR_EXIT, rect)

        # 绘制物品
        for item in self.items:
            rect = (MAP_X_OFFSET + item["x"] * GRID_SIZE + 4, MAP_Y_OFFSET + item["y"] * GRID_SIZE + 4, GRID_SIZE - 8, GRID_SIZE - 8)
            color = COLOR_POTION if item["type"] == "potion" else COLOR_WEAPON
            pygame.draw.rect(self.screen, color, rect)

        # 绘制敌人
        for enemy in self.enemies:
            rect = (MAP_X_OFFSET + enemy["x"] * GRID_SIZE + 4, MAP_Y_OFFSET + enemy["y"] * GRID_SIZE + 4, GRID_SIZE - 8, GRID_SIZE - 8)
            pygame.draw.rect(self.screen, COLOR_ENEMY, rect)

        # 绘制玩家
        px, py = self.player["x"], self.player["y"]
        rect = (MAP_X_OFFSET + px * GRID_SIZE + 4, MAP_Y_OFFSET + py * GRID_SIZE + 4, GRID_SIZE - 8, GRID_SIZE - 8)
        pygame.draw.rect(self.screen, COLOR_PLAYER, rect)

        # HUD: 属性面板（左侧）
        hud_x = 20
        y_offset = 30
        texts = [
            f"Floor: {self.floor}",
            f"HP: {self.player['hp']} / {self.player['max_hp']}",
            f"ATK: {self.player['atk']}",
            f"Level: {self.player['lv']}",
            f"EXP: {self.player['exp']} / {PLAYER_EXP_LIMIT}",
        ]
        for text in texts:
            label = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(label, (hud_x, y_offset))
            y_offset += 30

        # 游戏状态消息（右侧或底部）
        if self.game_over:
            text1 = self.font.render("Game Over", True, (255, 0, 0))
            text2 = self.font.render("Press R to Restart", True, (255, 255, 255))
            self.screen.blit(text1, (MAP_X_OFFSET + MAP_WIDTH_PX // 2 - 60, MAP_Y_OFFSET + MAP_HEIGHT_PX // 2 - 20))
            self.screen.blit(text2, (MAP_X_OFFSET + MAP_WIDTH_PX // 2 - 120, MAP_Y_OFFSET + MAP_HEIGHT_PX // 2 + 10))
        elif self.victory:
            text1 = self.font.render(self.message, True, (0, 255, 0))
            text2 = self.font.render("Press R to Restart", True, (255, 255, 255))
            self.screen.blit(text1, (MAP_X_OFFSET + MAP_WIDTH_PX // 2 - 80, MAP_Y_OFFSET + MAP_HEIGHT_PX // 2 - 20))
            self.screen.blit(text2, (MAP_X_OFFSET + MAP_WIDTH_PX // 2 - 120, MAP_Y_OFFSET + MAP_HEIGHT_PX // 2 + 10))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif not self.game_over and not self.victory:
                        if event.key == pygame.K_UP:
                            self.move_player(0, -1)
                        elif event.key == pygame.K_DOWN:
                            self.move_player(0, 1)
                        elif event.key == pygame.K_LEFT:
                            self.move_player(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move_player(1, 0)

            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()