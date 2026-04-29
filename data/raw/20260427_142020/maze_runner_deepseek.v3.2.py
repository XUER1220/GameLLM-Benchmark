import pygame
import random
import sys

# 固定参数
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 32
MAZE_COLS = 21  # 列数
MAZE_ROWS = 15  # 行数
MAZE_WIDTH = GRID_SIZE * MAZE_COLS
MAZE_HEIGHT = GRID_SIZE * MAZE_ROWS
MAZE_OFFSET_X = (SCREEN_WIDTH - MAZE_WIDTH) // 2
MAZE_OFFSET_Y = (SCREEN_HEIGHT - MAZE_HEIGHT) // 2
FPS = 60
RANDOM_SEED = 42

# 颜色定义
BACKGROUND_COLOR = (20, 20, 30)
MAZE_BG_COLOR = (30, 30, 40)
WALL_COLOR = (70, 90, 120)
PATH_COLOR = (230, 230, 240)
PLAYER_COLOR = (50, 200, 100)
EXIT_COLOR = (220, 80, 60)
TEXT_COLOR = (255, 255, 255)
HUD_BG_COLOR = (40, 40, 50, 180)
BUTTON_COLOR = (80, 120, 200)
BUTTON_HOVER_COLOR = (100, 150, 230)

# 迷宫生成常量
CELL_WALL = 0
CELL_PATH = 1
CELL_VISITED = 2

# 固定随机种子
random.seed(RANDOM_SEED)

# 方向向量 (dx, dy) 和对应的墙壁索引
DIRECTIONS = [
    (0, -1),  # 上
    (1, 0),   # 右
    (0, 1),   # 下
    (-1, 0)   # 左
]

