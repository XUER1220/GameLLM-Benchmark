import pygame
import random
import sys

# 固定参数
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GAME_GRID_COLS = 19
GAME_GRID_ROWS = 21
CELL_SIZE = 24
MARGIN_TOP = (WINDOW_HEIGHT - GAME_GRID_ROWS * CELL_SIZE) // 2
MARGIN_LEFT = (WINDOW_WIDTH - GAME_GRID_COLS * CELL_SIZE - 250) // 2  # 右侧预留HUD区域
FPS = 60
PLAYER_SPEED = 3
ENERGY_DURATION = 6 * FPS  # 6秒，帧数
PLAYER_LIVES = 3
SCORE_NORMAL_PELLET = 10
SCORE_POWER_PELLET = 50
SCORE_GHOST_EAT = 200
GAME_GRID_TOP = MARGIN_TOP
GAME_GRID_LEFT = MARGIN_LEFT

# 颜色定义
COLOR_WALL = (33, 66, 150)
COLOR_PELLET = (220, 220, 220)
COLOR_POWER_PELLET = (255, 255, 255)
COLOR_PLAYER = (255, 255, 0)
COLOR_GHOST1 = (255, 0, 0)     # Blinky (红)
COLOR_GHOST2 = (255, 184, 255) # Pinky (粉)
COLOR_GHOST3 = (0, 255, 255)   # Inky (青)
COLOR_GHOST4 = (255, 184, 82)  # Clyde (橙)
COLOR_SCARED_GHOST1 = (0, 0, 255)
COLOR_SCARED_GHOST2 = (0, 0, 200)
COLOR_GAME_TEXT = (255, 255, 255)
COLOR_HUD = (255, 255, 255)
COLOR_BG = (0, 0, 0)

# 迷宫地图: '#'=墙, '.'=普通豆子, 'o'=能量豆, ' '=空, 'P'=玩家出生点, 'G'=幽灵出生区
# 19列 x 21行
LEVEL_MAP = [
    "###################",
    "#........#........#",
    "#.##.###.#.###.##.#",
    "#o##.###.#.###.##o#",
    "#.##.###.#.###.##.#",
    "#.................#",
    "#.##.#.#####.#.##.#",
    "#....#...#...#....#",
    "####.#.G.G.G.#.####",
    "    #.G.....G.#    ",
    "####.#.#####.#.####",
    "#.................#",
    "#.##.###.#.###.##.#",
    "#o.#...#...#...#.o#",
    "##.#.#.#.#.#.#.#.##",
    "#....#...P...#....#",
    "#.######.###.######",
    "#........#........#",
    "#.##.###.#.###.##.#",
    "#........#........#",
    "###################"
]

# 游戏状态常量
INITIAL_STATE = 'initial'
PLAYING = 'playing'
GAME_OVER = 'game_over'
VICTORY = 'victory'

