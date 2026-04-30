import pygame
import random

# 固定常量
SEED = 42
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRID_SIZE = 24
GRID_WIDTH = 10
GRID_HEIGHT = 20
BOARD_WIDTH = GRID_WIDTH * GRID_SIZE  # 240
BOARD_HEIGHT = GRID_HEIGHT * GRID_SIZE  # 480
BOARD_X = (SCREEN_WIDTH - BOARD_WIDTH) // 2 - 100  # 居中偏左
BOARD_Y = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2
BACKGROUND_COLOR = (20, 20, 40)
GRID_COLOR = (40, 40, 60)
BOARD_COLOR = (10, 10, 30)
HUD_COLOR = (70, 70, 90)
TEXT_COLOR = (220, 220, 255)
GAME_OVER_COLOR = (200, 50, 50)

# 方块定义 (形状、颜色)
SHAPES = {
    'I': {'shape': [[1, 1, 1, 1]],
          'color': (0, 255, 255)},

    'O': {'shape': [[1, 1],
                    [1, 1]],
          'color': (255, 255, 0)},

    'T': {'shape': [[0, 1, 0],
                    [1, 1, 1]],
          'color': (255, 0, 255)},

    'S': {'shape': [[0, 1, 1],
                    [1, 1, 0]],
          'color': (0, 255, 0)},

    'Z': {'shape': [[1, 1, 0],
                    [0, 1, 1]],
          'color': (255, 0, 0)},

    'J': {'shape': [[1, 0, 0],
                    [1, 1, 1]],
          'color': (0, 0, 255)},

    'L': {'shape': [[0, 0, 1],
                    [1, 1, 1]],
          'color': (255, 165, 0)}
}

# 计分规则
SCORE_TABLE = {1: 100, 2: 300, 3: 500, 4: 800}
DROP_INTERVAL = 500  # ms

