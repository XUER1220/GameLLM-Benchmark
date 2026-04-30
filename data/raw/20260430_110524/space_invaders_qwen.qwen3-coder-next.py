import pygame
import random
import sys

# 初始化Pygame
pygame.init()
pygame.font.init()

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 游戏参数
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 32
PLAYER_Y_POS = SCREEN_HEIGHT - 40
PLAYER_SPEED = 6
PLAYER_LIVES = 3
PLAYER_COLOR = (0, 255, 0)

BULLET_WIDTH = 6
BULLET_HEIGHT = 16
BULLET_SPEED = 8
BULLET_COLOR = (255, 255, 255)

ALIEN_ROWS = 4
ALIEN_COLS = 8
ALIEN_WIDTH = 40
ALIEN_HEIGHT = 30
ALIEN_X_GAP = 40
ALIEN_Y_GAP = 20
ALIEN_MOVE_SPEED = 1.2
ALIEN_DROP_DISTANCE = 20
ALIEN_COLOR = (255, 255, 0)

FIRE_PROBABILITY = 0.02  # 每帧每个敌人发射子弹的概率
FIRE_COOLDOWN = 60       # 敌人每次发射后至少等待的帧数（约为1秒）
SCORE_PER_ALIEN = 10

# 颜色定义
BACKGROUND_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = PLAYER_Y_POS
        self.lives = PLAYER_LIVES

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += PLAYER_SPEED

    def shoot(self):
        return Bullet(self.rect.centerx, self.rect.top, -BULLET_SPEED)

class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((ALIEN_WIDTH, ALIEN_HEIGHT))
        self.image.fill(ALIEN_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.last_fire_time = 0

    def can_fire(self, current_time):
        return current_time - self.last_fire_time >= FIRE_COOLDOWN and random.random() < FIRE_PROBABILITY

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
        self.image.fill(BULLET_COLOR)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Game:
    def __init__(self):
        random.seed(42)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)

        self.reset_game()
        self.running = True
        self.game_over = False
        self.game_result = ""

    def reset_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.score = 0

        self.player = Player()
        self.all_sprites.add(self.player)
        
        # 创建外星人阵列
        start_x = (SCREEN_WIDTH - (ALIEN_COLS * (ALIEN_WIDTH + ALIEN_X_GAP))) // 2
        start_y = 50

        for row in range(ALIEN_ROWS):
            for col in range(ALIEN_COLS):
                alien = Alien(start_x + col * (ALIEN_WIDTH + ALIEN_X_GAP), start_y + row * (ALIEN_HEIGHT + ALIEN_Y_GAP))
                self.aliens.add(alien)
                self.all_sprites.add(alien)

        self.alien_direction = 1  # 1: right, -1: left
        self.game_over = False
        self.game_result = ""

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_SPACE and not self.game_over:
                    bullet = self.player.shoot()
                    self.player_bullets.add(bullet)
                    self.all_sprites.add(bullet)

    def update(self):
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys)

        # 更新子弹组
        self.player_bullets.update()
        self.alien_bullets.update()

        # 检查子弹撞击外星人
        hits = pygame.sprite.spritecollideany(None, self.player_bullets)
        for bullet in self.player_bullets:
            hit_alien = pygame.sprite.spritecollideany(bullet, self.aliens)
            if hit_alien:
                bullet.kill()
                hit_alien.kill()
                self.score += SCORE_PER_ALIEN
                # 移除外星人后重新计算方向（避免空阵列异常）
                if len(self.aliens) == 0:
                    self.game_over = True
                    self.game_result = "WIN"

        # 敌人发射子弹
        current_time = pygame.time.get_ticks()
        for alien in self.aliens:
            if alien.can_fire(current_time):
                bullet = Bullet(alien.rect.centerx, alien.rect.bottom, BULLET_SPEED)
                self.alien_bullets.add(bullet)
                self.all_sprites.add(bullet)
                alien.last_fire_time = current_time

        # 敌人子弹击中玩家
        if pygame.sprite.spritecollide(self.player, self.alien_bullets, True):
            self.player.lives -= 1
            if self.player.lives <= 0:
                self.game_over = True
                self.game_result = "GAME OVER"

        # 移动外星人
        alien_move_right = True
        alien_move_left = True
        for alien in self.aliens:
            if alien.rect.right >= SCREEN_WIDTH - 10:
                alien_move_right = False
            if alien.rect.left <= 10:
                alien_move_left = False

        move_direction = self.alien_direction
        if not alien_move_right:
            move_direction = -1
            for alien in self.aliens:
                alien.rect.y += ALIEN_DROP_DISTANCE
            self.alien_direction = -1
        elif not alien_move_left:
            move_direction = 1
            for alien in self.aliens:
                alien.rect.y += ALIEN_DROP_DISTANCE
            self.alien_direction = 1
        else:
            for alien in self.aliens:
                alien.rect.x += ALIEN_MOVE_SPEED * self.alien_direction

        # 游戏结束条件：敌人到达玩家高度
        for alien in self.aliens:
            if alien.rect.bottom >= self.player.rect.top:
                self.game_over = True
                self.game_result = "GAME OVER"
                break

        # 更新所有精灵
        self.all_sprites.update()

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        # 绘制所有精灵
        self.all_sprites.draw(self.screen)

        # 绘制HUD信息
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            if self.game_result == "WIN":
                result_text = self.font.render("YOU WIN!", True, (0, 255, 0))
            else:
                result_text = self.font.render("GAME OVER", True, (255, 0, 0))
            
            restart_text = self.font.render("Press R to Restart", True, TEXT_COLOR)
            self.screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()