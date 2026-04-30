import pygame
import sys
import random

pygame.init()

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 24
MAP_COLS = 19
MAP_ROWS = 21
MAP_WIDTH = GRID_SIZE * MAP_COLS
MAP_HEIGHT = GRID_SIZE * MAP_ROWS
FPS = 60

# HUD区域偏移
HUD_OFFSET_X = (SCREEN_WIDTH - MAP_WIDTH) // 2 + MAP_WIDTH + 20
HUD_OFFSET_Y = 60
HUD_TEXT_COLOR = (255, 255, 255)
HUD_BG_COLOR = (0, 0, 0)
SCORE_Y = HUD_OFFSET_Y
LIVES_Y = SCORE_Y + 40
GHOSTS_Y = LIVES_Y + 40
GHOSTS_COLOR = (255, 255, 0)
STATUS_Y = GHOSTS_Y + 40

# 游戏颜色
COLOR_BG = (0, 0, 0)
COLOR_WALL = (0, 0, 255)
COLOR_PATH = (0, 0, 0)
COLOR_PACMAN = (255, 255, 0)
COLOR_GHOST_RED = (255, 0, 0)
COLOR_GHOST_PINK = (255, 192, 203)
COLOR_GHOST_CYAN = (0, 255, 255)
COLOR_GHOST_ORANGE = (255, 165, 0)
COLOR_GHOST_SCARED = (0, 0, 255)
COLOR_GHOST_EATEN = (0, 0, 0)
COLOR_DOT = (255, 255, 255)
COLOR_POWER Dot = (255, 255, 0)

# 迷宫地图（19列 x 21行） '#'=墙, '.'=豆子, 'o'=能量豆, ' '=空地, 'P'=玩家出生点, 'G'=幽灵出生点
MAP_LAYOUT = [
    "###################",
    "#o........#........o#",
    "#.###.###.#.###.###.#",
    "#.###.###.#.###.###.#",
    "#...................#",
    "#.###.#.#####.#.###.#",
    "#.....#...#...#.....#",
    "#####.### # #.###.#####",
    "    #.#     #.#     #",
    "#####.# ### #.#.#####",
    "      # #GGG# #      ",
    "#####.# ### #.#.#####",
    "    #.#     #.#     #",
    "#####.### # #.###.#####",
    "#...................#",
    "#.###.###.#.###.###.#",
    "#.....#...#...#.....#",
    "#.###.###.#.###.###.#",
    "#.###.#...#...#.###.#",
    "#o........#...P.......o",
    "###################"
]

# 迷宫生成器
def generate_map():
    global CELL_SIZE
    map_grid = []
    for r, row in enumerate(MAP_LAYOUT):
        map_row = []
        for c, ch in enumerate(row):
            if ch == '#':
                map_row.append('WALL')
            elif ch == '.':
                map_row.append('DOT')
            elif ch == 'o':
                map_row.append('POWER DOT')
            elif ch == ' ':
                map_row.append('EMPTY')
            elif ch == 'P':
                map_row.append('EMPTY')
                player_start = (c * GRID_SIZE, r * GRID_SIZE)
            elif ch == 'G':
                map_row.append('GHOST_START')
        if 'player_start' not in locals():
            player_start = (9 * GRID_SIZE, 17 * GRID_SIZE)
        map_grid.append(map_row)
    return map_grid, player_start

# 状态枚举
PLAYER = 0
GHOST = 1

# 方向枚举
UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3

