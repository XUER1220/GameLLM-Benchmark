import pygame
import sys
import random
import math

# 常量定义
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
PACMAN_SPEED = 3
GHOST_SPEED = 2
ENERGIZER_DURATION = 6000
PLAYER_LIVES = 3
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
RED = (255, 0, 0)
PINK = (255, 105, 180)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)
PACMAN_COLOR = YELLOW
GHOST_COLORS = [CYAN, RED, PINK, ORANGE]
ENERGIZER_COLOR = BLUE
WALL_COLOR = WHITE
DOT_COLOR = WHITE

# 迷宫定义
MAZE = [
    "WWWWWWWWWWWWWWWWWWWWWW",
    "W........................W",
    "W.WWWWWWW.WW.WWWWWWW.W",
    "W.W......W.W.W......W.W",
    "W.W.WWWWWWWWWWWW.WWW.W",
    "W.W.W...W......W.W.W.W",
    "W.W.W.WWWWWWWWW.W.W.W.W",
    "W.W.W.W......W.W.W.W.W",
    "W.W.WWWWWWWWWW.W.WWW.W",
    "W.W.................W.W",
    "WWWW.WWWWWWWWWWWW.WWWW",
    "W.....W......W.W......W",
    "W.WWWWWWWWWWWWW.WWWWWW.W",
    "W......W.W......W......W",
    "W.WWWWWWW.WWWWWWW.WWWWWW.W",
    "W......W.W......W......W",
    "W.WWWWWWWWWWWWWWWWWWWWW.W",
    "W........................W",
    "WWWWWWWWWWWWWWWWWWWWWWWW",
]

# 初始化 Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
random.seed(42)

class Pacman:
    def __init__(self):
        self.rect = pygame.Rect(228, 484, 24, 24)
        self.direction = pygame.Vector2(0, 0)
        self.mouth_open = True
        self.mouth_timer = 0

    def move(self):
        self.rect.move_ip(self.direction * PACMAN_SPEED)
        if self.rect.left < 0:
            self.rect.right = 456
        elif self.rect.right > 456:
            self.rect.left = 0

    def draw(self, surface):
        angle = 0
        if self.direction.x > 0:
            angle = 0
        elif self.direction.x < 0:
            angle = 180
        elif self.direction.y > 0:
            angle = 90
        elif self.direction.y < 0:
            angle = 270
        rotated_surface = pygame.transform.rotate(pacman_image, angle)
        surface.blit(rotated_surface, self.rect.topleft)

class Ghost:
    def __init__(self, start_pos, color):
        self.rect = pygame.Rect(start_pos[0], start_pos[1], 24, 24)
        self.color = color
        self.direction = pygame.Vector2(0, 0)
        self.target = pygame.Vector2(0, 0)
        self.frightened = False

    def move(self):
        self.rect.move_ip(self.direction * GHOST_SPEED)

    def draw(self, surface):
        if self.frightened:
            pygame.draw.rect(surface, BLUE, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)

def draw_maze(surface):
    for y, row in enumerate(MAZE):
        for x, char in enumerate(row):
            if char == "W":
                pygame.draw.rect(surface, WALL_COLOR, (x * 24, y * 24, 24, 24))
            elif char == ".":
                pygame.draw.circle(surface, DOT_COLOR, (x * 24 + 12, y * 24 + 12), 3)
            elif char == "E":
                pygame.draw.circle(surface, ENERGIZER_COLOR, (x * 24 + 12, y * 24 + 12), 8)

def check_collisions(pacman, ghosts):
    global score, lives
    for ghost in ghosts:
        if pacman.rect.colliderect(ghost.rect):
            if ghost.frightened:
                ghost.rect.topleft = (288, 336)
                score += 200
            else:
                lives -= 1
                pacman.rect.topleft = (228, 484)
                for ghost in ghosts:
                    ghost.rect.topleft = ghost.start_pos

def game_over():
    screen.fill(BLACK)
    text = font.render("Game Over", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    restart_text = font.render("Press R to Restart", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    pygame.display.flip()

def you_win():
    screen.fill(BLACK)
    text = font.render("You Win", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    restart_text = font.render("Press R to Restart", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    pygame.display.flip()

def reset_game():
    global pacman, ghosts, score, lives, dots, energizers, start_time
    pacman = Pacman()
    ghosts = [Ghost((288, 336), GHOST_COLORS[i]) for i in range(4)]
    score = 0
    lives = PLAYER_LIVES
    dots = [(x * 24 + 12, y * 24 + 12) for y, row in enumerate(MAZE) for x, char in enumerate(row) if char == "."]
    energizers = [(x * 24 + 12, y * 24 + 12) for y, row in enumerate(MAZE) for x, char in enumerate(row) if char == "E"]
    start_time = pygame.time.get_ticks()

def main():
    global score, lives, dots, energizers, start_time
    reset_game()
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    reset_game()
                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    pacman.direction = pygame.Vector2(0, 0)
                    if event.key == pygame.K_UP:
                        pacman.direction.y = -1
                    elif event.key == pygame.K_DOWN:
                        pacman.direction.y = 1
                    elif event.key == pygame.K_LEFT:
                        pacman.direction.x = -1
                    elif eventgame.K_RIGHT:
                        pacman.direction.x = 1

        screen.fill(BLACK)
        draw_maze(screen)
        pacman.move()
        pacman.draw(screen)

        for ghost in ghosts:
            if current_time - start_time < ENERGIZER_DURATION and ghost.frightened:
                ghost.frightened = True
            else:
                ghost.frightened = False
            ghost.move()
            ghost.draw(screen)

        check_collisions(pacman, ghosts)

        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        dots_left_text = font.render(f"Dots Left: {len(dots)}", True, WHITE)
        screen.blit(score_text, (520, 20))
        screen.blit(lives_text, (520, 60))
        screen.blit(dots_left_text, (520, 100))

        if len(dots) == 0:
            you_win()
            pygame.time.wait(2000)
            reset_game()
        elif lives == 0:
            game_over()
            pygame.time.wait(2000)
            reset_game()

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()