import pygame
import random

pygame.init()

# 固定常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 24
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_WIDTH * CELL_SIZE) // 2 - 80
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_HEIGHT * CELL_SIZE) // 2
FPS = 60

# 方块定义
SHAPES = [
    [[1, 1, 1, 1]],                     # I
    [[1, 1], [1, 1]],                   # O
    [[0, 1, 0], [1, 1, 1]],             # T
    [[0, 1, 1], [1, 1, 0]],             # S
    [[1, 1, 0], [0, 1, 1]],             # Z
    [[1, 0, 0], [1, 1, 1]],             # J
    [[0, 0, 1], [1, 1, 1]]              # L
]

COLORS = [
    (0, 255, 255),   # I: 青色
    (255, 255, 0),   # O: 黄色
    (128, 0, 128),   # T: 紫色
    (0, 255, 0),     # S: 绿色
    (255, 0, 0),     # Z: 红色
    (0, 0, 255),     # J: 蓝色
    (255, 165, 0)    # L: 橙色
]

# 计分规则
SCORE_TABLE = {1: 100, 2: 300, 3: 500, 4: 800}

# 固定随机种子
random.seed(42)

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Medium")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)
        self.reset_game()

    def reset_game(self):
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.fall_time = 0
        self.fall_speed = 500  # 毫秒
        self.spawn_new_piece()

    def spawn_new_piece(self):
        shape_idx = random.randint(0, len(SHAPES) - 1)
        self.current_piece = {
            'shape': SHAPES[shape_idx],
            'color': COLORS[shape_idx],
            'x': GRID_WIDTH // 2 - len(SHAPES[shape_idx][0]) // 2,
            'y': 0
        }
        # 检查游戏结束
        if self.check_collision():
            self.game_over = True

    def rotate_piece(self):
        shape = self.current_piece['shape']
        rotated = [[shape[y][x] for y in range(len(shape)-1, -1, -1)] for x in range(len(shape[0]))]
        original_shape = self.current_piece['shape']
        self.current_piece['shape'] = rotated
        if self.check_collision():
            self.current_piece['shape'] = original_shape
            return False
        return True

    def check_collision(self, dx=0, dy=0):
        shape = self.current_piece['shape']
        px = self.current_piece['x'] + dx
        py = self.current_piece['y'] + dy
        
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    nx = px + x
                    ny = py + y
                    if nx < 0 or nx >= GRID_WIDTH or ny >= GRID_HEIGHT:
                        return True
                    if ny >= 0 and self.board[ny][nx]:
                        return True
        return False

    def merge_piece(self):
        shape = self.current_piece['shape']
        px = self.current_piece['x']
        py = self.current_piece['y']
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    ny = py + y
                    nx = px + x
                    if ny >= 0:
                        self.board[ny][nx] = self.current_piece['color']

    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.board[y]):
                lines_to_clear.append(y)
        
        if not lines_to_clear:
            return 0
        
        # 计分
        self.lines_cleared += len(lines_to_clear)
        self.score += SCORE_TABLE.get(len(lines_to_clear), 0)
        
        # 消除行
        for line in lines_to_clear:
            del self.board[line]
            self.board.insert(0, [0 for _ in range(GRID_WIDTH)])
        
        return len(lines_to_clear)

    def hard_drop(self):
        while not self.check_collision(dy=1):
            self.current_piece['y'] += 1
        self.lock_piece()

    def lock_piece(self):
        self.merge_piece()
        self.clear_lines()
        self.spawn_new_piece()

    def move(self, dx):
        if not self.check_collision(dx=dx):
            self.current_piece['x'] += dx
            return True
        return False

    def update(self, dt):
        if self.game_over:
            return

        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if not self.check_collision(dy=1):
                self.current_piece['y'] += 1
            else:
                self.lock_piece()

    def draw_grid(self):
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, (50, 50, 50),
                             (GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y),
                             (GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y + GRID_HEIGHT * CELL_SIZE))
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, (50, 50, 50),
                             (GRID_OFFSET_X, GRID_OFFSET_Y + y * CELL_SIZE),
                             (GRID_OFFSET_X + GRID_WIDTH * CELL_SIZE, GRID_OFFSET_Y + y * CELL_SIZE))

    def draw_board(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.board[y][x]:
                    rect = pygame.Rect(GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y + y * CELL_SIZE,
                                       CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, self.board[y][x], rect)
                    pygame.draw.rect(self.screen, (30, 30, 30), rect, 1)

    def draw_current_piece(self):
        shape = self.current_piece['shape']
        px = self.current_piece['x']
        py = self.current_piece['y']
        color = self.current_piece['color']
        
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(GRID_OFFSET_X + (px + x) * CELL_SIZE,
                                       GRID_OFFSET_Y + (py + y) * CELL_SIZE,
                                       CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, color, rect)
                    pygame.draw.rect(self.screen, (30, 30, 30), rect, 1)

    def draw_hud(self):
        hud_x = GRID_OFFSET_X + GRID_WIDTH * CELL_SIZE + 40
        hud_y = GRID_OFFSET_Y
        
        # 标题
        title = self.font.render("TETRIS", True, (255, 255, 255))
        self.screen.blit(title, (hud_x, hud_y))
        
        # 分数
        score_text = self.small_font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (hud_x, hud_y + 60))
        
        # 消除行数
        lines_text = self.small_font.render(f"Lines: {self.lines_cleared}", True, (255, 255, 255))
        self.screen.blit(lines_text, (hud_x, hud_y + 100))
        
        # 控制说明
        controls = [
            "Controls:",
            "Left/Right: Move",
            "Up: Rotate",
            "Down: Soft Drop",
            "Space: Hard Drop",
            "R: Restart",
            "ESC: Quit"
        ]
        
        for i, line in enumerate(controls):
            control_text = self.small_font.render(line, True, (200, 200, 200))
            self.screen.blit(control_text, (hud_x, hud_y + 160 + i * 30))
        
        # 游戏结束提示
        if self.game_over:
            overlay = pygame.Surface((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (GRID_OFFSET_X, GRID_OFFSET_Y))
            
            game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
            final_score = self.small_font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            restart_text = self.small_font.render("Press R to Restart", True, (255, 255, 255))
            
            center_x = GRID_OFFSET_X + GRID_WIDTH * CELL_SIZE // 2
            center_y = GRID_OFFSET_Y + GRID_HEIGHT * CELL_SIZE // 2
            
            self.screen.blit(game_over_text, (center_x - game_over_text.get_width() // 2, center_y - 50))
            self.screen.blit(final_score, (center_x - final_score.get_width() // 2, center_y))
            self.screen.blit(restart_text, (center_x - restart_text.get_width() // 2, center_y + 40))

    def draw(self):
        self.screen.fill((20, 20, 30))
        
        # 绘制棋盘区域背景
        board_bg = pygame.Rect(GRID_OFFSET_X, GRID_OFFSET_Y,
                               GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)
        pygame.draw.rect(self.screen, (10, 10, 20), board_bg)
        
        self.draw_grid()
        self.draw_board()
        if not self.game_over:
            self.draw_current_piece()
        self.draw_hud()

    def run(self):
        running = True
        last_time = pygame.time.get_ticks()
        
        while running:
            current_time = pygame.time.get_ticks()
            dt = current_time - last_time
            last_time = current_time
            
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
                            self.move(-1)
                        elif event.key == pygame.K_RIGHT:
                            self.move(1)
                        elif event.key == pygame.K_UP:
                            self.rotate_piece()
                        elif event.key == pygame.K_DOWN:
                            if not self.check_collision(dy=1):
                                self.current_piece['y'] += 1
                        elif event.key == pygame.K_SPACE:
                            self.hard_drop()
            
            if not self.game_over:
                # 持续左右移动
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    if pygame.time.get_ticks() % 10 == 0:
                        self.move(-1)
                if keys[pygame.K_RIGHT]:
                    if pygame.time.get_ticks() % 10 == 0:
                        self.move(1)
                if keys[pygame.K_DOWN]:
                    self.fall_speed = 50
                else:
                    self.fall_speed = 500
            
            self.update(dt)
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()