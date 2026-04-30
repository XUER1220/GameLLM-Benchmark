import pygame
import random

pygame.init()

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 24

BOARD_WIDTH = GRID_WIDTH * CELL_SIZE
BOARD_HEIGHT = GRID_HEIGHT * CELL_SIZE
BOARD_OFFSET_X = (SCREEN_WIDTH // 2) - (BOARD_WIDTH // 2) - 100
BOARD_OFFSET_Y = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2

FPS = 60
FALL_SPEED_INITIAL = 500  # 初始下落间隔(ms)
SOFT_DROP_MULTIPLIER = 20  # 加速下落的速度倍数

SCORE_PER_LINE = {1: 100, 2: 300, 3: 500, 4: 800}

COLORS = [
    (0, 0, 0),         # 0: 背景黑
    (0, 255, 255),     # 1: I - 青色
    (255, 255, 0),     # 2: O - 黄色
    (128, 0, 128),     # 3: T - 紫色
    (0, 255, 0),       # 4: S - 绿色
    (255, 0, 0),       # 5: Z - 红色
    (0, 0, 255),       # 6: J - 蓝色
    (255, 165, 0)      # 7: L - 橙色
]

SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[2, 2],
     [2, 2]],        # O
    [[0, 3, 0],
     [3, 3, 3]],     # T
    [[0, 4, 4],
     [4, 4, 0]],     # S
    [[5, 5, 0],
     [0, 5, 5]],     # Z
    [[6, 0, 0],
     [6, 6, 6]],     # J
    [[0, 0, 7],
     [7, 7, 7]]      # L
]

# 随机种子
random.seed(42)

# 初始化pygame
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris Medium")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 28)

