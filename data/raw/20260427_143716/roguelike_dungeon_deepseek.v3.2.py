import pygame
import random
import sys

# 初始化设置
pygame.init()
WIDTH, HEIGHT = 800, 600
GRID_WIDTH, GRID_HEIGHT = 21, 15
TILE_SIZE = 32
MAP_WIDTH, MAP_HEIGHT = GRID_WIDTH * TILE_SIZE, GRID_HEIGHT * TILE_SIZE
MAP_X, MAP_Y = (WIDTH - MAP_WIDTH) // 2, (HEIGHT - MAP_HEIGHT) // 2
FPS = 60
SEED = 42
random.seed(SEED)

# 颜色定义 - 符合可区分要求
COLOR_BG = (20, 20, 40)
COLOR_WALL = (60, 60, 100)
COLOR_FLOOR = (80, 70, 60)
COLOR_PLAYER = (240, 240, 80)
COLOR_ENEMY = (220, 50, 50)
COLOR_POTION = (50, 220, 120)
COLOR_WEAPON = (200, 150, 50)
COLOR_EXIT = (80, 180, 240)
COLOR_HUD_BG = (30, 30, 50, 200)
COLOR_HUD_TEXT = (220, 220, 220)
COLOR_WHITE = (255, 255, 255)
COLOR_GAME_OVER_BG = (0, 0, 0, 180)
COLOR_STATUS_BAR = (70, 70, 100)

# 游戏常量
PLAYER_HP_INIT = 20
PLAYER_ATK_INIT = 5
PLAYER_LV_INIT = 1
PLAYER_EXP_INIT = 0
ENEMY_HP_INIT = 8
ENEMY_ATK_INIT = 3
ENEMY_COUNT = 4
POTION_COUNT = 2
WEAPON_COUNT = 1
POTION_HEAL = 8
WEAPON_BONUS = 2
EXP_PER_KILL = 5
EXP_TO_LEVEL = 10
LEVEL_HP_BONUS = 5
LEVEL_ATK_BONUS = 1

# 游戏状态枚举
class GameState:
    PLAYING = 0
    GAME_OVER = 1
    VICTORY = 2

