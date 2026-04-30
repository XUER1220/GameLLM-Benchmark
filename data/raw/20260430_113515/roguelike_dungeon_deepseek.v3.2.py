import pygame
import random
import sys

# 初始化
pygame.init()
random.seed(42)

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
MAP_COLS = 21
MAP_ROWS = 15
MAP_WIDTH = MAP_COLS * TILE_SIZE
MAP_HEIGHT = MAP_ROWS * TILE_SIZE
MAP_X = (SCREEN_WIDTH - MAP_WIDTH) // 2
MAP_Y = (SCREEN_HEIGHT - MAP_HEIGHT) // 2
FPS = 60

# 颜色定义
COLOR_BG = (30, 30, 40)
COLOR_GROUND = (50, 50, 60)
COLOR_WALL = (100, 100, 120)
COLOR_PLAYER = (70, 200, 70)
COLOR_ENEMY = (220, 70, 70)
COLOR_HP_POTION = (70, 200, 220)
COLOR_WEAPON = (220, 200, 70)
COLOR_EXIT = (180, 70, 220)
COLOR_HUD_BG = (40, 40, 50)
COLOR_HUD_TEXT = (240, 240, 240)
COLOR_MSG = (255, 200, 100)

# 玩家初始属性
PLAYER_HP = 20
PLAYER_ATK = 5
PLAYER_LV = 1
PLAYER_EXP = 0
PLAYER_EXP_TO_NEXT = 10

# 敌人属性
ENEMY_HP = 8
ENEMY_ATK = 3
ENEMY_COUNT = 4

# 道具效果
POTION_HEAL = 8
WEAPON_BONUS = 2
POTION_COUNT = 2
WEAPON_COUNT = 1

# 方向向量
DIRECTIONS = {'LEFT': (-1, 0), 'RIGHT': (1, 0), 'UP': (0, -1), 'DOWN': (0, 1)}