class Pacman(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.speed = 3
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.mouth_open = 0
        self.mouth_direction = 1
        
    def update(self, map_grid):
        # 更新嘴巴动作
        self.mouth_open += self.mouth_direction * 0.15
        if self.mouth_open > 0.25 or self.mouth_open < 0:
            self.mouth_direction *= -1
        
        # 尝试转向
        if self.next_direction != self.direction:
            new_x = int(round(self.x))
            new_y = int(round(self.y))
            if (new_x % GRID_SIZE == 0 and new_y % GRID_SIZE == 0) or self.next_direction in [0, 2] and new_y % GRID_SIZE == 0 or self.next_direction in [1, 3] and new_x % GRID_SIZE == 0:
                self.x = new_x
                self.y = new_y
                self.rect.x = int(self.x)
                self.rect.y = int(self.y)
                if self._can_move(self.next_direction, map_grid):
                    self.direction = self.next_direction
        
        # 移动
        if self._can_move(self.direction, map_grid):
            if self.direction == UP:
                self.y -= self.speed
            elif self.direction == DOWN:
                self.y += self.speed
            elif self.direction == LEFT:
                self.x -= self.speed
            elif self.direction == RIGHT:
                self.x += self.speed
        
        # 边界处理（左右贯通隧道）
        if self.x < 0:
            self.x = MAP_WIDTH - GRID_SIZE
        elif self.x >= MAP_WIDTH:
            self.x = 0
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def _can_move(self, direction, map_grid):
        next_x = self.rect.x
        next_y = self.rect.y
        if direction == UP:
            next_y -= self.speed
        elif direction == DOWN:
            next_y += self.speed
        elif direction == LEFT:
            next_x -= self.speed
        elif direction == RIGHT:
            next_x += self.speed
        
        # 检查包围盒
        test_rect = pygame.Rect(next_x, next_y, GRID_SIZE, GRID_SIZE)
        for dr in range(2):
            for dc in range(2):
                r = (next_y + dr * (GRID_SIZE-1)) // GRID_SIZE
                c = (next_x + dc * (GRID_SIZE-1)) // GRID_SIZE
                if 0 <= r < MAP_ROWS and 0 <= c < MAP_COLS:
                    if map_grid[r][c] == 'WALL':
                        return False
        return True
    
    def draw(self, surface):
        color = COLOR_PACMAN
        cx = self.rect.centerx
        cy = self.rect.centery
        
        # 计算嘴巴角度
        angle = 0
        if self.direction == UP:
            angle = -0.25 * self.mouth_open * 3.14159
        elif self.direction == DOWN:
            angle = 0.25 * self.mouth_open * 3.14159
        elif self.direction == LEFT:
            angle = 0.75 * self.mouth_open * 3.14159
        elif self.direction == RIGHT:
            angle = -0.75 * self.mouth_open * 3.14159
        
        # 绘制
        if self.mouth_open > 0:
            x, y = self.rect.center
            r = GRID_SIZE // 2
            points = [(x, y)]
            for i in range(int(angle * 2 * 10), int(2 * 10 - angle * 2 * 10)):
                ang = (i / 20) * 3.14159 + angle
                px = x + r * (1 - self.mouth_open * 0.5) * round(3.14159 * 20) / (3.14159 * 20) * round(3.14159 * 20) / (3.14159 * 20) * round(3.14159 * 20) / (3.14159 * 20) * round(3.14159 * 20) / (3.14159 * 20) * round(3.14159 * 20) / (3.14159 * 20) * round(3.14159 * 20) / (3.14159 * 20)
                py = y + r * (1 - self.mouth_open * 0.5) * round(3.14159 * 20) / (3.14159 * 20) * round(3.14159 * 20) / (3.14159 * 20) * round(3.14159 * 20) / (3.14159 * 20) * round(3.14159 * 20) / (3.14159 * 20) * round(3.14159 * 20) / (3.14159 * 20) * round(3.14159 * 20) / (3.14159 * 20)
                points.append((px, py))
            points.append((x, y))
            pygame.draw.polygon(surface, color, points)
        else:
            pygame.draw.circle(surface, color, (self.rect.centerx, self.rect.centery), GRID_SIZE // 2)

class Ghost(pygame.sprite.Sprite):
    def __init__(self, x, y, color, type_idx):
        super().__init__()
        self.rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.color = color
        self.original_color = color
        self.start_position = (x, y)
        self.speed = 2
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.target_direction = self.direction
        self.scared_timer = 0
        self.eaten = False
        self.scared_duration = 6 * FPS
        self.moving = False
        self.last_move = 0
        self.move_interval = 1000 // (self.speed * 10) // 2 + 1
    
    def reset(self):
        self.rect.x, self.rect.y = self.start_position
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.scared_timer = 0
        self.eaten = False
        self.color = self.original_color
    
    def move(self, map_grid, pacman):
        if not self.moving:
            if pygame.time.get_ticks() - self.last_move < self.move_interval:
                return
            self.last_move = pygame.time.get_ticks()
            self.moving = True
        
        # 更新朝向
        if self.scared_timer > 0:
            self.scared_timer -= 1
            if self.scared_timer <= 0:
                self.color = self.original_color
            else:
                self.color = COLOR_GHOST_SCARED if (self.scared_timer // 10) % 2 else (255, 0, 255)
        
        # 移动到网格对齐
        if self.rect.left % GRID_SIZE == 0 and self.rect.top % GRID_SIZE == 0:
            # 选择新方向
            self._choose_direction(map_grid, pacman)
        
        # 移动
        if self.eaten:
            if self.rect.center == self._to_grid(*self.start_position):
                self.eaten = False
                self.color = self.original_color
                self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
            else:
                # 返回出生点
                dx, dy = self.start_position[0] - self.rect.x, self.start_position[1] - self.rect.y
                if dx != 0:
                    self.direction = RIGHT if dx > 0 else LEFT
                if dy != 0:
                    self.direction = DOWN if dy > 0 else UP
                self._apply_direction()
        else:
            self._apply_direction()
    
    def _to_grid(self, x, y):
        return (x // GRID_SIZE * GRID_SIZE, y // GRID_SIZE * GRID_SIZE)
    
    def _get_valid_directions(self, map_grid):
        valid = []
        grid_x, grid_y = self.rect.x // GRID_SIZE, self.rect.y // GRID_SIZE
        for direction in [UP, DOWN, LEFT, RIGHT]:
            if direction == UP:
                r, c = grid_y - 1, grid_x
            elif direction == DOWN:
                r, c = grid_y + 1, grid_x
            elif direction == LEFT:
                r, c = grid_y, grid_x - 1
            elif direction == RIGHT:
                r, c = grid_y, grid_x + 1
            if 0 <= r < MAP_ROWS and 0 <= c < MAP_COLS:
                if map_grid[r][c] != 'WALL':
                    valid.append(direction)
        return valid
    
    def _choose_direction(self, map_grid, pacman):
        valid_directions = self._get_valid_directions(map_grid)
        if not valid_directions:
            return
        
        # 如果吃掉状态，直接返回出生点
        if self.eaten:
            return
        
        # 否则按策略选择方向
        if len(valid_directions) == 1:
            self.direction = valid_directions[0]
            return
        
        # 去除反方向（避免立即折返）
        opposite = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
        directions = [d for d in valid_directions if d != opposite.get(self.direction)]
        if not directions:
            directions = valid_directions
        
        # 计算目标
        target_x, target_y = pacman.rect.centerx, pacman.rect.centery
        
        # 如果被吓到，则远离玩家
        if self.scared_timer > 0:
            best_distance = -1
            for direction in directions:
                next_x, next_y = self._get_next_pos(direction)
                dist = (next_x - target_x)**2 + (next_y - target_y)**2
                if dist > best_distance:
                    best_distance = dist
                    self.target_direction = direction
        else:
            best_distance = float('inf')
            for direction in directions:
                next_x, next_y = self._get_next_pos(direction)
                if self.color == COLOR_GHOST_PINK:
                    # Pinky: 4格 ahead of pacman
                    dx, dy = 0, 0
                    if pacman.direction == UP:
                        dy = -4 * GRID_SIZE
                    elif pacman.direction == DOWN:
                        dy = 4 * GRID_SIZE
                    elif pacman.direction == LEFT:
                        dx = -4 * GRID_SIZE
                    elif pacman.direction == RIGHT:
                        dx = 4 * GRID_SIZE
                    target_x, target_y = pacman.rect.centerx + dx, pacman.rect.centery + dy
                elif self.color == COLOR_GHOST_ORANGE:
                    # Clyde: if far, pacman, else random
                    dist = (next_x - target_x)**2 + (next_y - target_y)**2
                    if dist > (2500):
                        target_x, target_y = pacman.rect.centerx, pacman.rect.centery
                    else:
                        target_x, target_y = (MAP_WIDTH - GRID_SIZE), 6 * GRID_SIZE
                elif self.color == COLOR_GHOST_RED:
                    target_x, target_y = pacman.rect.centerx, pacman.rect.centery
                elif self.color == COLOR_GHOST_CYAN:
                    target_x, target_y = pacman.rect.centerx, pacman.rect.centery
                
                dist = (next_x - target_x)**2 + (next_y - target_y)**2
                if dist < best_distance:
                    best_distance = dist
                    self.target_direction = direction
        
        self.direction = self.target_direction
        self._apply_direction()
    
    def _get_next_pos(self, direction):
        x, y = self.rect.x, self.rect.y
        if direction == UP:
            y -= GRID_SIZE
        elif direction == DOWN:
            y += GRID_SIZE
        elif direction == LEFT:
            x -= GRID_SIZE
        elif direction == RIGHT:
            x += GRID_SIZE
        return x, y
    
    def _apply_direction(self):
        if self.direction == UP:
            self.y -= self.speed
        elif self.direction == DOWN:
            self.y += self.speed
        elif self.direction == LEFT:
            self.x -= self.speed
        elif self.direction == RIGHT:
            self.x += self.speed
        
        # 边界检查
        if self.y < 0:
            self.y = MAP_HEIGHT - GRID_SIZE
        elif self.y >= MAP_HEIGHT:
            self.y = 0
        
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def draw(self, surface):
        # 减少闪烁
        color = self.color
        x, y = self.rect.centerx, self.rect.centery
        r = GRID_SIZE // 2
        pygame.draw.circle(surface, color, (x, y), r)
        if not self.eaten:
            # 眼睛
            eye_x, eye_y = x - r//3, y - r//3
            for _ in range(2):
                pygame.draw.circle(surface, (255, 255, 255), (eye_x, eye_y), r//4)
                pygame.draw.circle(surface, (0, 0, 0), (eye_x, eye_y), r//8)
                eye_x += r//1.5
            # 如果被吓到了，加个嘴巴
            if self.scared_timer > 0:
                pygame.draw.arc(surface, (255, 255, 255), (x-r, y-r//2, r*2, r), 0.5, 2.6, 2)

def draw_hud(surface, score, lives, dots_remaining, game_status, power_mode, ghosts):
    font = pygame.font.SysFont(None, 24)
    # HUD框
    pygame.draw.rect(surface, HUD_BG_COLOR, (HUD_OFFSET_X - 10, 10, 240, 200))
    # 分数
    text = font.render(f"Score: {score}", True, HUD_TEXT_COLOR)
    surface.blit(text, (HUD_OFFSET_X, SCORE_Y))
    # 生命
    text = font.render(f"Lives: {lives}", True, HUD_TEXT_COLOR)
    surface.blit(text, (HUD_OFFSET_X, LIVES_Y))
    # 剩余豆子
    text = font.render(f"Dots: {dots_remaining}", True, HUD_TEXT_COLOR)
    surface.blit(text, (HUD_OFFSET_X, GHOSTS_Y))
    # 幽灵状态
    text = font.render("Ghost State: ", True, HUD_TEXT_COLOR)
    surface.blit(text, (HUD_OFFSET_X, GHOSTS_Y + 40))
    if power_mode:
        text = font.render("SCARED", True, COLOR_GHOST_SCARED)
    else:
        text = font.render("NORMAL", True, (255, 255, 255))
    surface.blit(text, (HUD_OFFSET_X + 150, GHOSTS_Y + 40))
    # 游戏状态
    if game_status in ['WIN', 'LOSE']:
        font_large = pygame.font.SysFont(None, 48)
        if game_status == 'WIN':
            text = font_large.render("YOU WIN!", True, (255, 255, 0))
        else:
            text = font_large.render("GAME OVER", True, (255, 0, 0))
        text_rect = text.get_rect(center=(MAP_WIDTH // 2 + 10, MAP_HEIGHT // 2))
        surface.blit(text, text_rect)
        
        font_small = pygame.font.SysFont(None, 32)
        text = font_small.render(f"Final Score: {score}", True, HUD_TEXT_COLOR)
        text_rect = text.get_rect(center=(MAP_WIDTH // 2 + 10, MAP_HEIGHT // 2 + 50))
        surface.blit(text, text_rect)
        
        text = font_small.render("Press R to Restart", True, (255, 255, 255))
        text_rect = text.get_rect(center=(MAP_WIDTH // 2 + 10, MAP_HEIGHT // 2 + 100))
        surface.blit(text, text_rect)

def draw_map(surface, map_grid, dots, power_dots):
    # 背景
    surface.fill(COLOR_PATH)
    # 墙体
    wall_rect = pygame.Rect((0, 0), (MAP_WIDTH, MAP_HEIGHT))
    pygame.draw.rect(surface, COLOR_BG, wall_rect)
    
    for r, row in enumerate(map_grid):
        for c, cell in enumerate(row):
            x, y = c * GRID_SIZE, r * GRID_SIZE
            if cell == 'WALL':
                pygame.draw.rect(surface, COLOR_WALL, (x, y, GRID_SIZE, GRID_SIZE))
            elif cell == 'EMPTY' and (r, c) not in dots and (r, c) not in power_dots:
                # 通路装饰（可选）
                pass
            elif (r, c) in dots:
                dot = dots[(r, c)]
                if not dot['eaten']:
                    pygame.draw.circle(surface, COLOR_DOT, (x + GRID_SIZE//2, y + GRID_SIZE//2), 4)
            elif (r, c) in power_dots:
                power = power_dots[(r, c)]
                if not power['eaten']:
                    radius = 8 if (pygame.time.get_ticks() // 200) % 2 else 6
                    pygame.draw.circle(surface, COLOR_POWER Dot, (x + GRID_SIZE//2, y + GRID_SIZE//2), radius)

def main():
    # 初始化
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pac-Man")
    clock = pygame.time.Clock()
    random.seed(42)
    
    # 游戏状态变量
    MAP_GRID, player_start = generate_map()
    
    # 豆子数据
    dots = {}
    power_dots = {}
    for r in range(len(MAP_LAYOUT)):
        for c in range(len(MAP_LAYOUT[r])):
            if MAP_LAYOUT[r][c] == '.':
                dots[(r, c)] = {'eaten': False}
            elif MAP_LAYOUT[r][c] == 'o':
                power_dots[(r, c)] = {'eaten': False}
    
    # 创建玩家
    player = Pacman(player_start[0], player_start[1])
    
    # 创建幽灵（固定位置）
    ghost_positions = [
        (9 * GRID_SIZE, 10 * GRID_SIZE, COLOR_GHOST_RED),
        (9 * GRID_SIZE, 9 * GRID_SIZE, COLOR_GHOST_PINK),
        (8 * GRID_SIZE, 10 * GRID_SIZE, COLOR_GHOST_CYAN),
        (10 * GRID_SIZE, 10 * GRID_SIZE, COLOR_GHOST_ORANGE)
    ]
    ghosts = []
    for x, y, color in ghost_positions:
        ghosts.append(Ghost(x, y, color, len(ghosts)))
    
    # 游戏状态
    score = 0
    lives = 3
    power_mode = False
    power_timer = 0
    game_status = 'PLAYING'
    dots_remaining = len(dots) + len(power_dots)
    
    # 主循环
    running = True
    while running:
        # 控制
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_status != 'PLAYING':
                    # 重新开始游戏
                    return main()
                elif game_status == 'PLAYING':
                    if event.key == pygame.K_UP:
                        player.next_direction = UP
                    elif event.key == pygame.K_DOWN:
                        player.next_direction = DOWN
                    elif event.key == pygame.K_LEFT:
                        player.next_direction = LEFT
                    elif event.key == pygame.K_RIGHT:
                        player.next_direction = RIGHT
        
        # 绘制背景
        screen.fill(COLOR_BG)
        
        # 绘制地图及豆子
        dots_remaining = len([d for d in dots.values() if not d['eaten']]) + len([p for p in power_dots.values() if not p['eaten']])
        draw_map(screen, MAP_GRID, dots, power_dots)
        
        # 玩家更新
        if game_status == 'PLAYING':
            player.update(MAP_GRID)
            px, py = player.rect.centerx // GRID_SIZE, player.rect.centery // GRID_SIZE
            # 吃豆子
            if (py, px) in dots:
                if not dots[(py, px)]['eaten']:
                    dots[(py, px)]['eaten'] = True
                    score += 10
                    dots_remaining -= 1
            if (py, px) in power_dots:
                if not power_dots[(py, px)]['eaten']:
                    power_dots[(py, px)]['eaten'] = True
                    score += 50
                    dots_remaining -= 1
                    power_mode = True
                    power_timer = 6 * FPS
        
            # 吃豆子逻辑
            for ghost in ghosts:
                if ghost.rect.colliderect(player.rect):
                    if power_mode and not ghost.eaten:
                        ghost.eaten = True
                        score += 200
                    elif not ghost.eaten:
                        lives -= 1
                        if lives > 0:
                            # 重置位置
                            player.x, player.y = player_start
                            player.rect.x, player.rect.y = player_start
                            player.direction = RIGHT
                            player.next_direction = RIGHT
                            for g in ghosts:
                                g.reset()
                        else:
                            game_status = 'LOSE'
        
            # 幽灵更新
            for ghost in ghosts:
                ghost.move(MAP_GRID, player)
                # 碰撞检测
                if ghost.rect.colliderect(player.rect) and not ghost.eaten:
                    if power_mode:
                        ghost.eaten = True
                        score += 200
                    else:
                        lives -= 1
                        if lives > 0:
                            player.x, player.y = player_start
                            player.rect.x, player.rect.y = player_start
                            player.direction = RIGHT
                            player.next_direction = RIGHT
                            for g in ghosts:
                                g.reset()
                        else:
                            game_status = 'LOSE'
        
            if dots_remaining == 0:
                game_status = 'WIN'
        
        # 实际吃豆逻辑（防止遗漏）
        if player.rect.colliderect(player.rect):
            pass
        
        # 幽灵状态更新（防止漏判）
        for ghost in ghosts:
            ghost.move(MAP_GRID, player)
        
        # 绘制角色
        player.draw(screen)
        for ghost in ghosts:
            ghost.draw(screen)
        
        # HUD
        draw_hud(screen, score, lives, dots_remaining, game_status, power_mode, ghosts)
        
        # 更新
        pygame.display.flip()
        clock.tick(FPS)
        
        # 动画效果更新
        if power_mode:
            power_timer -= 1
            if power_timer <= 0:
                power_mode = False
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()