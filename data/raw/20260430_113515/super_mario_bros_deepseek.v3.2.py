import pygame
import random

pygame.init()

# ===== 常量定义 =====
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WORLD_WIDTH = 3200
WORLD_HEIGHT = 600
FPS = 60
random.seed(42)

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 150, 50)
GRAY = (150, 150, 150)
BROWN = (150, 100, 50)
PURPLE = (200, 50, 200)
LIGHT_BLUE = (100, 200, 255)
LIGHT_GREEN = (100, 255, 150)

# 玩家
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 48
PLAYER_COLOR = BLUE
PLAYER_SPEED = 5
JUMP_SPEED = -12
GRAVITY = 0.5
MAX_FALL_SPEED = 15

# 地面与基本地图
GROUND_HEIGHT = 480  # 地面顶部Y坐标
GROUND_COLOR = BROWN

# 砖块和问号砖
BLOCK_WIDTH = 40
BLOCK_HEIGHT = 40
BRICK_COLOR = RED
QUESTION_COLOR = YELLOW

# 金币
COIN_SIZE = 18
COIN_COLOR = YELLOW
COIN_SCORE = 100

# 敌人
ENEMY_SIZE = 32
ENEMY_COLOR = RED
ENEMY_SPEED = 2
ENEMY_SCORE = 200

# 管道
PIPE_WIDTH = 60
PIPE_HEIGHT = 80
PIPE_COLOR = GREEN

# 台阶
STAIR_WIDTH = 40
STAIR_HEIGHT = 20
STAIR_COLOR = GRAY

# 旗杆
FLAGPOLE_WIDTH = 20
FLAGPOLE_HEIGHT =82
FLAGPOLE_X = WORLD_WIDTH - 100
FLAGPOLE_COLOR = WHITE
FLAG_COLOR = RED

# HUD
HUD_HEIGHT = 70
FONT_SIZE = 28
LIVES_START = 3

# ===== 关卡固定布局 =====
# 地面（y坐标固定）
ground_rects = [
    pygame.Rect(0, GROUND_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT - GROUND_HEIGHT)
]

# 砖块 (位置x, y)
brick_positions = [
    (200, 400), (240, 400), (280, 400), (320, 400),
    (500, 350), (540, 350), (580, 350),
    (1200, 300), (1240, 300), (1280, 300),
    (1800, 350), (1840, 350)
]

# 问号砖
question_positions = [
    (400, 300), (440, 300), (480, 300),
    (900, 250), (940, 250),
    (1400, 300), (1440, 300),
    (1900, 250), (1940, 250), (1980, 250)
]

# 管道 (x, y) y为顶部坐标
pipe_rects = [
    pygame.Rect(700, GROUND_HEIGHT - PIPE_HEIGHT, PIPE_WIDTH, PIPE_HEIGHT),
    pygame.Rect(1100, GROUND_HEIGHT - PIPE_HEIGHT, PIPE_WIDTH, PIPE_HEIGHT),
    pygame.Rect(2400, GROUND_HEIGHT - 60, PIPE_WIDTH, 60)
]

# 台阶 (x, y) 平台性质，Y为顶部坐标
stair_rects = [
    pygame.Rect(2200, GROUND_HEIGHT - 60, 150, 20),
    pygame.Rect(2700, GROUND_HEIGHT - 100, 200, 20),
    pygame.Rect(FLAGPOLE_X - 80, GROUND_HEIGHT - 120, 100, 20)
]

# 坑洞 (x_start, x_end)
gaps = [
    (1500, 1600),
    (2600, 2680)
]

# 金币 (x, y)
coin_positions = [
    (220, 360), (260, 360), (300, 360), (340, 360),
    (520, 310), (560, 310),
    (1220, 260), (1260, 260),
    (1420, 260), (1460, 260),
    (1920, 210), (1980, 210)
]

