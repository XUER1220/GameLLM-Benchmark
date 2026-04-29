import pygame
import random
import sys

# 初始化随机种子
random.seed(42)

# 窗口与游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 32
MAP_COLS = 21
MAP_ROWS = 15
MAP_WIDTH = MAP_COLS * TILE_SIZE
MAP_HEIGHT = MAP_ROWS * TILE_SIZE
MAP_X_OFFSET = (SCREEN_WIDTH - MAP_WIDTH) // 2
MAP_Y_OFFSET = (SCREEN_HEIGHT - MAP_HEIGHT) // 2

# 颜色定义
COLOR_BG = (20, 20, 40)
COLOR_FLOOR = (60, 60, 80)
COLOR_WALL = (120, 80, 40)
COLOR_PLAYER = (0, 200, 255)
COLOR_ENEMY = (255, 100, 100)
COLOR_HEALTH_POTION = (100, 255, 100)
COLOR_WEAPON = (255, 255, 100)
COLOR_EXIT = (180, 100, 255)
COLOR_HUD_BG = (30, 30, 50, 200)
COLOR_HUD_TEXT = (230, 230, 250)
COLOR_GAME_OVER_TEXT = (255, 80, 80)
COLOR_GAME_OVER_BG = (0, 0, 0, 180)

# 游戏参数
PLAYER_HP_INIT = 20
PLAYER_ATK_INIT = 5
PLAYER_LV_INIT = 1
PLAYER_EXP_INIT = 0
ENEMY_HP_INIT = 8
ENEMY_ATK_INIT = 3
HEAL_AMOUNT = 8
WEAPON_BONUS = 2
EXP_PER_KILL = 5
EXP_TO_LEVEL = 10
LEVEL_HP_BONUS = 5
LEVEL_ATK_BONUS = 1
NUM_ENEMIES = 4
NUM_POTIONS = 2
NUM_WEAPONS = 1

# 地图单元格类型
CELL_EMPTY = 0
CELL_WALL = 1
CELL_FLOOR = 2
CELL_PLAYER = 3
CELL_ENEMY = 4
CELL_HEALTH_POTION = 5
CELL_WEAPON = 6
CELL_EXIT = 7

# 方向向量
DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

