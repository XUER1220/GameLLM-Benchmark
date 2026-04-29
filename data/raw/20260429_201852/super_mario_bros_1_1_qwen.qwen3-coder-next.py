import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
LEVEL_WIDTH = 3200
LEVEL_HEIGHT = 600
FPS = 60

# Colors
SKY_COLOR = (135, 206, 235)
PLAYER_COLOR = (220, 60, 60)
GROUND_COLOR = (101, 67, 33)
BRICK_COLOR = (179, 101, 67)
QUESTION_BLOCK_COLOR = (255, 215, 0)
PIPE_COLOR = (50, 205, 50)
PIPE_TOP_COLOR = (34, 139, 34)
ENEMY_COLOR = (139, 69, 19)
COIN_COLOR = (255, 215, 0)
FLAG_POLE_COLOR = (34, 139, 34)
FLAG_TOP_COLOR = (255, 255, 255)
HUD_COLOR = (0, 0, 0)

# Physics
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 48
PLAYER_SPEED_X = 5
PLAYER_JUMP_FORCE = -12
GRAVITY = 0.5
ENEMY_SPEED = 2
ENEMY_WIDTH = 32
ENEMY_HEIGHT = 32
COIN_WIDTH = 18
COIN_HEIGHT = 18

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
VICTORY = 3

