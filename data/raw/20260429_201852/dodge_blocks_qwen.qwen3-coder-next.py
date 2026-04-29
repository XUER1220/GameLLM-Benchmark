import pygame
import random
import sys
import time

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

PLAYER_WIDTH = 60
PLAYER_HEIGHT = 60
PLAYER_Y_POS = SCREEN_HEIGHT - 40 - PLAYER_HEIGHT
PLAYER_SPEED = 7

OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 40
OBSTACLE_SPEED_MIN = 4
OBSTACLE_SPEED_MAX = 8
OBSTACLE_SPAWN_RATE = 40  # 帧数

# 颜色定义
BG_COLOR = (20, 20, 40)
PLAYER_COLOR = (70, 200, 100)
OBSTACLE_COLOR = (220, 70, 70)
TEXT_COLOR = (255, 255, 255)
HUD_COLOR = (50, 100, 150)

# 初始化 Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge Blocks Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 32)

# 设置固定的随机种子
random.seed(42)


def main():
    # 游戏状态变量
    player_x = (SCREEN_WIDTH - PLAYER_WIDTH) // 2
    obstacles = []
    score = 0
    frame_count = 0
    running = True
    game_over = False
    start_time = time.time()

    while running:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    # 重置游戏
                    player_x = (SCREEN_WIDTH - PLAYER_WIDTH) // 2
                    obstacles = []
                    score = 0
                    frame_count = 0
                    game_over = False
                    start_time = time.time()
                elif event.key == pygame.K_r and not game_over:
                    # 在游戏中按 R 也会重置（可选，但符合规范）
                    player_x = (SCREEN_WIDTH - PLAYER_WIDTH) // 2
                    obstacles = []
                    score = 0
                    frame_count = 0
                    game_over = False
                    start_time = time.time()

        # 游戏未结束时更新
        if not game_over:
            # 移动玩家
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_x = max(0, player_x - PLAYER_SPEED)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_x = min(SCREEN_WIDTH - PLAYER_WIDTH, player_x + PLAYER_SPEED)

            # 更新障碍物
            frame_count += 1
            if frame_count % OBSTACLE_SPAWN_RATE == 0:
                obstacle_x = random.randint(0, SCREEN_WIDTH - OBSTACLE_WIDTH)
                obstacle_y = -OBSTACLE_HEIGHT
                speed = random.randint(OBSTACLE_SPEED_MIN, OBSTACLE_SPEED_MAX)
                obstacles.append([obstacle_x, obstacle_y, speed])

            # 更新所有障碍物位置
            for obstacle in obstacles:
                obstacle[1] += obstacle[2]

            # 移除屏幕外的障碍物
            obstacles = [obs for obs in obstacles if obs[1] < SCREEN_HEIGHT]

            # 检测碰撞（玩家矩形：(player_x, PLAYER_Y_POS, PLAYER_WIDTH, PLAYER_HEIGHT)）
            player_rect = pygame.Rect(player_x, PLAYER_Y_POS, PLAYER_WIDTH, PLAYER_HEIGHT)
            for obstacle in obstacles:
                obstacle_rect = pygame.Rect(obstacle[0], obstacle[1], OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
                if player_rect.colliderect(obstacle_rect):
                    game_over = True

            # 更新分数（每秒 +1 分）
            current_time = time.time()
            if int(current_time - start_time) > score:
                score = int(current_time - start_time)

        # 绘制部分
        screen.fill(BG_COLOR)

        # 绘制玩家
        pygame.draw.rect(screen, PLAYER_COLOR, (player_x, PLAYER_Y_POS, PLAYER_WIDTH, PLAYER_HEIGHT))

        # 绘制障碍物
        for obstacle in obstacles:
            pygame.draw.rect(screen, OBSTACLE_COLOR, (obstacle[0], obstacle[1], OBSTACLE_WIDTH, OBSTACLE_HEIGHT))

        # HUD: 分数显示
        score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))

        # 游戏结束界面
        if game_over:
            # 半透明覆盖层（视觉增强）
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            game_over_text = font.render("GAME OVER", True, TEXT_COLOR)
            final_score_text = small_font.render(f"Final Score: {score}", True, TEXT_COLOR)
            restart_text = small_font.render("Press R to Restart", True, TEXT_COLOR)
            exit_text = small_font.render("Press ESC to Quit", True, TEXT_COLOR)

            # 居中绘制
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 200))
            screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, 260))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 300))
            screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, 340))

        elif frame_count < 5:  # 刚开始显示小提示
            start_text = font.render("Dodge Blocks!", True, TEXT_COLOR)
            screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 100))

        # 屏幕左下角显示操作提示（除非游戏结束）
        if not game_over:
            controls_text = small_font.render("←/→ or A/D to move", True, HUD_COLOR)
            screen.blit(controls_text, (10, SCREEN_HEIGHT - 30))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()