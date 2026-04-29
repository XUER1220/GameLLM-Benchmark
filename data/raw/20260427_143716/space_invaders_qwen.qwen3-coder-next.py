import pygame
import random
import sys

# 固定参数
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 玩家参数
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 32
PLAYER_Y = SCREEN_HEIGHT - 40 - PLAYER_HEIGHT
PLAYER_SPEED = 6

# 子弹参数
BULLET_WIDTH = 6
BULLET_HEIGHT = 16
BULLET_SPEED = 8

# 敌人参数
ALIEN_ROWS = 4
ALIEN_COLS = 8
ALIEN_WIDTH = 40
ALIEN_HEIGHT = 30
ALIEN_X_START = 50
ALIEN_Y_START = 50
ALIEN_SEP_X = 35
ALIEN_SEP_Y = 25
ALIEN_MOVE_SPEED = 1.2
ALIEN_DROP_DISTANCE = 20
ALIEN_SHOOT_RATE = 0.005  # 每帧射击概率

# 分数与生命
PLAYER_LIVES = 3
SCORE_PER_KILL = 10

# 颜色
BG_COLOR = (0, 0, 0)
PLAYER_COLOR = (0, 255, 0)
ALIEN_COLOR = (255, 0, 0)
BULLET_COLOR = (255, 255, 255)
TEXT_COLOR = (255, 255, 255)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, PLAYER_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.lives = PLAYER_LIVES
        self.bullets = []

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        # 保持在屏幕内
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))

    def shoot(self):
        bullet = Bullet(self.rect.centerx - BULLET_WIDTH // 2, self.rect.top, -1)
        self.bullets.append(bullet)

    def reset(self):
        self.rect.x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
        self.lives = PLAYER_LIVES
        self.bullets = []


class Bullet:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, BULLET_WIDTH, BULLET_HEIGHT)
        self.direction = direction  # -1: up (player), 1: down (alien)
        self.speed = BULLET_SPEED

    def update(self):
        self.rect.y += self.direction * self.speed

    def is_offscreen(self):
        return self.rect.y < 0 or self.rect.y > SCREEN_HEIGHT


class Alien:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, ALIEN_WIDTH, ALIEN_HEIGHT)
        self.alive = True

    def set_position(self, x, y):
        self.rect.topleft = (x, y)


class Game:
    def __init__(self):
        random.seed(42)
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders Medium")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.aliens = []
        self.aliens_bullets = []
        self.score = 0
        self.is_running = True
        self.game_over = False
        self.won = False
        self.alien_direction = 1

        # 初始化敌人阵列
        self.create_aliens()

    def create_aliens(self):
        self.aliens.clear()
        for row in range(ALIEN_ROWS):
            for col in range(ALIEN_COLS):
                x = ALIEN_X_START + col * (ALIEN_WIDTH + ALIEN_SEP_X)
                y = ALIEN_Y_START + row * (ALIEN_HEIGHT + ALIEN_SEP_Y)
                self.aliens.append(Alien(x, y))

    def update(self):
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.player.move(keys)

        # 玩家射击（空格键）
        if keys[pygame.K_SPACE] and len(self.player.bullets) == 0:
            self.player.shoot()

        # 更新玩家子弹
        self.player.bullets = [b for b in self.player.bullets if not b.is_offscreen()]
        for bullet in self.player.bullets:
            bullet.update()

        # 更新敌人子弹
        self.aliens_bullets = [b for b in self.aliens_bullets if not b.is_offscreen()]
        for bullet in self.aliens_bullets:
            bullet.update()

        # 外星人移动
        self.move_aliens()

        # 敌人射击（随机）
        alive_aliens = [a for a in self.aliens if a.alive]
        for alien in alive_aliens:
            if random.random() < ALIEN_SHOOT_RATE:
                bullet = Bullet(alien.rect.centerx - BULLET_WIDTH // 2, alien.rect.bottom, 1)
                self.aliens_bullets.append(bullet)

        # 检测碰撞
        self.check_collisions()

        # 检查胜利条件
        if not any(a.alive for a in self.aliens):
            self.game_over = True
            self.won = True

        # 检查失败条件：敌人到达玩家高度
        for alien in self.aliens:
            if alien.alive and alien.rect.bottom >= PLAYER_Y + PLAYER_HEIGHT:
                self.game_over = True
                self.won = False

        # 玩家生命值归零
        if self.player.lives <= 0:
            self.game_over = True
            self.won = False

    def move_aliens(self):
        alive_aliens = [a for a in self.aliens if a.alive]
        if not alive_aliens:
            return

        move_right = self.alien_direction > 0
        # 计算边界
        if move_right:
            rightmost = max(a.rect.right for a in alive_aliens)
            if rightmost + ALIEN_MOVE_SPEED > SCREEN_WIDTH - 10:
                self.alien_direction = -1
                for alien in self.aliens:
                    if alien.alive:
                        alien.rect.y += ALIEN_DROP_DISTANCE
        else:
            leftmost = min(a.rect.left for a in alive_aliens)
            if leftmost - ALIEN_MOVE_SPEED < 10:
                self.alien_direction = 1
                for alien in self.aliens:
                    if alien.alive:
                        alien.rect.y += ALIEN_DROP_DISTANCE

        # 整体移动
        for alien in self.aliens:
            if alien.alive:
                alien.rect.x += ALIEN_MOVE_SPEED * self.alien_direction

    def check_collisions(self):
        # 玩家子弹击中敌人
        for bullet in self.player.bullets:
            for alien in self.aliens:
                if alien.alive and bullet.rect.colliderect(alien.rect):
                    alien.alive = False
                    bullet.rect.y = -100  # marked for removal
                    self.score += SCORE_PER_KILL
                    break

        # 敌人子弹击中玩家
        for bullet in self.aliens_bullets:
            if bullet.rect.colliderect(self.player.rect):
                bullet.rect.y = SCREEN_HEIGHT + 100  # marked for removal
                self.player.lives -= 1

        # 移除已击中的玩家子弹（标记的）
        self.player.bullets = [b for b in self.player.bullets if b.rect.y > -50]

    def draw(self):
        self.screen.fill(BG_COLOR)

        # 绘制玩家
        pygame.draw.rect(self.screen, PLAYER_COLOR, self.player.rect)

        # 绘制敌人
        for alien in self.aliens:
            if alien.alive:
                pygame.draw.rect(self.screen, ALIEN_COLOR, alien.rect)

        # 绘制玩家子弹
        for bullet in self.player.bullets:
            pygame.draw.rect(self.screen, BULLET_COLOR, bullet.rect)

        # 绘制敌人子弹
        for bullet in self.aliens_bullets:
            pygame.draw.rect(self.screen, BULLET_COLOR, bullet.rect)

        # HUD
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))

        if self.game_over:
            if self.won:
                msg = "You Win!"
            else:
                msg = "Game Over"
            game_over_text = self.font.render(msg, True, TEXT_COLOR)
            restart_text = self.font.render("Press R to Restart", True, TEXT_COLOR)
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()

    def run(self):
        while self.is_running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()