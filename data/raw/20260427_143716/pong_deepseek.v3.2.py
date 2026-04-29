import pygame
import random
import sys

# 设置随机种子
random.seed(42)

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
PADDLE_SPEED = 7

BALL_SIZE = 18
BALL_SPEED_X = 5
BALL_SPEED_Y = 5

WIN_SCORE = 7

# 颜色定义
BACKGROUND_COLOR = (15, 15, 30)
PADDLE_COLOR = (70, 200, 255)
BALL_COLOR = (255, 255, 180)
NET_COLOR = (60, 60, 80, 128)
TEXT_COLOR = (230, 230, 255)
SCORE_COLOR = (255, 255, 200)
WIN_COLOR = (255, 180, 100)

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = PADDLE_SPEED
        
    def move(self, dy):
        self.rect.y += dy * self.speed
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - PADDLE_HEIGHT))
        
    def draw(self, screen):
        pygame.draw.rect(screen, PADDLE_COLOR, self.rect, border_radius=8)

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
        self.reset()
        
    def reset(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed_x = BALL_SPEED_X
        self.speed_y = BALL_SPEED_Y
        if random.choice([True, False]):
            self.speed_x = -self.speed_x
        
    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # 上下边界反弹
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.speed_y = -self.speed_y
            self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - BALL_SIZE))
            
    def check_collision(self, left_paddle, right_paddle):
        # 左球拍碰撞
        if self.speed_x < 0 and self.rect.colliderect(left_paddle.rect):
            self.rect.left = left_paddle.rect.right
            self.speed_x = -self.speed_x
        # 右球拍碰撞
        elif self.speed_x > 0 and self.rect.colliderect(right_paddle.rect):
            self.rect.right = right_paddle.rect.left
            self.speed_x = -self.speed_x
            
    def is_out_of_bounds(self):
        return self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH
        
    def draw(self, screen):
        pygame.draw.ellipse(screen, BALL_COLOR, self.rect)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pong Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 32)
        
        self.left_paddle = Paddle(30, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.right_paddle = Paddle(SCREEN_WIDTH - 30 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ball = Ball()
        
        self.left_score = 0
        self.right_score = 0
        self.game_over = False
        self.winner = ""
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r and self.game_over:
                    self.restart()
        
        # 键盘控制
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.left_paddle.move(-1)
        if keys[pygame.K_s]:
            self.left_paddle.move(1)
        if keys[pygame.K_UP]:
            self.right_paddle.move(-1)
        if keys[pygame.K_DOWN]:
            self.right_paddle.move(1)
            
    def update(self):
        if self.game_over:
            return
            
        self.ball.move()
        self.ball.check_collision(self.left_paddle, self.right_paddle)
        
        # 越界得分
        if self.ball.is_out_of_bounds():
            if self.ball.rect.left <= 0:
                self.right_score += 1
            elif self.ball.rect.right >= SCREEN_WIDTH:
                self.left_score += 1
                
            if self.left_score >= WIN_SCORE:
                self.game_over = True
                self.winner = "LEFT PLAYER"
            elif self.right_score >= WIN_SCORE:
                self.game_over = True
                self.winner = "RIGHT PLAYER"
            else:
                self.ball.reset()
        
    def draw_net(self):
        for y in range(0, SCREEN_HEIGHT, 30):
            pygame.draw.rect(self.screen, NET_COLOR, (SCREEN_WIDTH // 2 - 2, y, 4, 20), border_radius=2)
            
    def draw_scores(self):
        left_score_text = self.font.render(str(self.left_score), True, SCORE_COLOR)
        right_score_text = self.font.render(str(self.right_score), True, SCORE_COLOR)
        self.screen.blit(left_score_text, (SCREEN_WIDTH // 4, 30))
        self.screen.blit(right_score_text, (SCREEN_WIDTH * 3 // 4 - right_score_text.get_width(), 30))
        
    def draw_winner(self):
        if self.game_over:
            win_text = self.font.render(f"{self.winner} WINS!", True, WIN_COLOR)
            self.screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            
            restart_text = self.small_font.render("Press R to Restart", True, TEXT_COLOR)
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2))
            
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_net()
        self.left_paddle.draw(self.screen)
        self.right_paddle.draw(self.screen)
        self.ball.draw(self.screen)
        self.draw_scores()
        self.draw_winner()
        pygame.display.flip()
        
    def restart(self):
        self.left_paddle.rect.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.right_paddle.rect.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.ball.reset()
        self.left_score = 0
        self.right_score = 0
        self.game_over = False
        self.winner = ""
        
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()