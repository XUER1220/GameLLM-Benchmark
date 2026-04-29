import pygame
import sys
import random

# 参数常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 鸟的属性
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
BIRD_X = 160
BIRD_Y_START = 300
GRAVITY = 0.35
JUMP_STRENGTH = -7.5

# 管道属性
PIPE_WIDTH = 80
PIPE_GAP = 170
PIPE_SPEED = 3
PIPE_SPAWN_INTERVAL = 90
PIPE_MIN_Y = 100
PIPE_MAX_Y = SCREEN_HEIGHT - 100 - PIPE_GAP

# 颜色常量
BG_COLOR = (135, 206, 235)
BIRD_COLOR = (255, 255, 0)
PIPE_COLOR = (34, 139, 34)
GROUND_COLOR = (139, 69, 19)
TEXT_COLOR = (255, 255, 255)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flappy Bird Easy")
    clock = pygame.time.Clock()
    font_large = pygame.font.SysFont(None, 48)
    font_small = pygame.font.SysFont(None, 32)
    font_hud = pygame.font.SysFont(None, 36)
    random.seed(42)

    def reset_game():
        bird_y = BIRD_Y_START
        bird_velocity = 0
        pipes = []
        frame_count = 0
        score = 0
        passed_pipes = set()
        game_state = "start"  # start, playing, game_over
        return bird_y, bird_velocity, pipes, frame_count, score, passed_pipes, game_state

    # 初始化游戏状态
    bird_y, bird_velocity, pipes, frame_count, score, passed_pipes, game_state = reset_game()

    while True:
        dt = clock.tick(FPS)

        # 输入处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r and game_state == "game_over":
                    bird_y, bird_velocity, pipes, frame_count, score, passed_pipes, game_state = reset_game()
                elif event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if game_state == "start":
                        game_state = "playing"
                        bird_velocity = JUMP_STRENGTH
                    elif game_state == "playing":
                        bird_velocity = JUMP_STRENGTH
                    elif game_state == "game_over":
                        bird_y, bird_velocity, pipes, frame_count, score, passed_pipes, game_state = reset_game()
                        game_state = "playing"
                        bird_velocity = JUMP_STRENGTH

        # 游戏逻辑
        if game_state == "playing":
            frame_count += 1

            # 鸟物理
            bird_velocity += GRAVITY
            bird_y += bird_velocity

            # 更新管道
            if frame_count % PIPE_SPAWN_INTERVAL == 0:
                gap_center = random.randint(PIPE_MIN_Y + PIPE_GAP // 2, PIPE_MAX_Y + PIPE_GAP // 2)
                pipes.append({
                    "x": SCREEN_WIDTH,
                    "top_y": gap_center - PIPE_GAP,
                    "bottom_y": gap_center,
                    "passed": False
                })

            for pipe in pipes:
                pipe["x"] -= PIPE_SPEED

            # 移除出界管道
            pipes = [p for p in pipes if p["x"] + PIPE_WIDTH > 0]

            # 碰撞检测：上下边界
            if bird_y < 0 or bird_y + BIRD_HEIGHT > SCREEN_HEIGHT:
                game_state = "game_over"

            # 碰撞检测：管道
            bird_rect = pygame.Rect(BIRD_X, bird_y, BIRD_WIDTH, BIRD_HEIGHT)
            for pipe in pipes:
                top_rect = pygame.Rect(pipe["x"], 0, PIPE_WIDTH, pipe["top_y"])
                bottom_rect = pygame.Rect(pipe["x"], pipe["bottom_y"], PIPE_WIDTH, SCREEN_HEIGHT - pipe["bottom_y"])
                if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                    game_state = "game_over"

            # 分数更新
            for i, pipe in enumerate(pipes):
                if not pipe["passed"] and BIRD_X > pipe["x"] + PIPE_WIDTH:
                    pipe["passed"] = True
                    score += 1

            # 分数更新：使用 passed_pipes 集合防止重复计分（冗余防护）
            pass  # 逻辑已覆盖

        # 绘制
        screen.fill(BG_COLOR)

        # 绘制地面装饰
        pygame.draw.rect(screen, GROUND_COLOR, (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))

        # 绘制鸟
        pygame.draw.rect(screen, BIRD_COLOR, (BIRD_X, bird_y, BIRD_WIDTH, BIRD_HEIGHT))
        
        # 绘制管道
        for pipe in pipes:
            pygame.draw.rect(screen, PIPE_COLOR, (pipe["x"], 0, PIPE_WIDTH, pipe["top_y"]))
            pygame.draw.rect(screen, PIPE_COLOR, (pipe["x"], pipe["bottom_y"], PIPE_WIDTH, SCREEN_HEIGHT - pipe["bottom_y"]))

        # 绘制 HUD（分数）
        score_text = font_hud.render(f"Score: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))

        # 绘制标题
        title_text = font_hud.render("Flappy Bird Easy", True, TEXT_COLOR)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 10))

        # 绘制状态提示
        if game_state == "start":
            start_text = font_large.render("Press SPACE to Start", True, TEXT_COLOR)
            screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))
        elif game_state == "game_over":
            game_over_text = font_large.render("Game Over", True, TEXT_COLOR)
            final_score_text = font_small.render(f"Score: {score}", True, TEXT_COLOR)
            restart_text = font_small.render("Press R to Restart", True, TEXT_COLOR)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()

if __name__ == "__main__":
    main()