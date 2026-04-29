import pygame
import random
import sys
from collections import deque

# 全局参数
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
MAZE_COLS, MAZE_ROWS = 21, 15
CELL_SIZE = 32
MAZE_WIDTH = MAZE_COLS * CELL_SIZE
MAZE_HEIGHT = MAZE_ROWS * CELL_SIZE
FPS = 60
SEED = 42

# 颜色定义（RGB）
BACKGROUND = (15, 15, 30)
MAZE_BG = (25, 25, 35)
WALL_COLOR = (90, 90, 150)
PATH_COLOR = (35, 35, 45)
PLAYER_COLOR = (70, 220, 100)
EXIT_COLOR = (220, 100, 100)
TEXT_COLOR = (240, 240, 255)
HUD_BG = (30, 30, 45, 200)

class MazeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Maze Runner Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.big_font = pygame.font.SysFont(None, 48)
        self.reset_game()

    def reset_game(self):
        random.seed(SEED)
        self.maze = self.generate_maze()
        self.player_x, self.player_y = 1, 1
        self.exit_x, self.exit_y = MAZE_COLS - 2, MAZE_ROWS - 2
        self.game_won = False
        self.start_time = None
        self.current_time = 0
        self.running = True

    def generate_maze(self):
        maze = [[1 for _ in range(MAZE_COLS)] for __ in range(MAZE_ROWS)]
        stack = [(1, 1)]
        maze[1][1] = 0
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]

        while stack:
            x, y = stack[-1]
            random.shuffle(directions)
            found = False
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 < nx < MAZE_COLS - 1 and 0 < ny < MAZE_ROWS - 1 and maze[ny][nx] == 1:
                    wall_x, wall_y = x + dx // 2, y + dy // 2
                    maze[ny][nx] = 0
                    maze[wall_y][wall_x] = 0
                    stack.append((nx, ny))
                    found = True
                    break
            if not found:
                stack.pop()
        return maze

    def draw_maze(self):
        margin_x = (SCREEN_WIDTH - MAZE_WIDTH) // 2
        margin_y = (SCREEN_HEIGHT - MAZE_HEIGHT) // 2
        pygame.draw.rect(self.screen, MAZE_BG, (margin_x, margin_y, MAZE_WIDTH, MAZE_HEIGHT))

        for y in range(MAZE_ROWS):
            for x in range(MAZE_COLS):
                rect = pygame.Rect(
                    margin_x + x * CELL_SIZE,
                    margin_y + y * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                if self.maze[y][x] == 1:
                    pygame.draw.rect(self.screen, WALL_COLOR, rect)
                    pygame.draw.rect(self.screen, (60, 60, 100), rect, 1)
                else:
                    pygame.draw.rect(self.screen, PATH_COLOR, rect)
                    pygame.draw.rect(self.screen, (50, 50, 70), rect, 1)

        exit_rect = pygame.Rect(
            margin_x + self.exit_x * CELL_SIZE,
            margin_y + self.exit_y * CELL_SIZE,
            CELL_SIZE, CELL_SIZE
        )
        pygame.draw.rect(self.screen, EXIT_COLOR, exit_rect)
        pygame.draw.rect(self.screen, (255, 150, 150), exit_rect, 3)

        player_rect = pygame.Rect(
            margin_x + self.player_x * CELL_SIZE + 4,
            margin_y + self.player_y * CELL_SIZE + 4,
            CELL_SIZE - 8, CELL_SIZE - 8
        )
        pygame.draw.ellipse(self.screen, PLAYER_COLOR, player_rect)
        pygame.draw.ellipse(self.screen, (150, 255, 150), player_rect, 2)

    def draw_hud(self):
        if not self.game_won:
            if self.start_time is None:
                self.current_time = 0
            else:
                self.current_time = (pygame.time.get_ticks() - self.start_time) / 1000.0
        time_text = f"Time: {self.current_time:.2f}s"
        time_surf = self.font.render(time_text, True, TEXT_COLOR)
        self.screen.blit(time_surf, (20, 20))

        if self.game_won:
            win_surf = self.big_font.render("You Win!", True, (100, 255, 100))
            self.screen.blit(win_surf, (SCREEN_WIDTH // 2 - win_surf.get_width() // 2, 50))
            time_msg_surf = self.font.render(f"Total Time: {self.current_time:.2f}s", True, TEXT_COLOR)
            self.screen.blit(time_msg_surf, (SCREEN_WIDTH // 2 - time_msg_surf.get_width() // 2, 110))
            restart_surf = self.font.render("Press R to Restart", True, (255, 255, 150))
            self.screen.blit(restart_surf, (SCREEN_WIDTH // 2 - restart_surf.get_width() // 2, 150))
        else:
            hint_surf = self.font.render("Use Arrow Keys to move", True, (200, 200, 255))
            self.screen.blit(hint_surf, (SCREEN_WIDTH // 2 - hint_surf.get_width() // 2, 20))

        restart_hint = self.font.render("R: Restart  ESC: Exit", True, (200, 200, 220))
        self.screen.blit(restart_hint, (SCREEN_WIDTH - restart_hint.get_width() - 20, SCREEN_HEIGHT - 40))

    def move_player(self, dx, dy):
        if self.game_won:
            return
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        if 0 <= new_x < MAZE_COLS and 0 <= new_y < MAZE_ROWS:
            if self.maze[new_y][new_x] == 0:
                self.player_x = new_x
                self.player_y = new_y
                if self.start_time is None:
                    self.start_time = pygame.time.get_ticks()
        if self.player_x == self.exit_x and self.player_y == self.exit_y:
            self.game_won = True

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.reset_game()
                elif not self.game_won:
                    if event.key == pygame.K_UP:
                        self.move_player(0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.move_player(0, 1)
                    elif event.key == pygame.K_LEFT:
                        self.move_player(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move_player(1, 0)

    def run(self):
        while self.running:
            self.handle_input()
            self.screen.fill(BACKGROUND)
            self.draw_maze()
            self.draw_hud()
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = MazeGame()
    game.run()