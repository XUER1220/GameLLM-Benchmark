import pygame
import sys
import random

# 常量定义
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
PLAYER_WIDTH = 110
PLAYER_HEIGHT = 18
PLAYER_SPEED = 8
BALL_SIZE = 16
BALL_SPEED_X = 4
BALL_SPEED_Y = -5
BRICK_COLS = 8
BRICK_ROWS = 5
BRICK_WIDTH = 84
BRICK_HEIGHT = 24
TOTAL_LIVES = 3
POINT_PER_BRICK = 10

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (50, 200, 50)
BLUE = (50, 50, 220)
PLAYER_COLOR = (100, 200, 255)
BALL_COLOR = (255, 255, 255)

# 砖块颜色映射
BRICK_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE]


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Breakout Medium")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        random.seed(42)
        self.reset_game()

    def reset_game(self):
        self.score = 0
        self.lives = TOTAL_LIVES
        self.game_over = False
        self.victory = False
        
        # 初始化球拍
        self.player_x = (WINDOW_WIDTH - PLAYER_WIDTH) // 2
        self.player_y = WINDOW_HEIGHT - PLAYER_HEIGHT - 10
        
        # 初始化小球
        self.ball_x = self.player_x + PLAYER_WIDTH // 2 - BALL_SIZE // 2
        self.ball_y = self.player_y - BALL_SIZE - 5
        self.ball_dx = BALL_SPEED_X
        self.ball_dy = BALL_SPEED_Y
        
        # 初始化砖块
        self.bricks = []
        padding = 20  # 球拍上方和砖块之间的空隙
        total_bricks_width = BRICK_COLS * BRICK_WIDTH
        total_padding = WINDOW_WIDTH - total_bricks_width
        h_spacing = total_padding // (BRICK_COLS + 1)
        v_spacing = 20
        brick_top = 80
        
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = h_spacing + col * (BRICK_WIDTH + h_spacing)
                y = brick_top + row * (BRICK_HEIGHT + v_spacing)
                self.bricks.append({
                    'x': x,
                    'y': y,
                    'width': BRICK_WIDTH,
                    'height': BRICK_HEIGHT,
                    'color': BRICK_COLORS[row]
                })

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r and (self.game_over or self.victory):
                    self.reset_game()
        return True

    def update(self):
        if self.game_over or self.victory:
            return
        
        # 玩家移动
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player_x = max(0, self.player_x - PLAYER_SPEED)
        if keys[pygame.K_RIGHT]:
            self.player_x = min(WINDOW_WIDTH - PLAYER_WIDTH, self.player_x + PLAYER_SPEED)
        
        # 更新球位置
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # 边界反弹
        if self.ball_x <= 0:
            self.ball_x = 0
            self.ball_dx = -self.ball_dx
        elif self.ball_x + BALL_SIZE >= WINDOW_WIDTH:
            self.ball_x = WINDOW_WIDTH - BALL_SIZE
            self.ball_dx = -self.ball_dx
            
        if self.ball_y <= 0:
            self.ball_y = 0
            self.ball_dy = -self.ball_dy
        elif self.ball_y >= WINDOW_HEIGHT:
            # 球掉到底部
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                # 重置球位置
                self.ball_x = self.player_x + PLAYER_WIDTH // 2 - BALL_SIZE // 2
                self.ball_y = self.player_y - BALL_SIZE - 5
                self.ball_dx = BALL_SPEED_X * (1 if random.random() > 0.5 else -1)
                self.ball_dy = BALL_SPEED_Y
        
        # 球拍碰撞检测
        if (self.ball_y + BALL_SIZE >= self.player_y and 
            self.ball_y <= self.player_y + PLAYER_HEIGHT and
            self.ball_x + BALL_SIZE >= self.player_x and 
            self.ball_x <= self.player_x + PLAYER_WIDTH):
            # 球拍反弹，根据球击中球拍的位置微调水平速度
            hit_pos = (self.ball_x + BALL_SIZE//2) - (self.player_x + PLAYER_WIDTH//2)
            self.ball_dy = -abs(self.ball_dy)
            self.ball_dx = max(-8, min(8, hit_pos // 10))
            # 修正球位置防止卡住
            self.ball_y = self.player_y - BALL_SIZE - 1
        
        # 砖块碰撞检测
        brick_hit = False
        for brick in list(self.bricks):
            if (self.ball_x + BALL_SIZE >= brick['x'] and
                self.ball_x <= brick['x'] + brick['width'] and
                self.ball_y + BALL_SIZE >= brick['y'] and
                self.ball_y <= brick['y'] + brick['height']):
                
                # 砖块被击中
                self.bricks.remove(brick)
                self.score += POINT_PER_BRICK
                
                # 简单反弹逻辑：确定是水平还是垂直碰撞
                # 计算球和砖块中心距离
                ball_center_x = self.ball_x + BALL_SIZE // 2
                ball_center_y = self.ball_y + BALL_SIZE // 2
                brick_center_x = brick['x'] + brick['width'] // 2
                brick_center_y = brick['y'] + brick['height'] // 2
                
                overlap_x = min(abs(ball_center_x - brick['x']), 
                               abs(ball_center_x - (brick['x'] + brick['width'])))
                overlap_y = min(abs(ball_center_y - brick['y']), 
                               abs(ball_center_y - (brick['y'] + brick['height'])))
                
                if overlap_x < overlap_y:
                    self.ball_dx = -self.ball_dx
                else:
                    self.ball_dy = -self.ball_dy
                
                brick_hit = True
                break
        
        # 胜利判定
        if len(self.bricks) == 0:
            self.victory = True

    def draw(self):
        self.screen.fill(BLACK)
        
        # 绘制球拍
        pygame.draw.rect(self.screen, PLAYER_COLOR, 
                        (self.player_x, self.player_y, PLAYER_WIDTH, PLAYER_HEIGHT))
        
        # 绘制小球
        pygame.draw.rect(self.screen, BALL_COLOR, 
                        (self.ball_x, self.ball_y, BALL_SIZE, BALL_SIZE))
        
        # 绘制砖块
        for brick in self.bricks:
            pygame.draw.rect(self.screen, brick['color'], 
                           (brick['x'], brick['y'], brick['width'], brick['height']))
        
        # 绘制HUD信息
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.small_font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (WINDOW_WIDTH - 150, 10))
        
        # 游戏状态信息
        if self.game_over:
            text = self.font.render("GAME OVER", True, RED)
            rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(text, rect)
            restart_text = self.small_font.render("Press R to Restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
            self.screen.blit(restart_text, restart_rect)
        elif self.victory:
            text = self.font.render("YOU WIN!", True, GREEN)
            rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(text, rect)
            restart_text = self.small_font.render("Press R to Restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()