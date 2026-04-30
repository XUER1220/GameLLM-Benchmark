import pygame
import random
import sys

# 初始化随机种子
random.seed(42)

# 窗口与网格常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 32
MAP_COLS = 21
MAP_ROWS = 15
MAP_WIDTH = MAP_COLS * TILE_SIZE
MAP_HEIGHT = MAP_ROWS * TILE_SIZE
MAP_X = (SCREEN_WIDTH - MAP_WIDTH) // 2
MAP_Y = (SCREEN_HEIGHT - MAP_HEIGHT) // 2

# 颜色定义
COLOR_BG = (20, 12, 28)
COLOR_GROUND = (40, 40, 60)
COLOR_WALL = (72, 50, 60)
COLOR_PLAYER = (200, 200, 100)
COLOR_ENEMY = (200, 60, 60)
COLOR_POTION = (60, 200, 60)
COLOR_WEAPON = (100, 160, 220)
COLOR_EXIT = (220, 140, 60)
COLOR_HUD_BG = (30, 30, 40)
COLOR_HUD_TEXT = (240, 220, 180)
COLOR_GAME_OVER_BG = (0, 0, 0, 180)
COLOR_GRID_LINE = (60, 60, 80, 100)

# 游戏初始属性
PLAYER_HP_INIT = 20
PLAYER_ATK_INIT = 5
PLAYER_LV_INIT = 1
PLAYER_EXP_INIT = 0
PLAYER_MAX_HP_PER_LEVEL = 5
ENEMY_HP_INIT = 8
ENEMY_ATK_INIT = 3
ENEMY_COUNT = 4
POTION_COUNT = 2
POTION_HEAL = 8
WEAPON_BOOST = 2
EXP_PER_ENEMY = 5
EXP_TO_NEXT_LEVEL = 10

# 方向向量
DIRECTIONS = {
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0)
}

class DungeonGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Roguelike Dungeon Hard")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 24)
        self.reset_game()

    def reset_game(self):
        self.floor = 1
        self.player_hp = PLAYER_HP_INIT
        self.player_max_hp = PLAYER_HP_INIT
        self.player_atk = PLAYER_ATK_INIT
        self.player_lv = PLAYER_LV_INIT
        self.player_exp = PLAYER_EXP_INIT
        self.player_pos = None
        self.exit_pos = None
        self.enemies = []
        self.potions = []
        self.weapons = []
        self.tiles = []
        self.game_over = False
        self.victory = False
        self.turn_done = False
        self.generate_map()

    def generate_map(self):
        # 初始化所有为墙壁
        self.tiles = [[1 for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
        
        # 生成房间
        rooms = []
        for _ in range(6):
            w = random.randint(4, 6)
            h = random.randint(4, 6)
            x = random.randint(1, MAP_COLS - w - 1)
            y = random.randint(1, MAP_ROWS - h - 1)
            rooms.append((x, y, w, h))
        
        # 挖空房间
        for x, y, w, h in rooms:
            for dy in range(h):
                for dx in range(w):
                    if 0 <= y+dy < MAP_ROWS and 0 <= x+dx < MAP_COLS:
                        self.tiles[y+dy][x+dx] = 0
        
        # 连通房间（简单连通）
        for i in range(len(rooms)-1):
            x1 = rooms[i][0] + rooms[i][2] // 2
            y1 = rooms[i][1] + rooms[i][3] // 2
            x2 = rooms[i+1][0] + rooms[i+1][2] // 2
            y2 = rooms[i+1][1] + rooms[i+1][3] // 2
            # 水平走廊
            for x in range(min(x1, x2), max(x1, x2)+1):
                if 0 <= x < MAP_COLS:
                    self.tiles[y1][x] = 0
            # 垂直走廊
            for y in range(min(y1, y2), max(y1, y2)+1):
                if 0 <= y < MAP_ROWS:
                    self.tiles[y][x2] = 0
        
        # 确保所有空地可达
        ground_cells = []
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                if self.tiles[y][x] == 0:
                    ground_cells.append((x, y))
        
        # 放置玩家
        self.player_pos = random.choice(ground_cells)
        ground_cells.remove(self.player_pos)
        
        # 放置出口
        self.exit_pos = random.choice(ground_cells)
        ground_cells.remove(self.exit_pos)
        
        # 放置敌人
        self.enemies = []
        for _ in range(ENEMY_COUNT):
            if not ground_cells:
                break
            pos = random.choice(ground_cells)
            ground_cells.remove(pos)
            self.enemies.append({
                'pos': pos,
                'hp': ENEMY_HP_INIT,
                'atk': ENEMY_ATK_INIT
            })
        
        # 放置药水
        self.potions = []
        for _ in range(POTION_COUNT):
            if not ground_cells:
                break
            pos = random.choice(ground_cells)
            ground_cells.remove(pos)
            self.potions.append(pos)
        
        # 放置武器
        self.weapons = []
        if ground_cells:
            pos = random.choice(ground_cells)
            ground_cells.remove(pos)
            self.weapons.append(pos)

    def is_walkable(self, x, y):
        if not (0 <= x < MAP_COLS and 0 <= y < MAP_ROWS):
            return False
        if self.tiles[y][x] == 1:
            return False
        if (x, y) == self.exit_pos:
            return True
        for enemy in self.enemies:
            if (x, y) == enemy['pos']:
                return False
        return True

    def move_player(self, dx, dy):
        if self.game_over or self.turn_done:
            return False
        nx = self.player_pos[0] + dx
        ny = self.player_pos[1] + dy
        if self.is_walkable(nx, ny):
            self.player_pos = (nx, ny)
            # 检查物品
            if self.player_pos in self.potions:
                self.potions.remove(self.player_pos)
                self.player_hp = min(self.player_max_hp, self.player_hp + POTION_HEAL)
            if self.player_pos in self.weapons:
                self.weapons.remove(self.player_pos)
                self.player_atk += WEAPON_BOOST
            # 检查出口
            if self.player_pos == self.exit_pos:
                self.floor += 1
                if self.floor > 2:
                    self.victory = True
                    self.game_over = True
                else:
                    self.generate_map()
                return True
            self.turn_done = True
            return True
        return False

    def enemies_turn(self):
        if self.game_over:
            return
        # 移动敌人
        for enemy in self.enemies:
            px, py = self.player_pos
            ex, ey = enemy['pos']
            dx = 0
            dy = 0
            if random.random() < 0.7:
                if abs(px - ex) > abs(py - ey):
                    dx = 1 if px > ex else -1
                else:
                    dy = 1 if py > ey else -1
            else:
                dx = random.choice([-1, 0, 1])
                dy = random.choice([-1, 0, 1])
            
            new_x = ex + dx
            new_y = ey + dy
            if self.is_walkable(new_x, new_y) and (new_x, new_y) != self.player_pos:
                enemy['pos'] = (new_x, new_y)
        
        # 攻击玩家
        for enemy in self.enemies:
            ex, ey = enemy['pos']
            px, py = self.player_pos
            if abs(ex - px) + abs(ey - py) == 1:
                self.player_hp -= enemy['atk']
        
        self.turn_done = False
        # 检查玩家死亡
        if self.player_hp <= 0:
            self.game_over = True

    def attack_enemy(self):
        # 简单攻击：如果玩家与敌人相邻，则攻击敌人
        px, py = self.player_pos
        for enemy in self.enemies[:]:
            ex, ey = enemy['pos']
            if abs(ex - px) + abs(ey - py) == 1:
                enemy['hp'] -= self.player_atk
                if enemy['hp'] <= 0:
                    self.enemies.remove(enemy)
                    self.player_exp += EXP_PER_ENEMY
                    if self.player_exp >= EXP_TO_NEXT_LEVEL:
                        self.player_lv += 1
                        self.player_exp -= EXP_TO_NEXT_LEVEL
                        self.player_max_hp += PLAYER_MAX_HP_PER_LEVEL
                        self.player_hp = self.player_max_hp
                        self.player_atk += 1
                return True
        return False

    def handle_input(self, key):
        if key in DIRECTIONS:
            dx, dy = DIRECTIONS[key]
            if self.move_player(dx, dy):
                if not self.game_over:
                    self.enemies_turn()
        elif key == pygame.K_SPACE:
            if self.attack_enemy():
                self.enemies_turn()

    def draw(self):
        self.screen.fill(COLOR_BG)
        
        # 绘制地图区域背景
        pygame.draw.rect(self.screen, COLOR_HUD_BG, (MAP_X-2, MAP_Y-2, MAP_WIDTH+4, MAP_HEIGHT+4))
        
        # 绘制地图
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                rect = (MAP_X + x*TILE_SIZE, MAP_Y + y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if self.tiles[y][x] == 0:
                    pygame.draw.rect(self.screen, COLOR_GROUND, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                # 网格线
                pygame.draw.rect(self.screen, COLOR_GRID_LINE, rect, 1)
        
        # 绘制出口
        if self.exit_pos:
            ex, ey = self.exit_pos
            rect = (MAP_X + ex*TILE_SIZE, MAP_Y + ey*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.screen, COLOR_EXIT, rect)
            pygame.draw.rect(self.screen, (255, 200, 100), rect, 2)
        
        # 绘制药水
        for x, y in self.potions:
            center = (MAP_X + x*TILE_SIZE + TILE_SIZE//2, MAP_Y + y*TILE_SIZE + TILE_SIZE//2)
            pygame.draw.circle(self.screen, COLOR_POTION, center, TILE_SIZE//3)
        
        # 绘制武器
        for x, y in self.weapons:
            rect = (MAP_X + x*TILE_SIZE + 4, MAP_Y + y*TILE_SIZE + 4, TILE_SIZE-8, TILE_SIZE-8)
            pygame.draw.rect(self.screen, COLOR_WEAPON, rect)
        
        # 绘制敌人
        for enemy in self.enemies:
            x, y = enemy['pos']
            center = (MAP_X + x*TILE_SIZE + TILE_SIZE//2, MAP_Y + y*TILE_SIZE + TILE_SIZE//2)
            pygame.draw.circle(self.screen, COLOR_ENEMY, center, TILE_SIZE//2 - 2)
            # 敌人血条
            bar_width = TILE_SIZE - 4
            bar_height = 4
            bar_x = MAP_X + x*TILE_SIZE + 2
            bar_y = MAP_Y + y*TILE_SIZE + 2
            pygame.draw.rect(self.screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            health_width = int(bar_width * enemy['hp'] / ENEMY_HP_INIT)
            pygame.draw.rect(self.screen, (200, 0, 0), (bar_x, bar_y, health_width, bar_height))
        
        # 绘制玩家
        px, py = self.player_pos
        center = (MAP_X + px*TILE_SIZE + TILE_SIZE//2, MAP_Y + py*TILE_SIZE + TILE_SIZE//2)
        pygame.draw.circle(self.screen, COLOR_PLAYER, center, TILE_SIZE//2 - 2)
        
        # HUD
        hud_y = MAP_Y + MAP_HEIGHT + 10
        lines = [
            f"HP: {self.player_hp}/{self.player_max_hp}",
            f"ATK: {self.player_atk}",
            f"LV: {self.player_lv}",
            f"EXP: {self.player_exp}/{EXP_TO_NEXT_LEVEL}",
            f"Floor: {self.floor}"
        ]
        for i, line in enumerate(lines):
            text = self.font.render(line, True, COLOR_HUD_TEXT)
            self.screen.blit(text, (MAP_X + i * 150, hud_y))
        
        # 操作提示
        tips = [
            "Arrow Keys: Move",
            "Space: Attack",
            "R: Restart",
            "ESC: Quit"
        ]
        for i, tip in enumerate(tips):
            text = self.small_font.render(tip, True, COLOR_HUD_TEXT)
            self.screen.blit(text, (MAP_X + MAP_WIDTH - 200, hud_y + i * 25))
        
        # 游戏结束遮罩
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(COLOR_GAME_OVER_BG)
            self.screen.blit(overlay, (0, 0))
            
            if self.victory:
                title = "VICTORY! You escaped the dungeon!"
            else:
                title = "GAME OVER"
            title_text = self.font.render(title, True, (255, 255, 200))
            restart_text = self.font.render("Press R to Restart", True, (200, 230, 255))
            
            self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        
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
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif not self.game_over:
                        self.handle_input(event.key)
            
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = DungeonGame()
    game.run()