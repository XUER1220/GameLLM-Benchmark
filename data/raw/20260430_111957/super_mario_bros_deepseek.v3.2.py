import pygame
import random
import sys

# 初始化随机种子
random.seed(42)

# 窗口常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 颜色常量
COLOR_BACKGROUND = (107, 140, 255)  # 天空蓝
COLOR_GROUND = (118, 66, 0)         # 棕色地面
COLOR_BRICK = (178, 34, 34)         # 砖红色
COLOR_QUESTION = (255, 215, 0)      # 金黄色问号块
COLOR_PIPE = (0, 100, 0)            # 绿色管道
COLOR_STAIR = (139, 69, 19)         # 棕色台阶
COLOR_PLAYER = (255, 0, 0)          # 红色玩家
COLOR_ENEMY = (0, 0, 0)             # 黑色敌人
COLOR_COIN = (255, 223, 0)          # 金币黄
COLOR_FLAG = (255, 255, 255)        # 白色旗杆
COLOR_FLAG_FLAG = (0, 0, 255)       # 蓝色旗面
COLOR_TEXT = (255, 255, 255)        # 白色文本
COLOR_HUD_BG = (50, 50, 50, 180)    # 半透明HUD背景

# 游戏常量
WORLD_WIDTH = 3200
WORLD_HEIGHT = 600
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 48
INITIAL_LIVES = 3
PLAYER_SPEED = 5
JUMP_SPEED = -12
GRAVITY = 0.5

ENEMY_WIDTH = 32
ENEMY_HEIGHT = 32
ENEMY_SPEED = 2

COIN_SIZE = 18
COIN_SCORE = 100
ENEMY_SCORE = 200

# 关卡元素布局（位置x,y,宽度,高度）
GROUND_Y = WORLD_HEIGHT - 100
GROUND_HEIGHT = 100
GROUND = [(0, GROUND_Y, WORLD_WIDTH, GROUND_HEIGHT)]

BRICKS = [
    # 第一组砖块
    (300, GROUND_Y - 32, 32, 32),
    (332, GROUND_Y - 32, 32, 32),
    (364, GROUND_Y - 32, 32, 32),
    # 第二组问号块和砖块
    (500, GROUND_Y - 64, 32, 32),
    (532, GROUND_Y - 64, 32, 32),
    (564, GROUND_Y - 64, 32, 32),
    (596, GROUND_Y - 32, 32, 32),
    (628, GROUND_Y - 32, 32, 32),
    # 第三组砖块（平台上）
    (850, GROUND_Y - 160, 32, 32),
    (882, GROUND_Y - 160, 32, 32),
    (914, GROUND_Y - 160, 32, 32),
    (946, GROUND_Y - 160, 32, 32)
]

QUESTIONS = [
    (400, GROUND_Y - 96, 32, 32),
    (432, GROUND_Y - 96, 32, 32),
    (464, GROUND_Y - 96, 32, 32)
]

PIPES = [
    (700, GROUND_Y - 96, 64, 96),
    (1100, GROUND_Y - 128, 64, 128)
]

STAIRS = [
    (1500, GROUND_Y - 160, 128, 32),
    (1500, GROUND_Y - 128, 96, 32),
    (1500, GROUND_Y - 96, 64, 32),
    (1500, GROUND_Y - 64, 32, 32)
]

ENEMIES_POS = [
    (600, GROUND_Y - ENEMY_HEIGHT),
    (1000, GROUND_Y - ENEMY_HEIGHT),
    (1400, GROUND_Y - ENEMY_HEIGHT)
]

COINS_POS = [
    (300, GROUND_Y - 80),
    (332, GROUND_Y - 80),
    (364, GROUND_Y - 80),
    (400, GROUND_Y - 128),
    (432, GROUND_Y - 128),
    (464, GROUND_Y - 128),
    (500, GROUND_Y - 96),
    (532, GROUND_Y - 96),
    (564, GROUND_Y - 96),
    (850, GROUND_Y - 192),
    (882, GROUND_Y - 192),
    (914, GROUND_Y - 192)
]

FLAG_POS = (3000, GROUND_Y - 200)
FLAG_WIDTH = 20
FLAG_HEIGHT = 200

# 坑洞定义（开始x, 结束x）
PITS = [
    (1200, 1300),
    (1800, 1900)
]

