import pygame
import random

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
BALL_SIZE = 18
PADDLE_SPEED = 7
BALL_SPEED_X = 5
BALL_SPEED_Y = 5
WINNING_SCORE = 7
BACKGROUND_COLOR = (0, 0, 0)
PADDLE_COLOR = (255, 255, 255)
BALL_COLOR = (255, 255, 255)
TEXT_COLOR = (255, 255, 255)
LINE_COLOR = (255, 255, 255)

random.seed(42)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pong Easy")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 48)

def create_text_surface(text, font_obj, color):
    return font_obj.render(text, True, color)

def reset_ball():
    ball_rect = pygame.Rect(WINDOW_WIDTH // 2 - BALL_SIZE // 2, WINDOW_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
    direction = random.choice([-1, 1])
    ball_speed_x = BALL_SPEED_X * direction
    ball_speed_y = BALL_SPEED_Y * (random.choice([-1, 1]))
    return ball_rect, ball_speed_x, ball_speed_y

def main():
    running = True
    game_over = False
    winner_text = ""
    
    # Paddle positions
    left_paddle = pygame.Rect(20, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = pygame.Rect(WINDOW_WIDTH - 20 - PADDLE_WIDTH, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    
    # Score
    left_score = 0
    right_score = 0
    
    # Ball setup
    ball_rect, ball_speed_x, ball_speed_y = reset_ball()
    
    # Key states
    keys = set()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    left_score = 0
                    right_score = 0
                    game_over = False
                    left_paddle.y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
                    right_paddle.y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
                    ball_rect, ball_speed_x, ball_speed_y = reset_ball()
                else:
                    keys.add(event.key)
            elif event.type == pygame.KEYUP:
                keys.discard(event.key)
        
        if game_over:
            continue
        
        # Move left paddle (W/S)
        if pygame.K_w in keys:
            left_paddle.y = max(0, left_paddle.y - PADDLE_SPEED)
        if pygame.K_s in keys:
            left_paddle.y = min(WINDOW_HEIGHT - PADDLE_HEIGHT, left_paddle.y + PADDLE_SPEED)
        
        # Move right paddle (Up/Down arrows)
        if pygame.K_UP in keys:
            right_paddle.y = max(0, right_paddle.y - PADDLE_SPEED)
        if pygame.K_DOWN in keys:
            right_paddle.y = min(WINDOW_HEIGHT - PADDLE_HEIGHT, right_paddle.y + PADDLE_SPEED)
        
        # Move ball
        ball_rect.x += ball_speed_x
        ball_rect.y += ball_speed_y
        
        # Ball bounce off top/bottom
        if ball_rect.top <= 0 or ball_rect.bottom >= WINDOW_HEIGHT:
            ball_speed_y = -ball_speed_y
        
        # Ball collision with paddles
        if ball_rect.colliderect(left_paddle):
            ball_speed_x = abs(ball_speed_x)
            ball_rect.left = left_paddle.right + 1
        elif ball_rect.colliderect(right_paddle):
            ball_speed_x = -abs(ball_speed_x)
            ball_rect.right = right_paddle.left - 1
        
        # Scoring
        if ball_rect.left <= 0:
            right_score += 1
            if right_score >= WINNING_SCORE:
                game_over = True
                winner_text = "Right Player Wins!"
            else:
                ball_rect, ball_speed_x, ball_speed_y = reset_ball()
        elif ball_rect.right >= WINDOW_WIDTH:
            left_score += 1
            if left_score >= WINNING_SCORE:
                game_over = True
                winner_text = "Left Player Wins!"
            else:
                ball_rect, ball_speed_x, ball_speed_y = reset_ball()
        
        # Draw everything
        screen.fill(BACKGROUND_COLOR)
        
        # Draw center line
        pygame.draw.aaline(screen, LINE_COLOR, (WINDOW_WIDTH // 2, 0), (WINDOW_WIDTH // 2, WINDOW_HEIGHT))
        
        # Draw paddles
        pygame.draw.rect(screen, PADDLE_COLOR, left_paddle)
        pygame.draw.rect(screen, PADDLE_COLOR, right_paddle)
        
        # Draw ball
        pygame.draw.rect(screen, BALL_COLOR, ball_rect)
        
        # Draw scores
        left_score_surface = create_text_surface(str(left_score), font, TEXT_COLOR)
        right_score_surface = create_text_surface(str(right_score), font, TEXT_COLOR)
        screen.blit(left_score_surface, (WINDOW_WIDTH // 4, 20))
        screen.blit(right_score_surface, (3 * WINDOW_WIDTH // 4, 20))
        
        if game_over:
            winner_surface = create_text_surface(winner_text, big_font, TEXT_COLOR)
            restart_surface = create_text_surface("Press R to Restart", font, TEXT_COLOR)
            screen.blit(winner_surface, (WINDOW_WIDTH // 2 - winner_surface.get_width() // 2, WINDOW_HEIGHT // 2 - 20))
            screen.blit(restart_surface, (WINDOW_WIDTH // 2 - restart_surface.get_width() // 2, WINDOW_HEIGHT // 2 + 40))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()