# 游戏状态
STATE_PLAYING = 0
STATE_GAME_OVER = 1
STATE_WIN = 2

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Roguelike Dungeon Hard")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 48)
        self.reset_game()

    def reset_game(self):
        self.floor = 1
        self.state = STATE_PLAYING
        self.init_player()
        self.generate_dungeon()

    def init_player(self):
        self.player_hp = PLAYER_HP
        self.player_max_hp = PLAYER_HP
        self.player_atk = PLAYER_ATK
        self.player_lv = PLAYER_LV
        self.player_exp = PLAYER_EXP
        self.player_exp_to_next = PLAYER_EXP_TO_NEXT
        self.player_pos = [0, 0]

    def generate_dungeon(self):
        self.map = [[1 for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
        rooms = []
        # 生成房间
        for _ in range(6):
            w = random.randint(3, 6)
            h = random.randint(3, 5)
            x = random.randint(1, MAP_COLS - w - 1)
            y = random.randint(1, MAP_ROWS - h - 1)
            rooms.append((x, y, w, h))
        # 绘制房间
        for rx, ry, rw, rh in rooms:
            for dy in range(rh):
                for dx in range(rw):
                    self.map[ry + dy][rx + dx] = 0
        # 连接房间
        for i in range(len(rooms) - 1):
            x1, y1, w1, h1 = rooms[i]
            x2, y2, w2, h2 = rooms[i + 1]
            cx1 = x1 + w1 // 2
            cy1 = y1 + h1 // 2
            cx2 = x2 + w2 // 2
            cy2 = y2 + h2 // 2
            # 水平走廊
            for x in range(min(cx1, cx2), max(cx1, cx2) + 1):
                if 0 <= x < MAP_COLS:
                    self.map[cy1][x] = 0
            # 垂直走廊
            for y in range(min(cy1, cy2), max(cy1, cy2) + 1):
                if 0 <= y < MAP_ROWS:
                    self.map[y][cx2] = 0
        # 确保玩家出生在空地
        empty_tiles = [(x, y) for y in range(MAP_ROWS) for x in range(MAP_COLS) if self.map[y][x] == 0]
        self.player_pos = list(random.choice(empty_tiles))
        # 放置敌人
        self.enemies = []
        for _ in range(ENEMY_COUNT):
            pos = random.choice([t for t in empty_tiles if t != tuple(self.player_pos)])
            self.enemies.append({'pos': list(pos), 'hp': ENEMY_HP, 'atk': ENEMY_ATK})
            empty_tiles.remove(pos)
        # 放置药水
        self.potions = []
        for _ in range(POTION_COUNT):
            pos = random.choice([t for t in empty_tiles if t != tuple(self.player_pos)])
            self.potions.append(list(pos))
            empty_tiles.remove(pos)
        # 放置武器
        self.weapons = []
        for _ in range(WEAPON_COUNT):
            pos = random.choice([t for t in empty_tiles if t != tuple(self.player_pos)])
            self.weapons.append(list(pos))
            empty_tiles.remove(pos)
        # 放置出口
        self.exit_pos = random.choice([t for t in empty_tiles if t != tuple(self.player_pos)])

    def move_player(self, dx, dy):
        if self.state != STATE_PLAYING:
            return
        nx = self.player_pos[0] + dx
        ny = self.player_pos[1] + dy
        if 0 <= nx < MAP_COLS and 0 <= ny < MAP_ROWS and self.map[ny][nx] == 0:
            self.player_pos = [nx, ny]
            self.check_collisions()
            self.enemy_turn()
            self.check_game_over()

    def check_collisions(self):
        # 敌人
        for enemy in self.enemies[:]:
            if enemy['pos'] == self.player_pos:
                damage = self.player_atk
                enemy['hp'] -= damage
                if enemy['hp'] <= 0:
                    self.enemies.remove(enemy)
                    self.player_exp += 5
                    if self.player_exp >= self.player_exp_to_next:
                        self.level_up()
                return
        # 药水
        for potion in self.potions[:]:
            if potion == self.player_pos:
                self.player_hp = min(self.player_max_hp, self.player_hp + POTION_HEAL)
                self.potions.remove(potion)
                return
        # 武器
        for weapon in self.weapons[:]:
            if weapon == self.player_pos:
                self.player_atk += WEAPON_BONUS
                self.weapons.remove(weapon)
                return
        # 出口
        if list(self.exit_pos) == self.player_pos:
            self.next_floor()

    def next_floor(self):
        self.floor += 1
        self.generate_dungeon()

    def level_up(self):
        self.player_lv += 1
        self.player_exp = 0
        self.player_max_hp += 5
        self.player_hp = self.player_max_hp
        self.player_atk += 1
        self.player_exp_to_next += 5

    def enemy_turn(self):
        for enemy in self.enemies:
            px, py = self.player_pos
            ex, ey = enemy['pos']
            # 简单靠近玩家
            if abs(px - ex) + abs(py - ey) == 1:
                self.player_hp -= enemy['atk']
            else:
                if abs(px - ex) > abs(py - ey):
                    if px > ex and self.map[ey][ex+1] == 0: enemy['pos'][0] += 1
                    elif px < ex and self.map[ey][ex-1] == 0: enemy['pos'][0] -= 1
                else:
                    if py > ey and self.map[ey+1][ex] == 0: enemy['pos'][1] += 1
                    elif py < ey and self.map[ey-1][ex] == 0: enemy['pos'][1] -= 1

    def check_game_over(self):
        if self.player_hp <= 0:
            self.state = STATE_GAME_OVER
        elif self.floor > 2:
            self.state = STATE_WIN

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    self.reset_game()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.move_player(-1, 0)
        if keys[pygame.K_RIGHT]: self.move_player(1, 0)
        if keys[pygame.K_UP]: self.move_player(0, -1)
        if keys[pygame.K_DOWN]: self.move_player(0, 1)

    def draw(self):
        self.screen.fill(COLOR_BG)
        # 绘制地图
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                rect = pygame.Rect(MAP_X + x * TILE_SIZE, MAP_Y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if self.map[y][x] == 1:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_GROUND, rect)
        # 绘制出口
        ex, ey = self.exit_pos
        pygame.draw.rect(self.screen, COLOR_EXIT, (MAP_X + ex * TILE_SIZE, MAP_Y + ey * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        # 绘制药水
        for x, y in self.potions:
            pygame.draw.rect(self.screen, COLOR_HP_POTION, (MAP_X + x * TILE_SIZE, MAP_Y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        # 绘制武器
        for x, y in self.weapons:
            pygame.draw.rect(self.screen, COLOR_WEAPON, (MAP_X + x * TILE_SIZE, MAP_Y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        # 绘制敌人
        for enemy in self.enemies:
            x, y = enemy['pos']
            pygame.draw.rect(self.screen, COLOR_ENEMY, (MAP_X + x * TILE_SIZE, MAP_Y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        # 绘制玩家
        px, py = self.player_pos
        pygame.draw.rect(self.screen, COLOR_PLAYER, (MAP_X + px * TILE_SIZE, MAP_Y + py * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        # HUD 背景
        pygame.draw.rect(self.screen, COLOR_HUD_BG, (0, 0, SCREEN_WIDTH, MAP_Y))
        pygame.draw.rect(self.screen, COLOR_HUD_BG, (0, MAP_Y + MAP_HEIGHT, SCREEN_WIDTH, MAP_Y))
        # HUD 文字
        hud_texts = [
            f"HP: {self.player_hp}/{self.player_max_hp}",
            f"ATK: {self.player_atk}",
            f"LV: {self.player_lv}",
            f"EXP: {self.player_exp}/{self.player_exp_to_next}",
            f"Floor: {self.floor}"
        ]
        for i, text in enumerate(hud_texts):
            surf = self.font.render(text, True, COLOR_HUD_TEXT)
            self.screen.blit(surf, (20 + i * 150, 10))
        # 游戏状态提示
        if self.state == STATE_GAME_OVER:
            surf = self.big_font.render("GAME OVER", True, COLOR_ENEMY)
            self.screen.blit(surf, (SCREEN_WIDTH//2 - surf.get_width()//2, SCREEN_HEIGHT//2 - 50))
            surf = self.font.render("Press R to Restart", True, COLOR_MSG)
            self.screen.blit(surf, (SCREEN_WIDTH//2 - surf.get_width()//2, SCREEN_HEIGHT//2 + 20))
        elif self.state == STATE_WIN:
            surf = self.big_font.render("YOU WIN!", True, COLOR_PLAYER)
            self.screen.blit(surf, (SCREEN_WIDTH//2 - surf.get_width()//2, SCREEN_HEIGHT//2 - 50))
            surf = self.font.render("Press R to Restart", True, COLOR_MSG)
            self.screen.blit(surf, (SCREEN_WIDTH//2 - surf.get_width()//2, SCREEN_HEIGHT//2 + 20))
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()