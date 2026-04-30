import pygame
import sys
import random
import time

pygame.init()
random.seed(42)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SPEED = 3
GHOST_SPEED = 2
ENERGY_DURATION = 6000
PLAYER_LIVES = 3

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man Medium")
clock = pygame.time.Clock()

maze = [
    "###########################",
    "#      #        #        #",
    "## ### ## ##### ## ### ##",
    "#  #   #   #       #   # #",
    "# ## ### ### ##### ### ###",
    "#      #    #   #    #   #",
    "### ### # ##   #  ## # ###",
    "   #   #   #   #   #     #",
    "### ### #  ##   #  ## ####",
    "#      #   #   #   #    #",
    "# ## ###   #   #   ### ###",
    "#  #   #   #   #   #   # #",
    "## ### ### #### ##### ## #",
    "#      #               # #",
    "# ## ### ########## ### #",
    "#  #   #   #   #   #   # #",
    "# ## ###   #   #   ### ###",
    "#  #   #   #   #   #   # #",
    "##     ##   ##   ##     #",
    "##########################"
]

class Player:
    def __init__(self):
        self.x = 240
        self.y = 390
        self.rect = pygame.Rect(self.x, self.y, 24, 24)
        self.lives = PLAYER_LIVES
        self.score = 0
        self.direction = (0, 0)

    def move(self):
        self.x += self.direction[0] * PLAYER_SPEED
        self.y += self.direction[1] * PLAYER_SPEED
        self.rect.topleft = (self.x, self.y)

    def reset(self):
        self.x = 240
        self.y = 390
        self.rect.topleft = (self.x, self.y)
        self.lives -= 1

class Ghost:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, 24, 24)
        self.color = color
        self.direction = (0, 0)
        self.target_direction = (0, 0)
        self.scared = False
        self.scared_start_time = 0

    def move(self):
        self.x += self.direction[0] * GHOST_SPEED
        self.y += self.direction[1] * GHOST_SPEED
        self.rect.topleft = (self.x, self.y)

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.rect.topleft = (self.x, self.y)
        self.scared = False
        self.scared_start_time = 0

class Game:
    def __init__(self):
        self.player = Player()
        self.ghosts = [
            Ghost(240, 240, RED),
            Ghost(240, 264, CYAN),
            Ghost(264, 240, ORANGE),
            Ghost(264, 264, PURPLE)
        ]
        for ghost in self.ghosts:
            ghost.start_x = ghost.x
            ghost.start_y = ghost.y
        self.dots = []
        self.energizers = []
        self.load_maze()
        self.running = True
        self.game_over = False
        self.win = False
        self.start_time = pygame.time.get_ticks()

    def load_maze(self):
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                if cell == " ":
                    self.dots.append((x * 24 + 12, y * 24 + 12))
                elif cell == "#":
                    pass
                elif cell == "o":
                    self.energizers.append((x * 24 + 12, y * 24 + 12))

    def check_collisions(self):
        for dot in self.dots[:]:
            if self.player.rect.collidepoint(dot):
                self.dots.remove(dot)
                self.player.score += 10
        for energizer in self.energizers[:]:
            if self.player.rect.collidepoint(energizer):
                self.energizers.remove(energizer)
                self.player.score += 50
                for ghost in self.ghosts:
                    ghost.scared = True
                    ghost.scared_start_time = pygame.time.get_ticks()
        for ghost in self.ghosts:
            if self.player.rect.colliderect(ghost.rect):
                if ghost.scared:
                    self.player.score += 200
                    ghost.reset()
                else:
                    self.player.reset()

    def update(self):
        if not self.game_over and not self.win:
            self.player.move()
            for ghost in self.ghosts:
                ghost.move()
                if ghost.scared and pygame.time.get_ticks() - ghost.scared_start_time > ENERGY_DURATION:
                    ghost.scared = False
            self.check_collisions()
            if len(self.dots) == 0:
                self.win = True
            if self.player.lives == 0:
                self.game_over = True

    def draw(self):
        screen.fill(BLACK)
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                if cell == "#":
                    pygame.draw.rect(screen, WHITE, (x * 24, y * 24, 24, 24))
                elif cell == " ":
                    pygame.draw.circle(screen, WHITE, (x * 24 + 12, y * 24 + 12), 3)
                elif cell == "o":
                    pygame.draw.circle(screen, YELLOW, (x * 24 + 12, y * 24 + 12), 6)
        pygame.draw.circle(screen, YELLOW, (self.player.rect.centerx, self.player.rect.centery), 12)
        for ghost in self.ghosts:
            if ghost.scared:
                pygame.draw.rect(screen, BLUE, ghost.rect)
            else:
                pygame.draw.rect(screen, ghost.color, ghost.rect)
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.player.score}", True, WHITE)
        lives_text = font.render(f"Lives: {self.player.lives}", True, WHITE)
        dots_text = font.render(f"Dots: {len(self.dots)}", True, WHITE)
        screen.blit(score_text, (500, 20))
        screen.blit(lives_text, (500, 60))
        screen.blit(dots_text, (500, 100))
        if self.game_over:
            game_over_text = font.render("Game Over", True, RED)
            screen.blit(game_over_text, (500, 200))
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(restart_text, (500, 240))
        elif self.win:
            win_text = font.render("You Win", True, GREEN)
            screen.blit(win_text, (500, 200))
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(restart_text, (500, 240))
        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_r:
                        self.__init__()
                    if not self.game_over and not self.win:
                        if event.key == pygame.K_UP:
                            self.player.direction = (0, -1)
                        elif event.key == pygame.K_DOWN:
                            self.player.direction = (0, 1)
                        elif event.key == pygame.K_LEFT:
                            self.player.direction = (-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.player.direction = (1, 0)
            if not self.game_over and not self.win:
                self.update()
            self.draw()
            clock.tick(FPS)

game = Game()
game.run()