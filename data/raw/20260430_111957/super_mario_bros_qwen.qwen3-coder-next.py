import pygame
import sys
import random

pygame.init()

# 常量定义
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
LEVEL_WIDTH, LEVEL_HEIGHT = 3200, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)
GRASS_GREEN = (34, 139, 34)
SKY_BLUE = (135, 206, 235)
GRAY = (192, 192, 192)
PURPLE = (238, 130, 238)
PINK = (255, 192, 203)

# 玩家参数
PLAYER_WIDTH, PLAYER_HEIGHT = 32, 48
PLAYER_SPEED = 5
PLAYER_JUMP_FORCE = -12
PLAYER_GRAVITY = 0.5
PLAYER_MAX_LIVES = 3

# 金币
COIN_SIZE = 18
COIN_VALUE = 100

# 敌人参数
ENEMY_WIDTH, ENEMY_HEIGHT = 32, 32
ENEMY_SPEED = 2
ENEMY_KILL_SCORE = 200

# 地图元素尺寸
BRICK_WIDTH, BRICK_HEIGHT = 32, 32
BLOCK_WIDTH, BLOCK_HEIGHT = 32, 32
PIPE_WIDTH, PIPE_HEIGHT = 48, 48
STEAM_HEIGHT = 15

# 游戏状态
GAME_STATE_RUNNING = 0
GAME_STATE_GAME_OVER = 1
GAME_STATE_WIN = 2

random.seed(42)

# 设置屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario Bros Medium")
clock = pygame.time.Clock()


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.vel_x = 0
        self.vel_y = 0
        self.is_jumping = False
        self.lives = PLAYER_MAX_LIVES
        self.score = 0
        self.coins = 0
        self.safe_x, self.safe_y = x, y
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.dead = False

    def update(self, keys, platforms, enemies):
        # X轴移动
        if keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
        elif keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED
        else:
            self.vel_x = 0

        self.x += self.vel_x

        # X轴碰撞检测
        self.rect.x = self.x
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_x > 0:  # 向右碰撞
                    self.rect.right = p.rect.left
                    self.x = self.rect.left
                elif self.vel_x < 0:  # 向左碰撞
                    self.rect.left = p.rect.right
                    self.x = self.rect.left

        # Y轴移动（重力）
        self.vel_y += PLAYER_GRAVITY
        if self.vel_y > 12:  # 最大下落速度限制
            self.vel_y = 12

        self.y += self.vel_y
        self.rect.y = self.y

        # Y轴碰撞检测
        self.is_jumping = True
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_y > 0:  # 向下（落地）
                    self.rect.bottom = p.rect.top
                    self.y = self.rect.top
                    self.vel_y = 0
                    self.is_jumping = False
                elif self.vel_y < 0:  # 向上（顶头）
                    self.rect.top = p.rect.bottom
                    self.y = self.rect.bottom
                    self.vel_y = 0
                    # 砸碎问号块等逻辑可在此扩展

        # 禁用水平移动超出关卡边界
        if self.x < 0:
            self.x = 0
            self.rect.left = 0
        if self.x > LEVEL_WIDTH - self.width:
            self.x = LEVEL_WIDTH - self.width
            self.rect.right = LEVEL_WIDTH

        # 跌落检测
        if self.y > LEVEL_HEIGHT + 100:
            self.dead = True

        # 敌人碰撞检测
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                # 判定是否踩到敌人（从上方）
                if (self.vel_y > 0 and
                    self.y + self.height - self.vel_y <= enemy.y + enemy.height * 0.5):
                    enemy.die()
                    self.vel_y = -8  # 踩弹跳效果
                    self.score += ENEMY_KILL_SCORE
                else:
                    self.lose_life()

    def jump(self):
        if not self.is_jumping:
            self.vel_y = PLAYER_JUMP_FORCE
            self.is_jumping = True

    def lose_life(self):
        self.lives -= 1
        self.x, self.y = self.safe_x, self.safe_y
        self.rect.x, self.rect.y = self.x, self.y
        self.vel_x = 0
        self.vel_y = 0
        if self.lives <= 0:
            self.dead = True

    def respawn(self, x, y):
        self.safe_x, self.safe_y = x, y
        self.x, self.y = x, y
        self.rect.x, self.rect.y = self.x, self.y
        self.vel_x = 0
        self.vel_y = 0
        self.dead = False


