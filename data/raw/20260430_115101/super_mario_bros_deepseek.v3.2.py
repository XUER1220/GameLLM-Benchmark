import pygame
import random
import sys

# 初始化
pygame.init()
random.seed(42)

# 窗口设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GAME_WIDTH = 3200
GAME_HEIGHT = 600

# 颜色
COLOR_BG = (137, 207, 240)  # 天空蓝
COLOR_GND = (90, 175, 80)   # 地面绿
COLOR_BLK = (180, 100, 50)  # 砖块棕
COLOR_QBL = (255, 200, 50)  # 问号块黄
COLOR_PIP = (0, 155, 0)     # 管道绿
COLOR_PLR = (255, 0, 0)     # 玩家红
COLOR_ENM = (0, 0, 255)     # 敌人蓝
COLOR_COIN = (255, 215, 0)  # 金币金
COLOR_FLAG = (255, 255, 0)  # 旗杆黄
COLOR_HUD = (50, 50, 50)    # HUD深灰
COLOR_TEXT = (255, 255, 255)# 文字白
COLOR_WIN = (50, 255, 100)  # 胜利绿
COLOR_LOSE = (255, 50, 50)  # 失败红

# 物理参数
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 48
PLAYER_SPEED = 5
JUMP_SPEED = -12
GRAVITY = 0.5

ENEMY_WIDTH = 32
ENEMY_HEIGHT = 32
ENEMY_SPEED = 2

COIN_SIZE = 18

