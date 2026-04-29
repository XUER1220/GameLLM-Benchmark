import pygame
import sys
import random

# 固定参数
_WIDTH, _HEIGHT = 800, 600
FPS = 60
PLAYER_WIDTH, PLAYER_HEIGHT = 40, 56
PLAYER_SPEED = 5
JUMP_FORCE = -12
GRAVITY = 0.5
MAX_LIVES = 3
SCORE_PER_COIN = 10

# 颜色定义
COLOR_PLAYER = (0, 255, 255)
COLOR_PLATFORM = (100, 100, 100)
COLOR_ENEMY = (255, 50, 50)
COLOR_COIN = (255, 215, 0)
COLOR_FLAG = (0, 255, 0)
COLOR_HUD_BG = (30, 30, 30)
COLOR_HUD_TEXT = (255, 255, 255)
COLOR_GAME_OVER = (200, 50, 50)
COLOR_VICTORY = (50, 200, 50)

# 平台定义: (x, y, width, height)
PLATFORMS = [
    (0, 550, 800, 50),  # 地面平台
    (200, 450, 200, 20),
    (500, 380, 150, 20),
    (100, 300, 180, 20),
    (400, 220, 200, 20),
    (650, 150, 150, 20),
]

# 金币定义: (x, y)
COINS = [
    (250, 420),
    (550, 350),
    (150, 270),
    (450, 190),
    (700, 120),
]

# 敌人定义: (x, y, patrol_left, patrol_right)
ENEMIES = [
    (220, 420, 200, 350),
    (520, 350, 450, 600),
    (670, 120, 650, 750),
]

# 终点旗帜位置
FLAG_X, FLAG_Y = 750, 100

# 初始化
random.seed(42)
pygame.init()
screen = pygame.display.set_mode((_WIDTH, _HEIGHT))
pygame.display.set_caption("Platformer Hard")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)


class Player:
    def __init__(self):
        self.rect = pygame.Rect(50, 494, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_y = 0
        self.lives = MAX_LIVES
        self.is_dead = False

    def update(self, platforms):
        if self.is_dead:
            return

        # 水平移动
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED

        # 边界检查
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > _WIDTH:
            self.rect.right = _WIDTH

        # 跳跃
        if keys[pygame.K_SPACE] and self.on_ground(platforms):
            self.vel_y = JUMP_FORCE

        # 重力
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # 碰撞检测（平台）
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vel_y > 0:  # 下落中碰撞
                    self.rect.bottom = plat.top
                    self.vel_y = 0
                elif self.vel_y < 0:  # 上升中碰撞
                    self.rect.top = plat.bottom
                    self.vel_y = 0

        # 生命为零或掉出屏幕底部
        if self.rect.bottom > _HEIGHT:
            self.lives = 0
            self.is_dead = True

    def on_ground(self, platforms):
        if self.rect.bottom >= _HEIGHT - 2:
            return True
        for plat in platforms:
            if self.rect.bottom <= plat.bottom and \
               self.rect.bottom >= plat.top and \
               self.rect.left < plat.right and \
               self.rect.right > plat.left and \
               self.vel_y >= 0:
                return True
        return False

    def hit_by_enemy(self):
        self.lives -= 1
        if self.lives <= 0:
            self.lives = 0
            self.is_dead = True
        else:
            # 击退/重置到最近安全位置
            # 简单处理：重置到出生点
            self.rect.x = 50
            self.rect.y = 494 - PLAYER_HEIGHT
            self.vel_y = 0

    def draw(self, screen):
        pygame.draw.rect(screen, COLOR_PLAYER, self.rect)


class Enemy:
    def __init__(self, x, y, min_x, max_x):
        self.rect = pygame.Rect(x, y, 36, 36)
        self.min_x = min_x
        self.max_x = max_x
        self.direction = 1  # 1: right, -1: left
        self.speed = 2

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.left <= self.min_x or self.rect.right >= self.max_x:
            self.direction *= -1

    def draw(self, screen):
        pygame.draw.rect(screen, COLOR_ENEMY, self.rect)


class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.collected = False

    def draw(self, screen):
        if not self.collected:
            pygame.draw.circle(screen, COLOR_COIN, self.rect.center, 10)


class Flag:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 50)

    def draw(self, screen):
        pygame.draw.rect(screen, COLOR_FLAG, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)


def draw_hud(score, player):
    hud_surface = pygame.Surface((_WIDTH, 40))
    hud_surface.fill(COLOR_HUD_BG)
    screen.blit(hud_surface, (0, 0))
    
    lives_text = font.render(f"Lives: {player.lives}", True, COLOR_HUD_TEXT)
    score_text = font.render(f"Score: {score}", True, COLOR_HUD_TEXT)
    screen.blit(lives_text, (10, 5))
    screen.blit(score_text, (200, 5))


def draw_game_over(score, victory=False):
    overlay = pygame.Surface((_WIDTH, _HEIGHT))
    overlay.set_alpha(200)
    color = COLOR_VICTORY if victory else COLOR_GAME_OVER
    overlay.fill(color)
    screen.blit(overlay, (0, 0))

    msg = font.render("VICTORY!" if victory else "GAME OVER", True, (255, 255, 255))
    score_msg = font.render(f"Final Score: {score}", True, (255, 255, 255))
    restart_msg = font.render("Press R to Restart", True, (255, 255, 255))

    screen.blit(msg, (_WIDTH // 2 - msg.get_width() // 2, 200))
    screen.blit(score_msg, (_WIDTH // 2 - score_msg.get_width() // 2, 250))
    screen.blit(restart_msg, (_WIDTH // 2 - restart_msg.get_width() // 2, 300))


def reset_game():
    player = Player()
    enemies = [Enemy(*e) for e in ENEMIES]
    coins = [Coin(*c) for c in COINS]
    flag = Flag(FLAG_X, FLAG_Y)
    score = 0
    game_over = False
    victory = False
    
    return player, enemies, coins, flag, score, game_over, victory


def main():
    player, enemies, coins, flag, score, game_over, victory = reset_game()
    platforms = [pygame.Rect(*p) for p in PLATFORMS]
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    player, enemies, coins, flag, score, game_over, victory = reset_game()

        if not game_over:
            player.update(platforms)
            for enemy in enemies:
                enemy.update()
                if player.rect.colliderect(enemy.rect):
                    player.hit_by_enemy()
                    if player.lives == 0:
                        game_over = True

            for coin in coins:
                if not coin.collected and player.rect.colliderect(coin.rect):
                    coin.collected = True
                    score += SCORE_PER_COIN

            if player.rect.colliderect(flag.rect) and not player.is_dead:
                game_over = True
                victory = True

            if player.lives == 0:
                game_over = True
            if player.rect.bottom > _HEIGHT:
                game_over = True

        # 绘制
        screen.fill((50, 50, 50))
        for plat in platforms:
            pygame.draw.rect(screen, COLOR_PLATFORM, plat)

        for coin in coins:
            coin.draw(screen)
        flag.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        player.draw(screen)
        
        draw_hud(score, player)

        if game_over:
            draw_game_over(score, victory)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()