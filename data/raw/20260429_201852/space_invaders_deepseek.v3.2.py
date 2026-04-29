import pygame
import sys
import random

pygame.init()

# 固定常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 32
PLAYER_SPEED = 6
PLAYER_BULLET_WIDTH = 6
PLAYER_BULLET_HEIGHT = 16
PLAYER_BULLET_SPEED = 8
ENEMY_ROWS = 4
ENEMY_COLS = 8
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 30
ENEMY_SPEED = 1.2
ENEMY_DROP = 20
ENEMY_FIRE_RATE = 0.005
INITIAL_LIVES = 3
SCORE_PER_ENEMY = 10
PLAYER_COLOR = (0, 200, 50)
ENEMY_COLOR = (220, 50, 50)
PLAYER_BULLET_COLOR = (0, 200, 255)
ENEMY_BULLET_COLOR = (255, 200, 0)
BG_COLOR = (10, 10, 40)
TEXT_COLOR = (255, 255, 255)
HUD_BG_COLOR = (30, 30, 60, 200)
GAME_OVER_BG_COLOR = (0, 0, 0, 180)

random.seed(42)

class Player:
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 40
        self.speed = PLAYER_SPEED
        self.lives = INITIAL_LIVES
        self.bullets = []
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, direction):
        if direction == "left":
            self.x -= self.speed
        elif direction == "right":
            self.x += self.speed
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        self.rect.topleft = (self.x, self.y)

    def shoot(self):
        bullet = pygame.Rect(
            self.x + self.width // 2 - PLAYER_BULLET_WIDTH // 2,
            self.y - PLAYER_BULLET_HEIGHT,
            PLAYER_BULLET_WIDTH,
            PLAYER_BULLET_HEIGHT
        )
        self.bullets.append(bullet)

    def update_bullets(self):
        new_bullets = []
        for bullet in self.bullets:
            bullet.y -= PLAYER_BULLET_SPEED
            if bullet.y > -PLAYER_BULLET_HEIGHT:
                new_bullets.append(bullet)
        self.bullets = new_bullets

    def draw(self, screen):
        pygame.draw.rect(screen, PLAYER_COLOR, self.rect)
        for bullet in self.bullets:
            pygame.draw.rect(screen, PLAYER_BULLET_COLOR, bullet)

class Enemy:
    def __init__(self, x, y):
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.x = x
        self.y = y
        self.alive = True
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if self.alive:
            pygame.draw.rect(screen, ENEMY_COLOR, self.rect)

class EnemySwarm:
    def __init__(self):
        self.enemies = []
        self.direction = 1
        self.bullets = []
        self.create_swarm()

    def create_swarm(self):
        start_x = (SCREEN_WIDTH - ENEMY_COLS * ENEMY_WIDTH) // 2
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                x = start_x + col * (ENEMY_WIDTH + 10)
                y = 60 + row * (ENEMY_HEIGHT + 10)
                self.enemies.append(Enemy(x, y))

    def update(self):
        move_down = False
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            enemy.x += ENEMY_SPEED * self.direction
            if enemy.x <= 0 or enemy.x + enemy.width >= SCREEN_WIDTH:
                move_down = True
            enemy.rect.topleft = (enemy.x, enemy.y)

        if move_down:
            self.direction *= -1
            for enemy in self.enemies:
                if enemy.alive:
                    enemy.y += ENEMY_DROP
                    enemy.rect.topleft = (enemy.x, enemy.y)

        self.update_bullets()

    def fire_random(self):
        alive_enemies = [e for e in self.enemies if e.alive]
        if alive_enemies and random.random() < ENEMY_FIRE_RATE:
            shooter = random.choice(alive_enemies)
            bullet = pygame.Rect(
                shooter.x + shooter.width // 2 - 3,
                shooter.y + shooter.height,
                6,
                12
            )
            self.bullets.append(bullet)

    def update_bullets(self):
        new_bullets = []
        for bullet in self.bullets:
            bullet.y += 5
            if bullet.y < SCREEN_HEIGHT:
                new_bullets.append(bullet)
        self.bullets = new_bullets

    def draw(self, screen):
        for enemy in self.enemies:
            enemy.draw(screen)
        for bullet in self.bullets:
            pygame.draw.rect(screen, ENEMY_BULLET_COLOR, bullet)

    def all_dead(self):
        return all(not enemy.alive for enemy in self.enemies)

    def reached_bottom(self):
        for enemy in self.enemies:
            if enemy.alive and enemy.y + enemy.height >= SCREEN_HEIGHT - 100:
                return True
        return False

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
        self.swarm = EnemySwarm()
        self.score = 0
        self.state = "playing"
        self.result_text = ""

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    self.reset()
                if event.key == pygame.K_SPACE and self.state == "playing":
                    self.player.shoot()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move("left")
        if keys[pygame.K_RIGHT]:
            self.player.move("right")

    def check_collisions(self):
        # 玩家子弹 vs 敌人
        for bullet in self.player.bullets[:]:
            bullet_rect = pygame.Rect(bullet)
            for enemy in self.swarm.enemies:
                if enemy.alive and bullet_rect.colliderect(enemy.rect):
                    enemy.alive = False
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    self.score += SCORE_PER_ENEMY
                    break

        # 敌人子弹 vs 玩家
        for bullet in self.swarm.bullets[:]:
            bullet_rect = pygame.Rect(bullet)
            if bullet_rect.colliderect(self.player.rect):
                self.swarm.bullets.remove(bullet)
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self.state = "game_over"
                    self.result_text = "GAME OVER"

    def update(self):
        if self.state != "playing":
            return
        self.player.update_bullets()
        self.swarm.update()
        self.swarm.fire_random()
        self.check_collisions()

        if self.swarm.all_dead():
            self.state = "game_over"
            self.result_text = "YOU WIN!"
        elif self.swarm.reached_bottom():
            self.state = "game_over"
            self.result_text = "GAME OVER"

    def draw_hud(self):
        hud_bg = pygame.Surface((SCREEN_WIDTH, 50), pygame.SRCALPHA)
        hud_bg.fill(HUD_BG_COLOR)
        self.screen.blit(hud_bg, (0, 0))

        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, TEXT_COLOR)
        self.screen.blit(score_text, (20, 10))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 150, 10))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(GAME_OVER_BG_COLOR)
        self.screen.blit(overlay, (0, 0))

        result_surf = self.font.render(self.result_text, True, TEXT_COLOR)
        restart_surf = self.small_font.render("Press R to Restart", True, TEXT_COLOR)
        self.screen.blit(result_surf, (SCREEN_WIDTH // 2 - result_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(restart_surf, (SCREEN_WIDTH // 2 - restart_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.player.draw(self.screen)
        self.swarm.draw(self.screen)
        self.draw_hud()
        if self.state == "game_over":
            self.draw_game_over()
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()