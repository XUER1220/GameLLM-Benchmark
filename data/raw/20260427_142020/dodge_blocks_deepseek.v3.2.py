import pygame
import random
import sys

random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 60
PLAYER_START_X = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
PLAYER_START_Y = SCREEN_HEIGHT - PLAYER_HEIGHT - 40
PLAYER_SPEED = 7
OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 40
OBSTACLE_MIN_SPEED = 4
OBSTACLE_MAX_SPEED = 8
OBSTACLE_SPAWN_INTERVAL = 40

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
BLUE = (50, 150, 255)
GREEN = (50, 255, 100)
YELLOW = (255, 255, 50)
PURPLE = (180, 70, 230)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Dodge Blocks Easy")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    def reset_game():
        nonlocal player_rect, obstacles, frame_count, game_over, score
        player_rect = pygame.Rect(PLAYER_START_X, PLAYER_START_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
        obstacles = []
        frame_count = 0
        game_over = False
        score = 0

    reset_game()

    while True:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r and game_over:
                    reset_game()

        if not game_over:
            frame_count += 1
            score = frame_count // FPS

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_rect.x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_rect.x += PLAYER_SPEED
            player_rect.clamp_ip(screen.get_rect())

            if frame_count % OBSTACLE_SPAWN_INTERVAL == 0:
                speed = random.randint(OBSTACLE_MIN_SPEED, OBSTACLE_MAX_SPEED)
                x = random.randint(0, SCREEN_WIDTH - OBSTACLE_WIDTH)
                obstacles.append({
                    'rect': pygame.Rect(x, -OBSTACLE_HEIGHT, OBSTACLE_WIDTH, OBSTACLE_HEIGHT),
                    'speed': speed
                })

            to_remove = []
            for obs in obstacles:
                obs['rect'].y += obs['speed']
                if obs['rect'].colliderect(player_rect):
                    game_over = True
                if obs['rect'].top > SCREEN_HEIGHT:
                    to_remove.append(obs)
            for obs in to_remove:
                obstacles.remove(obs)

        screen.fill(BLACK)

        pygame.draw.rect(screen, BLUE, player_rect, border_radius=8)
        for obs in obstacles:
            pygame.draw.rect(screen, RED, obs['rect'], border_radius=6)

        time_text = font.render(f"Time: {score}s", True, GREEN)
        screen.blit(time_text, (10, 10))

        if game_over:
            game_over_text = font.render("GAME OVER", True, YELLOW)
            final_score_text = font.render(f"Final Score: {score}s", True, YELLOW)
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
            screen.blit(final_score_text, (SCREEN_WIDTH//2 - final_score_text.get_width()//2, SCREEN_HEIGHT//2 - 20))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 20))

        pygame.display.flip()

if __name__ == "__main__":
    main()