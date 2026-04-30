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
BACKGROUND_COLOR = (95, 175, 255)
GROUND_COLOR = (94, 53, 19)
BRICK_COLOR = (180, 40, 40)
QUESTION_COLOR = (255, 180, 30)
PIPE_COLOR = (40, 180, 40)
STAIR_COLOR = (200, 150, 100)
PLAYER_COLOR = (255, 30, 30)
ENEMY_COLOR = (0, 0, 0)
COIN_COLOR = (255, 230, 0)
FLAG_COLOR = (255, 255, 255)
FLAG_POLE_COLOR = (150, 150, 150)
HUD_BG_COLOR = (30, 30, 30, 180)
HUD_TEXT_COLOR = (255, 255, 255)
DEATH_COLOR = (255, 50, 50, 200)
WIN_COLOR = (50, 255, 50, 200)
BLACK = (0, 0, 0)

# 游戏常量
WORLD_WIDTH = 3200
WORLD_HEIGHT = 600
GRAVITY = 0.5
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 48
PLAYER_SPEED = 5
PLAYER_JUMP_SPEED = -12
ENEMY_SIZE = 32
COIN_SIZE = 18
GROUND_Y = WORLD_HEIGHT - 64  # 地面顶部Y坐标
TILE_SIZE = 32

# 初始位置
PLAYER_START_X = 100
PLAYER_START_Y = GROUND_Y - PLAYER_HEIGHT

class Player:
    def __init__(self):
        self.rect = pygame.Rect(PLAYER_START_X, PLAYER_START_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.lives = 3
        self.score = 0
        self.coins = 0
        self.dead = False
        self.won = False

    def handle_input(self, keys):
        if self.dead or self.won:
            return
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = PLAYER_JUMP_SPEED
            self.on_ground = False

    def update(self, platforms, holes, enemies, coins, flag):
        if self.dead or self.won:
            return

        # 水平移动
        self.rect.x += self.vel_x
        # 边界检查
        self.rect.x = max(0, min(self.rect.x, WORLD_WIDTH - self.rect.width))

        # 水平碰撞
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vel_x > 0:
                    self.rect.right = plat.left
                elif self.vel_y < 0:
                    self.rect.left = plat.right

        # 垂直移动和重力
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        self.on_ground = False

        # 垂直碰撞
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vel_y > 0:
                    self.rect.bottom = plat.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = plat.bottom
                    self.vel_y = 0

        # 检查坑洞
        for hole in holes:
            if self.rect.colliderect(hole):
                self.lose_life()
                return

        # 检查屏幕底部
        if self.rect.top >= WORLD_HEIGHT:
            self.lose_life()
            return

        # 收集金币
        for coin in coins[:]:
            if self.rect.colliderect(coin):
                coins.remove(coin)
                self.score += 100
                self.coins += 1

        # 敌人碰撞
        for enemy in enemies[:]:
            if self.rect.colliderect(enemy):
                if self.vel_y > 0 and self.rect.bottom <= enemy.rect.top + 10:
                    enemies.remove(enemy)
                    self.score += 200
                    self.vel_y = PLAYER_JUMP_SPEED * 0.7
                else:
                    self.lose_life()
                break

        # 检查旗杆
        if not self.won and self.rect.colliderect(flag):
            self.won = True

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.dead = True
        else:
            self.rect.x = PLAYER_START_X
            self.rect.y = PLAYER_START_Y
            self.vel_x = 0
            self.vel_y = 0

    def reset(self):
        self.rect.x = PLAYER_START_X
        self.rect.y = PLAYER_START_Y
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.lives = 3
        self.score = 0
        self.coins = 0
        self.dead = False
        self.won = False

class Enemy:
    def __init__(self, x, y, platform_left, platform_right):
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        self.speed = random.choice([-1.5, 1.5])
        self.platform_left = platform_left
        self.platform_right = platform_right

    def update(self, platforms):
        self.rect.x += self.speed
        # 平台边界检查
        if self.rect.left <= self.platform_left:
            self.rect.left = self.platform_left
            self.speed = abs(self.speed)
        elif self.rect.right >= self.platform_right:
            self.rect.right = self.platform_right
            self.speed = -abs(self.speed)

        # 简单的地面追踪
        on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat) and self.rect.bottom <= plat.top + 5:
                on_ground = True
                break
        if not on_ground:
            self.speed *= -1

