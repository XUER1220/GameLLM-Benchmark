import pygame
import random
import sys

# ===== 固定参数 =====
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
# 地牢网格参数
GRID_WIDTH, GRID_HEIGHT = 21, 15
TILE_SIZE = 32
MAP_PIXEL_WIDTH = GRID_WIDTH * TILE_SIZE
MAP_PIXEL_HEIGHT = GRID_HEIGHT * TILE_SIZE
MAP_OFFSET_X = (SCREEN_WIDTH - MAP_PIXEL_WIDTH) // 2
MAP_OFFSET_Y = (SCREEN_HEIGHT - MAP_PIXEL_HEIGHT) // 2
# 颜色
COLOR_BG = (20, 20, 40)
COLOR_WALL = (60, 60, 80)
COLOR_FLOOR = (70, 70, 100)
COLOR_PLAYER = (50, 200, 50)
COLOR_ENEMY = (200, 50, 50)
COLOR_POTION = (50, 200, 200)
COLOR_WEAPON = (200, 200, 50)
COLOR_EXIT = (180, 50, 180)
COLOR_HUD_BG = (30, 30, 50, 180)
COLOR_HUD_TEXT = (240, 240, 240)
COLOR_GAME_OVER_BG = (0, 0, 0, 200)
# 玩家初始属性
PLAYER_HP_INIT = 20
PLAYER_ATK_INIT = 5
PLAYER_LV_INIT = 1
PLAYER_EXP_INIT = 0
# 敌人初始属性
ENEMY_HP_INIT = 8
ENEMY_ATK_INIT = 3
ENEMY_COUNT = 4
# 道具效果
POTION_HEAL = 8
WEAPON_ATK_BONUS = 2
# 经验与升级
EXP_PER_KILL = 5
EXP_TO_LEVEL = 10
LEVEL_HP_BONUS = 5
LEVEL_ATK_BONUS = 1
# 随机种子
random.seed(42)

# ===== Pygame 初始化 =====
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roguelike Dungeon Hard")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 48)

