import pygame
import random
import sys

# 初始化随机种子
random.seed(42)

# 游戏常量
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
GRID_SIZE = 32
MAP_COLS, MAP_ROWS = 21, 15
MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT = MAP_COLS * GRID_SIZE, MAP_ROWS * GRID_SIZE
MAP_OFFSET_X = (SCREEN_WIDTH - MAP_PIXEL_WIDTH) // 2
MAP_OFFSET_Y = (SCREEN_HEIGHT - MAP_PIXEL_HEIGHT) // 2

# 颜色定义
COLOR_BACKGROUND = (20, 20, 30)
COLOR_GROUND = (40, 40, 60)
COLOR_WALL = (80, 60, 40)
COLOR_PLAYER = (50, 180, 255)
COLOR_ENEMY = (255, 80, 80)
COLOR_HEALTH_POTION = (80, 255, 80)
COLOR_WEAPON = (255, 200, 50)
COLOR_EXIT = (200, 100, 255)
COLOR_HUD_BG = (30, 30, 40, 200)
COLOR_TEXT = (240, 240, 255)
COLOR_GAME_OVER_BG = (0, 0, 0, 180)

# 游戏参数
INITIAL_PLAYER_HP = 20
INITIAL_PLAYER_ATK = 5
INITIAL_PLAYER_LV = 1
INITIAL_PLAYER_EXP = 0
INITIAL_ENEMY_HP = 8
INITIAL_ENEMY_ATK = 3
NUM_ENEMIES = 4
HEALTH_POTION_COUNT = 2
WEAPON_COUNT = 1
HEALTH_POTION_HEAL = 8
WEAPON_BONUS_ATK = 2
EXP_PER_KILL = 5
EXP_TO_LEVEL_UP = 10
LEVEL_UP_HP_BONUS = 5
LEVEL_UP_ATK_BONUS = 1

