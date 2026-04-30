import pygame
import random
import sys

# 音效初始化
pygame.init()
pygame.mixer.init()

# 固定参数
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_WIDTH, PLAYER_HEIGHT = 60, 32
PLAYER_Y = HEIGHT - 40 - PLAYER_HEIGHT
PLAYER_SPEED = 6
PLAYER_LIVES = 3
BULLET_WIDTH, BULLET_HEIGHT = 6, 16
BULLET_SPEED = 8
ALIEN_ROWS, ALIEN_COLS = 4, 8
ALIEN_WIDTH, ALIEN_HEIGHT = 40, 30
ALIEN_DX = 1.2
ALIEN_DROP = 20
ALIEN_BULLET_SPEED = 5
ALIEN_BULLET_CHANCE = 0.01  # 每帧发射子弹概率，较低频率
SCORE_PER_KILL = 10

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# 初始化
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders Medium")
clock = pygame.time.Clock()
random.seed(42)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - PLAYER_WIDTH // 2, PLAYER_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.lives = PLAYER_LIVES
        self.bullets = []

    def move_left(self):
        self.rect.x -= PLAYER_SPEED
        if self.rect.x < 0:
            self.rect.x = 0

    def move_right(self):
        self.rect.x += PLAYER_SPEED
        if self.rect.x > WIDTH - PLAYER_WIDTH:
            self.rect.x = WIDTH - PLAYER_WIDTH

    def shoot(self):
        bullet = pygame.Rect(self.rect.centerx - BULLET_WIDTH // 2, self.rect.top, BULLET_WIDTH, BULLET_HEIGHT)
        self.bullets.append(bullet)

class Alien:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, ALIEN_WIDTH, ALIEN_HEIGHT)
        self.bullets = []

class Game:
    def __init__(self):
        self.player = Player()
        self.alien_bullets = []
        self.score = 0
        self.game_state = "PLAYING"  # "PLAYING", "GAME_OVER", "VICTORY"
        self.alien_direction = 1
        self.alien_x_velocity = ALIEN_DX
        self.alien_y_velocity = 0
        self.aliens = []
        self.create_aliens()
    
    def create_aliens(self):
        self.aliens = []
        alien_spacing_x = ALIEN_WIDTH + 10
        alien_spacing_y = ALIEN_HEIGHT + 20
        start_x = (WIDTH - (ALIEN_COLS * alien_spacing_x)) // 2 + ALIEN_WIDTH // 2
        start_y = 50
        
        for row in range(ALIEN_ROWS):
            for col in range(ALIEN_COLS):
                x = start_x + col * alien_spacing_x
                y = start_y + row * alien_spacing_y
                self.aliens.append(Alien(x, y))

    def update(self):
        if self.game_state != "PLAYING":
            return
        
        # 玩家子弹更新
        self.player.bullets = [b for b in self.player.bullets if b.bottom > 0]
        self.player.bullets = [b.move(0, -BULLET_SPEED) for b in self.player.bullets]
        
        # 敌人子弹更新
        self.alien_bullets = [b for b in self.alien_bullets if b.top < HEIGHT]
        self.alien_bullets = [b.move(0, ALIEN_BULLET_SPEED) for b in self.alien_bullets]
        
        # 外星人移动
        if self.aliens:
            right_edge = max(alien.rect.right for alien in self.aliens)
            left_edge = min(alien.rect.left for alien in self.aliens)
            
            if self.alien_direction == 1:
                if right_edge + self.alien_x_velocity >= WIDTH:
                    self.alien_direction = -1
                    for alien in self.aliens:
                        alien.rect.y += ALIEN_DROP
                else:
                    for alien in self.aliens:
                        alien.rect.x += self.alien_x_velocity
            else:
                if left_edge - self.alien_x_velocity <= 0:
                    self.alien_direction = 1
                    for alien in self.aliens:
                        alien.rect.y += ALIEN_DROP
                else:
                    for alien in self.aliens:
                        alien.rect.x -= self.alien_x_velocity
        
        # 敌人随机射击
        if self.aliens and random.random() < ALIEN_BULLET_CHANCE:
            shooter = random.choice(self.aliens)
            bullet = pygame.Rect(shooter.rect.centerx - BULLET_WIDTH // 2, shooter.rect.bottom, BULLET_WIDTH, BULLET_HEIGHT)
            self.alien_bullets.append(bullet)
        
        # 检查外星人是否到达玩家高度
        for alien in self.aliens:
            if alien.rect.bottom >= self.player.rect.top:
                self.game_state = "GAME_OVER"
                return
        
        # 碰撞检测：玩家子弹击中敌人
        new_aliens = []
        for alien in self.aliens:
            hit = False
            for bullet in self.player.bullets:
                if alien.rect.colliderect(bullet):
                    self.score += SCORE_PER_KILL
                    hit = True
                    try:
                        self.player.bullets.remove(bullet)
                    except ValueError:
                        pass
                    break
            if not hit:
                new_aliens.append(alien)
        self.aliens = new_aliens
        
        # 胜利条件
        if not self.aliens:
            self.game_state = "VICTORY"
            return
        
        # 碰撞检测：敌人子弹击中玩家
        player_hit = False
        new_bullets = []
        for bullet in self.alien_bullets:
            if self.player.rect.colliderect(bullet):
                player_hit = True
                self.player.lives -= 1
            else:
                new_bullets.append(bullet)
        self.alien_bullets = new_bullets
        
        if self.player.lives <= 0:
            self.game_state = "GAME_OVER"
    
    def draw(self, screen):
        screen.fill(BLACK)
        
        # 绘制玩家
        if self.game_state != "GAME_OVER" or (self.game_state == "GAME_OVER" and (pygame.time.get_ticks() // 200) % 2 == 0):
            pygame.draw.rect(screen, GREEN, self.player.rect)
            # 简单的飞船形状细节
            pygame.draw.rect(screen, (0, 150, 0), self.player.rect.inflate(-10, -10))
        
        # 绘制敌人
        for alien in self.aliens:
            pygame.draw.rect(screen, RED, alien.rect)
            # 简单的敌人细节
            pygame.draw.rect(screen, (180, 0, 0), alien.rect.inflate(-8, -8))
        
        # 绘制玩家子弹
        for bullet in self.player.bullets:
            pygame.draw.rect(screen, BLUE, bullet)
        
        # 绘制敌人子弹
        for bullet in self.alien_bullets:
            pygame.draw.rect(screen, YELLOW, bullet)
        
        # HUD
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        lives_text = font.render(f"Lives: {self.player.lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        
        # 游戏状态提示
        if self.game_state == "GAME_OVER":
            over_font = pygame.font.Font(None, 72)
            text = over_font.render("GAME OVER", True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render("Press R to Restart", True, WHITE)
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))
        elif self.game_state == "VICTORY":
            win_font = pygame.font.Font(None, 72)
            text = win_font.render("YOU WIN!", True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render("Press R to Restart", True, WHITE)
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))
        
        pygame.display.flip()

# 主程序
def main():
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game.game_state != "PLAYING":
                    game = Game()
        
        keys = pygame.key.get_pressed()
        
        if game.game_state == "PLAYING":
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                game.player.move_left()
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                game.player.move_right()
            if keys[pygame.K_SPACE]:
                if not game.player.bullets or game.player.bullets[-1].bottom < game.player.rect.top:
                    game.player.shoot()
        
        game.update()
        game.draw(screen)
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()