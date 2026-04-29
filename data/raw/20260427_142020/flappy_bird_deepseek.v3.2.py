import pygame
import random
import sys

# 初始化随机种子
random.seed(42)

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.35
FLAP_STRENGTH = -7.5
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
BIRD_START_X = 160
BIRD_START_Y = 300
PIPE_WIDTH = 80
PIPE_GAP = 170
PIPE_SPEED = 3
PIPE_FREQUENCY = 90
GROUND_HEIGHT = 50
PIPE_MIN_HEIGHT = 100
PIPE_MAX_HEIGHT = SCREEN_HEIGHT - GROUND_HEIGHT - PIPE_MIN_HEIGHT

# 颜色
BACKGROUND = (135, 206, 235)
BIRD_COLOR = (255, 255, 0)
PIPE_COLOR = (0, 180, 0)
GROUND_COLOR = (222, 184, 135)
TEXT_COLOR = (255, 255, 255)
HUD_BG_COLOR = (0, 0, 0, 128)

class Bird:
    def __init__(self):
        self.x = BIRD_START_X
        self.y = BIRD_START_Y
        self.vel_y = 0
        self.rect = pygame.Rect(self.x - BIRD_WIDTH//2, self.y - BIRD_HEIGHT//2, BIRD_WIDTH, BIRD_HEIGHT)
    
    def flap(self):
        self.vel_y = FLAP_STRENGTH
    
    def update(self):
        self.vel_y += GRAVITY
        self.y += self.vel_y
        self.rect.center = (self.x, self.y)
    
    def draw(self, screen):
        pygame.draw.ellipse(screen, BIRD_COLOR, self.rect)
        # 眼睛
        eye_radius = 4
        eye_x = self.x + BIRD_WIDTH//4
        eye_y = self.y - BIRD_HEIGHT//4
        pygame.draw.circle(screen, (0, 0, 0), (int(eye_x), int(eye_y)), eye_radius)
        # 喙
        beak_points = [(self.x + BIRD_WIDTH//2, self.y), 
                       (self.x + BIRD_WIDTH//2 + 10, self.y - 5),
                       (self.x + BIRD_WIDTH//2 + 10, self.y + 5)]
        pygame.draw.polygon(screen, (255, 150, 0), beak_points)
    
    def check_collision(self, pipes):
        # 屏幕边界碰撞
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT - GROUND_HEIGHT:
            return True
        # 管道碰撞
        for pipe in pipes:
            if self.rect.colliderect(pipe.top_rect) or self.rect.colliderect(pipe.bottom_rect):
                return True
        return False

class Pipe:
    def __init__(self, x):
        self.x = x
        self.passed = False
        self.gap_y = random.randint(PIPE_MIN_HEIGHT, PIPE_MAX_HEIGHT)
        top_height = self.gap_y - PIPE_GAP//2
        bottom_y = self.gap_y + PIPE_GAP//2
        self.top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, top_height)
        self.bottom_rect = pygame.Rect(self.x, bottom_y, PIPE_WIDTH, SCREEN_HEIGHT - bottom_y)
    
    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x
    
    def draw(self, screen):
        pygame.draw.rect(screen, PIPE_COLOR, self.top_rect)
        pygame.draw.rect(screen, PIPE_COLOR, self.bottom_rect)
        # 添加管道帽子
        cap_offset = 10
        top_cap = pygame.Rect(self.x - cap_offset//2, self.top_rect.height, PIPE_WIDTH + cap_offset, 20)
        bottom_cap = pygame.Rect(self.x - cap_offset//2, self.bottom_rect.y - 20, PIPE_WIDTH + cap_offset, 20)
        pygame.draw.rect(screen, (0, 150, 0), top_cap)
        pygame.draw.rect(screen, (0, 150, 0), bottom_cap)
    
    def is_offscreen(self):
        return self.x < -PIPE_WIDTH

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird Easy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 32)
        self.small_font = pygame.font.SysFont('Arial', 24)
        self.reset()
    
    def reset(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.frame_count = 0
        self.pipe_spawn_timer = 0
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if not self.game_over and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                    self.bird.flap()
                if event.key == pygame.K_r:
                    self.reset()
    
    def update(self):
        if not self.game_over:
            self.bird.update()
            
            # 生成新管道
            self.pipe_spawn_timer += 1
            if self.pipe_spawn_timer >= PIPE_FREQUENCY:
                self.pipes.append(Pipe(SCREEN_WIDTH))
                self.pipe_spawn_timer = 0
            
            # 更新管道
            for pipe in self.pipes[:]:
                pipe.update()
                if pipe.is_offscreen():
                    self.pipes.remove(pipe)
                
                # 计分
                if not pipe.passed and pipe.x < self.bird.x:
                    pipe.passed = True
                    self.score += 1
            
            # 碰撞检测
            if self.bird.check_collision(self.pipes):
                self.game_over = True
    
    def draw(self):
        self.screen.fill(BACKGROUND)
        
        # 绘制管道
        for pipe in self.pipes:
            pipe.draw(self.screen)
        
        # 绘制地面
        pygame.draw.rect(self.screen, GROUND_COLOR, 
                        (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        
        # 绘制鸟
        self.bird.draw(self.screen)
        
        # 绘制分数HUD
        score_text = self.font.render(f'Score: {self.score}', True, TEXT_COLOR)
        score_bg = pygame.Surface((score_text.get_width() + 20, score_text.get_height() + 10), pygame.SRCALPHA)
        score_bg.fill(HUD_BG_COLOR)
        self.screen.blit(score_bg, (10, 10))
        self.screen.blit(score_text, (20, 15))
        
        # 游戏结束提示
        if self.game_over:
            # 半透明覆盖层
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render('Game Over', True, TEXT_COLOR)
            final_score_text = self.font.render(f'Final Score: {self.score}', True, TEXT_COLOR)
            restart_text = self.small_font.render('Press R to Restart', True, TEXT_COLOR)
            
            self.screen.blit(game_over_text, 
                           (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
            self.screen.blit(final_score_text, 
                           (SCREEN_WIDTH//2 - final_score_text.get_width()//2, SCREEN_HEIGHT//2 - 20))
            self.screen.blit(restart_text, 
                           (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        
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