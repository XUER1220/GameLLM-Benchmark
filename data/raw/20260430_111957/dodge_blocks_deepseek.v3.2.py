import pygame
import random
import sys

# 固定随机种子
random.seed(42)

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 玩家常量
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 60
PLAYER_SPEED = 7
PLAYER_INIT_X = (SCREEN_WIDTH - PLAYER_WIDTH) // 2
PLAYER_INIT_Y = SCREEN_HEIGHT - PLAYER_HEIGHT - 40

# 障碍物常量
OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 40
OBSTACLE_MIN_SPEED = 4
OBSTACLE_MAX_SPEED = 8
OBSTACLE_SPAWN_INTERVAL = 40

# 颜色
BACKGROUND_COLOR = (20, 20, 35)
PLAYER_COLOR = (70, 180, 240)
OBSTACLE_COLOR = (240, 90, 90)
TEXT_COLOR = (240, 240, 240)
HIGHLIGHT_COLOR = (255, 210, 0)
GAME_OVER_BG_COLOR = (30, 30, 50, 220)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Dodge Blocks Easy")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 28)

    def init_game():
        nonlocal player_x, player_y, obstacles, score, alive, frame_count
        player_x = PLAYER_INIT_X
        player_y = PLAYER_INIT_Y
        obstacles = []
        score = 0
        alive = True
        frame_count = 0

    init_game()

    running = True
    while running:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    init_game()

        if not alive:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                init_game()
            screen.fill(BACKGROUND_COLOR)
            # 绘制存活的障碍物和玩家
            for obs in obstacles:
                pygame.draw.rect(screen, OBSTACLE_COLOR, (obs['x'], obs['y'], OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
            pygame.draw.rect(screen, PLAYER_COLOR, (player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT))
            # 游戏结束层
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(GAME_OVER_BG_COLOR)
            screen.blit(overlay, (0, 0))
            game_over_text = font.render("GAME OVER", True, HIGHLIGHT_COLOR)
            score_text = font.render(f"Final Score: {score}", True, TEXT_COLOR)
            restart_text = small_font.render("Press R to Restart", True, TEXT_COLOR)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 10))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
            pygame.display.flip()
            clock.tick(FPS)
            continue

        # 玩家移动
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_x += PLAYER_SPEED
        player_x = max(0, min(SCREEN_WIDTH - PLAYER_WIDTH, player_x))

        # 生成障碍物
        if frame_count % OBSTACLE_SPAWN_INTERVAL == 0:
            speed = random.randint(OBSTACLE_MIN_SPEED, OBSTACLE_MAX_SPEED)
            x = random.randint(0, SCREEN_WIDTH - OBSTACLE_WIDTH)
            obstacles.append({'x': x, 'y': -OBSTACLE_HEIGHT, 'speed': speed})

        # 更新障碍物并检测碰撞
        player_rect = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
        new_obstacles = []
        for obs in obstacles:
            obs['y'] += obs['speed']
            obs_rect = pygame.Rect(obs['x'], obs['y'], OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
            if obs_rect.colliderect(player_rect):
                alive = False
            if obs['y'] < SCREEN_HEIGHT:
                new_obstacles.append(obs)
        obstacles = new_obstacles

        # 更新分数（每帧加1/60，约每秒1分）
        score += 1 / FPS
        frame_count += 1

        # 绘制
        screen.fill(BACKGROUND_COLOR)
        for obs in obstacles:
            pygame.draw.rect(screen, OBSTACLE_COLOR, (obs['x'], obs['y'], OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
        pygame.draw.rect(screen, PLAYER_COLOR, (player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT))

        # 绘制HUD
        score_text = font.render(f"Score: {int(score)}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))
        controls_text = small_font.render("Move: Left/Right or A/D | Restart: R | Exit: ESC", True, TEXT_COLOR)
        screen.blit(controls_text, (SCREEN_WIDTH - controls_text.get_width() - 10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()