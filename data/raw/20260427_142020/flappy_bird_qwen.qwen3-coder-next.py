import pygame
import sys
import random

# 常量定义
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
BIRD_X = 160
BIRD_Y_START = 300
GRAVITY = 0.35
FLAP_VELOCITY = -7.5
PIPE_WIDTH = 80
PIPE_GAP = 170
PIPE_SPEED = 3
PIPE_INTERVAL = 90
PIPE_MIN_Y = 100
PIPE_MAX_Y = WINDOW_HEIGHT - 100 - PIPE_GAP
GROUND_HEIGHT = 50

# 颜色定义
SKY_COLOR = (135, 206, 235)
BIRD_COLOR = (255, 215, 0)
PIPE_COLOR = (34, 139, 34)
PIPE_BORDER_COLOR = (0, 100, 0)
GROUND_COLOR = (139, 69, 19)
HUD_COLOR = (255, 255, 255)
TEXT_COLOR = (0, 0, 0)
GAME_OVER_COLOR = (255, 0, 0)

class Bird:
    def __init__(self):
        self.x = BIRD_X
        self.y = BIRD_Y_START
        self.velocity = 0
        self.width = BIRD_WIDTH
        self.height = BIRD_HEIGHT
        self.mask = None  # 无碰撞掩码支持（矩形检测）

    def flap(self):
        self.velocity = FLAP_VELOCITY

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def draw(self, screen):
        pygame.draw.rect(screen, BIRD_COLOR, (self.x, self.y, self.width, self.height))
        # 简单的眼睛
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + self.width - 8), int(self.y + 8)), 3)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x + self.width - 6), int(self.y + 6)), 1)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Pipe:
    def __init__(self, x, top_height):
        self.x = x
        self.top_height = top_height
        self.bottom_y = top_height + PIPE_GAP
        self.bottom_height = WINDOW_HEIGHT - GROUND_HEIGHT - self.bottom_y
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self, screen):
        # 上管道
        pygame.draw.rect(screen, PIPE_COLOR, (self.x, 0, PIPE_WIDTH, self.top_height))
        pygame.draw.rect(screen, PIPE_BORDER_COLOR, (self.x, 0, PIPE_WIDTH, self.top_height), 2)
        
        # 下管道
        pygame.draw.rect(screen, PIPE_COLOR, (self.x, self.bottom_y, PIPE_WIDTH, self.bottom_height))
        pygame.draw.rect(screen, PIPE_BORDER_COLOR, (self.x, self.bottom_y, PIPE_WIDTH, self.bottom_height), 2)

    def get_rects(self):
        top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.top_height)
        bottom_rect = pygame.Rect(self.x, self.bottom_y, PIPE_WIDTH, self.bottom_height)
        return top_rect, bottom_rect

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Flappy Bird Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # 随机种子
        random.seed(42)

    def init_game(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.frame_count = 0
        self.game_active = True
        self.first_pipe_ready = False
        self.game_over = False

    def spawn_pipe(self):
        # 确保管道间距合理
        center = random.randint(PIPE_MIN_Y + PIPE_GAP // 2, PIPE_MAX_Y + PIPE_GAP // 2)
        top_height = center - PIPE_GAP // 2
        
        pipe = Pipe(WINDOW_WIDTH, top_height)
        self.pipes.append(pipe)

    def check_collisions(self):
        bird_rect = self.bird.get_rect()

        # 地面和天花板碰撞
        if self.bird.y <= 0 or self.bird.y + self.bird.height >= WINDOW_HEIGHT - GROUND_HEIGHT:
            return True

        # 管道碰撞
        for pipe in self.pipes:
            top_rect, bottom_rect = pipe.get_rects()
            if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                return True

        return False

    def update(self):
        if not self.game_active:
            return

        self.frame_count += 1
        
        # 更新鸟的位置
        self.bird.update()

        # 管道生成逻辑：第一次延迟启动，然后按固定间隔生成
        if not self.first_pipe_ready and self.frame_count > 30:
            self.spawn_pipe()
            self.first_pipe_ready = True
        elif self.frame_count % PIPE_INTERVAL == 0 and self.frame_count > 30:
            self.spawn_pipe()

        # 更新管道位置
        for pipe in self.pipes:
            pipe.update()

        # 删除超出屏幕的管道
        self.pipes = [p for p in self.pipes if p.x + PIPE_WIDTH > 0]

        # 分数检测
        for pipe in self.pipes:
            if not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.x:
                pipe.passed = True
                self.score += 1

        # 碰撞检测
        if self.check_collisions():
            self.game_active = False
            self.game_over = True

    def draw(self):
        self.screen.fill(SKY_COLOR)
        
        # 绘制地面
        pygame.draw.rect(self.screen, GROUND_COLOR, (0, WINDOW_HEIGHT - GROUND_HEIGHT, WINDOW_WIDTH, GROUND_HEIGHT))
        
        # 绘制管道
        for pipe in self.pipes:
            pipe.draw(self.screen)
        
        # 绘制鸟
        self.bird.draw(self.screen)
        
        # HUD（分数、标题等）
        title_surface = self.font.render("Flappy Bird Easy", True, HUD_COLOR)
        self.screen.blit(title_surface, (WINDOW_WIDTH // 2 - title_surface.get_width() // 2, 20))
        
        # 当前分数
        score_surface = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_surface, (10, 10))
        
        # 游戏结束信息
        if self.game_over:
            game_over_surface = self.font.render("GAME OVER", True, GAME_OVER_COLOR)
            score_end_surface = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            restart_surface = self.small_font.render("Press 'R' to Restart or 'ESC' to Quit", True, TEXT_COLOR)
            
            self.screen.blit(game_over_surface, (WINDOW_WIDTH // 2 - game_over_surface.get_width() // 2, WINDOW_HEIGHT // 2 - 60))
            self.screen.blit(score_end_surface, (WINDOW_WIDTH // 2 - score_end_surface.get_width() // 2, WINDOW_HEIGHT // 2 - 20))
            self.screen.blit(restart_surface, (WINDOW_WIDTH // 2 - restart_surface.get_width() // 2, WINDOW_HEIGHT // 2 + 20))

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r and self.game_over:
                    self.init_game()
                elif event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if self.game_active:
                        self.bird.flap()
                    elif not self.game_active and not self.game_over:
                        self.init_game()
        return True

    def run(self):
        self.init_game()
        
        while True:
            if not self.handle_events():
                pygame.quit()
                sys.exit()
            
            self.update()
            self.draw()
            
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()