import pygame
import sys
import random

# 固定参数
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BALL_SIZE = 18
PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
PADDLE_SPEED = 7
BALL_SPEED_X = 5
BALL_SPEED_Y = 5
WINNING_SCORE = 7

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# 初始化 Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong Easy")
clock = pygame.time.Clock()

# 随机种子
random.seed(42)

def draw_text(text, x, y, font_size=36, color=WHITE):
    font = pygame.font.Font(None, font_size)
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    rect.center = (x, y)
    screen.blit(surface, rect)

def reset_ball():
    ball.rect.x = (SCREEN_WIDTH - BALL_SIZE) // 2
    ball.rect.y = (SCREEN_HEIGHT - BALL_SIZE) // 2
    direction = random.choice([-1, 1])
    ball.speed_x = BALL_SPEED_X * direction
    ball.speed_y = BALL_SPEED_Y * random.choice([-1, 1])

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
        self.speed_x = 0
        self.speed_y = 0
        reset_ball()

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # 碰到上下边界反弹
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.speed_y = -self.speed_y

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

class Paddle:
    def __init__(self, x, color=WHITE):
        self.rect = pygame.Rect(x, (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.color = color
        self.speed_y = 0

    def update(self, keys, up_key, down_key):
        self.speed_y = 0
        if keys[up_key]:
            self.speed_y = -PADDLE_SPEED
        if keys[down_key]:
            self.speed_y = PADDLE_SPEED
        
        self.rect.y += self.speed_y

        # 防止移出屏幕
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)

# 初始化游戏对象
left_paddle = Paddle(30)
right_paddle = Paddle(SCREEN_WIDTH - 30 - PADDLE_WIDTH, WHITE)
ball = Ball()

left_score = 0
right_score = 0
game_over = False
winner = ""

# 游戏循环
while True:
    # 处理事件
    keys = pygame.key.get_pressed()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if game_over and event.key == pygame.K_r:
                left_score = 0
                right_score = 0
                game_over = False
                winner = ""
                reset_ball()

    if not game_over:
        # 更新球拍和球
        left_paddle.update(keys, pygame.K_w, pygame.K_s)
        right_paddle.update(keys, pygame.K_UP, pygame.K_DOWN)
        ball.update()

        # 球与球拍碰撞检测
        # 左球拍碰撞
        if ball.rect.colliderect(left_paddle.rect) and ball.speed_x < 0:
            ball.speed_x = -ball.speed_x
            # 将球推出球拍避免卡住
            ball.rect.left = left_paddle.rect.right
        
        # 右球拍碰撞
        if ball.rect.colliderect(right_paddle.rect) and ball.speed_x > 0:
            ball.speed_x = -ball.speed_x
            # 将球推出球拍避免卡住
            ball.rect.right = right_paddle.rect.left

        # 得分检测
        if ball.rect.left <= 0:
            right_score += 1
            if right_score >= WINNING_SCORE:
                game_over = True
                winner = "Right Player"
            else:
                reset_ball()
        elif ball.rect.right >= SCREEN_WIDTH:
            left_score += 1
            if left_score >= WINNING_SCORE:
                game_over = True
                winner = "Left Player"
            else:
                reset_ball()

    # 绘制画面
    screen.fill(BLACK)
    
    # 绘制中线
    pygame.draw.aaline(screen, GRAY, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))
    
    # 绘制球拍和球
    left_paddle.draw()
    right_paddle.draw()
    ball.draw()
    
    # 绘制分数
    draw_text(f"{left_score}", SCREEN_WIDTH // 4, 50)
    draw_text(f"{right_score}", 3 * SCREEN_WIDTH // 4, 50)
    
    # 游戏结束提示
    if game_over:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        draw_text(f"Winner: {winner}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40, font_size=48)
        draw_text("Press R to Restart", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)

    pygame.display.flip()
    clock.tick(FPS)