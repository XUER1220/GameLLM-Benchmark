import pygame
import random
import sys

# 固定参数
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
GRID_COLS = 10
GRID_ROWS = 20
GRID_SIZE = 24
BOARD_TOP = (WINDOW_HEIGHT - GRID_ROWS * GRID_SIZE) // 2 + 40
BOARD_LEFT = (WINDOW_WIDTH - GRID_COLS * GRID_SIZE) // 2 - 180
AUTO_DROP_INTERVAL = 500

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)

# 7种方块颜色
COLORS = {
    'I': (0, 255, 255),  # Cyan
    'O': (255, 255, 0),  # Yellow
    'T': (128, 0, 128),  # Purple
    'S': (0, 255, 0),    # Green
    'Z': (255, 0, 0),    # Red
    'J': (0, 0, 255),    # Blue
    'L': (255, 165, 0)   # Orange
}

# 形状定义（使用偏移坐标对）
SHAPES = {
    'I': [[0, 0], [1, 0], [2, 0], [3, 0]],
    'O': [[1, 0], [0, 0], [1, 1], [0, 1]],
    'T': [[1, 0], [0, 0], [2, 0], [1, 1]],
    'S': [[1, 0], [2, 0], [0, 1], [1, 1]],
    'Z': [[0, 0], [1, 0], [1, 1], [2, 1]],
    'J': [[0, 0], [0, 1], [1, 1], [2, 1]],
    'L': [[2, 0], [0, 1], [1, 1], [2, 1]]
}

# 初始化随机种子
random.seed(42)


class TetrisGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tetris Medium")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 48)
        self.reset_game()

    def reset_game(self):
        # 清空棋盘
        self.board = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.last_drop_time = pygame.time.get_ticks()
        self.new_piece()

    def new_piece(self):
        if self.game_over:
            return
        
        # 随机选择一个方块类型
        pieces = list(SHAPES.keys())
        shape_type = random.choice(pieces)
        
        # 创建新方块对象
        self.piece = {
            'type': shape_type,
            'matrix': [list(offset) for offset in SHAPES[shape_type]],
            'x': 3,  # 初始居中（10列，中心列约为4，但I型需要调整）
            'y': 0
        }
        
        # 若新方块生成即冲突，游戏结束
        if self.is_collision():
            self.game_over = True

    def rotate(self):
        shape_type = self.piece['type']
        new_matrix = []
        max_x = max(p[0] for p in self.piece['matrix'])
        
        # 顺时针旋转: (x, y) -> (max_x - y, x)
        for x, y in self.piece['matrix']:
            new_matrix.append([max_x - y, x])
        
        old_x = self.piece['x']
        old_y = self.piece['y']
        
        # 旋转后的位置
        self.piece['matrix'] = new_matrix
        
        # 简单的墙踢（如果旋转后出界）
        if self.is_collision():
            self.piece['x'] = old_x + 1
            if self.is_collision():
                self.piece['x'] = old_x - 1
                if self.is_collision():
                    self.piece['x'] = old_x
                    # 仍冲突，则撤销旋转
                    self.piece['matrix'] = [
                        [p[0], p[1]] for p in self.piece['matrix']  # 实际上需要还原成旋转前的状态
                    ]
                    # 再次修复 matrix（通过旋转三次来还原）
                    for _ in range(3):
                        max_x = max(p[0] for p in self.piece['matrix'])
                        new_matrix = []
                        for x, y in self.piece['matrix']:
                            new_matrix.append([max_x - y, x])
                        self.piece['matrix'] = new_matrix

    def move(self, dx, dy):
        self.piece['x'] += dx
        self.piece['y'] += dy
        
        # 如果碰撞，还原移动
        if self.is_collision():
            self.piece['x'] -= dx
            self.piece['y'] -= dy
            return False  # 表示移动失败（可能触底）
        return True

    def is_collision(self):
        for x, y in self.piece['matrix']:
            board_x = self.piece['x'] + x
            board_y = self.piece['y'] + y
            
            # 检查边界
            if board_x < 0 or board_x >= GRID_COLS or board_y >= GRID_ROWS:
                return True
            # 检查是否与已有方块重叠
            if board_y >= 0 and self.board[board_y][board_x] is not None:
                return True
        return False

    def lock_piece(self):
        shape_type = self.piece['type']
        for x, y in self.piece['matrix']:
            board_x = self.piece['x'] + x
            board_y = self.piece['y'] + y
            if 0 <= board_y < GRID_ROWS and 0 <= board_x < GRID_COLS:
                self.board[board_y][board_x] = COLORS[shape_type]

        # 检查并消除完整行
        self.clear_lines()
        
        # 生成新方块
        self.new_piece()

    def clear_lines(self):
        lines_cleared = 0
        y = GRID_ROWS - 1
        while y >= 0:
            if all(cell is not None for cell in self.board[y]):
                # 移除整行
                del self.board[y]
                self.board.insert(0, [None for _ in range(GRID_COLS)])
                lines_cleared += 1
                # 检查同一行（因为下移后的行可能也满了）
            else:
                y -= 1
        
        if lines_cleared > 0:
            self.lines_cleared += lines_cleared
            # 根据消除行数计算分数
            if lines_cleared == 1:
                self.score += 100
            elif lines_cleared == 2:
                self.score += 300
            elif lines_cleared == 3:
                self.score += 500
            elif lines_cleared == 4:
                self.score += 800

    def hard_drop(self):
        while True:
            self.piece['y'] += 1
            if self.is_collision():
                self.piece['y'] -= 1
                break
        self.lock_piece()

    def update(self, current_time):
        if self.game_over:
            return
        
        # 检查自动下落
        if current_time - self.last_drop_time >= AUTO_DROP_INTERVAL:
            if not self.move(0, 1):
                self.lock_piece()
            self.last_drop_time = current_time

    def draw(self):
        # 填充背景
        self.screen.fill(BLACK)
        
        # 绘制网格线
        for i in range(GRID_ROWS + 1):
            start = (BOARD_LEFT, BOARD_TOP + i * GRID_SIZE)
            end = (BOARD_LEFT + GRID_COLS * GRID_SIZE, BOARD_TOP + i * GRID_SIZE)
            pygame.draw.line(self.screen, LIGHT_GRAY, start, end, 1)
        for i in range(GRID_COLS + 1):
            start = (BOARD_LEFT + i * GRID_SIZE, BOARD_TOP)
            end = (BOARD_LEFT + i * GRID_SIZE, BOARD_TOP + GRID_ROWS * GRID_SIZE)
            pygame.draw.line(self.screen, LIGHT_GRAY, start, end, 1)
        
        # 绘制已固定的方块
        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                if self.board[y][x] is not None:
                    rect = pygame.Rect(
                        BOARD_LEFT + x * GRID_SIZE + 1,
                        BOARD_TOP + y * GRID_SIZE + 1,
                        GRID_SIZE - 2,
                        GRID_SIZE - 2
                    )
                    pygame.draw.rect(self.screen, self.board[y][x], rect)
                    # 边框增强
                    pygame.draw.rect(self.screen, tuple(c // 5 for c in self.board[y][x]), rect, 1)
        
        # 绘制当前下落的方块
        if not self.game_over:
            color = COLORS[self.piece['type']]
            for x, y in self.piece['matrix']:
                board_x = self.piece['x'] + x
                board_y = self.piece['y'] + y
                if 0 <= board_y < GRID_ROWS:
                    rect = pygame.Rect(
                        BOARD_LEFT + board_x * GRID_SIZE + 1,
                        BOARD_TOP + board_y * GRID_SIZE + 1,
                        GRID_SIZE - 2,
                        GRID_SIZE - 2
                    )
                    pygame.draw.rect(self.screen, color, rect)
                    # 边框增强
                    pygame.draw.rect(self.screen, tuple(c // 5 for c in color), rect, 1)
        
        # HUD 区域
        hud_x = BOARD_LEFT + GRID_COLS * GRID_SIZE + 40
        hud_y = BOARD_TOP
        
        # 分数与行数显示
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        
        self.screen.blit(score_text, (hud_x, hud_y))
        self.screen.blit(lines_text, (hud_x, hud_y + 30))
        
        # 游戏结束提示
        if self.game_over:
            game_over_text = self.big_font.render("GAME OVER", True, (255, 0, 0))
            score_final = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.font.render("Press R to Restart", True, WHITE)
            
            self.screen.blit(game_over_text, (BOARD_LEFT + (GRID_COLS * GRID_SIZE - game_over_text.get_width()) // 2, 250))
            self.screen.blit(score_final, (BOARD_LEFT + (GRID_COLS * GRID_SIZE - score_final.get_width()) // 2, 320))
            self.screen.blit(restart_text, (BOARD_LEFT + (GRID_COLS * GRID_SIZE - restart_text.get_width()) // 2, 360))
        
        # 控制说明
        self.screen.blit(self.font.render("Controls:", True, WHITE), (BOARD_LEFT + (GRID_COLS * GRID_SIZE + 40), hud_y + 100))
        self.screen.blit(self.font.render("← → : Move", True, WHITE), (BOARD_LEFT + (GRID_COLS * GRID_SIZE + 40), hud_y + 130))
        self.screen.blit(self.font.render("↑ : Rotate", True, WHITE), (BOARD_LEFT + (GRID_COLS * GRID_SIZE + 40), hud_y + 160))
        self.screen.blit(self.font.render("↓ : Down", True, WHITE), (BOARD_LEFT + (GRID_COLS * GRID_SIZE + 40), hud_y + 190))
        self.screen.blit(self.font.render("Space : Hard Drop", True, WHITE), (BOARD_LEFT + (GRID_COLS * GRID_SIZE + 40), hud_y + 220))
        self.screen.blit(self.font.render("ESC : Exit", True, WHITE), (BOARD_LEFT + (GRID_COLS * GRID_SIZE + 40), hud_y + 250))
        self.screen.blit(self.font.render("R : Restart", True, WHITE), (BOARD_LEFT + (GRID_COLS * GRID_SIZE + 40), hud_y + 280))
        
        # 窗口边框
        board_rect = pygame.Rect(BOARD_LEFT - 10, BOARD_TOP - 10, GRID_COLS * GRID_SIZE + 20, GRID_ROWS * GRID_SIZE + 20)
        pygame.draw.rect(self.screen, WHITE, board_rect, 3)
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset_game()
                    elif event.key == pygame.K_r and not self.game_over:
                        self.reset_game()
                    elif not self.game_over:
                        if event.key == pygame.K_LEFT:
                            self.move(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move(1, 0)
                        elif event.key == pygame.K_UP:
                            self.rotate()
                        elif event.key == pygame.K_DOWN:
                            if not self.move(0, 1):
                                self.lock_piece()
                            self.last_drop_time = current_time - AUTO_DROP_INTERVAL // 2  # 快速重置计时器
                        elif event.key == pygame.K_SPACE:
                            self.hard_drop()
                            self.last_drop_time = current_time - AUTO_DROP_INTERVAL // 2
            
            self.update(current_time)
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = TetrisGame()
    game.run()