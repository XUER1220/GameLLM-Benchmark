import pygame
import random
import sys

# 初始化
pygame.init()
random.seed(42)

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BACKGROUND_COLOR = (15, 15, 35)
PADDLE_COLOR = (70, 180, 255)
BALL_COLOR = (255, 220, 70)
BRICK_COLORS = [
    (255, 50, 50),
    (255, 150, 50),
    (255, 220, 50),
    (50, 220, 50),
    (50, 180, 255)
]
TEXT_COLOR = (230, 230, 230)
GAMEOVER_COLOR = (255, 80, 80)
WIN_COLOR = (80, 255, 130)

# 游戏对象参数
PADDLE_WIDTH = 110
PADDLE_HEIGHT = 18
PADDLE_SPEED = 8
BALL_SIZE = 16
BALL_INIT_SPEED_X = 4
BALL_INIT_SPEED_Y = -5
BRICK_ROWS = 5
BRICK_COLS = 8
BRICK_WIDTH = 84
BRICK_HEIGHT = 24
BRICK_GAP = 4
LIVES = 3
SCORE_PER_BRICK = 10

# 计算砖块区域起始位置
BRICK_AREA_WIDTH = BRICK_COLS * (BRICK_WIDTH + BRICK_GAP) - BRICK_GAP
BRICK_AREA_HEIGHT = BRICK_ROWS * (BRICK_HEIGHT + BRICK_GAP) - BRICK_GAP
BRICK_AREA_X = (SCREEN_WIDTH - BRICK_AREA_WIDTH) // 2
BRICK_AREA_Y = 80

class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 40
        self.speed = PADDLE_SPEED
    
    def move(self, direction):
        if direction == "left":
            self.x = max(0, self.x - self.speed)
        elif direction == "right":
            self.x = min(SCREEN_WIDTH - self.width, self.x + self.speed)
    
    def draw(self, screen):
        pygame.draw.rect(screen, PADDLE_COLOR, (self.x, self.y, self.width, self.height), 0, 5)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Ball:
    def __init__(self, paddle):
        self.size = BALL_SIZE
        self.reset(paddle)
    
    def reset(self, paddle):
        self.x = paddle.x + paddle.width // 2 - self.size // 2
        self.y = paddle.y - self.size
        self.speed_x = BALL_INIT_SPEED_X if random.random() > 0.5 else -BALL_INIT_SPEED_X
        self.speed_y = BALL_INIT_SPEED_Y
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        
        # 左右边界反弹
        if self.x <= 0 or self.x >= SCREEN_WIDTH - self.size:
            self.speed_x = -self.speed_x
            self.x = max(0, min(self.x, SCREEN_WIDTH - self.size))
        
        # 上边界反弹
        if self.y <= 0:
            self.speed_y = -self.speed_y
            self.y = 0
    
    def draw(self, screen):
        pygame.draw.ellipse(screen, BALL_COLOR, (self.x, self.y, self.size, self.size))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
    
    def check_paddle_collision(self, paddle):
        ball_rect = self.get_rect()
        paddle_rect = paddle.get_rect()
        
        if ball_rect.colliderect(paddle_rect) and self.speed_y > 0:
            # 根据击中球拍的位置调整反弹角度
            relative_x = (self.x + self.size/2) - (paddle.x + paddle.width/2)
            factor = relative_x / (paddle.width/2)
            self.speed_x = factor * 6
            self.speed_y = -abs(self.speed_y)
            self.y = paddle.y - self.size
            return True
        return False
    
    def check_brick_collision(self, bricks):
        ball_rect = self.get_rect()
        for brick in bricks:
            if brick.active and ball_rect.colliderect(brick.rect):
                brick.active = False
                
                # 确定从哪边反弹
                if (self.x + self.size//2 < brick.rect.left and self.speed_x > 0) or \
                   (self.x + self.size//2 > brick.rect.right and self.speed_x < 0):
                    self.speed_x = -self.speed_x
                else:
                    self.speed_y = -self.speed_y
                
                return brick
        return None
    
    def is_out_of_bounds(self):
        return self.y > SCREEN_HEIGHT

class Brick:
    def __init__(self, x, y, color):
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = color
        self.active = True
    
    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, self.color, self.rect, 0, 3)
            pygame.draw.rect(screen, (min(255, self.color[0]+30), 
                                      min(255, self.color[1]+30), 
                                      min(255, self.color[2]+30)), 
                             self.rect, 2, 3)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Breakout Medium")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)
        self.reset_game()
    
    def reset_game(self):
        self.paddle = Paddle()
        self.ball = Ball(self.paddle)
        self.bricks = []
        self.score = 0
        self.lives = LIVES
        self.game_over = False
        self.win = False
        
        # 创建砖块
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = BRICK_AREA_X + col * (BRICK_WIDTH + BRICK_GAP)
                y = BRICK_AREA_Y + row * (BRICK_HEIGHT + BRICK_GAP)
                color = BRICK_COLORS[row % len(BRICK_COLORS)]
                self.bricks.append(Brick(x, y, color))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
                if (self.game_over or self.win) and event.key == pygame.K_r:
                    self.reset_game()
        
        if not (self.game_over or self.win):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.paddle.move("left")
            if keys[pygame.K_RIGHT]:
                self.paddle.move("right")
    
    def update(self):
        if self.game_over or self.win:
            return
        
        self.ball.update()
        
        # 检查球拍碰撞
        self.ball.check_paddle_collision(self.paddle)
        
        # 检查砖块碰撞
        hit_brick = self.ball.check_brick_collision(self.bricks)
        if hit_brick:
            self.score += SCORE_PER_BRICK
        
        # 检查球是否出界
        if self.ball.is_out_of_bounds():
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.ball.reset(self.paddle)
        
        # 检查是否胜利
        bricks_left = sum(1 for brick in self.bricks if brick.active)
        if bricks_left == 0:
            self.win = True
    
    def draw_hud(self):
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        lives_text = self.font.render(f"Lives: {self.lives}", True, TEXT_COLOR)
        self.screen.blit(score_text, (20, 20))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 20))
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        if self.win:
            text = self.font.render("YOU WIN!", True, WIN_COLOR)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
            self.screen.blit(text, text_rect)
        else:
            text = self.font.render("GAME OVER", True, GAMEOVER_COLOR)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
            self.screen.blit(text, text_rect)
        
        restart_text = self.small_font.render("Press R to Restart", True, TEXT_COLOR)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        self.screen.blit(restart_text, restart_rect)
        
        esc_text = self.small_font.render("ESC to Quit", True, TEXT_COLOR)
        esc_rect = esc_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
        self.screen.blit(esc_text, esc_rect)
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            
            # 绘制
            self.screen.fill(BACKGROUND_COLOR)
            
            # 绘制砖块
            for brick in self.bricks:
                brick.draw(self.screen)
            
            # 绘制球拍和小球
            self.paddle.draw(self.screen)
            self.ball.draw(self.screen)
            
            # 绘制HUD
            self.draw_hud()
            
            # 绘制游戏结束/胜利画面
            if self.game_over or self.win:
                self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()