class Player:
    def __init__(self):
        self.rect = pygame.Rect(50, GROUND_Y - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.lives = INITIAL_LIVES
        self.score = 0
        self.coins = 0
        self.dead = False
        self.won = False

    def update(self, platforms, enemies, coins, flag_rect, pits):
        # 水平移动
        self.rect.x += self.vel_x
        # 限制在世界边界
        self.rect.x = max(0, min(WORLD_WIDTH - PLAYER_WIDTH, self.rect.x))

        # 水平碰撞检测
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vel_x > 0:
                    self.rect.right = plat.left
                elif self.vel_x < 0:
                    self.rect.left = plat.right

        # 垂直移动
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        self.on_ground = False

        # 垂直碰撞检测
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vel_y > 0:
                    self.rect.bottom = plat.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = plat.bottom
                    self.vel_y = 0

        # 金币收集
        for coin in coins[:]:
            if self.rect.colliderect(coin):
                coins.remove(coin)
                self.score += COIN_SCORE
                self.coins += 1

        # 敌人碰撞
        for enemy in enemies[:]:
            if self.rect.colliderect(enemy.rect):
                # 从上方踩到
                if self.vel_y > 0 and self.rect.bottom < enemy.rect.bottom + 10:
                    enemies.remove(enemy)
                    self.score += ENEMY_SCORE
                    self.vel_y = JUMP_SPEED * 0.7  # 反弹
                else:
                    # 侧面碰撞，失去生命
                    self.lives -= 1
                    self.respawn(platforms)
                    if self.lives <= 0:
                        self.dead = True
                    break

        # 坑洞检测
        for pit_start, pit_end in pits:
            if pit_start <= self.rect.centerx <= pit_end and self.rect.bottom >= GROUND_Y:
                self.lives -= 1
                self.respawn(platforms)
                if self.lives <= 0:
                    self.dead = True
                break

        # 掉落世界底部
        if self.rect.top > WORLD_HEIGHT:
            self.lives -= 1
            self.respawn(platforms)
            if self.lives <= 0:
                self.dead = True

        # 到达旗杆
        if self.rect.colliderect(flag_rect) and not self.dead:
            self.won = True

    def respawn(self, platforms):
        # 找到最近的安全位置（左侧最近的平台）
        safe_x = 50
        for plat in platforms:
            if plat.y == GROUND_Y and plat.left <= self.rect.centerx <= plat.right:
                safe_x = plat.left
                break
        self.rect.x = safe_x
        self.rect.y = GROUND_Y - PLAYER_HEIGHT
        self.vel_x = 0
        self.vel_y = 0

    def draw(self, screen, camera_x):
        # 绘制玩家
        pygame.draw.rect(screen, COLOR_PLAYER, (self.rect.x - camera_x, self.rect.y, self.rect.width, self.rect.height))
        # 简单眼睛
        eye_x = self.rect.right - 10 if self.facing_right else self.rect.left + 10
        pygame.draw.circle(screen, (255, 255, 255), (eye_x - camera_x, self.rect.y + 15), 4)

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT)
        self.vel_x = ENEMY_SPEED * random.choice([-1, 1])
        self.start_x = x

    def update(self, platforms):
        self.rect.x += self.vel_x
        # 简单巡逻范围
        if abs(self.rect.x - self.start_x) > 100:
            self.vel_x *= -1

        # 防止掉落边缘
        on_platform = False
        test_rect = pygame.Rect(self.rect.x, self.rect.bottom + 1, self.rect.width, 2)
        for plat in platforms:
            if test_rect.colliderect(plat):
                on_platform = True
                break
        if not on_platform:
            self.vel_x *= -1

        # 水平碰撞反转
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vel_x > 0:
                    self.rect.right = plat.left
                    self.vel_x *= -1
                elif self.vel_x < 0:
                    self.rect.left = plat.right
                    self.vel_x *= -1

    def draw(self, screen, camera_x):
        pygame.draw.rect(screen, COLOR_ENEMY, (self.rect.x - camera_x, self.rect.y, self.rect.width, self.rect.height))
        # 简单眼睛
        pygame.draw.circle(screen, (255, 255, 255), (self.rect.x + 8 - camera_x, self.rect.y + 10), 4)
        pygame.draw.circle(screen, (255, 255, 255), (self.rect.right - 8 - camera_x, self.rect.y + 10), 4)

def create_platforms():
    platforms = []
    # 地面
    for g in GROUND:
        platforms.append(pygame.Rect(*g))
    # 砖块
    for b in BRICKS:
        platforms.append(pygame.Rect(*b))
    # 问号块
    for q in QUESTIONS:
        platforms.append(pygame.Rect(*q))
    # 管道
    for p in PIPES:
        platforms.append(pygame.Rect(*p))
    # 台阶
    for s in STAIRS:
        platforms.append(pygame.Rect(*s))
    return platforms

def create_coins():
    coins = []
    for pos in COINS_POS:
        coin_rect = pygame.Rect(pos[0], pos[1], COIN_SIZE, COIN_SIZE)
        coins.append(coin_rect)
    return coins

def create_enemies():
    enemies = []
    for pos in ENEMIES_POS:
        enemies.append(Enemy(pos[0], pos[1]))
    return enemies

