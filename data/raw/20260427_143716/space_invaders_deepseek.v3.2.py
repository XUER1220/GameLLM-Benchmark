import pygame
import random
import sys

pygame.init()

# 固定常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 32
PLAYER_SPEED = 6
BULLET_WIDTH = 6
BULLET_HEIGHT = 16
BULLET_SPEED = 8
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 30
ENEMY_ROWS = 4
ENEMY_COLS = 8
ENEMY_SPEED = 1.2
ENEMY_DROP = 20
PLAYER_LIVES = 3
ENEMY_BULLET_CHANCE = 0.005  # 每帧每个敌人发射子弹的概率
random.seed(42)

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 50, 50)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 200)
GRAY = (150, 150, 150)

class Player:
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - PLAYER_HEIGHT - 40
        self.speed = PLAYER_SPEED
        self.lives = PLAYER_LIVES
        self.bullets = []
        self.cooldown = 0
        self.cooldown_time = 15
    
    def move(self, direction):
        if direction == "left":
            self.x -= self.speed
        elif direction == "right":
            self.x += self.speed
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
    
    def shoot(self):
        if self.cooldown == 0:
            self.bullets.append(Bullet(self.x + self.width // 2 - BULLET_WIDTH // 2, self.y))
            self.cooldown = self.cooldown_time
    
    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y < -BULLET_HEIGHT:
                self.bullets.remove(bullet)
    
    def draw(self, screen):
        pygame.draw.polygon(screen, GREEN, [
            (self.x + self.width//2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ])
        pygame.draw.rect(screen, GREEN, (self.x + self.width//4, self.y + self.height, self.width//2, 2))
        for bullet in self.bullets:
            bullet.draw(screen)

class Enemy:
    def __init__(self, x, y):
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.x = x
        self.y = y
        self.active = True
        self.bullets = []
    
    def draw(self, screen):
        if not self.active:
            return
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, WHITE, (self.x + 5, self.y + 5, self.width - 10, self.height - 10))
        pygame.draw.circle(screen, BLACK, (self.x + self.width//2, self.y + self.height//2), 4)
    
    def update(self):
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y > SCREEN_HEIGHT:
                self.bullets.remove(bullet)
    
    def try_shoot(self):
        if self.active and random.random() < ENEMY_BULLET_CHANCE:
            self.bullets.append(EnemyBullet(self.x + self.width // 2 - BULLET_WIDTH // 2, self.y + self.height))

class Bullet:
    def __init__(self, x, y):
        self.width = BULLET_WIDTH
        self.height = BULLET_HEIGHT
        self.x = x
        self.y = y
        self.speed = -BULLET_SPEED
    
    def update(self):
        self.y += self.speed
    
    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))

class EnemyBullet:
    def __init__(self, x, y):
        self.width = BULLET_WIDTH
        self.height = BULLET_HEIGHT
        self.x = x
        self.y = y
        self.speed = BULLET_SPEED
    
    def update(self):
        self.y += self.speed
    
    def draw(self, screen):
        pygame.draw.rect(screen, PURPLE, (self.x, self.y, self.width, self.height))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders Medium")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.reset_game()
    
    def reset_game(self):
        self.player = Player()
        self.enemies = []
        self.enemy_direction = 1
        self.score = 0
        self.game_over = False
        self.win = False
        self.init_enemies()
    
    def init_enemies(self):
        start_x = 120
        start_y = 80
        spacing_x = 60
        spacing_y = 50
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                self.enemies.append(Enemy(x, y))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    if self.game_over:
                        self.reset_game()
                if event.key == pygame.K_SPACE and not self.game_over:
                    self.player.shoot()
        
        if not self.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.move("left")
            if keys[pygame.K_RIGHT]:
                self.player.move("right")
    
    def update_enemies(self):
        move_down = False
        for enemy in self.enemies:
            if not enemy.active:
                continue
            enemy.x += ENEMY_SPEED * self.enemy_direction
            if enemy.x <= 0 or enemy.x + ENEMY_WIDTH >= SCREEN_WIDTH:
                move_down = True
        
        if move_down:
            self.enemy_direction *= -1
            for enemy in self.enemies:
                if enemy.active:
                    enemy.y += ENEMY_DROP
    
    def check_collisions(self):
        # 玩家子弹击中敌人
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies:
                if enemy.active and bullet.x < enemy.x + enemy.width and bullet.x + bullet.width > enemy.x and \
                   bullet.y < enemy.y + enemy.height and bullet.y + bullet.height > enemy.y:
                    enemy.active = False
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    self.score += 10
                    break
        
        # 敌人子弹击中玩家
        for enemy in self.enemies:
            for ebullet in enemy.bullets[:]:
                if ebullet.x < self.player.x + self.player.width and ebullet.x + ebullet.width > self.player.x and \
                   ebullet.y < self.player.y + self.player.height and ebullet.y + ebullet.height > self.player.y:
                    self.player.lives -= 1
                    enemy.bullets.remove(ebullet)
                    if self.player.lives <= 0:
                        self.game_over = True
                        self.win = False
                    break
        
        # 敌人到达底部
        for enemy in self.enemies:
            if enemy.active and enemy.y + enemy.height >= self.player.y:
                self.game_over = True
                self.win = False
                break
        
        # 检查是否胜利
        all_dead = True
        for enemy in self.enemies:
            if enemy.active:
                all_dead = False
                break
        if all_dead:
            self.game_over = True
            self.win = True
    
    def update(self):
        if self.game_over:
            return
        
        self.player.update()
        self.update_enemies()
        
        for enemy in self.enemies:
            enemy.try_shoot()
            enemy.update()
        
        self.check_collisions()
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # 绘制星星背景
        for i in range(100):
            x = (i * 13) % SCREEN_WIDTH
            y = (i * 7) % SCREEN_HEIGHT
            pygame.draw.circle(self.screen, GRAY, (x, y), 1)
        
        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # HUD
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))
        
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            result_text = "YOU WIN!" if self.win else "GAME OVER"
            color = GREEN if self.win else RED
            result_surf = self.font.render(result_text, True, color)
            restart_surf = self.font.render("Press R to Restart", True, WHITE)
            self.screen.blit(result_surf, (SCREEN_WIDTH//2 - result_surf.get_width()//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(restart_surf, (SCREEN_WIDTH//2 - restart_surf.get_width()//2, SCREEN_HEIGHT//2))
        
        pygame.display.flip()
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()