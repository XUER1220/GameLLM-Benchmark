import pygame
import sys
import random

# 常量定义
WIDTH, HEIGHT = 800, 600
FPS = 60
Bird_WIDTH, Bird_HEIGHT = 40, 30
Bird_X, Bird_Y_INIT = 160, 300
GRAVITY = 0.35
FLAP_STRENGTH = -7.5
PIPE_SPEED = 3
PIPE_WIDTH = 80
PIPE_GAP = 170
PIPE_SPAWN_RATE = 90
MIN_PIPE_Y = 100
MAX_PIPE_Y = 430

# 颜色定义
BACKGROUND_COLOR = (135, 206, 235)
GROUND_COLOR = (160, 82, 45)
BIRD_COLOR = (255, 215, 0)
PIPE_COLOR = (0, 128, 0)
TEXT_COLOR = (255, 255, 255)

# 初始化pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Easy")
clock = pygame.time.Clock()
font_large = pygame.font.SysFont(None, 64)
font_small = pygame.font.SysFont(None, 32)

class Bird:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.rect = pygame.Rect(Bird_X, Bird_Y_INIT, Bird_WIDTH, Bird_HEIGHT)
        self.velocity = 0
        self.passed_pipes = []
        self.score = 0
    
    def flap(self):
        self.velocity = FLAP_STRENGTH
    
    def update(self):
        self.velocity += GRAVITY
        self.rect.y += self.velocity
        
        # 地面/天花板碰撞检测
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            return True
        return False

    def draw(self, screen):
        pygame.draw.rect(screen, BIRD_COLOR, self.rect)

class Pipe:
    def __init__(self, x, gap_center_y):
        self.x = x
        self.gap_center_y = gap_center_y
        self.top_height = gap_center_y - PIPE_GAP // 2
        self.bottom_y = gap_center_y + PIPE_GAP // 2
        self.passed = False
        
    def update(self):
        self.x -= PIPE_SPEED
        
    def draw(self, screen):
        # 上管道
        pygame.draw.rect(screen, PIPE_COLOR, (self.x, 0, PIPE_WIDTH, self.top_height))
        # 下管道
        bottom_pipe_height = HEIGHT - self.bottom_y
        pygame.draw.rect(screen, PIPE_COLOR, (self.x, self.bottom_y, PIPE_WIDTH, bottom_pipe_height))
    
    def check_collision(self, bird):
        if bird.rect.right > self.x and bird.rect.left < self.x + PIPE_WIDTH:
            if bird.rect.top < self.top_height or bird.rect.bottom > self.bottom_y:
                return True
        return False

def create_pipe():
    gap_center_y = random.randint(MIN_PIPE_Y, MAX_PIPE_Y)
    return Pipe(WIDTH, gap_center_y)

def draw_text_center(text, font, y_offset=0):
    text_surface = font.render(text, True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(text_surface, text_rect)

def main():
    random.seed(42)
    
    bird = Bird()
    pipes = []
    frame_count = 0
    score = 0
    game_state = "start"  # start, playing, game_over
    
    # 初始设置：延迟生成第一组管道
    first_pipe_delay = 60
    
    while True:
        # 处理输入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r and game_state == "game_over":
                    bird.reset()
                    pipes = []
                    frame_count = 0
                    game_state = "start"
                elif event.key == pygame.K_r and game_state == "playing":
                    bird.reset()
                    pipes = []
                    frame_count = 0
                    score = 0
                    game_state = "start"
                elif event.key in (pygame.K_SPACE, pygame.K_UP):
                    if game_state == "start":
                        game_state = "playing"
                        bird.flap()
                    elif game_state == "playing":
                        bird.flap()
        
        # 游戏更新逻辑
        if game_state == "playing":
            frame_count += 1
            
            # 更新鸟的位置
            if bird.update():
                game_state = "game_over"
            
            # 管道生成
            if frame_count >= first_pipe_delay and (frame_count - first_pipe_delay) % PIPE_SPAWN_RATE == 0:
                pipes.append(create_pipe())
                first_pipe_delay = 0  # 后续稳定生成
            
            # 更新管道
            for pipe in pipes[:]:
                pipe.update()
                
                # 碰撞检测
                if pipe.check_collision(bird):
                    game_state = "game_over"
                
                # 分数更新
                if not pipe.passed and bird.rect.left > pipe.x + PIPE_WIDTH:
                    pipe.passed = True
                    score += 1
                    bird.score = score
                
                # 移除屏幕外的管道
                if pipe.x + PIPE_WIDTH < 0:
                    pipes.remove(pipe)
        
        # 绘制
        screen.fill(BACKGROUND_COLOR)
        
        # 绘制地面（装饰条）
        pygame.draw.rect(screen, GROUND_COLOR, (0, HEIGHT - 30, WIDTH, 30))
        
        # 绘制管道
        for pipe in pipes:
            pipe.draw(screen)
        
        # 绘制鸟
        bird.draw(screen)
        
        # HUD：显示当前分数
        score_text = font_small.render(f"Score: {score if game_state == 'playing' else bird.score}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))
        
        # 状态显示
        if game_state == "start":
            draw_text_center("Flappy Bird", font_large, -120)
            draw_text_center("Press Space/Up to Start", font_small, 0)
        elif game_state == "game_over":
            draw_text_center("Game Over", font_large, -60)
            final_score_text = font_small.render(f"Final Score: {bird.score}", True, TEXT_COLOR)
            final_score_rect = final_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
            screen.blit(final_score_text, final_score_rect)
            draw_text_center("Press R to Restart", font_small, 80)
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()