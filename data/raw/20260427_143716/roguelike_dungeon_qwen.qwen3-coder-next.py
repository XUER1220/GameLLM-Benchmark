import pygame
import random
import sys

# 常量定义
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_COLS = 21
GRID_ROWS = 15
GRID_SIZE = 32
MAP_WIDTH = GRID_COLS * GRID_SIZE  # 672
MAP HEIGHT = GRID_ROWS * GRID_SIZE  # 480
MAP_X = (WINDOW_WIDTH - MAP_WIDTH) // 2
MAP_Y = (WINDOW_HEIGHT - MAP_HEIGHT) // 2
FPS = 60

# 颜色定义
COLOR_WALL = (64, 64, 64)
COLOR_FLOOR = (32, 32, 32)
COLOR_PLAYER = (0, 255, 0)
COLOR_ENEMY = (255, 0, 0)
COLOR_POTION = (0, 0, 255)
COLOR_WEAPON = (255, 215, 0)
COLOR_EXIT = (0, 255, 255)
COLOR_HUD_BG = (20, 20, 20)
COLOR_TEXT = (255, 255, 255)

# 游戏状态常量
STATE_PLAYING = 0
STATE_GAME_OVER = 1

# 道具位置
DRINK_AMOUNT = 8
WEAPON_BONUS = 2
PLAYER_START_HP = 20
PLAYER_START_ATK = 5
PLAYER_START_LV = 1
PLAYER_START_EXP = 0
ENEMY_COUNT = 4
ENEMY_HP = 8
ENEMY_ATK = 3
ENEMY_EXP = 5
EXP_TO_LEVEL = 10
LEVEL_MAX_HP_BONUS = 5
LEVEL_ATK_BONUS = 1

# 地图生成参数
MIN_ROOM_SIZE = 3
MAX_ROOM_SIZE = 7
NUM_ROOMS = 6

# 初始化 pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Roguelike Dungeon Hard")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 36)

# 全局随机种子
random.seed(42)


