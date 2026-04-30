import pygame
import random

# 初始化pygame
pygame.init()

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_SIZE = 24
BOARD_WIDTH = 10
BOARD_HEIGHT = 20

# 窗口居中偏左显示
BOARD_X = (SCREEN_WIDTH - BOARD_WIDTH * BLOCK_SIZE) // 2 - 100
BOARD_Y = (SCREEN_HEIGHT - BOARD_HEIGHT * BLOCK_SIZE) // 2

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
LIGHT_GREY = (200, 200, 200)

# 7种方块（使用标准形状定义）
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]]
}

# 7种方块颜色（按I, O, T, S, Z, J, L顺序）
COLORS = [
    (0, 255, 255),  # I - Cyan
    (255, 255, 0),  # O - Yellow
    (128, 0, 128),  # T - Purple
    (0, 255, 0),    # S - Green
    (255, 0, 0),    # Z - Red
    (0, 0, 255),    # J - Blue
    (255, 165, 0)   # L - Orange
]

# 帧率和游戏速度
FPS = 60
DROP_INTERVAL = 500  # 毫秒

# 分数规则
SCORE_RULES = {1: 100, 2: 300, 3: 500, 4: 800}

# 随机种子
random.seed(42)


class Tetromino:
    def __init__(self, x, y, shape_key):
        self.x = x
        self.y = y
        self.shape_key = shape_key
        self.shape = SHAPES[shape_key]
        self.color = COLORS[["I", "O", "T", "S", "Z", "J", "L"].index(shape_key)]

    def rotate(self):
        # 旋转方块
        rotated = list(zip(*self.shape[::-1]))
        self.shape = [list(row) for row in rotated]


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Medium")
        self.clock = pygame.time.Clock()
        self.reset_game()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    def reset_game(self):
        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.lines_cleared = 0
        self.last_drop_time = 0
        self.game_over = False
        self.current_piece = self.new_piece()
        self.next_piece_key = random.choice(list(SHAPES.keys()))
        self.next_piece = Tetromino(0, 0, self.next_piece_key)

    def new_piece(self):
        # 生成新方块
        piece_key = self.next_piece_key
        self.next_piece_key = random.choice(list(SHAPES.keys()))
        piece = Tetromino(BOARD_WIDTH // 2 - len(SHAPES[piece_key][0]) // 2, 0, piece_key)
        self.next_piece = Tetromino(0, 0, self.next_piece_key)  # 重置next_piece位置用于绘制
        return piece

    def check_collision(self, piece, offset_x=0, offset_y=0):
        # 检测碰撞
        shape = piece.shape
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + offset_x
                    new_y = piece.y + y + offset_y
                    if new_x < 0 or new_x >= BOARD_WIDTH or new_y >= BOARD_HEIGHT:
                        return True
                    if new_y >= 0 and self.board[new_y][new_x]:
                        return True
        return False

    def lock_piece(self):
        # 将当前方块固定到棋盘
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    board_y = self.current_piece.y + y
                    board_x = self.current_piece.x + x
                    if board_y < 0:  # 游戏结束
                        self.game_over = True
                        return
                    self.board[board_y][board_x] = self.current_piece.color
        self.clear_lines()
        self.current_piece = self.new_piece()
        # 检查新生成方块是否碰撞，若是则游戏结束
        if self.check_collision(self.current_piece):
            self.game_over = True

    def clear_lines(self):
        # 消除完整行
        lines_to_clear = []
        for y in range(BOARD_HEIGHT):
            if all(self.board[y]):
                lines_to_clear.append(y)
        if lines_to_clear:
            for y in reversed(lines_to_clear):
                del self.board[y]
                self.board.insert(0, [None for _ in range(BOARD_WIDTH)])
            cleared_count = len(lines_to_clear)
            self.lines_cleared += cleared_count
            self.score += SCORE_RULES.get(cleared_count, 0)

    def move(self, dx, dy):
        # 移动方块
        if not self.check_collision(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False

    def hard_drop(self):
        # 硬降
        while self.move(0, 1):
            pass

    def rotate_piece(self):
        # 旋转方块（带简单墙踢）
        original_shape = self.current_piece.shape
        self.current_piece.rotate()
        if self.check_collision(self.current_piece):
            # 无效旋转，恢复原状
            self.current_piece.shape = original_shape
            self.current_piece.rotate()
            self.current_piece.rotate()
            self.current_piece.rotate()

    def update(self, dt):
        # 游戏逻辑更新
        if self.game_over:
            return
        current_time = pygame.time.get_ticks()
        if current_time - self.last_drop_time >= DROP_INTERVAL:
            if not self.move(0, 1):
                self.lock_piece()
            self.last_drop_time = current_time

    def draw(self):
        # 绘制画面
        self.screen.fill(BLACK)
        
        # 绘制主棋盘背景
        pygame.draw.rect(self.screen, BLACK, 
                         (BOARD_X, BOARD_Y, BOARD_WIDTH * BLOCK_SIZE, BOARD_HEIGHT * BLOCK_SIZE))
        # 绘制棋盘网格线
        for x in range(BOARD_WIDTH + 1):
            pygame.draw.line(self.screen, GREY, 
                             (BOARD_X + x * BLOCK_SIZE, BOARD_Y),
                             (BOARD_X + x * BLOCK_SIZE, BOARD_Y + BOARD_HEIGHT * BLOCK_SIZE), 1)
        for y in range(BOARD_HEIGHT + 1):
            pygame.draw.line(self.screen, GREY, 
                             (BOARD_X, BOARD_Y + y * BLOCK_SIZE),
                             (BOARD_X + BOARD_WIDTH * BLOCK_SIZE, BOARD_Y + y * BLOCK_SIZE), 1)
        
        # 绘制已固定的方块
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.board[y][x]:
                    pygame.draw.rect(self.screen, self.board[y][x], 
                                     (BOARD_X + x * BLOCK_SIZE, BOARD_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                    # 添加边框
                    pygame.draw.rect(self.screen, BLACK, 
                                     (BOARD_X + x * BLOCK_SIZE, BOARD_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 2)
        
        # 绘制当前方块
        if self.current_piece:
            for y, row in enumerate(self.current_piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, self.current_piece.color,
                                         (BOARD_X + (self.current_piece.x + x) * BLOCK_SIZE,
                                          BOARD_Y + (self.current_piece.y + y) * BLOCK_SIZE,
                                          BLOCK_SIZE, BLOCK_SIZE))
                        pygame.draw.rect(self.screen, BLACK,
                                         (BOARD_X + (self.current_piece.x + x) * BLOCK_SIZE,
                                          BOARD_Y + (self.current_piece.y + y) * BLOCK_SIZE,
                                          BLOCK_SIZE, BLOCK_SIZE), 2)

        # HUD: 分数信息
        hud_x = BOARD_X + BOARD_WIDTH * BLOCK_SIZE + 20
        hud_y = BOARD_Y + 10
        
        # 绘制HUD背景
        pygame.draw.rect(self.screen, LIGHT_GREY, 
                         (hud_x, hud_y, 200, 200))
        
        # 分数
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (hud_x + 10, hud_y + 10))
        
        # 已消除行数
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, BLACK)
        self.screen.blit(lines_text, (hud_x + 10, hud_y + 60))
        
        # 下一个方块
        next_text = self.font.render("Next:", True, BLACK)
        self.screen.blit(next_text, (hud_x + 10, hud_y + 110))
        
        # 绘制下一个方块
        if self.next_piece.shape:
            for y, row in enumerate(self.next_piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        draw_x = hud_x + 10 + x * BLOCK_SIZE
                        draw_y = hud_y + 140 + y * BLOCK_SIZE
                        pygame.draw.rect(self.screen, self.next_piece.color, 
                                        (draw_x, draw_y, BLOCK_SIZE, BLOCK_SIZE))
                        pygame.draw.rect(self.screen, BLACK, 
                                        (draw_x, draw_y, BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # 游戏结束界面
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("Game Over", True, WHITE)
            score_final_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.font.render("Press R to Restart", True, WHITE)
            esc_text = self.small_font.render("Press ESC to Exit", True, WHITE)
            
            self.screen.blit(game_over_text, 
                             (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
            self.screen.blit(score_final_text, 
                             (SCREEN_WIDTH // 2 - score_final_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(restart_text, 
                             (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
            self.screen.blit(esc_text, 
                             (SCREEN_WIDTH // 2 - esc_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif not self.game_over:
                        if event.key == pygame.K_LEFT:
                            self.move(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move(1, 0)
                        elif event.key == pygame.K_UP:
                            self.rotate_piece()
                        elif event.key == pygame.K_DOWN:
                            self.move(0, 1)
                            self.last_drop_time = pygame.time.get_ticks()  # 重置下落时间
                        elif event.key == pygame.K_SPACE:
                            self.hard_drop()
                            self.last_drop_time = pygame.time.get_ticks()
            
            # 更新游戏状态
            self.update(dt)
            # 绘制画面
            self.draw()
        
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()