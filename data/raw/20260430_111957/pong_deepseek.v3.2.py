import pygame
import sys
import random

# 固定随机种子
random.seed(42)

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BG_COLOR = (10, 20, 30)
ELEMENT_COLOR = (200, 230, 255)
ACCENT_COLOR = (255, 180, 100)
TEXT_COLOR = (230, 240, 255)

PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
PADDLE_SPEED = 7
LEFT_PADDLE_X = 30
RIGHT_PADDLE_X = SCREEN_WIDTH - 30 - PADDLE_WIDTH

BALL_SIZE = 18
BALL_INIT_SPEED_X = 5
BALL_INIT_SPEED_Y = 5

WIN_SCORE = 7

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)

    def move(self, dy):
        new_y = self.rect.y + dy
        if new_y < 0:
            new_y = 0
        elif new_y > SCREEN_HEIGHT - PADDLE_HEIGHT:
            new_y = SCREEN_HEIGHT - PADDLE_HEIGHT
        self.rect.y = new_y

    def draw(self, surface):
        pygame.draw.rect(surface, ELEMENT_COLOR, self.rect, border_radius=8)
        inner = pygame.Rect(self.rect.x + 4, self.rect.y + 4, self.rect.width - 8, self.rect.height - 8)
        pygame.draw.rect(surface, ACCENT_COLOR, inner, border_radius=4)

class Ball:
    def __init__(self):
        self.reset()
        self.rect = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)

    def reset(self):
        self.x = SCREEN_WIDTH // 2 - BALL_SIZE // 2
        self.y = SCREEN_HEIGHT // 2 - BALL_SIZE // 2
        self.speed_x = BALL_INIT_SPEED_X * (1 if random.choice([True, False]) else -1)
        self.speed_y = BALL_INIT_SPEED_Y * (1 if random.choice([True, False]) else -1)
        self.rect.x = self.x
        self.rect.y = self.y

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # 上下边界反弹
        if self.rect.top <= 0:
            self.rect.top = 0
            self.speed_y = abs(self.speed_y)
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.speed_y = -abs(self.speed_y)

    def check_collision(self, left_paddle, right_paddle):
        if self.rect.colliderect(left_paddle.rect) and self.speed_x < 0:
            self.speed_x = abs(self.speed_x)
            offset = (self.rect.centery - left_paddle.rect.centery) / (PADDLE_HEIGHT / 2)
            self.speed_y = offset * BALL_INIT_SPEED_Y
        elif self.rect.colliderect(right_paddle.rect) and self.speed_x > 0:
            self.speed_x = -abs(self.speed_x)
            offset = (self.rect.centery - right_paddle.rect.centery) / (PADDLE_HEIGHT / 2)
            self.speed_y = offset * BALL_INIT_SPEED_Y

    def draw(self, surface):
        pygame.draw.circle(surface, ACCENT_COLOR, self.rect.center, BALL_SIZE // 2)
        pygame.draw.circle(surface, ELEMENT_COLOR, self.rect.center, BALL_SIZE // 2 - 3)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pong Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 36, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 24)
        self.left_paddle = Paddle(LEFT_PADDLE_X, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.right_paddle = Paddle(RIGHT_PADDLE_X, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ball = Ball()
        self.left_score = 0
        self.right_score = 0
        self.game_over = False
        self.winner = None

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

    def update(self):
        if self.game_over:
            return

        # 球拍控制
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.left_paddle.move(-PADDLE_SPEED)
        if keys[pygame.K_s]:
            self.left_paddle.move(PADDLE_SPEED)
        if keys[pygame.K_UP]:
            self.right_paddle.move(-PADDLE_SPEED)
        if keys[pygame.K_DOWN]:
            self.right_paddle.move(PADDLE_SPEED)

        # 球移动和碰撞
        self.ball.move()
        self.ball.check_collision(self.left_paddle, self.right_paddle)

        # 得分检测
        if self.ball.rect.left <= 0:
            self.right_score += 1
            self.ball.reset()
            self.check_win()
        elif self.ball.rect.right >= SCREEN_WIDTH:
            self.left_score += 1
            self.ball.reset()
            self.check_win()

    def check_win(self):
        if self.left_score >= WIN_SCORE:
            self.game_over = True
            self.winner = "LEFT"
        elif self.right_score >= WIN_SCORE:
            self.game_over = True
            self.winner = "RIGHT"

    def restart(self):
        self.left_score = 0
        self.right_score = 0
        self.game_over = False
        self.winner = None
        self.left_paddle.rect.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.right_paddle.rect.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.ball.reset()

    def draw(self):
        self.screen.fill(BG_COLOR)

        # 中线虚线
        for y in range(0, SCREEN_HEIGHT, 20):
            pygame.draw.rect(self.screen, (40, 60, 80), (SCREEN_WIDTH // 2 - 2, y, 4, 10))

        # 球拍和球
        self.left_paddle.draw(self.screen)
        self.right_paddle.draw(self.screen)
        self.ball.draw(self.screen)

        # 分数显示
        left_score_text = self.font.render(str(self.left_score), True, TEXT_COLOR)
        right_score_text = self.font.render(str(self.right_score), True, TEXT_COLOR)
        self.screen.blit(left_score_text, (SCREEN_WIDTH // 4 - left_score_text.get_width() // 2, 30))
        self.screen.blit(right_score_text, (SCREEN_WIDTH * 3 // 4 - right_score_text.get_width() // 2, 30))

        # 胜利提示
        if self.game_over:
            win_text = f"{self.winner} WINS!"
            win_surface = self.font.render(win_text, True, ACCENT_COLOR)
            self.screen.blit(win_surface, (SCREEN_WIDTH // 2 - win_surface.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            restart_text = self.small_font.render("Press R to Restart", True, ELEMENT_COLOR)
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

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