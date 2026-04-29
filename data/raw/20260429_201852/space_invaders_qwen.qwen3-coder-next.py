import pygame
import random

# 固定参数
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_WIDTH, PLAYER_HEIGHT = 60, 32
PLAYER_Y_MARGIN = 40
PLAYER_SPEED = 6
BULLET_WIDTH, BULLET_HEIGHT = 6, 16
BULLET_SPEED = 8
ALIEN_ROWS, ALIEN_COLS = 4, 8
ALIEN_WIDTH, ALIEN_HEIGHT = 40, 30
ALIEN_MOVE_SPEED = 1.2
ALIEN_DROP_DISTANCE = 20
PLAYER_LIVES = 3
ALIEN_BULLET_CHANCE = 0.002  # 每帧敌子弹发射概率（较低频率）

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# 初始化pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()

# 设置随机种子
random.seed(42)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(
            (WIDTH - PLAYER_WIDTH) // 2, 
            HEIGHT - PLAYER_Y_MARGIN - PLAYER_HEIGHT, 
            PLAYER_WIDTH, PLAYER_HEIGHT
        )
        self.lives = PLAYER_LIVES
        self.bullets = []
        self.shoot_cooldown = 0

    def update(self, keys):
        # 移动玩家
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        # 边界检查
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        
        # 发射子弹
        if keys[pygame.K_SPACE] and self.shoot_cooldown <= 0:
            self.bullets.append(pygame.Rect(
                self.rect.centerx - BULLET_WIDTH // 2, 
                self.rect.top, 
                BULLET_WIDTH, BULLET_HEIGHT
            ))
            self.shoot_cooldown = 10  # 发射间隔
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def draw(self, surface):
        # 绘制玩家飞船（简单矩形）
        pygame.draw.rect(surface, GREEN, self.rect)

class Alien:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, ALIEN_WIDTH, ALIEN_HEIGHT)

class Game:
    def __init__(self):
        self.player = Player()
        self.aliens = []
        self.alien_direction = 1  # 1向右，-1向左
        self.alien_move_timer = 0
        self.alien_bullets = []
        self.score = 0
        self.game_over = False
        self.won = False
        
        # 初始化外星人阵列
        alien_start_x = (WIDTH - (ALIEN_COLS * ALIEN_WIDTH)) // 2
        alien_start_y = 60
        for row in range(ALIEN_ROWS):
            for col in range(ALIEN_COLS):
                alien = Alien(
                    alien_start_x + col * ALIEN_WIDTH,
                    alien_start_y + row * (ALIEN_HEIGHT + 15)
                )
                self.aliens.append(alien)

    def update(self, keys):
        if self.game_over:
            return

        # 更新玩家
        self.player.update(keys)

        # 更新玩家子弹
        for bullet in self.player.bullets[:]:
            bullet.y -= BULLET_SPEED
            if bullet.y < 0:
                self.player.bullets.remove(bullet)

        # 更新敌人子弹
        for bullet in self.alien_bullets[:]:
            bullet.y += BULLET_SPEED
            if bullet.y > HEIGHT:
                self.alien_bullets.remove(bullet)
                continue

            # 敌人子弹击中玩家
            if bullet.colliderect(self.player.rect):
                self.alien_bullets.remove(bullet)
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self.game_over = True

        # 更新外星人移动
        self.alien_move_timer += ALIEN_MOVE_SPEED
        if self.alien_move_timer >= 1.0:
            self.alien_move_timer = 0
            
            # 碰到边界则下移并反向
            hit_boundary = False
            for alien in self.aliens:
                if self.alien_direction == 1 and alien.rect.right >= WIDTH:
                    hit_boundary = True
                    break
                elif self.alien_direction == -1 and alien.rect.left <= 0:
                    hit_boundary = True
                    break
            
            if hit_boundary:
                self.alien_direction *= -1
                for alien in self.aliens:
                    alien.rect.y += ALIEN_DROP_DISTANCE
                    # 游戏失败条件：敌人到达玩家高度
                    if alien.rect.bottom >= self.player.rect.top:
                        self.game_over = True
            else:
                # 常规移动
                for alien in self.aliens:
                    alien.rect.x += self.alien_direction * ALIEN_MOVE_SPEED

        # 敌人随机发射子弹
        for alien in self.aliens:
            if random.random() < ALIEN_BULLET_CHANCE:
                self.alien_bullets.append(pygame.Rect(
                    alien.rect.centerx - BULLET_WIDTH // 2,
                    alien.rect.bottom,
                    BULLET_WIDTH, BULLET_HEIGHT
                ))

        # 碰撞检测：玩家子弹击中敌人
        for bullet in self.player.bullets[:]:
            for alien in self.aliens[:]:
                if bullet.colliderect(alien.rect):
                    self.player.bullets.remove(bullet)
                    self.aliens.remove(alien)
                    self.score += 10
                    break  # 一颗子弹只能击中一个敌人
        
        # 胜利条件：所有敌人被消灭
        if len(self.aliens) == 0:
            self.won = True
            self.game_over = True

    def draw(self, surface):
        # 背景
        surface.fill(BLACK)
        
        # 绘制玩家
        self.player.draw(surface)
        
        # 绘制敌人
        for alien in self.aliens:
            pygame.draw.rect(surface, RED, alien.rect)
        
        # 绘制玩家子弹
        for bullet in self.player.bullets:
            pygame.draw.rect(surface, WHITE, bullet)
        
        # 绘制敌人子弹
        for bullet in self.alien_bullets:
            pygame.draw.rect(surface, YELLOW, bullet)
        
        # HUD
        font = pygame.font.SysFont(None, 24)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        lives_text = font.render(f'Lives: {self.player.lives}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - 120, 10))
        
        # 游戏结束界面
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            big_font = pygame.font.SysFont(None, 64)
            if self.won:
                text = big_font.render('YOU WIN!', True, GREEN)
            else:
                text = big_font.render('GAME OVER', True, RED)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            screen.blit(text, rect)
            
            restart_font = pygame.font.SysFont(None, 32)
            restart_text = restart_font.render('Press R to Restart', True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
            screen.blit(restart_text, restart_rect)

    def reset(self):
        self.__init__()

def main():
    game = Game()
    running = True
    keys = pygame.key.get_pressed()

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game.game_over:
                    game.reset()

        keys = pygame.key.get_pressed()
        game.update(keys)
        game.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()