def draw_hud(screen, player, font):
    hud_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 40)
    pygame.draw.rect(screen, COLOR_HUD_BG, hud_rect)

    lives_text = font.render(f"Lives: {player.lives}", True, COLOR_TEXT)
    score_text = font.render(f"Score: {player.score}", True, COLOR_TEXT)
    coins_text = font.render(f"Coins: {player.coins}", True, COLOR_TEXT)

    screen.blit(lives_text, (10, 5))
    screen.blit(score_text, (150, 5))
    screen.blit(coins_text, (300, 5))

def draw_game_over(screen, player, font, big_font):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    if player.won:
        text = big_font.render("You Win!", True, (0, 255, 0))
    else:
        text = big_font.render("Game Over", True, (255, 0, 0))
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 200))

    score_text = font.render(f"Final Score: {player.score}", True, COLOR_TEXT)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 280))

    restart_text = font.render("Press R to Restart", True, COLOR_TEXT)
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 350))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Super Mario Bros Medium")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    big_font = pygame.font.SysFont(None, 72)

    # 游戏初始化
    platforms = create_platforms()
    coins = create_coins()
    enemies = create_enemies()
    flag_rect = pygame.Rect(FLAG_POS[0], FLAG_POS[1], FLAG_WIDTH, FLAG_HEIGHT)
    player = Player()
    camera_x = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and (player.dead or player.won):
                    # 重置游戏
                    platforms = create_platforms()
                    coins = create_coins()
                    enemies = create_enemies()
                    player = Player()
                    camera_x = 0
                elif event.key == pygame.K_SPACE and player.on_ground and not player.dead and not player.won:
                    player.vel_y = JUMP_SPEED

        # 玩家输入
        keys = pygame.key.get_pressed()
        if not player.dead and not player.won:
            if keys[pygame.K_LEFT]:
                player.vel_x = -PLAYER_SPEED
                player.facing_right = False
            elif keys[pygame.K_RIGHT]:
                player.vel_x = PLAYER_SPEED
                player.facing_right = True
            else:
                player.vel_x = 0

        # 更新
        if not player.dead and not player.won:
            player.update(platforms, enemies, coins, flag_rect, PITS)
            for enemy in enemies:
                enemy.update(platforms)

        # 相机跟随
        if not player.dead and not player.won:
            target_x = player.rect.centerx - SCREEN_WIDTH // 2
            camera_x = max(0, min(target_x, WORLD_WIDTH - SCREEN_WIDTH))

        # 绘制
        screen.fill(COLOR_BACKGROUND)

        # 绘制地面和平台
        for plat in platforms:
            color = COLOR_GROUND
            if plat in [pygame.Rect(*b) for b in BRICKS]:
                color = COLOR_BRICK
            elif plat in [pygame.Rect(*q) for q in QUESTIONS]:
                color = COLOR_QUESTION
            elif plat in [pygame.Rect(*p) for p in PIPES]:
                color = COLOR_PIPE
            elif plat in [pygame.Rect(*s) for s in STAIRS]:
                color = COLOR_STAIR
            pygame.draw.rect(screen, color, (plat.x - camera_x, plat.y, plat.width, plat.height))
            if color == COLOR_BRICK or color == COLOR_QUESTION:
                pygame.draw.rect(screen, (0, 0, 0), (plat.x - camera_x, plat.y, plat.width, plat.height), 2)

        # 绘制坑洞
        for pit_start, pit_end in PITS:
            pygame.draw.rect(screen, COLOR_BACKGROUND, (pit_start - camera_x, GROUND_Y, pit_end - pit_start, GROUND_HEIGHT))

        # 绘制金币
        for coin in coins:
            pygame.draw.ellipse(screen, COLOR_COIN, (coin.x - camera_x, coin.y, coin.width, coin.height))
            pygame.draw.ellipse(screen, (0, 0, 0), (coin.x - camera_x, coin.y, coin.width, coin.height), 2)

        # 绘制敌人
        for enemy in enemies:
            enemy.draw(screen, camera_x)

        # 绘制旗杆
        pygame.draw.rect(screen, COLOR_FLAG, (flag_rect.x - camera_x, flag_rect.y, flag_rect.width, flag_rect.height))
        flag_points = [
            (flag_rect.x - camera_x + flag_rect.width, flag_rect.y + 30),
            (flag_rect.x - camera_x + flag_rect.width + 60, flag_rect.y + 50),
            (flag_rect.x - camera_x + flag_rect.width, flag_rect.y + 70)
        ]
        pygame.draw.polygon(screen, COLOR_FLAG_FLAG, flag_points)

        # 绘制玩家
        player.draw(screen, camera_x)

        # 绘制HUD
        draw_hud(screen, player, font)

        # 游戏结束画面
        if player.dead or player.won:
            draw_game_over(screen, player, font, big_font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()