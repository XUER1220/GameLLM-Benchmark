import pygame
import random
import time
import sys

# 固定随机种子
random.seed(42)

# 通用参数
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 迷宫参数
COLS = 21
ROWS = 15
CELL_SIZE = 32
MAZE_WIDTH = COLS * CELL_SIZE
MAZE_HEIGHT = ROWS * CELL_SIZE
MAZE_X = (SCREEN_WIDTH - MAZE_WIDTH) // 2
MAZE_Y = (SCREEN_HEIGHT - MAZE_HEIGHT) // 2

# 颜色定义
COLOR_WALL = (0, 0, 0)
COLOR_PATH = (255, 255, 255)
COLOR_PLAYER = (255, 0, 0)
COLOR_EXIT = (0, 255, 0)
COLOR_TEXT = (0, 0, 0)
COLOR_HUD_BG = (240, 240, 240)

# 方向向量
DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # 上、下、左、右


def generate_maze(cols, rows):
    # 创建迷宫：1 表示墙，0 表示通路
    maze = [[1] * cols for _ in range(rows)]
    # 起始点设为通路
    start_x, start_y = 0, 0
    maze[start_y][start_x] = 0

    stack = [(start_x, start_y)]
    visited = set()
    visited.add((start_x, start_y))

    while stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx * 2, y + dy * 2
            if 0 <= nx < cols and 0 <= ny < rows and (nx, ny) not in visited:
                neighbors.append((nx, ny, dx, dy))

        if neighbors:
            nx, ny, dx, dy = random.choice(neighbors)
            # 打通中间的墙
            maze[y + dy][x + dx] = 0
            maze[ny][nx] = 0
            visited.add((nx, ny))
            stack.append((nx, ny))
        else:
            stack.pop()

    return maze


class MazeRunnerGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Maze Runner Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)

    def reset_game(self):
        self.maze = generate_maze(COLS, ROWS)
        self.player_pos = (0, 0)
        self.exit_pos = (COLS - 1, ROWS - 1)
        self.start_time = None
        self.elapsed_time = 0
        self.game_state = "playing"  # playing, won
        self.first_move_done = False

    def draw_maze(self):
        for y in range(ROWS):
            for x in range(COLS):
                rect = (MAZE_X + x * CELL_SIZE, MAZE_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if self.maze[y][x] == 0:
                    pygame.draw.rect(self.screen, COLOR_PATH, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)

        # 绘制出口
        exit_rect = (
            MAZE_X + self.exit_pos[0] * CELL_SIZE + 4,
            MAZE_Y + self.exit_pos[1] * CELL_SIZE + 4,
            CELL_SIZE - 8,
            CELL_SIZE - 8
        )
        pygame.draw.rect(self.screen, COLOR_EXIT, exit_rect)

    def draw_player(self):
        px, py = self.player_pos
        player_rect = (
            MAZE_X + px * CELL_SIZE + 8,
            MAZE_Y + py * CELL_SIZE + 8,
            CELL_SIZE - 16,
            CELL_SIZE - 16
        )
        pygame.draw.rect(self.screen, COLOR_PLAYER, player_rect)

    def draw_hud(self):
        hud_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 40)
        pygame.draw.rect(self.screen, COLOR_HUD_BG, hud_rect)

        time_text = self.small_font.render(f"Time: {self.elapsed_time:.2f}", True, COLOR_TEXT)
        self.screen.blit(time_text, (10, 10))

        if self.game_state == "won":
            win_text = self.font.render("You Win!", True, COLOR_EXIT)
            self.screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, MAZE_Y + MAZE_HEIGHT + 20))

            time_result_text = self.font.render(f"Time: {self.elapsed_time:.2f} s", True, COLOR_TEXT)
            self.screen.blit(time_result_text, (
                SCREEN_WIDTH // 2 - time_result_text.get_width() // 2,
                MAZE_Y + MAZE_HEIGHT + 60
            ))

            restart_text = self.small_font.render("Press R to Restart", True, COLOR_TEXT)
            self.screen.blit(restart_text, (
                SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                MAZE_Y + MAZE_HEIGHT + 100
            ))

    def move_player(self, dx, dy):
        if self.game_state != "playing":
            return

        current_x, current_y = self.player_pos
        new_x, new_y = current_x + dx, current_y + dy

        # 边界检查与墙检查
        if 0 <= new_x < COLS and 0 <= new_y < ROWS and self.maze[new_y][new_x] == 0:
            self.player_pos = (new_x, new_y)
            if not self.first_move_done:
                self.start_time = time.time()
                self.first_move_done = True

        # 检查是否到达终点
        if self.player_pos == self.exit_pos:
            self.game_state = "won"
            if self.first_move_done:
                self.elapsed_time = time.time() - self.start_time
            else:
                self.elapsed_time = 0.0

    def update_time(self):
        if self.first_move_done and self.game_state == "playing":
            self.elapsed_time = time.time() - self.start_time

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:
                    self.reset_game()
                elif self.game_state == "playing":
                    if event.key == pygame.K_UP:
                        self.move_player(0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.move_player(0, 1)
                    elif event.key == pygame.K_LEFT:
                        self.move_player(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move_player(1, 0)
        return True

    def run(self):
        self.reset_game()
        running = True

        while running:
            self.clock.tick(FPS)
            running = self.handle_events()
            self.update_time()

            self.screen.fill((255, 255, 255))
            self.draw_maze()
            self.draw_player()
            self.draw_hud()

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = MazeRunnerGame()
    game.run()