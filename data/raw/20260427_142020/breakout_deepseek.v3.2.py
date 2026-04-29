import pygame
import random
import sys

# 初始化配置
pygame.init()
random.seed(42)

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
COLOR_BG = (30, 30, 40)
COLOR_PADDLE = (90, 180, 255)
COLOR_BALL = (255, 230, 100)
COLOR_BRICK = [
    (220, 90, 90),
    (240, 140, 70),
    (220, 200, 80),
    (90, 190, 120),
    (100, 160, 220)
]
COLOR_TEXT = (240, 240, 255)
COLOR_HUD = (200, 220, 255)

# 游戏对象常量
PADDLE_WIDTH = 110
PADDLE_HEIGHT = 18
PADDLE_SPEED = 8
PADDLE_Y = SCREEN_HEIGHT - 40
BALL_SIZE = 16
BALL_INIT_SPEED_X = 4
BALL_INIT_SPEED_Y = -5
BRICK_ROWS = 5
BRICK_COLS = 8
BRICK_WIDTH = 84
BRICK_HEIGHT = 24
BRICK_GAP = 4
BRICK_START_Y = 80
HUD_FONT_SIZE = 24
MESSAGE_FONT_SIZE = 48
LIVES = 3
SCORE_PER_BRICK = 10

class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = PADDLE_Y
        self.speed = PADDLE_SPEED
        self.color = COLOR_PADDLE
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        if direction == "right" and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        self.rect.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=6)

class Ball:
    def __init__(self, paddle):
        self.size = BALL_SIZE
        self.reset(paddle)
        self.color = COLOR_BALL

    def reset(self, paddle):
        self.x = paddle.x + paddle.width // 2 - self.size // 2
        self.y = paddle.y - self.size - 5
        self.speed_x = BALL_INIT_SPEED_X
        self.speed_y = BALL_INIT_SPEED_Y
        self.active = True
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x <= 0 or self.x >= SCREEN_WIDTH - self.size:
            self.speed_x = -self.speed_x
        if self.y <= 0:
            self.speed_y = -self.speed_y
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)

class Brick:
    def __init__(self, x, y, row):
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.x = x
        self.y = y
        self.color = COLOR_BRICK[row % len(COLOR_BRICK)]
        self.visible = True
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if self.visible:
            pygame.draw.rect(screen, self.color, self.rect, border_radius=3)
            pygame.draw.rect(screen, COLOR_BG, self.rect, 2, border_radius=3)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Breakout Medium")
        self.clock = pygame.time.Clock()
        self.font_hud = pygame.font.SysFont(None, HUD_FONT_SIZE)
        self.font_msg = pygame.font.SysFont(None, MESSAGE_FONT_SIZE)
        self.reset_game()

    def reset_game(self):
        self.paddle = Paddle()
        self.ball = Ball(self.paddle)
        self.bricks = []
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = col * (BRICK_WIDTH + BRICK_GAP) + BRICK_GAP
                y = row * (BRICK_HEIGHT + BRICK_GAP) + BRICK_START_Y
                self.bricks.append(Brick(x, y, row))
        self.score = 0
        self.lives = LIVES
        self.game_over = False
        self.game_won = False

    def handle_ball_collisions(self):
        # 球与挡板碰撞
        if self.ball.rect.colliderect(self.paddle.rect) and self.ball.speed_y > 0:
            self.ball.speed_y = -self.ball.speed_y
            offset = (self.ball.rect.centerx - self.paddle.rect.centerx) / (self.paddle.width / 2)
            self.ball.speed_x = offset * 4
            self.ball.y = self.paddle.y - self.ball.size

        # 球与砖块碰撞
        for brick in self.bricks:
            if brick.visible and self.ball.rect.colliderect(brick.rect):
                brick.visible = False
                self.score += SCORE_PER_BRICK
                # 判断从哪个方向碰撞
                if (self.ball.rect.right >= brick.rect.left and self.ball.rect.left <= brick.rect.left and self.ball.speed_x > 0) or \
                   (self.ball.rect.left <= brick.rect.right and self.ball.rect.right >= brick.rect.right and self.ball.speed_x < 0):
                    self.ball.speed_x = -self.ball.speed_x
                else:
                    self.ball.speed_y = -self.ball.speed_y
                break

        # 球落到底部
        if self.ball.y > SCREEN_HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.ball.reset(self.paddle)

        # 检查是否清空所有砖块
        if all(not brick.visible for brick in self.bricks):
            self.game_won = True
            self.game_over = True

    def draw_hud(self):
        score_text = self.font_hud.render(f"Score: {self.score}", True, COLOR_HUD)
        lives_text = self.font_hud.render(f"Lives: {self.lives}", True, COLOR_HUD)
        self.screen.blit(score_text, (20, 20))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 20))

    def draw_message(self):
        if self.game_won:
            msg = self.font_msg.render("You Win!", True, (100, 255, 150))
        else:
            msg = self.font_msg.render("Game Over", True, (255, 120, 100))
        restart_text = self.font_hud.render("Press R to Restart", True, COLOR_TEXT)
        msg_rect = msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        self.screen.blit(msg, msg_rect)
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_r:
                        self.reset_game()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.paddle.move("left")
            if keys[pygame.K_RIGHT]:
                self.paddle.move("right")

            if not self.game_over:
                self.ball.move()
                self.handle_ball_collisions()

            # 绘制
            self.screen.fill(COLOR_BG)
            for brick in self.bricks:
                brick.draw(self.screen)
            self.paddle.draw(self.screen)
            self.ball.draw(self.screen)
            self.draw_hud()
            if self.game_over:
                self.draw_message()

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()