class Entity:
    def __init__(self, x, y, hp, atk, symbol):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.atk = atk
        self.symbol = symbol

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Roguelike Dungeon Hard")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 48)
        self.reset_game()

    def reset_game(self):
        self.floor = 1
        self.generate_map()
        self.init_player()
        self.init_enemies()
        self.init_items()
        self.turn = 0
        self.game_over = False
        self.victory = False

    def generate_map(self):
        # 创建全墙壁地图
        self.map = [[CELL_WALL for _ in range(MAP_COLS)] for __ in range(MAP_ROWS)]
        
        # 生成房间
        rooms = []
        for _ in range(6):
            w = random.randint(4, 6)
            h = random.randint(3, 5)
            x = random.randint(1, MAP_COLS - w - 1)
            y = random.randint(1, MAP_ROWS - h - 1)
            rooms.append((x, y, w, h))
        
        # 绘制房间为地板
        for (x, y, w, h) in rooms:
            for i in range(y, y + h):
                for j in range(x, x + w):
                    if 0 <= i < MAP_ROWS and 0 <= j < MAP_COLS:
                        self.map[i][j] = CELL_FLOOR
        
        # 连通房间（简单直线连接）
        for i in range(len(rooms) - 1):
            x1 = rooms[i][0] + rooms[i][2] // 2
            y1 = rooms[i][1] + rooms[i][3] // 2
            x2 = rooms[i+1][0] + rooms[i+1][2] // 2
            y2 = rooms[i+1][1] + rooms[i+1][3] // 2
            
            # 水平连接
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 <= x < MAP_COLS and 0 <= y1 < MAP_ROWS:
                    self.map[y1][x] = CELL_FLOOR
            # 垂直连接
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if 0 <= x2 < MAP_COLS and 0 <= y < MAP_ROWS:
                    self.map[y][x2] = CELL_FLOOR
        
        # 确保有足够的空地放置实体
        self.floor_cells = []
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                if self.map[y][x] == CELL_FLOOR:
                    self.floor_cells.append((x, y))

    def init_player(self):
        # 放置玩家在随机空地
        pos = random.choice(self.floor_cells)
        self.player = Entity(pos[0], pos[1], PLAYER_HP_INIT, PLAYER_ATK_INIT, '@')
        self.map[self.player.y][self.player.x] = CELL_PLAYER

    def init_enemies(self):
        self.enemies = []
        floor_without_player = [c for c in self.floor_cells if (c[0], c[1]) != (self.player.x, self.player.y)]
        for _ in range(NUM_ENEMIES):
            if not floor_without_player:
                break
            pos = random.choice(floor_without_player)
            floor_without_player.remove(pos)
            enemy = Entity(pos[0], pos[1], ENEMY_HP_INIT, ENEMY_ATK_INIT, 'E')
            self.enemies.append(enemy)
            self.map[enemy.y][enemy.x] = CELL_ENEMY

    def init_items(self):
        # 放置药水和武器
        floor_free = [c for c in self.floor_cells if self.map[c[1]][c[0]] == CELL_FLOOR]
        # 药水
        for _ in range(NUM_POTIONS):
            if not floor_free:
                break
            pos = random.choice(floor_free)
            floor_free.remove(pos)
            self.map[pos[1]][pos[0]] = CELL_HEALTH_POTION
        # 武器
        for _ in range(NUM_WEAPONS):
            if not floor_free:
                break
            pos = random.choice(floor_free)
            floor_free.remove(pos)
            self.map[pos[1]][pos[0]] = CELL_WEAPON
        # 出口
        if floor_free:
            pos = random.choice(floor_free)
            self.map[pos[1]][pos[0]] = CELL_EXIT
            self.exit_pos = pos
        else:
            # 备用出口位置
            for y in range(MAP_ROWS):
                for x in range(MAP_COLS):
                    if self.map[y][x] == CELL_FLOOR:
                        self.map[y][x] = CELL_EXIT
                        self.exit_pos = (x, y)
                        return

    def move_player(self, dx, dy):
        if self.game_over:
            return False
        
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        
        if not (0 <= new_x < MAP_COLS and 0 <= new_y < MAP_ROWS):
            return False
        
        target_cell = self.map[new_y][new_x]
        
        # 撞墙
        if target_cell == CELL_WALL:
            return False
        
        # 移动到出口
        if target_cell == CELL_EXIT:
            self.next_floor()
            return True
        
        # 攻击敌人
        enemy = self.get_enemy_at(new_x, new_y)
        if enemy:
            self.attack(self.player, enemy)
            self.map[self.player.y][self.player.x] = CELL_FLOOR
            self.map[new_y][new_x] = CELL_PLAYER
            self.player.x, self.player.y = new_x, new_y
            self.enemy_turn()
            return True
        
        # 拾取物品
        if target_cell == CELL_HEALTH_POTION:
            self.player.hp = min(self.player.max_hp, self.player.hp + HEAL_AMOUNT)
        elif target_cell == CELL_WEAPON:
            self.player.atk += WEAPON_BONUS
        
        # 移动到空位
        self.map[self.player.y][self.player.x] = CELL_FLOOR
        self.map[new_y][new_x] = CELL_PLAYER
        self.player.x, self.player.y = new_x, new_y
        
        self.enemy_turn()
        return True

    def get_enemy_at(self, x, y):
        for e in self.enemies:
            if e.x == x and e.y == y:
                return e
        return None

    def attack(self, attacker, defender):
        defender.hp -= attacker.atk
        if defender.hp <= 0:
            defender.hp = 0
            if defender == self.player:
                self.game_over = True
            else:
                # 敌人死亡
                self.enemies.remove(defender)
                self.map[defender.y][defender.x] = CELL_FLOOR
                if attacker == self.player:
                    self.player_exp_gain()
        # 反击（如果是敌人攻击玩家）
        if defender == self.player and attacker in self.enemies:
            self.player.hp -= attacker.atk
            if self.player.hp <= 0:
                self.player.hp = 0
                self.game_over = True

    def player_exp_gain(self):
        self.player.exp += EXP_PER_KILL
        while self.player.exp >= EXP_TO_LEVEL:
            self.player.exp -= EXP_TO_LEVEL
            self.player.lv += 1
            self.player.max_hp += LEVEL_HP_BONUS
            self.player.hp = self.player.max_hp
            self.player.atk += LEVEL_ATK_BONUS

    def enemy_turn(self):
        # 每个敌人移动或攻击
        for enemy in self.enemies[:]:  # 复制列表，防止迭代时删除
            # 首先检查是否在玩家相邻位置
            adjacent = False
            for dx, dy in DIRECTIONS:
                if self.player.x == enemy.x + dx and self.player.y == enemy.y + dy:
                    adjacent = True
                    self.attack(enemy, self.player)
                    break
            if adjacent:
                continue
            
            # 否则尝试向玩家移动一步
            possible_moves = []
            for dx, dy in DIRECTIONS:
                nx, ny = enemy.x + dx, enemy.y + dy
                if 0 <= nx < MAP_COLS and 0 <= ny < MAP_ROWS:
                    cell = self.map[ny][nx]
                    if cell == CELL_FLOOR or cell == CELL_PLAYER:
                        possible_moves.append((dx, dy, abs(nx - self.player.x) + abs(ny - self.player.y)))
            if possible_moves:
                # 选择最接近玩家的方向
                possible_moves.sort(key=lambda m: m[2])
                dx, dy, _ = possible_moves[0]
                new_x, new_y = enemy.x + dx, enemy.y + dy
                # 如果移动到玩家位置，则攻击
                if self.map[new_y][new_x] == CELL_PLAYER:
                    self.attack(enemy, self.player)
                elif self.map[new_y][new_x] == CELL_FLOOR:
                    self.map[enemy.y][enemy.x] = CELL_FLOOR
                    self.map[new_y][new_x] = CELL_ENEMY
                    enemy.x, enemy.y = new_x, new_y

    def next_floor(self):
        self.floor += 1
        if self.floor > 2:
            self.victory = True
            self.game_over = True
        else:
            self.generate_map()
            self.init_player()
            self.init_enemies()
            self.init_items()

    def draw(self):
        self.screen.fill(COLOR_BG)
        
        # 绘制地图
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                rect = pygame.Rect(MAP_X_OFFSET + x * TILE_SIZE, MAP_Y_OFFSET + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                cell = self.map[y][x]
                if cell == CELL_WALL:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                elif cell == CELL_FLOOR:
                    pygame.draw.rect(self.screen, COLOR_FLOOR, rect)
                elif cell == CELL_PLAYER:
                    pygame.draw.rect(self.screen, COLOR_FLOOR, rect)
                    pygame.draw.rect(self.screen, COLOR_PLAYER, rect.inflate(-8, -8))
                elif cell == CELL_ENEMY:
                    pygame.draw.rect(self.screen, COLOR_FLOOR, rect)
                    pygame.draw.rect(self.screen, COLOR_ENEMY, rect.inflate(-8, -8))
                elif cell == CELL_HEALTH_POTION:
                    pygame.draw.rect(self.screen, COLOR_FLOOR, rect)
                    pygame.draw.rect(self.screen, COLOR_HEALTH_POTION, rect.inflate(-8, -8))
                elif cell == CELL_WEAPON:
                    pygame.draw.rect(self.screen, COLOR_FLOOR, rect)
                    pygame.draw.rect(self.screen, COLOR_WEAPON, rect.inflate(-8, -8))
                elif cell == CELL_EXIT:
                    pygame.draw.rect(self.screen, COLOR_FLOOR, rect)
                    pygame.draw.rect(self.screen, COLOR_EXIT, rect.inflate(-8, -8))
        
        # 绘制HUD背景
        hud_rect = pygame.Rect(10, 10, SCREEN_WIDTH - 20, 60)
        pygame.draw.rect(self.screen, COLOR_HUD_BG, hud_rect, border_radius=5)
        
        # 绘制玩家状态
        info = [
            f"HP: {self.player.hp}/{self.player.max_hp}",
            f"ATK: {self.player.atk}",
            f"LV: {self.player.lv}",
            f"EXP: {self.player.exp}/{EXP_TO_LEVEL}",
            f"Floor: {self.floor}"
        ]
        for i, text in enumerate(info):
            surf = self.font.render(text, True, COLOR_HUD_TEXT)
            self.screen.blit(surf, (20, 15 + i * 20))
        
        # 绘制敌人数量
        enemy_text = f"Enemies: {len(self.enemies)}"
        surf = self.font.render(enemy_text, True, COLOR_HUD_TEXT)
        self.screen.blit(surf, (SCREEN_WIDTH - 150, 15))
        
        # 游戏结束画面
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(COLOR_GAME_OVER_BG)
            self.screen.blit(overlay, (0, 0))
            
            if self.victory:
                text = "VICTORY! You escaped the dungeon!"
            else:
                text = "GAME OVER"
            surf = self.big_font.render(text, True, COLOR_GAME_OVER_TEXT)
            rect = surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
            self.screen.blit(surf, rect)
            
            restart_text = "Press R to Restart, ESC to Quit"
            surf2 = self.font.render(restart_text, True, COLOR_HUD_TEXT)
            rect2 = surf2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))
            self.screen.blit(surf2, rect2)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif not self.game_over:
                        if event.key == pygame.K_UP:
                            self.move_player(0, -1)
                        elif event.key == pygame.K_DOWN:
                            self.move_player(0, 1)
                        elif event.key == pygame.K_LEFT:
                            self.move_player(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move_player(1, 0)
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# 添加玩家属性
class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_HP_INIT, PLAYER_ATK_INIT, '@')
        self.lv = PLAYER_LV_INIT
        self.exp = PLAYER_EXP_INIT

