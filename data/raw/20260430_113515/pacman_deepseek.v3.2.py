import pygame
import random
import sys

# ========== 常量定义 ==========
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CELL_SIZE = 24
MAZE_COLS = 19
MAZE_ROWS = 21
MAZE_WIDTH = MAZE_COLS * CELL_SIZE
MAZE_HEIGHT = MAZE_ROWS * CELL_SIZE
MAZE_OFFSET_X = (SCREEN_WIDTH - MAZE_WIDTH) // 2 - 100
MAZE_OFFSET_Y = (SCREEN_HEIGHT - MAZE_HEIGHT) // 2
FPS = 60
PLAYER_SPEED = 3
GHOST_SPEED = 2
POWER_DURATION = 6 * FPS  # 6 秒
PLAYER_LIVES = 3
SCORE_DOT = 10
SCORE_POWER = 50
SCORE_GHOST = 200
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# 颜色定义
COLOR_BG = (0, 0, 0)
COLOR_WALL = (0, 0, 150)
COLOR_PATH = (0, 0, 20)
COLOR_DOT = (255, 255, 200)
COLOR_POWER = (255, 255, 0)
COLOR_PLAYER = (255, 255, 0)
COLOR_HUD = (255, 255, 255)
COLOR_TEXT = (255, 255, 255)
COLOR_WIN = (0, 255, 0)
COLOR_LOSE = (255, 50, 50)
GHOST_COLORS = [
    (255, 0, 0),      # 红
    (255, 182, 255),  # 粉
    (0, 255, 255),    # 青
    (255, 184, 82)    # 橙
]
COLOR_GHOST_VULNERABLE = (0, 0, 255)

# 迷宫定义 (19x21)
# '#' 墙, '.' 通路, 'o' 豆子, 'O' 能量豆, 'P' 玩家出生点, 'G' 幽灵出生区
MAZE_LAYOUT = [
    "###################",
    "#........#........#",
    "#o##.###.#.###.##o#",
    "#.................#",
    "#.##.#.#####.#.##.#",
    "#....#...#...#....#",
    "#.####.#G#G#.####.#",
    "#......#GGG#......#",
    "#.####.#####.####.#",
    "#.................#",
    "#o##.#.#####.#.##o#",
    "#...#.#.....#...#.#",
    "###.#.#G###G#.#.###",
    "#.....#GGGGG#.....#",
    "###.#.#G###G#.#.###",
    "#...#.#.....#...#.#",
    "#o##.#.#####.#.##o#",
    "#.................#",
    "#.####.#####.####.#",
    "#......#   #......#",
    "###################"
]

