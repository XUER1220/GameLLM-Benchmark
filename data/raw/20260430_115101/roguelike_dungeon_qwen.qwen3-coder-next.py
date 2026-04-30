import pygame
import random
import sys

# 固定种子
random.seed(42)

# 常量
WIDTH, HEIGHT = 800, 600
GRID_COLS, GRID_ROWS = 21, 15
GRID_SIZE = 32
MAP_WIDTH = GRID_COLS * GRID_SIZE  # 672
MAP_HEIGHT = GRID_ROWS * GRID_SIZE  # 480
MAP_OFFSET_X = (WIDTH - MAP_WIDTH) // 2
MAP_OFFSET_Y = (HEIGHT - MAP_HEIGHT) // 2
FPS = 60

# 颜色
COLOR_WALL = (64, 64, 64)
COLOR_FLOOR = (128, 128, 128)
COLOR_PLAYER = (0, 255, 0)
COLOR_ENEMY = (255, 0, 0)
COLOR_POTION = (0, 0, 255)
COLOR_WEAPON = (255, 215, 0)
COLOR_EXIT = (0, 255, 255)

# 游戏状态
STATE_PLAYING = 0
STATE_GAME_OVER = 1
STATE_WON = 2

# 参数常量
PLAYER_BASE_HP = 20
PLAYER_BASE_ATK = 5
PLAYER_BASE_LV = 1
PLAYER_BASE_EXP = 0
ENEMY_COUNT = 4
ENEMY_HP = 8
ENEMY_ATK = 3
POTION_COUNT = 2
WEAPON_COUNT = 1
POTION_RECOVER = 8
WEAPON_ATK_BONUS = 2
ENEMY_XP = 5
LEVEL_UP_EXP = 10
LEVEL_UP_HP = 5
LEVEL_UP_ATK = 1
LAYER_MIN = 2


class Entity:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 0
        self.atk = 0


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = PLAYER_BASE_HP
        self.max_hp = PLAYER_BASE_HP
        self.atk = PLAYER_BASE_ATK
        self.lv = PLAYER_BASE_LV
        self.exp = PLAYER_BASE_EXP


class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = ENEMY_HP
        self.atk = ENEMY_ATK


class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.type = item_type  # 'potion' or 'weapon'


