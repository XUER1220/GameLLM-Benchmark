import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_WIDTH, PLAYER_HEIGHT = 60, 32
PLAYER_SPEED = 6
BULLET_WIDTH, BULLET_HEIGHT = 6, 16
BULLET_SPEED = 8
ENEMY_WIDTH, ENEMY_HEIGHT = 40, 30
ENEMY_ROWS, ENEMY_COLS = 4, 8
ENEMY_SPEED = 1.2
ENEMY_DROP = 20
ENEMY_SHOOT_CHANCE = 0.002
PLAYER_LIVES = 3
SCORE_PER_ENEMY = 10
BG_COLOR = (10, 10, 40)
PLAYER_COLOR = (70, 200, 255)
ENEMY_COLOR = (255, 100, 100)
PLAYER_BULLET_COLOR = (255, 255, 100)
ENEMY_BULLET_COLOR = (255, 50, 50)
TEXT_COLOR = (220, 220, 220)
HUD_BG_COLOR = (30, 30, 60, 180)

random.seed(42)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 40
        self.speed = PLAYER_SPEED
        self.lives = PLAYER_LIVES
        self.bullets = []
        self.cooldown = 0

    def move(self, dx):
        self.rect.x += dx * self.speed
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))

    def shoot(self):
        if self.cooldown <= 0:
            bullet = pygame.Rect(0, 0, BULLET_WIDTH, BULLET_HEIGHT)
            bullet.centerx = self.rect.centerx
            bullet.bottom = self.rect.top
            self.bullets.append(bullet)
            self.cooldown = 10

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
        for bullet in self.bullets[:]:
            bullet.y -= BULLET_SPEED
            if bullet.bottom < 0:
                self.bullets.remove(bullet)

    def draw(self, screen):
        pygame.draw.rect(screen, PLAYER_COLOR, self.rect, border_radius=8)
        for bullet in self.bullets:
            pygame.draw.rect(screen, PLAYER_BULLET_COLOR, bullet, border_radius=2)

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT)
        self.alive = True
        self.bullets = []

    def maybe_shoot(self):
        if random.random() < ENEMY_SHOOT_CHANCE:
            bullet = pygame.Rect(0, 0, BULLET_WIDTH // 2, BULLET_HEIGHT)
            bullet.centerx = self.rect.centerx
            bullet.top = self.rect.bottom
            self.bullets.append(bullet)
            return True
        return False

    def draw(self, screen):
        if self.alive:
            pygame.draw.rect(screen, ENEMY_COLOR, self.rect, border_radius=5)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Invaders Medium")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)
        self.reset()

    def reset(self):
        self.player = Player()
        self.enemies = []
        self.enemy_bullets = []
        self.enemy_direction = 1
        self.score = 0
        self.game_over = False
        self.win = False
        self.init_enemies()

    def init_enemies(self):
        start_x = 100
        start_y = 80
        spacing_x = 70
        spacing_y = 50
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                self.enemies.append(Enemy(x, y))

    def update_enemies(self):
        move_down = False
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            enemy.rect.x += self.enemy_direction * ENEMY_SPEED
            if enemy.rect.right >= WIDTH or enemy.rect.left <= 0:
                move_down = True
        if move_down:
            self.enemy_direction *= -1
            for enemy in self.enemies:
                if enemy.alive:
                    enemy.rect.y += ENEMY_DROP

        for enemy in self.enemies:
            if enemy.alive and enemy.maybe_shoot():
                for bullet in enemy.bullets:
                    self.enemy_bullets.append(bullet)
                enemy.bullets.clear()

    def check_collisions(self):
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies:
                if enemy.alive and bullet.colliderect(enemy.rect):
                    enemy.alive = False
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    self.score += SCORE_PER_ENEMY
                    break

        for bullet in self.enemy_bullets[:]:
            if bullet.colliderect(self.player.rect):
                self.enemy_bullets.remove(bullet)
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self.game_over = True
                    self.win = False
                continue
            if bullet.top > HEIGHT:
                self.enemy_bullets.remove(bullet)

        for enemy in self.enemies:
            if enemy.alive and enemy.rect.bottom >= self.player.rect.top:
                self.game_over = True
                self.win = False
                break

        alive_enemies = [e for e in self.enemies if e.alive]
        if not alive_enemies:
            self.game_over = True
            self.win = True

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_r:
                        self.reset()
                    if event.key == pygame.K_SPACE and not self.game_over:
                        self.player.shoot()

            if not self.game_over:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    self.player.move(-1)
                if keys[pygame.K_RIGHT]:
                    self.player.move(1)

                self.player.update()
                self.update_enemies()
                self.check_collisions()

                for bullet in self.enemy_bullets:
                    bullet.y += BULLET_SPEED

            self.screen.fill(BG_COLOR)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            self.player.draw(self.screen)
            for bullet in self.enemy_bullets:
                pygame.draw.rect(self.screen, ENEMY_BULLET_COLOR, bullet, border_radius=1)

            hud_bg = pygame.Surface((WIDTH, 50), pygame.SRCALPHA)
            hud_bg.fill(HUD_BG_COLOR)
            self.screen.blit(hud_bg, (0, 0))

            score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
            lives_text = self.font.render(f"Lives: {self.player.lives}", True, TEXT_COLOR)
            self.screen.blit(score_text, (20, 10))
            self.screen.blit(lives_text, (WIDTH - 150, 10))

            if self.game_over:
                result = "You Win!" if self.win else "Game Over"
                color = (100, 255, 100) if self.win else (255, 100, 100)
                result_text = self.font.render(result, True, color)
                restart_text = self.small_font.render("Press R to Restart", True, TEXT_COLOR)
                self.screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT // 2 - 30))
                self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()