random.seed(42)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.SysFont(None, 24)
        self.font_large = pygame.font.SysFont(None, 48)
        
        self.reset_game()
    
    def reset_game(self):
        self.grid = []
        self.pellets = []
        self.power_pellets = []
        self.player_start = (0, 0)
        self.ghost_starts = []
        
        for row_idx, row in enumerate(LEVEL_MAP):
            grid_row = []
            for col_idx, tile in enumerate(row):
                if tile == '#':
                    grid_row.append('wall')
                elif tile == '.':
                    grid_row.append('pellet')
                    self.pellets.append((col_idx, row_idx))
                elif tile == 'o':
                    grid_row.append('power_pellet')
                    self.power_pellets.append((col_idx, row_idx))
                elif tile == 'P':
                    grid_row.append('empty')
                    self.player_start = (col_idx, row_idx)
                elif tile == ' ':
                    grid_row.append('empty')
                elif tile == 'G':
                    grid_row.append('empty')
                    self.ghost_starts.append((col_idx, row_idx))
                else:
                    grid_row.append('empty')
            self.grid.append(grid_row)
        
        self.player = Pacman(self.player_start[0], self.player_start[1])
        self.ghosts = []
        ghost_colors = [
            (COLOR_GHOST1, 0),
            (COLOR_GHOST2, 1),
            (COLOR_GHOST3, 2),
            (COLOR_GHOST4, 3)
        ]
        
        # 用前四个幽灵出生点；如果不足则循环
        for i in range(min(4, len(self.ghost_starts))):
            x, y = self.ghost_starts[i]
            color, _ = ghost_colors[i]
            self.ghosts.append(Ghost(x, y, color, i))
        
        # 初始化游戏状态
        self.score = 0
        self.lives = PLAYER_LIVES
        self.state = INITIAL_STATE
        self.energy_active = False
        self.energy_timer = 0
        self.game_over_reason = ""
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:
                    self.reset_game()
                elif self.state == PLAYING:
                    if event.key == pygame.K_UP:
                        self.player.set_direction(0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.player.set_direction(0, 1)
                    elif event.key == pygame.K_LEFT:
                        self.player.set_direction(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.player.set_direction(1, 0)
        return True
    
    def update(self):
        if self.state == PLAYING:
            # 玩家移动
            self.player.move(self.grid)
            
            # 豆子检测
            self.collect_pellets()
            
            # 能量状态检测
            if self.energy_active:
                self.energy_timer -= 1
                if self.energy_timer <= 0:
                    self.energy_active = False
            
            # 幽灵移动
            for ghost in self.ghosts:
                ghost.move(self.grid, self.player, self.energy_active)
            
            # 玩家与幽灵碰撞检测
            self.check_ghost_collision()
            
            # 胜负判定
            if self.lives <= 0:
                self.state = GAME_OVER
                self.game_over_reason = "Game Over"
            elif len(self.pellets) == 0 and len(self.power_pellets) == 0:
                self.state = VICTORY
                self.game_over_reason = "You Win"
    
    def collect_pellets(self):
        px, py = self.player.get_grid_position()
        # 检查普通豆子
        if (px, py) in self.pellets:
            self.pellets.remove((px, py))
            self.score += SCORE_NORMAL_PELLET
        
        # 检查能量豆
        if (px, py) in self.power_pellets:
            self.power_pellets.remove((px, py))
            self.score += SCORE_POWER_PELLET
            self.energy_active = True
            self.energy_timer = ENERGY_DURATION
    
    def check_ghost_collision(self):
        px, py = self.player.get_grid_position()
        for ghost in self.ghosts:
            gx, gy = ghost.get_grid_position()
            if px == gx and py == gy:
                if self.energy_active:
                    self.score += SCORE_GHOST_EAT
                    ghost.go_to_start()
                else:
                    self.lives -= 1
                    self.player.reset_position()
                    for g in self.ghosts:
                        g.go_to_start()
    
    def draw(self):
        self.screen.fill(COLOR_BG)
        
        # 绘制迷宫
        self.draw_maze()
        
        # 绘制游戏对象
        self.player.draw(self.screen)
        for ghost in self.ghosts:
            ghost.draw(self.screen)
        
        # 绘制HUD
        self.draw_hud()
        
        # 绘制游戏状态信息
        if self.state in (GAME_OVER, VICTORY):
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_maze(self):
        # 墙体
        for row_idx, row in enumerate(self.grid):
            for col_idx, tile in enumerate(row):
                if tile == 'wall':
                    x = GAME_GRID_LEFT + col_idx * CELL_SIZE
                    y = GAME_GRID_TOP + row_idx * CELL_SIZE
                    pygame.draw.rect(self.screen, COLOR_WALL, (x, y, CELL_SIZE, CELL_SIZE))
        
        # 豆子
        for (x, y) in self.pellets:
            cx = GAME_GRID_LEFT + x * CELL_SIZE + CELL_SIZE // 2
            cy = GAME_GRID_TOP + y * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(self.screen, COLOR_PELLET, (cx, cy), 3)
        
        # 能量豆
        for (x, y) in self.power_pellets:
            cx = GAME_GRID_LEFT + x * CELL_SIZE + CELL_SIZE // 2
            cy = GAME_GRID_TOP + y * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(self.screen, COLOR_POWER_PELLET, (cx, cy), 7)
    
    def draw_hud(self):
        y_offset = GAME_GRID_TOP + 5
        text_y = y_offset
        self.draw_text(f"Score: {self.score}", GAME_GRID_LEFT, text_y, COLOR_HUD)
        text_y += 25
        self.draw_text(f"Lives: {self.lives}", GAME_GRID_LEFT, text_y, COLOR_HUD)
        text_y += 25
        self.draw_text(f"Remaining Pellets: {len(self.pellets) + len(self.power_pellets)}", GAME_GRID_LEFT, text_y, COLOR_HUD)
    
    def draw_game_over(self):
        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2
        
        text1 = self.font_large.render(self.game_over_reason, True, COLOR_GAME_TEXT)
        text2 = self.font_small.render(f"Final Score: {self.score}", True, COLOR_GAME_TEXT)
        text3 = self.font_small.render("Press R to Restart", True, COLOR_GAME_TEXT)
        
        text_rect1 = text1.get_rect(center=(center_x, center_y - 40))
        text_rect2 = text2.get_rect(center=(center_x, center_y))
        text_rect3 = text3.get_rect(center=(center_x, center_y + 40))
        
        self.screen.blit(text1, text_rect1)
        self.screen.blit(text2, text_rect2)
        self.screen.blit(text3, text_rect3)
    
    def draw_text(self, text, x, y, color):
        rendered_text = self.font_small.render(text, True, color)
        self.screen.blit(rendered_text, (x, y))
    
    def run(self):
        running = True
        self.state = PLAYING
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


class Pacman:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = GAME_GRID_LEFT + grid_x * CELL_SIZE + CELL_SIZE // 2
        self.y = GAME_GRID_TOP + grid_y * CELL_SIZE + CELL_SIZE // 2
        self.dx = 0
        self.dy = 0
        self.next_dx = 0
        self.next_dy = 0
        self.radius = CELL_SIZE // 2 - 2
    
    def set_direction(self, dx, dy):
        # 允许预判方向
        self.next_dx = dx
        self.next_dy = dy
    
    def get_grid_position(self):
        return (self.grid_x, self.grid_y)
    
    def reset_position(self):
        self.grid_x = GAME_GRID_COLS // 2
        self.grid_y = GAME_GRID_ROWS // 2 + 1
        self.x = GAME_GRID_LEFT + self.grid_x * CELL_SIZE + CELL_SIZE // 2
        self.y = GAME_GRID_TOP + self.grid_y * CELL_SIZE + CELL_SIZE // 2
        self.dx = 0
        self.dy = 0
        self.next_dx = 0
        self.next_dy = 0
    
    def move(self, grid):
        # 尝试转向
        if self.next_dx != 0 or self.next_dy != 0:
            # 检查下一个格子是否为空或豆子（允许在中心位置转向）
            next_grid_x = self.grid_x + self.next_dx
            next_grid_y = self.grid_y + self.next_dy
            if self.can_move_to(next_grid_x, next_grid_y, grid):
                self.dx = self.next_dx
                self.dy = self.next_dy
                self.next_dx = 0
                self.next_dy = 0
        
        # 实际移动
        next_x = self.x + self.dx * PLAYER_SPEED
        next_y = self.y + self.dy * PLAYER_SPEED
        next_grid_x = self.grid_x + self.dx
        next_grid_y = self.grid_y + self.dy
        
        if self.can_move_to(next_grid_x, next_grid_y, grid):
            self.x = next_x
            self.y = next_y
            self.dx = self.dx
            self.dy = self.dy
        else:
            # 检查是否在通道尽头（左右贯通）
            if self.x < 0:
                self.x = WINDOW_WIDTH
                self.grid_x = GAME_GRID_COLS - 1
            elif self.x >= WINDOW_WIDTH:
                self.x = 0
                self.grid_x = 0
        
        # 更新网格坐标
        self.grid_x = (self.x - GAME_GRID_LEFT) // CELL_SIZE
        self.grid_y = (self.y - GAME_GRID_TOP) // CELL_SIZE
        
        # 处理左右贯通逻辑（修正）
        if self.x < GAME_GRID_LEFT:
            self.x = GAME_GRID_LEFT + (GAME_GRID_COLS - 1) * CELL_SIZE + CELL_SIZE // 2
            self.grid_x = GAME_GRID_COLS - 1
        elif self.x >= GAME_GRID_LEFT + GAME_GRID_COLS * CELL_SIZE:
            self.x = GAME_GRID_LEFT + CELL_SIZE // 2
            self.grid_x = 0
    
    def can_move_to(self, grid_x, grid_y, grid):
        if 0 <= grid_x < GAME_GRID_COLS and 0 <= grid_y < GAME_GRID_ROWS:
            tile = grid[grid_y][grid_x]
            return tile != 'wall'
        return False
    
    def draw(self, screen):
        center = (int(self.x), int(self.y))
        # 吃豆人嘴巴动画模拟
        mouth = abs(pygame.time.get_ticks() % 200 - 100) / 100.0 * 0.25 * 3.14159
        
        if self.dx == 1:  # Right
            start_angle = 0.26 * 3.14159
            end_angle = 2.88 * 3.14159
        elif self.dx == -1:  # Left
            start_angle = 0.26 * 3.14159 + 3.14159
            end_angle = 2.88 * 3.14159 + 3.14159
        elif self.dy == -1:  # Up
            start_angle = 0.26 * 3.14159 + 1.5708
            end_angle = 2.88 * 3.14159 + 1.5708
        elif self.dy == 1:  # Down
            start_angle = 0.26 * 3.14159 - 1.5708
            end_angle = 2.88 * 3.14159 - 1.5708
        else:  # Idle
            start_angle = 0.26 * 3.14159
            end_angle = 2.88 * 3.14159
        
        # 动画嘴巴张合
        if self.dx != 0 or self.dy != 0:
            mouth_adjust = 0.1 * abs(pygame.time.get_ticks() % 500 - 250) / 250.0
            start_angle += mouth_adjust if self.dx in (1, 0) and self.dy in (1, 0) else -mouth_adjust
            end_angle -= mouth_adjust if self.dx in (1, 0) and self.dy in (1, 0) else mouth_adjust
        
        pygame.draw.circle(screen, COLOR_PLAYER, center, self.radius)
        pygame.draw.circle(screen, COLOR_BG, center, self.radius, 1)
        
        # 绘制嘴巴
        mouth_points = [
            center,
            (center[0] + self.radius * pygame.math.Vector2(1, 0).rotate(pygame.math.Vector2(0, 1).angle_to((1, 0)) + start_angle).x),
            (center[0] + self.radius * pygame.math.Vector2(1, 0).rotate(start_angle).x,
             center[1] + self.radius * pygame.math.Vector2(1, 0).rotate(start_angle).y),
            (center[0] + self.radius * pygame.math.Vector2(1, 0).rotate(end_angle).x,
             center[1] + self.radius * pygame.math.Vector2(1, 0).rotate(end_angle).y)
        ]
        pygame.draw.polygon(screen, COLOR_BG, mouth_points)


class Ghost:
    def __init__(self, grid_x, grid_y, color, index):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.start_grid_x = grid_x
        self.start_grid_y = grid_y
        self.x = GAME_GRID_LEFT + grid_x * CELL_SIZE + CELL_SIZE // 2
        self.y = GAME_GRID_TOP + grid_y * CELL_SIZE + CELL_SIZE // 2
        self.color = color
        self.index = index
        self.directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        self.dx = self.directions[index][0]
        self.dy = self.directions[index][1]
        self.scared = False
        self.speed = 2
    
    def get_grid_position(self):
        return (self.grid_x, self.grid_y)
    
    def go_to_start(self):
        self.grid_x = self.start_grid_x
        self.grid_y = self.start_grid_y
        self.x = GAME_GRID_LEFT + self.grid_x * CELL_SIZE + CELL_SIZE // 2
        self.y = GAME_GRID_TOP + self.grid_y * CELL_SIZE + CELL_SIZE // 2
        self.dx = 0
        self.dy = 0
    
    def move(self, grid, player, energy_active):
        self.scared = energy_active
        
        # 更新网格位置
        self.grid_x = (self.x - GAME_GRID_LEFT) // CELL_SIZE
        self.grid_y = (self.y - GAME_GRID_TOP) // CELL_SIZE
        
        # 每次移动一步
        next_x = self.x + self.dx * self.speed
        next_y = self.y + self.dy * self.speed
        
        next_grid_x = self.grid_x + self.dx
        next_grid_y = self.grid_y + self.dy
        
        # 检查前方是否有墙
        if self.can_move_to(next_grid_x, next_grid_y, grid):
            self.x = next_x
            self.y = next_y
        else:
            self.change_direction(grid, player)
            next_grid_x = self.grid_x + self.dx
            next_grid_y = self.grid_y + self.dy
            if self.can_move_to(next_grid_x, next_grid_y, grid):
                self.x += self.dx * self.speed
                self.y += self.dy * self.speed
        
        # 处理左右贯通逻辑
        if self.x < 0:
            self.x = WINDOW_WIDTH
            self.grid_x = GAME_GRID_COLS - 1
        elif self.x >= WINDOW_WIDTH:
            self.x = 0
            self.grid_x = 0
    
    def can_move_to(self, grid_x, grid_y, grid):
        if 0 <= grid_x < GAME_GRID_COLS and 0 <= grid_y < GAME_GRID_ROWS:
            return grid[grid_y][grid_x] != 'wall'
        return False
    
    def change_direction(self, grid, player):
        valid_directions = []
        for dx, dy in self.directions:
            if self.can_move_to(self.grid_x + dx, self.grid_y + dy, grid):
                # 不允许直接掉头（除非死胡同）
                if dx != -self.dx or dy != -self.dy or len(valid_directions) == 0:
                    valid_directions.append((dx, dy))
        
        if len(valid_directions) == 0:
            # 死胡同：只能掉头
            if self.can_move_to(self.grid_x - self.dx, self.grid_y - self.dy, grid):
                self.dx = -self.dx
                self.dy = -self.dy
            return
        
        # 选择最优方向
        if self.scared:
            # 逃跑：远离玩家（伪），实际随机
            self.dx, self.dy = random.choice(valid_directions)
        else:
            # 追逐：优先朝玩家方向移动（曼哈顿距离）
            best_direction = None
            min_dist = float('inf')
            
            player_grid_x = player.get_grid_position()[0]
            player_grid_y = player.get_grid_position()[1]
            
            for dx, dy in valid_directions:
                new_x = self.grid_x + dx
                new_y = self.grid_y + dy
                dist = abs(new_x - player_grid_x) + abs(new_y - player_grid_y)
                if dist < min_dist:
                    min_dist = dist
                    best_direction = (dx, dy)
            
            if best_direction:
                self.dx, self.dy = best_direction
            else:
                self.dx, self.dy = random.choice(valid_directions)
    
    def draw(self, screen):
        center = (int(self.x), int(self.y))
        
        # 精灵颜色
        if self.scared:
            # 蓝色闪烁效果
            if pygame.time.get_ticks() // 100 % 2 == 0:
                color = COLOR_SCARED_GHOST1
            else:
                color = COLOR_SCARED_GHOST2
        else:
            color = self.color
        
        # 绘制幽灵（圆顶矩形）
        radius = CELL_SIZE // 2 - 2
        body_rect = pygame.Rect(center[0] - radius, center[1] - radius, radius * 2, radius * 2)
        pygame.draw.circle(screen, color, (center[0], center[1] - 2), radius)
        pygame.draw.rect(screen, color, (center[0] - radius, center[1] - 2, radius * 2, radius))
        
        # 眼睛
        eye_offset = 4
        eye_size = 3
        if self.dx == 0 and self.dy == 0:
            pygame.draw.circle(screen, (255, 255, 255), (center[0] - 3, center[1] - 5), eye_size)
            pygame.draw.circle(screen, (255, 255, 255), (center[0] + 3, center[1] - 5), eye_size)
        elif self.dx == 1:
            pygame.draw.circle(screen, (255, 255, 255), (center[0] - 2, center[1] - 5), eye_size)
            pygame.draw.circle(screen, (255, 255, 255), (center[0] - 2, center[1] + 1), eye_size)
        elif self.dx == -1:
            pygame.draw.circle(screen, (255, 255, 255), (center[0] + 2, center[1] - 5), eye_size)
            pygame.draw.circle(screen, (255, 255, 255), (center[0] + 2, center[1] + 1), eye_size)
        elif self.dy == 1:
            pygame.draw.circle(screen, (255, 255, 255), (center[0] - 5, center[1] + 2), eye_size)
            pygame.draw.circle(screen, (255, 255, 255), (center[0] + 1, center[1] + 2), eye_size)
        elif self.dy == -1:
            pygame.draw.circle(screen, (255, 255, 255), (center[0] - 5, center[1] - 2), eye_size)
            pygame.draw.circle(screen, (255, 255, 255), (center[0] + 1, center[1] - 2), eye_size)


if __name__ == "__main__":
    game = Game()
    game.run()