class Tetris:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Medium")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 32)
        self.big_font = pygame.font.SysFont(None, 48)
        self.reset_game()

    def reset_game(self):
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.drop_time = 0
        self.spawn_new_piece()
        random.seed(SEED)

    def spawn_new_piece(self):
        shape_names = list(SHAPES.keys())
        shape_name = random.choice(shape_names)
        shape_data = SHAPES[shape_name]
        self.current_piece = {
            'shape': shape_data['shape'],
            'color': shape_data['color'],
            'x': GRID_WIDTH // 2 - len(shape_data['shape'][0]) // 2,
            'y': 0
        }
        # 检查游戏结束
        if self.check_collision(self.current_piece['x'], self.current_piece['y'], self.current_piece['shape']):
            self.game_over = True

    def check_collision(self, x, y, shape):
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    new_x = x + j
                    new_y = y + i
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return True
                    if new_y >= 0 and self.board[new_y][new_x]:
                        return True
        return False

    def rotate_piece(self):
        shape = self.current_piece['shape']
        # 转置然后行反转 = 顺时针旋转90度
        rotated = [list(row) for row in zip(*shape[::-1])]
        if not self.check_collision(self.current_piece['x'], self.current_piece['y'], rotated):
            self.current_piece['shape'] = rotated

    def move_piece(self, dx, dy):
        if not self.game_over:
            new_x = self.current_piece['x'] + dx
            new_y = self.current_piece['y'] + dy
            if not self.check_collision(new_x, new_y, self.current_piece['shape']):
                self.current_piece['x'] = new_x
                self.current_piece['y'] = new_y
                return True
        return False

    def hard_drop(self):
        while self.move_piece(0, 1):
            pass
        self.lock_piece()

    def lock_piece(self):
        shape = self.current_piece['shape']
        color = self.current_piece['color']
        x, y = self.current_piece['x'], self.current_piece['y']

        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    board_y = y + i
                    board_x = x + j
                    if 0 <= board_y < GRID_HEIGHT and 0 <= board_x < GRID_WIDTH:
                        self.board[board_y][board_x] = color

        self.clear_lines()
        self.spawn_new_piece()

    def clear_lines(self):
        lines_to_clear = []
        for i in range(GRID_HEIGHT):
            if all(self.board[i]):
                lines_to_clear.append(i)

        if lines_to_clear:
            # 消除行
            for line in lines_to_clear:
                del self.board[line]
                self.board.insert(0, [0 for _ in range(GRID_WIDTH)])

            # 计分
            cleared = len(lines_to_clear)
            self.score += SCORE_TABLE.get(cleared, 0)
            self.lines_cleared += cleared

    def draw_board(self):
        # 绘制棋盘背景
        pygame.draw.rect(self.screen, BOARD_COLOR, (BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT))

        # 绘制网格线
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, GRID_COLOR,
                             (BOARD_X + x * GRID_SIZE, BOARD_Y),
                             (BOARD_X + x * GRID_SIZE, BOARD_Y + BOARD_HEIGHT), 1)
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, GRID_COLOR,
                             (BOARD_X, BOARD_Y + y * GRID_SIZE),
                             (BOARD_X + BOARD_WIDTH, BOARD_Y + y * GRID_SIZE), 1)

        # 绘制已锁定方块
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.board[y][x]:
                    rect = (BOARD_X + x * GRID_SIZE + 1,
                            BOARD_Y + y * GRID_SIZE + 1,
                            GRID_SIZE - 1, GRID_SIZE - 1)
                    pygame.draw.rect(self.screen, self.board[y][x], rect)

        # 绘制当前下落方块
        shape = self.current_piece['shape']
        color = self.current_piece['color']
        px, py = self.current_piece['x'], self.current_piece['y']
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    rect = (BOARD_X + (px + j) * GRID_SIZE + 1,
                            BOARD_Y + (py + i) * GRID_SIZE + 1,
                            GRID_SIZE - 1, GRID_SIZE - 1)
                    pygame.draw.rect(self.screen, color, rect)

    def draw_hud(self):
        hud_x = BOARD_X + BOARD_WIDTH + 30
        hud_width = 200
        pygame.draw.rect(self.screen, HUD_COLOR, (hud_x, BOARD_Y, hud_width, 200), border_radius=10)
        # 分数
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, TEXT_COLOR)
        self.screen.blit(score_text, (hud_x + 20, BOARD_Y + 30))
        self.screen.blit(lines_text, (hud_x + 20, BOARD_Y + 70))

        # 操作说明
        controls = [
            "Controls:",
            "Left/Right - Move",
            "Up - Rotate",
            "Down - Soft drop",
            "Space - Hard drop",
            "R - Restart",
            "ESC - Quit"
        ]
        for idx, line in enumerate(controls):
            text = self.font.render(line, True, TEXT_COLOR)
            self.screen.blit(text, (hud_x + 20, BOARD_Y + 130 + idx * 30))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.big_font.render("GAME OVER", True, GAME_OVER_COLOR)
        score_text = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
        restart_text = self.font.render("Press R to Restart", True, TEXT_COLOR)

        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

    def run(self):
        while True:
            current_time = pygame.time.get_ticks()
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                    if event.key == pygame.K_r:
                        self.reset_game()
                    if not self.game_over:
                        if event.key == pygame.K_LEFT:
                            self.move_piece(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move_piece(1, 0)
                        elif event.key == pygame.K_UP:
                            self.rotate_piece()
                        elif event.key == pygame.K_DOWN:
                            self.move_piece(0, 1)
                        elif event.key == pygame.K_SPACE:
                            self.hard_drop()

            # 自动下落
            if not self.game_over and current_time - self.drop_time > DROP_INTERVAL:
                if not self.move_piece(0, 1):
                    self.lock_piece()
                self.drop_time = current_time

            # 绘制
            self.screen.fill(BACKGROUND_COLOR)
            self.draw_board()
            self.draw_hud()
            if self.game_over:
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Tetris()
    game.run()