def create_world():
    platforms = []
    coins = []
    enemies = []
    holes = []

    # 地面
    platforms.append(pygame.Rect(0, GROUND_Y, WORLD_WIDTH, 64))

    # 砖块和问号块 (12个)
    brick_positions = [(200, GROUND_Y - 64), (232, GROUND_Y - 64), (264, GROUND_Y - 64),
                       (350, GROUND_Y - 96), (382, GROUND_Y - 96), (414, GROUND_Y - 96),
                       (500, GROUND_Y - 64), (532, GROUND_Y - 64),
                       (600, GROUND_Y - 96), (632, GROUND_Y - 96)]
    for x, y in brick_positions:
        platforms.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))

    question_positions = [(300, GROUND_Y - 96), (332, GROUND_Y - 96)]
    for x, y in question_positions:
        platforms.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))

    # 管道和台阶 (4个)
    platforms.append(pygame.Rect(700, GROUND_Y - 96, 64, 96))
    platforms.append(pygame.Rect(900, GROUND_Y - 64, 64, 64))
    platforms.append(pygame.Rect(1100, GROUND_Y - 128, 32, 128))
    platforms.append(pygame.Rect(1300, GROUND_Y - 96, 64, 96))

    # 坑洞 (2个)
    holes.append(pygame.Rect(800, GROUND_Y, 100, 64))
    holes.append(pygame.Rect(1200, GROUND_Y, 100, 64))

    # 金币 (12个)
    for i in range(6):
        coins.append(pygame.Rect(250 + i*30, GROUND_Y - 120, COIN_SIZE, COIN_SIZE))
    for i in range(6):
        coins.append(pygame.Rect(550 + i*30, GROUND_Y - 160, COIN_SIZE, COIN_SIZE))

    # 敌人 (3个)
    enemies.append(Enemy(400, GROUND_Y - ENEMY_SIZE, 350, 500))
    enemies.append(Enemy(750, GROUND_Y - ENEMY_SIZE - 64, 700, 850))
    enemies.append(Enemy(1150, GROUND_Y - ENEMY_SIZE, 1100, 1250))

    # 终点旗杆
    flag_x = WORLD_WIDTH - 150
    flag_rect = pygame.Rect(flag_x + 10, GROUND_Y - 200, 20, 200)

    return platforms, coins, enemies, holes, flag_rect

