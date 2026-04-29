import pygame
import random
import sys

pygame.init()
random.seed(42)

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
PADDLE_SPEED = 7

BALL_SIZE = 18
BALL_INIT_SPEED_X = 5
BALL_INIT_SPEED_Y = 5

WIN_SCORE = 7

# 颜色
BACKGROUND = (15, 25, 35)
ELEMENT_COLOR = (220, 235, 245)
NET_COLOR = (60, 80, 100)
TEXT_COLOR = (240, 245, 255)
HIGHLIGHT = (100, 200, 255)
SCORE_COLOR = (180, 220, 255)

class Paddle:
    def __init__(self, x):
        self.rect = pygame.Rect(x, SCREEN_HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.score = 0
    
    def move(self, direction):
        if direction == "up":
            self.rect.y = max(0, self.rect.y - PADDLE_SPEED)
        elif direction == "down":
            self.rect.y = min(SCREEN_HEIGHT - PADDLE_HEIGHT, self.rect.y + PADDLE_SPEED)

class Ball:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.rect = pygame.Rect(SCREEN_WIDTH//2 - BALL_SIZE//2, SCREEN_HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)
        self.speed_x = BALL_INIT_SPEED_X if random.choice([True, False]) else -BALL_INIT_SPEED_X
        self.speed_y = BALL_INIT_SPEED_Y if random.choice([True, False]) else -BALL_INIT_SPEED_Y
    
    def update(self, left_paddle, right_paddle):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # 上下边界反弹
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.speed_y = -self.speed_y
        
        # 球拍碰撞反弹
        if self.rect.colliderect(left_paddle.rect) and self.speed_x < 0:
            self.speed_x = -self.speed_x
            offset = (self.rect.centery - left_paddle.rect.centery) / (PADDLE_HEIGHT/2)
            self.speed_y += offset * 2
            # 限制垂直速度防止过强
            if self.speed_y > 8: self.speed_y = 8
            elif self.speed_y < -8: self.speed_y = -8
            
        if self.rect.colliderect(right_paddle.rect) and self.speed_x > 0:
            self.speed_x = -self.speed_x
            offset = (self.rect.centery - right_paddle.rect.centery) / (PADDLE_HEIGHT/2)
            self.speed_y += offset * 2
            if self.speed_y > 8: self.speed_y = 8
            elif self.speed_y < -8: self.speed_y = -8
        
        # 出界检测
        if self.rect.left <= 0:
            right_paddle.score += 1
            return "right_scored"
        if self.rect.right >= SCREEN_WIDTH:
            left_paddle.score += 1
            return "left_scored"
        return None

def draw_net(surface):
    for y in range(0, SCREEN_HEIGHT, 24):
        pygame.draw.rect(surface, NET_COLOR, (SCREEN_WIDTH//2 - 2, y, 4, 12))

def draw_score(surface, font_big, font_small, left_score, right_score, winner=None):
    # 左侧分数
    score_surf = font_big.render(str(left_score), True, SCORE_COLOR)
    surface.blit(score_surf, (SCREEN_WIDTH//4 - score_surf.get_width()//2, 30))
    
    # 右侧分数
    score_surf = font_big.render(str(right_score), True, SCORE_COLOR)
    surface.blit(score_surf, (SCREEN_WIDTH*3//4 - score_surf.get_width()//2, 30))
    
    # 胜负信息
    if winner is not None:
        win_text = "Left Player Wins!" if winner == "left" else "Right Player Wins!"
        win_surf = font_big.render(win_text, True, HIGHLIGHT)
        surface.blit(win_surf, (SCREEN_WIDTH//2 - win_surf.get_width()//2, SCREEN_HEIGHT//2 - 60))
        
        restart_surf = font_small.render("Press R to Restart", True, ELEMENT_COLOR)
        surface.blit(restart_surf, (SCREEN_WIDTH//2 - restart_surf.get_width()//2, SCREEN_HEIGHT//2 + 20))

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pong Easy")
    clock = pygame.time.Clock()
    
    font_big = pygame.font.SysFont("Arial", 64, bold=True)
    font_small = pygame.font.SysFont("Arial", 36)
    info_font = pygame.font.SysFont("Arial", 20)
    
    left_paddle = Paddle(30)
    right_paddle = Paddle(SCREEN_WIDTH - 30 - PADDLE_WIDTH)
    ball = Ball()
    
    winner = None
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    # 重置游戏
                    left_paddle = Paddle(30)
                    right_paddle = Paddle(SCREEN_WIDTH - 30 - PADDLE_WIDTH)
                    ball.reset()
                    winner = None
        
        if winner is None:
            # 球拍控制
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                left_paddle.move("up")
            if keys[pygame.K_s]:
                left_paddle.move("down")
            if keys[pygame.K_UP]:
                right_paddle.move("up")
            if keys[pygame.K_DOWN]:
                right_paddle.move("down")
            
            # 更新小球
            score_event = ball.update(left_paddle, right_paddle)
            if score_event:
                ball.reset()
                if left_paddle.score >= WIN_SCORE:
                    winner = "left"
                elif right_paddle.score >= WIN_SCORE:
                    winner = "right"
        
        # 绘制
        screen.fill(BACKGROUND)
        draw_net(screen)
        
        pygame.draw.rect(screen, ELEMENT_COLOR, left_paddle.rect)
        pygame.draw.rect(screen, ELEMENT_COLOR, right_paddle.rect)
        pygame.draw.ellipse(screen, HIGHLIGHT, ball.rect)
        
        # 绘制控制说明
        left_ctrl = info_font.render("W / S", True, NET_COLOR)
        right_ctrl = info_font.render("↑ / ↓", True, NET_COLOR)
        screen.blit(left_ctrl, (50, SCREEN_HEIGHT - 40))
        screen.blit(right_ctrl, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 40))
        
        draw_score(screen, font_big, font_small, left_paddle.score, right_paddle.score, winner)
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()