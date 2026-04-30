import pygame
import random

random.seed(42)

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WORLD_WIDTH = 3200
WORLD_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 50)
BROWN = (150, 80, 30)
GRAY = (100, 100, 100)
PURPLE = (180, 50, 230)
CYAN = (50, 200, 200)
ORANGE = (255, 150, 50)
DARK_GREEN = (30, 100, 30)

# Player
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 48
PLAYER_SPEED = 5
JUMP_VEL = -12
GRAVITY = 0.5

# Coin
COIN_SIZE = 18

# Enemy
ENEMY_SIZE = 32

# Fixed level layout
GROUND_HEIGHT = 50
GROUND_Y = WORLD_HEIGHT - GROUND_HEIGHT

# Tiles
TILE_SIZE = 40

def create_world():
    bricks = []
    question_blocks = []
    pipes = []
    coins = []
    enemies = []
    platforms = []
    pits = []
    flagpole = []

    # Ground
    ground_rect = pygame.Rect(0, GROUND_Y, WORLD_WIDTH, GROUND_HEIGHT)

    # Brick blocks (12 bricks)
    brick_positions = [
        (200, GROUND_Y - TILE_SIZE),
        (240, GROUND_Y - TILE_SIZE),
        (280, GROUND_Y - TILE_SIZE),
        (400, GROUND_Y - TILE_SIZE * 2),
        (440, GROUND_Y - TILE_SIZE * 2),
        (480, GROUND_Y - TILE_SIZE),
        (520, GROUND_Y - TILE_SIZE),
        (600, GROUND_Y - TILE_SIZE * 3),
        (640, GROUND_Y - TILE_SIZE * 3),
        (680, GROUND_Y - TILE_SIZE * 3),
        (800, GROUND_Y - TILE_SIZE * 2),
        (840, GROUND_Y - TILE_SIZE * 2),
    ]
    bricks = [pygame.Rect(x, y, TILE_SIZE, TILE_SIZE) for x, y in brick_positions]

    # Question blocks (12 blocks)
    question_positions = [
        (320, GROUND_Y - TILE_SIZE * 2),
        (360, GROUND_Y - TILE_SIZE * 2),
        (560, GROUND_Y - TILE_SIZE * 2),
        (720, GROUND_Y - TILE_SIZE * 4),
        (760, GROUND_Y - TILE_SIZE * 4),
        (900, GROUND_Y - TILE_SIZE * 2),
        (940, GROUND_Y - TILE_SIZE * 2),
        (1100, GROUND_Y - TILE_SIZE * 3),
        (1140, GROUND_Y - TILE_SIZE * 3),
        (1180, GROUND_Y - TILE_SIZE * 3),
        (1500, GROUND_Y - TILE_SIZE * 2),
        (1540, GROUND_Y - TILE_SIZE * 2),
    ]
    question_blocks = [pygame.Rect(x, y, TILE_SIZE, TILE_SIZE) for x, y in question_positions]

    # Pipes/platforms (4 obstacles)
    pipes.append(pygame.Rect(1000, GROUND_Y - TILE_SIZE * 2, TILE_SIZE * 2, TILE_SIZE * 2))
    pipes.append(pygame.Rect(1200, GROUND_Y - TILE_SIZE * 3, TILE_SIZE * 2, TILE_SIZE * 3))
    platforms.append(pygame.Rect(1800, GROUND_Y - TILE_SIZE * 2, TILE_SIZE * 4, TILE_SIZE))
    platforms.append(pygame.Rect(2200, GROUND_Y - TILE_SIZE * 3, TILE_SIZE * 3, TILE_SIZE))

    # Coins (12 coins)
    coin_positions = [
        (330, GROUND_Y - TILE_SIZE * 2 - 30),
        (370, GROUND_Y - TILE_SIZE * 2 - 30),
        (570, GROUND_Y - TILE_SIZE * 2 - 30),
        (730, GROUND_Y - TILE_SIZE * 4 - 30),
        (770, GROUND_Y - TILE_SIZE * 4 - 30),
        (910, GROUND_Y - TILE_SIZE * 2 - 30),
        (950, GROUND_Y - TILE_SIZE * 2 - 30),
        (1110, GROUND_Y - TILE_SIZE * 3 - 30),
        (1150, GROUND_Y - TILE_SIZE * 3 - 30),
        (1190, GROUND_Y - TILE_SIZE * 3 - 30),
        (1510, GROUND_Y - TILE_SIZE * 2 - 30),
        (1550, GROUND_Y - TILE_SIZE * 2 - 30),
    ]
    coins = [pygame.Rect(x, y, COIN_SIZE, COIN_SIZE) for x, y in coin_positions]

    # Enemies (3 enemies)
    enemies.append({
        "rect": pygame.Rect(500, GROUND_Y - ENEMY_SIZE, ENEMY_SIZE, ENEMY_SIZE),
        "vel": 2,
        "patrol_left": 450,
        "patrol_right": 750,
    })
    enemies.append({
        "rect": pygame.Rect(1300, GROUND_Y - ENEMY_SIZE, ENEMY_SIZE, ENEMY_SIZE),
        "vel": -2,
        "patrol_left": 1250,
        "patrol_right": 1450,
    })
    enemies.append({
        "rect": pygame.Rect(1900, GROUND_Y - ENEMY_SIZE - TILE_SIZE, ENEMY_SIZE, ENEMY_SIZE),
        "vel": 2,
        "patrol_left": 1850,
        "patrol_right": 2100,
    })

    # Pits (2 pits)
    pits.append(pygame.Rect(800, GROUND_Y, 200, GROUND_HEIGHT))
    pits.append(pygame.Rect(1600, GROUND_Y, 250, GROUND_HEIGHT))

    # Flagpole
    flagpole.append(pygame.Rect(WORLD_WIDTH - 100, GROUND_Y - TILE_SIZE * 5, 10, TILE_SIZE * 5))
    flagpole.append(pygame.Rect(WORLD_WIDTH - 100, GROUND_Y - TILE_SIZE * 5, 50, 30))

    return {
        "ground": ground_rect,
        "bricks": bricks,
        "question_blocks": question_blocks,
        "pipes": pipes,
        "platforms": platforms,
        "coins": coins,
        "enemies": enemies,
        "pits": pits,
        "flagpole": flagpole,
    }