def draw(win, player, platforms, coins, enemies, holes, flag, camera_x):
    win.fill(BACKGROUND_COLOR)

    # 绘制地面和平台
    for plat in platforms:
        pygame.draw.rect(win, GROUND_COLOR, (plat.x - camera_x, plat.y, plat.width, plat.height))
        # 顶部草皮
        if plat.y == GROUND_Y:
            pygame.draw.rect(win, (80, 150, 30), (plat.x - camera_x, plat.y, plat.width, 8))

    # 绘制砖块和问号块
    for plat in platforms:
        if plat.height == TILE_SIZE:
            if plat.x in [200, 232, 264, 500, 532]:
                pygame.draw.rect(win, BRICK_COLOR, (plat.x - camera_x, plat.y, plat.width, plat.height))
                pygame.draw.rect(win, (150, 30, 30), (plat.x - camera_x, plat.y, plat.width, plat.height), 2)
            elif plat.x in [300, 332]:
                pygame.draw.rect(win, QUESTION_COLOR, (plat.x - camera_x, plat.y, plat.width, plat.height))
                pygame.draw.rect(win, (200, 150, 0), (plat.x - camera_x, plat.y, plat.width, plat.height), 2)
                # 问号图案
                pygame.draw.rect(win, BLACK, (plat.x - camera_x + 12, plat.y + 8, 8, 8))
                pygame.draw.rect(win, BLACK, (plat.x - camera_x + 8, plat.y + 20, 16, 4))

    # 绘制管道和台阶
    for plat in platforms:
        if plat.width >= 64:  # 管道
            pygame.draw.rect(win, PIPE_COLOR, (plat.x - camera_x, plat.y, plat.width, plat.height))
            pygame.draw.rect(win, (30, 120, 30), (plat.x - camera_x, plat.y, plat.width, plat.height), 3)
        elif plat.width == 32:  # 细台阶
            pygame.draw.rect(win, STAIR_COLOR, (plat.x - camera_x, plat.y, plat.width, plat.height))
            pygame.draw.rect(win, (150, 100, 80), (plat.x - camera_x, plat.y, plat.width, plat.height), 2)

    # 绘制坑洞
    for hole in holes:
        pygame.draw.rect(win, BLACK, (hole.x - camera_x, hole.y, hole.width, hole.height))

    # 绘制金币
    for coin in coins:
        pygame.draw.circle(win, COIN_COLOR, (coin.centerx - camera_x, coin.centery), COIN_SIZE//2)
        pygame.draw.circle(win, (200, 180, 0), (coin.centerx - camera_x, coin.centery), COIN_SIZE//2, 2)

    # 绘制敌人
    for enemy in enemies:
        pygame.draw.rect(win, ENEMY_COLOR, (enemy.rect.x - camera_x, enemy.rect.y, enemy.rect.width, enemy.rect.height))
        # 眼睛
        pygame.draw.rect(win, (255, 255, 255), (enemy.rect.x - camera_x + 8, enemy.rect.y + 8, 6, 6))
        pygame.draw.rect(win, (255, 255, 255), (enemy.rect.x - camera_x + 18, enemy.rect.y + 8, 6, 6))

    # 绘制旗杆
    pygame.draw.rect(win, FLAG_POLE_COLOR, (flag.x - camera_x, flag.y, flag.width, flag.height))
    pygame.draw.rect(win, (100, 100, 100), (flag.x - camera_x, flag.y, flag.width, flag.height), 3)
    flag_top = pygame.Rect(flag.x - camera_x - 40, flag.y + 20, 50, 30)
    pygame.draw.rect(win, FLAG_COLOR, flag_top)
    pygame.draw.rect(win, BLACK, flag_top, 2)

    # 绘制玩家
    if not player.dead:
        pygame.draw.rect(win, PLAYER_COLOR, (player.rect.x - camera_x, player.rect.y, player.rect.width, player.rect.height))
        # 简单面部
        pygame.draw.rect(win, BLACK, (player.rect.x - camera_x + 10, player.rect.y + 12, 6, 6))
        pygame.draw.rect(win, BLACK, (player.rect.x - camera_x + 16, player.rect.y + 12, 6, 6))
        # 帽子
        pygame.draw.rect(win, (200, 50, 50), (player.rect.x - camera_x, player.rect.y, player.rect.width, 10))

    # 绘制HUD
    hud_surface = pygame.Surface((SCREEN_WIDTH, 60), pygame.SRCALPHA)
    hud_surface.fill(HUD_BG_COLOR)
    win.blit(hud_surface, (0, 0))

    font = pygame.font.SysFont(None, 36)
    lives_text = font.render(f"Lives: {player.lives}", True, HUD_TEXT_COLOR)
    score_text = font.render(f"Score: {player.score}", True, HUD_TEXT_COLOR)
    coins_text = font.render(f"Coins: {player.coins}", True, HUD_TEXT_COLOR)

    win.blit(lives_text, (20, 15))
    win.blit(score_text, (200, 15))
    win.blit(coins_text, (400, 15))

    # 游戏结束画面
    if player.dead:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(DEATH_COLOR)
        win.blit(overlay, (0, 0))

        font_large = pygame.font.SysFont(None, 72)
        game_over = font_large.render("GAME OVER", True, BLACK)
        final_score = font.render(f"Final Score: {player.score}", True, BLACK)
        restart = font.render("Press R to Restart", True, BLACK)

        win.blit(game_over, (SCREEN_WIDTH//2 - game_over.get_width()//2, SCREEN_HEIGHT//2 - 60))
        win.blit(final_score, (SCREEN_WIDTH//2 - final_score.get_width()//2, SCREEN_HEIGHT//2))
        win.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, SCREEN_HEIGHT//2 + 60))

    elif player.won:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(WIN_COLOR)
        win.blit(overlay, (0, 0))

        font_large = pygame.font.SysFont(None, 72)
        win_text = font_large.render("YOU WIN!", True, BLACK)
        final_score = font.render(f"Final Score: {player.score}", True, BLACK)
        restart = font.render("Press R to Restart", True, BLACK)

        win.blit(win_text, (SCREEN_WIDTH//2 - win_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
        win.blit(final_score, (SCREEN_WIDTH//2 - final_score.get_width()//2, SCREEN_HEIGHT//2))
        win.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, SCREEN_HEIGHT//2 + 60))

def main():
    pygame.init()
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Super Mario Bros Medium")
    clock = pygame.time.Clock()

    player = Player()
    platforms, coins, enemies, holes, flag = create_world()

    running = True
    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    player.reset()
                    platforms, coins, enemies, holes, flag = create_world()

        keys = pygame.key.get_pressed()
        player.handle_input(keys)

        player.update(platforms, holes, enemies, coins, flag)

        for enemy in enemies:
            enemy.update(platforms)

        # 摄像机位置
        camera_x = max(0, min(player.rect.centerx - SCREEN_WIDTH//2, WORLD_WIDTH - SCREEN_WIDTH))

        draw(win, player, platforms, coins, enemies, holes, flag, camera_x)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()