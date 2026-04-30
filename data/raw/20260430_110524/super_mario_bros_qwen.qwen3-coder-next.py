import pygame
import random

# 固定常量
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
LEVEL_WIDTH = 3200
LEVEL_HEIGHT = 600
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 48
PLAYER_SPEED_X = 5
PLAYER_JUMP_VEL = -12
GRAVITY = 0.5
COIN_WIDTH = 18
COIN_HEIGHT = 18
ENEMY_WIDTH = 32
ENEMY_HEIGHT = 32
ENEMY_SPEED = 2
START_LIVES = 3
TOTAL_COINS = 12
TOTAL_ENEMIES = 3

# 颜色定义
COLOR_SKY = (135, 206, 235)
COLOR_GROUND = (160, 82, 45)
COLOR_BRICK = (160, 82, 45)
COLOR_QUESTION = (255, 215, 0)
COLOR_PIPE = (0, 128, 0)
COLOR_PIPE_LIP = (0, 100, 0)
COLOR_PLAYER = (255, 0, 0)
COLOR_ENEMY = (139, 69, 19)
COLOR_COIN = (255, 215, 0)
COLOR_FLAG_POLE = (255, 255, 255)
COLOR_FLAG_TOP = (255, 0, 0)
COLOR_UI_TEXT = (255, 255, 255)
COLOR_TEXT_BG = (0, 0, 0)

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_y = 0
        self.on_ground = False
        self.lives = START_LIVES
        self.score = 0
        self.coins = 0
        self.x_start = x
        self.y_start = y
        self.alive = True
        self.dead = False

    def update(self, platforms, enemies, coins, flag):
        # 水平移动
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED_X
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED_X

        # 碰撞检测：水平
        self.handle_platform_collision(platforms, horizontal=True)

        # 跳跃
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = PLAYER_JUMP_VEL
            self.on_ground = False

        # 垂直移动
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        self.on_ground = False  # 默认未在地面，碰撞后修正
        
        # 碰撞检测：垂直
        self.handle_platform_collision(platforms, horizontal=False)

        # 边界检查
        if self.rect.bottom > LEVEL_HEIGHT:
            self.die()

        # 收集金币
        for coin in coins[:]:
            if self.rect.colliderect(coin.rect):
                self.coins += 1
                self.score += 100
                coins.remove(coin)
        
        # 敌人 interaction
        for enemy in enemies[:]:
            if self.rect.colliderect(enemy.rect):
                # 踩头判定：玩家下落且位于敌人上方
                if self.vel_y > 0 and self.rect.bottom - self.vel_y <= enemy.rect.top + 5:
                    self.score += 200
                    enemies.remove(enemy)
                    self.vel_y = -8  # 踩后反弹
                else:
                    if self.alive:
                        self.die()

        # 旗杆判定
        if flag.check_terminate(self.rect):
            game_state["win"] = True
            game_state["end"] = True

    def handle_platform_collision(self, platforms, horizontal=False):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if horizontal:
                    if self.rect.right > platform.rect.left and self.rect.left < platform.rect.left:
                        self.rect.right = platform.rect.left
                    elif self.rect.left < platform.rect.right and self.rect.right > platform.rect.right:
                        self.rect.left = platform.rect.right
                else:
                    if self.vel_y > 0 and self.rect.bottom <= platform.rect.top + self.vel_y:
                        self.rect.bottom = platform.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0 and self.rect.top >= platform.rect.bottom + self.vel_y:
                        self.rect.top = platform.rect.bottom
                        self.vel_y = 0

    def die(self):
        if not self.dead:
            self.lives -= 1
            self.dead = True
            self.rect.x = self.x_start
            self.rect.y = self.y_start
            self.vel_y = 0
            self.on_ground = False
            game_state["camera_x"] = 0
            
            if self.lives <= 0:
                self.alive = False
                game_state["end"] = True
            else:
                # 稍后复活
                pass

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT)
        self.direction = 1
        self.speed = ENEMY_SPEED

    def update(self, platforms):
        self.rect.x += self.speed * self.direction

        # 检测是否走到平台尽头（在地面上才检测）
        if self.is_on_ground(platforms):
            # 检查前方是否有平台阻挡
            future_rect = self.rect.copy()
            if self.direction > 0:
                future_rect.x += 5
            else:
                future_rect.x -= 5
            
            collided = False
            for platform in platforms:
                if future_rect.colliderect(platform.rect):
                    collided = True
                    break
            
            if collided:
                self.direction *= -1
        else:
            self.direction *= -1

    def is_on_ground(self, platforms):
        test_rect = self.rect.copy()
        test_rect.y += 1
        for platform in platforms:
            if test_rect.colliderect(platform.rect) and platform.is_ground:
                return True
        return False

