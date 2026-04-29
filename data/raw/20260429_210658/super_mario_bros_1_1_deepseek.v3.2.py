import pygame
import random

random.seed(42)

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WORLD_WIDTH = 3200
WORLD_HEIGHT = 600

# 颜色定义
BACKGROUND = (107, 140, 255)
GROUND_COLOR = (94, 163, 67)
BRICK_COLOR = (180, 80, 40)
QUESTION_COLOR = (255, 200, 0)
PIPE_COLOR = (0, 180, 0)
STAIR_COLOR = (150, 150, 150)
ENEMY_COLOR = (200, 50, 50)
PLAYER_COLOR = (255, 0, 0)
COIN_COLOR = (255, 215, 0)
FLAG_COLOR = (255, 255, 255)
HUD_COLOR = (50, 50, 50)
TEXT_COLOR = (255, 255, 255)

# 玩家常量
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 48
PLAYER_SPEED = 5
JUMP_SPEED = -12
GRAVITY = 0.5

# 物体尺寸
COIN_SIZE = 18
ENEMY_WIDTH = 32
ENEMY_HEIGHT = 32
BRICK_WIDTH = 32
BRICK_HEIGHT = 32

# 游戏状态
class Game:
    def __init__(self):
        self.player = None
        self.ground = []
        self.bricks = []
        self.questions = []
        self.pipes = []
        self.stairs = []
        self.enemies = []
        self.coins = []
        self.flag = None
        self.score = 0
        self.coin_count = 0
        self.lives = 3
        self.game_over = False
        self.win = False
        self.init_world()

    def init_world(self):
        # 玩家
        self.player = Player(50, WORLD_HEIGHT - PLAYER_HEIGHT - 40)

        # 地面 (长条)
        self.ground = [pygame.Rect(0, WORLD_HEIGHT - 40, WORLD_WIDTH, 40)]

        # 砖块 (12个)
        brick_positions = [
            (300, 400), (332, 400), (364, 400),
            (500, 350), (532, 350),
            (700, 300), (732, 300), (764, 300),
            (1100, 400), (1132, 400), (1164, 400), (1196, 400)
        ]
        self.bricks = [pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT) for x, y in brick_positions]

        # 问号块 (6个，总共12个砖块+问号块)
        question_positions = [
            (396, 400),
            (564, 350),
            (796, 300),
            (1228, 400),
            (1500, 300),
            (1800, 250)
        ]
        self.questions = [pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT) for x, y in question_positions]

        # 管道 (2个)
        self.pipes = [
            pygame.Rect(900, WORLD_HEIGHT - 90 - 40, 64, 90),
            pygame.Rect(1300, WORLD_HEIGHT - 120 - 40, 64, 120)
        ]

        # 台阶 (2个)
        self.stairs = [
            pygame.Rect(1600, WORLD_HEIGHT - 80 - 40, 96, 80),
            pygame.Rect(2000, WORLD_HEIGHT - 120 - 40, 128, 120)
        ]

        # 敌人 (3个)
        self.enemies = [
            Enemy(400, WORLD_HEIGHT - ENEMY_HEIGHT - 40),
            Enemy(950, WORLD_HEIGHT - ENEMY_HEIGHT - 40),
            Enemy(1650, WORLD_HEIGHT - ENEMY_HEIGHT - 40)
        ]

        # 金币 (12个)
        coin_positions = [
            (310, 350), (342, 350), (374, 350),
            (510, 300), (542, 300),
            (710, 250), (742, 250),
            (1110, 350), (1142, 350),
            (1510, 250),
            (1810, 200),
            (2500, 300)
        ]
        self.coins = [pygame.Rect(x, y, COIN_SIZE, COIN_SIZE) for x, y in coin_positions]

        # 旗杆
        self.flag = pygame.Rect(WORLD_WIDTH - 120, 100, 20, 300)

    def reset(self):
        self.__init__()

    def update(self):
        if self.game_over or self.win:
            return

        self.player.update(self)
        for enemy in self.enemies:
            enemy.update()

        # 检查玩家是否掉出屏幕
        if self.player.rect.bottom > WORLD_HEIGHT:
            self.lose_life()

        # 检查是否到达旗杆
        if self.player.rect.colliderect(self.flag):
            self.win = True
            self.game_over = True

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
        else:
            # 回到最近安全位置 (左侧)
            self.player.rect.x = 50
            self.player.rect.y = WORLD_HEIGHT - PLAYER_HEIGHT - 40
            self.player.vel_y = 0

    def draw(self, screen, camera_x):
        # 背景
        screen.fill(BACKGROUND)

        # 地面
        for rect in self.ground:
            pygame.draw.rect(screen, GROUND_COLOR, rect.move(-camera_x, 0))

        # 砖块
        for rect in self.bricks:
            pygame.draw.rect(screen, BRICK_COLOR, rect.move(-camera_x, 0))

        # 问号块
        for rect in self.questions:
            pygame.draw.rect(screen, QUESTION_COLOR, rect.move(-camera_x, 0))

        # 管道
        for rect in self.pipes:
            pygame.draw.rect(screen, PIPE_COLOR, rect.move(-camera_x, 0))

        # 台阶
        for rect in self.stairs:
            pygame.draw.rect(screen, STAIR_COLOR, rect.move(-camera_x, 0))

        # 金币
        for coin in self.coins:
            pygame.draw.ellipse(screen, COIN_COLOR, coin.move(-camera_x, 0))

        # 敌人
        for enemy in self.enemies:
            enemy.draw(screen, camera_x)

        # 旗杆
        pygame.draw.rect(screen, FLAG_COLOR, self.flag.move(-camera_x, 0))
        pygame.draw.polygon(screen, (255, 0, 0), [
            (self.flag.x - camera_x + 25, self.flag.y + 50),
            (self.flag.x - camera_x + 100, self.flag.y + 70),
            (self.flag.x - camera_x + 25, self.flag.y + 90)
        ])

        # 玩家
        self.player.draw(screen, camera_x)

        # HUD
        font = pygame.font.SysFont(None, 36)
        lives_text = font.render(f"Lives: {self.lives}", True, TEXT_COLOR)
        score_text = font.render(f"Score: {self.score}", True, TEXT_COLOR)
        coin_text = font.render(f"Coins: {self.coin_count}", True, TEXT_COLOR)
        screen.blit(lives_text, (10, 10))
        screen.blit(score_text, (10, 50))
        screen.blit(coin_text, (10, 90))

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            if self.win:
                game_over_text = font.render("You Win!", True, (0, 255, 0))
                screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 80))
            else:
                game_over_text = font.render("Game Over", True, (255, 0, 0))
                screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 - 80))
            final_score = font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            restart_text = font.render("Press R to Restart", True, TEXT_COLOR)
            screen.blit(final_score, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 30))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 20))

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

    def update(self, game):
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED

        # 跳跃
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = JUMP_SPEED
            self.on_ground = False

        # 重力
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        self.on_ground = False

        # 碰撞检测 - 地面
        for ground_rect in game.ground:
            if self.rect.colliderect(ground_rect):
                if self.vel_y > 0:
                    self.rect.bottom = ground_rect.top
                    self.vel_y = 0
                    self.on_ground = True

        # 砖块和问号块
        for brick in game.bricks + game.questions:
            if self.rect.colliderect(brick):
                if self.vel_y > 0 and self.rect.bottom - self.vel_y <= brick.top:
                    self.rect.bottom = brick.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = brick.bottom
                    self.vel_y = 0

        # 管道
        for pipe in game.pipes:
            if self.rect.colliderect(pipe):
                if self.vel_y > 0 and self.rect.bottom - self.vel_y <= pipe.top:
                    self.rect.bottom = pipe.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = pipe.bottom
                    self.vel_y = 0

        # 台阶
        for stair in game.stairs:
            if self.rect.colliderect(stair):
                if self.vel_y > 0 and self.rect.bottom - self.vel_y <= stair.top:
                    self.rect.bottom = stair.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = stair.bottom
                    self.vel_y = 0

        # 水平移动和碰撞
        self.rect.x += self.vel_x
        for brick in game.bricks + game.questions:
            if self.rect.colliderect(brick):
                if self.vel_x > 0:
                    self.rect.right = brick.left
                elif self.vel_x < 0:
                    self.rect.left = brick.right

        for pipe in game.pipes:
            if self.rect.colliderect(pipe):
                if self.vel_x > 0:
                    self.rect.right = pipe.left
                elif self.vel_x < 0:
                    self.rect.left = pipe.right

        for stair in game.stairs:
            if self.rect.colliderect(stair):
                if self.vel_x > 0:
                    self.rect.right = stair.left
                elif self.vel_x < 0:
                    self.rect.left = stair.right

        # 金币收集
        for coin in game.coins[:]:
            if self.rect.colliderect(coin):
                game.coins.remove(coin)
                game.score += 100
                game.coin_count += 1

        # 敌人碰撞
        for enemy in game.enemies[:]:
            if self.rect.colliderect(enemy.rect):
                # 从上方踩到
                if self.vel_y > 0 and self.rect.bottom - self.vel_y <= enemy.rect.top + 10:
                    game.enemies.remove(enemy)
                    game.score += 200
                    self.vel_y = JUMP_SPEED * 0.7
                else:
                    game.lose_life()
                    break

        # 坑洞检测 (模拟)
        if 1200 < self.rect.x < 1300 and self.rect.bottom > WORLD_HEIGHT - 40:
            game.lose_life()
        if 2100 < self.rect.x < 2200 and self.rect.bottom > WORLD_HEIGHT - 40:
            game.lose_life()

    def draw(self, screen, camera_x):
        pygame.draw.rect(screen, PLAYER_COLOR, self.rect.move(-camera_x, 0))
        pygame.draw.circle(screen, (0, 0, 0), (self.rect.x - camera_x + PLAYER_WIDTH // 2, self.rect.y + 15), 5)

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT)
        self.direction = random.choice([-1, 1])
        self.speed = 2

    def update(self):
        self.rect.x += self.direction * self.speed
        if self.rect.x <= 0 or self.rect.x >= WORLD_WIDTH - ENEMY_WIDTH:
            self.direction *= -1
            self.speed = random.uniform(1.5, 2.5)

    def draw(self, screen, camera_x):
        pygame.draw.rect(screen, ENEMY_COLOR, self.rect.move(-camera_x, 0))
        pygame.draw.circle(screen, (0, 0, 0), (self.rect.x - camera_x + ENEMY_WIDTH // 2, self.rect.y + 10), 5)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Super Mario Bros 1-1 Medium")
    clock = pygame.time.Clock()

    game = Game()
    camera_x = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r and game.game_over:
                    game.reset()
                    camera_x = 0

        game.update()

        # 摄像机跟随
        if not game.game_over:
            target_camera_x = game.player.rect.centerx - SCREEN_WIDTH // 2
            target_camera_x = max(0, min(target_camera_x, WORLD_WIDTH - SCREEN_WIDTH))
            camera_x = camera_x * 0.9 + target_camera_x * 0.1

        game.draw(screen, camera_x)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()