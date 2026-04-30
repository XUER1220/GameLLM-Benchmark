import pygame
import random

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 32
PLAYER_SPEED = 6
PLAYER_BULLET_WIDTH = 6
PLAYER_BULLET_HEIGHT = 16
PLAYER_BULLET_SPEED = 8
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 30
ENEMY_ROWS = 4
ENEMY_COLS = 8
ENEMY_SPEED = 1.2
ENEMY_DROP = 20
ENEMY_BULLET_WIDTH = 8
ENEMY_BULLET_HEIGHT = 16
ENEMY_BULLET_SPEED = 5
ENEMY_SHOOT_PROB = 0.001
PLAYER_LIVES = 3
SCORE_PER_ENEMY = 10

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders Medium")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

class Player:
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 40
        self.speed = PLAYER_SPEED
        self.lives = PLAYER_LIVES
        self.bullets = []
        self.color = GREEN

    def move_left(self):
        self.x -= self.speed
        if self.x < 0:
            self.x = 0

    def move_right(self):
        self.x += self.speed
        if self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width

    def shoot(self):
        bullet = pygame.Rect(self.x + self.width // 2 - PLAYER_BULLET_WIDTH // 2,
                             self.y,
                             PLAYER_BULLET_WIDTH,
                             PLAYER_BULLET_HEIGHT)
        self.bullets.append(bullet)

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.y -= PLAYER_BULLET_SPEED
            if bullet.y < 0:
                self.bullets.remove(bullet)

    def draw(self, surface):
        pygame.draw.polygon(surface, self.color, [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ])
        for bullet in self.bullets:
            pygame.draw.rect(surface, BLUE, bullet)

class Enemy:
    def __init__(self, x, y):
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = RED
        self.alive = True

    def draw(self, surface):
        if self.alive:
            pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, WHITE, self.rect, 2)

class EnemyGroup:
    def __init__(self):
        self.enemies = []
        self.direction = 1
        self.bullets = []
        self.create_enemies()

    def create_enemies(self):
        start_x = 100
        start_y = 50
        spacing_x = ENEMY_WIDTH + 10
        spacing_y = ENEMY_HEIGHT + 10
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                self.enemies.append(Enemy(x, y))

    def update(self):
        move_down = False
        for enemy in self.enemies:
            if enemy.alive:
                enemy.rect.x += ENEMY_SPEED * self.direction
                if enemy.rect.right >= SCREEN_WIDTH or enemy.rect.left <= 0:
                    move_down = True
        if move_down:
            self.direction *= -1
            for enemy in self.enemies:
                if enemy.alive:
                    enemy.rect.y += ENEMY_DROP

        if random.random() < ENEMY_SHOOT_PROB:
            self.shoot()

        for bullet in self.bullets[:]:
            bullet.y += ENEMY_BULLET_SPEED
            if bullet.y > SCREEN_HEIGHT:
                self.bullets.remove(bullet)

    def shoot(self):
        alive_enemies = [e for e in self.enemies if e.alive]
        if alive_enemies:
            shooter = random.choice(alive_enemies)
            bullet = pygame.Rect(shooter.rect.centerx - ENEMY_BULLET_WIDTH // 2,
                                 shooter.rect.bottom,
                                 ENEMY_BULLET_WIDTH,
                                 ENEMY_BULLET_HEIGHT)
            self.bullets.append(bullet)

    def draw(self, surface):
        for enemy in self.enemies:
            enemy.draw(surface)
        for bullet in self.bullets:
            pygame.draw.rect(surface, YELLOW, bullet)

    def all_dead(self):
        return all(not e.alive for e in self.enemies)

    def reached_bottom(self):
        for enemy in self.enemies:
            if enemy.alive and enemy.rect.bottom >= SCREEN_HEIGHT - 100:
                return True
        return False

def check_collisions(player, enemy_group, score):
    for bullet in player.bullets[:]:
        bullet_rect = bullet
        for enemy in enemy_group.enemies:
            if enemy.alive and bullet_rect.colliderect(enemy.rect):
                enemy.alive = False
                if bullet in player.bullets:
                    player.bullets.remove(bullet)
                score += SCORE_PER_ENEMY
                break

    for bullet in enemy_group.bullets[:]:
        bullet_rect = bullet
        if bullet_rect.colliderect(pygame.Rect(player.x, player.y, player.width, player.height)):
            enemy_group.bullets.remove(bullet)
            player.lives -= 1

    return score

def draw_hud(surface, score, lives, game_over, win):
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    surface.blit(score_text, (10, 10))
    surface.blit(lives_text, (SCREEN_WIDTH - 120, 10))

    if game_over:
        result = "You Win!" if win else "Game Over"
        result_color = GREEN if win else RED
        result_text = font.render(result, True, result_color)
        restart_text = font.render("Press R to Restart", True, WHITE)
        surface.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2))

def main():
    player = Player()
    enemy_group = EnemyGroup()
    score = 0
    game_over = False
    win = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    player = Player()
                    enemy_group = EnemyGroup()
                    score = 0
                    game_over = False
                    win = False
                if event.key == pygame.K_SPACE and not game_over:
                    player.shoot()

        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.move_left()
            if keys[pygame.K_RIGHT]:
                player.move_right()

            player.update_bullets()
            enemy_group.update()
            score = check_collisions(player, enemy_group, score)

            if enemy_group.all_dead():
                game_over = True
                win = True
            elif enemy_group.reached_bottom() or player.lives <= 0:
                game_over = True
                win = False

        screen.fill(BLACK)
        player.draw(screen)
        enemy_group.draw(screen)
        draw_hud(screen, score, player.lives, game_over, win)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()