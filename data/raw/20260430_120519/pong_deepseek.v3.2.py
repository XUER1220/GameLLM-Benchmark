import pygame
import sys
import random

# 初始化随机种子
random.seed(42)

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
PADDLE_SPEED = 7
LEFT_PADDLE_X = 30
RIGHT_PADDLE_X = SCREEN_WIDTH - 30 - PADDLE_WIDTH

BALL_SIZE = 18
BALL_INIT_SPEED_X = 5
BALL_INIT_SPEED_Y = 5

WIN_SCORE = 7

# 颜色
BACKGROUND_COLOR = (10, 10, 40)
PADDLE_COLOR = (255, 255, 255)
BALL_COLOR = (255, 255, 255)
NET_COLOR = (60, 60, 100)
TEXT_COLOR = (255, 255, 255)
SCORE_COLOR = (200, 200, 255)

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = 0
    
    def move(self):
        self.rect.y += self.speed
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
    
    def draw(self, screen):
        pygame.draw.rect(screen, PADDLE_COLOR, self.rect, border_radius=3)
        pygame.draw.rect(screen, PADDLE_COLOR, self.rect, width=2, border_radius=3)

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
        self.reset()
    
    def reset(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed_x = BALL_INIT_SPEED_X
        self.speed_y = BALL_INIT_SPEED_Y
        if random.choice([True, False]):
            self.speed_x *= -1
        if random.choice([True, False]):
            self.speed_y *= -1
    
    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        if self.rect.top <= 0:
            self.rect.top = 0
            self.speed_y *= -1
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.speed_y *= -1
    
    def draw(self, screen):
        pygame.draw.ellipse(screen, BALL_COLOR, self.rect)
        pygame.draw.ellipse(screen, BALL_COLOR, self.rect, width=2)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pong Easy")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 36)
        
        self.left_paddle = Paddle(LEFT_PADDLE_X, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.right_paddle = Paddle(RIGHT_PADDLE_X, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
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
                
                if event.key == pygame.K_r:
                    self.restart()
                
                if not self.game_over:
                    if event.key == pygame.K_w:
                        self.left_paddle.speed = -PADDLE_SPEED
                    elif event.key == pygame.K_s:
                        self.left_paddle.speed = PADDLE_SPEED
                    
                    if event.key == pygame.K_UP:
                        self.right_paddle.speed = -PADDLE_SPEED
                    elif event.key == pygame.K_DOWN:
                        self.right_paddle.speed = PADDLE_SPEED
            
            if event.type == pygame.KEYUP:
                if not self.game_over:
                    if event.key in (pygame.K_w, pygame.K_s):
                        self.left_paddle.speed = 0
                    if event.key in (pygame.K_UP, pygame.K_DOWN):
                        self.right_paddle.speed = 0
    
    def check_collisions(self):
        if self.ball.rect.colliderect(self.left_paddle.rect):
            if self.ball.speed_x < 0:
                self.ball.speed_x *= -1
                offset = (self.ball.rect.centery - self.left_paddle.rect.centery) / (PADDLE_HEIGHT / 2)
                self.ball.speed_y = offset * 5
        
        if self.ball.rect.colliderect(self.right_paddle.rect):
            if self.ball.speed_x > 0:
                self.ball.speed_x *= -1
                offset = (self.ball.rect.centery - self.right_paddle.rect.centery) / (PADDLE_HEIGHT / 2)
                self.ball.speed_y = offset * 5
    
    def update(self):
        if self.game_over:
            return
        
        self.left_paddle.move()
        self.right_paddle.move()
        self.ball.move()
        self.check_collisions()
        
        if self.ball.rect.left <= 0:
            self.right_score += 1
            self.check_winner()
            if not self.game_over:
                self.ball.reset()
        
        if self.ball.rect.right >= SCREEN_WIDTH:
            self.left_score += 1
            self.check_winner()
            if not self.game_over:
                self.ball.reset()
    
    def check_winner(self):
        if self.left_score >= WIN_SCORE:
            self.game_over = True
            self.winner = "LEFT PLAYER"
        elif self.right_score >= WIN_SCORE:
            self.game_over = True
            self.winner = "RIGHT PLAYER"
    
    def draw_net(self):
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.rect(self.screen, NET_COLOR, (SCREEN_WIDTH // 2 - 2, y, 4, 20))
    
    def draw_scores(self):
        left_score_text = self.font.render(str(self.left_score), True, SCORE_COLOR)
        right_score_text = self.font.render(str(self.right_score), True, SCORE_COLOR)
        
        self.screen.blit(left_score_text, (SCREEN_WIDTH // 4 - left_score_text.get_width() // 2, 30))
        self.screen.blit(right_score_text, (3 * SCREEN_WIDTH // 4 - right_score_text.get_width() // 2, 30))
    
    def draw_game_over(self):
        if not self.game_over:
            return
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        winner_text = self.font.render(f"{self.winner} WINS!", True, TEXT_COLOR)
        restart_text = self.small_font.render("Press R to Restart", True, TEXT_COLOR)
        
        self.screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
    
    def restart(self):
        self.left_paddle.rect.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.right_paddle.rect.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.ball.reset()
        self.left_score = 0
        self.right_score = 0
        self.game_over = False
        self.winner = ""
    
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_net()
        self.left_paddle.draw(self.screen)
        self.right_paddle.draw(self.screen)
        self.ball.draw(self.screen)
        self.draw_scores()
        self.draw_game_over()
        pygame.display.flip()
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()