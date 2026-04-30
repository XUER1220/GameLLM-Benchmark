import pygame
import random
import sys

random.seed(42)

WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.35
JUMP_SPEED = -7.5
PIPE_SPEED = 3
PIPE_WIDTH = 80
GAP_HEIGHT = 170
PIPE_FREQ = 90
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
BIRD_START_X = 160
BIRD_START_Y = 300
GROUND_HEIGHT = 80
MIN_Y = 100
MAX_Y = HEIGHT - GROUND_HEIGHT - 100

BACKGROUND_COLOR = (113, 197, 207)
GROUND_COLOR = (222, 184, 135)
BIRD_COLOR = (255, 204, 0)
PIPE_COLOR = (96, 174, 78)
TEXT_COLOR = (30, 30, 30)
GAME_OVER_BG_COLOR = (0, 0, 0, 180)

class Bird:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.x = BIRD_START_X
        self.y = BIRD_START_Y
        self.velocity = 0
        self.rect = pygame.Rect(0, 0, BIRD_WIDTH, BIRD_HEIGHT)
        self.update_rect()
    
    def update_rect(self):
        self.rect.center = (self.x, self.y)
    
    def jump(self):
        self.velocity = JUMP_SPEED
    
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.update_rect()
    
    def draw(self, screen):
        pygame.draw.ellipse(screen, BIRD_COLOR, self.rect)
        pygame.draw.ellipse(screen, (200, 150, 0), self.rect, 2)
        
        eye_center = (self.x + BIRD_WIDTH//4, self.y - BIRD_HEIGHT//6)
        pygame.draw.circle(screen, (30, 30, 30), eye_center, 4)
        
        beak_points = [(self.x + BIRD_WIDTH//2, self.y), 
                       (self.x + BIRD_WIDTH//2 + 15, self.y - 5),
                       (self.x + BIRD_WIDTH//2 + 15, self.y + 5)]
        pygame.draw.polygon(screen, (255, 128, 0), beak_points)

class Pipe:
    def __init__(self, x, gap_y):
        self.x = x
        self.gap_y = gap_y
        self.top_rect = pygame.Rect(x, 0, PIPE_WIDTH, gap_y - GAP_HEIGHT//2)
        self.bottom_rect = pygame.Rect(x, gap_y + GAP_HEIGHT//2, PIPE_WIDTH, HEIGHT)
        self.passed = False
    
    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x
    
    def draw(self, screen):
        pygame.draw.rect(screen, PIPE_COLOR, self.top_rect)
        pygame.draw.rect(screen, (70, 140, 60), self.top_rect, 2)
        
        pygame.draw.rect(screen, PIPE_COLOR, self.bottom_rect)
        pygame.draw.rect(screen, (70, 140, 60), self.bottom_rect, 2)
        
        cap_width = PIPE_WIDTH + 10
        top_cap = pygame.Rect(self.x - 5, self.top_rect.bottom - 10, cap_width, 20)
        bottom_cap = pygame.Rect(self.x - 5, self.bottom_rect.top - 10, cap_width, 20)
        pygame.draw.rect(screen, (80, 160, 70), top_cap)
        pygame.draw.rect(screen, (80, 160, 70), bottom_cap)
        pygame.draw.rect(screen, (70, 140, 60), top_cap, 2)
        pygame.draw.rect(screen, (70, 140, 60), bottom_cap, 2)

def draw_ground(screen):
    ground_rect = pygame.Rect(0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT)
    pygame.draw.rect(screen, GROUND_COLOR, ground_rect)
    
    for i in range(20):
        x = (i * 40) % (WIDTH + 40)
        y = HEIGHT - GROUND_HEIGHT
        pygame.draw.line(screen, (200, 150, 100), (x, y), (x + 20, y), 2)

def draw_hud(screen, score, game_over):
    font = pygame.font.SysFont('arial', 40)
    score_text = font.render(f'Score: {score}', True, TEXT_COLOR)
    screen.blit(score_text, (10, 10))
    
    title_font = pygame.font.SysFont('arial', 60, True)
    title_text = title_font.render('Flappy Bird Easy', True, TEXT_COLOR)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 20))
    
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(GAME_OVER_BG_COLOR)
        screen.blit(overlay, (0, 0))
        
        game_over_font = pygame.font.SysFont('arial', 72, True)
        game_over_text = game_over_font.render('GAME OVER', True, (255, 255, 255))
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 120))
        
        score_font = pygame.font.SysFont('arial', 50)
        final_score_text = score_font.render(f'Final Score: {score}', True, (255, 255, 255))
        screen.blit(final_score_text, (WIDTH//2 - final_score_text.get_width()//2, HEIGHT//2 - 30))
        
        restart_font = pygame.font.SysFont('arial', 36)
        restart_text = restart_font.render('Press R to Restart, ESC to Quit', True, (255, 255, 255))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 60))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Flappy Bird Easy")
    clock = pygame.time.Clock()
    
    bird = Bird()
    pipes = []
    frame_count = 0
    score = 0
    game_over = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                if not game_over and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                    bird.jump()
                
                if game_over and event.key == pygame.K_r:
                    bird.reset()
                    pipes.clear()
                    frame_count = 0
                    score = 0
                    game_over = False
        
        if not game_over:
            bird.update()
            
            if frame_count % PIPE_FREQ == 30:
                gap_y = random.randint(MIN_Y, MAX_Y)
                pipes.append(Pipe(WIDTH, gap_y))
            
            for pipe in pipes[:]:
                pipe.update()
                
                if not pipe.passed and pipe.x + PIPE_WIDTH < bird.x:
                    pipe.passed = True
                    score += 1
                
                if pipe.x + PIPE_WIDTH < 0:
                    pipes.remove(pipe)
            
            pipes = [pipe for pipe in pipes if pipe.x + PIPE_WIDTH > 0]
            
            if bird.y < 0 or bird.y > HEIGHT - GROUND_HEIGHT:
                game_over = True
            
            for pipe in pipes:
                if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                    game_over = True
            
            frame_count += 1
        
        screen.fill(BACKGROUND_COLOR)
        
        for pipe in pipes:
            pipe.draw(screen)
        
        draw_ground(screen)
        bird.draw(screen)
        draw_hud(screen, score, game_over)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()