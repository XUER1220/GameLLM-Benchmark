import pygame
import random
import sys

# 固定参数
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GROUND_HEIGHT = 60
GRAVITY = 0.35
FLAP_STRENGTH = -7.5
PIPE_SPEED = 3
PIPE_WIDTH = 80
PIPE_GAP = 170
PIPE_SPAWN_DELAY = 90
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
BIRD_START_X = 160
BIRD_START_Y = 300
random.seed(42)

# 颜色
SKY_BLUE = (135, 206, 235)
GROUND_GREEN = (86, 125, 70)
PIPE_GREEN = (94, 180, 94)
BIRD_YELLOW = (255, 255, 0)
BIRD_ORANGE = (255, 165, 0)
BIRD_EYE = (0, 0, 0)
BIRD_BEAK = (255, 69, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
TEXT_COLOR = (40, 40, 40)

class Bird:
    def __init__(self):
        self.x = BIRD_START_X
        self.y = BIRD_START_Y
        self.vel_y = 0
        self.width = BIRD_WIDTH
        self.height = BIRD_HEIGHT
        self.alive = True
        
    def update(self):
        if not self.alive:
            return
        self.vel_y += GRAVITY
        self.y += self.vel_y
        # 边界检测
        if self.y <= 0 or self.y + self.height >= SCREEN_HEIGHT - GROUND_HEIGHT:
            self.alive = False
    
    def flap(self):
        if self.alive:
            self.vel_y = FLAP_STRENGTH
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        # 身体
        body_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, BIRD_YELLOW, body_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, body_rect, 2, border_radius=10)
        # 头部
        head_center = (self.x + self.width - 10, self.y + self.height//2)
        pygame.draw.circle(screen, BIRD_YELLOW, head_center, 15)
        pygame.draw.circle(screen, BLACK, head_center, 15, 2)
        # 眼睛
        pygame.draw.circle(screen, BIRD_EYE, (head_center[0]+5, head_center[1]-5), 4)
        # 喙
        beak_points = [(head_center[0]+10, head_center[1]), 
                       (head_center[0]+25, head_center[1]-3),
                       (head_center[0]+25, head_center[1]+3)]
        pygame.draw.polygon(screen, BIRD_BEAK, beak_points)
        pygame.draw.polygon(screen, BLACK, beak_points, 2)
        # 翅膀（动态）
        wing_y = self.y + 10 + abs(int(self.vel_y * 2))
        wing_points = [(self.x+5, wing_y), (self.x+30, wing_y-5), (self.x+30, wing_y+5)]
        pygame.draw.polygon(screen, BIRD_ORANGE, wing_points)
        pygame.draw.polygon(screen, BLACK, wing_points, 2)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = PIPE_WIDTH
        self.passed = False
        self.set_gap_position()
        
    def set_gap_position(self):
        min_gap_y = 100
        max_gap_y = SCREEN_HEIGHT - GROUND_HEIGHT - 100 - PIPE_GAP
        self.gap_y = random.randint(min_gap_y, max_gap_y)
    
    def update(self):
        self.x -= PIPE_SPEED
    
    def collide(self, bird_rect):
        top_pipe = pygame.Rect(self.x, 0, self.width, self.gap_y)
        bottom_pipe = pygame.Rect(self.x, self.gap_y + PIPE_GAP, self.width, SCREEN_HEIGHT)
        return bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe)
    
    def draw(self, screen):
        # 上管道
        top_height = self.gap_y
        top_rect = pygame.Rect(self.x, 0, self.width, top_height)
        pygame.draw.rect(screen, PIPE_GREEN, top_rect)
        pygame.draw.rect(screen, BLACK, top_rect, 2)
        # 上管道帽
        cap_rect = pygame.Rect(self.x - 5, top_height - 20, self.width + 10, 20)
        pygame.draw.rect(screen, PIPE_GREEN, cap_rect)
        pygame.draw.rect(screen, BLACK, cap_rect, 2)
        # 下管道
        bottom_y = self.gap_y + PIPE_GAP
        bottom_height = SCREEN_HEIGHT - bottom_y
        bottom_rect = pygame.Rect(self.x, bottom_y, self.width, bottom_height)
        pygame.draw.rect(screen, PIPE_GREEN, bottom_rect)
        pygame.draw.rect(screen, BLACK, bottom_rect, 2)
        # 下管道帽
        cap_rect2 = pygame.Rect(self.x - 5, bottom_y, self.width + 10, 20)
        pygame.draw.rect(screen, PIPE_GREEN, cap_rect2)
        pygame.draw.rect(screen, BLACK, cap_rect2, 2)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)
        self.reset_game()
        
    def reset_game(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.frame_count = 0
        self.game_over = False
        
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
                    self.reset_game()
                if not self.game_over and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                    self.bird.flap()
    
    def update(self):
        if self.game_over:
            return
            
        self.bird.update()
        self.frame_count += 1
        
        # 生成新管道
        if self.frame_count % PIPE_SPAWN_DELAY == 40:
            self.pipes.append(Pipe(SCREEN_WIDTH))
        
        # 更新管道
        for pipe in self.pipes[:]:
            pipe.update()
            if pipe.collide(self.bird.get_rect()):
                self.bird.alive = False
            # 计分
            if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                pipe.passed = True
                self.score += 1
            # 移除屏幕外的管道
            if pipe.x + pipe.width < 0:
                self.pipes.remove(pipe)
        
        # 检查游戏结束
        if not self.bird.alive:
            self.game_over = True
    
    def draw(self):
        # 天空
        self.screen.fill(SKY_BLUE)
        
        # 管道
        for pipe in self.pipes:
            pipe.draw(self.screen)
        
        # 地面
        ground_rect = pygame.Rect(0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT)
        pygame.draw.rect(self.screen, GROUND_GREEN, ground_rect)
        pygame.draw.line(self.screen, BLACK, (0, SCREEN_HEIGHT - GROUND_HEIGHT), 
                         (SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT), 3)
        
        # 鸟
        self.bird.draw(self.screen)
        
        # 分数
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (20, 20))
        
        # 游戏结束提示
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("GAME OVER", True, RED)
            final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.small_font.render("Press R to Restart", True, WHITE)
            
            self.screen.blit(game_over_text, 
                            (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
            self.screen.blit(final_score_text, 
                            (SCREEN_WIDTH//2 - final_score_text.get_width()//2, SCREEN_HEIGHT//2 - 20))
            self.screen.blit(restart_text, 
                            (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        
        # 操作提示
        if not self.game_over:
            hint_text = self.small_font.render("SPACE / UP KEY: Flap", True, TEXT_COLOR)
            self.screen.blit(hint_text, (SCREEN_WIDTH - hint_text.get_width() - 20, 20))
        
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