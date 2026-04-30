import pygame
import random
import sys

# 顶部常量定义
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
BIRD_X_POS = 160
BIRD_INITIAL_Y = 300
GRAVITY = 0.35
FLAP_STRENGTH = -7.5
PIPE_WIDTH = 80
PIPE_GAP = 170
PIPE_SPEED = 3
PIPE_SPAWN_INTERVAL = 90
MIN_PIPE_Y = 100
MAX_PIPE_Y = WINDOW_HEIGHT - 150 - PIPE_GAP

# 颜色定义
BACKGROUND_COLOR = (135, 206, 235)
PIPE_COLOR = (34, 139, 34)
PIPE_BORDER_COLOR = (0, 100, 0)
GROUND_COLOR = (139, 69, 19)
GROUND_BORDER_COLOR = (101, 67, 33)
BIRD_COLOR = (255, 215, 0)
BIRD_BORDER_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
SCORE_COLOR = (255, 255, 0)

class Bird:
    def __init__(self):
        self.rect = pygame.Rect(BIRD_X_POS, BIRD_INITIAL_Y, BIRD_WIDTH, BIRD_HEIGHT)
        self.velocity = 0
        
    def update(self):
        self.velocity += GRAVITY
        self.rect.y += self.velocity
        
    def flap(self):
        self.velocity = FLAP_STRENGTH
        
    def draw(self, screen):
        pygame.draw.rect(screen, BIRD_COLOR, self.rect)
        pygame.draw.rect(screen, BIRD_BORDER_COLOR, self.rect, 2)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = PIPE_WIDTH
        self.scored = False
        
        # 生成随机中间位置，保证空隙可通行
        random.seed(42)  # 保证可重现性
        center_y = random.randint(MIN_PIPE_Y, MAX_PIPE_Y)
        
        self.top_height = center_y - PIPE_GAP // 2
        self.bottom_y = center_y + PIPE_GAP // 2
        self.bottom_height = WINDOW_HEIGHT - self.bottom_y
        
        self.top_rect = pygame.Rect(x, 0, self.width, self.top_height)
        self.bottom_rect = pygame.Rect(x, self.bottom_y, self.width, self.bottom_height)
        
    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x
        
    def draw(self, screen):
        # Top pipe
        pygame.draw.rect(screen, PIPE_COLOR, self.top_rect)
        pygame.draw.rect(screen, PIPE_BORDER_COLOR, self.top_rect, 3)
        # Bottom pipe
        pygame.draw.rect(screen, PIPE_COLOR, self.bottom_rect)
        pygame.draw.rect(screen, PIPE_BORDER_COLOR, self.bottom_rect, 3)

def draw_ground(screen):
    ground_height = 40
    ground_top = WINDOW_HEIGHT - ground_height
    pygame.draw.rect(screen, GROUND_COLOR, (0, ground_top, WINDOW_WIDTH, ground_height))
    pygame.draw.rect(screen, GROUND_BORDER_COLOR, (0, ground_top, WINDOW_WIDTH, ground_height), 2)
    
def draw_hud(screen, font, score, game_over=False, final_score=0):
    title_font = pygame.font.SysFont(None, 48)
    score_font = pygame.font.SysFont(None, 36)
    
    # Draw title
    title_text = title_font.render("Flappy Bird Easy", True, TEXT_COLOR)
    screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 20))
    
    # Draw current score
    if not game_over:
        score_text = score_font.render(f"Score: {score}", True, SCORE_COLOR)
        screen.blit(score_text, (10, 10))
    
    if game_over:
        game_over_text = title_font.render("Game Over!", True, TEXT_COLOR)
        screen.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
        
        final_score_text = score_font.render(f"Final Score: {final_score}", True, TEXT_COLOR)
        screen.blit(final_score_text, (WINDOW_WIDTH // 2 - final_score_text.get_width() // 2, WINDOW_HEIGHT // 2 + 10))
        
        restart_text = score_font.render("Press R to Restart", True, TEXT_COLOR)
        screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2 + 60))

def main():
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Flappy Bird Easy")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    
    # Game state variables
    running = True
    game_over = False
    score = 0
    frame_count = 0
    
    # Initialize game objects
    bird = Bird()
    pipes = []
    
    # Initial random setup
    random.seed(42)
    
    # Main game loop
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    # Restart game
                    bird = Bird()
                    pipes = []
                    score = 0
                    frame_count = 0
                    game_over = False
                elif event.key in (pygame.K_SPACE, pygame.K_UP):
                    if not game_over:
                        bird.flap()
        
        # Game logic
        if not game_over:
            # Update bird
            bird.update()
            
            # Pipe spawning
            frame_count += 1
            if frame_count % PIPE_SPAWN_INTERVAL == 0:
                pipes.append(Pipe(WINDOW_WIDTH))
                
            # Generate first pipe earlier if needed
            if len(pipes) == 0 and frame_count == 60:
                pipes.append(Pipe(WINDOW_WIDTH + 100))
                
            # Update and check pipes
            for pipe in pipes[:]:
                pipe.update()
                
                # Check collisions with pipes
                if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                    game_over = True
                    
                # Remove off-screen pipes
                if pipe.x + pipe.width < 0:
                    pipes.remove(pipe)
                    
                # Score counting
                if not pipe.scored and pipe.x + pipe.width < bird.rect.x:
                    pipe.scored = True
                    score += 1
                    
            # Check boundaries
            if bird.rect.top <= 0 or bird.rect.bottom >= WINDOW_HEIGHT:
                game_over = True
                
            # Update ground collision at bottom of screen
            ground_height = 40
            if bird.rect.bottom >= WINDOW_HEIGHT - ground_height:
                game_over = True
                
        # Drawing
        screen.fill(BACKGROUND_COLOR)
        
        # Draw ground
        draw_ground(screen)
        
        # Draw pipes
        for pipe in pipes:
            pipe.draw(screen)
            
        # Draw bird
        bird.draw(screen)
        
        # Draw HUD
        draw_hud(screen, font, score, game_over=game_over, final_score=score)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()