# ===== 游戏类定义 =====
class Game:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.floor = 1
        self.player = Player()
        self.dungeon = Dungeon()
        self.spawn_entities()
        self.game_over = False
        self.victory = False
    
    def spawn_entities(self):
        # 敌人
        self.enemies = []
        for _ in range(ENEMY_COUNT):
            pos = self.dungeon.random_floor_tile()
            if pos:
                self.enemies.append(Enemy(pos))
        # 药水
        self.potions = []
        for _ in range(2):
            pos = self.dungeon.random_floor_tile()
            if pos and pos not in [e.pos for e in self.enemies]:
                self.potions.append(Entity(pos, 'potion'))
        # 武器
        self.weapon = None
        pos = self.dungeon.random_floor_tile()
        if pos and pos not in [e.pos for e in self.enemies] and pos not in [p.pos for p in self.potions]:
            self.weapon = Entity(pos, 'weapon')
        # 出口
        self.exit = None
        pos = self.dungeon.random_floor_tile()
        if pos and pos not in [e.pos for e in self.enemies] and pos not in [p.pos for p in self.potions] and (self.weapon is None or pos != self.weapon.pos):
            self.exit = Entity(pos, 'exit')
    
    def handle_player_move(self, dx, dy):
        if self.game_over:
            return
        new_x = self.player.pos[0] + dx
        new_y = self.player.pos[1] + dy
        new_pos = (new_x, new_y)
        # 检查墙壁
        if not self.dungeon.is_floor(new_pos):
            return
        # 检查敌人碰撞
        for enemy in self.enemies[:]:
            if enemy.pos == new_pos:
                self.player.attack(enemy)
                if enemy.hp <= 0:
                    self.enemies.remove(enemy)
                    self.player.gain_exp(EXP_PER_KILL)
                return
        # 检查道具
        for potion in self.potions[:]:
            if potion.pos == new_pos:
                self.player.hp = min(self.player.max_hp, self.player.hp + POTION_HEAL)
                self.potions.remove(potion)
                break
        # 检查武器
        if self.weapon and new_pos == self.weapon.pos:
            self.player.atk += WEAPON_ATK_BONUS
            self.weapon = None
        # 检查出口
        if self.exit and new_pos == self.exit.pos:
            self.next_floor()
            return
        # 移动玩家
        self.player.pos = new_pos
        # 敌人回合
        for enemy in self.enemies:
            enemy.move_towards(self.player.pos, self.dungeon)
            if enemy.pos == self.player.pos:
                enemy.attack(self.player)
                if self.player.hp <= 0:
                    self.game_over = True
    
    def next_floor(self):
        self.floor += 1
        self.dungeon = Dungeon()
        self.spawn_entities()
        # 重置玩家位置到随机地面
        pos = self.dungeon.random_floor_tile()
        if pos:
            self.player.pos = pos
    
    def draw(self, screen):
        # 背景
        screen.fill(COLOR_BG)
        # 绘制地图
        self.dungeon.draw(screen)
        # 绘制出口
        if self.exit:
            pygame.draw.rect(screen, COLOR_EXIT, (MAP_OFFSET_X + self.exit.pos[0]*TILE_SIZE, MAP_OFFSET_Y + self.exit.pos[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        # 绘制武器
        if self.weapon:
            pygame.draw.rect(screen, COLOR_WEAPON, (MAP_OFFSET_X + self.weapon.pos[0]*TILE_SIZE, MAP_OFFSET_Y + self.weapon.pos[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        # 绘制药水
        for potion in self.potions:
            pygame.draw.rect(screen, COLOR_POTION, (MAP_OFFSET_X + potion.pos[0]*TILE_SIZE, MAP_OFFSET_Y + potion.pos[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        # 绘制敌人
        for enemy in self.enemies:
            enemy.draw(screen)
        # 绘制玩家
        self.player.draw(screen)
        # HUD
        self.draw_hud(screen)
        # 游戏结束画面
        if self.game_over:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill(COLOR_GAME_OVER_BG)
            screen.blit(s, (0,0))
            text = big_font.render("GAME OVER", True, COLOR_ENEMY)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            sub = font.render("Press R to Restart", True, COLOR_HUD_TEXT)
            screen.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, SCREEN_HEIGHT//2 + 20))
        elif self.victory:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill(COLOR_GAME_OVER_BG)
            screen.blit(s, (0,0))
            text = big_font.render("VICTORY!", True, COLOR_EXIT)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            sub = font.render("Press R to Restart", True, COLOR_HUD_TEXT)
            screen.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, SCREEN_HEIGHT//2 + 20))
    
    def draw_hud(self, screen):
        hud_rect = pygame.Rect(10, 10, 200, 120)
        pygame.draw.rect(screen, COLOR_HUD_BG, hud_rect)
        info = [
            f"HP: {self.player.hp}/{self.player.max_hp}",
            f"ATK: {self.player.atk}",
            f"LV: {self.player.lv}",
            f"EXP: {self.player.exp}/{EXP_TO_LEVEL}",
            f"Floor: {self.floor}",
            f"Enemies: {len(self.enemies)}",
            f"Potions: {len(self.potions)}",
            f"Weapon: {'Picked' if self.weapon is None else 'Available'}"
        ]
        for i, line in enumerate(info):
            text = font.render(line, True, COLOR_HUD_TEXT)
            screen.blit(text, (hud_rect.x + 10, hud_rect.y + 10 + i*20))

class Dungeon:
    def __init__(self):
        self.grid = [[1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.rooms = []
        self.generate()
    
    def generate(self):
        # 生成房间
        for _ in range(6):
            w = random.randint(4, 6)
            h = random.randint(4, 6)
            x = random.randint(1, GRID_WIDTH - w - 1)
            y = random.randint(1, GRID_HEIGHT - h - 1)
            self.rooms.append((x, y, w, h))
        # 绘制房间
        for rx, ry, rw, rh in self.rooms:
            for y in range(ry, ry+rh):
                for x in range(rx, rx+rw):
                    self.grid[y][x] = 0
        # 连通房间
        for i in range(len(self.rooms)-1):
            x1 = self.rooms[i][0] + self.rooms[i][2]//2
            y1 = self.rooms[i][1] + self.rooms[i][3]//2
            x2 = self.rooms[i+1][0] + self.rooms[i+1][2]//2
            y2 = self.rooms[i+1][1] + self.rooms[i+1][3]//2
            # 水平走廊
            for x in range(min(x1, x2), max(x1, x2)+1):
                self.grid[y1][x] = 0
            # 垂直走廊
            for y in range(min(y1, y2), max(y1, y2)+1):
                self.grid[y][x2] = 0
    
    def is_floor(self, pos):
        x, y = pos
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            return self.grid[y][x] == 0
        return False
    
    def random_floor_tile(self):
        floor_tiles = []
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] == 0:
                    floor_tiles.append((x, y))
        if floor_tiles:
            return random.choice(floor_tiles)
        return None
    
    def draw(self, screen):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = COLOR_FLOOR if self.grid[y][x] == 0 else COLOR_WALL
                pygame.draw.rect(screen, color, (MAP_OFFSET_X + x*TILE_SIZE, MAP_OFFSET_Y + y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(screen, (COLOR_BG), (MAP_OFFSET_X + x*TILE_SIZE, MAP_OFFSET_Y + y*TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

class Player:
    def __init__(self):
        self.max_hp = PLAYER_HP_INIT
        self.hp = self.max_hp
        self.atk = PLAYER_ATK_INIT
        self.lv = PLAYER_LV_INIT
        self.exp = PLAYER_EXP_INIT
        self.pos = (0, 0)
    
    def gain_exp(self, amount):
        self.exp += amount
        while self.exp >= EXP_TO_LEVEL:
            self.exp -= EXP_TO_LEVEL
            self.lv += 1
            self.max_hp += LEVEL_HP_BONUS
            self.hp = self.max_hp
            self.atk += LEVEL_ATK_BONUS
    
    def attack(self, enemy):
        enemy.hp -= self.atk
    
    def draw(self, screen):
        pygame.draw.rect(screen, COLOR_PLAYER, (MAP_OFFSET_X + self.pos[0]*TILE_SIZE, MAP_OFFSET_Y + self.pos[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE))

class Enemy:
    def __init__(self, pos):
        self.max_hp = ENEMY_HP_INIT
        self.hp = self.max_hp
        self.atk = ENEMY_ATK_INIT
        self.pos = pos
    
    def move_towards(self, player_pos, dungeon):
        px, py = player_pos
        ex, ey = self.pos
        dx = 0
        dy = 0
        if abs(px - ex) > abs(py - ey):
            dx = 1 if px > ex else -1
        else:
            dy = 1 if py > ey else -1
        new_pos = (ex + dx, ey + dy)
        if dungeon.is_floor(new_pos):
            self.pos = new_pos
    
    def attack(self, player):
        player.hp -= self.atk
    
    def draw(self, screen):
        pygame.draw.rect(screen, COLOR_ENEMY, (MAP_OFFSET_X + self.pos[0]*TILE_SIZE, MAP_OFFSET_Y + self.pos[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE))

class Entity:
    def __init__(self, pos, type):
        self.pos = pos
        self.type = type

# ===== 主循环 =====
def main():
    game = Game()
    # 初始位置
    pos = game.dungeon.random_floor_tile()
    if pos:
        game.player.pos = pos
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game.reset()
                elif not game.game_over and not game.victory:
                    dx, dy = 0, 0
                    if event.key == pygame.K_UP:
                        dy = -1
                    elif event.key == pygame.K_DOWN:
                        dy = 1
                    elif event.key == pygame.K_LEFT:
                        dx = -1
                    elif event.key == pygame.K_RIGHT:
                        dx = 1
                    if dx != 0 or dy != 0:
                        game.handle_player_move(dx, dy)
        
        # 绘制
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()