class Door:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Room:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.center_x = x + w // 2
        self.center_y = y + h // 2


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        self.state = STATE_PLAYING
        self.floor = 1
        self.map = []
        self.player = None
        self.enemies = []
        self.items = []
        self.exit = None
        self.generate_level()

    def generate_level(self):
        # 重置
        self.map = [[1 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.enemies = []
        self.items = []
        self.exit = None

        # 生成房间
        rooms = []
        attempts = 0
        max_attempts = 100
        while len(rooms) < 6 and attempts < max_attempts:
            attempts += 1
            w = random.randint(3, 6)
            h = random.randint(3, 6)
            x = random.randint(1, GRID_COLS - w - 1)
            y = random.randint(1, GRID_ROWS - h - 1)
            # 确保不重叠
            overlap = False
            for r in rooms:
                if (x < r.x + r.w + 1 and x + w + 1 > r.x and
                        y < r.y + r.h + 1 and y + h + 1 > r.y):
                    overlap = True
                    break
            if not overlap:
                rooms.append(Room(x, y, w, h))
                # 清空房间区域为地板
                for row in range(y, y + h):
                    for col in range(x, x + w):
                        self.map[row][col] = 0

        # 连接房间（相邻房间间挖走廊）
        for i in range(len(rooms) - 1):
            r1 = rooms[i]
            r2 = rooms[i + 1]
            # 水平走廊
            x_start = min(r1.center_x, r2.center_x)
            x_end = max(r1.center_x, r2.center_x)
            y = r1.center_y
            for x in range(x_start, x_end + 1):
                if 0 < x < GRID_COLS - 1 and 0 < y < GRID_ROWS - 1:
                    self.map[y][x] = 0
            # 垂直走廊
            y_start = min(r1.center_y, r2.center_y)
            y_end = max(r1.center_y, r2.center_y)
            x = r2.center_x
            for y in range(y_start, y_end + 1):
                if 0 < x < GRID_COLS - 1 and 0 < y < GRID_ROWS - 1:
                    self.map[y][x] = 0

        # 确保边界是墙
        for row in range(GRID_ROWS):
            self.map[row][0] = 1
            self.map[row][GRID_COLS - 1] = 1
        for col in range(GRID_COLS):
            self.map[0][col] = 1
            self.map[GRID_ROWS - 1][col] = 1

        # 放置玩家（第一个房间中心）
        self.player = Player(rooms[0].center_x, rooms[0].center_y)

        # 放置出口（最后一个房间中心）
        self.exit = Door(rooms[-1].center_x, rooms[-1].center_y)

        # 放置敌人（避开玩家和出口）
        for _ in range(ENEMY_COUNT):
            placed = False
            while not placed:
                room = random.choice(rooms)
                ex = random.randint(room.x, room.x + room.w - 1)
                ey = random.randint(room.y, room.y + room.h - 1)
                if (ex != self.player.x or ey != self.player.y) and (ex != self.exit.x or ey != self.exit.y):
                    # 检查是否已有敌人
                    if not any(e.x == ex and e.y == ey for e in self.enemies):
                        self.enemies.append(Enemy(ex, ey))
                        placed = True

        # 放置药水
        for _ in range(POTION_COUNT):
            placed = False
            while not placed:
                room = random.choice(rooms)
                ix = random.randint(room.x, room.x + room.w - 1)
                iy = random.randint(room.y, room.y + room.h - 1)
                if (ix != self.player.x or iy != self.player.y) and (ix != self.exit.x or iy != self.exit.y):
                    # 检查是否已有物品
                    if not any(item.x == ix and item.y == iy for item in self.items):
                        self.items.append(Item(ix, iy, 'potion'))
                        placed = True

        # 放置武器
        for _ in range(WEAPON_COUNT):
            placed = False
            while not placed:
                room = random.choice(rooms)
                ix = random.randint(room.x, room.x + room.w - 1)
                iy = random.randint(room.y, room.y + room.h - 1)
                if (ix != self.player.x or iy != self.player.y) and (ix != self.exit.x or iy != self.exit.y):
                    # 检查是否已有物品
                    if not any(item.x == ix and item.y == iy for item in self.items):
                        self.items.append(Item(ix, iy, 'weapon'))
                        placed = True

    def move_player(self, dx, dy):
        if self.state != STATE_PLAYING:
            return

        nx, ny = self.player.x + dx, self.player.y + dy
        # 检查边界和墙壁
        if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS and self.map[ny][nx] == 0:
            # 碰到敌人？自动攻击最近的敌人
            target = None
            for enemy in self.enemies:
                if abs(enemy.x - nx) + abs(enemy.y - ny) == 1:
                    target = enemy
                    break
            if target:
                self.attack_enemies(target)
            else:
                # 碰到道具？
                for item in self.items[:]:
                    if item.x == nx and item.y == ny:
                        if item.type == 'potion':
                            self.player.hp = min(self.player.hp + POTION_RECOVER, self.player.max_hp)
                        elif item.type == 'weapon':
                            self.player.atk += WEAPON_ATK_BONUS
                        self.items.remove(item)
                        break  # 拾取一个物品
                # 移动玩家
                self.player.x, self.player.y = nx, ny
                # 碰到出口？
                if self.player.x == self.exit.x and self.player.y == self.exit.y:
                    self.next_floor()
                    return
                # 轮到敌人行动
                self.enemy_turn()

    def attack_enemies(self, target):
        target.hp -= self.player.atk
        if target.hp <= 0:
            self.enemies.remove(target)
            self.gain_xp(ENEMY_XP)

    def gain_xp(self, xp):
        self.player.exp += xp
        if self.player.exp >= LEVEL_UP_EXP:
            self.player.exp -= LEVEL_UP_EXP
            self.player.lv += 1
            self.player.max_hp += LEVEL_UP_HP
            self.player.hp = self.player.max_hp
            self.player.atk += LEVEL_UP_ATK

    def enemy_turn(self):
        for enemy in self.enemies[:]:
            # 简单AI：靠近玩家就移动
            dx = self.player.x - enemy.x
            dy = self.player.y - enemy.y
            dist = abs(dx) + abs(dy)
            if dist == 1:
                # 攻击玩家
                self.player.hp -= enemy.atk
                if self.player.hp <= 0:
                    self.player.hp = 0
                    self.game_over()
                    return
            elif dist <= 6:  # 只在近期移动
                move_x, move_y = 0, 0
                if abs(dx) > abs(dy):
                    move_x = 1 if dx > 0 else -1
                else:
                    move_y = 1 if dy > 0 else -1
                # 检查是否可移动
                nx, ny = enemy.x + move_x, enemy.y + move_y
                if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS:
                    if self.map[ny][nx] == 0 and not any(e.x == nx and e.y == ny for e in self.enemies):
                        if not (nx == self.player.x and ny == self.player.y):  # 避免直接走到玩家身上
                            enemy.x, enemy.y = nx, ny
                # 重试另一个方向（如卡住了）
                if abs(dx) <= abs(dy):
                    if move_x == 0:
                        move_y = 1 if dy > 0 else -1
                        nx, ny = enemy.x + move_x, enemy.y + move_y
                        if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS and self.map[ny][nx] == 0 and \
                                not any(e.x == nx and e.y == ny for e in self.enemies):
                            enemy.x, enemy.y = nx, ny

    def next_floor(self):
        self.floor += 1
        if self.floor > LAYER_MIN:
            self.state = STATE_WON
        else:
            self.generate_level()

    def game_over(self):
        self.state = STATE_GAME_OVER

    def draw(self):
        self.screen.fill((0, 0, 0))
        
        # 绘制地图
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                rect = pygame.Rect(
                    MAP_OFFSET_X + col * GRID_SIZE,
                    MAP_OFFSET_Y + row * GRID_SIZE,
                    GRID_SIZE, GRID_SIZE
                )
                if self.map[row][col] == 1:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_FLOOR, rect)
        
        # 绘制出口
        if self.exit:
            rect = pygame.Rect(
                MAP_OFFSET_X + self.exit.x * GRID_SIZE,
                MAP_OFFSET_Y + self.exit.y * GRID_SIZE,
                GRID_SIZE, GRID_SIZE
            )
            pygame.draw.rect(self.screen, COLOR_EXIT, rect)
            # 绘制文字标识
            font = pygame.font.Font(None, 20)
            text = font.render("EXIT", True, (255, 255, 255))
            self.screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

        # 绘制道具
        for item in self.items:
            rect = pygame.Rect(
                MAP_OFFSET_X + item.x * GRID_SIZE,
                MAP_OFFSET_Y + item.y * GRID_SIZE,
                GRID_SIZE, GRID_SIZE
            )
            if item.type == 'potion':
                pygame.draw.rect(self.screen, COLOR_POTION, rect)
            else:  # weapon
                pygame.draw.rect(self.screen, COLOR_WEAPON, rect)

        # 绘制敌人
        for enemy in self.enemies:
            rect = pygame.Rect(
                MAP_OFFSET_X + enemy.x * GRID_SIZE,
                MAP_OFFSET_Y + enemy.y * GRID_SIZE,
                GRID_SIZE, GRID_SIZE
            )
            pygame.draw.rect(self.screen, COLOR_ENEMY, rect)

        # 绘制玩家
        rect = pygame.Rect(
            MAP_OFFSET_X + self.player.x * GRID_SIZE,
            MAP_OFFSET_Y + self.player.y * GRID_SIZE,
            GRID_SIZE, GRID_SIZE
        )
        pygame.draw.rect(self.screen, COLOR_PLAYER, rect)

        # HUD 绘制
        hud_font = pygame.font.Font(None, 24)
        stat_x = 20
        stat_y = 20
        stats = [
            f"Floor: {self.floor}",
            f"HP: {self.player.hp}/{self.player.max_hp}",
            f"ATK: {self.player.atk}",
            f"LV: {self.player.lv}",
            f"EXP: {self.player.exp}/{LEVEL_UP_EXP}",
        ]
        for stat in stats:
            text = hud_font.render(stat, True, (255, 255, 255))
            self.screen.blit(text, (stat_x, stat_y))
            stat_y += 30

        # 状态消息
        if self.state == STATE_GAME_OVER:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            font = pygame.font.Font(None, 48)
            text1 = font.render("GAME OVER", True, (255, 0, 0))
            text2 = font.render("Press R to Restart", True, (255, 255, 255))
            self.screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 2 - 50))
            self.screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2 + 50))
        elif self.state == STATE_WON:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            font = pygame.font.Font(None, 48)
            text1 = font.render("YOU WIN!", True, (0, 255, 0))
            text2 = font.render("Press R to Restart", True, (255, 255, 255))
            self.screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 2 - 50))
            self.screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in (pygame.K_r, pygame.K_R) and self.state in (STATE_GAME_OVER, STATE_WON):
                        self.reset_game()
                    elif self.state == STATE_PLAYING:
                        if event.key == pygame.K_UP:
                            self.move_player(0, -1)
                        elif event.key == pygame.K_DOWN:
                            self.move_player(0, 1)
                        elif event.key == pygame.K_LEFT:
                            self.move_player(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move_player(1, 0)

            self.clock.tick(FPS)
            self.draw()

        pygame.quit()
        sys.exit()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Roguelike Dungeon Hard")
    game = Game(screen)
    game.run()


if __name__ == "__main__":
    main()