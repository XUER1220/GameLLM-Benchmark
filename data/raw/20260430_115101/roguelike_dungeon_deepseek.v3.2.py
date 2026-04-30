import pygame
import random
import sys

# 初始化
pygame.init()
random.seed(42)

# 窗口和游戏常量
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
MAP_CELL_SIZE = 32
MAP_COLS, MAP_ROWS = 21, 15
MAP_WIDTH, MAP_HEIGHT = MAP_COLS * MAP_CELL_SIZE, MAP_ROWS * MAP_CELL_SIZE
MAP_OFFSET_X = (SCREEN_WIDTH - MAP_WIDTH) // 2
MAP_OFFSET_Y = (SCREEN_HEIGHT - MAP_HEIGHT) // 2

# 颜色定义
COLOR_BACKGROUND = (20, 20, 40)
COLOR_WALL = (50, 50, 90)
COLOR_FLOOR = (70, 70, 100)
COLOR_PLAYER = (0, 200, 255)
COLOR_ENEMY = (255, 100, 100)
COLOR_POTION = (100, 255, 100)
COLOR_WEAPON = (255, 255, 100)
COLOR_EXIT = (180, 100, 255)
COLOR_TEXT = (255, 255, 255)
COLOR_HUD_BG = (30, 30, 50, 200)
COLOR_GAME_OVER_BG = (0, 0, 0, 180)

# 游戏参数
PLAYER_START_HP = 20
PLAYER_START_ATK = 5
PLAYER_START_LV = 1
PLAYER_START_EXP = 0
PLAYER_START_FLOOR = 1
ENEMY_HP = 8
ENEMY_ATK = 3
ENEMY_COUNT = 4
POTION_COUNT = 2
WEAPON_COUNT = 1
POTION_HEAL = 8
WEAPON_BONUS = 2
EXP_PER_KILL = 5
EXP_TO_LEVEL = 10
LEVEL_HP_BONUS = 5
LEVEL_ATK_BONUS = 1

# 方向向量
DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

# 实体类型
WALL = 0
FLOOR = 1
PLAYER = 2
ENEMY = 3
POTION = 4
WEAPON = 5
EXIT = 6

