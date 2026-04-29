import pygame
import random
import sys

# 固定常量
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 32
MAP_COLS, MAP_ROWS = 21, 15
HUD_X, HUD_Y = 0, 0
FPS = 60

# 游戏状态
PLAYING, GAME_OVER = 0, 1

# 颜色
COLOR_WALL = (64, 64, 64)
COLOR_FLOOR = (20, 20, 30)
COLOR_PLAYER = (0, 200, 0)
COLOR_ENEMY = (200, 0, 0)
COLOR_POTION = (0, 0, 200)
COLOR_WEAPON = (200, 200, 0)
COLOR_EXIT = (0, 200, 200)
COLOR_TEXT = (255, 255, 255)

# 玩家初始属性
INIT_PLAYER_HP = 20
INIT_PLAYER_ATK = 5
INIT_PLAYER_LV = 1
INIT_PLAYER_EXP = 0

# 敌人属性
INIT_ENEMY_HP = 8
INIT_ENEMY_ATK = 3

# 道具与经验
POTION_HP-heal = 8
WEAPON_ATKBoost = 2
EXP_PER_ENEMY = 5
EXP_TO_LEVEL_UP = 10
LEVEL_UP_HP_BONUS = 5

# 固定种子
random.seed(42)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = INIT_PLAYER_HP
        self.max_hp = INIT_PLAYER_HP
        self.atk = INIT_PLAYER_ATK
        self.level = INIT_PLAYER_LV
        self.exp = INIT_PLAYER_EXP
        self.floor = 1


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = INIT_ENEMY_HP
        self.atk = INIT_ENEMY_ATK


class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.type = item_type  # 'potion' or 'weapon'


