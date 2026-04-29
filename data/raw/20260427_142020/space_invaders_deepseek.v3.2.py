import pygame
import random

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders Medium")
clock = pygame.time.Clock()
FPS = 60
random.seed(42)

COLOR_BG = (10, 10, 30)
COLOR_PLAYER = (20, 200, 100)
COLOR_ENEMY = (220, 80, 60)
COLOR_PLAYER_BULLET = (100, 200, 255)
COLOR_ENEMY_BULLET = (255, 200, 50)
COLOR_TEXT = (240, 240, 240)
COLOR_HUD_BG = (20, 20, 40, 180)

PLAYER_WIDTH, PLAYER_HEIGHT = 60, 32
PLAYER_SPEED = 6
PLAYER_BULLET_WIDTH, PLAYER_BULLET_HEIGHT = 6, 16
PLAYER_BULLET_SPEED = 8
ENEMY_WIDTH, ENEMY_HEIGHT = 40, 30
ENEMY_ROWS, ENEMY_COLS = 4, 8
ENEMY_COUNT = ENEMY_ROWS * ENEMY_COLS
ENEMY_SPEED_X = 1.2
ENEMY_SPEED_Y = 20
ENEMY_BULLET_WIDTH, ENEMY_BULLET_HEIGHT = 6, 12
ENEMY_BULLET_SPEED = 4
ENEMY_SHOOT_CHANCE = 0.005
PLAYER_LIVES = 3
SCORE_PER_ENEMY = 10
PLAYER_BOTTOM_MARGIN = 40

class Player:
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - PLAYER_BOTTOM_MARGIN - self.height
        self.speed = PLAYER_SPEED
        self.lives = PLAYER_LIVES
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        if direction == "right" and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        self.rect.update(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        pygame.draw.polygon(surface, COLOR_PLAYER, [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ])
        pygame.draw.rect(surface, COLOR_PLAYER, (self.x + self.width//2 - 5, self.y + self.height, 10, 5))

class Enemy:
    def __init__(self, x, y):
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        pygame.draw.ellipse(surface, COLOR_ENEMY, (self.x, self.y, self.width, self.height))
        pygame.draw.ellipse(surface, (140, 30, 20), (self.x + 10, self.y + 10, 8, 8))
        pygame.draw.ellipse(surface, (140, 30, 20), (self.x + self.width - 18, self.y + 10, 8, 8))

class Bullet:
    def __init__(self, x, y, width, height, speed, is_player):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.is_player = is_player
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        if self.is_player:
            self.y -= self.speed
        else:
            self.y += self.speed
        self.rect.update(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        color = COLOR_PLAYER_BULLET if self.is_player else COLOR_ENEMY_BULLET
        pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))

def create_enemies():
    enemies = []
    start_x = 80
    start_y = 60
    spacing_x = 60
    spacing_y = 50
    for row in range(ENEMY_ROWS):
        for col in range(ENEMY_COLS):
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            enemies.append(Enemy(x, y))
    return enemies

def draw_hud(surface, score, lives, game_over, victory):
    hud_bg = pygame.Surface((SCREEN_WIDTH, 40), pygame.SRCALPHA)
    hud_bg.fill(COLOR_HUD_BG)
    surface.blit(hud_bg, (0, 0))
    font = pygame.font.SysFont(None, 28)
    score_text = font.render(f"Score: {score}", True, COLOR_TEXT)
    lives_text = font.render(f"Lives: {lives}", True, COLOR_TEXT)
    surface.blit(score_text, (20, 10))
    surface.blit(lives_text, (SCREEN_WIDTH - 100, 10))
    if game_over:
        font_large = pygame.font.SysFont(None, 48)
        if victory:
            result_text = font_large.render("YOU WIN!", True, (100, 255, 150))
        else:
            result_text = font_large.render("GAME OVER", True, (255, 100, 100))
        surface.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
        font_small = pygame.font.SysFont(None, 32)
        restart_text = font_small.render("Press R to Restart", True, COLOR_TEXT)
        surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

def main():
    player = Player()
    enemies = create_enemies()
    player_bullets = []
    enemy_bullets = []
    score = 0
    game_over = False
    victory = False
    enemy_direction = 1
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r and game_over:
                    player = Player()
                    enemies = create_enemies()
                    player_bullets.clear()
                    enemy_bullets.clear()
                    score = 0
                    game_over = False
                    victory = False
                    enemy_direction = 1
                if event.key == pygame.K_SPACE and not game_over:
                    player_bullets.append(Bullet(
                        player.x + player.width // 2 - PLAYER_BULLET_WIDTH // 2,
                        player.y,
                        PLAYER_BULLET_WIDTH,
                        PLAYER_BULLET_HEIGHT,
                        PLAYER_BULLET_SPEED,
                        True
                    ))

        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.move("left")
            if keys[pygame.K_RIGHT]:
                player.move("right")

            enemy_move_down = False
            max_x = max(e.x + e.width for e in enemies) if enemies else 0
            min_x = min(e.x for e in enemies) if enemies else 0
            if max_x > SCREEN_WIDTH - 20 or min_x < 20:
                enemy_direction *= -1
                enemy_move_down = True

            for enemy in enemies:
                enemy.x += ENEMY_SPEED_X * enemy_direction
                if enemy_move_down:
                    enemy.y += ENEMY_SPEED_Y
                enemy.rect.update(enemy.x, enemy.y, enemy.width, enemy.height)
                if random.random() < ENEMY_SHOOT_CHANCE:
                    enemy_bullets.append(Bullet(
                        enemy.x + enemy.width // 2 - ENEMY_BULLET_WIDTH // 2,
                        enemy.y + enemy.height,
                        ENEMY_BULLET_WIDTH,
                        ENEMY_BULLET_HEIGHT,
                        ENEMY_BULLET_SPEED,
                        False
                    ))

            for bullet in player_bullets[:]:
                bullet.update()
                if bullet.y < 0:
                    player_bullets.remove(bullet)
                    continue
                hit = False
                for enemy in enemies[:]:
                    if bullet.rect.colliderect(enemy.rect):
                        enemies.remove(enemy)
                        player_bullets.remove(bullet)
                        score += SCORE_PER_ENEMY
                        hit = True
                        break
                if hit:
                    continue

            for bullet in enemy_bullets[:]:
                bullet.update()
                if bullet.y > SCREEN_HEIGHT:
                    enemy_bullets.remove(bullet)
                    continue
                if bullet.rect.colliderect(player.rect):
                    enemy_bullets.remove(bullet)
                    player.lives -= 1
                    if player.lives <= 0:
                        game_over = True
                        victory = False

            if not enemies:
                game_over = True
                victory = True

            for enemy in enemies:
                if enemy.y + enemy.height >= player.y:
                    game_over = True
                    victory = False
                    break

        screen.fill(COLOR_BG)
        for enemy in enemies:
            enemy.draw(screen)
        for bullet in player_bullets:
            bullet.draw(screen)
        for bullet in enemy_bullets:
            bullet.draw(screen)
        player.draw(screen)
        draw_hud(screen, score, player.lives, game_over, victory)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()