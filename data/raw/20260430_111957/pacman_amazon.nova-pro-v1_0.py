import pygame
import sys
import random
import time

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
MAZE_WIDTH, MAZE_HEIGHT = 456, 504
GRID_SIZE = 24
PLAYER_SPEED = 3
GHOST_SPEED = 2
POWER_PELLET_TIME = 6000  # in milliseconds

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

maze_layout = [
    "11111111111111111111",
    "10000000000000000001",
    "1011111110111111101",
    "1011111110111111101",
    "1000000000000000001",
    "1011110000111100001",
    "1011110000111100001",
    "1000000000000000001",
    "1011110000111100001",
    "1011110000111100001",
    "1000000000000000001",
    "1011111110111111101",
    "1011111110111111101",
    "1000000000000000001",
    "1011111111111111101",
    "1011111111111111101",
    "1000000000000000001",
    "1111111110111111111",
    "1111111110111111111",
    "1000000000000000001",
    "1111111111111111111",
]

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 240, 504 - GRID_SIZE
        self.direction = (0, 0)

    def update(self):
        self.rect.x += self.direction[0] * PLAYER_SPEED
        self.rect.y += self.direction[1] * PLAYER_SPEED

class Ghost(pygame.sprite.Sprite):
    def __init__(self, color, start_x, start_y):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = start_x, start_y
        self.direction = (0, 0)
        self.target_direction = (0, 0)
        self.frightened = False

    def update(self):
        self.rect.x += self.direction[0] * GHOST_SPEED
        self.rect.y += self.direction[1] * GHOST_SPEED

class Pellet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE // 2, GRID_SIZE // 2))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x + GRID_SIZE // 4, y + GRID_SIZE // 4

class PowerPellet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE // 2, GRID_SIZE // 2))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x + GRID_SIZE // 4, y + GRID_SIZE // 4

def draw_maze(screen):
    for y, row in enumerate(maze_layout):
        for x, col in enumerate(row):
            if col == '1':
                pygame.draw.rect(screen, WHITE, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pac-Man Medium")
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    pellets = pygame.sprite.Group()
    power_pellets = pygame.sprite.Group()
    ghosts = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    ghost_colors = [RED, ORANGE, PINK, CYAN]
    ghost_positions = [(240, 264), (240, 288), (240, 312), (240, 336)]

    for color, pos in zip(ghost_colors, ghost_positions):
        ghost = Ghost(color, pos[0], pos[1])
        ghosts.add(ghost)
        all_sprites.add(ghost)

    for y, row in enumerate(maze_layout):
        for x, col in enumerate(row):
            if col == '0':
                pellet = Pellet(x * GRID_SIZE, y * GRID_SIZE)
                pellets.add(pellet)
                all_sprites.add(pellet)
            elif col == '2':
                power_pellet = PowerPellet(x * GRID_SIZE, y * GRID_SIZE)
                power_pellets.add(power_pellet)
                all_sprites.add(power_pellet)

    score = 0
    lives = 3
    power_pellet_active = False
    power_pellet_time = 0

    game_over = False
    win = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    main()
                    return
                elif event.key == pygame.K_LEFT:
                    player.direction = (-1, 0)
                elif event.key == pygame.K_RIGHT:
                    player.direction = (1, 0)
                elif event.key == pygame.K_UP:
                    player.direction = (0, -1)
                elif event.key == pygame.K_DOWN:
                    player.direction = (0, 1)

        screen.fill(BLACK)
        draw_maze(screen)

        if not game_over and not win:
            all_sprites.update()

            if pygame.sprite.spritecollide(player, pellets, True):
                score += 10

            if pygame.sprite.spritecollide(player, power_pellets, True):
                score += 50
                power_pellet_active = True
                power_pellet_time = pygame.time.get_ticks()

            if power_pellet_active:
                current_time = pygame.time.get_ticks()
                if current_time - power_pellet_time > POWER_PELLET_TIME:
                    power_pellet_active = False

                eaten_ghosts = pygame.sprite.spritecollide(player, ghosts, False)
                for ghost in eaten_ghosts:
                    ghost.rect.x, ghost.rect.y = ghost_positions[ghosts.sprites().index(ghost)]
                    score += 200

            if pygame.sprite.spritecollide(player, ghosts, False) and not power_pellet_active:
                lives -= 1
                if lives == 0:
                    game_over = True
                else:
                    player.rect.x, player.rect.y = 240, 504 - GRID_SIZE
                    for ghost in ghosts:
                        ghost.rect.x, ghost.rect.y = ghost_positions[ghosts.sprites().index(ghost)]

            if len(pellets) == 0:
                win = True

        all_sprites.draw(screen)

        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        pellets_left_text = font.render(f"Pellets Left: {len(pellets)}", True, WHITE)
        screen.blit(score_text, (600, 10))
        screen.blit(lives_text, (600, 50))
        screen.blit(pellets_left_text, (600, 90))

        if game_over:
            game_over_text = font.render("Game Over", True, RED)
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(game_over_text, (300, 250))
            screen.blit(final_score_text, (300, 300))
            screen.blit(restart_text, (300, 350))

        if win:
            win_text = font.render("You Win", True, GREEN)
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(win_text, (300, 250))
            screen.blit(final_score_text, (300, 300))
            screen.blit(restart_text, (300, 350))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()