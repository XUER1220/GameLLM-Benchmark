import pygame
import sys
import random

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
GRID_SIZE = 24
MAZE_WIDTH, MAZE_HEIGHT = 19, 21
MAZE_DISPLAY_WIDTH, MAZE_DISPLAY_HEIGHT = MAZE_WIDTH * GRID_SIZE, MAZE_HEIGHT * GRID_SIZE
PLAYER_SPEED = 3
GHOST_SPEED = 2
POWER_PELLET_TIME = 60 * 6  # 6 seconds

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
RED = (255, 0, 0)
PINK = (255, 192, 203)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

maze_layout = [
    "#####################",
    "#      #        #   #",
    "## ### ######### # #",
    "#  #  ##     ##  # #",
    "#  #  #  ##  #  #  #",
    "###  ## ##### ##  ###",
    "#    #      #  #    #",
    "#  ## ##    ## ##  #",
    "#  #  #  ##  #  #  #",
    "###  #  #####  #  ###",
    "#    #        #    #",
    "#  ## #########  ## #",
    "#  #                 #",
    "###  #############  #",
    "#     #      #      #",
    "#  ## #########  ## #",
    "#  #                 #",
    "###  #############  #",
    "#    #      #      #",
    "#  ## #########  ## #",
    "#####################",
]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man Medium")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

class Player:
    def __init__(self):
        self.x = 9 * GRID_SIZE
        self.y = 20 * GRID_SIZE
        self.direction = (0, 0)
        self.rect = pygame.Rect(self.x, self.y, GRID_SIZE, GRID_SIZE)

    def move(self):
        self.x += self.direction[0] * PLAYER_SPEED
        self.y += self.direction[1] * PLAYER_SPEED
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2), GRID_SIZE // 2)

class Ghost:
    def __init__(self, start_x, start_y, color):
        self.x = start_x
        self.y = start_y
        self.color = color
        self.direction = (0, 0)
        self.rect = pygame.Rect(self.x, self.y, GRID_SIZE, GRID_SIZE)
        self.frightened = False

    def move(self):
        self.x += self.direction[0] * GHOST_SPEED
        self.y += self.direction[1] * GHOST_SPEED
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        if self.frightened:
            pygame.draw.circle(surface, CYAN, (self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2), GRID_SIZE // 2)
        else:
            pygame.draw.circle(surface, self.color, (self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2), GRID_SIZE // 2)

class Game:
    def __init__(self):
        self.player = Player()
        self.ghosts = [
            Ghost(13 * GRID_SIZE, 14 * GRID_SIZE, RED),
            Ghost(13 * GRID_SIZE, 14 * GRID_SIZE, PINK),
            Ghost(13 * GRID_SIZE, 14 * GRID_SIZE, ORANGE),
            Ghost(13 * GRID_SIZE, 14 * GRID_SIZE, PURPLE),
        ]
        self.dots = []
        self.power_pellets = []
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.win = False
        self.power_pellet_active = False
        self.power_pellet_timer = 0
        self.load_maze()

    def load_maze(self):
        for y, row in enumerate(maze_layout):
            for x, cell in enumerate(row):
                if cell == " ":
                    self.dots.append((x * GRID_SIZE, y * GRID_SIZE))
                elif cell == ".":
                    self.dots.append((x * GRID_SIZE, y * GRID_SIZE))
                elif cell == "o":
                    self.power_pellets.append((x * GRID_SIZE, y * GRID_SIZE))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    self.__init__()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.player.direction = (0, -1)
        elif keys[pygame.K_DOWN]:
            self.player.direction = (0, 1)
        elif keys[pygame.K_LEFT]:
            self.player.direction = (-1, 0)
        elif keys[pygame.K_RIGHT]:
            self.player.direction = (1, 0)
        else:
            self.player.direction = (0, 0)

    def check_collisions(self):
        self.player.move()
        player_rect = pygame.Rect(self.player.x, self.player.y, GRID_SIZE, GRID_SIZE)

        for dot in self.dots[:]:
            dot_rect = pygame.Rect(dot[0], dot[1], GRID_SIZE, GRID_SIZE)
            if player_rect.colliderect(dot_rect):
                self.dots.remove(dot)
                self.score += 10

        for pellet in self.power_pellets[:]:
            pellet_rect = pygame.Rect(pellet[0], pellet[1], GRID_SIZE, GRID_SIZE)
            if player_rect.colliderect(pellet_rect):
                self.power_pellets.remove(pellet)
                self.score += 50
                self.power_pellet_active = True
                self.power_pellet_timer = POWER_PELLET_TIME

        for ghost in self.ghosts:
            ghost_rect = pygame.Rect(ghost.x, ghost.y, GRID_SIZE, GRID_SIZE)
            if player_rect.colliderect(ghost_rect):
                if self.power_pellet_active:
                    ghost.x, ghost.y = 13 * GRID_SIZE, 14 * GRID_SIZE
                    self.score += 200
                else:
                    self.lives -= 1
                    if self.lives == 0:
                        self.game_over = True
                    else:
                        self.player.x, self.player.y = 9 * GRID_SIZE, 20 * GRID_SIZE
                        for g in self.ghosts:
                            g.x, g.y = 13 * GRID_SIZE, 14 * GRID_SIZE

    def update(self):
        self.handle_events()
        self.check_collisions()

        if self.power_pellet_active:
            self.power_pellet_timer -= 1
            if self.power_pellet_timer <= 0:
                self.power_pellet_active = False

        if not self.dots and not self.game_over:
            self.win = True

    def draw(self, surface):
        surface.fill(BLACK)
        for y, row in enumerate(maze_layout):
            for x, cell in enumerate(row):
                if cell == "#":
                    pygame.draw.rect(surface, WHITE, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        for dot in self.dots:
            pygame.draw.circle(surface, WHITE, (dot[0] + GRID_SIZE // 2, dot[1] + GRID_SIZE // 2), GRID_SIZE // 10)
        for pellet in self.power_pellets:
            pygame.draw.circle(surface, CYAN, (pellet[0] + GRID_SIZE // 2, pellet[1] + GRID_SIZE // 2), GRID_SIZE // 5)
        self.player.draw(surface)
        for ghost in self.ghosts:
            ghost.draw(surface)

        score_text = font.render(f"Score: {self.score}", True, WHITE)
        lives_text = font.render(f"Lives: {self.lives}", True, WHITE)
        dots_left_text = font.render(f"Dots Left: {len(self.dots)}", True, WHITE)
        surface.blit(score_text, (650, 10))
        surface.blit(lives_text, (650, 50))
        surface.blit(dots_left_text, (650, 90))

        if self.game_over:
            game_over_text = font.render("Game Over", True, RED)
            final_score_text = font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = font.render("Press R to Restart", True, WHITE)
            surface.blit(game_over_text, (650, 150))
            surface.blit(final_score_text, (650, 190))
            surface.blit(restart_text, (650, 230))
        elif self.win:
            win_text = font.render("You Win", True, GREEN)
            final_score_text = font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = font.render("Press R to Restart", True, WHITE)
            surface.blit(win_text, (650, 150))
            surface.blit(final_score_text, (650, 190))
            surface.blit(restart_text, (650, 230))

game = Game()

while True:
    game.update()
    game.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)