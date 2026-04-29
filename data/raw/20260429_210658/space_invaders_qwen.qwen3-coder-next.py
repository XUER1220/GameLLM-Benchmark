import pygame
import random
import sys

pygame.init()

# 固定参数
WIDTH, HEIGHT = 800, 600
FPS = 60
FPS_CLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders Medium")

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# 常量定义
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 32
PLAYER_Y = HEIGHT - 40 - PLAYER_HEIGHT
PLAYER_SPEED = 6

BULLET_WIDTH = 6
BULLET_HEIGHT = 16
BULLET_SPEED = 8

ENEMY_ROWS = 4
ENEMY_COLS = 8
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 30
ENEMY startX = (WIDTH - ENEMY_COLS * ENEMY_WIDTH) // 2
ENEMY_Y_START = 60
ENEMY_SPEED = 1.2
ENEMY_DROP = 20

PLAYER_LIVES = 3
SCORE_PER_KILL = 10

random.seed(42)

# 按钮控制
KEYS_PRESSED = {}

class Player:
    def __init__(self):
        self.rect = pygame.Rect((WIDTH - PLAYER_WIDTH) // 2, PLAYER_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.lives = PLAYER_LIVES
        self.bullets = []
        self.shoot_cooldown = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED

        self.rect.x = max(0, min(self.rect.x, WIDTH - PLAYER_WIDTH))

        # 发射子弹
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if KEYS_PRESSED.get(pygame.K_SPACE) and self.shoot_cooldown == 0:
            bullet = pygame.Rect(self.rect.centerx - BULLET_WIDTH // 2, self.rect.top, BULLET_WIDTH, BULLET_HEIGHT)
            self.bullets.append(bullet)
            self.shoot_cooldown = 20  # 冷却时间

    def draw(self, screen):
        # 简单的玩家飞船绘制（蓝色梯形）
        points = [
            (self.rect.centerx, self.rect.top),  # 顶点
            (self.rect.left, self.rect.bottom),
            (self.rect.right, self.rect.bottom)
        ]
        pygame.draw.polygon(screen, BLUE, points)

    def draw_lives(self, screen, font):
        text = font.render(f'Lives: {self.lives}', True, WHITE)
        screen.blit(text, (10, 50))

class Enemy:
    def __init__(self):
        self.enemies = []
        self.direction = 1  # 1 = 右, -1 = 左
        self.speed = ENEMY_SPEED

        # 创建外星人阵列
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                x = ENEMY startX + col * ENEMY_WIDTH
                y = ENEMY_Y_START + row * ENEMY_HEIGHT
                self.enemies.append(pygame.Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT))

    def update(self):
        move_right = self.direction > 0
        will_hit_boundary = False

        # 检查是否碰到边界
        for enemy in self.enemies:
            if self.direction == 1 and enemy.right >= WIDTH:
                will_hit_boundary = True
                break
            elif self.direction == -1 and enemy.left <= 0:
                will_hit_boundary = True
                break

        if will_hit_boundary:
            self.direction *= -1
            for enemy in self.enemies:
                enemy.y += ENEMY_DROP
        else:
            for enemy in self.enemies:
                enemy.x += self.direction * self.speed

    def draw(self, screen):
        for enemy in self.enemies:
            # 简单的敌人形状（绿色矩形 + 眼睛）
            pygame.draw.rect(screen, GREEN, enemy)
            # 简单的眼睛
            eye_size = 4
            left_eye = pygame.Rect(enemy.x + 8, enemy.y + 6, eye_size, eye_size)
            right_eye = pygame.Rect(enemy.x + 24, enemy.y + 6, eye_size, eye_size)
            pygame.draw.rect(screen, BLACK, left_eye)
            pygame.draw.rect(screen, BLACK, right_eye)

    def fire_bullet(self, bullets):
        # 随机选择一行中的多个敌人进行射击
        if len(self.enemies) > 0 and random.random() < 0.02:  # 较低频率
            shooter = random.choice(self.enemies)
            bullet = pygame.Rect(shooter.centerx - BULLET_WIDTH // 2, shooter.bottom, BULLET_WIDTH, BULLET_HEIGHT)
            bullets.append(bullet)

class Game:
    def __init__(self):
        self.player = Player()
        self.enemies = Enemy()
        self.enemy_bullets = []
        self.score = 0
        self.game_over = False
        self.victory = False
        self.font = pygame.font.SysFont(None, 36)
        self.big_font = pygame.font.SysFont(None, 72)

    def reset(self):
        self.player = Player()
        self.enemies = Enemy()
        self.enemy_bullets = []
        self.score = 0
        self.game_over = False
        self.victory = False

    def check_collisions(self):
        # 玩家子弹击中敌人
        for bullet in list(self.player.bullets):
            hit = False
            for enemy in list(self.enemies.enemies):
                if bullet.colliderect(enemy):
                    self.enemies.enemies.remove(enemy)
                    self.player.bullets.remove(bullet)
                    self.score += SCORE_PER_KILL
                    hit = True
                    break
            if not hit and bullet.y < 0:
                self.player.bullets.remove(bullet)

        # 敌人子弹击中玩家
        for bullet in list(self.enemy_bullets):
            if bullet.colliderect(self.player.rect):
                self.player.bullets.remove(bullet) if bullet in self.player.bullets else None
                self.enemy_bullets.remove(bullet)
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self.game_over = True
            elif bullet.y > HEIGHT:
                self.enemy_bullets.remove(bullet)

        # 检查敌人是否到达玩家所在高度或全部消灭
        for enemy in self.enemies.enemies:
            if enemy.bottom >= PLAYER_Y:
                self.game_over = True
                break
        if len(self.enemies.enemies) == 0:
            self.victory = True

    def draw_ui(self, screen):
        # 分数
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        screen.blit(score_text, (10, 10))

        # 生命
        self.player.draw_lives(screen, self.font)

        # 游戏状态
        if self.game_over or self.victory:
            if self.victory:
                text = self.big_font.render("VICTORY!", True, GREEN)
            else:
                text = self.big_font.render("GAME OVER", True, RED)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
            screen.blit(text, text_rect)

            restart_text = self.font.render("Press R to Restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
            screen.blit(restart_text, restart_rect)

    def update(self):
        if self.game_over or self.victory:
            return

        self.player.update()
        self.enemies.update()
        
        # 敌人射击
        self.enemies.fire_bullet(self.enemy_bullets)

        # 更新子弹位置
        for bullet in self.player.bullets:
            bullet.y -= BULLET_SPEED
        for bullet in self.enemy_bullets:
            bullet.y += BULLET_SPEED

        self.check_collisions()

    def draw(self, screen):
        # 背景
        screen.fill(BLACK)

        # 绘制所有对象
        self.player.draw(screen)
        self.enemies.draw(screen)

        # 绘制子弹
        for bullet in self.player.bullets:
            pygame.draw.rect(screen, WHITE, bullet)
        for bullet in self.enemy_bullets:
            pygame.draw.rect(screen, RED, bullet)

        # HUD 和 UI
        self.draw_ui(screen)

        pygame.display.flip()

def main():
    game = Game()
    running = True

    while running:
        KEYS_PRESSED.clear()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                KEYS_PRESSED[event.key] = True
                if event.key == pygame.K_r and (game.game_over or game.victory):
                    game.reset()
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.KEYUP:
                if event.key in KEYS_PRESSED:
                    del KEYS_PRESSED[event.key]

        game.update()
        game.draw(SCREEN)

        FPS_CLOCK.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()