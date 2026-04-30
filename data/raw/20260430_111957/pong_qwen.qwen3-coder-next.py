import pygame
import random

# 固定常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
BALL_SIZE = 18
PADDLE_SPEED = 7
BALL_SPEED_X = 5
BALL_SPEED_Y = 5
WIN_SCORE = 7

# 颜色常量
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (50, 205, 50)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pong Easy")
        self.clock = pygame.time.Clock()
        random.seed(42)
        self.running = True
        self.reset_game()

    def reset_game(self):
        self.left_score = 0
        self.right_score = 0
        self.game_over = False
        self.reset_ball()

    def reset_ball(self):
        self.ball_x = SCREEN_WIDTH // 2 - BALL_SIZE // 2
        self.ball_y = SCREEN_HEIGHT // 2 - BALL_SIZE // 2
        
        # 随机决定左右方向（但种子固定）
        direction = random.choice([-1, 1])
        self.ball_dx = direction * BALL_SPEED_X
        self.ball_dy = BALL_SPEED_Y
        if random.random() < 0.5:
            self.ball_dy = -self.ball_dy

    def update(self):
        if self.game_over:
            return

        # 球拍移动
        keys = pygame.key.get_pressed()
        
        # 左侧球拍：W/S
        if keys[pygame.K_w] and self.left_paddle_y > 0:
            self.left_paddle_y -= PADDLE_SPEED
        if keys[pygame.K_s] and self.left_paddle_y < SCREEN_HEIGHT - PADDLE_HEIGHT:
            self.left_paddle_y += PADDLE_SPEED
        
        # 右侧球拍：上/下方向键
        if keys[pygame.K_UP] and self.right_paddle_y > 0:
            self.right_paddle_y -= PADDLE_SPEED
        if keys[pygame.K_DOWN] and self.right_paddle_y < SCREEN_HEIGHT - PADDLE_HEIGHT:
            self.right_paddle_y += PADDLE_SPEED

        # 更新球位置
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # 上下边界反弹
        if self.ball_y <= 0 or self.ball_y + BALL_SIZE >= SCREEN_HEIGHT:
            self.ball_dy = -self.ball_dy

        # 左边界（左侧球拍处理）
        left_paddle_rect = pygame.Rect(20, self.left_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)
        right_paddle_rect = pygame.Rect(SCREEN_WIDTH - 20 - PADDLE_WIDTH, self.right_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)
        ball_rect = pygame.Rect(self.ball_x, self.ball_y, BALL_SIZE, BALL_SIZE)

        # 左侧球拍碰撞检测
        if ball_rect.colliderect(left_paddle_rect) and self.ball_dx < 0:
            self.ball_dx = abs(self.ball_dx)
            # 确保球不会"卡"在球拍内
            self.ball_x = left_paddle_rect.right + 1

        # 右侧球拍碰撞检测
        if ball_rect.colliderect(right_paddle_rect) and self.ball_dx > 0:
            self.ball_dx = -abs(self.ball_dx)
            # 确保球不会"卡"在球拍内
            self.ball_x = right_paddle_rect.left - BALL_SIZE

        # 得分检测
        if self.ball_x < 0:
            self.right_score += 1
            if self.right_score >= WIN_SCORE:
                self.game_over = True
                self.winner = "Right Player"
            else:
                self.reset_ball()
        elif self.ball_x > SCREEN_WIDTH:
            self.left_score += 1
            if self.left_score >= WIN_SCORE:
                self.game_over = True
                self.winner = "Left Player"
            else:
                self.reset_ball()

    def draw(self):
        self.screen.fill(BLACK)
        
        # 画中线
        for y in range(0, SCREEN_HEIGHT, 20):
            pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH // 2 - 2, y, 4, 10))
        
        # 画球拍
        left_paddle_rect = pygame.Rect(20, self.left_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)
        right_paddle_rect = pygame.Rect(SCREEN_WIDTH - 20 - PADDLE_WIDTH, self.right_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)
        pygame.draw.rect(self.screen, WHITE, left_paddle_rect)
        pygame.draw.rect(self.screen, WHITE, right_paddle_rect)
        
        # 画球
        pygame.draw.rect(self.screen, WHITE, (self.ball_x, self.ball_y, BALL_SIZE, BALL_SIZE))
        
        # 显示分数
        font = pygame.font.SysFont(None, 64)
        score_text = font.render(f"{self.left_score}   {self.right_score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 20))
        
        # 游戏结束显示
        if self.game_over:
            font = pygame.font.SysFont(None, 48)
            win_text = font.render(f"{self.winner} Wins!", True, GREEN)
            self.screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            
            restart_text = font.render("Press R to Restart", True, WHITE)
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 30))

        pygame.display.flip()

    def run(self):
        # 初始化球拍位置
        self.left_paddle_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.right_paddle_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r:
                        self.reset_game()
                        self.left_paddle_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
                        self.right_paddle_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()