# 游戏状态
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario Bros.")
        self.clock = pygame.time.Clock()
        self.reset()
        
    def reset(self):
        self.camera_x = 0
        self.player = Player()
        self.grounds = []
        self.blocks = []
        self.pipes = []
        self.coins = []
        self.enemies = []
        self.flag = Flag()
        self.init_level()
        self.score = 0
        self.coins_collected = 0
        self.lives = 3
        self.game_over = False
        self.win = False
        
    def init_level(self):
        # 地面
        for x in range(0, GAME_WIDTH, 50):
            self.grounds.append(pygame.Rect(x, GAME_HEIGHT - 50, 50, 50))
        
        # 砖块和问号块 (12个)
        block_data = [
            (400, 400, 'b'), (450, 400, 'b'), (500, 400, 'b'),
            (600, 350, 'b'), (650, 350, 'b'),
            (800, 300, 'b'), (850, 300, 'b'), (900, 300, 'b'),
            (1100, 250, 'q'), (1150, 250, 'q'),
            (1400, 200, 'b'), (1450, 200, 'b')
        ]
        for x, y, typ in block_data:
            rect = pygame.Rect(x, y, 40, 40)
            if typ == 'q':
                self.blocks.append({'rect': rect, 'type': 'question'})
            else:
                self.blocks.append({'rect': rect, 'type': 'brick'})
        
        # 管道和台阶 (4个)
        self.pipes.append(pygame.Rect(1000, GAME_HEIGHT - 150, 60, 150))
        self.pipes.append(pygame.Rect(1600, GAME_HEIGHT - 120, 60, 120))
        self.pipes.append(pygame.Rect(2000, GAME_HEIGHT - 100, 60, 100))
        self.pipes.append(pygame.Rect(2600, GAME_HEIGHT - 80, 60, 80))
        
        # 金币 (12个)
        coin_pos = [(420, 360), (470, 360), (520, 360),
                    (620, 310), (670, 310),
                    (820, 260), (870, 260), (920, 260),
                    (1110, 210), (1160, 210),
                    (1420, 160), (1470, 160)]
        for x, y in coin_pos:
            self.coins.append(pygame.Rect(x, y, COIN_SIZE, COIN_SIZE))
        
        # 敌人 (3个)
        self.enemies.append(Enemy(700, GAME_HEIGHT - 50 - ENEMY_HEIGHT))
        self.enemies.append(Enemy(1300, GAME_HEIGHT - 150 - ENEMY_HEIGHT, patrol_range=100))
        self.enemies.append(Enemy(1800, GAME_HEIGHT - 50 - ENEMY_HEIGHT, patrol_range=150))
        
        # 终点旗杆
        self.flag.rect.x = GAME_WIDTH - 100
        
        # 坑洞 (两个)
        self.hole1 = pygame.Rect(1200, GAME_HEIGHT - 50, 100, 50)
        self.hole2 = pygame.Rect(2200, GAME_HEIGHT - 50, 150, 50)
        
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset()
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            if not self.game_over and not self.win:
                self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()
        sys.exit()
    
    def update(self, dt):
        # 玩家输入
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT]:
            dx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            dx += PLAYER_SPEED
        
        # 玩家更新
        self.player.update(dx, keys[pygame.K_SPACE], self.grounds + [obj['rect'] for obj in self.blocks] + self.pipes)
        
        # 相机跟随
        target_camera_x = self.player.rect.centerx - SCREEN_WIDTH // 2
        self.camera_x = max(0, min(target_camera_x, GAME_WIDTH - SCREEN_WIDTH))
        
        # 敌人更新
        for enemy in self.enemies[:]:
            enemy.update(self.grounds + self.pipes)
            # 敌人与玩家碰撞
            if enemy.rect.colliderect(self.player.rect):
                if self.player.vel_y > 0 and self.player.rect.bottom < enemy.rect.centery:
                    self.enemies.remove(enemy)
                    self.score += 200
                else:
                    self.lose_life()
        
        # 金币收集
        for coin in self.coins[:]:
            if self.player.rect.colliderect(coin):
                self.coins.remove(coin)
                self.score += 100
                self.coins_collected += 1
        
        # 坑洞检测
        if self.player.rect.bottom >= GAME_HEIGHT:
            self.lose_life()
        elif self.hole1.collidepoint(self.player.rect.midbottom) or \
             self.hole2.collidepoint(self.player.rect.midbottom):
            self.lose_life()
        
        # 旗杆触碰
        if self.player.rect.colliderect(self.flag.rect) and self.lives > 0:
            self.win = True
        
        # 生命检查
        if self.lives <= 0:
            self.game_over = True
    
    def lose_life(self):
        self.lives -= 1
        if self.lives > 0:
            # 回到最近的平台
            self.player.rect.x = max(50, self.player.rect.x - 200)
            self.player.rect.y = GAME_HEIGHT - 100
            self.player.vel_y = 0
            # 重置相机
            self.camera_x = max(0, self.player.rect.centerx - SCREEN_WIDTH // 2)
        else:
            self.game_over = True
    
    def draw(self):
        self.screen.fill(COLOR_BG)
        
        # 绘制地面
        for ground in self.grounds:
            pygame.draw.rect(self.screen, COLOR_GND, ground.move(-self.camera_x, 0))
        
        # 绘制坑洞
        pygame.draw.rect(self.screen, COLOR_BG, self.hole1.move(-self.camera_x, 0))
        pygame.draw.rect(self.screen, COLOR_BG, self.hole2.move(-self.camera_x, 0))
        
        # 绘制砖块和问号块
        for block in self.blocks:
            color = COLOR_QBL if block['type'] == 'question' else COLOR_BLK
            pygame.draw.rect(self.screen, color, block['rect'].move(-self.camera_x, 0))
            if block['type'] == 'question':
                pygame.draw.rect(self.screen, (200, 150, 0), block['rect'].move(-self.camera_x, 0), 3)
                pygame.draw.polygon(self.screen, (255, 255, 200), [
                    (block['rect'].centerx - 10 - self.camera_x, block['rect'].centery),
                    (block['rect'].centerx - self.camera_x, block['rect'].centery - 10),
                    (block['rect'].centerx + 10 - self.camera_x, block['rect'].centery),
                    (block['rect'].centerx - self.camera_x, block['rect'].centery + 10)
                ])
        
        # 绘制管道
        for pipe in self.pipes:
            pygame.draw.rect(self.screen, COLOR_PIP, pipe.move(-self.camera_x, 0))
            pygame.draw.rect(self.screen, (0, 100, 0), pipe.move(-self.camera_x, 0), 3)
        
        # 绘制金币
        for coin in self.coins:
            pygame.draw.circle(self.screen, COLOR_COIN, 
                               (coin.centerx - self.camera_x, coin.centery), COIN_SIZE // 2)
            pygame.draw.circle(self.screen, (200, 150, 0), 
                               (coin.centerx - self.camera_x, coin.centery), COIN_SIZE // 2, 2)
        
        # 绘制敌人
        for enemy in self.enemies:
            pygame.draw.rect(self.screen, COLOR_ENM, enemy.rect.move(-self.camera_x, 0))
            pygame.draw.circle(self.screen, (150, 150, 255), 
                               (enemy.rect.centerx - self.camera_x, enemy.rect.top + 10), 8)
        
        # 绘制旗杆
        flag_rect = self.flag.rect.move(-self.camera_x, 0)
        pygame.draw.rect(self.screen, (200, 200, 200), flag_rect)
        pygame.draw.rect(self.screen, COLOR_FLAG, 
                         (flag_rect.x + 10, flag_rect.y + 10, 30, 20))
        
        # 绘制玩家
        pygame.draw.rect(self.screen, COLOR_PLR, 
                         self.player.rect.move(-self.camera_x, 0))
        pygame.draw.circle(self.screen, (255, 150, 150), 
                           (self.player.rect.centerx - self.camera_x, self.player.rect.y + 15), 10)
        
        # HUD
        self.draw_hud()
        
        # 游戏结束/胜利提示
        if self.game_over:
            self.draw_text("GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, COLOR_LOSE, 64)
            self.draw_text(f"Score: {self.score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20, COLOR_TEXT, 36)
            self.draw_text("Press R to Restart", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, COLOR_TEXT, 36)
        elif self.win:
            self.draw_text("YOU WIN!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, COLOR_WIN, 64)
            self.draw_text(f"Score: {self.score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20, COLOR_TEXT, 36)
            self.draw_text("Press R to Restart", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, COLOR_TEXT, 36)
    
    def draw_hud(self):
        hud_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 40)
        pygame.draw.rect(self.screen, COLOR_HUD, hud_rect)
        self.draw_text(f"Lives: {self.lives}", 100, 20, COLOR_TEXT)
        self.draw_text(f"Score: {self.score}", 300, 20, COLOR_TEXT)
        self.draw_text(f"Coins: {self.coins_collected}", 500, 20, COLOR_TEXT)
    
    def draw_text(self, text, x, y, color, size=30):
        font = pygame.font.SysFont(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, GAME_HEIGHT - 100, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
    
    def update(self, dx, jump, platforms):
        # 水平移动
        self.rect.x += dx
        # 水平碰撞
        for plat in platforms:
            if self.rect.colliderect(plat):
                if dx > 0:
                    self.rect.right = plat.left
                elif dx < 0:
                    self.rect.left = plat.right
        
        # 重力
        self.vel_y += GRAVITY
        if jump and self.on_ground:
            self.vel_y = JUMP_SPEED
            self.on_ground = False
        
        # 垂直移动
        self.rect.y += self.vel_y
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vel_y > 0:
                    self.rect.bottom = plat.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = plat.bottom
                    self.vel_y = 0
        
        # 边界限制
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(GAME_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)

class Enemy:
    def __init__(self, x, y, patrol_range=80):
        self.rect = pygame.Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT)
        self.vel_x = ENEMY_SPEED
        self.start_x = x
        self.patrol_range = patrol_range
        self.direction = 1
    
    def update(self, platforms):
        self.rect.x += self.vel_x * self.direction
        # 巡逻反转
        if self.rect.x > self.start_x + self.patrol_range:
            self.direction = -1
        elif self.rect.x < self.start_x - self.patrol_range:
            self.direction = 1
        
        # 地面检测
        on_ground = False
        test_rect = pygame.Rect(self.rect.x, self.rect.bottom + 1, self.rect.width, 2)
        for plat in platforms:
            if test_rect.colliderect(plat):
                on_ground = True
                break
        if not on_ground:
            self.direction *= -1
            self.rect.x += self.vel_x * self.direction

class Flag:
    def __init__(self):
        self.rect = pygame.Rect(0, GAME_HEIGHT - 250, 20, 250)

if __name__ == "__main__":
    game = Game()
    game.run()