class MazeGenerator:
    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.maze = [[CELL_WALL] * (cols * 2 + 1) for _ in range(rows * 2 + 1)]
        self.generate()
    
    def generate(self):
        # 初始化所有内部单元格为未访问的墙
        for y in range(self.rows * 2 + 1):
            for x in range(self.cols * 2 + 1):
                self.maze[y][x] = CELL_WALL
        
        # 从起点开始
        start_x, start_y = 1, 1
        self.maze[start_y][start_x] = CELL_PATH
        stack = [(start_x, start_y)]
        
        while stack:
            x, y = stack[-1]
            # 查找未访问的邻居
            neighbors = []
            for dx, dy in DIRECTIONS:
                nx, ny = x + dx * 2, y + dy * 2
                if 0 < nx < self.cols * 2 and 0 < ny < self.rows * 2:
                    if self.maze[ny][nx] == CELL_WALL:
                        neighbors.append((dx, dy, nx, ny))
            
            if neighbors:
                # 随机选择一个邻居
                dx, dy, nx, ny = random.choice(neighbors)
                # 打通墙壁
                wx, wy = x + dx, y + dy
                self.maze[wy][wx] = CELL_PATH
                self.maze[ny][nx] = CELL_PATH
                stack.append((nx, ny))
            else:
                stack.pop()
        
        # 确保出口可通行（右下角）
        exit_x, exit_y = self.cols * 2 - 1, self.rows * 2 - 1
        if self.maze[exit_y][exit_x] == CELL_WALL:
            # 尝试打通右侧或下方的墙
            if exit_x > 1 and self.maze[exit_y][exit_x - 1] == CELL_PATH:
                self.maze[exit_y][exit_x] = CELL_PATH
            elif exit_y > 1 and self.maze[exit_y - 1][exit_x] == CELL_PATH:
                self.maze[exit_y][exit_x] = CELL_PATH
            else:
                # 强制打通
                self.maze[exit_y][exit_x - 1] = CELL_PATH
                self.maze[exit_y][exit_x] = CELL_PATH

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Maze Runner Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.small_font = pygame.font.SysFont("Arial", 20)
        self.reset_game()
    
    def reset_game(self):
        self.maze_gen = MazeGenerator(MAZE_COLS, MAZE_ROWS)
        # 玩家起始位置（左上角路径）
        self.player_x = 1
        self.player_y = 1
        self.exit_x = MAZE_COLS * 2 - 1
        self.exit_y = MAZE_ROWS * 2 - 1
        self.game_won = False
        self.game_started = False
        self.start_time = None
        self.end_time = None
    
    def can_move(self, dx, dy):
        # 检查目标位置是否是通路
        nx = self.player_x + dx
        ny = self.player_y + dy
        if 0 <= nx < MAZE_COLS * 2 + 1 and 0 <= ny < MAZE_ROWS * 2 + 1:
            return self.maze_gen.maze[ny][nx] == CELL_PATH
        return False
    
    def check_win(self):
        return self.player_x == self.exit_x and self.player_y == self.exit_y
    
    def get_elapsed_time(self):
        if self.start_time is None:
            return 0
        if self.game_won and self.end_time:
            return (self.end_time - self.start_time) / 1000.0
        return (pygame.time.get_ticks() - self.start_time) / 1000.0
    
    def draw_maze(self):
        # 绘制迷宫背景
        pygame.draw.rect(self.screen, MAZE_BG_COLOR, 
                         (MAZE_OFFSET_X, MAZE_OFFSET_Y, MAZE_WIDTH, MAZE_HEIGHT))
        
        # 绘制墙壁和路径
        for y in range(MAZE_ROWS * 2 + 1):
            for x in range(MAZE_COLS * 2 + 1):
                rect_x = MAZE_OFFSET_X + x * GRID_SIZE // 2
                rect_y = MAZE_OFFSET_Y + y * GRID_SIZE // 2
                
                if self.maze_gen.maze[y][x] == CELL_PATH:
                    color = PATH_COLOR
                    pygame.draw.rect(self.screen, color, 
                                     (rect_x, rect_y, GRID_SIZE // 2, GRID_SIZE // 2))
                else:
                    color = WALL_COLOR
                    pygame.draw.rect(self.screen, color, 
                                     (rect_x, rect_y, GRID_SIZE // 2, GRID_SIZE // 2))
        
        # 绘制出口（右下角）
        exit_rect = pygame.Rect(
            MAZE_OFFSET_X + self.exit_x * GRID_SIZE // 2 + 2,
            MAZE_OFFSET_Y + self.exit_y * GRID_SIZE // 2 + 2,
            GRID_SIZE // 2 - 4,
            GRID_SIZE // 2 - 4
        )
        pygame.draw.ellipse(self.screen, EXIT_COLOR, exit_rect)
        
        # 绘制玩家
        player_rect = pygame.Rect(
            MAZE_OFFSET_X + self.player_x * GRID_SIZE // 2 + 4,
            MAZE_OFFSET_Y + self.player_y * GRID_SIZE // 2 + 4,
            GRID_SIZE // 2 - 8,
            GRID_SIZE // 2 - 8
        )
        pygame.draw.ellipse(self.screen, PLAYER_COLOR, player_rect)
        
        # 绘制迷宫边框
        pygame.draw.rect(self.screen, WALL_COLOR, 
                         (MAZE_OFFSET_X, MAZE_OFFSET_Y, MAZE_WIDTH, MAZE_HEIGHT), 2)
    
    def draw_hud(self):
        # 绘制半透明HUD背景
        hud_rect = pygame.Rect(10, 10, SCREEN_WIDTH - 20, 50)
        pygame.draw.rect(self.screen, HUD_BG_COLOR, hud_rect, border_radius=5)
        pygame.draw.rect(self.screen, (100, 100, 120), hud_rect, 2, border_radius=5)
        
        # 显示时间
        elapsed = self.get_elapsed_time()
        time_text = f"Time: {elapsed:.2f}s"
        time_surface = self.font.render(time_text, True, TEXT_COLOR)
        self.screen.blit(time_surface, (20, 20))
        
        # 显示操作提示
        controls_text = "Arrow Keys: Move  |  R: Restart  |  ESC: Exit"
        controls_surface = self.small_font.render(controls_text, True, TEXT_COLOR)
        self.screen.blit(controls_surface, (SCREEN_WIDTH // 2 - controls_surface.get_width() // 2, 25))
        
        # 如果游戏胜利
        if self.game_won:
            # 胜利消息背景
            win_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - 200,
                SCREEN_HEIGHT // 2 - 100,
                400,
                150
            )
            pygame.draw.rect(self.screen, HUD_BG_COLOR, win_rect, border_radius=10)
            pygame.draw.rect(self.screen, (100, 180, 100), win_rect, 3, border_radius=10)
            
            # 胜利文本
            win_text = self.font.render("You Win!", True, (100, 255, 100))
            time_text = self.font.render(f"Total Time: {elapsed:.2f} seconds", True, TEXT_COLOR)
            restart_text = self.small_font.render("Press R to Restart", True, TEXT_COLOR)
            
            self.screen.blit(win_text, 
                            (SCREEN_WIDTH // 2 - win_text.get_width() // 2, 
                             SCREEN_HEIGHT // 2 - 70))
            self.screen.blit(time_text, 
                            (SCREEN_WIDTH // 2 - time_text.get_width() // 2, 
                             SCREEN_HEIGHT // 2 - 30))
            self.screen.blit(restart_text, 
                            (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                             SCREEN_HEIGHT // 2 + 10))
    
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
                    return
                
                # 玩家移动
                if not self.game_won:
                    dx, dy = 0, 0
                    if event.key == pygame.K_LEFT:
                        dx = -2
                    elif event.key == pygame.K_RIGHT:
                        dx = 2
                    elif event.key == pygame.K_UP:
                        dy = -2
                    elif event.key == pygame.K_DOWN:
                        dy = 2
                    
                    if dx != 0 or dy != 0:
                        if not self.game_started:
                            self.game_started = True
                            self.start_time = pygame.time.get_ticks()
                        
                        if self.can_move(dx, dy):
                            self.player_x += dx
                            self.player_y += dy
                            
                            if self.check_win() and not self.game_won:
                                self.game_won = True
                                self.end_time = pygame.time.get_ticks()
    
    def run(self):
        while True:
            self.handle_events()
            
            # 绘制背景
            self.screen.fill(BACKGROUND_COLOR)
            
            # 绘制迷宫和游戏元素
            self.draw_maze()
            self.draw_hud()
            
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()