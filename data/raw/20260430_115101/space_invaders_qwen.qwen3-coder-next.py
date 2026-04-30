import pygame
import random
import sys

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

PLAYER_WIDTH = 60
PLAYER_HEIGHT = 32
PLAYER_Y_OFFSET = 40
PLAYER_SPEED = 6

BULLET_WIDTH = 6
BULLET_HEIGHT = 16
BULLET_SPEED = 8

ALIEN_ROWS = 4
ALIEN_COLS = 8
ALIEN_WIDTH = 40
ALIEN_HEIGHT = 30
ALIEN_MARGIN_X = 20
ALIEN_MARGIN_TOP = 50
ALIEN_MOVE_SPEED = 1.2
ALIEN_DROP_HEIGHT = 20

ALIEN_BULLET_SPEED = 4
ALIEN_FIRE_RATE = 0.005  # per frame

MAX_LIVES = 3
SCORE_PER_KILL = 10

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders Medium")
clock = pygame.time.Clock()

random.seed(42)

def draw_text_centered(text, x, y, color=(255, 255, 255), font_size=36):
    font = pygame.font.Font(None, font_size)
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)

def draw_text_left(text, x, y, color=(255, 255, 255), font_size=24):
    font = pygame.font.Font(None, font_size)
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))

class Player:
    def __init__(self):
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2,
            SCREEN_HEIGHT - PLAYER_Y_OFFSET - PLAYER_HEIGHT,
            PLAYER_WIDTH,
            PLAYER_HEIGHT
        )
        self.lives = MAX_LIVES
        self.bullets = []
        self.shoot_cooldown = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += PLAYER_SPEED
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def fire(self):
        if self.shoot_cooldown <= 0:
            bullet = pygame.Rect(
                self.rect.centerx - BULLET_WIDTH // 2,
                self.rect.top,
                BULLET_WIDTH,
                BULLET_HEIGHT
            )
            self.bullets.append(bullet)
            self.shoot_cooldown = 15  # frames between shots

    def draw(self):
        pygame.draw.rect(screen, (0, 255, 0), self.rect)

class Alien:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, ALIEN_WIDTH, ALIEN_HEIGHT)
        self.active = True
    
    def draw(self):
        if self.active:
            pygame.draw.rect(screen, (255, 255, 0), self.rect)

class AlienManager:
    def __init__(self):
        self.aliens = []
        self.direction = 1  # 1 for right, -1 for left
        self.move_counter = 0
        
        # Create the alien grid
        total_alien_width = ALIEN_COLS * ALIEN_WIDTH + (ALIEN_COLS - 1) * 10
        start_x = (SCREEN_WIDTH - total_alien_width) // 2
        
        for row in range(ALIEN_ROWS):
            for col in range(ALIEN_COLS):
                x = start_x + col * (ALIEN_WIDTH + 10)
                y = ALIEN_MARGIN_TOP + row * (ALIEN_HEIGHT + 15)
                self.aliens.append(Alien(x, y))
        
        self.active_aliens = len(self.aliens)

    def update(self):
        move_x = ALIEN_MOVE_SPEED * self.direction
        max_right = max(alien.rect.right for alien in self.aliens if alien.active)
        min_left = min(alien.rect.left for alien in self.aliens if alien.active)
        
        if max_right + move_x > SCREEN_WIDTH or min_left + move_x < 0:
            self.direction *= -1
            for alien in self.aliens:
                if alien.active:
                    alien.rect.y += ALIEN_DROP_HEIGHT
        else:
            for alien in self.aliens:
                if alien.active:
                    alien.rect.x += move_x
    
    def fire(self):
        # Find active aliens that can fire (only aliens in bottom rows per column)
        active_aliens = [a for a in self.aliens if a.active]
        if not active_aliens:
            return []
        
        # Group by column and get bottom-most alien in each column
        columns = {}
        for a in active_aliens:
            col_key = a.rect.x // (ALIEN_WIDTH + 10)
            if col_key not in columns or a.rect.bottom > columns[col_key].rect.bottom:
                columns[col_key] = a
        
        bottom_aliens = list(columns.values())
        
        bullets = []
        for alien in bottom_aliens:
            if random.random() < ALIEN_FIRE_RATE:
                bullet = pygame.Rect(
                    alien.rect.centerx - BULLET_WIDTH // 2,
                    alien.rect.bottom,
                    BULLET_WIDTH,
                    BULLET_HEIGHT
                )
                bullets.append(bullet)
        return bullets
    
    def check_game_over_height(self, player_y):
        for alien in self.aliens:
            if alien.active and alien.rect.bottom >= player_y:
                return True
        return False

    def draw(self):
        for alien in self.aliens:
            alien.draw()