def generate_map():
    """生成包含房间和走廊的地牢地图"""
    # 创建全墙地图
    grid = [[1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    rooms = []
    
    # 生成房间
    for _ in range(6):
        room_width = random.randint(4, 7)
        room_height = random.randint(4,10)
        x = random.randint(1, GRID_WIDTH - room_width - 1)
        y = random.randint(1, GRID_HEIGHT - room_height - 1)
        
        # 检查房间重叠
        overlap = False
        for rx, ry, rw, rh in rooms:
            if not (x + room_width < rx - 1 or x > rx + rw + 1 or 
                    y + room_height < ry - 1 or y > ry + rh + 1):
                overlap = True
                break
        
        if not overlap:
            rooms.append((x, y, room_width, room_height))
            for dy in range(room_height):
                for dx in range(room_width):
                    grid[y + dy][x + dx] = 0
    
    # 连接房间
    for i in range(len(rooms) - 1):
        x1, y1, w1, h1 = rooms[i]
        x2, y2, w2, h2 = rooms[i + 1]
        
        center_x1, center_y1 = x1 + w1 // 2, y1 + h1 // 2
        center_x2, center_y2 = x2 + w2 // 2, y2 + h2 // 2
        
        # 水平走廊
        step_x = 1 if center_x2 > center_x1 else -1
        for x in range(center_x1, center_x2 + step_x, step_x):
            if 0 <= x < GRID_WIDTH:
                grid[center_y1][x] = 0
        
        # 垂直走廊
        step_y = 1 if center_y2 > center_y1 else -1
        for y in range(center_y1, center_y2 + step_y, step_y):
            if 0 <= y < GRID_HEIGHT:
                if 0 <= center_x2 < GRID_WIDTH:
                    grid[y][center_x2] = 0
    
    return grid

def find_empty_tile(grid):
    """在地板上找到随机空位置"""
    while True:
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        if grid[y][x] == 0:
            return (x, y)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_hp = PLAYER_HP_INIT
        self.hp = self.max_hp
        self.atk = PLAYER_ATK_INIT
        self.lv = PLAYER_LV_INIT
        self.exp = PLAYER_EXP_INIT
        self.turn = True
        
    def move(self, dx, dy, grid, entities):
        """玩家移动"""
        new_x, new_y = self.x + dx, self.y + dy
        
        # 检查边界和墙壁
        if not (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT):
            return False
        if grid[new_y][new_x] == 1:
            return False
        
        self.x, self.y = new_x, new_y
        self.turn = False
        return True
    
    def attack(self, enemy):
        """攻击敌人"""
        damage = self.atk
        enemy.hp -= damage
        return damage
    
    def take_damage(self, damage):
        """受到伤害"""
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
    
    def heal(self, amount):
        """恢复生命值"""
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
    
    def gain_exp(self, amount):
        """获得经验"""
        self.exp += amount
        if self.exp >= EXP_TO_LEVEL:
            self.level_up()
    
    def level_up(self):
        """升级"""
        self.lv += 1
        self.exp = max(0, self.exp - EXP_TO_LEVEL)
        self.max_hp += LEVEL_HP_BONUS
        self.hp = self.max_hp
        self.atk += LEVEL_ATK_BONUS

class Enemy:
    def __init__(self, x, y, enemy_id):
        self.x = x
        self.y = y
        self.id = enemy_id
        self.max_hp = ENEMY_HP_INIT
        self.hp = self.max_hp
        self.atk = ENEMY_ATK_INIT
    
    def move_towards(self, target_x, target_y, grid, entities):
        """向玩家移动"""
        dx, dy = 0, 0
        
        # 简单AI：优先移动更接近玩家的方向
        if abs(self.x - target_x) > abs(self.y - target_y):
            if self.x < target_x:
                dx = 1
            elif self.x > target_x:
                dx = -1
        else:
            if self.y < target_y:
                dy = 1
            elif self.y > target_y:
                dy = -1
        
        new_x, new_y = self.x + dx, self.y + dy
        
        # 检查是否可以移动
        if (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and 
            grid[new_y][new_x] == 0):
            # 检查是否与其他实体重叠
            can_move = True
            for entity in entities:
                if hasattr(entity, 'x') and entity.x == new_x and entity.y == new_y:
                    can_move = False
                    break
            
            if can_move:
                self.x, self.y = new_x, new_y

class Potion:
    def __init__(self, x, y, potion_id):
        self.x = x
        self.y = y
        self.id = potion_id

class Weapon:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Exit:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Roguelike Dungeon Hard")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 20)
        self.big_font = pygame.font.SysFont('Arial', 40)
        self.reset()
    
    def reset(self):
        """重置游戏"""
        self.state = GameState.PLAYING
        self.floor = 1
        self.generate_level()
    
    def generate_level(self):
        """生成新的一层"""
        self.grid = generate_map()
        self.entities = []
        self.enemies = []
        self.potions = []
        
        # 放置玩家
        if self.floor == 1:
            player_pos = find_empty_tile(self.grid)
            self.player = Player(player_pos[0], player_pos[1])
        else:
            # 保持玩家属性，但重新放置位置
            player_pos = find_empty_tile(self.grid)
            self.player.x, self.player.y = player_pos[0], player_pos[1]
        
        # 放置敌人
        for i in range(ENEMY_COUNT):
            pos = find_empty_tile(self.grid)
            enemy = Enemy(pos[0], pos[1], i)
            self.enemies.append(enemy)
            self.entities.append(enemy)
        
        # 放置药水
        for i in range(POTION_COUNT):
            pos = find_empty_tile(self.grid)
            potion = Potion(pos[0], pos[1], i)
            self.potions.append(potion)
            self.entities.append(potion)
        
        # 放置武器
        weapon_pos = find_empty_tile(self.grid)
        self.weapon = Weapon(weapon_pos[0], weapon_pos[1])
        self.entities.append(self.weapon)
        
        # 放置出口
        exit_pos = find_empty_tile(self.grid)
        self.exit = Exit(exit_pos[0], exit_pos[1])
        self.entities.append(self.exit)
        
        # 重置玩家回合
        self.player.turn = True
    
    def handle_events(self):
        """处理输入事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
                if event.key == pygame.K_r and self.state != GameState.PLAYING:
                    self.reset()
                    return
                
                if self.state == GameState.PLAYING and self.player.turn:
                    moved = False
                    if event.key == pygame.K_UP:
                        moved = self.player.move(0, -1, self.grid, self.entities)
                    elif event.key == pygame.K_DOWN:
                        moved = self.player.move(0, 1, self.grid, self.entities)
                    elif event.key == pygame.K_LEFT:
                        moved = self.player.move(-1, 0, self.grid, self.entities)
                    elif event.key == pygame.K_RIGHT:
                        moved = self.player.move(1, 0, self.grid, self.entities)
                    
                    if moved:
                        self.handle_player_action()
    
    def handle_player_action(self):
        """处理玩家行动后的逻辑"""
        # 检查是否拾取道具
        for entity in self.entities[:]:
            if entity.x == self.player.x and entity.y == self.player.y:
                if isinstance(entity, Potion):
                    self.player.heal(POTION_HEAL)
                    self.entities.remove(entity)
                    self.potions.remove(entity)
                elif isinstance(entity, Weapon):
                    self.player.atk += WEAPON_BONUS
                    self.entities.remove(entity)
                elif isinstance(entity, Exit):
                    self.floor += 1
                    if self.floor > 2:
                        self.state = GameState.VICTORY
                    else:
                        self.generate_level()
                    return
        
        # 检查是否与敌人相邻并攻击
        for enemy in self.enemies[:]:
            if (abs(enemy.x - self.player.x) + abs(enemy.y - self.player.y) == 1 and
                enemy.hp > 0):
                damage = self.player.attack(enemy)
                if enemy.hp <= 0:
                    self.player.gain_exp(EXP_PER_KILL)
                    self.entities.remove(enemy)
                    self.enemies.remove(enemy)
        
        # 敌人回合
        self.enemy_turn()
        
        # 重置玩家回合
        self.player.turn = True
        
        # 检查游戏结束
        if self.player.hp <= 0:
            self.state = GameState.GAME_OVER
    
    def enemy_turn(self):
        """敌人行动回合"""
        for enemy in self.enemies:
            if enemy.hp > 0:
                # 检查是否与玩家相邻
                if abs(enemy.x - self.player.x) + abs(enemy.y - self.player.y) == 1:
                    # 攻击玩家
                    self.player.take_damage(enemy.atk)
                else:
                    # 向玩家移动
                    enemy.move_towards(self.player.x, self.player.y, self.grid, self.entities)
    
    def draw(self):
        """绘制游戏"""
        self.screen.fill(COLOR_BG)
        
        # 绘制地图
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    MAP_X + x * TILE_SIZE,
                    MAP_Y + y * TILE_SIZE,
                    TILE_SIZE, TILE_SIZE
                )
                
                if self.grid[y][x] == 1:  # 墙壁
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                    pygame.draw.rect(self.screen, (40, 40, 80), rect, 2)
                else:  # 地板
                    pygame.draw.rect(self.screen, COLOR_FLOOR, rect)
                    pygame.draw.rect(self.screen, (60, 50, 40), rect, 1)
        
        # 绘制实体
        for entity in self.entities:
            rect = pygame.Rect(
                MAP_X + entity.x * TILE_SIZE,
                MAP_Y + entity.y * TILE_SIZE,
                TILE_SIZE, TILE_SIZE
            )
            
            if isinstance(entity, Player):
                pygame.draw.rect(self.screen, COLOR_PLAYER, rect)
                pygame.draw.rect(self.screen, (200, 200, 60), rect, 2)
            elif isinstance(entity, Enemy):
                pygame.draw.rect(self.screen, COLOR_ENEMY, rect)
                pygame.draw.rect(self.screen, (180, 30, 30), rect, 2)
            elif isinstance(entity, Potion):
                pygame.draw.circle(self.screen, COLOR_POTION, rect.center, TILE_SIZE // 3)
                pygame.draw.circle(self.screen, (30, 180, 90), rect.center, TILE_SIZE // 3, 2)
            elif isinstance(entity, Weapon):
                pygame.draw.polygon(self.screen, COLOR_WEAPON, [
                    (rect.centerx, rect.top + 4),
                    (rect.left + 8, rect.bottom - 4),
                    (rect.right - 8, rect.bottom - 4)
                ])
            elif isinstance(entity, Exit):
                pygame.draw.rect(self.screen, COLOR_EXIT, rect, 4)
                pygame.draw.rect(self.screen, (60, 140, 200), rect, 1)
        
        # 绘制玩家（确保在最上层）
        player_rect = pygame.Rect(
            MAP_X + self.player.x * TILE_SIZE,
            MAP_Y + self.player.y * TILE_SIZE,
            TILE_SIZE, TILE_SIZE
        )
        pygame.draw.rect(self.screen, COLOR_PLAYER, player_rect)
        pygame.draw.rect(self.screen, (200, 200, 60), player_rect, 2)
        
        # 绘制HUD
        self.draw_hud()
        
        # 绘制游戏结束/胜利画面
        if self.state != GameState.PLAYING:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_hud(self):
        """绘制状态栏"""
        # HUD背景
        hud_rect = pygame.Rect(0, 0, WIDTH, MAP_Y)
        pygame.draw.rect(self.screen, COLOR_HUD_BG, hud_rect)
        
        # 状态条
        hp_percent = self.player.hp / self.player.max_hp
        hp_bar_rect = pygame.Rect(20, 20, 200, 20)
        pygame.draw.rect(self.screen, COLOR_STATUS_BAR, hp_bar_rect)
        pygame.draw.rect(self.screen, (220, 50, 50), 
                         (hp_bar_rect.x, hp_bar_rect.y, 
                          int(hp_bar_rect.width * hp_percent), hp_bar_rect.height))
        pygame.draw.rect(self.screen, COLOR_WHITE, hp_bar_rect, 1)
        
        exp_percent = min(self.player.exp / EXP_TO_LEVEL, 1.0)
        exp_bar_rect = pygame.Rect(20, 50, 200, 15)
        pygame.draw.rect(self.screen, COLOR_STATUS_BAR, exp_bar_rect)
        pygame.draw.rect(self.screen, (80, 180, 240), 
                         (exp_bar_rect.x, exp_bar_rect.y, 
                          int(exp_bar_rect.width * exp_percent), exp_bar_rect.height))
        pygame.draw.rect(self.screen, COLOR_WHITE, exp_bar_rect, 1)
        
        # 文本信息
        hp_text = self.font.render(f"HP: {self.player.hp}/{self.player.max_hp}", True, COLOR_HUD_TEXT)
        self.screen.blit(hp_text, (230, 18))
        
        atk_text = self.font.render(f"ATK: {self.player.atk}", True, COLOR_HUD_TEXT)
        self.screen.blit(atk_text, (400, 18))
        
        lv_text = self.font.render(f"LV: {self.player.lv}", True, COLOR_HUD_TEXT)
        self.screen.blit(lv_text, (500, 18))
        
        exp_text = self.font.render(f"EXP: {self.player.exp}/{EXP_TO_LEVEL}", True, COLOR_HUD_TEXT)
        self.screen.blit(exp_text, (230, 48))
        
        floor_text = self.font.render(f"Floor: {self.floor}/2", True, COLOR_HUD_TEXT)
        self.screen.blit(floor_text, (400, 48))
        
        # 控制提示
        controls_text = self.font.render("Arrow Keys: Move | R: Restart | ESC: Quit", True, COLOR_HUD_TEXT)
        self.screen.blit(controls_text, (20, HEIGHT - MAP_Y + 10))
    
    def draw_game_over(self):
        """绘制游戏结束画面"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLOR_GAME_OVER_BG)
        self.screen.blit(overlay, (0, 0))
        
        if self.state == GameState.GAME_OVER:
            text = self.big_font.render("GAME OVER", True, (220, 50, 50))
        else:
            text = self.big_font.render("VICTORY!", True, (80, 180, 240))
        
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        self.screen.blit(text, text_rect)
        
        restart_text = self.font.render("Press R to Restart", True, COLOR_WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        """运行游戏主循环"""
        while True:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()