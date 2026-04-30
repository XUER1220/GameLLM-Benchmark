import pygame
import random
import sys

# 固定常量
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_COLS = 21
GRID_ROWS = 15
GRID_SIZE = 32
MAP_WIDTH = GRID_COLS * GRID_SIZE  # 672
MAP_HEIGHT = GRID_ROWS * GRID_SIZE  # 480
FPS = 60
SEED = 42
MAX_ROOMS = 6
MIN_ROOM_SIZE = 3
MAX_ROOM_SIZE = 7
ENEMY_COUNT = 4
POTION_COUNT = 2
WEAPON_COUNT = 1
BASE_PLAYER_HP = 20
BASE_PLAYER_ATK = 5
MAX_EXP = 10
EXP_PER_ENEMY = 5
POTION_RESTORE = 8
WEAPON_BOOST = 2
ENEMY_HP = 8
ENEMY_ATK = 3
ENEMY_EXP = 0  # 不用于逻辑，保持一致性
BASE_FLOOR = 1

# 颜色
COLOR_WALL = (64, 64, 64)
COLOR_FLOOR = (220, 220, 220)
COLOR_PLAYER = (0, 255, 0)
COLOR_ENEMY = (255, 0, 0)
COLOR_POTION = (0, 0, 255)
COLOR_WEAPON = (255, 255, 0)
COLOR_EXIT = (255, 165, 0)
COLOR_HUD_BG = (0, 0, 0)
COLOR_HUD_TEXT = (255, 255, 255)
COLOR_OVERLAY_BG = (0, 0, 0, 150)

# 初始化 Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Roguelike Dungeon Hard")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)


def get_centered_map_rect():
    x = (WINDOW_WIDTH - MAP_WIDTH) // 2
    y = (WINDOW_HEIGHT - MAP_HEIGHT) // 2
    return pygame.Rect(x, y, MAP_WIDTH, MAP_HEIGHT)