class Player:
    def __init__(self):
        self.rect = pygame.Rect(50, GROUND_Y - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.lives = 3
        self.score = 0
        self.coins = 0
        self.won = False
        self.dead = False

    def update(self, world, keys):
        if self.dead or self.won:
            return

        # Horizontal movement
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED

        # Apply horizontal movement
        self.rect.x += self.vel_x
        # Keep player in world bounds
        self.rect.x = max(0, min(self.rect.x, WORLD_WIDTH - PLAYER_WIDTH))

        # Check collisions with solid objects horizontally
        solids = world["bricks"] + world["question_blocks"] + world["pipes"] + world["platforms"] + [world["ground"]]
        for obj in solids:
            if self.rect.colliderect(obj):
                if self.vel_x > 0:
                    self.rect.right = obj.left
                elif self.vel_x < 0:
                    self.rect.left = obj.right

        # Vertical movement (gravity)
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        self.on_ground = False

        # Ground collision
        if self.rect.colliderect(world["ground"]):
            if self.vel_y > 0:
                self.rect.bottom = world["ground"].top
                self.vel_y = 0
                self.on_ground = True

        # Brick and question block collision (vertical)
        for obj in world["bricks"] + world["question_blocks"] + world["pipes"] + world["platforms"]:
            if self.rect.colliderect(obj):
                if self.vel_y > 0:
                    self.rect.bottom = obj.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = obj.bottom
                    self.vel_y = 0

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = JUMP_VEL
            self.on_ground = False

        # Coin collection
        for coin in world["coins"][:]:
            if self.rect.colliderect(coin):
                world["coins"].remove(coin)
                self.score += 100
                self.coins += 1

        # Enemy collision
        for enemy in world["enemies"][:]:
            if self.rect.colliderect(enemy["rect"]):
                if self.vel_y > 0 and self.rect.bottom < enemy["rect"].top + 10:
                    # Stomp
                    world["enemies"].remove(enemy)
                    self.score += 200
                    self.vel_y = JUMP_VEL * 0.7
                else:
                    # Hit
                    self.lose_life(world)

        # Pit collision
        for pit in world["pits"]:
            if self.rect.colliderect(pit) and self.rect.bottom > pit.top:
                self.lose_life(world)
                break

        # Fall off world
        if self.rect.top > WORLD_HEIGHT:
            self.lose_life(world)

        # Flagpole collision
        if self.rect.colliderect(world["flagpole"][0]) or self.rect.colliderect(world["flagpole"][1]):
            if not self.won:
                self.won = True
                self.score += 1000

    def lose_life(self, world):
        self.lives -= 1
        if self.lives <= 0:
            self.dead = True
        else:
            # Reset to safe position (start)
            self.rect.x = 50
            self.rect.y = GROUND_Y - PLAYER_HEIGHT
            self.vel_y = 0
            self.on_ground = True

def draw_hud(screen, player, camera_x):
    font = pygame.font.SysFont(None, 36)
    hud_bg = pygame.Rect(0, 0, SCREEN_WIDTH, 40)
    pygame.draw.rect(screen, GRAY, hud_bg)
    pygame.draw.line(screen, WHITE, (0, 40), (SCREEN_WIDTH, 40), 2)

    lives_text = font.render(f"Lives: {player.lives}", True, GREEN)
    score_text = font.render(f"Score: {player.score}", True, YELLOW)
    coins_text = font.render(f"Coins: {player.coins}", True, CYAN)

    screen.blit(lives_text, (20, 5))
    screen.blit(score_text, (200, 5))
    screen.blit(coins_text, (400, 5))

    if player.dead:
        game_over = font.render("GAME OVER", True, RED)
        restart = font.render("Press R to Restart", True, WHITE)
        screen.blit(game_over, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 50))
        screen.blit(restart, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2))
    elif player.won:
        win_text = font.render("YOU WIN!", True, GREEN)
        final_score = font.render(f"Final Score: {player.score}", True, YELLOW)
        restart = font.render("Press R to Restart", True, WHITE)
        screen.blit(win_text, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 - 50))
        screen.blit(final_score, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
        screen.blit(restart, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 50))