class Platform:
    def __init__(self, x, y, width, height, type="ground"):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = type
        self.is_ground = (type == "ground")

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, COIN_WIDTH, COIN_HEIGHT)
        self.collected = False

class Flag:
    def __init__(self, x, y):
        self.pole_x = x
        self.pole_y = y
        self.pole_height = 400
        self.rect = pygame.Rect(x, y - 20, 20, 20)

    def check_terminate(self, player_rect):
        # player touching the top of the flag
        return (player_rect.right >= self.pole_x and 
                player_rect.left <= self.pole_x + 20 and 
                player_rect.bottom >= self.pole_y - 20 and 
                player_rect.bottom <= self.pole_y + 20)

def create_level():
    platforms = []
    coins = []
    enemies = []

    # 地面
    platforms.append(Platform(0, 550, 600, 50, "ground"))
    platforms.append(Platform(700, 550, 300, 50, "ground"))
    platforms.append(Platform(1150, 550, 500, 50, "ground"))
    platforms.append(Platform(1800, 550, 200, 50, "ground"))
    platforms.append(Platform(2100, 550, 1100, 50, "ground"))  # 延伸到终点

    # 平地上砖块图案
    platforms.append(Platform(300, 400, 32, 32, "bricks"))
    platforms.append(Platform(332, 400, 32, 32, "question"))
    platforms.append(Platform(364, 400, 32, 32, "bricks"))
    platforms.append(Platform(480, 400, 32, 32, "bricks"))
    platforms.append(Platform(512, 400, 32, 32, "bricks"))
    platforms.append(Platform(544, 400, 32, 32, "bricks"))
    platforms.append(Platform(600, 250, 32, 32, "bricks"))
    platforms.append(Platform(2300, 300, 32, 32, "bricks"))
    platforms.append(Platform(2332, 300, 32, 32, "question"))
    platforms.append(Platform(2364, 300, 32, 32, "bricks"))
    platforms.append(Platform(2450, 300, 32, 32, "bricks"))
    platforms.append(Platform(2482, 300, 32, 32, "bricks"))

    # 管道
    platforms.append(Platform(480, 480, 64, 70, "pipe"))
    platforms.append(Platform(850, 450, 64, 100, "pipe"))
    platforms.append(Platform(1500, 480, 64, 70, "pipe"))
    platforms.append(Platform(2600, 400, 64, 150, "pipe"))

    # 小台阶
    platforms.append(Platform(1000, 450, 32, 32, "block"))
    platforms.append(Platform(1032, 450, 32, 32, "block"))
    platforms.append(Platform(1064, 450, 32, 32, "block"))
    platforms.append(Platform(1096, 450, 32, 32, "block"))

    platforms.append(Platform(1300, 400, 32, 32, "block"))
    platforms.append(Platform(1332, 400, 32, 32, "block"))
    platforms.append(Platform(1364, 400, 32, 32, "block"))
    platforms.append(Platform(1396, 400, 32, 32, "block"))
    platforms.append(Platform(1428, 400, 32, 32, "block"))

    platforms.append(Platform(2500, 400, 32, 32, "block"))
    platforms.append(Platform(2532, 400, 32, 32, "block"))
    platforms.append(Platform(2564, 400, 32, 32, "block"))
    platforms.append(Platform(2596, 400, 32, 32, "block"))
    platforms.append(Platform(2628, 400, 32, 32, "block"))
    platforms.append(Platform(2660, 400, 32, 32, "block"))
    platforms.append(Platform(2692, 400, 32, 32, "block"))
    platforms.append(Platform(2724, 400, 32, 32, "block"))
    platforms.append(Platform(2756, 400, 32, 32, "block"))
    platforms.append(Platform(2788, 400, 32, 32, "block"))
    platforms.append(Platform(2820, 400, 32, 32, "block"))
    platforms.append(Platform(2852, 400, 32, 32, "block"))

    # 金币位置
    coin_positions = [
        (332 + 6, 370),  # 问号块上方
        (364 + 6, 370),
        (480 + 6, 370),
        (512 + 6, 370),
        (544 + 6, 370),
        (600 + 6, 220),
        (1000 + 6, 420),
        (1032 + 6, 420),
        (1064 + 6, 420),
        (1300 + 6, 370),
        (2332 + 6, 270),
        (2852 + 6, 370)
    ]
    coins = [Coin(x, y) for x, y in coin_positions]

    # 敌人
    enemy_positions = [(400, 518), (900, 518), (2000, 518)]
    enemies = [Enemy(x, y) for x, y in enemy_positions]

    # 旗杆
    flag = Flag(3000, 150)

    return platforms, coins, enemies, flag

