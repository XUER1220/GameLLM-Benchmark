import pygame
import sys
import random

# 固定常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 60
PLAYER_Y = SCREEN_HEIGHT - 40 - PLAYER_HEIGHT
PLAYER_SPEED = 7
OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 40
OBSTACLE_SPEED_MIN = 4
OBSTACLE_SPEED_MAX = 8
OBSTACLE_SPAWN_INTERVAL = 40

# 颜色定义
COLOR_BACKGROUND = (30, 30, 40)
COLOR_PLAYER = (50, 200, 100)
COLOR_OBSTACLE = (200, 50, 50)
COLOR_TEXT = (255, 255, 255)
COLOR_GAME_OVER = (255, 60, 60)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Dodge Blocks Easy")
    clock = pygame.time.Clock()
    random.seed(42)
    
    # 字体设置（使用系统默认字体）
    try:
        font = pygame.font.SysFont(None, 36)
        big_font = pygame.font.SysFont(None, 72)
    except:
        font = pygame.font.Font(None, 36)
        big_font = pygame.font.Font(None, 72)
    
    def reset_game():
        player_rect = pygame.Rect((SCREEN_WIDTH - PLAYER_WIDTH) // 2, PLAYER_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
        obstacles = []  # list of rects
        obstacle_speeds = []
        frame_count = 0
        score = 0
        frame_since_last_second = 0
        return {
            'player': player_rect,
            'obstacles': obstacles,
            'obstacle_speeds': obstacle_speeds,
            'frame_count': frame_count,
            'score': score,
            'frame_since_last_second': frame_since_last_second,
            'game_over': False,
            'game_over_frame': 0
        }
    
    state = reset_game()
    
    # 游戏主循环
    running = True
    
    while running:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and state['game_over']:
                    state = reset_game()
                    state['game_over'] = False
        
        # 如果游戏未结束
        if not state['game_over']:
            # 键盘输入处理
            keys = pygame.key.get_pressed()
            dx = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = PLAYER_SPEED
            state['player'].x += dx
            
            # 边界限制
            if state['player'].left < 0:
                state['player'].left = 0
            if state['player'].right > SCREEN_WIDTH:
                state['player'].right = SCREEN_WIDTH
            
            # 增加帧计数
            state['frame_count'] += 1
            state['frame_since_last_second'] += 1
            
            # 每秒加分
            if state['frame_since_last_second'] >= FPS:
                state['frame_since_last_second'] = 0
                state['score'] += 1
            
            # 每 OBSTACLE_SPAWN_INTERVAL 帧生成障碍物
            if state['frame_count'] % OBSTACLE_SPAWN_INTERVAL == 0:
                # 生成位置（完整屏幕内）
                x_pos = random.randint(0, SCREEN_WIDTH - OBSTACLE_WIDTH)
                new_obstacle = pygame.Rect(x_pos, -OBSTACLE_HEIGHT, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
                # 速度固定为种子决定
                speed = random.randint(OBSTACLE_SPEED_MIN, OBSTACLE_SPEED_MAX)
                state['obstacles'].append(new_obstacle)
                state['obstacle_speeds'].append(speed)
            
            # 更新障碍物位置
            for i in range(len(state['obstacles']) - 1, -1, -1):
                state['obstacles'][i].y += state['obstacle_speeds'][i]
                # 移除屏幕外障碍物
                if state['obstacles'][i].top > SCREEN_HEIGHT:
                    state['obstacles'].pop(i)
                    state['obstacle_speeds'].pop(i)
            
            # 碰撞检测
            player_rect = state['player']
            for obstacle in state['obstacles']:
                if player_rect.colliderect(obstacle):
                    state['game_over'] = True
                    state['game_over_frame'] = state['frame_count']
                    break
        
        # 绘制
        screen.fill(COLOR_BACKGROUND)
        
        # 绘制玩家
        pygame.draw.rect(screen, COLOR_PLAYER, state['player'])
        
        # 绘制障碍物
        for obstacle in state['obstacles']:
            pygame.draw.rect(screen, COLOR_OBSTACLE, obstacle)
        
        # 绘制HUD
        # 分数
        score_text = font.render(f"Score: {state['score']}", True, COLOR_TEXT)
        screen.blit(score_text, (10, 10))
        
        # 时间显示（以秒为单位，仅显示整数）
        seconds = state['score']  # 因为按秒加分
        time_text = font.render(f"Time: {seconds}s", True, COLOR_TEXT)
        screen.blit(time_text, (SCREEN_WIDTH - 150, 10))
        
        # 游戏结束画面
        if state['game_over']:
            # 半透明黑色遮罩
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Game Over 文字
            game_over_text = big_font.render("Game Over", True, COLOR_GAME_OVER)
            rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(game_over_text, rect)
            
            # 最终分数
            final_score_text = font.render(f"Final Score: {state['score']}", True, COLOR_TEXT)
            rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            screen.blit(final_score_text, rect)
            
            # 重新开始提示
            restart_text = font.render("Press R to Restart", True, COLOR_TEXT)
            rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
            screen.blit(restart_text, rect)
        
        # 刷新屏幕
        pygame.display.flip()
        
        # 保持帧率
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()