class Game:
    def __init__(self):
        self.map_data = []
        self.player = None
        self.enemies = []
        self.items = []
        self.exit_tile = None
        self.state = PLAYING
        self.generate_dungeon()

    def generate_dungeon(self):
        # 初始化地图全为墙
        self.map_data = [[1 for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
        self.enemies = []
        self.items = []
        
        # 生成6个房间（room size 3x3 to 5x5）
        rooms = []
        min_room_size = 3
        max_room_size = 5
        
        for _ in range(6):
            w = random.randint(min_room_size, max_room_size)
            h = random.randint(min_room_size, max_room_size)
            x = random.randint(1, MAP_COLS - w - 1)
            y = random.randint(1, MAP_ROWS - h - 1)
            
            # 排除太靠近边缘或重叠太严重的
            for rx in range(x, x + w):
                for ry in range(y, y + h):
                    self.map_data[ry][rx] = 0
            
            room_center = (x + w // 2, y + h // 2)
            rooms.append((x, y, w, h, room_center))
        
        # 连接相邻房间：按顺序连接，形成走廊
        for i in range(len(rooms) - 1):
            cx1, cy1 = rooms[i][4]
            cx2, cy2 = rooms[i + 1][4]
            
            # L型走廊：先横后竖 或 先竖后横
            if random.random() < 0.5:
                # 先横向
                x_start, x_end = min(cx1, cx2), max(cx1, cx2)
                for x in range(x_start, x_end + 1):
                    self.map_data[cy1][x] = 0
                y_start, y_end = min(cy1, cy2), max(cy1, cy2)
                for y in range(y_start, y_end + 1):
                    self.map_data[y][cx2] = 0
            else:
                # 先竖向
                y_start, y_end = min(cy1, cy2), max(cy1, cy2)
                for y in range(y_start, y_end + 1):
                    self.map_data[y][cx1] = 0
                x_start, x_end = min(cx1, cx2), max(cx1, cx2)
                for x in range(x_start, x_end + 1):
                    self.map_data[cy2][x] = 0
        
        # 确保房间边界无单格墙壁穿透（确保连通）
        # ——忽略，依赖种子决定生成稳定性
        
        # 玩家位置：第一个房间中心
        px, py = rooms[0][4]
        self.player = Player(px, py)
        
        # 出口位置：最后一个房间中心
        ex, ey = rooms[-1][4]
        self.exit_tile = (ex, ey)
        
        # 敌人：前5个房间（跳过首末），每房间1个；确保不与玩家/出口重叠
        for i in range(1, len(rooms) - 1):
            rx, ry, w, h, _ = rooms[i]
            tried = set()
            while True:
                x = random.randint(rx, rx + w - 1)
                y = random.randint(ry, ry + h - 1)
                if (x, y) != (px, py) and (x, y) != (ex, ey) and (x, y) not in tried:
                    tried.add((x, y))
                    break
            self.enemies.append(Enemy(x, y))
        
        # 补足4个敌人（若不足）
        while len(self.enemies) < 4:
            while True:
                x = random.randint(1, MAP_COLS - 2)
                y = random.randint(1, MAP_ROWS - 2)
                if self.map_data[y][x] == 0 and (x, y) != (px, py) and (x, y) != (ex, ey) and not any(e.x == x and e.y == y for e in self.enemies):
                    self.enemies.append(Enemy(x, y))
                    break
        
        # 道具：2药水+1武器，避免重叠 & 玩家/敌人/出口
        item_count = 0
        item_types = ['potion', 'potion', 'weapon']
        while item_count < 3:
            x = random.randint(1, MAP_COLS - 2)
            y = random.randint(1, MAP_ROWS - 2)
            if self.map_data[y][x] == 0 and (x, y) != (px, py) and (x, y) != (ex, ey) \
               and not any(e.x == x and e.y == y for e in self.enemies) \
               and not any(it.x == x and it.y == y for it in self.items):
                self.items.append(Item(x, y, item_types[item_count]))
                item_count += 1

    def move_player(self, dx, dy):
        if self.state != PLAYING:
            return
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        
        if self.map_data[new_y][new_x] == 0:
            # 检查敌人碰撞
            enemy_idx = None
            for i, e in enumerate(self.enemies):
                if e.x == new_x and e.y == new_y:
                    enemy_idx = i
                    break
            
            if enemy_idx is not None:
                # 战斗
                enemy = self.enemies[enemy_idx]
                damage = self.player.atk
                enemy.hp -= damage
                if enemy.hp <= 0:
                    # 消除敌人
                    self.enemies.pop(enemy_idx)
                    self.player.exp += EXP_PER_ENEMY
                    self.check_level_up()
            else:
                # 移动
                self.player.x = new_x
                self.player.y = new_y
                
                # 检查道具
                for i, item in enumerate(self.items):
                    if item.x == new_x and item.y == new_y:
                        if item.type == 'potion':
                            heal_amount = min(POTION_HP_heal, self.player.max_hp - self.player.hp)
                            self.player.hp += heal_amount
                        elif item.type == 'weapon':
                            self.player.atk += WEAPON_ATKBoost
                        self.items.pop(i)
                        break
                
                # 检查出口
                if self.exit_tile and self.player.x == self.exit_tile[0] and self.player.y == self.exit_tile[1]:
                    self.player.floor += 1
                    if self.player.floor > 2:  # 至少2层
                        self.state = GAME_OVER
                        return
                    self.generate_dungeon()
                    return
                
                # 敌人回合
                self.enemy_turn()
    
    def check_level_up(self):
        if self.player.exp >= EXP_TO_LEVEL_UP:
            self.player.level += 1
            self.player.exp -= EXP_TO_LEVEL_UP
            self.player.max_hp += LEVEL_UP_HP_BONUS
            self.player.hp = self.player.max_hp
            self.player.atk += 1
    
    def enemy_turn(self):
        player = self.player
        for enemy in self.enemies:
            dx = player.x - enemy.x
            dy = player.y - enemy.y
            
            # 在玩家相邻时（曼哈顿距离 <= 2）考虑移动
            if abs(dx) + abs(dy) <= 2:
                if abs(dx) > abs(dy):
                    move_dx = 1 if dx > 0 else -1
                    move_dy = 0
                else:
                    move_dx = 0
                    move_dy = 1 if dy > 0 else -1
                
                new_x = enemy.x + move_dx
                new_y = enemy.y + move_dy
                
                if self.map_data[new_y][new_x] == 0:
                    # 如果没碰到玩家，则移动
                    if not (new_x == player.x and new_y == player.y):
                        # 检查是否被另一个敌人阻挡
                        blocked = False
                        for e in self.enemies:
                            if e.x == new_x and e.y == new_y and e != enemy:
                                blocked = True
                                break
                        if not blocked:
                            enemy.x, enemy.y = new_x, new_y
                    else:
                        # 攻击玩家
                        player.hp -= enemy.atk
                        if player.hp <= 0:
                            self.state = GAME_OVER
                            return
                else:
                    # 墙壁阻挡，直接攻击（如果 adjacent）
                    pass
            else:
                # 远离则不移动
                pass
    
    def draw(self, screen):
        # 绘制地图
        offset_x = (WIDTH - MAP_COLS * TILE_SIZE) // 2
        offset_y = (HEIGHT - MAP_ROWS * TILE_SIZE) // 2
        
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                rect = pygame.Rect(offset_x + x * TILE_SIZE, offset_y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, COLOR_FLOOR, rect)
        
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                if self.map_data[y][x] == 1:
                    rect = pygame.Rect(offset_x + x * TILE_SIZE, offset_y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, COLOR_WALL, rect)
        
        # 绘制出口
        if self.exit_tile:
            ex, ey = self.exit_tile
            rect = pygame.Rect(offset_x + ex * TILE_SIZE, offset_y + ey * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, COLOR_EXIT, rect)
        
        # 绘制道具
        for item in self.items:
            rect = pygame.Rect(offset_x + item.x * TILE_SIZE, offset_y + item.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            color = COLOR_POTION if item.type == 'potion' else COLOR_WEAPON
            pygame.draw.rect(screen, color, rect)
        
        # 绘制敌人
        for enemy in self.enemies:
            rect = pygame.Rect(offset_x + enemy.x * TILE_SIZE, offset_y + enemy.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, COLOR_ENEMY, rect)
        
        # 绘制玩家
        rect = pygame.Rect(offset_x + self.player.x * TILE_SIZE, offset_y + self.player.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, COLOR_PLAYER, rect)
        
        # HUD
        hud_surface = pygame.Surface((WIDTH, 80))
        hud_surface.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 24)
        
        lines = [
            f"Floor: {self.player.floor}",
            f"Level: {self.player.level}",
            f"HP: {self.player.hp}/{self.player.max_hp}",
            f"ATK: {self.player.atk}",
            f"EXP: {self.player.exp}/{EXP_TO_LEVEL_UP}",
            "",
        ]
        
        for i, line in enumerate(lines):
            text = font.render(line, True, COLOR_TEXT)
            hud_surface.blit(text, (10, 10 + i * 24))
        
        # 如果游戏结束
        if self.state == GAME_OVER:
            end_text1 = font.render("You Win!" if self.player.floor >= 2 else "Game Over", True, COLOR_TEXT)
            end_text2 = font.render("Press R to Restart", True, COLOR_TEXT)
            hud_surface.blit(end_text1, (WIDTH // 2 - end_text1.get_width() // 2, 10))
            hud_surface.blit(end_text2, (WIDTH // 2 - end_text2.get_width() // 2, 40))
        
        screen.blit(hud_surface, (HUD_X, HUD_Y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Roguelike Dungeon Hard")
    clock = pygame.time.Clock()
    
    game = Game()
    font = pygame.font.SysFont(None, 24)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game.state == GAME_OVER:
                    game = Game()
                elif game.state == PLAYING:
                    if event.key == pygame.K_UP:
                        game.move_player(0, -1)
                    elif event.key == pygame.K_DOWN:
                        game.move_player(0, 1)
                    elif event.key == pygame.K_LEFT:
                        game.move_player(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        game.move_player(1, 0)
        
        screen.fill((0, 0, 0))
        game.draw(screen)
        
        # 屏幕未显示文字提示（HUD部分包含必要信息）
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()