def get_ui_surface(player, font):
    ui_text = [
        f"SCORE: {player.score}",
        f"LIVES: {player.lives}",
        f"WORLD 1-1",
        f"COINS: {player.coins}"
    ]
    texts = []
    for i, text in enumerate(ui_text):
        texts.append(font.render(text, True, COLOR_UI_TEXT, COLOR_TEXT_BG))
    return texts

def draw_level(screen, platforms, coins, enemies, flag):
    for platform in platforms:
        if platform.type == "ground":
            pygame.draw.rect(screen, COLOR_GROUND, platform.rect)
        elif platform.type == "bricks":
            pygame.draw.rect(screen, COLOR_BRICK, platform.rect)
            pygame.draw.rect(screen, (0,0,0), platform.rect, 2)
            # 砖块纹理细节
            pygame.draw.line(screen, (0,0,0), (platform.rect.left + 10, platform.rect.top), 
                             (platform.rect.left + 10, platform.rect.bottom), 1)
            pygame.draw.line(screen, (0,0,0), (platform.rect.left, platform.rect.top + 16), 
                             (platform.rect.right, platform.rect.top + 16), 1)
        elif platform.type == "question":
            pygame.draw.rect(screen, COLOR_QUESTION, platform.rect)
            pygame.draw.rect(screen, (0,0,0), platform.rect, 2)
            font = pygame.font.SysFont('Arial', 20, bold=True)
            text = font.render('?', True, (0,0,0))
            screen.blit(text, (platform.rect.centerx - text.get_width()//2, 
                               platform.rect.centery - text.get_height()//2))
        elif platform.type == "pipe":
            pygame.draw.rect(screen, COLOR_PIPE, platform.rect)
            # 管道口边缘
            top_rect = pygame.Rect(platform.rect.x, platform.rect.y, platform.rect.width, 30)
            pygame.draw.rect(screen, COLOR_PIPE_LIP, top_rect)
            # 管道侧线
            pygame.draw.line(screen, (0,100,0), (platform.rect.left + 4, platform.rect.top), 
                             (platform.rect.left + 4, platform.rect.bottom), 2)
            pygame.draw.line(screen, (0,100,0), (platform.rect.right - 4, platform.rect.top), 
                             (platform.rect.right - 4, platform.rect.bottom), 2)
        elif platform.type == "block":
            pygame.draw.rect(screen, (210, 180, 140), platform.rect)  # 木块颜色
            pygame.draw.rect(screen, (0,0,0), platform.rect, 2)
            # X 形刻痕
            pygame.draw.line(screen, (0,0,0), (platform.rect.left, platform.rect.top),
                             (platform.rect.right, platform.rect.bottom), 1)
            pygame.draw.line(screen, (0,0,0), (platform.rect.right, platform.rect.top),
                             (platform.rect.left, platform.rect.bottom), 1)
    
    # 金币
    for coin in coins:
        if not coin.collected:
            pygame.draw.ellipse(screen, COLOR_COIN, coin.rect)
            pygame.draw.ellipse(screen, (184,134,0), coin.rect, 2)
    
    # 敌人
    for enemy in enemies:
        pygame.draw.ellipse(screen, COLOR_ENEMY, enemy.rect)
        # 敌人的眼睛
        pygame.draw.circle(screen, (255,255,255), (enemy.rect.left + 10, enemy.rect.top + 10), 3)
        pygame.draw.circle(screen, (255,255,255), (enemy.rect.right - 10, enemy.rect.top + 10), 3)
        pygame.draw.circle(screen, (0,0,0), (enemy.rect.left + 10, enemy.rect.top + 10), 1)
        pygame.draw.circle(screen, (0,0,0), (enemy.rect.right - 10, enemy.rect.top + 10), 1)
        # 敌人脚
        if enemy.direction > 0:
            pygame.draw.line(screen, COLOR_ENEMY, (enemy.rect.left + 4, enemy.rect.bottom),
                             (enemy.rect.left - 2, enemy.rect.bottom + 8), 3)
            pygame.draw.line(screen, COLOR_ENEMY, (enemy.rect.right - 4, enemy.rect.bottom),
                             (enemy.rect.right + 2, enemy.rect.bottom + 8), 3)
        else:
            pygame.draw.line(screen, COLOR_ENEMY, (enemy.rect.left + 4, enemy.rect.bottom),
                             (enemy.rect.left + 10, enemy.rect.bottom + 8), 3)
            pygame.draw.line(screen, COLOR_ENEMY, (enemy.rect.right - 4, enemy.rect.bottom),
                             (enemy.rect.right - 10, enemy.rect.bottom + 8), 3)
    
    # 旗杆
    pygame.draw.rect(screen, COLOR_FLAG_POLE, (flag.pole_x, flag.pole_y, 4, flag.pole_height))
    # 顶部球
    pygame.draw.circle(screen, COLOR_FLAG_TOP, (flag.pole_x + 2, flag.pole_y), 6)
    # 旗帜
    flag_rect = pygame.Rect(flag.pole_x + 4, flag.pole_y + 10, 40, 30)
    pygame.draw.polygon(screen, COLOR_FLAG_TOP, [
        (flag.pole_x + 4, flag.pole_y + 10),
        (flag.pole_x + 40, flag.pole_y + 20),
        (flag.pole_x + 4, flag.pole_y + 30)
    ])

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Super Mario Bros - World 1-1")
    clock = pygame.time.Clock()
    
    # 加载字体（使用系统默认字体，避免依赖外部字体文件）
    try:
        font = pygame.font.SysFont('Arial', 24)
    except:
        font = pygame.font.Font(None, 24)
    
    big_font = pygame.font.SysFont('Arial', 48)
    
    # 游戏状态
    global game_state
    game_state = {
        "camera_x": 0,
        "win": False,
        "end": False,
        "restart": False
    }

    def reset_game():
        nonlocal player, platforms, coins, enemies, flag
        player = Player(100, 450)
        platforms, coins, enemies, flag = create_level()
        game_state["win"] = False
        game_state["end"] = False
        game_state["restart"] = False
        game_state["camera_x"] = 0

    reset_game()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                if event.key == pygame.K_r and game_state["end"]:
                    reset_game()
        
        # 更新逻辑
        if not game_state["end"]:
            player.update(platforms, enemies, coins, flag)
            for enemy in enemies:
                enemy.update(platforms)

        # 摄像机控制
        camera_x = player.rect.centerx - WINDOW_WIDTH // 2
        camera_x = max(0, min(camera_x, LEVEL_WIDTH - WINDOW_WIDTH))
        game_state["camera_x"] = int(camera_x)
        
        # 渲染
        screen.fill(COLOR_SKY)
        
        # 绘制关卡（平移摄像机）
        screen.set_clip(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
        
        draw_level(screen, platforms, coins, enemies, flag)
        
        # 绘制玩家
        if player.alive:
            pygame.draw.rect(screen, COLOR_PLAYER, player.rect)
            # 简单马里奥帽
            pygame.draw.rect(screen, COLOR_PLAYER, (player.rect.left, player.rect.top, 
                                                    player.rect.width, player.rect.height//3))
        
        # 游戏结束或胜利画面
        if game_state["end"]:
            if game_state["win"]:
                text = big_font.render("YOU WIN!", True, (0, 255, 0), (0, 0, 0))
            elif not player.alive:
                text = big_font.render("GAME OVER", True, (255, 0, 0), (0, 0, 0))
            else:
                text = big_font.render("GAME OVER", True, (255, 0, 0), (0, 0, 0))
            
            text_rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
            screen.blit(text, text_rect)
            
            restart_text = font.render("Press R to Restart", True, (255, 255, 255), (0, 0, 0))
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20))
            screen.blit(restart_text, restart_rect)
            
            score_text = font.render(f"Final Score: {player.score}", True, (255, 255, 255), (0, 0, 0))
            score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 60))
            screen.blit(score_text, score_rect)
        
        # HUD（固定屏幕上方，不随摄像机移动）
        hud_surface = get_ui_text_surface(player)
        screen.blit(hud_surface[0], (10, 10))  # SCORE
        screen.blit(hud_surface[1], (10, 40))  # LIVES
        screen.blit(hud_surface[2], (10, 70))  # WORLD
        screen.blit(hud_surface[3], (WINDOW_WIDTH - 150, 10))  # COINS
        
        pygame.display.flip()
        clock.tick(FPS)

def get_ui_text_surface(player):
    font = pygame.font.SysFont('Arial', 24)
    ui_text = [
        f"SCORE: {player.score}",
        f"LIVES: {player.lives}",
        f"WORLD 1-1",
        f"COINS: {player.coins}"
    ]
    return [font.render(text, True, COLOR_UI_TEXT, COLOR_TEXT_BG) for text in ui_text]

# 修改主函数以解决嵌套问题
if __name__ == "__main__":
    main()