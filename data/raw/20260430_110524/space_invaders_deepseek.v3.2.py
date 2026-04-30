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
PLAYER_BOTTOM_MARGIN = 40
PLAYER_START_X = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
PLAYER_START_Y = SCREEN_HEIGHT - PLAYER_BOTTOM_MARGIN - PLAYER_HEIGHT

BULLET_WIDTH = 6
BULLET_HEIGHT = 16
PLAYER_BULLET_SPEED = 8
ENEMY_BULLET_SPEED = 4
ENEMY_SHOOT_CHANCE = 0.003

ENEMY_ROWS = 4
ENEMY_COLS = 8
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 30
ENEMY_SPEED = 1.2
ENEMY_DROP_DISTANCE = 20
ENEMY_START_OFFSET_X = 80
ENEMY_START_OFFSET_Y = 60
ENEMY_GAP_X = 10
ENEMY_GAP_Y = 10

PLAYER_LIVES = 3
SCORE_PER_ENEMY = 10

COLOR_BG = (10, 10, 40)
COLOR_PLAYER = (50, 200, 255)
COLOR_ENEMY = (255, 50, 100)
COLOR_PLAYER_BULLET = (255, 255, 100)
COLOR_ENEMY_BULLET = (255, 100, 100)
COLOR_HUD = (230, 230, 230)
COLOR_TEXT = (255, 255, 255)
COLOR_WIN = (100, 255, 150)
COLOR_LOSE = (255, 150, 100)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(PLAYER_START_X, PLAYER_START_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.lives = PLAYER_LIVES
        self.bullets = []
        self.shoot_cooldown = 0

    def move(self, dx):
        self.rect.x = max(0, min(SCREEN_WIDTH - self.rect.width, self.rect.x + dx))

    def shoot(self):
        if self.shoot_cooldown <= 0:
            bullet_rect = pygame.Rect(
                self.rect.centerx - BULLET_WIDTH // 2,
                self.rect.top - BULLET_HEIGHT,
                BULLET_WIDTH, BULLET_HEIGHT
            )
            self.bullets.append(bullet_rect)
            self.shoot_cooldown = 10

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        for bullet in self.bullets[:]:
            bullet.y -= PLAYER_BULLET_SPEED
            if bullet.bottom < 0:
                self.bullets.remove(bullet)

    def draw(self, screen):
        pygame.draw.rect(screen, COLOR_PLAYER, self.rect, border_radius=8)
        for bullet in self.bullets:
            pygame.draw.rect(screen, COLOR_PLAYER_BULLET, bullet, border_radius=2)

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT)
        self.active = True
        self.bullets = []

    def update(self):
        for bullet in self.bullets[:]:
            bullet.y += ENEMY_BULLET_SPEED
            if bullet.top > SCREEN_HEIGHT:
                self.bullets.remove(bullet)

    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, COLOR_ENEMY, self.rect, border_radius=6)
        for bullet in self.bullets:
            pygame.draw.rect(screen, COLOR_ENEMY_BULLET, bullet, border_radius=2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders Medium")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.enemies = []
        self.enemy_direction = 1
        self.enemy_move_timer = 0
        self.enemy_move_delay = 1
        self.score = 0
        self.game_state = "PLAYING"
        self.create_enemies()

    def create_enemies(self):
        total_width = ENEMY_COLS * ENEMY_WIDTH + (ENEMY_COLS - 1) * ENEMY_GAP_X
        start_x = (SCREEN_WIDTH - total_width) // 2
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                x = start_x + col * (ENEMY_WIDTH + ENEMY_GAP_X)
                y = ENEMY_START_OFFSET_Y + row * (ENEMY_HEIGHT + ENEMY_GAP_Y)
                self.enemies.append(Enemy(x, y))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                if event.key == pygame.K_r:
                    self.reset_game()
                if self.game_state == "PLAYING" and event.key == pygame.K_SPACE:
                    self.player.shoot()

        if self.game_state == "PLAYING":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.move(-PLAYER_SPEED)
            if keys[pygame.K_RIGHT]:
                self.player.move(PLAYER_SPEED)

    def update_enemies(self):
        self.enemy_move_timer += 1
        if self.enemy_move_timer >= self.enemy_move_delay:
            self.enemy_move_timer = 0
            move_this_frame = False
            for enemy in self.enemies:
                if enemy.active:
                    enemy.rect.x += ENEMY_SPEED * self.enemy_direction
                    move_this_frame = True
                    if random.random() < ENEMY_SHOOT_CHANCE:
                        bullet = pygame.Rect(
                            enemy.rect.centerx - BULLET_WIDTH // 2,
                            enemy.rect.bottom,
                            BULLET_WIDTH, BULLET_HEIGHT
                        )
                        enemy.bullets.append(bullet)
            if move_this_frame:
                for enemy in self.enemies:
                    if enemy.active:
                        if enemy.rect.left <= 0 or enemy.rect.right >= SCREEN_WIDTH:
                            self.enemy_direction *= -1
                            for e in self.enemies:
                                if e.active:
                                    e.rect.y += ENEMY_DROP_DISTANCE
                            break
        for enemy in self.enemies:
            enemy.update()

    def check_collisions(self):
        for enemy in self.enemies:
            if enemy.active:
                for bullet in self.player.bullets[:]:
                    if bullet.colliderect(enemy.rect):
                        enemy.active = False
                        if bullet in self.player.bullets:
                            self.player.bullets.remove(bullet)
                        self.score += SCORE_PER_ENEMY

        for enemy in self.enemies:
            for bullet in enemy.bullets[:]:
                if bullet.colliderect(self.player.rect):
                    enemy.bullets.remove(bullet)
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.game_state = "LOST"

        if all(not enemy.active for enemy in self.enemies):
            self.game_state = "WON"

        for enemy in self.enemies:
            if enemy.active and enemy.rect.bottom >= self.player.rect.top:
                self.game_state = "LOST"

    def draw_hud(self):
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_HUD)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, COLOR_HUD)
        self.screen.blit(score_text, (20, 20))
        self.screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 20, 20))

    def draw_game_over(self):
        if self.game_state == "WON":
            text = self.font.render("YOU WIN!", True, COLOR_WIN)
        else:
            text = self.font.render("GAME OVER", True, COLOR_LOSE)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(text, rect)
        restart_text = self.small_font.render("Press R to Restart", True, COLOR_TEXT)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        while True:
            self.handle_input()
            self.screen.fill(COLOR_BG)

            if self.game_state == "PLAYING":
                self.player.update()
                self.update_enemies()
                self.check_collisions()

            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)

            self.draw_hud()
            if self.game_state != "PLAYING":
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()