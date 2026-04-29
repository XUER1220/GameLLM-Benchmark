import pygame
import sys
import random

# 初始化随机种子
random.seed(42)

# ========== 常量定义 ==========
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

WORLD_WIDTH = 3200
WORLD_HEIGHT = 600

PLAYER_WIDTH = 32
PLAYER_HEIGHT = 48
PLAYER_SPEED = 5
JUMP_SPEED = -12
GRAVITY = 0.5

GROUND_HEIGHT = 64

COIN_SIZE = 18
ENEMY_SIZE = 32

LIVES_START = 3

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE_SKY = (135, 206, 235)
GREEN_GRASS = (76, 175, 80)
BROWN_GROUND = (139, 69, 19)
RED_PLAYER = (255, 0, 0)
YELLOW_COIN = (255, 255, 0)
GRAY_BRICK = (140, 140, 140)
CYAN_QUESTION = (0, 255, 255)
GREEN_PIPE = (0, 180, 0)
PURPLE_ENEMY = (128, 0, 128)
GREEN_FLAGPOLE = (20, 200, 20)
RED_FLAG = (255, 50, 50)

# 关卡元素坐标 (都是矩形，格式 (x, y, width, height))
GROUND_RECTS = [
    (0, WORLD_HEIGHT - GROUND_HEIGHT, WORLD_WIDTH, GROUND_HEIGHT)
]

BRICKS = [
    (200, 400, 32, 32), (232, 400, 32, 32), (264, 400, 32, 32),
    (400, 350, 32, 32), (432, 350, 32, 32),
    (500, 300, 32, 32), (532, 300, 32, 32),
    (800, 400, 32, 32), (832, 400, 32, 32),
    (1000, 350, 32, 32), (1032, 350, 32, 32),
    (1200, 400, 32, 32)
]

QUESTION_BLOCKS = [
    (300, 350, 32, 32), (332, 350, 32, 32),
    (600, 300, 32, 32), (632, 300, 32, 32),
    (900, 350, 32, 32), (932, 350, 32, 32)
]

PIPES = [
    (700, WORLD_HEIGHT - GROUND_HEIGHT - 96, 64, 96),
    (1100, WORLD_HEIGHT - GROUND_HEIGHT - 64, 64, 64),
    (1400, WORLD_HEIGHT - GROUND_HEIGHT - 128, 64, 128)
]

STAIRS = [
    (2500, WORLD_HEIGHT - GROUND_HEIGHT - 32, 32, 32),
    (2532, WORLD_HEIGHT - GROUND_HEIGHT - 64, 32, 64),
    (2564, WORLD_HEIGHT - GROUND_HEIGHT - 96, 32, 96)
]

COINS = [
    (220, 360, COIN_SIZE, COIN_SIZE), (252, 360, COIN_SIZE, COIN_SIZE), (284, 360, COIN_SIZE, COIN_SIZE),
    (320, 320, COIN_SIZE, COIN_SIZE), (352, 320, COIN_SIZE, COIN_SIZE),
    (510, 270, COIN_SIZE, COIN_SIZE), (542, 270, COIN_SIZE, COIN_SIZE),
    (810, 360, COIN_SIZE, COIN_SIZE), (842, 360, COIN_SIZE, COIN_SIZE),
    (1010, 320, COIN_SIZE, COIN_SIZE), (1042, 320, COIN_SIZE, COIN_SIZE),
    (1210, 360, COIN_SIZE, COIN_SIZE)
]

ENEMIES = []
for i, x in enumerate([450, 950, 1500]):
    ENEMIES.append({
        'rect': pygame.Rect(x, WORLD_HEIGHT - GROUND_HEIGHT - ENEMY_SIZE, ENEMY_SIZE, ENEMY_SIZE),
        'speed': 2 if i % 2 == 0 else -2,
        'alive': True
    })

FLAGPOLE = pygame.Rect(WORLD_WIDTH - 100, WORLD_HEIGHT - GROUND_HEIGHT - 200, 16, 200)

PITS = [
    (1300, WORLD_HEIGHT - GROUND_HEIGHT, 150, GROUND_HEIGHT),
    (1800, WORLD_HEIGHT - GROUND_HEIGHT, 150, GROUND_HEIGHT)
]

