import pygame
import sys
import random

# 初始化 Pygame
pygame.init()

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CAPTION = "Super Mario Bros - World 1-1 (Fixed Level)"
FPS = 60

# 窗口设置
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(CAPTION)
clock = pygame.time.Clock()

# 随机种子
random.seed(42)

# 颜色定义
COLORS = {
    "mario": (255, 0, 0),
    "ground": (139, 69, 19),
    "brick": (205, 133, 63),
    "question_block": (255, 215, 0),
    "pipe": (0, 128, 0),
    "platform": (100, 100, 100),
    "enemy": (139, 0, 0),
    "coin": (255, 215, 0),
    "flagpole": (0, 0, 255),
    "sky": (135, 206, 235),
    "text": (255, 255, 255),
    "textShadow": (0, 0, 0)
}

# 游戏参数常量
LEVEL_WIDTH = 3200
LEVEL_HEIGHT = 600
PLAYER_SIZE = (32, 48)
PLAYER_SPEED_X = 5
PLAYER_JUMP_VEL = -12
PLAYER_GRAVITY = 0.5
PLAYER_LIVES = 3
COIN_VALUE = 100
ENEMY_VALUE = 200
COIN_SIZE = 18
ENEMY_SIZE = (32, 32)
ENEMY_SPEED = 2

# 游戏状态
GAME_PLAYING = 0
GAME_WIN = 1
GAME_OVER = 2

# 分组类，用于绘制顺序（简化版本）
class SpriteGroup(pygame.sprite.Group):
    pass

# 玩家类
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width, self.height = PLAYER_SIZE
        self.image = pygame.Surface(self.width, self.height)
        self.image.fill(COLORS["mario"])
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = 0
        self.vel_y = 0
        self.is_ground = False
        self.x = x
        self.y = y
        self.safety_x = x
        self.safety_y = y

    def update(self, platforms, enemies, coins, level_width):
        # 应用重力
        self.vel_y += PLAYER_GRAVITY
        # 水平移动
        self.rect.x += self.vel_x
        # 碰撞检测（水平）
        block_hit_list = pygame.sprite.spritecollide(self, platforms, False)
        for block in block_hit_list:
            if self.vel_x > 0:
                self.rect.right = block.rect.left
            elif self.vel_x < 0:
                self.rect.left = block.rect.right
        # 更新实际坐标
        self.x = self.rect.x
        # 垂直移动
        self.rect.y += self.vel_y
        self.is_ground = False
        # 碰撞检测（垂直）
        block_hit_list = pygame.sprite.spritecollide(self, platforms, False)
        for block in block_hit_list:
            if self.vel_y > 0:
                self.rect.bottom = block.rect.top
                self.vel_y = 0
                self.is_ground = True
            elif self.vel_y < 0:
                self.rect.top = block.rect.bottom
                self.vel_y = 0
        # 边界检测
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > level_width:
            self.rect.right = level_width
        self.y = self.rect.y

    def move_left(self):
        self.vel_x = -PLAYER_SPEED_X
    def move_right(self):
        self.vel_x = PLAYER_SPEED_X
    def stop_x(self):
        self.vel_x = 0
    def jump(self):
        if self.is_ground:
            self.vel_y = PLAYER_JUMP_VEL

    def reset_to_safety(self):
        self.rect.topleft = (self.safety_x, self.safety_y)
        self.vel_x = 0
        self.vel_y = 0
        self.is_ground = False

