import pygame
import random
import sys

# 固定参数
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 游戏对象参数
PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
BALL_SIZE = 18
PADDLE_SPEED = 7
BALL_SPEED_X = 5
BALL_SPEED_Y = 5

# 颜色定义
BG_COLOR = (15, 15, 30)
PADDLE_COLOR = (100, 200, 255)
BALL_COLOR = (255, 255, 200)
NET_COLOR = (60, 60, 90)
TEXT_COLOR = (230, 230, 255)
WIN_COLOR = (255, 200, 100)
HINT_COLOR = (180, 180, 220)

# 随机种子
random.seed(42)

class Paddle:
    def __init__(self, x, y, up_key, down_key, is_left=True):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.up_key = up_key
        self.down_key = down_key
        self.is_left = is_left
        self.score = 0

    def move(self, keys):
        if keys[self.up_key] and self.rect.top > 0:
            self.rect.y -= PADDLE_SPEED
        if keys[self.down_key] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += PADDLE_SPEED

    def draw(self, screen):
        pygame.draw.rect(screen, PADDLE_COLOR, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2,
                                 SCREEN_HEIGHT // 2 - BALL_SIZE // 2,
                                 BALL_SIZE, BALL_SIZE)
        self.reset()

    def reset(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.vx = BALL_SPEED_X
        self.vy = BALL_SPEED_Y
        if random.choice([True, False]):
            self.vx = -self.vx

    def update(self, left_paddle, right_paddle):
        self.rect.x += self.vx
        self.rect.y += self.vy

        # 上下边界反弹
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vy = -self.vy
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vy = -self.vy

        # 球拍碰撞
        if self.rect.colliderect(left_paddle.rect) and self.vx < 0:
            self.rect.left = left_paddle.rect.right
            self.vx = -self.vx
        elif self.rect.colliderect(right_paddle.rect) and self.vx > 0:
            self.rect.right = right_paddle.rect.left
            self.vx = -self.vx

        # 出界检测
        if self.rect.left <= 0:
            right_paddle.score += 1
            return 'right'
        elif self.rect.right >= SCREEN_WIDTH:
            left_paddle.score += 1
            return 'left'
        return None

    def draw(self, screen):
        pygame.draw.ellipse(screen, BALL_COLOR, self.rect)
        pygame.draw.ellipse(screen, (255, 255, 255), self.rect, 2)

def draw_net(screen):
    for y in range(0, SCREEN_HEIGHT, 30):
        pygame.draw.rect(screen, NET_COLOR, (SCREEN_WIDTH // 2 - 2, y, 4, 15))

def draw_scores(screen, left_score, right_score):
    font = pygame.font.SysFont('consolas', 48)
    left_text = font.render(str(left_score), True, TEXT_COLOR)
    right_text = font.render(str(right_score), True, TEXT_COLOR)
    screen.blit(left_text, (SCREEN_WIDTH // 4 - left_text.get_width() // 2, 30))
    screen.blit(right_text, (SCREEN_WIDTH * 3 // 4 - right_text.get_width() // 2, 30))

def draw_winner(screen, winner):
    font = pygame.font.SysFont('consolas', 64)
    text = font.render(f'{winner} WINS!', True, WIN_COLOR)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

def draw_restart_hint(screen):
    font = pygame.font.SysFont('consolas', 32)
    text = font.render('Press R to Restart', True, HINT_COLOR)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 30))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Pong Easy')
    clock = pygame.time.Clock()

    left_paddle = Paddle(20, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, pygame.K_w, pygame.K_s)
    right_paddle = Paddle(SCREEN_WIDTH - 20 - PADDLE_WIDTH,
                          SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2,
                          pygame.K_UP, pygame.K_DOWN, is_left=False)
    ball = Ball()
    game_over = False
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
                if event.key == pygame.K_r and game_over:
                    left_paddle.score = 0
                    right_paddle.score = 0
                    ball.reset()
                    game_over = False
                    winner = None

        keys = pygame.key.get_pressed()
        if not game_over:
            left_paddle.move(keys)
            right_paddle.move(keys)
            result = ball.update(left_paddle, right_paddle)
            if result:
                ball.reset()
                if left_paddle.score >= 7:
                    game_over = True
                    winner = 'LEFT'
                elif right_paddle.score >= 7:
                    game_over = True
                    winner = 'RIGHT'

        screen.fill(BG_COLOR)
        draw_net(screen)
        left_paddle.draw(screen)
        right_paddle.draw(screen)
        ball.draw(screen)
        draw_scores(screen, left_paddle.score, right_paddle.score)

        if game_over and winner:
            draw_winner(screen, winner)
            draw_restart_hint(screen)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()