# 敌人初始位置和巡逻边界 (x, y, left_bound, right_bound)
enemies_init = [
    (400, GROUND_HEIGHT - ENEMY_SIZE, 350, 500),
    (1000, GROUND_HEIGHT - ENEMY_SIZE, 950, 1150),
    (2300, GROUND_HEIGHT - 60 - ENEMY_SIZE, 2250, 2400)
]

# ===== 游戏类 =====
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario Bros Medium")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.reset()

    def reset(self):
        # 玩家
        self.player = pygame.Rect(50, GROUND_HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True

        # 游戏状态
        self.lives = LIVES_START
        self.score = 0
        self.coins = 0
        self.game_over = False
        self.game_won = False
        self.camera_x = 0

        # 金币
        self.coins = [pygame.Rect(x, y, COIN_SIZE, COIN_SIZE) for x, y in coin_positions]

        # 敌人
        self.enemies = []
        for x, y, left, right in enemies_init:
            enemy = {
                "rect": pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE),
                "direction": 1,
                "left_bound": left,
                "right_bound": right
            }
            self.enemies.append(enemy)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                if event.key == pygame.K_r:
                    self.reset()
                if not self.game_over and not self.game_won:
                    if event.key == pygame.K_SPACE and self.on_ground:
                        self.vel_y = JUMP_SPEED
                        self.on_ground = False

        if not self.game_over and not self.game_won:
            keys = pygame.key.get_pressed()
            self.vel_x = 0
            if keys[pygame.K_LEFT]:
                self.vel_x = -PLAYER_SPEED
                self.facing_right = False
            if keys[pygame.K_RIGHT]:
                self.vel_x = PLAYER_SPEED
                self.facing_right = True

    def update_player(self):
        # 水平移动
        self.player.x += self.vel_x
        if self.player.left < 0:
            self.player.left = 0
        if self.player.right > WORLD_WIDTH:
            self.player.right = WORLD_WIDTH

        # 垂直移动（重力）
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED
        self.player.y += self.vel_y

        # 防止穿地
        if self.player.bottom > WORLD_HEIGHT:
            self.player.bottom = WORLD_HEIGHT
            self.vel_y = 0

        # 检查是否在地面
        self.on_ground = False
        if self.player.bottom == WORLD_HEIGHT or self.check_collisions_vertical():
            self.on_ground = True
            self.vel_y = 0

        # 摄像机跟随
        target_camera_x = self.player.centerx - SCREEN_WIDTH // 2
        self.camera_x = max(0, min(target_camera_x, WORLD_WIDTH - SCREEN_WIDTH))

        # 跌落坑洞
        in_gap = any(start < self.player.centerx < end for start, end in gaps)
        if self.player.top > WORLD_HEIGHT or in_gap:
            self.lose_life()

        # 触碰旗杆
        flagpole_rect = pygame.Rect(FLAGPOLE_X, GROUND_HEIGHT - FLAGPOLE_HEIGHT, FLAGPOLE_WIDTH, FLAGPOLE_HEIGHT)
        if self.player.colliderect(flagpole_rect):
            if not self.game_over:
                self.game_won = True

    def check_collisions_vertical(self):
        # 检查地面碰撞
        for rect in ground_rects:
            if self.player.colliderect(rect) and self.vel_y > 0 and self.player.bottom <= rect.top + 10:
                self.player.bottom = rect.top
                return True

        # 检查砖块、问号砖
        for pos in brick_positions + question_positions:
            block_rect = pygame.Rect(pos[0], pos[1], BLOCK_WIDTH, BLOCK_HEIGHT)
            if self.player.colliderect(block_rect) and self.vel_y > 0 and self.player.bottom <= block_rect.top + 10:
                self.player.bottom = block_rect.top
                return True

        # 管道
        for rect in pipe_rects:
            if self.player.colliderect(rect) and self.vel_y > 0 and self.player.bottom <= rect.top + 10:
                self.player.bottom = rect.top
                return True

        # 台阶
        for rect in stair_rects:
            if self.player.colliderect(rect) and self.vel_y > 0 and self.player.bottom <= rect.top + 10:
                self.player.bottom = rect.top
                return True
        return False

    def update_enemies(self):
        for enemy in self.enemies[:]:
            enemy["rect"].x += enemy["direction"] * ENEMY_SPEED
            if enemy["rect"].left <= enemy["left_bound"]:
                enemy["direction"] = 1
            if enemy["rect"].right >= enemy["right_bound"]:
                enemy["direction"] = -1

            # 敌人与玩家碰撞
            if self.player.colliderect(enemy["rect"]):
                if self.vel_y > 0 and self.player.bottom <= enemy["rect"].top + 15:
                    # 踩敌人
                    self.enemies.remove(enemy)
                    self.score += ENEMY_SCORE
                    self.vel_y = JUMP_SPEED * 0.5
                else:
                    # 侧面碰撞
                    self.lose_life()

    def update_coins(self):
        for coin in self.coins[:]:
            if self.player.colliderect(coin):
                self.coins.remove(coin)
                self.score += COIN_SCORE
                self.coins += 1

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
        else:
            # 复位到安全位置
            self.player.x = 50
            self.player.y = GROUND_HEIGHT - PLAYER_HEIGHT
            self.vel_x = 0
            self.vel_y = 0
            self.camera_x = 0

    def draw(self):
        self.screen.fill(LIGHT_BLUE)  # 天空色

        # 绘制地面
        for rect in ground_rects:
            pygame.draw.rect(self.screen, GROUND_COLOR, rect.move(-self.camera_x, 0))
            # 地面顶部线条
            pygame.draw.line(self.screen, BLACK,
                             (rect.left - self.camera_x, rect.top),
                             (rect.right - self.camera_x, rect.top), 2)

        # 绘制坑洞
        for start, end in gaps:
            hole_rect = pygame.Rect(start, GROUND_HEIGHT, end - start, 20)
            pygame.draw.rect(self.screen, BLACK, hole_rect.move(-self.camera_x, 0))

        # 绘制砖块
        for pos in brick_positions:
            rect = pygame.Rect(pos[0], pos[1], BLOCK_WIDTH, BLOCK_HEIGHT).move(-self.camera_x, 0)
            pygame.draw.rect(self.screen, BRICK_COLOR, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
            # 砖块纹理
            for i in range(3):
                pygame.draw.line(self.screen, (200, 100, 100),
                                 (rect.left + 5 + i * 10, rect.top + 5),
                                 (rect.left + 5 + i * 10, rect.bottom - 5), 2)

        # 绘制问号砖
        for pos in question_positions:
            rect = pygame.Rect(pos[0], pos[1], BLOCK_WIDTH, BLOCK_HEIGHT).move(-self.camera_x, 0)
            pygame.draw.rect(self.screen, QUESTION_COLOR, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
            # 问号标记
            font_small = pygame.font.SysFont(None, 30)
            text = font_small.render("?", True, BLACK)
            self.screen.blit(text, text.get_rect(center=rect.center))

        # 绘制管道
        for rect in pipe_rects:
            draw_rect = rect.move(-self.camera_x, 0)
            pygame.draw.rect(self.screen, PIPE_COLOR, draw_rect)
            pygame.draw.rect(self.screen, BLACK, draw_rect, 2)
            # 管道顶部
            top_rect = pygame.Rect(rect.left + 5, rect.top - 10, rect.width - 10, 10).move(-self.camera_x, 0)
            pygame.draw.rect(self.screen, PIPE_COLOR, top_rect)
            pygame.draw.rect(self.screen, BLACK, top_rect, 2)

        # 绘制台阶
        for rect in stair_rects:
            draw_rect = rect.move(-self.camera_x, 0)
            pygame.draw.rect(self.screen, STAIR_COLOR, draw_rect)
            pygame.draw.rect(self.screen, BLACK, draw_rect, 2)

        # 绘制金币
        for coin in self.coins:
            draw_rect = coin.move(-self.camera_x, 0)
            pygame.draw.ellipse(self.screen, COIN_COLOR, draw_rect)
            pygame.draw.ellipse(self.screen, ORANGE, draw_rect, 3)
            # 金币高光
            pygame.draw.ellipse(self.screen, WHITE, (draw_rect.x + 4, draw_rect.y + 4, 5, 5))

        # 绘制敌人
        for enemy in self.enemies:
            draw_rect = enemy["rect"].move(-self.camera_x, 0)
            pygame.draw.rect(self.screen, ENEMY_COLOR, draw_rect)
            pygame.draw.rect(self.screen, BLACK, draw_rect, 2)
            # 敌人眼睛
            eye_offset = 5 if enemy["direction"] > 0 else -5
            pygame.draw.circle(self.screen, WHITE, (draw_rect.centerx + eye_offset, draw_rect.centery - 6), 4)
            pygame.draw.circle(self.screen, BLACK, (draw_rect.centerx + eye_offset, draw_rect.centery - 6), 2)

        # 绘制旗杆
        flagpole_rect = pygame.Rect(FLAGPOLE_X, GROUND_HEIGHT - FLAGPOLE_HEIGHT, FLAGPOLE_WIDTH, FLAGPOLE_HEIGHT)
        draw_flagpole = flagpole_rect.move(-self.camera_x, 0)
        pygame.draw.rect(self.screen, FLAGPOLE_COLOR, draw_flagpole)
        pygame.draw.rect(self.screen, BLACK, draw_flagpole, 2)
        # 旗帜
        flag_rect = pygame.Rect(FLAGPOLE_X - 40, GROUND_HEIGHT - FLAGPOLE_HEIGHT + 20, 60, 40).move(-self.camera_x, 0)
        pygame.draw.polygon(self.screen, FLAG_COLOR, [
            (flag_rect.left, flag_rect.top),
            (flag_rect.right, flag_rect.centery),
            (flag_rect.left, flag_rect.bottom)
        ])
        pygame.draw.polygon(self.screen, BLACK, [
            (flag_rect.left, flag_rect.top),
            (flag_rect.right, flag_rect.centery),
            (flag_rect.left, flag_rect.bottom)
        ], 2)

        # 绘制玩家
        player_draw = self.player.move(-self.camera_x, 0)
        pygame.draw.rect(self.screen, PLAYER_COLOR, player_draw)
        pygame.draw.rect(self.screen, BLACK, player_draw, 2)
        # 玩家眼睛
        eye_x = player_draw.right - 10 if self.facing_right else player_draw.left + 10
        pygame.draw.circle(self.screen, WHITE, (eye_x, player_draw.top + 15), 6)
        pygame.draw.circle(self.screen, BLACK, (eye_x, player_draw.top + 15), 3)

        # HUD背景
        pygame.draw.rect(self.screen, BLACK, (0, 0, SCREEN_WIDTH, HUD_HEIGHT))
        pygame.draw.rect(self.screen, GRAY, (2, 2, SCREEN_WIDTH - 4, HUD_HEIGHT - 4))

        # HUD文字
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        coins_text = self.font.render(f"Coins: {self.coins}", True, WHITE)
        self.screen.blit(lives_text, (20, 20))
        self.screen.blit(score_text, (200, 20))
        self.screen.blit(coins_text, (400, 20))

        # 游戏结束或胜利提示
        if self.game_over or self.game_won:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            result_text = "You Win!" if self.game_won else "Game Over"
            color = GREEN if self.game_won else RED
            result_surf = self.font.render(result_text, True, color)
            score_surf = self.font.render(f"Final Score: {self.score}", True, YELLOW)
            restart_surf = self.font.render("Press R to Restart", True, WHITE)

            self.screen.blit(result_surf, result_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))
            self.screen.blit(score_surf, score_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
            self.screen.blit(restart_surf, restart_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)))

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            if not self.game_over and not self.game_won:
                self.update_player()
                self.update_enemies()
                self.update_coins()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()