class Tetris:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.lines_cleared = 0
        self.fall_speed = FALL_SPEED_INITIAL
        self.last_fall_time = pygame.time.get_ticks()
        self.piece_x = GRID_WIDTH // 2 - len(self.current_piece[0]) // 2
        self.piece_y = 0
    
    def new_piece(self):
        shape = random.choice(SHAPES)
        return shape
    
    def valid_move(self, piece, x, y, board=None):
        if board is None:
            board = self.board
        for row_idx, row in enumerate(piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    new_x = x + col_idx
                    new_y = y + row_idx
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return False
                    if new_y >= 0 and board[new_y][new_x]:
                        return False
        return True
    
    def rotate_piece(self, piece):
        return [[piece[y][x] for y in range(len(piece)-1, -1, -1)] for x in range(len(piece[0]))]
    
    def lock_piece(self):
        for row_idx, row in enumerate(self.current_piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    if self.piece_y + row_idx < 0:
                        self.game_over = True
                        return
                    self.board[self.piece_y + row_idx][self.piece_x + col_idx] = cell
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        self.piece_x = GRID_WIDTH // 2 - len(self.current_piece[0]) // 2
        self.piece_y = 0
        
        if not self.valid_move(self.current_piece, self.piece_x, self.piece_y):
            self.game_over = True
    
    def clear_lines(self):
        lines_to_clear = []
        for row_idx in range(GRID_HEIGHT):
            if all(self.board[row_idx]):
                lines_to_clear.append(row_idx)
        
        for row_idx in lines_to_clear:
            del self.board[row_idx]
            self.board.insert(0, [0 for _ in range(GRID_WIDTH)])
        
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            self.score += SCORE_PER_LINE.get(len(lines_to_clear), 0)
    
    def hard_drop(self):
        while self.valid_move(self.current_piece, self.piece_x, self.piece_y + 1):
            self.piece_y += 1
        self.lock_piece()
    
    def update(self, keys):
        if self.game_over:
            return
        
        current_time = pygame.time.get_ticks()
        
        # 自动下落
        if current_time - self.last_fall_time > self.fall_speed:
            if self.valid_move(self.current_piece, self.piece_x, self.piece_y + 1):
                self.piece_y += 1
            else:
                self.lock_piece()
            self.last_fall_time = current_time
        
        # 加速下落
        fall_speed = self.fall_speed
        if keys[pygame.K_DOWN]:
            fall_speed = self.fall_speed // SOFT_DROP_MULTIPLIER
        
        if current_time - self.last_fall_time > fall_speed:
            if self.valid_move(self.current_piece, self.piece_x, self.piece_y + 1):
                self.piece_y += 1
            else:
                self.lock_piece()
            self.last_fall_time = current_time
        
        # 左右移动
        if keys[pygame.K_LEFT]:
            if self.valid_move(self.current_piece, self.piece_x - 1, self.piece_y):
                self.piece_x -= 1
        if keys[pygame.K_RIGHT]:
            if self.valid_move(self.current_piece, self.piece_x + 1, self.piece_y):
                self.piece_x += 1
    
    def draw(self):
        # 绘制背景
        screen.fill((30, 30, 50))
        
        # 绘制棋盘背景
        pygame.draw.rect(screen, (20, 20, 40), 
                         (BOARD_OFFSET_X, BOARD_OFFSET_Y, BOARD_WIDTH, BOARD_HEIGHT))
        
        # 绘制网格线
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(screen, (50, 50, 70), 
                             (BOARD_OFFSET_X + x * CELL_SIZE, BOARD_OFFSET_Y),
                             (BOARD_OFFSET_X + x * CELL_SIZE, BOARD_OFFSET_Y + BOARD_HEIGHT),
                             1)
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(screen, (50, 50, 70), 
                             (BOARD_OFFSET_X, BOARD_OFFSET_Y + y * CELL_SIZE),
                             (BOARD_OFFSET_X + BOARD_WIDTH, BOARD_OFFSET_Y + y * CELL_SIZE),
                             1)
        
        # 绘制已固定的方块
        for row_idx, row in enumerate(self.board):
            for col_idx, cell in enumerate(row):
                if cell:
                    color_idx = cell
                    pygame.draw.rect(screen, COLORS[color_idx],
                                     (BOARD_OFFSET_X + col_idx * CELL_SIZE + 1,
                                      BOARD_OFFSET_Y + row_idx * CELL_SIZE + 1,
                                      CELL_SIZE - 2, CELL_SIZE - 2))
                    pygame.draw.rect(screen, (255, 255, 255),
                                     (BOARD_OFFSET_X + col_idx * CELL_SIZE + 1,
                                      BOARD_OFFSET_Y + row_idx * CELL_SIZE + 1,
                                      CELL_SIZE - 2, CELL_SIZE - 2), 1)
        
        # 绘制当前下落的方块
        if not self.game_over:
            for row_idx, row in enumerate(self.current_piece):
                for col_idx, cell in enumerate(row):
                    if cell:
                        color_idx = cell
                        pygame.draw.rect(screen, COLORS[color_idx],
                                         (BOARD_OFFSET_X + (self.piece_x + col_idx) * CELL_SIZE + 1,
                                          BOARD_OFFSET_Y + (self.piece_y + row_idx) * CELL_SIZE + 1,
                                          CELL_SIZE - 2, CELL_SIZE - 2))
                        pygame.draw.rect(screen, (255, 255, 255),
                                         (BOARD_OFFSET_X + (self.piece_x + col_idx) * CELL_SIZE + 1,
                                          BOARD_OFFSET_Y + (self.piece_y + row_idx) * CELL_SIZE + 1,
                                          CELL_SIZE - 2, CELL_SIZE - 2), 1)
        
        # 绘制侧边信息面板
        panel_x = BOARD_OFFSET_X + BOARD_WIDTH + 40
        panel_y = BOARD_OFFSET_Y
        
        # 绘制下一个方块预览
        next_text = font.render("NEXT", True, (255, 255, 255))
        screen.blit(next_text, (panel_x, panel_y))
        
        preview_size = len(self.next_piece[0]) * CELL_SIZE
        preview_x = panel_x + (150 - preview_size) // 2
        preview_y = panel_y + 50
        
        for row_idx, row in enumerate(self.next_piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    color_idx = cell
                    pygame.draw.rect(screen, COLORS[color_idx],
                                     (preview_x + col_idx * CELL_SIZE + 1,
                                      preview_y + row_idx * CELL_SIZE + 1,
                                      CELL_SIZE - 2, CELL_SIZE - 2))
                    pygame.draw.rect(screen, (255, 255, 255),
                                     (preview_x + col_idx * CELL_SIZE + 1,
                                      preview_y + row_idx * CELL_SIZE + 1,
                                      CELL_SIZE - 2, CELL_SIZE - 2), 1)
        
        # 绘制分数信息
        info_y = preview_y + len(self.next_piece) * CELL_SIZE + 40
        score_text = font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (panel_x, info_y))
        
        lines_text = font.render(f"LINES: {self.lines_cleared}", True, (255, 255, 255))
        screen.blit(lines_text, (panel_x, info_y + 50))
        
        # 绘制操作说明
        controls_y = info_y + 150
        controls = [
            "CONTROLS:",
            "←→ : Move",
            "↑  : Rotate",
            "↓  : Soft Drop",
            "SPACE: Hard Drop",
            "R: Restart",
            "ESC: Quit"
        ]
        
        for i, text in enumerate(controls):
            control_text = small_font.render(text, True, (200, 200, 255))
            screen.blit(control_text, (panel_x, controls_y + i * 30))
        
        # 游戏结束显示
        if self.game_over:
            # 半透明覆盖层
            overlay = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (BOARD_OFFSET_X, BOARD_OFFSET_Y))
            
            game_over_text = font.render("GAME OVER", True, (255, 50, 50))
            final_score_text = font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            restart_text = small_font.render("Press R to Restart", True, (200, 255, 200))
            
            center_x = BOARD_OFFSET_X + BOARD_WIDTH // 2
            center_y = BOARD_OFFSET_Y + BOARD_HEIGHT // 2
            
            screen.blit(game_over_text, 
                        (center_x - game_over_text.get_width() // 2, center_y - 60))
            screen.blit(final_score_text,
                        (center_x - final_score_text.get_width() // 2, center_y - 20))
            screen.blit(restart_text,
                        (center_x - restart_text.get_width() // 2, center_y + 30))

def main():
    game = Tetris()
    running = True
    
    while running:
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                if event.key == pygame.K_r:
                    game.reset()
                
                if not game.game_over:
                    if event.key == pygame.K_UP:
                        rotated = game.rotate_piece(game.current_piece)
                        if game.valid_move(rotated, game.piece_x, game.piece_y):
                            game.current_piece = rotated
                    
                    if event.key == pygame.K_SPACE:
                        game.hard_drop()
        
        game.update(keys)
        game.draw()
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()