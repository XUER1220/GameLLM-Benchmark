import pygame
import random
import sys

# 常量定义
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_COLS = 10
GRID_ROWS = 20
BLOCK_SIZE = 24
GAME_WIDTH = GRID_COLS * BLOCK_SIZE
GAME_HEIGHT = GRID_ROWS * BLOCK_SIZE
FPS = 60
AUTO_DROP_INTERVAL = 500  # ms

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)

# 方块颜色
COLORS = {
    'I': (0, 255, 255),   # Cyan
    'O': (255, 255, 0),   # Yellow
    'T': (128, 0, 128),   # Purple
    'S': (0, 255, 0),     # Green
    'Z': (255, 0, 0),     # Red
    'J': (0, 0, 255),     # Blue
    'L': (255, 165, 0)    # Orange
}

# 形状定义
SHAPES = {
    'I': [
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ],
    'O': [
        [1, 1],
        [1, 1]
    ],
    'T': [
        [0, 1, 0],
        [1, 1, 1],
        [0, 0, 0]
    ],
    'S': [
        [0, 1, 1],
        [1, 1, 0],
        [0, 0, 0]
    ],
    'Z': [
        [1, 1, 0],
        [0, 1, 1],
        [0, 0, 0]
    ],
    'J': [
        [1, 0, 0],
        [1, 1, 1],
        [0, 0, 0]
    ],
    'L': [
        [0, 0, 1],
        [1, 1, 1],
        [0, 0, 0]
    ]
}

# 确定游戏区域的左上角坐标
GAME_X = (WINDOW_WIDTH - GAME_WIDTH) // 2 - 20
GAME_Y = (WINDOW_HEIGHT - GAME_HEIGHT) // 2

# 消除行得分映射
SCORE_MAP = {
    1: 100,
    2: 300,
    3: 500,
    4: 800
}


def create_board():
    return [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]


def get_new_piece(pieces_list):
    shape_key = random.choice(list(SHAPES.keys()))
    shape = SHAPES[shape_key]
    return {
        'shape': shape,
        'color': COLORS[shape_key],
        'x': GRID_COLS // 2 - len(shape[0]) // 2,
        'y': 0,
        'type': shape_key
    }


def valid_move(board, piece, offset_x=0, offset_y=0):
    shape = piece['shape']
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                new_x = piece['x'] + x + offset_x
                new_y = piece['y'] + y + offset_y
                if new_x < 0 or new_x >= GRID_COLS or new_y >= GRID_ROWS:
                    return False
                if new_y >= 0 and board[new_y][new_x]:
                    return False
    return True


def rotate_piece(piece):
    shape = piece['shape']
    rotated = [list(row) for row in zip(*shape[::-1])]
    return {
        'shape': rotated,
        'color': piece['color'],
        'x': piece['x'],
        'y': piece['y'],
        'type': piece['type']
    }


def merge_piece(board, piece):
    shape = piece['shape']
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                board[piece['y'] + y][piece['x'] + x] = piece['color']


def clear_lines(board):
    lines_cleared = 0
    y = GRID_ROWS - 1
    while y >= 0:
        if all(board[y]):
            del board[y]
            board.insert(0, [0 for _ in range(GRID_COLS)])
            lines_cleared += 1
        else:
            y -= 1
    return lines_cleared


class TetrisGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.big_font = pygame.font.SysFont('Arial', 48)

    def reset(self):
        random.seed(42)
        self.board = create_board()
        self.pieces_queue = [get_new_piece(list(SHAPES.keys())) for _ in range(100)]
        self.current_piece = self.pieces_queue.pop(0)
        self.next_piece = self.pieces_queue.pop(0)
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.last_drop_time = 0

    def run(self):
        self.reset()
        while True:
            self.clock.tick(FPS)
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif not self.game_over:
                        if event.key == pygame.K_LEFT:
                            if valid_move(self.board, self.current_piece, offset_x=-1):
                                self.current_piece['x'] -= 1
                        elif event.key == pygame.K_RIGHT:
                            if valid_move(self.board, self.current_piece, offset_x=1):
                                self.current_piece['x'] += 1
                        elif event.key == pygame.K_UP:
                            rotated = rotate_piece(self.current_piece)
                            if valid_move(self.board, rotated):
                                self.current_piece = rotated
                        elif event.key == pygame.K_DOWN:
                            if valid_move(self.board, self.current_piece, offset_y=1):
                                self.current_piece['y'] += 1
                        elif event.key == pygame.K_SPACE:
                            # 硬降
                            while valid_move(self.board, self.current_piece, offset_y=1):
                                self.current_piece['y'] += 1

            # 自动下落
            current_time = pygame.time.get_ticks()
            if current_time - self.last_drop_time >= AUTO_DROP_INTERVAL and not self.game_over:
                if valid_move(self.board, self.current_piece, offset_y=1):
                    self.current_piece['y'] += 1
                else:
                    merge_piece(self.board, self.current_piece)
                    lines = clear_lines(self.board)
                    if lines > 0:
                        self.score += SCORE_MAP[lines]
                        self.lines_cleared += lines
                    # 生成新方块
                    if not self.pieces_queue:
                        self.pieces_queue = [get_new_piece(list(SHAPES.keys())) for _ in range(100)]
                    self.current_piece = self.pieces_queue.pop(0)
                    # 检查游戏结束
                    if not valid_move(self.board, self.current_piece):
                        self.game_over = True
                self.last_drop_time = current_time

            # 更新绘制
            self.draw()

    def draw(self):
        self.screen.fill(BLACK)

        # 绘制棋盘背景
        pygame.draw.rect(self.screen, GRAY, (GAME_X - 10, GAME_Y - 10, GAME_WIDTH + 20, GAME_HEIGHT + 20), 2)

        # 绘制网格
        for x in range(GRID_COLS + 1):
            pygame.draw.line(self.screen, LIGHT_GRAY, (GAME_X + x * BLOCK_SIZE, GAME_Y),
                             (GAME_X + x * BLOCK_SIZE, GAME_Y + GAME_HEIGHT))
        for y in range(GRID_ROWS + 1):
            pygame.draw.line(self.screen, LIGHT_GRAY, (GAME_X, GAME_Y + y * BLOCK_SIZE),
                             (GAME_X + GAME_WIDTH, GAME_Y + y * BLOCK_SIZE))

        # 绘制已有方块
        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                if self.board[y][x]:
                    self.draw_block(GAME_X + x * BLOCK_SIZE, GAME_Y + y * BLOCK_SIZE, self.board[y][x])

        # 绘制当前方块
        if not self.game_over:
            for y, row in enumerate(self.current_piece['shape']):
                for x, cell in enumerate(row):
                    if cell:
                        px = GAME_X + (self.current_piece['x'] + x) * BLOCK_SIZE
                        py = GAME_Y + (self.current_piece['y'] + y) * BLOCK_SIZE
                        self.draw_block(px, py, self.current_piece['color'])

        # HUD
        hud_x = GAME_X + GAME_WIDTH + 30
        self.draw_text("Score:", hud_x, GAME_Y, WHITE)
        self.draw_text(str(self.score), hud_x, GAME_Y + 30, WHITE)

        self.draw_text("Lines:", hud_x, GAME_Y + 100, WHITE)
        self.draw_text(str(self.lines_cleared), hud_x, GAME_Y + 130, WHITE)

        # Game Over 显示
        if self.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            self.draw_text("GAME OVER", GAME_X + GAME_WIDTH // 2 - 120, GAME_Y + 200, WHITE, font_size=60)
            self.draw_text(f"Final Score: {self.score}", GAME_X + GAME_WIDTH // 2 - 140, GAME_Y + 280, WHITE, font_size=36)
            self.draw_text("Press R to Restart", GAME_X + GAME_WIDTH // 2 - 140, GAME_Y + 350, WHITE, font_size=36)

        pygame.display.flip()

    def draw_block(self, x, y, color):
        pygame.draw.rect(self.screen, color, (x + 1, y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
        # 添加边框效果
        inner_rect = pygame.Rect(x + 3, y + 3, BLOCK_SIZE - 6, BLOCK_SIZE - 6)
        pygame.draw.rect(self.screen, tuple(min(c + 50, 255) for c in color), inner_rect, 1)

    def draw_text(self, text, x, y, color, font_size=24):
        font = pygame.font.SysFont('Arial', font_size)
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))


if __name__ == "__main__":
    game = TetrisGame()
    game.run()