# 修补Game类中的player初始化
Game.init_player = lambda self: (
    setattr(self, 'player', Player(*random.choice(self.floor_cells))),
    setattr(self.map[self.player.y][self.player.x], CELL_PLAYER)
)
# 修复攻击中的属性访问
Game.attack = lambda self, attacker, defender: (
    setattr(defender, 'hp', defender.hp - attacker.atk),
    defender.hp <= 0 and (
        defender == self.player and setattr(self, 'game_over', True) or
        (self.enemies.remove(defender), setattr(self.map[defender.y][defender.x], CELL_FLOOR),
         attacker == self.player and self.player_exp_gain())
    ),
    defender == self.player and attacker in self.enemies and (
        setattr(self.player, 'hp', self.player.hp - attacker.atk),
        self.player.hp <= 0 and (setattr(self.player, 'hp', 0), setattr(self, 'game_over', True))
    )
)
# 修复经验获取
Game.player_exp_gain = lambda self: (
    setattr(self.player, 'exp', self.player.exp + EXP_PER_KILL),
    while self.player.exp >= EXP_TO_LEVEL: (
        setattr(self.player, 'exp', self.player.exp - EXP_TO_LEVEL),
        setattr(self.player, 'lv', self.player.lv + 1),
        setattr(self.player, 'max_hp', self.player.max_hp + LEVEL_HP_BONUS),
        setattr(self.player, 'hp', self.player.max_hp),
        setattr(self.player, 'atk', self.player.atk + LEVEL_ATK_BONUS)
    )
)

if __name__ == "__main__":
    game = Game()
    game.run()