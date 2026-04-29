import pygame
import random
import sys
import math

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRID_SIZE = 24
MAP_COLS = 19
MAP_ROWS = 21
HUD_WIDTH = SCREEN_WIDTH - (MAP_COLS * GRID_SIZE)
MARGIN_X = (SCREEN_WIDTH - (MAP_COLS * GRID_SIZE)) // 2
MARGIN_Y = (SCREEN_HEIGHT - (MAP_ROWS * GRID_SIZE)) // 2

# 颜色常量
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_RED = (255, 0, 0)
COLOR_PINK = (255, 192, 203)
COLOR_CYAN = (0, 255, 255)
COLOR_ORANGE = (255, 165, 0)
COLOR_DOT = (255, 200, 0)
COLOR_POWER_DOT = (255, 255, 255)

# 玩家属性
PLAYER_SPEED = 3
PLAYER_LIVES = 3
SCORE_PER_DOT = 10
SCORE_PER_POWER = 50
SCORE_PER_GHOST = 200

# 幽灵属性
GHOST_SPEED = 2
POWER_DURATION = 6 * FPS  # 秒转换为帧数

# 迷宫地图: '#' = 墙, '.' = 豆子, 'o' = 能量豆, 'P' = 玩家出生地, 'G' = 幽灵出生地, ' ' = 空通道
# 固定21行19列
MAP_LAYOUT = [
    "###################",
    "#................#.",
    "#.###.###.###.###.#",
    "#o#...#.#.#...#...o",
    "#.###.###.###.###.#",
    "#...#.......#...#..",
    "#.###.#.###.#.###.#",
    "#.....#.#.#.#.....#",
    "###.###.#.#.###.###",
    "#.....#.#.#.#.....#",
    "#.###.#.###.#.###.#",
    "#...#.......#...#..",
    "#.###.###.###.###.#",
    "#o#...#.#.#...#...o",
    "#.###.###.###.###.#",
    "#................#.",
    "#.###.#####.###.###",
    "#.#...#...#...#...#",
    "#.#.###.###.###.#.#",
    "#................ G",
    "###################"
]

# 玩家出生点（在'MAP_LAYOUT'中查找）
PLAYER_START = (9, 15)
# 幽灵出生点列表（按顺序）
GHOST_STARTS = [(9, 9), (10, 9), (8, 9), (11, 9)]

# 幽灵颜色和名称映射
GHOST_COLORS = [COLOR_RED, COLOR_PINK, COLOR_CYAN, COLOR_ORANGE]
GHOST_NAMES = ["Blinky", "Pinky", "Inky", "Clyde"]

class PacmanGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Man Medium")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 36)
        
        random.seed(42)  # 固定随机种子
        
        # 初始化游戏状态变量
        self.map_data = []
        self.dots_count = 0
        self.power_dots_remaining = 0
        self.total_dots = 0
        self.pacman = None
        self.ghosts = []
        self.lives = PLAYER_LIVES
        self.score = 0
        self.game_state = "start"  # start, running, game_over, win
        self.power_mode_time = 0
        self.fps_counter = 0
        
        self.reset_level()

    def reset_level(self):
        # 解析地图并初始化数据结构
        self.map_data = []
        self.dots = set()  # (x, y) 豆子位置
        self.power_dots = set()  # (x, y) 能量豆位置
        self.walls = set()  # (x, y) 墙体
        self.open_path = set()  # 包括墙、豆子、出口点，但实际通行只走空地
        self.ghost_spawn_points = []
        
        for row_idx, row in enumerate(MAP_LAYOUT):
            map_row = []
            for col_idx, cell in enumerate(row):
                x = col_idx * GRID_SIZE
                y = row_idx * GRID_SIZE
                
                # 记录墙体
                if cell == '#':
                    self.walls.add((col_idx, row_idx))
                    map_row.append(cell)
                # 记录空通道
                elif cell == ' ':
                    self.open_path.add((col_idx, row_idx))
                    map_row.append(cell)
                # 豆子
                elif cell == '.':
                    self.open_path.add((col_idx, row_idx))
                    self.dots.add((col_idx, row_idx))
                    self.total_dots += 1
                    map_row.append('.')
                # 能量豆
                elif cell == 'o':
                    self.open_path.add((col_idx, row_idx))
                    self.power_dots.add((col_idx, row_idx))
                    self.power_dots_remaining += 1
                    self.total_dots += 1
                    map_row.append('o')
                # 玩家出生点
                elif cell == 'P':
                    self.open_path.add((col_idx, row_idx))
                    self.player_spawn = (col_idx, row_idx)
                    map_row.append(' ')
                # 幽灵出生点
                elif cell == 'G':
                    self.open_path.add((col_idx, row_idx))
                    self.ghost_spawn_points.append((col_idx, row_idx))
                    map_row.append(' ')
                # 越界处理（最后行幽灵出生地）
                else:
                    self.open_path.add((col_idx, row_idx))
                    map_row.append(' ')
            
            self.map_data.append(map_row)
        
        # 如果没有幽灵出生点则使用默认
        if not self.ghost_spawn_points:
            self.ghost_spawn_points = GHOST_STARTS[:4]
        else:
            # 若地图中幽灵出生点不足，使用默认补足
            while len(self.ghost_spawn_points) < 4:
                self.ghost_spawn_points.append(GHOST_STARTS[len(self.ghost_spawn_points)])
        
        # 初始化 Pacman
        self.reset_pacman()
        
        # 初始化 Ghosts
        self.ghosts = []
        for i in range(4):
            self.ghosts.append(Ghost(self.ghost_spawn_points[i], GHOST_COLORS[i], i))
        
        # 初始化状态
        self.lives = PLAYER_LIVES
        self.score = 0
        self.game_state = "running"
        self.power_mode_time = 0

    def reset_pacman(self):
        if hasattr(self, 'player_spawn') and self.player_spawn:
            self.pacman = Pacman(self.player_spawn[0], self.player_spawn[1])
        else:
            # fallback to center
            self.pacman = Pacman(9, 10)
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r and self.game_state != "running":
                    self.reset_level()
                elif event.key == pygame.K_r and self.game_state == "running":
                    self.reset_level()
                elif self.game_state == "start" and event.key == pygame.K_SPACE:
                    self.game_state = "running"
                elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    if self.game_state == "running" and self.pacman:
                        direction = None
                        if event.key == pygame.K_UP: direction = (0, -1)
                        if event.key == pygame.K_DOWN: direction = (0, 1)
                        if event.key == pygame.K_LEFT: direction = (-1, 0)
                        if event.key == pygame.K_RIGHT: direction = (1, 0)
                        if direction:
                            self.pacman.set_next_direction(direction)

    def update(self):
        if self.game_state != "running":
            return
        
        # 更新 Pacman
        self.pacman.update(self.walls, self.open_path)
        
        # 吃豆子逻辑
        center_x = self.pacman.x + GRID_SIZE // 2
        center_y = self.pacman.y + GRID_SIZE // 2
        grid_x = center_x // GRID_SIZE
        grid_y = center_y // GRID_SIZE
        
        # 吃普通豆子
        if (grid_x, grid_y) in self.dots:
            self.dots.remove((grid_x, grid_y))
            self.score += SCORE_PER_DOT
            self.dots_count -= 1
        
        # 吃能量豆
        if (grid_x, grid_y) in self.power_dots:
            self.power_dots.remove((grid_x, grid_y))
            self.power_dots_remaining -= 1
            self.score += SCORE_PER_POWER
            self.power_mode_time = POWER_DURATION
            
            # 激活幽灵恐惧状态
            for ghost in self.ghosts:
                ghost.scared = True
                ghost.scared_timer = self.power_mode_time
        
        # 检查是否所有豆子被吃光
        if len(self.dots) == 0 and len(self.power_dots) == 0:
            self.game_state = "win"
            return
        
        # 检查能量豆过期
        if self.power_mode_time > 0:
            self.power_mode_time -= 1
            if self.power_mode_time <= 0:
                for ghost in self.ghosts:
                    ghost.scared = False
        
        # 检查是否需要更新幽灵速度（恢复后恢复原速）
        for ghost in self.ghosts:
            if ghost.scared and ghost.scared_timer <= FPS:
                ghost.scared = False

        # 更新幽灵
        for ghost in self.ghosts:
            ghost.update(self.walls, self.open_path, self.pacman)
        
        # 碰撞检测 (Pacman与each ghost)
        for i, ghost in enumerate(self.ghosts):
            if abs(self.pacman.x - ghost.x) < GRID_SIZE and abs(self.pacman.y - ghost.y) < GRID_SIZE:
                if ghost.scared:
                    # 吃掉幽灵
                    self.score += SCORE_PER_GHOST
                    # 重置幽灵位置
                    ghost.x, ghost.y = self.ghost_spawn_points[i]
                    ghost.scared = False
                    ghost.scared_timer = 0
                    ghost.direction = (0, 0)
                else:
                    # 玩家被吃
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_state = "game_over"
                    else:
                        self.reset_pacman()
                        for j, g in enumerate(self.ghosts):
                            g.x, g.y = self.ghost_spawn_points[j]
                            g.direction = (0, 0)
                            g.scared = False
                            g.scared_timer = 0

    def draw(self):
        self.screen.fill(COLOR_BLACK)
        
        # 绘制地图区域
        for row_idx, row in enumerate(self.map_data):
            for col_idx, cell in enumerate(row):
                if cell == '#':
                    # 深蓝色墙体
                    rect = pygame.Rect(
                        MARGIN_X + col_idx * GRID_SIZE,
                        MARGIN_Y + row_idx * GRID_SIZE,
                        GRID_SIZE, GRID_SIZE
                    )
                    pygame.draw.rect(self.screen, COLOR_BLUE, rect)
        
        # 绘制 dot
        for (x, y) in self.dots:
            cx = MARGIN_X + x * GRID_SIZE + GRID_SIZE // 2
            cy = MARGIN_Y + y * GRID_SIZE + GRID_SIZE // 2
            radius = 3
            pygame.draw.circle(self.screen, COLOR_DOT, (cx, cy), radius)
        
        # 绘制 power dot
        for (x, y) in self.power_dots:
            cx = MARGIN_X + x * GRID_SIZE + GRID_SIZE // 2
            cy = MARGIN_Y + y * GRID_SIZE + GRID_SIZE // 2
            radius = 7
            pygame.draw.circle(self.screen, COLOR_POWER_DOT, (cx, cy), radius)
        
        # 绘制 Pacman
        if self.game_state != "start":
            self.pacman.draw(self.screen, MARGIN_X, MARGIN_Y)
        
        # 绘制幽灵
        for ghost in self.ghosts:
            ghost.draw(self.screen, MARGIN_X, MARGIN_Y)
        
        # HUD 部分 (右侧区域)
        hud_text = [
            f"Score: {self.score}",
            f"Lives: {self.lives}",
            f"Dots: {self.total_dots - (len(self.dots) + len(self.power_dots))}/{self.total_dots}",
        ]
        
        for i, text in enumerate(hud_text):
            img = self.font_small.render(text, True, COLOR_WHITE)
            self.screen.blit(img, (SCREEN_WIDTH - HUD_WIDTH + 10, 30 + i * 30))
        
        # 游戏状态信息
        if self.game_state == "start":
            self.draw_center_text("PAC-MAN", self.font_large, COLOR_YELLOW, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.draw_center_text("Press SPACE to Start", self.font_small, COLOR_WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        elif self.game_state == "game_over":
            self.draw_center_text("GAME OVER", self.font_large, COLOR_RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
            self.draw_center_text(f"Score: {self.score}", self.font_small, COLOR_WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.draw_center_text("Press R to Restart", self.font_small, COLOR_GRAY, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        elif self.game_state == "win":
            self.draw_center_text("YOU WIN!", self.font_large, COLOR_GREEN, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
            self.draw_center_text(f"Score: {self.score}", self.font_small, COLOR_WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.draw_center_text("Press R to Restart", self.font_small, COLOR_GRAY, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        
        # 能量豆效果图标
        if self.power_mode_time > 0:
            blink = (self.power_mode_time // 30) % 2 == 0
            if blink:
                self.draw_center_text("SCARED MODE!", self.font_small, COLOR_CYAN, (MARGIN_X + GRID_SIZE * 9, MARGIN_Y + GRID_SIZE * 21 + 20))
        
        pygame.display.flip()
    
    def draw_center_text(self, text, font, color, pos):
        img = font.render(text, True, color)
        rect = img.get_rect(center=pos)
        self.screen.blit(img, rect)

class Pacman:
    def __init__(self, start_x, start_y):
        self.x = start_x * GRID_SIZE
        self.y = start_y * GRID_SIZE
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.speed = PLAYER_SPEED
        self.mouth_open = 0.2
        self.mouth_angle = 0.1
    
    def set_next_direction(self, direction):
        # 防止反向转向
        if self.direction[0] == -direction[0] and self.direction[1] == -direction[1]:
            return
        self.next_direction = direction
    
    def update(self, walls, open_path):
        # 尝试转向 next_direction
        if self.next_direction != (0, 0):
            test_x = self.x + self.next_direction[0] * self.speed
            test_y = self.y + self.next_direction[1] * self.speed
            test_rect = pygame.Rect(test_x, test_y, GRID_SIZE, GRID_SIZE)
            
            # 检查是否允许继续移动（不穿墙）
            grid_x = (test_x + GRID_SIZE//2) // GRID_SIZE
            grid_y = (test_y + GRID_SIZE//2) // GRID_SIZE
            
            # 检查目标格子是否为空（即墙或越界）
            if (grid_x, grid_y) in walls:
                # 检查是否可以进入通路中心位置
                for d in [(self.direction[0] + GRID_SIZE//2, self.direction[1] + GRID_SIZE//2) for _ in range(1)]:
                    if self.direction != (0, 0):
                        test_pos_x = self.x + self.direction[0] * self.speed
                        test_pos_y = self.y + self.direction[1] * self.speed
                        if (test_pos_x + GRID_SIZE//2) // GRID_SIZE == grid_x and (test_pos_y + GRID_SIZE//2) // GRID_SIZE == grid_y:
                            # 不转向，直接继续沿当前方向
                            break
                        else:
                            # 尝试进入中间位置
                            self.direction = self.next_direction
                            break
                    else:
                        self.direction = self.next_direction
                        break
                else:
                    # 可能会误判，添加兜底策略
                    pass
            else:
                # 成功转向
                aligned = self.align_to_grid()
                if aligned or self.direction == (0, 0):
                    self.direction = self.next_direction
                    self.next_direction = (0, 0)
        
        # 更新位置
        if self.direction != (0, 0):
            new_x = self.x + self.direction[0] * self.speed
            new_y = self.y + self.direction[1] * self.speed
            
            # 边界检测 + 隧道逻辑
            # 左右 Tunnel
            if new_x < -GRID_SIZE//2:
                new_x = SCREEN_WIDTH - MARGIN_X - GRID_SIZE//2 - 1
            elif new_x > SCREEN_WIDTH - MARGIN_X - GRID_SIZE//2:
                new_x = -GRID_SIZE//2
            
            # 检查是否撞墙
            rect = pygame.Rect(new_x, new_y, GRID_SIZE, GRID_SIZE)
            collision = False
            # 检查中间点是否撞墙
            grid_x = (new_x + GRID_SIZE//2) // GRID_SIZE
            grid_y = (new_y + GRID_SIZE//2) // GRID_SIZE
            
            if (grid_x, grid_y) in walls:
                collision = True
            
            if not collision:
                self.x = new_x
                self.y = new_y
        
        # 动画参数
        self.mouth_angle = math.sin(pygame.time.get_ticks() / 50) * 0.2 + 0.1
    
    def align_to_grid(self):
        """判断是否已经对齐到网格中心"""
        center_x = self.x + GRID_SIZE // 2
        center_y = self.y + GRID_SIZE // 2
        remainder_x = center_x % GRID_SIZE
        remainder_y = center_y % GRID_SIZE
        # 确保在允许的误差范围内
        epsilon = 3
        return abs(remainder_x - GRID_SIZE//2) < epsilon or abs(remainder_y - GRID_SIZE//2) < epsilon
    
    def draw(self, screen, margin_x, margin_y):
        # 计算绘制方向角度
        if self.direction == (1, 0):
            angle = 0
        elif self.direction == (-1, 0):
            angle = math.pi
        elif self.direction == (0, 1):
            angle = math.pi / 2
        elif self.direction == (0, -1):
            angle = -math.pi / 2
        else:
            angle = 0
        
        cx = margin_x + self.x + GRID_SIZE // 2
        cy = margin_y + self.y + GRID_SIZE // 2
        radius = GRID_SIZE // 2 - 1
        
        # 绘制黄色 Pacman
        start_angle = self.mouth_angle
        end_angle = 2 * math.pi - self.mouth_angle
        
        points = [(cx, cy)]
        for i in range(360):
            rad = math.radians(angle + i * (end_angle - start_angle) / 360 + start_angle)
            px = cx + radius * math.cos(rad)
            py = cy + radius * math.sin(rad)
            points.append((px, py))
        points.append((cx, cy))
        
        pygame.draw.polygon(screen, COLOR_YELLOW, points)
        pygame.draw.polygon(screen, COLOR_BLACK, points, 2)


class Ghost:
    def __init__(self, start_pos, color, ghost_id):
        self.x = start_pos[0] * GRID_SIZE
        self.y = start_pos[1] * GRID_SIZE
        self.color = color
        self.ghost_id = ghost_id
        self.speed = GHOST_SPEED
        self.direction = (0, 0)
        self.scared = False
        self.scared_timer = 0
        self.direction_queue = []
    
    def update(self, walls, open_path, pacman):
        # 如果当前速度为0或尚未设置，先随机选择方向
        if self.direction == (0, 0):
            self.direction = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        
        # 更新方向（每4个像素更新一次，以避开穿墙）
        center_x = self.x + GRID_SIZE // 2
        center_y = self.y + GRID_SIZE // 2
        grid_x = center_x // GRID_SIZE
        grid_y = center_y // GRID_SIZE
        
        # 每次更新都尝试调整方向
        if self.x % GRID_SIZE == 0 and self.y % GRID_SIZE == 0:
            self.decide_direction(grid_x, grid_y, walls, pacman)
        
        # 移动
        new_x = self.x + self.direction[0] * self.speed
        new_y = self.y + self.direction[1] * self.speed
        
        # 边界检测
        if new_x < -GRID_SIZE//2:
            new_x = SCREEN_WIDTH - MARGIN_X - GRID_SIZE//2 - 1
        elif new_x > SCREEN_WIDTH - MARGIN_X - GRID_SIZE//2:
            new_x = -GRID_SIZE//2
        
        # 检查碰撞
        test_grid_x = (new_x + GRID_SIZE // 2) // GRID_SIZE
        test_grid_y = (new_y + GRID_SIZE // 2) // GRID_SIZE
        
        if (test_grid_x, test_grid_y) not in walls:
            self.x = new_x
            self.y = new_y
        else:
            # 回退一格并尝试新方向
            self.direction = (0, 0)
            self.decide_direction(grid_x, grid_y, walls, pacman)
    
    def decide_direction(self, grid_x, grid_y, walls, pacman):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        valid_directions = []
        
        for dx, dy in directions:
            nx = grid_x + dx
            ny = grid_y + dy
            
            if (nx, ny) not in walls:
                # 防止反向移动
                if (dx, dy) != (-self.direction[0], -self.direction[1]) or len(valid_directions) == 0:
                    valid_directions.append((dx, dy))
        
        if not valid_directions:
            # 无路可走（死胡同），允许反向
            for dx, dy in directions:
                nx = grid_x + dx
                ny = grid_y + dy
                if (nx, ny) not in walls:
                    valid_directions.append((dx, dy))
        
        if len(valid_directions) == 1:
            self.direction = valid_directions[0]
        elif len(valid_directions) > 1:
            # 路口策略
            if self.scared:
                # 爱运动（随机）
                self.direction = random.choice(valid_directions)
            else:
                # Blinky 追踪 Pacman
                if self.ghost_id == 0:
                    # 追踪玩家
                    best_dir = self.find_best_direction(pacman.x, pacman.y, valid_directions, grid_x, grid_y)
                    self.direction = best_dir
                else:
                    # 其他幽灵简单策略：部分随机
                    if self.ghost_id == 1 and random.random() > 0.5:
                        self.direction = random.choice(valid_directions)
                    elif self.ghost_id == 2:
                        # Cyan 随机性高
                        self.direction = random.choice(valid_directions)
                    else:
                        self.direction = self.find_best_direction(pacman.x, pacman.y, valid_directions, grid_x, grid_y)
        else:
            # 只能保持原方向
            pass
    
    def find_best_direction(self, target_x, target_y, valid_directions, grid_x, grid_y):
        best_dir = valid_directions[0]
        best_dist = float('inf')
        
        for dx, dy in valid_directions:
            # 获取下一步位置
            next_x = grid_x + dx
            next_y = grid_y + dy
            
            # 计算距离
            dist = math.sqrt((next_x * GRID_SIZE - target_x)**2 + (next_y * GRID_SIZE - target_y)**2)
            if dist < best_dist:
                best_dist = dist
                best_dir = (dx, dy)
        
        return best_dir
    
    def draw(self, screen, margin_x, margin_y):
        cx = margin_x + self.x + GRID_SIZE // 2
        cy = margin_y + self.y + GRID_SIZE // 2
        
        if self.scared:
            color = (0, 0, 255)  # 蓝色
        else:
            color = self.color
        
        # 绘制幽灵形状（圆角顶）
        if self.scared:
            pygame.draw.circle(screen, color, (cx, cy), GRID_SIZE // 2 - 1)
        else:
            points = [
                (cx, cy - GRID_SIZE//2 + 3),
                (cx + GRID_SIZE//2 - 1, cy - GRID_SIZE//4),
                (cx + GRID_SIZE//2 - 1, cy + GRID_SIZE//2 - 1),
                (cx + GRID_SIZE//4, cy + GRID_SIZE//2 - 1),
                (cx, cy + GRID_SIZE//2 - 3),
                (cx - GRID_SIZE//4, cy + GRID_SIZE//2 - 1),
                (cx - GRID_SIZE//2 + 1, cy + GRID_SIZE//2 - 1),
                (cx - GRID_SIZE//2 + 1, cy - GRID_SIZE//4)
            ]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, COLOR_BLACK, points, 2)
        
        # 眼睛
        eye_offset = 4
        eye_radius = 4
        eye_color = COLOR_WHITE
        
        if not self.scared:
            pygame.draw.circle(screen, eye_color, (cx - 4, cy - 2), eye_radius)
            pygame.draw.circle(screen, eye_color, (cx + 4, cy - 2), eye_radius)
            # 瞳孔
            dir_offset = (0, 0)
            if self.direction == (1, 0): dir_offset = (1, 0)
            elif self.direction == (-1, 0): dir_offset = (-1, 0)
            elif self.direction == (0, -1): dir_offset = (0, -1)
            elif self.direction == (0, 1): dir_offset = (0, 1)
            
            pygame.draw.circle(screen, (0, 0, 0), (cx - 4 + dir_offset[0]*1, cy - 2 + dir_offset[1]*1), 2)
            pygame.draw.circle(screen, (0, 0, 0), (cx + 4 + dir_offset[0]*1, cy - 2 + dir_offset[1]*1), 2)

# 全局常量补充
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_GRAY = (128, 128, 128)

if __name__ == "__main__":
    game = PacmanGame()
    game.run()