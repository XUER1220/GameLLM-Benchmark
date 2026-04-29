import pygame
import random
import sys

# 初始化随机数生成器
random.seed(42)

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 颜色定义
BACKGROUND_COLOR = (20, 20, 35)
PLAYER_COLOR = (70, 180, 255)
OBSTACLE_COLOR = (255, 80, 80)
TEXT_COLOR = (240, 240, 240)
GAME_OVER_COLOR = (255, 50, 50)

# 玩家常量
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 60
PLAYER_SPEED = 7
PLAYER_INIT_X = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
PLAYER_INIT_Y = SCREEN_HEIGHT - PLAYER_HEIGHT - 40

# 障碍物常量
OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 40
OBSTACLE_SPEED_MIN = 4
OBSTACLE_SPEED_MAX = 8
OBSTACLE_SPAWN_INTERVAL = 40  # 帧数

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Dodge Blocks Easy")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    big_font = pygame.font.SysFont(None, 64)

    def reset_game():
        nonlocal player_rect, obstacles, frames_passed, game_over, score
        player_rect = pygame.Rect(PLAYER_INIT_X, PLAYER_INIT_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
        obstacles = []
        frames_passed = 0
        game_over = False
        score = 0

    reset_game()

    while True:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    reset_game()

        # 玩家移动
        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_rect.x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_rect.x += PLAYER_SPEED
            # 边界限制
            if player_rect.left < 0:
                player_rect.left = 0
            if player_rect.right > SCREEN_WIDTH:
                player_rect.right = SCREEN_WIDTH

        # 障碍物生成
        if not game_over and frames_passed % OBSTACLE_SPAWN_INTERVAL == 0:
            speed = random.uniform(OBSTACLE_SPEED_MIN, OBSTACLE_SPEED_MAX)
            x = random.randint(0, SCREEN_WIDTH - OBSTACLE_WIDTH)
            obstacles.append({
                'rect': pygame.Rect(x, -OBSTACLE_HEIGHT, OBSTACLE_WIDTH, OBSTACLE_HEIGHT),
                'speed': speed
            })

        # 障碍物更新
        if not game_over:
            score = frames_passed // FPS
            for obs in obstacles[:]:
                obs['rect'].y += obs['speed']
                # 移除屏幕外的障碍物
                if obs['rect'].top > SCREEN_HEIGHT:
                    obstacles.remove(obs)
                # 碰撞检测
                elif obs['rect'].colliderect(player_rect):
                    game_over = True

        # 绘制
        screen.fill(BACKGROUND_COLOR)

        # 绘制障碍物
        for obs in obstacles:
            pygame.draw.rect(screen, OBSTACLE_COLOR, obs['rect'])

        # 绘制玩家
        pygame.draw.rect(screen, PLAYER_COLOR, player_rect)

        # 绘制分数
        score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (20, 20))

        # 游戏结束画面
        if game_over:
            # 半透明覆盖层
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            game_over_text = big_font.render("Game Over", True, GAME_OVER_COLOR)
            final_score_text = font.render(f"Final Score: {score}", True, TEXT_COLOR)
            restart_text = font.render("Press R to Restart", True, TEXT_COLOR)

            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
            screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()
        frames_passed += 1
        clock.tick(FPS)

if __name__ == "__main__":
    main()