# 敌人类
class Goomba(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width, self.height = ENEMY_SIZE
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(COLORS["enemy"])
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = -ENEMY_SPEED
        self.start_x = x
        self.end_x = x + 100
        self.patrol_range = 200

    def update(self, platforms, level_width):
        self.rect.x += self.vel_x
        block_hit_list = pygame.sprite.spritecollide(self, platforms, False)
        for block in block_hit_list:
            if self.vel_x > 0:
                self.rect.right = block.rect.left
                self.vel_x = -ENEMY_SPEED
            elif self.vel_x < 0:
                self.rect.left = block.rect.right
                self.vel_x = ENEMY_SPEED
        # 限制巡逻范围
        if self.rect.right < self.start_x or self.rect.left > self.start_x + self.patrol_range:
            self.vel_x = -self.vel_x
        # 边界
        if self.rect.left < 0:
            self.rect.left = 0
            self.vel_x = ENEMY_SPEED
        if self.rect.right > level_width:
            self.rect.right = level_width
            self.vel_x = -ENEMY_SPEED

# 平台基类
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

# 金币类
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.size = COIN_SIZE
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(COLORS["coin"])
        self.rect = self.image.get_rect(center=(x + self.size//2, y + self.size//2))

# 旗杆类
class Flagpole(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 10
        self.height = 300
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(COLORS["flagpole"])
        self.rect = self.image.get_rect(topleft=(x, y))
        # 小旗子
        self.flag_image = pygame.Surface((25, 20))
        self.flag_image.fill((255, 0, 0))
        self.flag_rect = self.flag_image.get_rect(center=(x + self.width//2, y + 40))
        self.image.blit(self.flag_image, self.flag_rect.topleft)

# 问号块类
class QuestionBlock(Platform):
    def __init__(self, x, y):
        super().__init__(x, y, 32, 32, COLORS["question_block"])

# 砖块类
class Brick(Platform):
    def __init__(self, x, y):
        super().__init__(x, y, 32, 32, COLORS["brick"])

# 管道类
class Pipe(Platform):
    def __init__(self, x, y, width=50, height=40):
        super().__init__(x, y, width, height, COLORS["pipe"])

# 游戏主类
class Game:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.state = GAME_PLAYING
        self.score = 0
        self.coins_collected = 0
        self.lives = PLAYER_LIVES
        self.level_width = LEVEL_WIDTH
        self.camera_x = 0
        self.last_safe_x = 0
        self.last_safe_y = 0
        self.font = pygame.font.SysFont(None, 24)
        
        # 创建玩家
        self.player = Player(100, 450)
        self.player.safety_x = 100
        self.player.safety_y = 450
        self.last_safe_x = 100
        self.last_safe_y = 450

        # 创建平台组
        self.platforms = SpriteGroup()
        self.enemies = SpriteGroup()
        self.coins = SpriteGroup()
        self.flagpole_group = SpriteGroup()

        self._create_level()

    def _create_level(self):
        # 地面（分段避免坑洞）
        # 坑1：x=600~800，坑2：x=2200~2400
        ground_parts = [
            (0, 500, 600, 100),
            (800, 500, 1400, 100),  # 600~800 坑洞
            (2200, 500, 1000, 100), # 2200~2400 坑洞
            (2400, 500, 800, 100)
        ]
        for x, y, width, height in ground_parts:
            self.platforms.add(Platform(x, y, width, height, COLORS["ground"]))

        # 砖块区
        self.platforms.add(Brick(280, 380))
        self.platforms.add(Brick(400, 380))
        self.platforms.add(Brick(432, 380))
        self.platforms.add(Brick(464, 380))
        self.platforms.add(Brick(510, 250))
        self.platforms.add(Brick(542, 250))
        self.platforms.add(Brick(574, 250))
        self.platforms.add(Brick(950, 380))
        self.platforms.add(Brick(982, 380))
        self.platforms.add(Brick(950, 250))

        # 问号块区
        self.platforms.add(QuestionBlock(320, 380))
        self.platforms.add(QuestionBlock(416, 250))
        self.platforms.add(QuestionBlock(448, 250))
        self.platforms.add(QuestionBlock(480, 250))

        # 管道
        self.platforms.add(Pipe(600, 460, 40, 40))
        self.platforms.add(Pipe(850, 430, 50, 70))
        self.platforms.add(Pipe(1600, 450, 60, 50))
        self.platforms.add(Pipe(1800, 430, 70, 70))

        # 平台（台阶）
        self.platforms.add(Platform(1100, 400, 100, 20, COLORS["platform"]))
        self.platforms.add(Platform(1250, 350, 100, 20, COLORS["platform"]))
        self.platforms.add(Platform(1400, 300, 100, 20, COLORS["platform"]))
        self.platforms.add(Platform(1650, 320, 100, 20, COLORS["platform"]))

        # 敌人（地面）
        self.enemies.add(Goomba(500, 468))
        self.enemies.add(Goomba(900, 468))
        self.enemies.add(Goomba(1500, 468))
        self.enemies.add(Goomba(2000, 468))

        # 金币
        coin_positions = [
            (300, 350), (350, 350), (400, 350),
            (600, 300), (630, 300),
            (850, 400), (920, 350),
            (1100, 370), (1130, 370),
            (1300, 320), (1350, 320),
            (1900, 380), (1930, 380), (1960, 380)
        ]
        for x, y in coin_positions:
            self.coins.add(Coin(x, y))

        # 终点旗杆
        self.flagpole_group.add(Flagpole(3000, 200))

    def handle_events(self):
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r and self.state != GAME_PLAYING:
                    self.reset_game()
                elif self.state == GAME_PLAYING:
                    if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                        self.player.jump()

        if self.state == GAME_PLAYING:
            if keys[pygame.K_LEFT]:
                self.player.move_left()
            elif keys[pygame.K_RIGHT]:
                self.player.move_right()
            else:
                self.player.stop_x()
        return True

    def update(self):
        if self.state == GAME_PLAYING:
            self.player.update(self.platforms, self.enemies, self.coins, self.level_width)

            # 检查敌人碰撞（踩踏或撞击）
            for enemy in self.enemies:
                enemy.update(self.platforms, self.level_width)
                # 踩踏检测（玩家底部与敌人顶部重叠）
                if (self.player.rect.bottom - self.player.vel_y < enemy.rect.top + 5 and
                    self.player.rect.bottom >= enemy.rect.top and
                    self.player.vel_y > 0 and
                    self.player.rect.right > enemy.rect.left + 5 and
                    self.player.rect.left < enemy.rect.right - 5):
                    self.score += ENEMY_VALUE
                    self.enemies.remove(enemy)
                    self.player.vel_y = -6  # 小跳反馈
                elif self.player.rect.colliderect(enemy.rect):
                    # 掉落坑洞安全检查
                    if self.player.rect.bottom > SCREEN_HEIGHT:
                        self.lives -= 1
                        self.player.reset_to_safety()
                        if self.lives <= 0:
                            self.state = GAME_OVER
                    # 检查是否从侧面撞
                    else:
                        self.lives -= 1
                        self.player.reset_to_safety()
                        if self.lives <= 0:
                            self.state = GAME_OVER

            # 金币收集碰撞检测
            coins_hit_list = pygame.sprite.spritecollide(self.player, self.coins, True)
            self.coins_collected += len(coins_hit_list)
            self.score += len(coins_hit_list) * COIN_VALUE

            # 旗杆胜利检测
            flag_hit = pygame.sprite.spritecollide(self.player, self.flagpole_group, False)
            if flag_hit and self.player.rect.right <= 3000 + 10:
                self.state = GAME_WIN

            # 跌落坑洞
            if self.player.rect.top > SCREEN_HEIGHT:
                self.lives -= 1
                self.player.reset_to_safety()
                if self.lives <= 0:
                    self.state = GAME_OVER

            # 更新摄像机位置（平滑跟随）
            self.camera_x = self.player.rect.centerx - SCREEN_WIDTH // 2
            self.camera_x = max(0, min(self.camera_x, self.level_width - SCREEN_WIDTH))

    def draw(self):
        screen.fill(COLORS["sky"])

        if self.state == GAME_PLAYING:
            # 绘制游戏内容
            # 地面
            for platform in self.platforms:
                if platform.image.get_height() >= 100 and platform.image.get_width() >= 100:
                    continue
                screen.blit(platform.image, (platform.rect.x - self.camera_x, platform.rect.y))
            
            # 平台（地面除外）
            for platform in self.platforms:
                if (platform.image.get_height() >= 100 and platform.image.get_width() >= 100):
                    screen.blit(platform.image, (platform.rect.x - self.camera_x, platform.rect.y))
            
            # 金币
            for coin in self.coins:
                screen.blit(coin.image, (coin.rect.x - self.camera_x, coin.rect.y))
            
            # 敌人
            for enemy in self.enemies:
                screen.blit(enemy.image, (enemy.rect.x - self.camera_x, enemy.rect.y))
            
            # 旗杆
            for flag in self.flagpole_group:
                screen.blit(flag.image, (flag.rect.x - self.camera_x, flag.rect.y))
            
            # 玩家
            screen.blit(self.player.image, (self.player.rect.x - self.camera_x, self.player.rect.y))

            # HUD（固定在屏幕上方）
            hud_surface = self.font.render(f"Score: {self.score}   Coins: {self.coins_collected}   Lives: {self.lives}", 
                                          True, COLORS["textShadow"])
            screen.blit(hud_surface, (10, 10))
            hud_surface = self.font.render(f"Score: {self.score}   Coins: {self.coins_collected}   Lives: {self.lives}", 
                                          True, COLORS["text"])
            screen.blit(hud_surface, (8, 8))

        else:
            # 游戏结束画面
            if self.state == GAME_WIN:
                text1 = "YOU WIN!"
                text2 = f"Final Score: {self.score}"
            else:
                text1 = "GAME OVER"
                text2 = f"Final Score: {self.score}"

            win_font = pygame.font.SysFont(None, 72)
            msg1 = win_font.render(text1, True, COLORS["textShadow"])
            msg2 = self.font.render(text2, True, COLORS["textShadow"])
            msg3 = self.font.render("Press R to Restart", True, COLORS["textShadow"])

            screen.blit(msg1, (SCREEN_WIDTH//2 - msg1.get_width()//2, SCREEN_HEIGHT//2 - 60))
            screen.blit(msg2, (SCREEN_WIDTH//2 - msg2.get_width()//2, SCREEN_HEIGHT//2))
            screen.blit(msg3, (SCREEN_WIDTH//2 - msg3.get_width()//2, SCREEN_HEIGHT//2 + 60))

            # 白色背景填充文本
            for surface in [msg1, msg2, msg3]:
                screen.blit(surface, (SCREEN_WIDTH//2 - surface.get_width()//2 - 2, SCREEN_HEIGHT//2 - 58 + [0,0,0][[msg1,mgs2,msg3].index(surface)]))

            # 重新渲染带白边的文本
            msg1 = win_font.render(text1, True, COLORS["text"])
            msg2 = self.font.render(text2, True, COLORS["text"])
            msg3 = self.font.render("Press R to Restart", True, COLORS["text"])
            screen.blit(msg1, (SCREEN_WIDTH//2 - msg1.get_width()//2, SCREEN_HEIGHT//2 - 60))
            screen.blit(msg2, (SCREEN_WIDTH//2 - msg2.get_width()//2, SCREEN_HEIGHT//2))
            screen.blit(msg3, (SCREEN_WIDTH//2 - msg3.get_width()//2, SCREEN_HEIGHT//2 + 60))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()