import pygame
import sys

# Initialization
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer Hard")
clock = pygame.time.Clock()

# Constants
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 56
PLAYER_SPEED = 5
PLAYER_JUMP_FORCE = -12
PLAYER_GRAVITY = 0.5
PLAYER_LIVES = 3
SCORE_PER_COIN = 10

# Colors
COLOR_PLAYER = (0, 200, 100)
COLOR_PLATFORM = (100, 100, 100)
COLOR_ENEMY = (255, 80, 80)
COLOR_COIN = (255, 255, 0)
COLOR_FLAG_POLE = (200, 200, 200)
COLOR_FLAG_FACE = (0, 200, 0)
COLOR_TEXT = (255, 255, 255)
COLOR_HUD = (255, 255, 255)
COLOR_BG = (30, 30, 50)

# Platform class
class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_PLATFORM, self.rect)

# Enemy class
class Enemy:
    def __init__(self, x, y, patrol_left, patrol_right, speed=2):
        self.rect = pygame.Rect(x, y, 36, 36)
        self.patrol_left = patrol_left
        self.patrol_right = patrol_right
        self.direction = 1
        self.speed = speed

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.left <= self.patrol_left or self.rect.right >= self.patrol_right:
            self.direction *= -1

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_ENEMY, self.rect)

# Coin class
class Coin:
    def __init__(self, x, y, width=20, height=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.collected = False

    def draw(self, surface):
        if not self.collected:
            pygame.draw.circle(surface, COLOR_COIN, 
                               (self.rect.centerx, self.rect.centery), self.rect.width // 2)

# Flag
class Flag:
    def __init__(self, x, y):
        self.pole_rect = pygame.Rect(x, y, 10, 50)
        self.flag_rect = pygame.Rect(x + 10, y, 40, 25)
        self.pole_rect.y += 25
        self.flag_rect.y += 25

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_FLAG_POLE, self.pole_rect)
        pygame.draw.polygon(surface, COLOR_FLAG_FACE, [
            (self.flag_rect.x, self.flag_rect.y),
            (self.flag_rect.x + self.flag_rect.width, self.flag_rect.y + self.flag_rect.height // 2),
            (self.flag_rect.x, self.flag_rect.y + self.flag_rect.height)
        ])

# Player class
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_y = 0
        self.lives = PLAYER_LIVES
        self.on_ground = False
        self.invulnerable = 0  # frames
        self.x = x
        self.y = y

    def update(self, platforms, enemies):
        if self.invulnerable > 0:
            self.invulnerable -= 1

        # Horizontal movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED

        # Jumping
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = PLAYER_JUMP_FORCE
            self.on_ground = False

        # Gravity
        self.vel_y += PLAYER_GRAVITY
        self.rect.y += self.vel_y

        # Collision with platforms
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Only collide from top
                if self.vel_y > 0 and self.rect.bottom <= platform.rect.top + 10:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True

        # Keep within horizontal bounds
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # Enemy collision
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect) and self.invulnerable <= 0:
                self.lives -= 1
                self.invulnerable = 60  # 1 second invulnerability at 60 FPS
                # Knockback
                self.vel_y = -8
                if self.rect.centerx < enemy.rect.centerx:
                    self.rect.x -= 40
                else:
                    self.rect.x += 40

        # Check if fell off screen
        if self.rect.top > SCREEN_HEIGHT:
            self.lives = 0

    def draw(self, surface):
        if self.invulnerable == 0 or (self.invulnerable // 5) % 2 == 0:
            pygame.draw.rect(surface, COLOR_PLAYER, self.rect)

def main():
    random.seed(42)
    running = True
    game_state = 'running'  # 'running', 'gameover', 'win'
    
    # Create platforms: ground + 5空中平台 = 6 total
    platforms = [
        Platform(0, 550, 800, 50),      # Ground
        Platform(100, 450, 200, 20),
        Platform(400, 400, 200, 20),
        Platform(250, 300, 200, 20),
        Platform(550, 250, 200, 20),
        Platform(350, 150, 150, 20)
    ]

    # Create coins (5 total)
    coins_data = [
        (200, 410),
        (500, 360),
        (350, 260),
        (650, 210),
        (400, 110)
    ]
    coins = [Coin(x, y) for x, y in coins_data]

    # Create enemies (3 total), on specific platforms
    enemies = [
        Enemy(420, 364, 400, 600),
        Enemy(270, 264, 250, 450),
        Enemy(570, 214, 550, 750)
    ]

    # Create flag
    flag = Flag(650, 95)

    # Create player at start platform
    player = Player(50, 494)

    score = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_state != 'running':
                    # Restart game
                    player = Player(50, 494)
                    score = 0
                    coins = [Coin(x, y) for x, y in coins_data]
                    enemies = [
                        Enemy(420, 364, 400, 600),
                        Enemy(270, 264, 250, 450),
                        Enemy(570, 214, 550, 750)
                    ]
                    game_state = 'running'

        if game_state == 'running':
            # Update entities
            for enemy in enemies:
                enemy.update()
            player.update(platforms, enemies)

            # Check win condition (touch flag)
            if player.rect.right >= flag.pole_rect.left and player.rect.top + player.rect.height >= flag.pole_rect.top and player.rect.top <= flag.pole_rect.bottom:
                game_state = 'win'

            # Check coin collection
            for coin in coins:
                if not coin.collected and player.rect.colliderect(coin.rect):
                    coin.collected = True
                    score += SCORE_PER_COIN

            # Check lose conditions
            if player.lives <= 0:
                game_state = 'gameover'

        # Draw everything
        screen.fill(COLOR_BG)

        # Platforms
        for platform in platforms:
            platform.draw(screen)

        # Coins
        for coin in coins:
            coin.draw(screen)

        # Enemies
        for enemy in enemies:
            enemy.draw(screen)

        # Flag
        flag.draw(screen)

        # Player
        player.draw(screen)

        # HUD
        font = pygame.font.SysFont(None, 36)
        lives_text = font.render(f"Lives: {player.lives}", True, COLOR_HUD)
        score_text = font.render(f"Score: {score}", True, COLOR_HUD)
        screen.blit(lives_text, (20, 20))
        screen.blit(score_text, (20, 60))

        # Overlay for game over or win
        if game_state in ('gameover', 'win'):
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            if game_state == 'gameover':
                end_text = "GAME OVER"
                end_color = (255, 50, 50)
            else:
                end_text = "YOU WIN!"
                end_color = (50, 255, 50)
            
            big_font = pygame.font.SysFont(None, 72)
            title_text = big_font.render(end_text, True, end_color)
            restart_text = font.render("Press R to Restart", True, COLOR_TEXT)
            
            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()