class Player:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.rect = pygame.Rect(50, WORLD_HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.lives = LIVES_START
        self.score = 0
        self.coins = 0
        self.won = False
        self.dead = False
    
    def update(self, platforms, pits, enemies):
        if self.dead or self.won:
            return
        
        # 水平移动
        self.rect.x += self.vx
        
        # 水平碰撞检测
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vx > 0:
                    self.rect.right = plat.left
                elif self.vx < 0:
                    self.rect.left = plat.right
        
        # 垂直移动
        self.vy += GRAVITY
        self.rect.y += self.vy
        self.on_ground = False
        
        # 垂直碰撞检测
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vy > 0:
                    self.rect.bottom = plat.top
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = plat.bottom
                    self.vy = 0
        
        # 坑洞检测
        for pit in pits:
            if self.rect.colliderect(pit):
                self.lose_life(platforms)
                return
        
        # 敌人碰撞
        for enemy in enemies:
            if not enemy['alive']:
                continue
            if self.rect.colliderect(enemy['rect']):
                if self.vy > 0 and self.rect.bottom - self.vy < enemy['rect'].top + 10:
                    # 踩到敌人
                    enemy['alive'] = False
                    self.score += 200
                    self.vy = JUMP_SPEED * 0.5
                else:
                    self.lose_life(platforms)
                break
        
        # 屏幕底部以下
        if self.rect.top >= WORLD_HEIGHT:
            self.lose_life(platforms)
        
        # 旗杆碰撞
        if self.rect.colliderect(FLAGPOLE):
            if not self.dead:
                self.won = True
    
    def lose_life(self, platforms):
        self.lives -= 1
        if self.lives <= 0:
            self.dead = True
        else:
            # 回到最近的安全位置（左侧第一个平台）
            self.rect.x = 50
            self.rect.y = WORLD_HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT
            self.vx = 0
            self.vy = 0
            self.on_ground = True
    
    def handle_input(self, keys):
        self.vx = 0
        if keys[pygame.K_LEFT]:
            self.vx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.vx += PLAYER_SPEED
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = JUMP_SPEED
            self.on_ground = False

class Camera:
    def __init__(self):
        self.x = 0
    
    def update(self, player_rect):
        target_x = player_rect.centerx - SCREEN_WIDTH // 2
        self.x = max(0, min(target_x, WORLD_WIDTH - SCREEN_WIDTH))
    
    def apply(self, rect):
        return pygame.Rect(rect.x - self.x, rect.y, rect.width, rect.height)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Super Mario Bros 1-1 Medium")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    
    def get_platforms():
        plat = GROUND_RECTS[:]
        plat.extend(BRICKS)
        plat.extend(QUESTION_BLOCKS)
        plat.extend(PIPES)
        plat.extend(STAIRS)
        return [pygame.Rect(*p) for p in plat]
    
    def get_pits():
        return [pygame.Rect(*p) for p in PITS]
    
    def reset_game():
        new_player = Player()
        new_enemies = []
        for i, x in enumerate([450, 950, 1500]):
            new_enemies.append({
                'rect': pygame.Rect(x, WORLD_HEIGHT - GROUND_HEIGHT - ENEMY_SIZE, ENEMY_SIZE, ENEMY_SIZE),
                'speed': 2 if i % 2 == 0 else -2,
                'alive': True
            })
        return new_player, new_enemies
    
    player, enemies = reset_game()
    camera = Camera()
    platforms = get_platforms()
    pits = get_pits()
    
    running = True
    while running:
        clock.tick(FPS)
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    player, enemies = reset_game()
                    camera = Camera()
        
        # 玩家输入
        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        
        # 更新敌人
        for enemy in enemies:
            if enemy['alive']:
                enemy['rect'].x += enemy['speed']
                # 碰撞检测
                for plat in platforms:
                    if enemy['rect'].colliderect(plat):
                        if enemy['speed'] > 0:
                            enemy['rect'].right = plat.left
                            enemy['speed'] = -enemy['speed']
                        else:
                            enemy['rect'].left = plat.right
                            enemy['speed'] = -enemy['speed']
                # 坑洞边缘检测
                if enemy['rect'].right >= WORLD_WIDTH or enemy['rect'].left <= 0:
                    enemy['speed'] = -enemy['speed']
        
        # 更新玩家
        player.update(platforms, pits, enemies)
        
        # 金币收集
        coins_to_remove = []
        for coin_rect in COINS:
            if player.rect.colliderect(pygame.Rect(*coin_rect)):
                coins_to_remove.append(coin_rect)
                player.score += 100
                player.coins += 1
        # 这里只是演示，实际上COINS是常量不会删除
        
        # 更新摄像机
        camera.update(player.rect)
        
        # 绘制
        screen.fill(BLUE_SKY)
        
        # 绘制地面和平台
        for plat in platforms:
            rect = camera.apply(pygame.Rect(*plat) if isinstance(plat, tuple) else plat)
            pygame.draw.rect(screen, BROWN_GROUND, rect)
        
        # 绘制砖块
        for brick in BRICKS:
            rect = camera.apply(pygame.Rect(*brick))
            pygame.draw.rect(screen, GRAY_BRICK, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
        
        # 绘制问号块
        for qblock in QUESTION_BLOCKS:
            rect = camera.apply(pygame.Rect(*qblock))
            pygame.draw.rect(screen, CYAN_QUESTION, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            pygame.draw.circle(screen, BLACK, rect.center, 6)
        
        # 绘制管道
        for pipe in PIPES:
            rect = camera.apply(pygame.Rect(*pipe))
            pygame.draw.rect(screen, GREEN_PIPE, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
        
        # 绘制台阶
        for stair in STAIRS:
            rect = camera.apply(pygame.Rect(*stair))
            pygame.draw.rect(screen, BROWN_GROUND, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
        
        # 绘制坑洞
        for pit in pits:
            rect = camera.apply(pit)
            pygame.draw.rect(screen, BLACK, rect)
        
        # 绘制金币
        for coin in COINS:
            if coin not in coins_to_remove:
                rect = camera.apply(pygame.Rect(*coin))
                pygame.draw.circle(screen, YELLOW_COIN, rect.center, COIN_SIZE//2)
                pygame.draw.circle(screen, BLACK, rect.center, COIN_SIZE//2, 2)
        
        # 绘制敌人
        for enemy in enemies:
            if enemy['alive']:
                rect = camera.apply(enemy['rect'])
                pygame.draw.rect(screen, PURPLE_ENEMY, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)
                # 简单的眼睛
                eye_x = rect.left + 8 if enemy['speed'] > 0 else rect.right - 8
                pygame.draw.circle(screen, WHITE, (eye_x, rect.top + 10), 4)
                pygame.draw.circle(screen, BLACK, (eye_x, rect.top + 10), 2)
        
        # 绘制旗杆
        flag_rect = camera.apply(FLAGPOLE)
        pygame.draw.rect(screen, GREEN_FLAGPOLE, flag_rect)
        flag = pygame.Rect(flag_rect.right, flag_rect.top, 40, 30)
        pygame.draw.rect(screen, RED_FLAG, flag)
        pygame.draw.rect(screen, BLACK, flag, 1)
        
        # 绘制玩家
        player_rect = camera.apply(player.rect)
        pygame.draw.rect(screen, RED_PLAYER, player_rect)
        pygame.draw.rect(screen, BLACK, player_rect, 2)
        
        # 绘制HUD（固定位置）
        hud_y = 10
        lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
        score_text = font.render(f"Score: {player.score}", True, WHITE)
        coins_text = font.render(f"Coins: {player.coins}", True, WHITE)
        screen.blit(lives_text, (10, hud_y))
        screen.blit(score_text, (200, hud_y))
        screen.blit(coins_text, (400, hud_y))
        
        # 游戏结束提示
        if player.dead:
            game_over = font.render("GAME OVER", True, WHITE)
            screen.blit(game_over, (SCREEN_WIDTH//2 - game_over.get_width()//2, SCREEN_HEIGHT//2 - 50))
        elif player.won:
            you_win = font.render("YOU WIN!", True, WHITE)
            screen.blit(you_win, (SCREEN_WIDTH//2 - you_win.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        # 通用提示
        restart_text = font.render("Press R to Restart, ESC to Quit", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT - 40))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()