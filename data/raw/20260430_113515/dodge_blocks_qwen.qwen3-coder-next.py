import pygame
import random

# 固定初始参数
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# 玩家参数
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 60
PLAYER_Y_OFFSET = 40
PLAYER_SPEED = 7
PLAYER_COLOR = (0, 200, 100)

# 障碍物参数
BLOCK_WIDTH = 40
BLOCK_HEIGHT = 40
BLOCK_MIN_SPEED = 4
BLOCK_MAX_SPEED = 8
BLOCK_COLOR = (200, 50, 50)
BLOCK_SPAWN_RATE = 40  # 帧间隔

# 分数参数
SCORE_PER_SECOND = 1

# 颜色定义
BG_COLOR = (30, 30, 40)
TEXT_COLOR = (255, 255, 255)
SCORE_COLOR = (255, 255, 0)
GAME_OVER_COLOR = (255, 50, 50)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Dodge Blocks Easy")
    clock = pygame.time.Clock()
    
    # 随机种子设置
    random.seed(42)
    
    # 字体设置（使用系统默认字体）
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)
    
    def reset_game():
        player_rect = pygame.Rect((WINDOW_WIDTH - PLAYER_WIDTH) // 2, WINDOW_HEIGHT - PLAYER_Y_OFFSET - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
        blocks = []
        score = 0
        frames = 0
        game_over = False
        start_time = pygame.time.get_ticks()
        return player_rect, blocks, score, frames, game_over, start_time
    
    # 初始化游戏状态
    player_rect, blocks, score, frames, game_over, start_time = reset_game()
    
    # 游戏主循环
    running = True
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r and game_over:
                    player_rect, blocks, score, frames, game_over, start_time = reset_game()
        
        # 更新游戏逻辑
        if not game_over:
            frames += 1
            
            # 计算分数（每秒 1 分）
            elapsed_seconds = (pygame.time.get_ticks() - start_time) // 1000
            score = elapsed_seconds
            
            # 处理输入
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_rect.x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_rect.x += PLAYER_SPEED
            
            # 玩家边界限制
            player_rect.x = max(0, min(WINDOW_WIDTH - PLAYER_WIDTH, player_rect.x))
            
            # 生成障碍物
            if frames % BLOCK_SPAWN_RATE == 0:
                block_x = random.randint(0, WINDOW_WIDTH - BLOCK_WIDTH)
                block_speed = random.randint(BLOCK_MIN_SPEED, BLOCK_MAX_SPEED)
                block_rect = pygame.Rect(block_x, -BLOCK_HEIGHT, BLOCK_WIDTH, BLOCK_HEIGHT)
                blocks.append((block_rect, block_speed))
            
            # 更新障碍物位置
            blocks_to_remove = []
            for i, (block_rect, speed) in enumerate(blocks):
                block_rect.y += speed
                if block_rect.y > WINDOW_HEIGHT:
                    blocks_to_remove.append(i)
                # 检测碰撞
                if player_rect.colliderect(block_rect):
                    game_over = True
            
            # 移除出屏幕的障碍物（倒序移除避免索引错误）
            for i in reversed(blocks_to_remove):
                del blocks[i]
        
        # 绘制画面
        screen.fill(BG_COLOR)
        
        # 绘制玩家
        pygame.draw.rect(screen, PLAYER_COLOR, player_rect)
        
        # 绘制障碍物
        for block_rect, _ in blocks:
            pygame.draw.rect(screen, BLOCK_COLOR, block_rect)
        
        # 绘制 HUD（分数和时间）
        score_text = font.render(f"Score: {score}", True, SCORE_COLOR)
        screen.blit(score_text, (10, 10))
        
        if game_over:
            # 游戏结束画面
            game_over_text = font.render("GAME OVER", True, GAME_OVER_COLOR)
            restart_text = small_font.render("Press R to Restart", True, TEXT_COLOR)
            
            # 居中绘制文本
            game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
            
            screen.blit(game_over_text, game_over_rect)
            screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()