def draw_world(screen, world, player, camera_x):
    # Clear screen
    screen.fill(DARK_GREEN)

    # Camera offset
    offset_x = -camera_x

    # Draw ground
    pygame.draw.rect(screen, BROWN, world["ground"].move(offset_x, 0))

    # Draw pits
    for pit in world["pits"]:
        pygame.draw.rect(screen, BLACK, pit.move(offset_x, 0))

    # Draw bricks
    for brick in world["bricks"]:
        pygame.draw.rect(screen, ORANGE, brick.move(offset_x, 0))
        pygame.draw.rect(screen, BLACK, brick.move(offset_x, 0), 2)

    # Draw question blocks
    for qb in world["question_blocks"]:
        pygame.draw.rect(screen, YELLOW, qb.move(offset_x, 0))
        pygame.draw.rect(screen, BLACK, qb.move(offset_x, 0), 2)
        # Draw question mark
        font = pygame.font.SysFont(None, 30)
        text = font.render("?", True, BLACK)
        screen.blit(text, (qb.x + 12 + offset_x, qb.y + 8))

    # Draw pipes
    for pipe in world["pipes"]:
        pygame.draw.rect(screen, GREEN, pipe.move(offset_x, 0))
        pygame.draw.rect(screen, DARK_GREEN, pipe.move(offset_x, 0), 2)

    # Draw platforms
    for plat in world["platforms"]:
        pygame.draw.rect(screen, BROWN, plat.move(offset_x, 0))
        pygame.draw.rect(screen, BLACK, plat.move(offset_x, 0), 2)

    # Draw coins
    for coin in world["coins"]:
        pygame.draw.rect(screen, YELLOW, coin.move(offset_x, 0))
        pygame.draw.rect(screen, ORANGE, coin.move(offset_x, 0), 3)

    # Draw enemies
    for enemy in world["enemies"]:
        pygame.draw.rect(screen, RED, enemy["rect"].move(offset_x, 0))
        pygame.draw.rect(screen, BLACK, enemy["rect"].move(offset_x, 0), 2)
        # Eyes
        pygame.draw.circle(screen, WHITE, (enemy["rect"].x + 10 + offset_x, enemy["rect"].y + 10), 4)
        pygame.draw.circle(screen, WHITE, (enemy["rect"].x + enemy["rect"].width - 10 + offset_x, enemy["rect"].y + 10), 4)
        pygame.draw.circle(screen, BLACK, (enemy["rect"].x + 10 + offset_x, enemy["rect"].y + 10), 2)
        pygame.draw.circle(screen, BLACK, (enemy["rect"].x + enemy["rect"].width - 10 + offset_x, enemy["rect"].y + 10), 2)

    # Draw flagpole
    pole, flag = world["flagpole"]
    pygame.draw.rect(screen, GRAY, pole.move(offset_x, 0))
    pygame.draw.rect(screen, WHITE, flag.move(offset_x, 0))

    # Draw player
    pygame.draw.rect(screen, BLUE, player.rect.move(offset_x, 0))
    # Face direction
    face_color = WHITE
    if player.vel_x > 0:
        pygame.draw.circle(screen, face_color, (player.rect.right - 10 + offset_x, player.rect.y + 15), 6)
    elif player.vel_x < 0:
        pygame.draw.circle(screen, face_color, (player.rect.x + 10 + offset_x, player.rect.y + 15), 6)
    else:
        pygame.draw.circle(screen, face_color, (player.rect.x + player.rect.width // 2 + offset_x, player.rect.y + 15), 6)

def update_camera(player):
    target_x = player.rect.centerx - SCREEN_WIDTH // 2
    camera_x = max(0, min(target_x, WORLD_WIDTH - SCREEN_WIDTH))
    return camera_x

def update_enemies(world):
    for enemy in world["enemies"]:
        enemy["rect"].x += enemy["vel"]
        if enemy["rect"].x <= enemy["patrol_left"]:
            enemy["vel"] = abs(enemy["vel"])
        if enemy["rect"].x + enemy["rect"].width >= enemy["patrol_right"]:
            enemy["vel"] = -abs(enemy["vel"])

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Super Mario Bros Medium")
    clock = pygame.time.Clock()

    world = create_world()
    player = Player()
    camera_x = 0

    running = True
    while running:
        dt = clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    # Restart
                    world = create_world()
                    player = Player()
                    camera_x = 0

        player.update(world, keys)
        update_enemies(world)
        camera_x = update_camera(player)
        draw_world(screen, world, player, camera_x)
        draw_hud(screen, player, camera_x)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()