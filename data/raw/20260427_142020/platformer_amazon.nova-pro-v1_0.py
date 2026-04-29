import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
WHITE, BLACK, RED, GREEN, BLUE, YELLOW, PURPLE = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (128, 0, 128)
PLAYER_SIZE, COIN_SIZE, ENEMY_SIZE = (40, 56), (20, 20), (36, 36)
GRAVITY, PLAYER_SPEED, INITIAL_JUMP_SPEED = 0.5, 5, -12
MAX_LIFE, INITIAL_SCORE = 3, 0
PLATFORMS = [(0, 550, 800, 50), (100, 400, 100, 20), (300, 300, 100, 20), (500, 400, 100, 20), (700, 200, 100, 20)]
COIN_POSITIONS = [(150, 380), (350, 280), (550, 380), (750, 180), (250, 80)]
ENEMY_POSITIONS = [(200, 380), (500, 380), (700, 180)]
ENEMY_PATROL_RANGE = [100, 50, 100]
END_FLAG_POSITION = (750, 150)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer Hard")
clock = pygame.time.Clock()

def draw_text(text, size, color, x, y):
    font = pygame.font.SysFont('arial', size)
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface(PLAYER_SIZE)
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (50, 550)
        self.vel_y = 0
        self.life = MAX_LIFE
        self.score = INITIAL_SCORE

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_SPACE] and self.rect.bottom >= SCREEN_HEIGHT:
            self.vel_y = INITIAL_JUMP_SPEED

        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = 0

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface(COIN_SIZE)
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_range):
        super().__init__()
        self.image = pygame.Surface(ENEMY_SIZE)
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.patrol_range = patrol_range
        self.direction = 1
        self.patrol_start_x = x

    def update(self):
        self.rect.x += self.direction * 2
        if abs(self.rect.x - self.patrol_start_x) > self.patrol_range:
            self.direction *= -1

class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

def create_sprites():
    player = Player()
    platforms = pygame.sprite.Group(*[Platform(*p) for p in PLATFORMS])
    coins = pygame.sprite.Group(*[Coin(*cp) for cp in COIN_POSITIONS])
    enemies = pygame.sprite.Group(*[Enemy(*ep, er) for ep, er in zip(ENEMY_POSITIONS, ENEMY_PATROL_RANGE)])
    flag = Flag(*END_FLAG_POSITION)
    return player, platforms, coins, enemies, flag

def main():
    player, platforms, coins, enemies, flag = create_sprites()
    all_sprites = pygame.sprite.Group(player, platforms, coins, enemies, flag)
    running = True
    game_over = False
    win = False

    while running:
        clock.tick(FPS)
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and (game_over or win):
                    player, platforms, coins, enemies, flag = create_sprites()
                    all_sprites = pygame.sprite.Group(player, platforms, coins, enemies, flag)
                    game_over = False
                    win = False

        if not game_over and not win:
            all_sprites.update()
            if pygame.sprite.spritecollide(player, platforms, False):
                player.vel_y = 0
            if pygame.sprite.spritecollide(player, coins, True):
                player.score += 10
            if pygame.sprite.spritecollide(player, enemies, False):
                player.life -= 1
                if player.life <= 0:
                    game_over = True
            if pygame.sprite.collide_rect(player, flag):
                win = True

        all_sprites.draw(screen)
        draw_text(f'Life: {player.life}', 20, WHITE, 10, 10)
        draw_text(f'Score: {player.score}', 20, WHITE, 10, 30)

        if game_over:
            draw_text('Game Over', 50, RED, 300, 250)
            draw_text('Press R to Restart', 30, WHITE, 270, 300)
        elif win:
            draw_text('You Win!', 50, GREEN, 320, 250)
            draw_text('Press R to Restart', 30, WHITE, 270, 300)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()