# Game parameters
MAX_LIVES = 3
SCORE_PER_COIN = 100
SCORE_PER_ENEMY = 200

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_x = 0
        self.vel_y = 0
        self.lives = MAX_LIVES
        self.score = 0
        self.coins = 0
        self.is_dead = False
        self.is_on_ground = False
        self.spawn_x = x
        self.spawn_y = y

    def update(self, platforms):
        # Apply gravity
        if not self.is_on_ground:
            self.vel_y += GRAVITY

        # Horizontal movement
        if not self.is_dead:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.vel_x = -PLAYER_SPEED_X
            elif keys[pygame.K_RIGHT]:
                self.vel_x = PLAYER_SPEED_X
            else:
                self.vel_x = 0

            # Jumping
            if keys[pygame.K_SPACE] and self.is_on_ground:
                self.vel_y = PLAYER_JUMP_FORCE

        # Update position
        self.rect.x += self.vel_x
        self.check_platform_collisions_x(platforms)

        self.rect.y += self.vel_y
        self.is_on_ground = False
        self.check_platform_collisions_y(platforms)

        # Check if fell off the world
        if self.rect.y > LEVEL_HEIGHT + 100:
            self.die()

    def check_platform_collisions_x(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right
                self.vel_x = 0

    def check_platform_collisions_y(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:  # Falling down
                    self.rect.bottom = platform.rect.top
                    self.is_on_ground = True
                    self.vel_y = 0
                elif self.vel_y < 0:  # Jumping up
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

    def die(self):
        if not self.is_dead:
            self.lives -= 1
            self.is_dead = True
            self.rect.x = self.spawn_x
            self.rect.y = self.spawn_y
            self.vel_x = 0
            self.vel_y = 0

    def draw(self, screen, camera_x):
        player_rect = self.rect.move(-camera_x, 0)
        pygame.draw.rect(screen, PLAYER_COLOR, player_rect)
        # Simple face for direction indication
        eyes_color = (255, 255, 255)
        if self.vel_x > 0 or (self.vel_x == 0 and self.is_on_ground):
            pygame.draw.rect(screen, eyes_color, (player_rect.x + 20, player_rect.y + 10, 4, 4))
        else:
            pygame.draw.rect(screen, eyes_color, (player_rect.x + 8, player_rect.y + 10, 4, 4))

class Platform:
    def __init__(self, x, y, width, height, type="brick"):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = type  # "ground", "brick", "question", "pipe"
        self.used = False

    def draw(self, screen, camera_x):
        rect = self.rect.move(-camera_x, 0)
        if rect.right < 0 or rect.left > WINDOW_WIDTH:
            return

        if self.type == "ground":
            pygame.draw.rect(screen, GROUND_COLOR, rect)
            # Add some texture
            pygame.draw.rect(screen, (76, 51, 25), (rect.x, rect.y + 10, rect.width, 2))
        elif self.type == "brick":
            pygame.draw.rect(screen, BRICK_COLOR, rect)
            # Bricks pattern
            pygame.draw.rect(screen, (150, 80, 50), (rect.x + 5, rect.y + 5, rect.width - 10, 2))
            pygame.draw.rect(screen, (150, 80, 50), (rect.x + 5, rect.y + rect.height - 7, rect.width - 10, 2))
            pygame.draw.rect(screen, (150, 80, 50), (rect.x + 5, rect.y + rect.height // 2, rect.width - 10, 2))
            pygame.draw.rect(screen, (150, 80, 50), (rect.x + rect.width // 2 - 1, rect.y + 2, 2, rect.height - 4))
        elif self.type == "question":
            color = QUESTION_BLOCK_COLOR if not self.used else (128, 128, 128)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (218, 165, 32), rect.inflate(-4, -4))
            if not self.used:
                font = pygame.font.SysFont(None, 24)
                text = font.render("?", True, (218, 165, 32))
                screen.blit(text, (rect.x + rect.width // 2 - text.get_width() // 2,
                                   rect.y + rect.height // 2 - text.get_height() // 2))
        elif self.type == "pipe":
            # Main pipe
            pygame.draw.rect(screen, PIPE_COLOR, rect)
            # Pipe top
            if self.height > 32:
                top_rect = pygame.Rect(self.rect.x - 4, self.rect.y, self.rect.width + 8, 32)
                pygame.draw.rect(screen, PIPE_TOP_COLOR, top_rect)
            # Pipe details
            pygame.draw.rect(screen, (30, 144, 20), (rect.x + 5, rect.y, 2, rect.height))
            pygame.draw.rect(screen, (34, 139, 34), (rect.x + rect.width - 7, rect.y, 2, rect.height))

class Enemy:
    def __init__(self, x, y, platforms):
        self.rect = pygame.Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT)
        self.vel_x = ENEMY_SPEED
        self.vel_y = 0
        self.platforms = platforms
        self.is_dead = False

    def update(self):
        if self.is_dead:
            return

        # Move horizontally
        self.rect.x += self.vel_x

        # Simple floor collision
        self.rect.y += 1
        on_ground = False
        for platform in self.platforms:
            if self.rect.colliderect(platform.rect):
                if platform.type == "ground" or platform.type == "brick" or platform.type == "pipe":
                    self.rect.bottom = platform.rect.top
                    on_ground = True
                    break
        if not on_ground:
            self.rect.y -= 1

        # Turn around at boundaries or when hitting walls
        hit_wall = False
        test_rect = self.rect.copy()
        test_rect.x += self.vel_x
        for platform in self.platforms:
            if test_rect.colliderect(platform.rect):
                hit_wall = True
                break
                
        if hit_wall or self.rect.x < 0 or self.rect.x > LEVEL_WIDTH - ENEMY_WIDTH:
            self.vel_x = -self.vel_x

    def draw(self, screen, camera_x):
        if self.is_dead:
            return
        
        enemy_rect = self.rect.move(-camera_x, 0)
        if enemy_rect.right < 0 or enemy_rect.left > WINDOW_WIDTH:
            return
            
        pygame.draw.rect(screen, ENEMY_COLOR, enemy_rect)
        # Eyes
        pygame.draw.rect(screen, (255, 255, 255), (enemy_rect.x + 6, enemy_rect.y + 8, 6, 6))
        pygame.draw.rect(screen, (255, 255, 255), (enemy_rect.x + 20, enemy_rect.y + 8, 6, 6))
        pygame.draw.rect(screen, (0, 0, 0), (enemy_rect.x + 8, enemy_rect.y + 10, 2, 2))
        pygame.draw.rect(screen, (0, 0, 0), (enemy_rect.x + 22, enemy_rect.y + 10, 2, 2))
        # Arms/antenna
        pygame.draw.rect(screen, ENEMY_COLOR, (enemy_rect.x + 12, enemy_rect.y - 4, 8, 4))
        pygame.draw.rect(screen, ENEMY_COLOR, (enemy_rect.x + 2, enemy_rect.y + 18, 28, 2))

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, COIN_WIDTH, COIN_HEIGHT)
        self.collected = False
        self.bounce_offset = 0
        self.bounce_direction = 1

    def update(self):
        if not self.collected:
            self.bounce_offset += 2 * self.bounce_direction
            if abs(self.bounce_offset) > 5:
                self.bounce_direction = -self.bounce_direction

    def draw(self, screen, camera_x):
        if self.collected:
            return
            
        coin_rect = pygame.Rect(self.rect.x - camera_x, self.rect.y + self.bounce_offset, 
                                self.rect.width, self.rect.height)
        if coin_rect.right < 0 or coin_rect.left > WINDOW_WIDTH:
            return

        pygame.draw.ellipse(screen, COIN_COLOR, coin_rect)
        pygame.draw.ellipse(screen, (218, 165, 32), coin_rect, 1)

class Flag:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.height = 300
        self.reached = False

    def draw(self, screen, camera_x):
        pole_x = self.x - camera_x
        if pole_x < -50 or pole_x > WINDOW_WIDTH:
            return

        # Flag pole
        pygame.draw.rect(screen, FLAG_POLE_COLOR, (pole_x, self.y, 5, self.height))
        
        # Flag top
        pygame.draw.circle(screen, FLAG_TOP_COLOR, (pole_x, self.y), 8)

        # Flag cloth
        if not self.reached:
            pygame.draw.polygon(screen, (255, 0, 0), [
                (pole_x + 5, self.y),
                (pole_x + 50, self.y + 20),
                (pole_x + 5, self.y + 40)
            ])
        else:
            pygame.draw.polygon(screen, (0, 0, 255), [
                (pole_x + 5, self.y),
                (pole_x + 50, self.y + 20),
                (pole_x + 5, self.y + 40)
            ])

def create_level():
    platforms = []
    enemies = []
    coins = []

    # Base ground
    i = 0
    while i < LEVEL_WIDTH:
        # Place gaps at specific locations: 600-700 and 1600-1700
        if i in range(600, 700) or i in range(1600, 1700):
            i += 100
            continue
        platforms.append(Platform(i, LEVEL_HEIGHT - 32, 100, 32, "ground"))
        i += 100

    # Platforms and bricks
    # Starting platform blocks
    platforms.extend([
        Platform(500, 350, 32, 32, "brick"),
        Platform(532, 350, 32, 32, "question"),
        Platform(564, 350, 32, 32, "brick"),
        Platform(596, 350, 32, 32, "question"),
        Platform(628, 350, 32, 32, "brick"),
        Platform(564, 180, 32, 32, "question"),
        Platform(250, 350, 32, 32, "brick"),
        Platform(282, 350, 32, 32, "brick"),
        Platform(314, 350, 32, 32, "question"),
        Platform(346, 350, 32, 32, "brick"),
        Platform(378, 350, 32, 32, "brick"),
        Platform(900, 350, 64, 64, "pipe"),
        Platform(1150, 400, 96, 32, "brick"),
        Platform(1182, 400, 32, 32, "question"),
        Platform(1214, 400, 64, 64, "pipe"),
        Platform(1500, 350, 64, 32, "brick"),
        Platform(1532, 350, 32, 32, "question"),
        Platform(1564, 350, 32, 32, "brick"),
        Platform(1596, 350, 32, 32, "question"),
        Platform(1628, 350, 32, 32, "brick"),
    ])

    # Coins
    coin_positions = [
        (532, 290), (596, 290), (564, 140),  # Above bricks
        (250, 290), (282, 290), (314, 290), (346, 290), (378, 290),  # Second platform
        (700, 320), (800, 320),  # Before the first pit
        (950, 250),  # On top of first pipe
        (1200, 350), (1500, 290), (1532, 290), (1564, 290), (1596, 290), (1628, 290),  # Later section
    ]
    for x, y in coin_positions:
        coins.append(Coin(x, y))

    # Enemies
    enemy_positions = [
        (700, LEVEL_HEIGHT - 32 - 32),
        (1200, LEVEL_HEIGHT - 32 - 32),
        (1800, LEVEL_HEIGHT - 32 - 32),
    ]
    for x, y in enemy_positions:
        enemies.append(Enemy(x, y, platforms))

    # Flag pole
    flag = Flag(3000, LEVEL_HEIGHT - 32 - 300)
    platforms.append(Platform(2950, LEVEL_HEIGHT - 32, 32, 32, "brick"))
    platforms.append(Platform(2982, LEVEL_HEIGHT - 32, 32, 32, "brick"))
    platforms.append(Platform(3014, LEVEL_HEIGHT - 32, 32, 32, "brick"))

    return platforms, enemies, coins, flag

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Super Mario Bros 1-1 Style")
    clock = pygame.time.Clock()
    
    random.seed(42)

    # Game state
    game_state = MENU
    camera_x = 0

    player = Player(100, LEVEL_HEIGHT - 100)
    platforms, enemies, coins, flag = create_level()
    original_platforms = platforms.copy()
    original_enemies = enemies.copy()
    original_coins = coins.copy()

    # HUD font
    font = pygame.font.SysFont(None, 30)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    if game_state in [GAME_OVER, VICTORY]:
                        # Reset game
                        player = Player(100, LEVEL_HEIGHT - 100)
                        platforms = [Platform(p.rect.x, p.rect.y, p.rect.width, p.rect.height, p.type) for p in original_platforms]
                        enemies = [Enemy(e.rect.x, e.rect.y, platforms) for e in original_enemies]
                        coins = [Coin(c.rect.x, c.rect.y) for c in original_coins]
                        flag.reached = False
                        game_state = PLAYING
                elif event.key == pygame.K_SPACE:
                    if game_state == MENU:
                        game_state = PLAYING

        keys = pygame.key.get_pressed()

        if game_state == MENU:
            screen.fill(SKY_COLOR)
            large_font = pygame.font.SysFont(None, 60)
            title1 = large_font.render("Super Mario", True, (255, 255, 255))
            title2 = large_font.render("1-1 Style Game", True, (255, 255, 255))
            start_txt = font.render("Press SPACE to Start", True, (255, 255, 255))
            quit_txt = font.render("Press ESC to Quit", True, (255, 255, 255))
            
            screen.blit(title1, (WINDOW_WIDTH//2 - title1.get_width()//2, 200))
            screen.blit(title2, (WINDOW_WIDTH//2 - title2.get_width()//2, 270))
            screen.blit(start_txt, (WINDOW_WIDTH//2 - start_txt.get_width()//2, 350))
            screen.blit(quit_txt, (WINDOW_WIDTH//2 - quit_txt.get_width()//2, 390))
            pygame.display.flip()
            clock.tick(FPS)
            continue

        elif game_state == PLAYING:
            # Update game objects
            player.update(platforms)
            
            # Camera logic
            camera_x = max(0, min(player.rect.x - WINDOW_WIDTH // 2, LEVEL_WIDTH - WINDOW_WIDTH))
            
            # Enemy updates
            for enemy in enemies:
                enemy.update()

            # Coin updates
            for coin in coins:
                coin.update()

            # Check player-enemy collisions
            for enemy in enemies:
                if not enemy.is_dead and player.rect.colliderect(enemy.rect):
                    # Check if player jumped on top of enemy
                    if player.vel_y > 0 and player.rect.bottom <= enemy.rect.top + 10:
                        enemy.is_dead = True
                        player.score += SCORE_PER_ENEMY
                        player.vel_y = -8  # Bounce up
                    else:
                        if not player.is_dead:
                            player.die()

            # Check player-coin collisions
            for coin in coins:
                if not coin.collected and player.rect.colliderect(coin.rect):
                    coin.collected = True
                    player.score += SCORE_PER_COIN
                    player.coins += 1

            # Check player-flags intersection
            if (player.rect.right >= flag.x + 5 and 
                player.rect.left <= flag.x + 10 and 
                player.rect.bottom >= flag.y and 
                player.rect.top <= flag.y + flag.height and
                not flag.reached):
                flag.reached = True
                player.score += 1000
                game_state = VICTORY

            # Check death condition
            if player.lives <= 0:
                game_state = GAME_OVER

            # Draw everything
            screen.fill(SKY_COLOR)
            
            # Draw platforms
            for platform in platforms:
                platform.draw(screen, camera_x)

            # Draw enemies
            for enemy in enemies:
                enemy.draw(screen, camera_x)

            # Draw coins
            for coin in coins:
                coin.draw(screen, camera_x)

            # Draw flag
            flag.draw(screen, camera_x)

            # Draw player
            player.draw(screen, camera_x)

            # Draw HUD
            hud_surface = font.render(f"Score: {player.score}", True, HUD_COLOR)
            screen.blit(hud_surface, (10, 10))
            
            coins_surface = font.render(f"Coins: {player.coins}", True, HUD_COLOR)
            screen.blit(coins_surface, (150, 10))
            
            lives_surface = font.render(f"Lives: {player.lives}", True, HUD_COLOR)
            screen.blit(lives_surface, (280, 10))

            pygame.display.flip()
            clock.tick(FPS)

        elif game_state == GAME_OVER:
            screen.fill((0, 0, 0))
            large_font = pygame.font.SysFont(None, 60)
            title1 = large_font.render("GAME OVER", True, (255, 0, 0))
            score_txt = font.render(f"Final Score: {player.score}", True, (255, 255, 255))
            restart_txt = font.render("Press R to Restart", True, (255, 255, 255))
            
            screen.blit(title1, (WINDOW_WIDTH//2 - title1.get_width()//2, 200))
            screen.blit(score_txt, (WINDOW_WIDTH//2 - score_txt.get_width()//2, 300))
            screen.blit(restart_txt, (WINDOW_WIDTH//2 - restart_txt.get_width()//2, 350))
            pygame.display.flip()
            clock.tick(FPS)

        elif game_state == VICTORY:
            screen.fill((0, 0, 0))
            large_font = pygame.font.SysFont(None, 60)
            title1 = large_font.render("YOU WIN!", True, (0, 255, 0))
            score_txt = font.render(f"Final Score: {player.score}", True, (255, 255, 255))
            restart_txt = font.render("Press R to Restart", True, (255, 255, 255))
            
            screen.blit(title1, (WINDOW_WIDTH//2 - title1.get_width()//2, 200))
            screen.blit(score_txt, (WINDOW_WIDTH//2 - score_txt.get_width()//2, 300))
            screen.blit(restart_txt, (WINDOW_WIDTH//2 - restart_txt.get_width()//2, 350))
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    main()