import pygame
import random
import sys

# 固定参数
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_COLS = 21
GRID_ROWS = 15
GRID_SIZE = 32
MAP_WIDTH = GRID_COLS * GRID_SIZE
MAP_HEIGHT = GRID_ROWS * GRID_SIZE
FPS = 60
NUM_ROOMS = 6
NUM_ENEMIES = 4
NUM_POTIONS = 2
NUM_WEAPONS = 1

# 颜色常量
COLOR_WALL = (64, 64, 64)
COLOR_FLOOR = (32, 32, 40)
COLOR_PLAYER = (0, 255, 0)
COLOR_ENEMY = (255, 0, 0)
COLOR_POTION = (0, 255, 255)
COLOR_WEAPON = (255, 255, 0)
COLOR_EXIT = (255, 255, 255)
COLOR_HUD_BG = (10, 10, 20)
COLOR_HUD_TEXT = (255, 255, 255)
COLOR_MESSAGE_TEXT = (255, 255, 100)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Roguelike Dungeon Hard")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 48)
        self.running = True
        self.restart()

    def restart(self):
        random.seed(42)
        self.floor = 1
        self.map_data = []
        self.entities = []
        self.player = {
            'x': 0, 'y': 0,
            'hp': 20, 'max_hp': 20,
            'atk': 5,
            'level': 1,
            'exp': 0,
            'exp_needed': 10,
            'in_dungeon': True
        }
        self.generate_dungeon()
        self.game_over = False
        self.game_won = False
        self.messages = []

    def generate_dungeon(self):
        # 初始化墙壁地图
        self.map_data = [[1] * GRID_COLS for _ in range(GRID_ROWS)]

        # 生成房间列表
        rooms = []
        attempts = 0
        while len(rooms) < NUM_ROOMS and attempts < 1000:
            attempts += 1
            w = random.randint(4, 8)
            h = random.randint(4, 6)
            x = random.randint(1, GRID_COLS - w - 1)
            y = random.randint(1, GRID_ROWS - h - 1)

            new_room = (x, y, w, h)

            # 检查是否与已有房间重叠
            overlap = False
            for ex_x, ex_y, ex_w, ex_h in rooms:
                if x < ex_x + ex_w + 1 and x + w + 1 > ex_x and y < ex_y + ex_h + 1 and y + h + 1 > ex_y:
                    overlap = True
                    break
            if not overlap:
                rooms.append(new_room)
                # 标记房间区域为地板
                for i in range(y, y + h):
                    for j in range(x, x + w):
                        self.map_data[i][j] = 0

        # 连接房间
        for i in range(len(rooms) - 1):
            x1, y1, w1, h1 = rooms[i]
            x2, y2, w2, h2 = rooms[i + 1]
            center1 = (x1 + w1 // 2, y1 + h1 // 2)
            center2 = (x2 + w2 // 2, y2 + h2 // 2)

            # 先水平后垂直
            self.carve_h_tunnel(center1[0], center2[0], center1[1])
            self.carve_v_tunnel(center1[1], center2[1], center2[0])

        # 确保至少有一个房间能容纳玩家
        if rooms:
            x, y, w, h = rooms[0]
            self.player['x'] = x + w // 2
            self.player['y'] = y + h // 2

        # 生成敌人
        self.entities = []
        for _ in range(NUM_ENEMIES):
            entity = self.spawn_entity(roles='enemy', x=0, y=0)
            while entity is None:
                entity = self.spawn_entity(roles='enemy', x=0, y=0)
            self.entities.append(entity)

        # 生成药水和武器
        for _ in range(NUM_POTIONS):
            item = self.spawn_entity(roles='potion', x=0, y=0)
            while item is None:
                item = self.spawn_entity(roles='potion', x=0, y=0)
            self.entities.append(item)

        for _ in range(NUM_WEAPONS):
            item = self.spawn_entity(roles='weapon', x=0, y=0)
            while item is None:
                item = self.spawn_entity(roles='weapon', x=0, y=0)
            self.entities.append(item)

        # 设置出口在最后一个房间
        if rooms:
            x, y, w, h = rooms[-1]
            exit_x = x + w // 2
            exit_y = y + h // 2
            self.entities.append({'x': exit_x, 'y': exit_y, 'type': 'exit'})

    def carve_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 < x < GRID_COLS - 1 and 0 < y < GRID_ROWS - 1:
                self.map_data[y][x] = 0

    def carve_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 < x < GRID_COLS - 1 and 0 < y < GRID_ROWS - 1:
                self.map_data[y][x] = 0

    def spawn_entity(self, roles, x=0, y=0):
        # 寻找空格子
        empty_slots = []
        for i in range(GRID_ROWS):
            for j in range(GRID_COLS):
                if self.map_data[i][j] == 0 and (j, i) != (self.player['x'], self.player['y']):
                    occupied = any(e['x'] == j and e['y'] == i for e in self.entities)
                    if not occupied and (roles != 'enemy' or (j, i) != (self.player['x'], self.player['y'])):
                        empty_slots.append((j, i))

        if not empty_slots:
            return None

        pos = random.choice(empty_slots)
        if roles == 'enemy':
            return {'x': pos[0], 'y': pos[1], 'type': 'enemy', 'hp': 8, 'max_hp': 8, 'atk': 3}
        elif roles == 'potion':
            return {'x': pos[0], 'y': pos[1], 'type': 'potion'}
        elif roles == 'weapon':
            return {'x': pos[0], 'y': pos[1], 'type': 'weapon'}
        return None

    def get_entity_at(self, x, y, exclude_player=False):
        for e in self.entities:
            if e['x'] == x and e['y'] == y:
                if exclude_player and e['type'] == 'player':
                    continue
                return e
        return None

    def move_player(self, dx, dy):
        if self.game_over or self.game_won:
            return

        new_x = self.player['x'] + dx
        new_y = self.player['y'] + dy

        # 检查边界和墙壁
        if (new_x < 0 or new_x >= GRID_COLS or new_y < 0 or new_y >= GRID_ROWS or 
            self.map_data[new_y][new_x] == 1):
            return

        # 检查是否有敌人阻挡
        enemy = self.get_entity_at(new_x, new_y)
        if enemy and enemy['type'] == 'enemy':
            self.attack_player(enemy)
            return

        # 移动玩家
        self.player['x'] = new_x
        self.player['y'] = new_y

        # 检查拾取道具
        item = self.get_entity_at(new_x, new_y, exclude_player=True)
        if item:
            if item['type'] == 'potion':
                self.player['hp'] = min(self.player['hp'] + 8, self.player['max_hp'])
                self.entities.remove(item)
                self.log("Picked up a potion (+8 HP)")
            elif item['type'] == 'weapon':
                self.player['atk'] += 2
                self.entities.remove(item)
                self.log("Picked up a weapon (+2 ATK)")
            elif item['type'] == 'exit':
                self.log("Entered exit! Level up!")
                self.floor += 1
                self.generate_dungeon()
                return

        # 敌人行动（回合制）
        self.enemy_turn()

        # 检查是否所有敌人已死亡且玩家到达出口
        enemies = [e for e in self.entities if e['type'] == 'enemy']
        if not enemies and self.get_entity_at(self.player['x'], self.player['y'], True) is None:
            for e in self.entities:
                if e['type'] == 'exit':
                    self.log("All enemies defeated, reach exit!")
                    break

    def enemy_turn(self):
        player_x, player_y = self.player['x'], self.player['y']
        enemies = [e for e in self.entities if e['type'] == 'enemy']

        for enemy in enemies:
            dx = player_x - enemy['x']
            dy = player_y - enemy['y']

            if abs(dx) + abs(dy) == 1:  # 紧邻
                self.attack_enemy(enemy)
            elif abs(dx) + abs(dy) <= 5:  # 5格内才移动
                move_x, move_y = 0, 0
                if abs(dx) > abs(dy):
                    move_x = 1 if dx > 0 else -1
                else:
                    move_y = 1 if dy > 0 else -1

                new_x = enemy['x'] + move_x
                new_y = enemy['y'] + move_y

                if (0 <= new_x < GRID_COLS and 0 <= new_y < GRID_ROWS and
                    self.map_data[new_y][new_x] == 0 and not self.get_entity_at(new_x, new_y)):
                    enemy['x'] = new_x
                    enemy['y'] = new_y
                    # 攻击玩家
                    if (enemy['x'] == player_x and enemy['y'] == player_y):
                        self.attack_player(enemy)

    def attack_player(self, enemy):
        self.player['hp'] -= enemy['atk']
        self.log(f"Enemy hit player for {enemy['atk']} damage")

        if self.player['hp'] <= 0:
            self.player['hp'] = 0
            self.game_over = True

    def attack_enemy(self, enemy):
        enemy['hp'] -= self.player['atk']
        self.log(f"Player hit enemy for {self.player['atk']} damage")
        if enemy['hp'] <= 0:
            self.entities.remove(enemy)
            self.player['exp'] += 5
            self.log("Enemy defeated! +5 EXP")
            self.check_level_up()

    def check_level_up(self):
        if self.player['exp'] >= self.player['exp_needed']:
            self.player['level'] += 1
            self.player['exp'] = 0
            self.player['exp_needed'] = int(self.player['exp_needed'] * 1.5)
            self.player['max_hp'] += 5
            self.player['hp'] = self.player['max_hp']
            self.player['atk'] += 1
            self.log(f"Level up! Now level {self.player['level']}")

    def log(self, msg):
        self.messages.append(msg)
        if len(self.messages) > 5:
            self.messages.pop(0)

    def draw(self):
        self.screen.fill((0, 0, 0))

        # 绘制地图
        map_x = (SCREEN_WIDTH - MAP_WIDTH) // 2
        map_y = (SCREEN_HEIGHT - MAP_HEIGHT) // 2

        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                if self.map_data[y][x] == 1:
                    pygame.draw.rect(self.screen, COLOR_WALL, 
                                     (map_x + x * GRID_SIZE, map_y + y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                else:
                    pygame.draw.rect(self.screen, COLOR_FLOOR, 
                                     (map_x + x * GRID_SIZE, map_y + y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # 绘制实体
        for e in self.entities:
            color = None
            if e['type'] == 'enemy':
                color = COLOR_ENEMY
            elif e['type'] == 'potion':
                color = COLOR_POTION
            elif e['type'] == 'weapon':
                color = COLOR_WEAPON
            elif e['type'] == 'exit':
                color = COLOR_EXIT
            if color:
                pygame.draw.rect(self.screen, color, 
                                 (map_x + e['x'] * GRID_SIZE, map_y + e['y'] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # 绘制玩家
        pygame.draw.rect(self.screen, COLOR_PLAYER, 
                         (map_x + self.player['x'] * GRID_SIZE, map_y + self.player['y'] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # HUD 绘制
        hud_y = map_y + MAP_HEIGHT + 10
        levels = [
            f"Floor: {self.floor}",
            f"HP: {self.player['hp']}/{self.player['max_hp']}",
            f"ATK: {self.player['atk']}",
            f"LV: {self.player['level']}",
            f"EXP: {self.player['exp']}/{self.player['exp_needed']}"
        ]
        for i, line in enumerate(levels):
            text = self.font.render(line, True, COLOR_HUD_TEXT)
            self.screen.blit(text, (10, 10 + i * 28))

        # 消息打印
        for i, msg in enumerate(self.messages):
            text = self.font.render(msg, True, COLOR_MESSAGE_TEXT)
            self.screen.blit(text, (10, SCREEN_HEIGHT - 100 + i * 20))

        # 游戏结束/胜利
        if self.game_over:
            pygame.draw.rect(self.screen, (0, 0, 0, 180), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            text = self.big_font.render("GAME OVER", True, (255, 0, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(text, text_rect)
            text2 = self.font.render(f"Reached Floor {self.floor}", True, (255, 255, 255))
            text2_rect = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 50))
            self.screen.blit(text2, text2_rect)
            text3 = self.font.render("Press R to Restart", True, (255, 255, 255))
            text3_rect = text3.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 100))
            self.screen.blit(text3, text3_rect)

        elif self.floor > 10:  # 胜利条件：到达第 10 层（可自定义）
            pygame.draw.rect(self.screen, (0, 0, 0, 180), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            text = self.big_font.render("YOU WIN!", True, (0, 255, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(text, text_rect)
            text2 = self.font.render(f"Final Floor: {self.floor}", True, (255, 255, 255))
            text2_rect = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 50))
            self.screen.blit(text2, text2_rect)
            text3 = self.font.render("Press R to Restart", True, (255, 255, 255))
            text3_rect = text3.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 100))
            self.screen.blit(text3, text3_rect)

        # 玩家到达出口提示
        if (self.player['x'] == 0 and self.player['y'] == 0 and 
            self.get_entity_at(self.player['x'], self.player['y'], True) and 
            self.get_entity_at(self.player['x'], self.player['y'], True)['type'] == 'exit'):
            text = self.font.render("Press ESC to exit or wait for next level...", True, (255, 255, 255))
            self.screen.blit(text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 30))

        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r and (self.game_over or self.floor > 10):
                        self.restart()
                    elif event.key == pygame.K_r and not self.game_over and self.floor <= 10:
                        self.restart()
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
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()