def generate_dungeon():
    grid = [[1] * GRID_COLS for _ in range(GRID_ROWS)]  # 1=wall, 0=floor

    rooms = []
    
    # 生成房间
    for _ in range(NUM_ROOMS):
        w = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
        h = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
        x = random.randint(1, GRID_COLS - w - 1)
        y = random.randint(1, GRID_ROWS - h - 1)
        
        # 确保房间内全部为地板
        for i in range(y, y + h):
            for j in range(x, x + w):
                grid[i][j] = 0
        
        room_center = (x + w // 2, y + h // 2)
        rooms.append((room_center, (x, y, w, h)))
    
    # 连接相邻房间
    for i in range(len(rooms) - 1):
        room1 = rooms[i][0]
        room2 = rooms[i + 1][0]
        # 水平走廊
        x1, y1 = room1
        x2, y2 = room2
        
        # 先横向
        min_x, max_x = min(x1, x2), max(x1, x2)
        for x in range(min_x, max_x + 1):
            grid[y1][x] = 0
        
        # 再纵向
        min_y, max_y = min(y1, y2), max(y1, y2)
        for y in range(min_y, max_y + 1):
            grid[y][x2] = 0
    
    # 清理角落连接点（确保不漏出角落墙）
    for i in range(GRID_ROWS):
        grid[i][0] = grid[i][GRID_COLS - 1] = 1
    for j in range(GRID_COLS):
        grid[0][j] = grid[GRID_ROWS - 1][j] = 1

    return grid, rooms


def get_empty_cell(grid):
    while True:
        x = random.randint(1, GRID_COLS - 2)
        y = random.randint(1, GRID_ROWS - 2)
        if grid[y][x] == 0:
            return x, y


def init_game():
    global player, enemies, items, exit_pos, level, grid, game_state
    
    grid, rooms = generate_dungeon()
    level = 1
    game_state = STATE_PLAYING
    
    # 初始化玩家
    player_x, player_y = get_empty_cell(grid)
    player = {
        'x': player_x,
        'y': player_y,
        'hp': PLAYER_START_HP,
        'max_hp': PLAYER_START_HP,
        'atk': PLAYER_START_ATK,
        'lv': PLAYER_START_LV,
        'exp': PLAYER_START_EXP,
        'floor': level
    }
    
    # 初始化敌人
    enemies = []
    while len(enemies) < ENEMY_COUNT:
        x, y = get_empty_cell(grid)
        if (x != player_x or y != player_y):
            enemies.append({
                'x': x,
                'y': y,
                'hp': ENEMY_HP,
                'max_hp': ENEMY_HP,
                'atk': ENEMY_ATK
            })
    
    # 初始化道具位置：2药水+1武器
    items = []
    for _ in range(2):
        x, y = get_empty_cell(grid)
        items.append({'x': x, 'y': y, 'type': 'potion'})
    x, y = get_empty_cell(grid)
    items.append({'x': x, 'y': y, 'type': 'weapon'})
    
    # 设置出口
    exit_room = rooms[-1][0]
    exit_pos = (exit_room[0], exit_room[1])


def draw_text(text, x, y, color=COLOR_TEXT, font_obj=font):
    surface = font_obj.render(text, True, color)
    screen.blit(surface, (x, y))


def draw_game():
    # 清屏背景
    screen.fill(COLOR_HUD_BG)
    
    # 绘制地图
    for y in range(GRID_ROWS):
        for x in range(GRID_COLS):
            rect = pygame.Rect(MAP_X + x * GRID_SIZE, MAP_Y + y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            if grid[y][x] == 1:
                pygame.draw.rect(screen, COLOR_WALL, rect)
            else:
                pygame.draw.rect(screen, COLOR_FLOOR, rect)
                # 添加微妙的格子线
                pygame.draw.rect(screen, (0, 0, 0, 0), rect, 1)
    
    # 绘制道具
    for item in items:
        rect = pygame.Rect(MAP_X + item['x'] * GRID_SIZE + 4, MAP_Y + item['y'] * GRID_SIZE + 4, GRID_SIZE - 8, GRID_SIZE - 8)
        if item['type'] == 'potion':
            pygame.draw.circle(screen, COLOR_POTION, rect.center, rect.width // 2)
        elif item['type'] == 'weapon':
            pygame.draw.rect(screen, COLOR_WEAPON, rect)
    
    # 绘制出口
    rect = pygame.Rect(MAP_X + exit_pos[0] * GRID_SIZE, MAP_Y + exit_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(screen, COLOR_EXIT, rect)
    # 在出口上显示O
    draw_text('E', MAP_X + exit_pos[0] * GRID_SIZE + GRID_SIZE//2 - 6, MAP_Y + exit_pos[1] * GRID_SIZE + GRID_SIZE//2 - 8, (0,0,0))
    
    # 绘制敌人
    for enemy in enemies:
        rect = pygame.Rect(MAP_X + enemy['x'] * GRID_SIZE, MAP_Y + enemy['y'] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.circle(screen, COLOR_ENEMY, rect.center, GRID_SIZE // 2 - 2)
        # 简单血条
        hp_bar_width = 24
        hp_bar_height = 4
        hp_percent = enemy['hp'] / enemy['max_hp'] if enemy['max_hp'] > 0 else 0
        pygame.draw.rect(screen, (0,0,0), (MAP_X + enemy['x'] * GRID_SIZE + 4, MAP_Y + enemy['y'] * GRID_SIZE - 6, hp_bar_width, hp_bar_height))
        pygame.draw.rect(screen, (255, 0, 0), (MAP_X + enemy['x'] * GRID_SIZE + 4, MAP_Y + enemy['y'] * GRID_SIZE - 6, hp_bar_width * hp_percent, hp_bar_height))
    
    # 绘制玩家
    rect = pygame.Rect(MAP_X + player['x'] * GRID_SIZE, MAP_Y + player['y'] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.circle(screen, COLOR_PLAYER, rect.center, GRID_SIZE // 2 - 2)
    
    # HUD 区域绘制：左下角
    hud_x = 10
    hud_y = 490
    draw_text(f"HP: {player['hp']}/{player['max_hp']}", hud_x, hud_y)
    draw_text(f"ATK: {player['atk']}", hud_x, hud_y + 30)
    draw_text(f"LV: {player['lv']}", hud_x, hud_y + 60)
    draw_text(f"EXP: {player['exp']}/{EXP_TO_LEVEL}", hud_x, hud_y + 90)
    draw_text(f"Floor: {player['floor']}", hud_x, hud_y + 120)


def draw_game_over():
    screen.fill((50, 0, 0))
    draw_text("GAME OVER", WINDOW_WIDTH // 2 - 90, WINDOW_HEIGHT // 2 - 60, (255, 255, 255), big_font)
    draw_text(f"Level: {player['lv']}", WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT // 2 - 30)
    draw_text(f"Floor: {player['floor']}", WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT // 2)
    draw_text("Press R to Restart", WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2 + 60)


def update():
    global enemies, items, player, level, game_state, exit_pos, grid
    
    # 检查敌人是否攻击玩家
    for enemy in enemies[:]:
        distance = abs(enemy['x'] - player['x']) + abs(enemy['y'] - player['y'])
        if distance == 1:
            player['hp'] -= enemy['atk']
            if player['hp'] <= 0:
                player['hp'] = 0
                game_state = STATE_GAME_OVER
    
    # 检查物品拾取
    for item in items[:]:
        if item['x'] == player['x'] and item['y'] == player['y']:
            if item['type'] == 'potion':
                player['hp'] = min(player['hp'] + DRINK_AMOUNT, player['max_hp'])
            elif item['type'] == 'weapon':
                player['atk'] += WEAPON_BONUS
            items.remove(item)
    
    # 检查是否到达出口
    if player['x'] == exit_pos[0] and player['y'] == exit_pos[1]:
        next_level()


def next_level():
    global level, player, enemies, items, exit_pos, grid, game_state
    
    # 不改变玩家属性，只进入下一关（但保留升级属性）
    player['floor'] += 1
    level += 1
    
    # 重新生成地图
    grid, rooms = generate_dungeon()
    
    # 玩家进入新地图的初始位置
    player_x, player_y = get_empty_cell(grid)
    player['x'] = player_x
    player['y'] = player_y
    
    # 生成敌人
    enemies = []
    while len(enemies) < ENEMY_COUNT:
        x, y = get_empty_cell(grid)
        if (x != player_x or y != player_y):
            enemies.append({
                'x': x,
                'y': y,
                'hp': ENEMY_HP,
                'max_hp': ENEMY_HP,
                'atk': ENEMY_ATK
            })
    
    # 重置道具
    items = []
    for _ in range(2):
        x, y = get_empty_cell(grid)
        items.append({'x': x, 'y': y, 'type': 'potion'})
    x, y = get_empty_cell(grid)
    items.append({'x': x, 'y': y, 'type': 'weapon'})
    
    # 设置出口
    exit_room = rooms[-1][0]
    exit_pos = (exit_room[0], exit_room[1])


def move_player(dx, dy):
    global player
    
    # 检查移动目标是否有效
    new_x = player['x'] + dx
    new_y = player['y'] + dy
    if new_x < 0 or new_x >= GRID_COLS or new_y < 0 or new_y >= GRID_ROWS:
        return  # 超出地图边界
    
    if grid[new_y][new_x] == 1:
        return  # 墙壁不能穿过
    
    # 检查是否与敌人重叠
    for enemy in enemies:
        if enemy['x'] == new_x and enemy['y'] == new_y:
            # 近战攻击
            enemy['hp'] -= player['atk']
            if enemy['hp'] <= 0:
                # 敌人死亡
                enemies.remove(enemy)
                player['exp'] += ENEMY_EXP
                # 检查升级
                if player['exp'] >= EXP_TO_LEVEL:
                    player['exp'] -= EXP_TO_LEVEL
                    player['lv'] += 1
                    player['max_hp'] += LEVEL_MAX_HP_BONUS
                    player['hp'] = player['max_hp']  # 回满血
                    player['atk'] += LEVEL_ATK_BONUS
            break  # 攻击后立即结束回合行动
    
    # 正常移动（不攻击敌人的情况下）
    if not any(e['x'] == new_x and e['y'] == new_y for e in enemies):
        player['x'] = new_x
        player['y'] = new_y


def enemy_turn():
    for enemy in enemies:
        # 简单AI: 向玩家移动（曼哈顿距离最小）
        dx = player['x'] - enemy['x']
        dy = player['y'] - enemy['y']
        
        # 只在相邻时攻击
        if abs(dx) + abs(dy) == 1:
            continue  # 攻击逻辑已在update中处理
        
        # 尝试向玩家靠近
        new_x, new_y = enemy['x'], enemy['y']
        if abs(dx) > abs(dy):
            if dx > 0:
                new_x += 1
            else:
                new_x -= 1
        else:
            if dy > 0:
                new_y += 1
            else:
                new_y -= 1
        
        # 确保目标位置是地板
        if new_x < 0 or new_x >= GRID_COLS or new_y < 0 or new_y >= GRID_ROWS:
            continue
        
        if grid[new_y][new_x] == 1:
            continue
        
        # 检查是否与其他敌人或玩家重叠
        occupied = False
        for e in enemies:
            if e['x'] == new_x and e['y'] == new_y:
                occupied = True
                break
        if not occupied and not (player['x'] == new_x and player['y'] == new_y):
            enemy['x'] = new_x
            enemy['y'] = new_y


def main():
    global player, enemies, items, exit_pos, grid, game_state
    
    # 初始化游戏
    init_game()
    
    running = True
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        move_player(0, -1)
                    elif event.key == pygame.K_DOWN:
                        move_player(0, 1)
                    elif event.key == pygame.K_LEFT:
                        move_player(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        move_player(1, 0)
                    elif event.key == pygame.K_r or event.key == pygame.K_ESCAPE:
                        if event.key == pygame.K_r:
                            init_game()
                        else:
                            running = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            elif game_state == STATE_GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        init_game()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
        
        if running and game_state == STATE_PLAYING:
            # 更新游戏状态（回合制）
            if hasattr(move_player, 'last_key') and move_player.last_key:  # 简单检测玩家是否移动
                move_player.last_key = False
                enemy_turn()
            update()
        
        # 绘制画面
        if game_state == STATE_PLAYING:
            draw_game()
        elif game_state == STATE_GAME_OVER:
            draw_game_over()
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()


# 添加移动记录属性
move_player.last_key = False

if __name__ == "__main__":
    main()