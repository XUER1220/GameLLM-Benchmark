import pygame
import random
import sys

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 32
BULLET_WIDTH = 6
BULLET_HEIGHT = 16
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 30
PLAYER_SPEED = 6
PLAYER_BULLET_SPEED = 8
ENEMY_SPEED = 1.2
ENEMY_BULLET_SPEED = 4
ENEMY_ROWS = 4
ENEMY_COLS = 8
PLAYER_LIVES = 3
ENEMY_SHOOT_CHANCE = 0.002
FPS = 60

BACKGROUND_COLOR = (20, 20, 40)
PLAYER_COLOR = (70, 200, 255)
ENEMY_COLOR = (255, 50, 50)
PLAYER_BULLET_COLOR = (0, 255, 150)
ENEMY_BULLET_COLOR = (255, 255, 100)
TEXT_COLOR = (255, 255, 255)
HUD_COLOR = (150, 150, 200)
WIN_COLOR = (100, 255, 100)
LOSE_COLOR = (255, 100, 100)

random.seed(42)

class Player:
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 40 - self.height
        self.speed = PLAYER_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.lives = PLAYER_LIVES

    def move(self, direction):
        if direction == "left":
            self.x -= self.speed
        elif direction == "right":
            self.x += self.speed
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        self.rect.x = self.x

    def draw(self, screen):
        points = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(screen, PLAYER_COLOR, points)

class Bullet:
    def __init__(self, x, y, is_player=True):
        self.width = BULLET_WIDTH
        self.height = BULLET_HEIGHT
        self.x = x - self.width // 2
        self.y = y
        self.speed = PLAYER_BULLET_SPEED if is_player else -ENEMY_BULLET_SPEED
        self.is_player = is_player
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, screen):
        color = PLAYER_BULLET_COLOR if self.is_player else ENEMY_BULLET_COLOR
        pygame.draw.rect(screen, color, self.rect)

class Enemy:
    def __init__(self, x, y):
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.alive = True

    def draw(self, screen):
        if self.alive:
            pygame.draw.rect(screen, ENEMY_COLOR, self.rect, border_radius=5)
            eye_x = self.x + self.width // 3
            eye_y = self.y + self.height // 4
            pygame.draw.circle(screen, (255, 255, 255), (eye_x, eye_y), 4)
            pygame.draw.circle(screen, (0, 0, 0), (eye_x, eye_y), 2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders Medium")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)
        self.reset()

    def reset(self):
        self.player = Player()
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.score = 0
        self.game_over = False
        self.win = False
        self.enemy_direction = 1
        self.enemy_move_down = False
        self.enemy_move_counter = 0
        self._create_enemies()

    def _create_enemies(self):
        start_x = (SCREEN_WIDTH - ENEMY_COLS * ENEMY_WIDTH) // 2
        start_y = 80
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                x = start_x + col * (ENEMY_WIDTH + 10)
                y = start_y + row * (ENEMY_HEIGHT + 10)
                self.enemies.append(Enemy(x, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r and self.game_over:
                    self.reset()
                if event.key == pygame.K_SPACE and not self.game_over:
                    bullet = Bullet(self.player.x + self.player.width // 2, self.player.y)
                    self.bullets.append(bullet)

        if not self.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.move("left")
            if keys[pygame.K_RIGHT]:
                self.player.move("right")

    def update_enemies(self):
        if self.enemy_move_down:
            for enemy in self.enemies:
                if enemy.alive:
                    enemy.y += 20
                    enemy.rect.y = enemy.y
            self.enemy_direction *= -1
            self.enemy_move_down = False
        else:
            move_this_frame = False
            self.enemy_move_counter += 1
            if self.enemy_move_counter >= 2:
                move_this_frame = True
                self.enemy_move_counter = 0

            if move_this_frame:
                move_amount = ENEMY_SPEED * self.enemy_direction
                edge_reached = False
                for enemy in self.enemies:
                    if not enemy.alive:
                        continue
                    enemy.x += move_amount
                    enemy.rect.x = enemy.x
                    if enemy.x <= 0 or enemy.x + enemy.width >= SCREEN_WIDTH:
                        edge_reached = True
                if edge_reached:
                    self.enemy_move_down = True

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y < -bullet.height:
                self.bullets.remove(bullet)
                continue
            for enemy in self.enemies:
                if enemy.alive and bullet.rect.colliderect(enemy.rect):
                    enemy.alive = False
                    self.score += 10
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break

        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if bullet.y > SCREEN_HEIGHT:
                self.enemy_bullets.remove(bullet)
            elif bullet.rect.colliderect(self.player.rect):
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self.game_over = True
                    self.win = False
                if bullet in self.enemy_bullets:
                    self.enemy_bullets.remove(bullet)

    def enemy_shoot(self):
        alive_enemies = [e for e in self.enemies if e.alive]
        if not alive_enemies:
            return
        shooter = random.choice(alive_enemies)
        if random.random() < ENEMY_SHOOT_CHANCE:
            bullet = Bullet(shooter.x + shooter.width // 2, shooter.y + shooter.height, False)
            self.enemy_bullets.append(bullet)

    def check_game_state(self):
        if self.game_over:
            return
        alive_count = sum(1 for e in self.enemies if e.alive)
        if alive_count == 0:
            self.game_over = True
            self.win = True
            return
        for enemy in self.enemies:
            if enemy.alive and enemy.y + enemy.height >= self.player.y:
                self.game_over = True
                self.win = False
                break

    def draw_hud(self):
        score_text = self.font.render(f"Score: {self.score}", True, HUD_COLOR)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, HUD_COLOR)
        self.screen.blit(score_text, (20, 20))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 20))

        if self.game_over:
            result = "YOU WIN!" if self.win else "GAME OVER"
            color = WIN_COLOR if self.win else LOSE_COLOR
            result_text = self.font.render(result, True, color)
            restart_text = self.small_font.render("Press R to Restart", True, TEXT_COLOR)
            self.screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

    def run(self):
        while True:
            self.handle_events()
            if not self.game_over:
                self.update_enemies()
                self.update_bullets()
                self.enemy_shoot()
                self.check_game_state()

            self.screen.fill(BACKGROUND_COLOR)
            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for bullet in self.bullets:
                bullet.draw(self.screen)
            for bullet in self.enemy_bullets:
                bullet.draw(self.screen)
            self.draw_hud()

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()