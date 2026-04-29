import pygame
import random
import sys

# ========== 常量参数 ==========
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_WIDTH = 30
GRID_HEIGHT = 24
CELL_SIZE = 20
GRID_AREA_WIDTH = GRID_WIDTH * CELL_SIZE
GRID_AREA_HEIGHT = GRID_HEIGHT * CELL_SIZE
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_AREA_WIDTH) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_AREA_HEIGHT) // 2 + 40

FPS = 60
SNAKE_SPEED = 10  # 每秒移动的网格数
INIT_SNAKE_LENGTH = 3
SNAKE_START_X = GRID_WIDTH // 2 - INIT_SNAKE_LENGTH // 2
SNAKE_START_Y = GRID_HEIGHT // 2
FOOD_SCORE = 10

COLOR_BG = (20, 20, 30)
COLOR_GRID = (40, 40, 60)
COLOR_GRID_LINE = (60, 60, 80)
COLOR_SNAKE_HEAD = (100, 200, 100)
COLOR_SNAKE_BODY = (80, 160, 80)
COLOR_FOOD = (220, 80, 80)
COLOR_TEXT = (240, 240, 240)
COLOR_HUD_BG = (30, 30, 40)
COLOR_GAME_OVER_BG = (0, 0, 0, 180)

# ========== Pygame 初始化 ==========
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 24)
big_font = pygame.font.SysFont("consolas", 48)

random.seed(42)

# ========== 游戏状态 ==========
class Game:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.snake = [(SNAKE_START_X, SNAKE_START_Y)]
        for i in range(1, INIT_SNAKE_LENGTH):
            self.snake.append((SNAKE_START_X - i, SNAKE_START_Y))
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.move_timer = 0
    
    def generate_food(self):
        free_cells = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT) 
                      if (x, y) not in self.snake]
        return random.choice(free_cells) if free_cells else (0, 0)
    
    def update(self, dt):
        if self.game_over:
            return
        
        # 处理方向变更
        dx, dy = self.next_direction
        cur_dx, cur_dy = self.direction
        if (dx, dy) != (-cur_dx, -cur_dy):
            self.direction = (dx, dy)
        
        # 移动计时器
        self.move_timer += dt
        move_interval = 1.0 / SNAKE_SPEED
        if self.move_timer < move_interval:
            return
        self.move_timer = 0
        
        # 计算新头部位置
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # 碰撞检测
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
            new_head in self.snake):
            self.game_over = True
            return
        
        # 移动蛇
        self.snake.insert(0, new_head)
        
        # 吃食物
        if new_head == self.food:
            self.score += FOOD_SCORE
            self.food = self.generate_food()
        else:
            self.snake.pop()
    
    def draw(self):
        screen.fill(COLOR_BG)
        
        # 绘制网格区域背景
        grid_rect = pygame.Rect(GRID_OFFSET_X, GRID_OFFSET_Y, 
                                GRID_AREA_WIDTH, GRID_AREA_HEIGHT)
        pygame.draw.rect(screen, COLOR_GRID, grid_rect)
        
        # 绘制网格线
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(screen, COLOR_GRID_LINE, 
                            (GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y),
                            (GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y + GRID_AREA_HEIGHT),
                            1)
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(screen, COLOR_GRID_LINE,
                            (GRID_OFFSET_X, GRID_OFFSET_Y + y * CELL_SIZE),
                            (GRID_OFFSET_X + GRID_AREA_WIDTH, GRID_OFFSET_Y + y * CELL_SIZE),
                            1)
        
        # 绘制食物
        fx, fy = self.food
        food_rect = pygame.Rect(GRID_OFFSET_X + fx * CELL_SIZE + 1,
                                GRID_OFFSET_Y + fy * CELL_SIZE + 1,
                                CELL_SIZE - 2, CELL_SIZE - 2)
        pygame.draw.rect(screen, COLOR_FOOD, food_rect, border_radius=CELL_SIZE//3)
        
        # 绘制蛇
        for i, (sx, sy) in enumerate(self.snake):
            snake_rect = pygame.Rect(GRID_OFFSET_X + sx * CELL_SIZE + 1,
                                     GRID_OFFSET_Y + sy * CELL_SIZE + 1,
                                     CELL_SIZE - 2, CELL_SIZE - 2)
            color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE_BODY
            pygame.draw.rect(screen, color, snake_rect, border_radius=CELL_SIZE//4 if i==0 else 0)
        
        # 绘制 HUD 背景
        hud_bg = pygame.Rect(0, 0, SCREEN_WIDTH, GRID_OFFSET_Y - 10)
        pygame.draw.rect(screen, COLOR_HUD_BG, hud_bg)
        
        # 绘制标题
        title_text = font.render("Snake Easy", True, COLOR_TEXT)
        screen.blit(title_text, (20, 10))
        
        # 绘制分数
        score_text = font.render(f"Score: {self.score}", True, COLOR_TEXT)
        screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 20, 10))
        
        # 绘制操作提示
        hint_text = font.render("Arrow Keys: Move | R: Restart | ESC: Exit", True, COLOR_TEXT)
        screen.blit(hint_text, ((SCREEN_WIDTH - hint_text.get_width()) // 2, 10))
        
        # 游戏结束遮罩
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(COLOR_GAME_OVER_BG)
            screen.blit(overlay, (0, 0))
            
            game_over_text = big_font.render("GAME OVER", True, COLOR_SNAKE_HEAD)
            screen.blit(game_over_text, ((SCREEN_WIDTH - game_over_text.get_width()) // 2, SCREEN_HEIGHT // 2 - 60))
            
            final_score_text = font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
            screen.blit(final_score_text, ((SCREEN_WIDTH - final_score_text.get_width()) // 2, SCREEN_HEIGHT // 2))
            
            restart_text = font.render("Press R to Restart", True, COLOR_TEXT)
            screen.blit(restart_text, ((SCREEN_WIDTH - restart_text.get_width()) // 2, SCREEN_HEIGHT // 2 + 40))

# ========== 主循环 ==========
def main():
    game = Game()
    running = True
    
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game.reset()
                elif not game.game_over:
                    if event.key == pygame.K_UP:
                        game.next_direction = (0, -1)
                    elif event.key == pygame.K_DOWN:
                        game.next_direction = (0, 1)
                    elif event.key == pygame.K_LEFT:
                        game.next_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        game.next_direction = (1, 0)
        
        # 游戏更新
        game.update(dt)
        
        # 绘制
        game.draw()
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()