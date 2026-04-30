import pygame
import sys
import random

# Fixed seed for reproducibility
random.seed(42)

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Player settings
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 32
PLAYER_SPEED = 6
PLAYER_Y_OFFSET = 40
PLAYER_LIVES = 3

# Bullet settings
PLAYER_BULLET_WIDTH = 6
PLAYER_BULLET_HEIGHT = 16
PLAYER_BULLET_SPEED = 8

# Enemy settings
ENEMY_ROWS = 4
ENEMY_COLS = 8
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 30
ENEMY_SPEED = 1.2
ENEMY_DROP_DISTANCE = 20
ENEMY_BULLET_PROBABILITY = 0.002  # Per frame per enemy

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

class Player:
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = (WINDOW_WIDTH - self.width) // 2
        self.y = WINDOW_HEIGHT - PLAYER_Y_OFFSET - self.height
        self.lives = PLAYER_LIVES
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.bullets = []
        self.last_shot_time = 0
        self.shoot_delay = 300  # milliseconds

    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y
        # Update bullets
        for bullet in self.bullets[:]:
            bullet[1] -= PLAYER_BULLET_SPEED
            if bullet[1] + PLAYER_BULLET_HEIGHT < 0:
                self.bullets.remove(bullet)

    def move_left(self):
        self.x = max(0, self.x - PLAYER_SPEED)
        self.rect.x = self.x

    def move_right(self):
        self.x = min(WINDOW_WIDTH - self.width, self.x + PLAYER_SPEED)
        self.rect.x = self.x

    def shoot(self, current_time):
        if current_time - self.last_shot_time > self.shoot_delay:
            self.bullets.append([
                self.x + self.width // 2 - PLAYER_BULLET_WIDTH // 2,
                self.y,
                PLAYER_BULLET_WIDTH,
                PLAYER_BULLET_HEIGHT
            ])
            self.last_shot_time = current_time

class Enemy:
    def __init__(self, x, y):
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.bullets = []

    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y
        # Update enemy bullets
        for bullet in self.bullets[:]:
            bullet[1] += PLAYER_BULLET_SPEED * 0.6  # Slower than player bullets
            if bullet[1] > WINDOW_HEIGHT:
                self.bullets.remove(bullet)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 32)
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.enemies = []
        self.score = 0
        self.game_over = False
        self.win = False
        self.direction = 1  # 1 for right, -1 for left
        
        # Create enemy grid
        enemy_start_x = 50
        enemy_start_y = 50
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                x = enemy_start_x + col * (ENEMY_WIDTH + 10)
                y = enemy_start_y + row * (ENEMY_HEIGHT + 10)
                self.enemies.append(Enemy(x, y))

    def handle_events(self):
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
        
        # Handle player movement
        if not self.game_over:
            if keys[pygame.K_LEFT]:
                self.player.move_left()
            if keys[pygame.K_RIGHT]:
                self.player.move_right()
            if keys[pygame.K_SPACE]:
                current_time = pygame.time.get_ticks()
                self.player.shoot(current_time)
        
        return True

    def update_game(self):
        if self.game_over:
            return
        
        # Update player
        self.player.update()
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update()
        
        # Move enemies horizontally
        move_right = self.direction > 0
        move_down = False
        
        # Check boundaries
        if move_right:
            max_x = max(enemy.x + enemy.width for enemy in self.enemies)
            if max_x >= WINDOW_WIDTH - 10:
                move_down = True
        else:
            min_x = min(enemy.x for enemy in self.enemies)
            if min_x <= 10:
                move_down = True
        
        if move_down:
            self.direction *= -1
            for enemy in self.enemies:
                enemy.y += ENEMY_DROP_DISTANCE
                enemy.rect.y = enemy.y
        else:
            for enemy in self.enemies:
                enemy.x += ENEMY_SPEED * self.direction
                enemy.rect.x = enemy.x
        
        # Check if enemies reached player's level
        for enemy in self.enemies:
            if enemy.y + enemy.height >= self.player.y:
                self.game_over = True
                self.win = False
                break
        
        # Enemy shooting logic
        for enemy in self.enemies:
            if random.random() < ENEMY_BULLET_PROBABILITY:
                enemy.bullets.append([
                    enemy.x + enemy.width // 2 - PLAYER_BULLET_WIDTH // 2,
                    enemy.y + enemy.height,
                    PLAYER_BULLET_WIDTH,
                    PLAYER_BULLET_HEIGHT
                ])
        
        # Check collisions with player bullets
        for bullet in self.player.bullets[:]:
            bullet_rect = pygame.Rect(bullet[0], bullet[1], bullet[2], bullet[3])
            for enemy in self.enemies[:]:
                if bullet_rect.colliderect(enemy.rect):
                    self.player.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 10
                    break
        
        # Check collisions with enemy bullets
        for enemy in self.enemies:
            for bullet in enemy.bullets[:]:
                bullet_rect = pygame.Rect(bullet[0], bullet[1], bullet[2], bullet[3])
                if bullet_rect.colliderect(self.player.rect):
                    enemy.bullets.remove(bullet)
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.game_over = True
                        self.win = False
        
        # Check win condition
        if len(self.enemies) == 0:
            self.game_over = True
            self.win = True
        
        # Update player rect again in case it was changed in earlier updates
        self.player.rect.x = self.player.x
        self.player.rect.y = self.player.y

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw player
        pygame.draw.rect(self.screen, GREEN, self.player.rect)
        
        # Draw enemies
        for enemy in self.enemies:
            pygame.draw.rect(self.screen, BLUE, enemy.rect)
        
        # Draw bullets
        for bullet in self.player.bullets:
            pygame.draw.rect(self.screen, YELLOW, pygame.Rect(bullet[0], bullet[1], bullet[2], bullet[3]))
        
        for enemy in self.enemies:
            for bullet in enemy.bullets:
                pygame.draw.rect(self.screen, RED, pygame.Rect(bullet[0], bullet[1], bullet[2], bullet[3]))
        
        # Draw HUD
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        
        self.screen.blit(lives_text, (10, 10))
        self.screen.blit(score_text, (WINDOW_WIDTH - 150, 10))
        
        # Draw game over or win screen
        if self.game_over:
            screen_center_x = WINDOW_WIDTH // 2
            screen_center_y = WINDOW_HEIGHT // 2
            
            if self.win:
                result_text = self.font.render("YOU WIN!", True, GREEN)
            else:
                result_text = self.font.render("GAME OVER", True, RED)
            
            restart_text = self.font.render("Press R to Restart", True, WHITE)
            
            result_rect = result_text.get_rect(center=(screen_center_x, screen_center_y - 20))
            restart_rect = restart_text.get_rect(center=(screen_center_x, screen_center_y + 20))
            
            self.screen.blit(result_text, result_rect)
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update_game()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()