class Room:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        return (self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2

    def intersects(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class Game:
    def __init__(self):
        self.floor = BASE_FLOOR
        self.player = {
            "x": 0,
            "y": 0,
            "hp": BASE_PLAYER_HP,
            "max_hp": BASE_PLAYER_HP,
            "atk": BASE_PLAYER_ATK,
            "level": 1,
            "exp": 0
        }
        self.map_data = []
        self.entities = []  # list of dicts: {'type': 'player'|'enemy'|'potion'|'weapon'|'exit', 'x': int, 'y': int}
        self.game_over = False
        self.win = False
        self.seed = SEED
        random.seed(self.seed)
        self.init_level()

    def init_level(self):
        # 生成地图
        self.map_data = [[1 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        rooms = []
        center_positions = []

        for i in range(MAX_ROOMS):
            w = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
            h = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
            x = random.randint(1, GRID_COLS - w - 1)
            y = random.randint(1, GRID_ROWS - h - 1)
            new_room = Room(x, y, w, h)
           _failed = False
            for other in rooms:
                if new_room.intersects(other):
                    _failed = True
                    break
            if _failed:
                continue
            # 铲平房间区域
            for yy in range(new_room.y1, new_room.y2):
                for xx in range(new_room.x1, new_room.x2):
                    self.map_data[yy][xx] = 0

            rooms.append(new_room)
            center_positions.append(new_room.center())

        # 连接房间（相邻房间连线）
        for i in range(len(rooms) - 1):
            cx1, cy1 = center_positions[i]
            cx2, cy2 = center_positions[i + 1]
            # 水平走廊
            for xx in range(min(cx1, cx2), max(cx1, cx2) + 1):
                self.map_data[cy1][xx] = 0
            # 垂直走廊
            for yy in range(min(cy1, cy2), max(cy1, cy2) + 1):
                self.map_data[yy][cx2] = 0

        self.entities = []
        
        # 放置玩家在第一个房间中心
        px, py = center_positions[0]
        # 如果中心不是地板，找最近的地板位置
        while self.map_data[py][px] != 0:
            px, py = px + 1, py
        self.player["x"] = px
        self.player["y"] = py
        self.entities.append({"type": "player", "x": px, "y": py})

        # 放置出口在最后一个房间中心
        ex, ey = center_positions[-1]
        while self.map_data[ey][ex] != 0:
            ex, ey = ex + 1, ey
        self.entities.append({"type": "exit", "x": ex, "y": ey})

        # 放置敌人
        enemies_placed = 0
        placed_positions = {(px, py), (ex, ey)}
        while enemies_placed < ENEMY_COUNT:
            cx = random.randint(1, GRID_COLS - 2)
            cy = random.randint(1, GRID_ROWS - 2)
            if (cx, cy) not in placed_positions and self.map_data[cy][cx] == 0:
                self.entities.append({"type": "enemy", "x": cx, "y": cy, "hp": ENEMY_HP})
                enemies_placed += 1
                placed_positions.add((cx, cy))

        # 放置药水
        potions_placed = 0
        while potions_placed < POTION_COUNT:
            cx = random.randint(1, GRID_COLS - 2)
            cy = random.randint(1, GRID_ROWS - 2)
            if (cx, cy) not in placed_positions and self.map_data[cy][cx] == 0:
                self.entities.append({"type": "potion", "x": cx, "y": cy})
                potions_placed += 1
                placed_positions.add((cx, cy))

        # 放置武器
        weapons_placed = 0
        while weapons_placed < WEAPON_COUNT:
            cx = random.randint(1, GRID_COLS - 2)
            cy = random.randint(1, GRID_ROWS - 2)
            if (cx, cy) not in placed_positions and self.map_data[cy][cx] == 0:
                self.entities.append({"type": "weapon", "x": cx, "y": cy})
                weapons_placed += 1
                placed_positions.add((cx, cy))

    def player_move(self, dx, dy):
        if self.game_over:
            return

        px = self.player["x"] + dx
        py = self.player["y"] + dy

        # 检查边界和墙壁
        if px < 0 or px >= GRID_COLS or py < 0 or py >= GRID_ROWS:
            return
        if self.map_data[py][px] == 1:
            return

        # 检查是否存在实体阻挡（敌人）
        enemy_at_target = None
        for entity in self.entities:
            if entity["type"] == "enemy" and entity["x"] == px and entity["y"] == py:
                enemy_at_target = entity
                break

        if enemy_at_target:
            # 攻击敌人
            enemy_at_target["hp"] -= self.player["atk"]
            if enemy_at_target["hp"] <= 0:
                self.entities.remove(enemy_at_target)
                self.player["exp"] += EXP_PER_ENEMY
                self.check_level_up()
                # 经验检查和升级
            # 敌人回合（因为玩家攻击算作行动）
            self.enemy_turn()
            return

        # 移动玩家
        self.entities[0]["x"] = px
        self.entities[0]["y"] = py
        self.player["x"] = px
        self.player["y"] = py

        # 检查物品和出口
        self.handle_tile_content(px, py)
        # 敌人回合
        self.enemy_turn()

    def handle_tile_content(self, x, y):
        # 检查敌人都在 enemy_turn 处理，只处理非敌对实体
        for i in range(len(self.entities) - 1, -1, -1):
            entity = self.entities[i]
            if entity["x"] == x and entity["y"] == y:
                if entity["type"] == "potion":
                    self.player["hp"] = min(self.player["hp"] + POTION_RESTORE, self.player["max_hp"])
                    self.entities.pop(i)
                elif entity["type"] == "weapon":
                    self.player["atk"] += WEAPON_BOOST
                    self.entities.pop(i)
                elif entity["type"] == "exit":
                    self.next_floor()
                    return

    def check_level_up(self):
        if self.player["exp"] >= MAX_EXP:
            self.player["level"] += 1
            self.player["exp"] = 0
            self.player["max_hp"] += 5
            self.player["hp"] = self.player["max_hp"]
            self.player["atk"] += 1

    def enemy_turn(self):
        for entity in self.entities:
            if entity["type"] == "enemy":
                ex, ey = entity["x"], entity["y"]
                px, py = self.player["x"], self.player["y"]
                # 简单 AI：靠近玩家
                dx, dy = 0, 0
                if abs(px - ex) > abs(py - ey):
                    dx = 1 if px > ex else -1
                elif abs(py - ey) > 0:
                    dy = 1 if py > ey else -1
                else:
                    dx = 1 if px > ex else -1  # fallback

                nx, ny = ex + dx, ey + dy
                # 检查是否到达玩家位置或障碍
                if nx == px and ny == py:
                    # 攻击玩家
                    self.player["hp"] -= entity.get("atk", ENEMY_ATK)
                elif self.map_data[ny][nx] == 0 and not any(
                    e["x"] == nx and e["y"] == ny and e["type"] != "enemy" 
                    for e in self.entities
                ):
                    # 移动敌人
                    entity["x"] = nx
                    entity["y"] = ny

        # 检查玩家死亡
        if self.player["hp"] <= 0:
            self.game_over = True

    def next_floor(self):
        self.floor += 1
        random.seed(self.seed + self.floor)
        self.init_level()

    def draw(self):
        # 清屏
        screen.fill((30, 30, 30))

        # 绘制地图区域背景
        map_rect = get_centered_map_rect()
        pygame.draw.rect(screen, (200, 200, 200), map_rect)
        map_rect_inner = pygame.Rect(
            map_rect.left + 2, map_rect.top + 2,
            map_rect.width - 4, map_rect.height - 4
        )
        pygame.draw.rect(screen, (0, 0, 0), map_rect_inner)

        # 绘制地图格子
        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                if self.map_data[y][x] == 1:
                    color = COLOR_WALL
                else:
                    color = COLOR_FLOOR
                rect = pygame.Rect(map_rect.left + x * GRID_SIZE, map_rect.top + y * GRID_SIZE,
                                   GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, color, rect)

        # 绘制实体
        for entity in self.entities:
            rect = pygame.Rect(
                map_rect.left + entity["x"] * GRID_SIZE,
                map_rect.top + entity["y"] * GRID_SIZE,
                GRID_SIZE, GRID_SIZE
            )
            if entity["type"] == "player":
                pygame.draw.rect(screen, COLOR_PLAYER, rect)
            elif entity["type"] == "enemy":
                pygame.draw.rect(screen, COLOR_ENEMY, rect)
            elif entity["type"] == "potion":
                pygame.draw.circle(screen, COLOR_POTION,
                                   (rect.centerx, rect.centery), GRID_SIZE // 4)
            elif entity["type"] == "weapon":
                pygame.draw.rect(screen, COLOR_WEAPON, rect)
            elif entity["type"] == "exit":
                pygame.draw.rect(screen, COLOR_EXIT, rect)

        # 绘制 HUD
        hud_rect = pygame.Rect(0, map_rect.bottom, WINDOW_WIDTH, WINDOW_HEIGHT - map_rect.bottom)
        pygame.draw.rect(screen, COLOR_HUD_BG, hud_rect)

        # 生命值、等级、经验等信息
        hp_text = font.render(f"HP: {self.player['hp']}/{self.player['max_hp']}", True, COLOR_HUD_TEXT)
        atk_text = font.render(f"ATK: {self.player['atk']}", True, COLOR_HUD_TEXT)
        lv_text = font.render(f"LV: {self.player['level']}", True, COLOR_HUD_TEXT)
        exp_text = font.render(f"EXP: {self.player['exp']}/{MAX_EXP}", True, COLOR_HUD_TEXT)
        floor_text = font.render(f"Floor: {self.floor}", True, COLOR_HUD_TEXT)

        y_offset = hud_rect.top + 10
        screen.blit(hp_text, (10, y_offset))
        screen.blit(atk_text, (150, y_offset))
        screen.blit(lv_text, (290, y_offset))
        screen.blit(exp_text, (430, y_offset))
        screen.blit(floor_text, (570, y_offset))

        # 胜利/失败状态
        if self.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            large_font = pygame.font.SysFont(None, 48)
            game_over_text = large_font.render("GAME OVER", True, (255, 0, 0))
            restart_text = font.render("Press R to Restart", True, (255, 255, 255))
            screen.blit(game_over_text, game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)))
            screen.blit(restart_text, restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)))

        elif self.win:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            large_font = pygame.font.SysFont(None, 48)
            win_text = large_font.render("YOU WIN!", True, (0, 255, 0))
            restart_text = font.render("Press R to Restart", True, (255, 255, 255))
            screen.blit(win_text, win_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)))
            screen.blit(restart_text, restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)))

        pygame.display.flip()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        moved = False

        if keys[pygame.K_UP]:
            dy = -1
            moved = True
        elif keys[pygame.K_DOWN]:
            dy = 1
            moved = True
        elif keys[pygame.K_LEFT]:
            dx = -1
            moved = True
        elif keys[pygame.K_RIGHT]:
            dx = 1
            moved = True

        if moved:
            self.player_move(dx, dy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:
                    if self.game_over or self.win:
                        self.restart()
                        return True

        return True

    def restart(self):
        self.__init__()
        random.seed(self.seed + self.floor - BASE_FLOOR)  # 重置房间序列
        self.init_level()
        self.game_over = False
        self.win = False


def main():
    game = Game()
    running = True
    while running:
        game.draw()
        running = game.handle_input()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()