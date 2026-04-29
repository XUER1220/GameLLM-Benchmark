import pygame
import sys
import random

# 顶部常量
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# 物理参数
GRAVITY = 0.35
FLAP_STRENGTH = -7.5
PIPE_SPEED = 3
PIPE_WIDTH = 80
PIPE_GAP_HEIGHT = 170
PIPE_SPAWN_INTERVAL = 90

# 位置与尺寸
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
BIRD_START_X = 160
BIRD_START_Y = 300

# 颜色
BACKGROUND_COLOR = (135, 206, 235)
BIRD_COLOR = (255, 235, 59)
PIPE_COLOR = (34, 139, 34)
PIPE_BORDER_COLOR = (0, 100, 0)
GROUND_COLOR = (222, 184, 135)
TEXT_COLOR = (255, 255, 255)
SHADOW_COLOR = (0, 0, 0)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Flappy Bird Easy")
    clock = pygame.time.Clock()
    font_large = pygame.font.SysFont(None, 64)
    font_small = pygame.font.SysFont(None, 32)
    
    # 随机种子保持可重现性
    random.seed(42)
    
    # 游戏状态
    bird_y = BIRD_START_Y
    bird_velocity = 0
    bird_rect = pygame.Rect(BIRD_START_X, bird_y, BIRD_WIDTH, BIRD_HEIGHT)
    
    pipes = []
    score = 0
    frames_since_last_pipe = 0
    game_state = "start"  # start, playing, gameover
    
    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r and game_state == "gameover":
                    # Reset game
                    bird_y = BIRD_START_Y
                    bird_velocity = 0
                    bird_rect.y = bird_y
                    pipes = []
                    score = 0
                    frames_since_last_pipe = 0
                    game_state = "start"
                elif event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if game_state == "start":
                        game_state = "playing"
                    elif game_state == "playing":
                        bird_velocity = FLAP_STRENGTH
                    elif game_state == "gameover":
                        # Restart on keypress after Game Over
                        bird_y = BIRD_START_Y
                        bird_velocity = 0
                        bird_rect.y = bird_y
                        pipes = []
                        score = 0
                        frames_since_last_pipe = 0
                        game_state = "start"
        
        # Update logic
        if game_state == "playing":
            # Bird physics
            bird_velocity += GRAVITY
            bird_y += bird_velocity
            bird_rect.y = bird_y
            
            # Prevent bird from going out of bounds
            if bird_rect.top <= 0 or bird_rect.bottom >= WINDOW_HEIGHT:
                game_state = "gameover"
            
            # Pipe generation
            frames_since_last_pipe += 1
            if frames_since_last_pipe >= PIPE_SPAWN_INTERVAL:
                frames_since_last_pipe = 0
                # Generate pipe with safe center position
                min_center = 100 + PIPE_GAP_HEIGHT // 2
                max_center = WINDOW_HEIGHT - 100 - PIPE_GAP_HEIGHT // 2
                center_y = random.randint(min_center, max_center)
                
                # Top pipe
                top_pipe = pygame.Rect(WINDOW_WIDTH, 0, PIPE_WIDTH, center_y - PIPE_GAP_HEIGHT // 2)
                # Bottom pipe
                bottom_pipe = pygame.Rect(WINDOW_WIDTH, center_y + PIPE_GAP_HEIGHT // 2, PIPE_WIDTH, WINDOW_HEIGHT - (center_y + PIPE_GAP_HEIGHT // 2))
                
                pipes.append({"top": top_pipe, "bottom": bottom_pipe, "passed": False})
            
            # Move pipes and check collisions
            for pipe in pipes[:]:
                pipe["top"].x -= PIPE_SPEED
                pipe["bottom"].x -= PIPE_SPEED
                
                # Remove off-screen pipes
                if pipe["top"].right < 0:
                    pipes.remove(pipe)
                    continue
                
                # Collision detection
                if bird_rect.colliderect(pipe["top"]) or bird_rect.colliderect(pipe["bottom"]):
                    game_state = "gameover"
                
                # Score increment
                if not pipe["passed"] and bird_rect.left > pipe["top"].right:
                    pipe["passed"] = True
                    score += 1
            
            # Ground check
            if bird_rect.bottom >= WINDOW_HEIGHT:
                game_state = "gameover"
        
        # Drawing
        screen.fill(BACKGROUND_COLOR)
        
        # Draw ground
        ground_height = 30
        pygame.draw.rect(screen, GROUND_COLOR, (0, WINDOW_HEIGHT - ground_height, WINDOW_WIDTH, ground_height))
        
        # Draw pipes
        for pipe in pipes:
            # Top pipe
            top_pipe = pipe["top"]
            pygame.draw.rect(screen, PIPE_COLOR, top_pipe)
            pygame.draw.rect(screen, PIPE_BORDER_COLOR, top_pipe, 2)
            
            # Bottom pipe
            bottom_pipe = pipe["bottom"]
            pygame.draw.rect(screen, PIPE_COLOR, bottom_pipe)
            pygame.draw.rect(screen, PIPE_BORDER_COLOR, bottom_pipe, 2)
        
        # Draw bird
        pygame.draw.rect(screen, BIRD_COLOR, bird_rect)
        pygame.draw.rect(screen, (0, 0, 0), bird_rect, 2)
        
        # Draw HUD
        # Title
        title_text = font_large.render("Flappy Bird Easy", True, TEXT_COLOR)
        title_shadow = font_large.render("Flappy Bird Easy", True, SHADOW_COLOR)
        screen.blit(title_shadow, (WINDOW_WIDTH // 2 - title_text.get_width() // 2 + 3, 43))
        screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 40))
        
        # Score
        score_text = font_small.render(f"Score: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (20, 100))
        
        # UI depending on state
        if game_state == "start":
            start_text = font_small.render("Press SPACE or UP to Start", True, TEXT_COLOR)
            screen.blit(start_text, (WINDOW_WIDTH // 2 - start_text.get_width() // 2, WINDOW_HEIGHT // 2 + 50))
        
        elif game_state == "gameover":
            # Game Over
            gameover_text = font_large.render("Game Over", True, TEXT_COLOR)
            gameover_shadow = font_large.render("Game Over", True, SHADOW_COLOR)
            screen.blit(gameover_shadow, (WINDOW_WIDTH // 2 - gameover_text.get_width() // 2 + 3, WINDOW_HEIGHT // 2 - 60 + 3))
            screen.blit(gameover_text, (WINDOW_WIDTH // 2 - gameover_text.get_width() // 2, WINDOW_HEIGHT // 2 - 60))
            
            final_score_text = font_small.render(f"Final Score: {score}", True, TEXT_COLOR)
            screen.blit(final_score_text, (WINDOW_WIDTH // 2 - final_score_text.get_width() // 2, WINDOW_HEIGHT // 2 + 10))
            
            restart_text = font_small.render("Press R to Restart", True, TEXT_COLOR)
            screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2 + 60))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()