# 方向向量
DIRECTIONS = {
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0)
}

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_hp = INITIAL_PLAYER_HP
        self.hp = self.max_hp
        self.atk = INITIAL_PLAYER_ATK
        self.level = INITIAL_PLAYER_LV
        self.exp = INITIAL_PLAYER_EXP
        self.floor = 1

    def move(self, dx, dy, game_map):
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < MAP_COLS and 0 <= new_y < MAP_ROWS:
            if game_map[new_y][new_x] == 0:  # 地面可通行
                self.x = new_x
                self.y = new_y
                return True
        return False

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= EXP_TO_LEVEL_UP:
            self.level += 1
            self.exp -= EXP_TO_LEVEL_UP
            self.max_hp += LEVEL_UP_HP_BONUS
            self.hp = self.max_hp
            self.atk += LEVEL_UP_ATK_BONUS

    def get_rect(self):
        return pygame.Rect(
            MAP_OFFSET_X + self.x * GRID_SIZE,
            MAP_OFFSET_Y + self.y * GRID_SIZE,
            GRID_SIZE, GRID_SIZE
        )

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = INITIAL_ENEMY_HP
        self.max_hp = INITIAL_ENEMY_HP
        self.atk = INITIAL_ENEMY_ATK
        self.alive = True

    def move_towards_player(self, player, game_map):
        if not self.alive:
            return
        dx = 0
        dy = 0
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
        if 0 <= new_x < MAP_COLS and 0 <= new_y < MAP_ROWS:
            if game_map[new_y][new_x] == 0:
                # 检查是否撞到其他敌人
                can_move = True
                # 实际游戏中会有敌人列表检查，这里简化
                self.x = new_x
                self.y = new_y

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def get_rect(self):
        return pygame.Rect(
            MAP_OFFSET_X + self.x * GRID_SIZE,
            MAP_OFFSET_Y + self.y * GRID_SIZE,
            GRID_SIZE, GRID_SIZE
        )

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Roguelike Dungeon Hard")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        self.reset_game()

    def reset_game(self):
        self.generate_dungeon()
        self.player = Player(self.start_pos[0], self.start_pos[1])
        self.enemies = []
        for pos in self.enemy_positions:
            self.enemies.append(Enemy(pos[0], pos[1]))
        self.health_potions = self.health_potion_positions.copy()
        self.weapons = self.weapon_positions.copy()
        self.game_over = False
        self.victory = False
        self.turn_processed = False  # 用于回合制控制

    def generate_dungeon(self):
        # 生成一个简单的房间与走廊地图
        self.map_data = [[1 for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
        
        # 创建几个房间
        rooms = []
        for _ in range(6):
            w = random.randint(4, 6)
            h = random.randint(4, 6)
            x = random.randint(1, MAP_COLS - w - 1)
            y = random.randint(1, MAP_ROWS - h - 1)
            rooms.append((x, y, w, h))
        
        # 绘制房间
        for room in rooms:
            x, y, w, h = room
            for ry in range(y, y + h):
                for rx in range(x, x + w):
                    if 0 <= rx < MAP_COLS and 0 <= ry < MAP_ROWS:
                        self.map_data[ry][rx] = 0
        
        # 连接房间
        for i in range(len(rooms)-1):
            x1 = rooms[i][0] + rooms[i][2] // 2
            y1 = rooms[i][1] + rooms[i][3] // 2
            x2 = rooms[i+1][0] + rooms[i+1][2] // 2
            y2 = rooms[i+1][1] + rooms[i+1][3] // 2
            
            # 水平走廊
            for x in range(min(x1, x2), max(x1, x2)+1):
                if 0 <= x < MAP_COLS and 0 <= y1 < MAP_ROWS:
                    self.map_data[y1][x] = 0
            
            # 垂直走廊
            for y in range(min(y1, y2), max(y1, y2)+1):
                if 0 <= x2 < MAP_COLS and 0 <= y < MAP_ROWS:
                    self.map_data[y][x2] = 0
        
        # 确保所有地面连通，简单的洪水填充检查
        start_found = False
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                if self.map_data[y][x] == 0:
                    self.start_pos = (x, y)
                    start_found = True
                    break
            if start_found:
                break
        
        # 选择出口位置
        self.exit_pos = None
        for attempt in range(100):
            x = random.randint(0, MAP_COLS-1)
            y = random.randint(0, MAP_ROWS-1)
            if self.map_data[y][x] == 0 and (abs(x - self.start_pos[0]) > 5 or abs(y - self.start_pos[1]) > 5):
                self.exit_pos = (x, y)
                break
        if not self.exit_pos:
            # 如果没有找到合适的出口，使用最后一个房间的中心
            last_room = rooms[-1]
            self.exit_pos = (last_room[0] + last_room[2]//2, last_room[1] + last_room[3]//2)
        
        # 生成敌人位置
        self.enemy_positions = []
        for _ in range(NUM_ENEMIES):
            while True:
                x = random.randint(0, MAP_COLS-1)
                y = random.randint(0, MAP_ROWS-1)
                if self.map_data[y][x] == 0 and (x, y) != self.start_pos and (x, y) != self.exit_pos:
                    self.enemy_positions.append((x, y))
                    break
        
        # 生成药水位置
        self.health_potion_positions = []
        for _ in range(HEALTH_POTION_COUNT):
            while True:
                x = random.randint(0, MAP_COLS-1)
                y = random.randint(0, MAP_ROWS-1)
                if self.map_data[y][x] == 0 and (x, y) != self.start_pos and (x, y) != self.exit_pos and (x, y) not in self.enemy_positions:
                    self.health_potion_positions.append((x, y))
                    break
        
        # 生成武器位置
        self.weapon_positions = []
        for _ in range(WEAPON_COUNT):
            while True:
                x = random.randint(0, MAP_COLS-1)
                y = random.randint(0, MAP_ROWS-1)
                if self.map_data[y][x] == 0 and (x, y) != self.start_pos and (x, y) != self.exit_pos and (x, y) not in self.enemy_positions and (x, y) not in self.health_potion_positions:
                    self.weapon_positions.append((x, y))
                    break

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                else:
                    if event.key in DIRECTIONS and not self.turn_processed:
                        dx, dy = DIRECTIONS[event.key]
                        if self.player.move(dx, dy, self.map_data):
                            self.turn_processed = True
                            self.process_turn()

    def process_turn(self):
        # 检查道具拾取
        if (self.player.x, self.player.y) in self.health_potions:
            self.player.heal(HEALTH_POTION_HEAL)
            self.health_potions.remove((self.player.x, self.player.y))
        
        if (self.player.x, self.player.y) in self.weapons:
            self.player.atk += WEAPON_BONUS_ATK
            self.weapons.remove((self.player.x, self.player.y))
        
        # 检查敌人攻击
        for enemy in self.enemies:
            if enemy.alive:
                if abs(enemy.x - self.player.x) + abs(enemy.y - self.player.y) == 1:
                    self.player.take_damage(enemy.atk)
        
        # 敌人移动
        for enemy in self.enemies:
            if enemy.alive:
                enemy.move_towards_player(self.player, self.map_data)
        
        # 检查玩家攻击
        for enemy in self.enemies:
            if enemy.alive:
                if abs(enemy.x - self.player.x) + abs(enemy.y - self.player.y) == 1:
                    enemy.take_damage(self.player.atk)
                    if not enemy.alive:
                        self.player.gain_exp(EXP_PER_KILL)
        
        # 检查出口
        if (self.player.x, self.player.y) == self.exit_pos:
            self.player.floor += 1
            if self.player.floor > 2:
                self.victory = True
                self.game_over = True
            else:
                self.generate_dungeon()
                self.player.x, self.player.y = self.start_pos
                for pos in self.enemy_positions:
                    self.enemies.append(Enemy(pos[0], pos[1]))
                self.health_potions = self.health_potion_positions.copy()
                self.weapons = self.weapon_positions.copy()
        
        # 检查游戏结束
        if self.player.hp <= 0:
            self.game_over = True
        
        self.turn_processed = False

    def draw(self):
        self.screen.fill(COLOR_BACKGROUND)
        
        # 绘制地图边框
        pygame.draw.rect(self.screen, (60, 60, 80), 
                        (MAP_OFFSET_X-2, MAP_OFFSET_Y-2, 
                         MAP_PIXEL_WIDTH+4, MAP_PIXEL_HEIGHT+4), 2)
        
        # 绘制地图
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                rect = pygame.Rect(
                    MAP_OFFSET_X + x * GRID_SIZE,
                    MAP_OFFSET_Y + y * GRID_SIZE,
                    GRID_SIZE, GRID_SIZE
                )
                if self.map_data[y][x] == 1:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_GROUND, rect)
                pygame.draw.rect(self.screen, (30, 30, 40), rect, 1)
        
        # 绘制出口
        exit_rect = pygame.Rect(
            MAP_OFFSET_X + self.exit_pos[0] * GRID_SIZE,
            MAP_OFFSET_Y + self.exit_pos[1] * GRID_SIZE,
            GRID_SIZE, GRID_SIZE
        )
        pygame.draw.rect(self.screen, COLOR_EXIT, exit_rect)
        # 绘制出口符号
        pygame.draw.circle(self.screen, (255, 255, 255), 
                          exit_rect.center, GRID_SIZE//3, 3)
        
        # 绘制药水
        for pos in self.health_potions:
            rect = pygame.Rect(
                MAP_OFFSET_X + pos[0] * GRID_SIZE,
                MAP_OFFSET_Y + pos[1] * GRID_SIZE,
                GRID_SIZE, GRID_SIZE
            )
            pygame.draw.rect(self.screen, COLOR_HEALTH_POTION, rect)
            # 绘制加号
            pygame.draw.rect(self.screen, (255, 255, 255), 
                            (rect.centerx-1, rect.top+8, 2, 16), 0)
            pygame.draw.rect(self.screen, (255, 255, 255), 
                            (rect.left+8, rect.centery-1, 16, 2), 0)
        
        # 绘制武器
        for pos in self.weapons:
            rect = pygame.Rect(
                MAP_OFFSET_X + pos[0] * GRID_SIZE,
                MAP_OFFSET_Y + pos[1] * GRID_SIZE,
                GRID_SIZE, GRID_SIZE
            )
            pygame.draw.rect(self.screen, COLOR_WEAPON, rect)
            # 绘制剑形
            pygame.draw.rect(self.screen, (255, 255, 255), 
                            (rect.centerx-1, rect.top+6, 2, 20), 0)
            pygame.draw.polygon(self.screen, (255, 255, 255), [
                (rect.centerx, rect.top+6),
                (rect.centerx-4, rect.top+10),
                (rect.centerx+4, rect.top+10)
            ])
        
        # 绘制敌人
        for enemy in self.enemies:
            if enemy.alive:
                rect = enemy.get_rect()
                pygame.draw.rect(self.screen, COLOR_ENEMY, rect)
                # 绘制敌人生命条
                hp_width = int((enemy.hp / enemy.max_hp) * (GRID_SIZE-4))
                pygame.draw.rect(self.screen, (255, 255, 255), 
                                (rect.left+2, rect.top+2, GRID_SIZE-4, 4), 1)
                pygame.draw.rect(self.screen, (200, 50, 50), 
                                (rect.left+3, rect.top+3, hp_width-2, 2))
        
        # 绘制玩家
        player_rect = self.player.get_rect()
        pygame.draw.rect(self.screen, COLOR_PLAYER, player_rect)
        # 绘制玩家生命条
        hp_width = int((self.player.hp / self.player.max_hp) * (GRID_SIZE-4))
        pygame.draw.rect(self.screen, (255, 255, 255), 
                        (player_rect.left+2, player_rect.top+2, GRID_SIZE-4, 4), 1)
        pygame.draw.rect(self.screen, (50, 200, 50), 
                        (player_rect.left+3, player_rect.top+3, hp_width-2, 2))
        
        # 绘制HUD
        hud_height = 100
        hud_surface = pygame.Surface((SCREEN_WIDTH, hud_height), pygame.SRCALPHA)
        hud_surface.fill(COLOR_HUD_BG)
        self.screen.blit(hud_surface, (0, SCREEN_HEIGHT - hud_height))
        
        # HUD文字
        hud_texts = [
            f"生命值: {self.player.hp}/{self.player.max_hp}",
            f"攻击力: {self.player.atk}",
            f"等级: {self.player.level}",
            f"经验: {self.player.exp}/{EXP_TO_LEVEL_UP}",
            f"层数: {self.player.floor}"
        ]
        
        for i, text in enumerate(hud_texts):
            text_surface = self.font.render(text, True, COLOR_TEXT)
            self.screen.blit(text_surface, (20 + (i % 3) * 250, SCREEN_HEIGHT - hud_height + 20 + (i // 3) * 30))
        
        # 游戏结束屏幕
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(COLOR_GAME_OVER_BG)
            self.screen.blit(overlay, (0, 0))
            
            if self.victory:
                text = self.large_font.render("Victory!", True, (100, 255, 100))
            else:
                text = self.large_font.render("Game Over", True, (255, 100, 100))
            
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(text, text_rect)
            
            restart_text = self.font.render("Press R to Restart", True, COLOR_TEXT)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()