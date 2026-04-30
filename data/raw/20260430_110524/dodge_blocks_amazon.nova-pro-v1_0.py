import pygame
import sys
import random

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SIZE = 60
PLAYER_SPEED = 7
OBSTACLE_SIZE = 40
OBSTACLE_FREQ = 40
OBSTACLE_SPEED_MIN = 4
OBSTACLE_SPEED_MAX = 8

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge Blocks Easy")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 40

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - PLAYER_SIZE))

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((OBSTACLE_SIZE, OBSTACLE_SIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - OBSTACLE_SIZE)
        self.rect.y = 0
        self.speedy = random.randint(OBSTACLE_SPEED_MIN, OBSTACLE_SPEED_MAX)

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

def main():
    player = Player()
    obstacles = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    obstacle_timer = 0
    score = 0
    start_ticks = pygame.time.get_ticks()

    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    game_over = False
                    obstacles.empty()
                    score = 0
                    start_ticks = pygame.time.get_ticks()
                    player.rect.centerx = SCREEN_WIDTH // 2
                    player.rect.bottom = SCREEN_HEIGHT - 40

        if not game_over:
            obstacle_timer += 1
            if obstacle_timer > OBSTACLE_FREQ:
                obstacle_timer = 0
                new_obstacle = Obstacle()
                obstacles.add(new_obstacle)
                all_sprites.add(new_obstacle)

            all_sprites.update()
            score = (pygame.time.get_ticks() - start_ticks) // 1000

            hits = pygame.sprite.spritecollide(player, obstacles, False)
            if hits:
                game_over = True

        screen.fill(BLACK)
        all_sprites.draw(screen)
        draw_text(f"Score: {score}", font, WHITE, screen, SCREEN_WIDTH // 2, 30)

        if game_over:
            draw_text("Game Over", font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            draw_text(f"Final Score: {score}", font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            draw_text("Press R to Restart", font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()