class Game:
    def __init__(self):
        self.player = Player()
        self.aliens = AlienManager()
        self.player_bullets = []
        self.alien_bullets = []
        self.score = 0
        self.game_state = "playing"  # "playing", "won", "lost"
        self.font = pygame.font.Font(None, 36)

    def reset(self):
        self.player = Player()
        self.aliens = AlienManager()
        self.player_bullets = []
        self.alien_bullets = []
        self.score = 0
        self.game_state = "playing"

    def update(self):
        if self.game_state != "playing":
            return
        
        self.player.update()
        self.aliens.update()
        
        # Player shooting
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            self.player.fire()
        
        # Update player bullets
        for bullet in self.player_bullets[:]:
            bullet.y -= BULLET_SPEED
            if bullet.y < 0:
                self.player_bullets.remove(bullet)
        
        # Update alien bullets
        for bullet in self.alien_bullets[:]:
            bullet.y += ALIEN_BULLET_SPEED
            if bullet.y > SCREEN_HEIGHT:
                self.alien_bullets.remove(bullet)
        
        # Check player bullet hits
        for bullet in self.player_bullets[:]:
            for alien in self.aliens.aliens:
                if alien.active and bullet.colliderect(alien.rect):
                    alien.active = False
                    self.player_bullets.remove(bullet)
                    self.aliens.active_aliens -= 1
                    self.score += SCORE_PER_KILL
                    break
        
        # Check alien bullet hits
        for bullet in self.alien_bullets[:]:
            if bullet.colliderect(self.player.rect):
                self.player.lives -= 1
                self.alien_bullets.remove(bullet)
                if self.player.lives <= 0:
                    self.game_state = "lost"
        
        # Fire alien bullets
        alien_bullets = self.aliens.fire()
        self.alien_bullets.extend(alien_bullets)
        
        # Check win/lose conditions
        if self.aliens.active_aliens == 0:
            self.game_state = "won"
        elif self.aliens.check_game_over_height(self.player.rect.top + PLAYER_HEIGHT // 2):
            self.game_state = "lost"

    def draw(self):
        # Background
        screen.fill((0, 0, 0))
        
        # HUD
        draw_text_left(f"Score: {self.score}", 10, 10)
        draw_text_left(f"Lives: {self.player.lives}", 10, 40)
        
        # Draw game objects
        self.player.draw()
        self.aliens.draw()
        
        for bullet in self.player_bullets:
            pygame.draw.rect(screen, (255, 0, 0), bullet)
        
        for bullet in self.alien_bullets:
            pygame.draw.rect(screen, (255, 165, 0), bullet)
        
        # Game over messages
        if self.game_state == "won":
            draw_text_centered("YOU WIN!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, (0, 255, 0), 64)
            draw_text_centered(f"Final Score: {self.score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10, (255, 255, 255), 36)
            draw_text_centered("Press R to Restart", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, (0, 255, 255), 32)
        elif self.game_state == "lost":
            draw_text_centered("GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, (255, 0, 0), 64)
            draw_text_centered(f"Final Score: {self.score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10, (255, 255, 255), 36)
            draw_text_centered("Press R to Restart", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, (0, 255, 255), 32)
        
        pygame.display.flip()

def main():
    game = Game()
    running = True
    
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game.game_state != "playing":
                    game.reset()
        
        game.update()
        game.draw()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()