import pygame
import random

# 初始化 Pygame
pygame.init()

# 通用常量
WIDTH, HEIGHT = 800, 600
FPS = 60
SEED = 42
random.seed(SEED)

# 颜色常量
BG_COLOR = (30, 30, 30)        # 深灰色背景
PLAYER_COLOR = (50, 205, 50)   # 鲜绿玩家
BLOCK_COLOR = (255, 69, 0)     # 橙红色障碍块
TEXT_COLOR = (255, 255, 255)   # 白色文字

# 玩家相关常量
PLAYER_WIDTH, PLAYER_HEIGHT = 60, 60
PLAYER_Y = HEIGHT - 40 - PLAYER_HEIGHT
PLAYER_SPEED = 7

# 障碍物相关常量
BLOCK_WIDTH, BLOCK_HEIGHT = 40, 40
BLOCK_Y_SPEED_MIN = 4
BLOCK_Y_SPEED_MAX = 8
BLOCK_SPAWN_INTERVAL = 40  # 帧数间隔

# 字体设置
FONT = pygame.font.Font(None, 36)
BIG_FONT = pygame.font.Font(None, 72)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Dodge Blocks Easy")
        self.clock = pygame.time.Clock()
        self.reset()
        
    def reset(self):
        self.player_x = (WIDTH - PLAYER_WIDTH) // 2
        self.player_y = PLAYER_Y
        self.blocks = []
        self.score = 0
        self.frames = 0
        self.running = True
        self.game_over = False
    
    def spawn_block(self):
        x = random.randint(0, WIDTH - BLOCK_WIDTH)
        y = -BLOCK_HEIGHT
        speed = random.randint(BLOCK_Y_SPEED_MIN, BLOCK_Y_SPEED_MAX)
        self.blocks.append(pygame.Rect(x, y, BLOCK_WIDTH, BLOCK_HEIGHT))
        self.block_speeds.append(speed)
    
    def update_player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_x += PLAYER_SPEED
        
        # 约束玩家位置
        self.player_x = max(0, min(self.player_x, WIDTH - PLAYER_WIDTH))
    
    def update_game_logic(self):
        if self.game_over:
            return
        
        self.frames += 1
        
        # 计分：每 60 帧（约 1 秒）加 1 分
        if self.frames % FPS == 0:
            self.score += 1
        
        # 每 BLOCK_SPAWN_INTERVAL 帧生成一个新障碍物
        if self.frames % BLOCK_SPAWN_INTERVAL == 0:
            self.spawn_block()
        
        # 移动障碍物
        for i, block in enumerate(self.blocks):
            block.y += self.block_speeds[i]
        
        # 移除超出屏幕底部的障碍物
        self.blocks = [block for block in self.blocks if block.y < HEIGHT]
        self.block_speeds = [
            self.block_speeds[i] 
            for i in range(len(self.blocks)) 
            if self.blocks[i].y < HEIGHT
        ]
        
        # 玩家矩形
        player_rect = pygame.Rect(self.player_x, self.player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
        
        # 碰撞检测
        for block in self.blocks:
            if player_rect.colliderect(block):
                self.game_over = True
                return
    
    def draw(self):
        self.screen.fill(BG_COLOR)
        
        # 绘制玩家
        pygame.draw.rect(self.screen, PLAYER_COLOR, 
                        (self.player_x, self.player_y, PLAYER_WIDTH, PLAYER_HEIGHT))
        
        # 绘制障碍物
        for block in self.blocks:
            pygame.draw.rect(self.screen, BLOCK_COLOR, block)
        
        # HUD
        score_text = FONT.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))
        
        if self.game_over:
            # 游戏结束界面
            game_over_text = BIG_FONT.render("GAME OVER", True, TEXT_COLOR)
            score_text = FONT.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            restart_text = FONT.render("Press R to Restart", True, TEXT_COLOR)
            
            game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def run(self):
        self.block_speeds = []  # 障碍物速度列表，对应 self.blocks
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset()
            
            if not self.game_over:
                self.update_player_input()
                self.update_game_logic()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    Game().run()