class Platform:
    def __init__(self, x, y, width, height, solid=True, type="brick"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.solid = solid
        self.type = type  # "ground", "brick", "block", "pipe", "step"
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surf, offset_x):
        x = self.x - offset_x
        if self.type == "ground":
            pygame.draw.rect(surf, BROWN, (x, self.y, self.width, self.height))
            pygame.draw.rect(surf, GRASS_GREEN, (x, self.y, self.width, 10))
        elif self.type == "brick":
            pygame.draw.rect(surf, BROWN, (x, self.y, self.width, self.height))
            pygame.draw.rect(surf, BLACK, (x, self.y, self.width, self.height), 2)
            # 砖块纹理细节
            pygame.draw.line(surf, BLACK, (x + self.width // 2, self.y), (x + self.width // 2, self.y + self.height), 1)
            pygame.draw.line(surf, BLACK, (x, self.y + self.height // 2), (x + self.width, self.y + self.height // 2), 1)
        elif self.type == "block":
            pygame.draw.rect(surf, PINK, (x, self.y, self.width, self.height))
            pygame.draw.rect(surf, BLACK, (x, self.y, self.width, self.height), 2)
            pygame.draw.circle(surf, BLACK, (x + 8, self.y + 8), 2)
            pygame.draw.circle(surf, BLACK, (x + self.width - 8, self.y + 8), 2)
            pygame.draw.circle(surf, BLACK, (x + 8, self.y + self.height - 8), 2)
            pygame.draw.circle(surf, BLACK, (x + self.width - 8, self.y + self.height - 8), 2)
        elif self.type == "pipe":
            pipe_color = (0, 128, 0)
            pygame.draw.rect(surf, pipe_color, (x, self.y, self.width, self.height))
            # 顶部
            top_y = self.y
            pygame.draw.rect(surf, pipe_color, (x - 2, top_y, self.width + 4, 32))
            pygame.draw.rect(surf, (0, 100, 0), (x, top_y + 15, self.width, 2))  # 暗影
        elif self.type == "step":
            pygame.draw.rect(surf, GRAY, (x, self.y, self.width, self.height))
            pygame.draw.rect(surf, BLACK, (x, self.y, self.width, self.height), 1)


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = COIN_SIZE
        self.height = COIN_SIZE
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.collected = False
        self.anim_timer = 0

    def draw(self, surf, offset_x):
        if self.collected:
            return
        self.anim_timer += 1
        x = self.x - offset_x
        # 动画呼吸效果
        scale = 1.0 + 0.1 * (1 - abs(self.anim_timer % 60 - 30) / 30)
        w = int(self.width * scale)
        h = int(self.height * scale)
        dx = (self.width - w) // 2
        dy = (self.height - h) // 2
        pygame.draw.circle(surf, GOLD, (x + self.width // 2, self.y + self.height // 2), w // 2)
        pygame.draw.circle(surf, (255, 192, 0), (x + self.width // 2 + 2, self.y + self.height // 2 + 2), w // 4)


class Enemy:
    def __init__(self, x, y, patrol_range):
        self.x = x
        self.y = y
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.speed = ENEMY_SPEED
        self.direction = 1
        self.start_x = x
        self.patrol_range = patrol_range
        self.dead = False
        self.anim_timer = 0

    def update(self, platforms):
        if self.dead:
            return
        self.anim_timer += 1

        self.x += self.speed * self.direction
        self.rect.x = self.x

        # 简单边界检测
        if self.x < self.start_x or self.x > self.start_x + self.patrol_range:
            self.direction *= -1

        # 地面检测
        self.y += PLAYER_GRAVITY
        self.rect.y = self.y
        on_ground = False
        for p in platforms:
            if (p.type in ["ground", "brick", "block", "step"] and
                self.rect.colliderect(p.rect)):
                if self.rect.bottom <= p.rect.bottom + 5 and self.rect.bottom >= p.rect.top - 5:
                    self.rect.bottom = p.rect.top
                    self.y = self.rect.top
                    on_ground = True
        if not on_ground and self.y > LEVEL_HEIGHT + 100:
            self.dead = True

    def die(self):
        self.dead = True

    def draw(self, surf, offset_x):
        if self.dead:
            return
        x = self.x - offset_x
        # Simple enemy (Goomba-like) drawing
        pygame.draw.ellipse(surf, BROWN, (x, self.y, self.width, self.height))
        # Eyes
        eye_size = 4
        pygame.draw.circle(surf, WHITE, (x + 8, self.y + 10), eye_size)
        pygame.draw.circle(surf, WHITE, (x + self.width - 8, self.y + 10), eye_size)
        pygame.draw.circle(surf, BLACK, (x + 8 + self.direction * 2, self.y + 10), 2)
        pygame.draw.circle(surf, BLACK, (x + self.width - 8 + self.direction * 2, self.y + 10), 2)


class Flag:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 12
        self.height = 300
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def draw(self, surf, offset_x):
        x = self.x - offset_x
        # Pole
        pygame.draw.rect(surf, WHITE, (x, self.y, self.width, self.height))
        # Ball on top
        pygame.draw.circle(surf, GOLD, (x + self.width // 2, self.y), 8)
        # Flag
        flag_x = x + self.width
        flag_y = self.y + 20
        pygame.draw.polygon(surf, RED, [
            (flag_x, flag_y),
            (flag_x + 40, flag_y + 20),
            (flag_x, flag_y + 40)
        ])
        # Base
        pygame.draw.rect(surf, GRAY, (x - 10, self.y + self.height - 30, 32, 30))


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.state = GAME_STATE_RUNNING
        self.player = Player(100, 450)
        self.camera_x = 0
        self.platforms = []
        self.coins = []
        self.enemies = []
        self.flag = None

        self._build_level()

    def _build_level(self):
        # 地面
        # 平地：0-800, 900-1800, 1950-2500, 2600-3200
        ground_y = LEVEL_HEIGHT - 40
        sections = [
            (0, 800),
            (900, 100),
            (1100, 200),
            (1400, 100),
            (1600, 100),
            (1950, 300),
            (2600, 600)
        ]
        for x, width in sections:
            self.platforms.append(Platform(x, ground_y, width, 40, type="ground"))

        # 砖块区（1）
        brick_positions = [
            (200, 350), (232, 350), (264, 350), (296, 350),
            (400, 250), (432, 250), (464, 250), (496, 250),
            (550, 200), (700, 350), (732, 350)
        ]
        for x, y in brick_positions:
            self.platforms.append(Platform(x, y, 32, 32, type="brick"))

        # 问号块
        block_positions = [
            (216, 250), (416, 180), (716, 250), (800, 350)
        ]
        for x, y in block_positions:
            self.platforms.append(Platform(x, y, 32, 32, type="block"))

        # 管道1
        self.platforms.append(Platform(550, ground_y - 48, 48, 48, type="pipe"))
        # 管道2
        self.platforms.append(Platform(1300, ground_y - 64, 48, 64, type="pipe"))
        # 管道3
        self.platforms.append(Platform(1800, ground_y - 32, 48, 32, type="pipe"))

        # 阶梯
        for i in range(5):
            self.platforms.append(Platform(2200 + i * 32, ground_y - (i + 1) * 32, 32, 32, type="step"))
        for i in range(3):
            self.platforms.append(Platform(2240 + i * 32, ground_y - 64 - (i + 1) * 32, 32, 32, type="step"))

        # 金币
        coin_positions = [
            (220, 300), (252, 300), (284, 300),
            (600, 300), (632, 300), (664, 300),
            (416, 200), (448, 200), (480, 200),
            (716, 200), (850, 300), (900, 300)
        ]
        for x, y in coin_positions:
            self.coins.append(Coin(x, y))

        # 敌人
        enemy_positions = [
            (600, ground_y - ENEMY_HEIGHT, 150),
            (1200, ground_y - ENEMY_HEIGHT, 200),
            (1650, ground_y - ENEMY_HEIGHT, 250)
        ]
        for x, y, range in enemy_positions:
            self.enemies.append(Enemy(x, y, range))

        # 终点旗杆
        self.flag = Flag(3100, ground_y - 300)

    def update(self, keys):
        if self.state != GAME_STATE_RUNNING:
            if keys[pygame.K_r]:
                self.reset()
            return

        # 更新玩家
        self.player.update(keys, self.platforms, self.enemies)
        
        # 跃迁/死亡检测
        if self.player.dead:
            if self.player.lives <= 0:
                self.state = GAME_STATE_GAME_OVER
            else:
                self.player.respawn(self.player.safe_x, self.player.safe_y)

        # 检查金币收集
        for coin in self.coins:
            if not coin.collected and self.player.rect.colliderect(coin.rect):
                coin.collected = True
                self.player.score += COIN_VALUE
                self.player.coins += 1

        # 更新敌人
        for enemy in self.enemies:
            enemy.update(self.platforms)

        # 检查旗杆碰撞（胜利条件）
        if self.player.rect.colliderect(self.flag.rect) and not self.player.dead:
            self.state = GAME_STATE_WIN

        # 更新摄像机
        self._update_camera()

    def _update_camera(self):
        # 限制摄像机范围
        self.camera_x = max(0, min(self.player.x - SCREEN_WIDTH // 2, LEVEL_WIDTH - SCREEN_WIDTH))

    def draw(self):
        # 背景
        screen.fill(SKY_BLUE)

        # 绘制平台
        for p in self.platforms:
            p.draw(screen, self.camera_x)

        # 绘制金币
        for coin in self.coins:
            coin.draw(screen, self.camera_x)

        # 绘制敌人
        for enemy in self.enemies:
            enemy.draw(screen, self.camera_x)

        # 绘制旗杆
        self.flag.draw(screen, self.camera_x)

        # 绘制玩家
        if not self.player.dead or self.state != GAME_STATE_RUNNING:
            # 简单的马里奥图形
            player_x = self.player.x - self.camera_x
            player_y = self.player.y
            # 身体（红色）
            pygame.draw.rect(screen, RED, (player_x, player_y, self.player.width, self.player.height))
            # 过膝工装裤（蓝色）
            pygame.draw.rect(screen, BLUE, (player_x, player_y + 20, self.player.width, self.player.height - 20))
            # 脸部（皮肤）
            pygame.draw.rect(screen, PINK, (player_x + 6, player_y + 4, 18, 10))
            # 帽子（红色）
            pygame.draw.rect(screen, RED, (player_x, player_y, self.player.width, 6))
            # 眼睛和鼻子（方向依赖）
            eye_offset = 6 if self.player.vel_x >= 0 else -2
            pygame.draw.circle(screen, BLACK, (player_x + 16, player_y + 8), 2)
            pygame.draw.circle(screen, PINK, (player_x + 22, player_y + 8), 3)

        # HUD（固定在屏幕顶部）
        font = pygame.font.SysFont("Arial", 20)
        score_text = font.render(f"Score: {self.player.score}", True, WHITE)
        coins_text = font.render(f"Coins: {self.player.coins}", True, WHITE)
        lives_text = font.render(f"Lives: {self.player.lives}", True, WHITE)

        screen.blit(score_text, (20, 20))
        screen.blit(coins_text, (300, 20))
        screen.blit(lives_text, (560, 20))

        # 胜利/失败
        if self.state == GAME_STATE_GAME_OVER:
            self._draw_game_over("Game Over", self.player.score)
        elif self.state == GAME_STATE_WIN:
            self._draw_game_over("You Win!", self.player.score + self.player.coins * 50)

    def _draw_game_over(self, message, final_score):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        big_font = pygame.font.SysFont("Arial", 48)
        small_font = pygame.font.SysFont("Arial", 24)

        msg_surface = big_font.render(message, True, WHITE)
        score_surface = small_font.render(f"Final Score: {final_score}", True, WHITE)
        restart_surface = small_font.render("Press R to Restart", True, WHITE)

        screen.blit(msg_surface, (SCREEN_WIDTH // 2 - msg_surface.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
        screen.blit(score_surface, (SCREEN_WIDTH // 2 - score_surface.get_width() // 2, SCREEN_HEIGHT // 2))
        screen.blit(restart_surface, (SCREEN_WIDTH // 2 - restart_surface.get_width() // 2, SCREEN_HEIGHT // 2 + 60))


def main():
    game = Game()
    running = True
    keys = pygame.key.get_pressed()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    game.player.jump()
                keys[Event.key] = True
            elif event.type == pygame.KEYUP:
                keys[event.key] = False

        keys = pygame.key.get_pressed()
        game.update(keys)
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()