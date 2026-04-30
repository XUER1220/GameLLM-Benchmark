import pygame
import random
import sys

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

PLAYER_SIZE = (60, 32)
PLAYER_SPEED = 6
PLAYER_BOTTOM_MARGIN = 40
PLAYER_COLOR = (0, 200, 50)
PLAYER_BULLET_SIZE = (6, 16)
PLAYER_BULLET_SPEED = 8
PLAYER_BULLET_COLOR = (255, 255, 100)

ENEMY_ROWS = 4
ENEMY_COLS = 8
ENEMY_SIZE = (40, 30)
ENEMY_SPEED = 1.2
ENEMY_DROP = 20
ENEMY_COLOR = (200, 50, 50)
ENEMY_BULLET_SIZE = (8, 20)
ENEMY_BULLET_SPEED = 5
ENEMY_BULLET_COLOR = (255, 150, 150)
ENEMY_SHOOT_CHANCE = 0.002

BACKGROUND_COLOR = (20, 20, 40)
UI_COLOR = (220, 220, 255)

INITIAL_LIVES = 3
SCORE_PER_ENEMY = 10

random.seed(42)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, PLAYER_SIZE[0], PLAYER_SIZE[1])
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - PLAYER_BOTTOM_MARGIN
        self.speed = PLAYER_SPEED
        self.lives = INITIAL_LIVES
        self.bullets = []
        self.shoot_cooldown = 0

    def move(self, dx):
        self.rect.x += dx
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, SCREEN_WIDTH)

    def shoot(self):
        if self.shoot_cooldown == 0:
            bullet_rect = pygame.Rect(0, 0, PLAYER_BULLET_SIZE[0], PLAYER_BULLET_SIZE[1])
            bullet_rect.centerx = self.rect.centerx
            bullet_rect.bottom = self.rect.top
            self.bullets.append(bullet_rect)
            self.shoot_cooldown = 10

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        for bullet in self.bullets[:]:
            bullet.y -= PLAYER_BULLET_SPEED
            if bullet.bottom < 0:
                self.bullets.remove(bullet)

    def draw(self, surface):
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect, border_radius=5)
        for bullet in self.bullets:
            pygame.draw.rect(surface, PLAYER_BULLET_COLOR, bullet, border_radius=2)

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, ENEMY_SIZE[0], ENEMY_SIZE[1])
        self.active = True

    def draw(self, surface):
        if self.active:
            pygame.draw.rect(surface, ENEMY_COLOR, self.rect, border_radius=4)

class EnemyGroup:
    def __init__(self):
        self.enemies = []
        self.bullets = []
        self.direction = 1
        self.create_enemies()

    def create_enemies(self):
        start_x = (SCREEN_WIDTH - (ENEMY_COLS * (ENEMY_SIZE[0] + 10))) // 2
        start_y = 80
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                x = start_x + col * (ENEMY_SIZE[0] + 10)
                y = start_y + row * (ENEMY_SIZE[1] + 10)
                self.enemies.append(Enemy(x, y))

    def update(self):
        move_down = False
        for enemy in self.enemies:
            if enemy.active:
                enemy.rect.x += ENEMY_SPEED * self.direction
                if enemy.rect.right >= SCREEN_WIDTH or enemy.rect.left <= 0:
                    move_down = True
        if move_down:
            self.direction *= -1
            for enemy in self.enemies:
                if enemy.active:
                    enemy.rect.y += ENEMY_DROP

        for bullet in self.bullets[:]:
            bullet.y += ENEMY_BULLET_SPEED
            if bullet.top > SCREEN_HEIGHT:
                self.bullets.remove(bullet)

        if random.random() < ENEMY_SHOOT_CHANCE and self.enemies:
            active_enemies = [e for e in self.enemies if e.active]
            if active_enemies:
                shooter = random.choice(active_enemies)
                bullet_rect = pygame.Rect(0, 0, ENEMY_BULLET_SIZE[0], ENEMY_BULLET_SIZE[1])
                bullet_rect.centerx = shooter.rect.centerx
                bullet_rect.top = shooter.rect.bottom
                self.bullets.append(bullet_rect)

    def draw(self, surface):
        for enemy in self.enemies:
            enemy.draw(surface)
        for bullet in self.bullets:
            pygame.draw.rect(surface, ENEMY_BULLET_COLOR, bullet, border_radius=2)

    def all_defeated(self):
        return all(not e.active for e in self.enemies)

    def reached_player(self, player_y):
        for enemy in self.enemies:
            if enemy.active and enemy.rect.bottom >= player_y:
                return True
        return False

def show_text(surface, text, y, color=UI_COLOR):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, y))
    surface.blit(text_surf, text_rect)

def main():
    player = Player()
    enemy_group = EnemyGroup()
    score = 0
    game_state = "playing"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r and game_state != "playing":
                    return

        keys = pygame.key.get_pressed()
        if game_state == "playing":
            if keys[pygame.K_LEFT]:
                player.move(-player.speed)
            if keys[pygame.K_RIGHT]:
                player.move(player.speed)
            if keys[pygame.K_SPACE]:
                player.shoot()

        screen.fill(BACKGROUND_COLOR)

        if game_state == "playing":
            player.update()
            enemy_group.update()

            for bullet in player.bullets[:]:
                for enemy in enemy_group.enemies:
                    if enemy.active and bullet.colliderect(enemy.rect):
                        enemy.active = False
                        if bullet in player.bullets:
                            player.bullets.remove(bullet)
                        score += SCORE_PER_ENEMY
                        break

            for bullet in enemy_group.bullets[:]:
                if bullet.colliderect(player.rect):
                    player.lives -= 1
                    enemy_group.bullets.remove(bullet)
                    if player.lives <= 0:
                        game_state = "lost"

            if enemy_group.reached_player(player.rect.top):
                game_state = "lost"

            if enemy_group.all_defeated():
                game_state = "won"

        player.draw(screen)
        enemy_group.draw(screen)

        pygame.draw.rect(screen, UI_COLOR, (10, 10, 150, 40), border_radius=5)
        pygame.draw.rect(screen, UI_COLOR, (SCREEN_WIDTH-160, 10, 150, 40), border_radius=5)
        score_text = font.render(f"Score: {score}", True, BACKGROUND_COLOR)
        lives_text = font.render(f"Lives: {player.lives}", True, BACKGROUND_COLOR)
        screen.blit(score_text, (20, 20))
        screen.blit(lives_text, (SCREEN_WIDTH-150, 20))

        if game_state == "won":
            show_text(screen, "Victory! All enemies destroyed.", SCREEN_HEIGHT//2 - 30, (100, 255, 100))
            show_text(screen, "Press R to Restart", SCREEN_HEIGHT//2 + 10)
        elif game_state == "lost":
            show_text(screen, "Game Over", SCREEN_HEIGHT//2 - 30, (255, 100, 100))
            show_text(screen, "Press R to Restart", SCREEN_HEIGHT//2 + 10)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    while True:
        main()