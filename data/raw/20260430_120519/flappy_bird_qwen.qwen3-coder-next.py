import pygame
import sys
import random

# 顶部常量定义
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
BIRD_START_X = 160
BIRD_START_Y = 300
GRAVITY = 0.35
FLAP_VELOCITY = -7.5
PIPE_SPEED = 3
PIPE_WIDTH = 80
PIPE_GAP_HEIGHT = 170
PIPE_SPAWN_INTERVAL = 90
PIPE_OFFSET = 100  # 第一组管道稍延迟出现
TOP_PIPE_MIN_Y = 50
BOTTOM_PIPE_MAX_Y = WINDOW_HEIGHT - 50 - PIPE_GAP_HEIGHT

# 颜色定义
BG_COLOR = (135, 206, 235)  # 浅蓝色背景
GROUND_COLOR = (75, 194, 83)  # 绿色地面
PIPE_COLOR = (34, 139, 34)  # 深绿色管道
BIRD_COLOR = (255, 215, 0)  # 金色鸟身
TEXT_COLOR = (255, 255, 255)  # 白色文字
SHADOW_COLOR = (0, 0, 0)  # 文字阴影颜色

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Flappy Bird Easy")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 28)

    running = True
    while running:
        state = game_loop(screen, clock, font, small_font)
        if state == "EXIT":
            running = False

    pygame.quit()
    sys.exit()

def game_loop(screen, clock, font, small_font):
    random.seed(42)
    
    # 游戏状态变量
    bird_x = BIRD_START_X
    bird_y = BIRD_START_Y
    bird_velocity_y = 0
    pipes = []
    score = 0
    frame_count = 0
    game_over = False
    passed_pipes = set()

    # 首次生成管道延迟
    first_pipe_delay = True
    
    while True:
        dt = clock.tick(FPS) / 1000.0

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "EXIT"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "EXIT"
                elif event.key == pygame.K_r and game_over:
                    return "RESTART"
                elif event.key in (pygame.K_SPACE, pygame.K_UP) and not game_over:
                    bird_velocity_y = FLAP_VELOCITY

        # 如果还未游戏结束，更新游戏逻辑
        if not game_over:
            frame_count += 1

            # 更新鸟的位置
            bird_velocity_y += GRAVITY
            bird_y += bird_velocity_y

            # 地面碰撞检测
            if bird_y + BIRD_HEIGHT >= WINDOW_HEIGHT - 50:  # 地面高度50
                bird_y = WINDOW_HEIGHT - 50 - BIRD_HEIGHT
                game_over = True

            # 天花板碰撞检测
            if bird_y < 0:
                bird_y = 0
                bird_velocity_y = 0

            # 生成管道
            if first_pipe_delay and frame_count > PIPE_OFFSET:
                first_pipe_delay = False
            
            if not first_pipe_delay and frame_count % PIPE_SPAWN_INTERVAL == 0:
                # 随机生成中间高度，确保管道空隙可到达
                center_y = random.randint(TOP_PIPE_MIN_Y + PIPE_GAP_HEIGHT // 2,
                                         BOTTOM_PIPE_MAX_Y + PIPE_GAP_HEIGHT // 2)
                top_pipe = {
                    "x": WINDOW_WIDTH,
                    "y": 0,
                    "width": PIPE_WIDTH,
                    "height": center_y - PIPE_GAP_HEIGHT // 2,
                    "passed": False
                }
                bottom_pipe = {
                    "x": WINDOW_WIDTH,
                    "y": center_y + PIPE_GAP_HEIGHT // 2,
                    "width": PIPE_WIDTH,
                    "height": WINDOW_HEIGHT - 50 - (center_y + PIPE_GAP_HEIGHT // 2),
                    "passed": False
                }
                pipes.append(top_pipe)
                pipes.append(bottom_pipe)

            # 更新管道位置
            for pipe in pipes[:]:
                pipe["x"] -= PIPE_SPEED
                # 移除超出屏幕左侧的管道
                if pipe["x"] + pipe["width"] < 0:
                    pipes.remove(pipe)
                    continue

                # 碰撞检测
                if (bird_x < pipe["x"] + pipe["width"] and
                    bird_x + BIRD_WIDTH > pipe["x"] and
                    bird_y < pipe["y"] + pipe["height"] and
                    bird_y + BIRD_HEIGHT > pipe["y"]):
                    game_over = True

            # 分数计分
            for i in range(0, len(pipes), 2):
                top_pipe = pipes[i]
                bottom_pipe = pipes[i+1] if i+1 < len(pipes) else None
                if top_pipe["passed"] == False and bird_x > top_pipe["x"] + top_pipe["width"]:
                    score += 1
                    top_pipe["passed"] = True
                    if bottom_pipe:
                        bottom_pipe["passed"] = True

        # 绘制画面
        # 背景
        screen.fill(BG_COLOR)
        
        # 地面
        pygame.draw.rect(screen, GROUND_COLOR, (0, WINDOW_HEIGHT - 50, WINDOW_WIDTH, 50))
        
        # 管道
        for pipe in pipes:
            pygame.draw.rect(screen, PIPE_COLOR, (pipe["x"], pipe["y"], pipe["width"], pipe["height"]))
            # 管道边框
            pygame.draw.rect(screen, (0, 0, 0), (pipe["x"], pipe["y"], pipe["width"], pipe["height"]), 2)

        # 鸟
        pygame.draw.rect(screen, BIRD_COLOR, (bird_x, bird_y, BIRD_WIDTH, BIRD_HEIGHT))
        pygame.draw.rect(screen, (0, 0, 0), (bird_x, bird_y, BIRD_WIDTH, BIRD_HEIGHT), 2)
        
        # HUD 分数（仅在游戏进行中显示）
        if not game_over:
            score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
            screen.blit(score_text, (20, 20))

        # 游戏结束界面
        if game_over:
            # Game Over 文本
            go_text = font.render("Game Over", True, SHADOW_COLOR)
            text_rect = go_text.get_rect(center=(WINDOW_WIDTH // 2 + 3, WINDOW_HEIGHT // 2 + 3))
            screen.blit(go_text, text_rect)
            go_text = font.render("Game Over", True, TEXT_COLOR)
            text_rect = go_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(go_text, text_rect)
            
            # 分数文本
            final_score_text = small_font.render(f"Final Score: {score}", True, TEXT_COLOR)
            screen.blit(final_score_text, final_score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60)))
            
            # 重置提示
            restart_text = small_font.render("Press 'R' to Restart", True, TEXT_COLOR)
            screen.blit(restart_text, restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100)))

        # 标题
        title_text = small_font.render("Flappy Bird Easy", True, TEXT_COLOR)
        screen.blit(title_text, title_text.get_rect(topleft=(20, 70)))

        pygame.display.flip()

        if game_over:
            # 暂停一小会儿处理按键输入，避免瞬间退出
            pygame.time.wait(100)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "EXIT"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "EXIT"
                    elif event.key == pygame.K_r:
                        return "RESTART"

if __name__ == "__main__":
    main()