# ========== 游戏对象 ==========
class Player:
    def __init__(self, x, y):
        self.start_x = x
        self.start_y = y
        self.reset()
    
    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.target_x = self.x
        self.target_y = self.y
        self.moving = False
        self.direction = (0, 0)
        self.next_direction = (0, 0)
    
    def move(self):
        if not self.moving:
            return
        self.x += self.direction[0] * PLAYER_SPEED
        self.y += self.direction[1] * PLAYER_SPEED
        # 对齐网格中心
        if abs(self.x - self.target_x) < PLAYER_SPEED and abs(self.y - self.target_y) < PLAYER_SPEED:
            self.x, self.y = self.target_x, self.target_y
            self.moving = False
    
    def set_direction(self, dx, dy, maze):
        if (dx, dy) == (0, 0):
            self.next_direction = (0, 0)
            return
        nx = self.target_x + dx * CELL_SIZE
        ny = self.target_y + dy * CELL_SIZE
        grid_x = nx // CELL_SIZE
        grid_y = ny // CELL_SIZE
        if 0 <= grid_x < MAZE_COLS and 0 <= grid_y < MAZE_ROWS:
            if MAZE_LAYOUT[grid_y][grid_x] != '#':
                self.next_direction = (dx, dy)
    
    def update(self, maze):
        if not self.moving:
            dx, dy = self.next_direction
            nx = self.target_x + dx * CELL_SIZE
            ny = self.target_y + dy * CELL_SIZE
            grid_x = nx // CELL_SIZE
            grid_y = ny // CELL_SIZE
            if 0 <= grid_x < MAZE_COLS and 0 <= grid_y < MAZE_ROWS:
                if MAZE_LAYOUT[grid_y][grid_x] != '#':
                    self.direction = (dx, dy)
                    self.target_x = nx
                    self.target_y = ny
                    self.moving = True
        self.move()
        # 隧道穿梭
        if self.x < -CELL_SIZE:
            self.x = MAZE_WIDTH
        elif self.x >= MAZE_WIDTH + CELL_SIZE:
            self.x = -CELL_SIZE
    
    def get_grid_pos(self):
        return (int(self.x // CELL_SIZE), int(self.y // CELL_SIZE))

class Ghost:
    def __init__(self, x, y, color_idx):
        self.start_x = x
        self.start_y = y
        self.color_idx = color_idx
        self.reset()
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # 固定优先级顺序
    
    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.dx = -1
        self.dy = 0
        self.vulnerable = False
        self.vulnerable_timer = 0
        self.dead = False
    
    def choose_direction(self, maze, player_grid):
        if self.dead:
            # 回出生点
            gx, gy = self.get_grid_pos()
            sx, sy = self.start_x // CELL_SIZE, self.start_y // CELL_SIZE
            if gx < sx:
                return (1, 0)
            elif gx > sx:
                return (-1, 0)
            elif gy < sy:
                return (0, 1)
            elif gy > sy:
                return (0, -1)
            else:
                self.dead = False
                self.vulnerable = False
                return (0, 0)
        
        gx, gy = self.get_grid_pos()
        px, py = player_grid
        # 追逐玩家方向
        best_dir = None
        best_dist = float('inf')
        for dx, dy in self.directions:
            nx, ny = gx + dx, gy + dy
            if 0 <= nx < MAZE_COLS and 0 <= ny < MAZE_ROWS:
                if maze[ny][nx] != '#':
                    dist = abs(nx - px) + abs(ny - py)
                    if dist < best_dist:
                        best_dist = dist
                        best_dir = (dx, dy)
        if best_dir is None:
            best_dir = (0, 0)
        # 避免立即掉头
        if (-self.dx, -self.dy) == best_dir:
            for dx, dy in self.directions:
                if (dx, dy) != (-self.dx, -self.dy):
                    nx, ny = gx + dx, gy + dy
                    if 0 <= nx < MAZE_COLS and 0 <= ny < MAZE_ROWS and maze[ny][nx] != '#':
                        best_dir = (dx, dy)
                        break
        return best_dir
    
    def update(self, maze, player_grid, power_active):
        if not power_active:
            self.vulnerable = False
            self.vulnerable_timer = 0
        
        if self.vulnerable:
            self.vulnerable_timer -= 1
            if self.vulnerable_timer <= 0:
                self.vulnerable = False
        
        gx, gy = self.get_grid_pos()
        # 检查是否在网格中心才改变方向
        if (int(self.x) % CELL_SIZE == 0 and int(self.y) % CELL_SIZE == 0):
            self.dx, self.dy = self.choose_direction(maze, player_grid)
        
        nx = self.x + self.dx * GHOST_SPEED
        ny = self.y + self.dy * GHOST_SPEED
        grid_x = int(nx // CELL_SIZE)
        grid_y = int(ny // CELL_SIZE)
        # 检查移动是否合法
        if 0 <= grid_x < MAZE_COLS and 0 <= grid_y < MAZE_ROWS:
            if maze[grid_y][grid_x] != '#':
                self.x = nx
                self.y = ny
        # 隧道穿梭
        if self.x < -CELL_SIZE:
            self.x = MAZE_WIDTH
        elif self.x >= MAZE_WIDTH + CELL_SIZE:
            self.x = -CELL_SIZE
    
    def get_grid_pos(self):
        return (int(self.x // CELL_SIZE), int(self.y // CELL_SIZE))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Man Medium")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.big_font = pygame.font.SysFont(None, 48)
        self.reset_game()
    
    def reset_game(self):
        self.score = 0
        self.lives = PLAYER_LIVES
        self.dots_left = 0
        self.power_active = False
        self.power_timer = 0
        self.game_over = False
        self.game_win = False
        
        # 解析迷宫
        self.maze_grid = []
        self.dots = []
        player_start = None
        ghost_starts = []
        for y, row in enumerate(MAZE_LAYOUT):
            maze_row = []
            for x, ch in enumerate(row):
                maze_row.append(ch)
                if ch == 'P':
                    player_start = (x * CELL_SIZE + CELL_SIZE//2, y * CELL_SIZE + CELL_SIZE//2)
                elif ch == 'G':
                    ghost_starts.append((x * CELL_SIZE + CELL_SIZE//2, y * CELL_SIZE + CELL_SIZE//2))
                elif ch == '.':
                    self.dots.append((x, y))
                    self.dots_left += 1
                elif ch == 'o':
                    self.dots.append((x, y))
                    self.dots_left += 1
                elif ch == 'O':
                    self.dots.append((x, y))
                    self.dots_left += 1
            self.maze_grid.append(maze_row)
        
        # 初始化玩家
        if player_start:
            self.player = Player(player_start[0], player_start[1])
        else:
            self.player = Player(CELL_SIZE*9 + CELL_SIZE//2, CELL_SIZE*10 + CELL_SIZE//2)
        
        # 初始化幽灵
        self.ghosts = []
        for i, (gx, gy) in enumerate(ghost_starts[:4]):
            self.ghosts.append(Ghost(gx, gy, i))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    self.reset_game()
                if not self.game_over and not self.game_win:
                    if event.key == pygame.K_UP:
                        self.player.set_direction(0, -1, self.maze_grid)
                    if event.key == pygame.K_DOWN:
                        self.player.set_direction(0, 1, self.maze_grid)
                    if event.key == pygame.K_LEFT:
                        self.player.set_direction(-1, 0, self.maze_grid)
                    if event.key == pygame.K_RIGHT:
                        self.player.set_direction(1, 0, self.maze_grid)
    
    def update(self):
        if self.game_over or self.game_win:
            return
        
        # 更新玩家
        self.player.update(self.maze_grid)
        player_grid = self.player.get_grid_pos()
        
        # 能量豆计时
        if self.power_active:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.power_active = False
        
        # 更新幽灵
        for ghost in self.ghosts:
            ghost.update(self.maze_grid, player_grid, self.power_active)
        
        # 吃豆子
        px, py = player_grid
        if (px, py) in self.dots:
            self.dots.remove((px, py))
            self.dots_left -= 1
            ch = self.maze_grid[py][px]
            if ch == '.':
                self.score += SCORE_DOT
            elif ch == 'o':
                self.score += SCORE_DOT
            elif ch == 'O':
                self.score += SCORE_POWER
                self.power_active = True
                self.power_timer = POWER_DURATION
                for ghost in self.ghosts:
                    if not ghost.dead:
                        ghost.vulnerable = True
                        ghost.vulnerable_timer = POWER_DURATION
            self.maze_grid[py][px] = ' '
        
        # 检查豆子吃完
        if self.dots_left == 0:
            self.game_win = True
        
        # 碰撞检测
        for ghost in self.ghosts:
            gx, gy = ghost.get_grid_pos()
            if (px, py) == (gx, gy) or (abs(self.player.x - ghost.x) < CELL_SIZE//2 and abs(self.player.y - ghost.y) < CELL_SIZE//2):
                if ghost.vulnerable and not ghost.dead:
                    # 吃掉幽灵
                    ghost.dead = True
                    ghost.x, ghost.y = ghost.start_x, ghost.start_y
                    self.score += SCORE_GHOST
                elif not ghost.vulnerable and not ghost.dead:
                    # 玩家死亡
                    self.lives -= 1
                    self.player.reset()
                    for g in self.ghosts:
                        g.reset()
                    if self.lives <= 0:
                        self.game_over = True
    
    def draw(self):
        self.screen.fill(COLOR_BG)
        
        # 绘制迷宫
        for y in range(MAZE_ROWS):
            for x in range(MAZE_COLS):
                rect = pygame.Rect(MAZE_OFFSET_X + x*CELL_SIZE, MAZE_OFFSET_Y + y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                ch = self.maze_grid[y][x]
                if ch == '#':
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_PATH, rect)
                if ch == '.':
                    dot_rect = pygame.Rect(MAZE_OFFSET_X + x*CELL_SIZE + CELL_SIZE//2 - 2, MAZE_OFFSET_Y + y*CELL_SIZE + CELL_SIZE//2 - 2, 4, 4)
                    pygame.draw.ellipse(self.screen, COLOR_DOT, dot_rect)
                elif ch == 'o':
                    dot_rect = pygame.Rect(MAZE_OFFSET_X + x*CELL_SIZE + CELL_SIZE//2 - 3, MAZE_OFFSET_Y + y*CELL_SIZE + CELL_SIZE//2 - 3, 6, 6)
                    pygame.draw.ellipse(self.screen, COLOR_DOT, dot_rect)
                elif ch == 'O':
                    dot_rect = pygame.Rect(MAZE_OFFSET_X + x*CELL_SIZE + CELL_SIZE//2 - 5, MAZE_OFFSET_Y + y*CELL_SIZE + CELL_SIZE//2 - 5, 10, 10)
                    pygame.draw.ellipse(self.screen, COLOR_POWER, dot_rect)
        
        # 绘制玩家
        player_rect = pygame.Rect(MAZE_OFFSET_X + self.player.x - CELL_SIZE//2, MAZE_OFFSET_Y + self.player.y - CELL_SIZE//2, CELL_SIZE, CELL_SIZE)
        pygame.draw.circle(self.screen, COLOR_PLAYER, (int(MAZE_OFFSET_X + self.player.x), int(MAZE_OFFSET_Y + self.player.y)), CELL_SIZE//2)
        
        # 绘制幽灵
        for ghost in self.ghosts:
            ghost_color = COLOR_GHOST_VULNERABLE if ghost.vulnerable else GHOST_COLORS[ghost.color_idx]
            if ghost.dead:
                ghost_color = (100, 100, 100)
            pygame.draw.circle(self.screen, ghost_color, (int(MAZE_OFFSET_X + ghost.x), int(MAZE_OFFSET_Y + ghost.y)), CELL_SIZE//2)
        
        # HUD
        hud_x = MAZE_OFFSET_X + MAZE_WIDTH + 20
        hud_y = MAZE_OFFSET_Y
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_HUD)
        lives_text = self.font.render(f"Lives: {self.lives}", True, COLOR_HUD)
        dots_text = self.font.render(f"Dots Left: {self.dots_left}", True, COLOR_HUD)
        power_text = self.font.render(f"Power: {self.power_timer//FPS if self.power_active else 0}s", True, COLOR_HUD)
        self.screen.blit(score_text, (hud_x, hud_y))
        self.screen.blit(lives_text, (hud_x, hud_y + 30))
        self.screen.blit(dots_text, (hud_x, hud_y + 60))
        self.screen.blit(power_text, (hud_x, hud_y + 90))
        
        # 游戏结束/胜利信息
        if self.game_over:
            game_over_text = self.big_font.render("GAME OVER", True, COLOR_LOSE)
            score_text = self.font.render(f"Final Score: {self.score}", True, COLOR_HUD)
            restart_text = self.font.render("Press R to Restart", True, COLOR_HUD)
            self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(score_text, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 + 10))
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - 90, SCREEN_HEIGHT//2 + 50))
        elif self.game_win:
            win_text = self.big_font.render("YOU WIN!", True, COLOR_WIN)
            score_text = self.font.render(f"Final Score: {self.score}", True, COLOR_HUD)
            restart_text = self.font.render("Press R to Restart", True, COLOR_HUD)
            self.screen.blit(win_text, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(score_text, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 + 10))
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - 90, SCREEN_HEIGHT//2 + 50))
        
        pygame.display.flip()
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()