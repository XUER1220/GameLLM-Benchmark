import pygame
import random
import time

# 固定参数
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
MAZE_COLS, MAZE_ROWS = 21, 15
CELL_SIZE = 32
MAZE_WIDTH, MAZE_HEIGHT = MAZE_COLS * CELL_SIZE, MAZE_ROWS * CELL_SIZE
OFFSET_X = (SCREEN_WIDTH - MAZE_WIDTH) // 2
OFFSET_Y = (SCREEN_HEIGHT - MAZE_HEIGHT) // 2

# 颜色配置
COLOR_WALL = (40, 40, 40)
COLOR_PATH = (240, 240, 240)
COLOR_PLAYER = (0, 100, 255)
COLOR_EXIT = (0, 200, 100)
COLOR_TEXT = (50, 50, 50)
COLOR_WIN_TEXT = (0, 100, 0)

class MazeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Maze Runner Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 32)
        self.big_font = pygame.font.SysFont(None, 64)
        
        # 初始化迷宫
        self.reset_game()
    
    def reset_game(self):
        random.seed(42)
        self.maze = self.generate_maze(MAZE_ROWS, MAZE_COLS)
        self.player_pos = (0, 0)
        self.exit_pos = (MAZE_ROWS - 1, MAZE_COLS - 1)
        self.start_time = None
        self.game_started = False
        self.game_over = False
        self.win_time = None
    
    def generate_maze(self, rows, cols):
        # 使用 DFS 回溯法生成迷宫（确保可通行）
        # 0: 墙, 1: 通路
        maze = [[0] * cols for _ in range(rows)]
        
        # 辅助函数检查坐标有效性
        def is_valid(r, c):
            return 0 <= r < rows and 0 <= c < cols and maze[r][c] == 0
        
        # DFS 生成迷宫（从 (0,0) 开始）
        stack = [(0, 0)]
        maze[0][0] = 1
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # 右、下、左、上
        
        while stack:
            r, c = stack[-1]
            neighbors = []
            
            # 检查可选的下一步（两次步长以跳过墙）
            for dr, dc in directions:
                if is_valid(r + 2*dr, c + 2*dc):
                    neighbors.append((dr, dc))
            
            if neighbors:
                dr, dc = random.choice(neighbors)
                # 移动到下一个通路并打通中间的墙
                maze[r + dr][c + dc] = 1
                maze[r + 2*dr][c + 2*dc] = 1
                stack.append((r + 2*dr, c + 2*dc))
            else:
                stack.pop()
        
        # 确保终点为通路（DFS生成后应该为1，但为了安全）
        maze[rows-1][cols-1] = 1
        return maze
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r and (self.game_over or self.start_time is not None):
                    self.reset_game()
                elif not self.game_over:
                    self.move_player(event.key)
        return True
    
    def move_player(self, key):
        if not self.game_started:
            self.game_started = True
            self.start_time = time.time()
        
        if self.game_over:
            return
        
        row, col = self.player_pos
        new_row, new_col = row, col
        
        if key == pygame.K_UP and row > 0:
            if self.maze[row - 1][col] == 1:
                new_row = row - 1
        elif key == pygame.K_DOWN and row < MAZE_ROWS - 1:
            if self.maze[row + 1][col] == 1:
                new_row = row + 1
        elif key == pygame.K_LEFT and col > 0:
            if self.maze[row][col - 1] == 1:
                new_col = col - 1
        elif key == pygame.K_RIGHT and col < MAZE_COLS - 1:
            if self.maze[row][col + 1] == 1:
                new_col = col + 1
        
        if (new_row, new_col) != (row, col):
            self.player_pos = (new_row, new_col)
            
            # 检查是否到达终点
            if self.player_pos == self.exit_pos:
                self.game_over = True
                self.win_time = time.time() - self.start_time
    
    def draw(self):
        self.screen.fill((255, 255, 255))
        
        # 绘制迷宫
        for row in range(MAZE_ROWS):
            for col in range(MAZE_COLS):
                rect = pygame.Rect(
                    OFFSET_X + col * CELL_SIZE,
                    OFFSET_Y + row * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                if self.maze[row][col] == 1:
                    pygame.draw.rect(self.screen, COLOR_PATH, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
        
        # 绘制出口
        exit_rect = pygame.Rect(
            OFFSET_X + self.exit_pos[1] * CELL_SIZE,
            OFFSET_Y + self.exit_pos[0] * CELL_SIZE,
            CELL_SIZE, CELL_SIZE
        )
        pygame.draw.rect(self.screen, COLOR_EXIT, exit_rect)
        
        # 绘制玩家
        player_rect = pygame.Rect(
            OFFSET_X + self.player_pos[1] * CELL_SIZE + 6,
            OFFSET_Y + self.player_pos[0] * CELL_SIZE + 6,
            CELL_SIZE - 12, CELL_SIZE - 12
        )
        pygame.draw.rect(self.screen, COLOR_PLAYER, player_rect, border_radius=4)
        
        # HUD: 绘制时间
        if self.start_time is not None and not self.game_over:
            elapsed = time.time() - self.start_time
            time_text = self.font.render(f"Time: {elapsed:.1f}s", True, COLOR_TEXT)
        elif self.win_time is not None:
            time_text = self.font.render(f"Time: {self.win_time:.2f}s", True, COLOR_TEXT)
        else:
            time_text = self.font.render("Time: 0.0s", True, COLOR_TEXT)
        self.screen.blit(time_text, (10, 10))
        
        # 胜利界面
        if self.game_over:
            win_time_str = f"{self.win_time:.2f}" if self.win_time is not None else "N/A"
            
            # 半透明背景
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 180))
            self.screen.blit(overlay, (0, 0))
            
            # 绘制胜利文本
            win_text = self.big_font.render("You Win!", True, COLOR_WIN_TEXT)
            win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(win_text, win_rect)
            
            time_result = self.font.render(f"Time: {win_time_str}s", True, COLOR_WIN_TEXT)
            time_rect = time_result.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(time_result, time_rect)
            
            restart_text = self.font.render("Press R to Restart", True, COLOR_TEXT)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            running = self.handle_events()
            self.draw()
        pygame.quit()

if __name__ == "__main__":
    game = MazeGame()
    game.run()