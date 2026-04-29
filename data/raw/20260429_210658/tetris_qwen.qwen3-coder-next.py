import pygame
import random

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_SIZE = 24
GRID_WIDTH = 10
GRID_HEIGHT = 20
GAME_X_OFFSET = 100
GAME_Y_OFFSET = 60
FPS = 60
DROP_INTERVAL = 500

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (64, 64, 64)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (160, 32, 240)
CYAN = (0, 255, 255)

# 方块形状定义
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]]
}

SHAPES_COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': PURPLE,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE
}

class TetrisGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tetris")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.big_font = pygame.font.SysFont('Arial', 48)
        random.seed(42)

        self.reset_game()

    def reset_game(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.piece_type = self.random_piece_type()
        self.piece_x = GRID_WIDTH // 2 - len(SHAPES[self.piece_type][0]) // 2
        self.piece_y = 0
        self.next_piece_type = self.random_piece_type()
        self.last_drop_time = 0
        self.drop_counter = 0

    def random_piece_type(self):
        return random.choice(list(SHAPES.keys()))

    def new_piece(self):
        self.piece_type = self.next_piece_type
        self.next_piece_type = self.random_piece_type()
        self.piece_x = GRID_WIDTH // 2 - len(SHAPES[self.piece_type][0]) // 2
        self.piece_y = 0
        
        # 检查新方块是否与已存在的方块重叠
        if self.collision(0, 0):
            self.game_over = True

    def collision(self, dx, dy):
        shape = SHAPES[self.piece_type]
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.piece_x + x + dx
                    new_y = self.piece_y + y + dy
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return True
                    if new_y >= 0 and self.grid[new_y][new_x] is not None:
                        return True
        return False

    def rotate(self):
        shape = SHAPES[self.piece_type]
        new_shape = [list(row) for row in zip(*shape[::-1])]
        # 直接创建一个临时对象进行碰撞检测
        old_shape = SHAPES[self.piece_type]
        SHAPES[self.piece_type] = new_shape
        
        # 检查旋转后是否碰撞，如果碰撞尝试墙踢（简单版本）
        if not self.collision(0, 0):
            # 旋转成功，保持新形状
            pass
        else:
            # 如果直接碰撞，尝试左右移动一格
            if not self.collision(1, 0):
                self.piece_x += 1
            elif not self.collision(-1, 0):
                self.piece_x -= 1
            else:
                # 无法旋转，恢复原形状
                SHAPES[self.piece_type] = old_shape
                return False
        
        return True

    def lock_piece(self):
        shape = SHAPES[self.piece_type]
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    if self.piece_y + y >= 0:
                        self.grid[self.piece_y + y][self.piece_x + x] = SHAPES_COLORS[self.piece_type]
        
        self.clear_lines()
        self.new_piece()

    def clear_lines(self):
        lines_to_remove = []
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                lines_to_remove.append(y)
        
        if len(lines_to_remove) > 0:
            for y in reversed(lines_to_remove):
                del self.grid[y]
                self.grid.insert(0, [None for _ in range(GRID_WIDTH)])
            
            # 更新计分系统
            lines = len(lines_to_remove)
            if lines == 1:
                self.score += 100
            elif lines == 2:
                self.score += 300
            elif lines == 3:
                self.score += 500
            elif lines == 4:
                self.score += 800
            
            self.lines_cleared += lines

    def hard_drop(self):
        while not self.collision(0, 1):
            self.piece_y += 1

    def update(self, dt):
        if self.game_over:
            return
        
        self.drop_counter += dt
        if self.drop_counter >= DROP_INTERVAL:
            self.drop_counter = 0
            if not self.collision(0, 1):
                self.piece_y += 1
            else:
                self.lock_piece()

    def handle_input(self, keys):
        if self.game_over:
            if keys[pygame.K_r]:
                self.reset_game()
            if keys[pygame.K_ESCAPE]:
                return True
            return False
        
        if keys[pygame.K_LEFT]:
            if not self.collision(-1, 0):
                self.piece_x -= 1
        if keys[pygame.K_RIGHT]:
            if not self.collision(1, 0):
                self.piece_x += 1
        if keys[pygame.K_DOWN]:
            if not self.collision(0, 1):
                self.piece_y += 1
        if keys[pygame.K_SPACE]:
            self.hard_drop()
        if keys[pygame.K_UP]:
            self.rotate()
        if keys[pygame.K_ESCAPE]:
            return True
        
        return False

    def draw_grid(self):
        # 绘制背景区域
        pygame.draw.rect(self.screen, BLACK, (GAME_X_OFFSET, GAME_Y_OFFSET, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE))
        
        # 绘制网格线
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, GRAY, (GAME_X_OFFSET + x * BLOCK_SIZE, GAME_Y_OFFSET), 
                             (GAME_X_OFFSET + x * BLOCK_SIZE, GAME_Y_OFFSET + GRID_HEIGHT * BLOCK_SIZE))
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, GRAY, (GAME_X_OFFSET, GAME_Y_OFFSET + y * BLOCK_SIZE), 
                             (GAME_X_OFFSET + GRID_WIDTH * BLOCK_SIZE, GAME_Y_OFFSET + y * BLOCK_SIZE))
        
        # 绘制已锁定的方块
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    pygame.draw.rect(self.screen, self.grid[y][x], 
                                     (GAME_X_OFFSET + x * BLOCK_SIZE + 1, GAME_Y_OFFSET + y * BLOCK_SIZE + 1, 
                                      BLOCK_SIZE - 2, BLOCK_SIZE - 2))
                    pygame.draw.rect(self.screen, WHITE, 
                                     (GAME_X_OFFSET + x * BLOCK_SIZE + 1, GAME_Y_OFFSET + y * BLOCK_SIZE + 1, 
                                      BLOCK_SIZE - 2, BLOCK_SIZE - 2), 1)

    def draw_piece(self):
        shape = SHAPES[self.piece_type]
        color = SHAPES_COLORS[self.piece_type]
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, color, 
                                     (GAME_X_OFFSET + (self.piece_x + x) * BLOCK_SIZE + 1, 
                                      GAME_Y_OFFSET + (self.piece_y + y) * BLOCK_SIZE + 1, 
                                      BLOCK_SIZE - 2, BLOCK_SIZE - 2))
                    pygame.draw.rect(self.screen, WHITE, 
                                     (GAME_X_OFFSET + (self.piece_x + x) * BLOCK_SIZE + 1, 
                                      GAME_Y_OFFSET + (self.piece_y + y) * BLOCK_SIZE + 1, 
                                      BLOCK_SIZE - 2, BLOCK_SIZE - 2), 1)

    def draw_hud(self):
        # 分数
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (GAME_X_OFFSET + GRID_WIDTH * BLOCK_SIZE + 50, 100))
        
        # 已消除行数
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (GAME_X_OFFSET + GRID_WIDTH * BLOCK_SIZE + 50, 150))
        
        # 下一个方块
        next_text = self.font.render("Next:", True, WHITE)
        self.screen.blit(next_text, (GAME_X_OFFSET + GRID_WIDTH * BLOCK_SIZE + 50, 200))
        
        shape = SHAPES[self.next_piece_type]
        color = SHAPES_COLORS[self.next_piece_type]
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, color, 
                                     (GAME_X_OFFSET + GRID_WIDTH * BLOCK_SIZE + 50 + x * 20, 
                                      230 + y * 20, 18, 18))
                    pygame.draw.rect(self.screen, WHITE, 
                                     (GAME_X_OFFSET + GRID_WIDTH * BLOCK_SIZE + 50 + x * 20, 
                                      230 + y * 20, 18, 18), 1)
        
        # 操作提示
        controls = [
            "Controls:",
            " Arrows: Move/Rotate",
            " Down: Soft Drop",
            " Space: Hard Drop",
            " ESC: Quit",
            " R: Restart"
        ]
        for i, text in enumerate(controls):
            color_str = WHITE
            if i == 0:
                color_str = (200, 200, 200)
            else:
                color_str = WHITE
            control_text = self.font.render(text, True, color_str)
            self.screen.blit(control_text, (GAME_X_OFFSET + GRID_WIDTH * BLOCK_SIZE + 50, 300 + i * 30))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.big_font.render("GAME OVER", True, RED)
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
        
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
        
        restart_text = self.font.render("Press R to Restart", True, WHITE)
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))
        
        quit_text = self.font.render("Press ESC to Quit", True, WHITE)
        self.screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))

    def draw(self):
        self.screen.fill(BLACK)
        
        title = self.big_font.render("TETRIS", True, CYAN)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        
        self.draw_grid()
        if not self.game_over:
            self.draw_piece()
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()

    def run(self):
        running = True
        
        while running:
            dt = self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            keys = pygame.key.get_pressed()
            if self.handle_input(keys):
                running = False
            
            self.update(dt)
            self.draw()
        
        pygame.quit()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()