class Entity:
    def __init__(self, x, y, type, hp=None, atk=None):
        self.x = x
        self.y = y
        self.type = type
        self.hp = hp
        self.max_hp = hp
        self.atk = atk
        self.alive = True

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Roguelike Dungeon Hard")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 48)
        self.reset()

    def reset(self):
        self.floor = PLAYER_START_FLOOR
        self.player = Entity(0, 0, PLAYER, PLAYER_START_HP, PLAYER_START_ATK)
        self.player.exp = PLAYER_START_EXP
        self.player.lv = PLAYER_START_LV
        self.generate_map()
        self.game_over = False
        self.victory = False

    def generate_map(self):
        # 初始化地图为墙壁
        self.map_data = [[WALL for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
        self.entities = []
        
        # 生成房间
        rooms = []
        for _ in range(6):
            w = random.randint(4, 6)
            h = random.randint(4, 6)
            x = random.randint(1, MAP_COLS - w - 1)
            y = random.randint(1, MAP_ROWS - h - 1)
            rooms.append((x, y, w, h))
            
        # 挖出房间
        for rx, ry, rw, rh in rooms:
            for dx in range(rw):
                for dy in range(rh):
                    self.map_data[ry + dy][rx + dx] = FLOOR
        
        # 连通房间
        for i in range(len(rooms) - 1):
            x1 = rooms[i][0] + rooms[i][2] // 2
            y1 = rooms[i][1] + rooms[i][3] // 2
            x2 = rooms[i+1][0] + rooms[i+1][2] // 2
            y2 = rooms[i+1][1] + rooms[i+1][3] // 2
            while x1 != x2:
                self.map_data[y1][x1] = FLOOR
                x1 += 1 if x1 < x2 else -1
            while y1 != y2:
                self.map_data[y1][x1] = FLOOR
                y1 += 1 if y1 < y2 else -1
        
        # 收集所有可走位置
        walkable = []
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                if self.map_data[y][x] == FLOOR:
                    walkable.append((x, y))
        
        # 放置玩家
        self.player.x, self.player.y = walkable[0]
        walkable.remove((self.player.x, self.player.y))
        
        # 放置敌人
        for _ in range(ENEMY_COUNT):
            if walkable:
                pos = random.choice(walkable)
                walkable.remove(pos)
                self.entities.append(Entity(pos[0], pos[1], ENEMY, ENEMY_HP, ENEMY_ATK))
        
        # 放置药水
        for _ in range(POTION_COUNT):
            if walkable:
                pos = random.choice(walkable)
                walkable.remove(pos)
                self.entities.append(Entity(pos[0], pos[1], POTION))
        
        # 放置武器
        if walkable:
            pos = random.choice(walkable)
            walkable.remove(pos)
            self.entities.append(Entity(pos[0], pos[1], WEAPON))
        
        # 放置出口
        if walkable:
            self.exit_pos = random.choice(walkable)
        else:
            self.exit_pos = (MAP_COLS - 2, MAP_ROWS - 2)
        self.map_data[self.exit_pos[1]][self.exit_pos[0]] = EXIT

    def move_player(self, dx, dy):
        if self.game_over:
            return False
        
        nx, ny = self.player.x + dx, self.player.y + dy
        if not (0 <= nx < MAP_COLS and 0 <= ny < MAP_ROWS):
            return False
        if self.map_data[ny][nx] == WALL:
            return False
        
        self.player.x, self.player.y = nx, ny
        
        # 检查与实体交互
        self.check_entity_interaction()
        
        # 检查出口
        if (self.player.x, self.player.y) == self.exit_pos:
            self.floor += 1
            self.generate_map()
            return True
        
        # 敌人行动
        self.enemy_turn()
        
        return True

    def check_entity_interaction(self):
        to_remove = []
        for i, entity in enumerate(self.entities):
            if (entity.x, entity.y) == (self.player.x, self.player.y):
                if entity.type == POTION:
                    self.player.hp = min(self.player.hp + POTION_HEAL, self.player.max_hp)
                    to_remove.append(i)
                elif entity.type == WEAPON:
                    self.player.atk += WEAPON_BONUS
                    to_remove.append(i)
                elif entity.type == ENEMY and entity.alive:
                    self.attack(self.player, entity)
                    if not entity.alive:
                        self.player.exp += EXP_PER_KILL
                        to_remove.append(i)
        
        for idx in reversed(to_remove):
            self.entities.pop(idx)
        
        # 检查升级
        while self.player.exp >= EXP_TO_LEVEL:
            self.player.exp -= EXP_TO_LEVEL
            self.player.lv += 1
            self.player.max_hp += LEVEL_HP_BONUS
            self.player.hp = self.player.max_hp
            self.player.atk += LEVEL_ATK_BONUS

    def enemy_turn(self):
        for entity in self.entities:
            if entity.type == ENEMY and entity.alive:
                # 简单AI：如果相邻则攻击，否则随机移动
                dist = abs(entity.x - self.player.x) + abs(entity.y - self.player.y)
                if dist == 1:
                    self.attack(entity, self.player)
                else:
                    # 随机移动
                    possible_moves = []
                    for dx, dy in DIRECTIONS:
                        nx, ny = entity.x + dx, entity.y + dy
                        if (0 <= nx < MAP_COLS and 0 <= ny < MAP_ROWS and 
                            self.map_data[ny][nx] != WALL and 
                            not (nx == self.player.x and ny == self.player.y)):
                            possible_moves.append((dx, dy))
                    if possible_moves:
                        dx, dy = random.choice(possible_moves)
                        entity.x += dx
                        entity.y += dy

    def attack(self, attacker, defender):
        defender.hp -= attacker.atk
        if defender.hp <= 0:
            defender.alive = False
            if defender == self.player:
                self.game_over = True

    def draw(self):
        self.screen.fill(COLOR_BACKGROUND)
        
        # 绘制地图
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                rect = pygame.Rect(MAP_OFFSET_X + x * MAP_CELL_SIZE, 
                                  MAP_OFFSET_Y + y * MAP_CELL_SIZE,
                                  MAP_CELL_SIZE, MAP_CELL_SIZE)
                if self.map_data[y][x] == WALL:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                elif self.map_data[y][x] == FLOOR:
                    pygame.draw.rect(self.screen, COLOR_FLOOR, rect)
                elif self.map_data[y][x] == EXIT:
                    pygame.draw.rect(self.screen, COLOR_EXIT, rect)
        
        # 绘制实体
        for entity in self.entities:
            rect = pygame.Rect(MAP_OFFSET_X + entity.x * MAP_CELL_SIZE,
                              MAP_OFFSET_Y + entity.y * MAP_CELL_SIZE,
                              MAP_CELL_SIZE, MAP_CELL_SIZE)
            if entity.type == ENEMY and entity.alive:
                pygame.draw.rect(self.screen, COLOR_ENEMY, rect)
            elif entity.type == POTION:
                pygame.draw.rect(self.screen, COLOR_POTION, rect)
            elif entity.type == WEAPON:
                pygame.draw.rect(self.screen, COLOR_WEAPON, rect)
        
        # 绘制玩家
        player_rect = pygame.Rect(MAP_OFFSET_X + self.player.x * MAP_CELL_SIZE,
                                 MAP_OFFSET_Y + self.player.y * MAP_CELL_SIZE,
                                 MAP_CELL_SIZE, MAP_CELL_SIZE)
        pygame.draw.rect(self.screen, COLOR_PLAYER, player_rect)
        
        # 绘制HUD背景
        hud_rect = pygame.Rect(10, 10, SCREEN_WIDTH - 20, 80)
        pygame.draw.rect(self.screen, COLOR_HUD_BG, hud_rect, border_radius=5)
        
        # 绘制玩家状态
        info_y = 20
        texts = [
            f"HP: {self.player.hp}/{self.player.max_hp}",
            f"ATK: {self.player.atk}",
            f"LV: {self.player.lv}",
            f"EXP: {self.player.exp}/{EXP_TO_LEVEL}",
            f"Floor: {self.floor}"
        ]
        for text in texts:
            surf = self.font.render(text, True, COLOR_TEXT)
            self.screen.blit(surf, (20, info_y))
            info_y += 25
        
        # 游戏结束界面
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(COLOR_GAME_OVER_BG)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.big_font.render("GAME OVER", True, (255, 50, 50))
            restart_text = self.font.render("Press R to Restart", True, COLOR_TEXT)
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        
        # 胜利界面（到达出口）
        if (self.player.x, self.player.y) == self.exit_pos and not self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(COLOR_GAME_OVER_BG)
            self.screen.blit(overlay, (0, 0))
            
            win_text = self.big_font.render("Floor Cleared!", True, (50, 255, 50))
            next_text = self.font.render("Move to Exit to Next Floor", True, COLOR_TEXT)
            self.screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(next_text, (SCREEN_WIDTH // 2 - next_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

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
                        self.reset()
            
            # 玩家移动
            keys = pygame.key.get_pressed()
            moved = False
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                moved = self.move_player(0, -1)
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                moved = self.move_player(1, 0)
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                moved = self.move_player(0, 1)
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                moved = self.move_player(-1, 0)
            
            # 绘制
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()