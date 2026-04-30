import pygame
import sys
import random
import time

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
MAZE_WIDTH, MAZE_HEIGHT = 456, 504
GRID_SIZE = 24
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
PINK = (255, 192, 203)
ORANGE = (255, 165, 0)
GHOST_COLORS = [CYAN, MAGENTA, RED, PINK]
PLAYER_SPEED = 3
POWER_DURATION = 6000  # in milliseconds

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man Medium")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

class Player:
    def __init__(self):
        self.x, self.y = 9 * GRID_SIZE, 20 * GRID_SIZE
        self.direction = (0, 0)
        self.next_direction = (0, 0)

    def move(self, maze):
        new_x, new_y = self.x + self.direction[0] * PLAYER_SPEED, self.y + self.direction[1] * PLAYER_SPEED
        if maze[int(new_y // GRID_SIZE)][int(new_x // GRID_SIZE)]!= 'X':
            self.x, self.y = new_x, new_y
        else:
            self.check_tunnel(maze)

    def check_tunnel(self, maze):
        if self.x < 0:
            self.x = MAZE_WIDTH - GRID_SIZE
        elif self.x >= MAZE_WIDTH:
            self.x = 0

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), GRID_SIZE // 2)

class Ghost:
    def __init__(self, start_x, start_y, color):
        self.x, self.y = start_x * GRID_SIZE, start_y * GRID_SIZE
        self.direction = (0, -1)
        self.color = color
        self.start_x, self.start_y = start_x * GRID_SIZE, start_y * GRID_SIZE

    def move(self, maze):
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        possible_directions = []
        for dx, dy in directions:
            nx, ny = self.x + dx * GRID_SIZE, self.y + dy * GRID_SIZE
            if maze[int(ny // GRID_SIZE)][int(nx // GRID_SIZE)]!= 'X':
                possible_directions.append((dx, dy))
        if possible_directions:
            self.direction = random.choice(possible_directions)
        self.x += self.direction[0] * PLAYER_SPEED
        self.y += self.direction[1] * PLAYER_SPEED

    def reset(self):
        self.x, self.y = self.start_x, self.start_y

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), GRID_SIZE // 2)

class Game:
    def __init__(self):
        self.maze = [
            "XXXXXXXXXXXXXXXXXXXXXXXX",
            "X   X   X       X   X  X",
            "X  XX XX XX XX XX XX  X",
            "X   X   X   X   X   X  X",
            "X  XX XX XX XX XX XX  X",
            "X        X   X        X",
            "X  XX XX XX XX XX XX  X",
            "X   X       X   X   X  X",
            "X  XX XX XX XX XX XX  X",
            "X   X   X   X   X   X  X",
            "XXXX XX XX XX XX XXXX X",
            "    X   X   X   X     X",
            "XXXXX XX XX XX XX XXXXX",
            "X                    X X",
            "X  XX XX XX XX XX XX X X",
            "X   X   X   X   X   X  X",
            "X  XX XX XX XX XX XX  X",
            "X   X       X   X   X  X",
            "X  XX XX XX XX XX XX  X",
            "X   X   X   X   X   X  X",
            "XXXXXXXXXXXXXXXXXXXXXXXX",
        ]
        self.player = Player()
        self.ghosts = [Ghost(13, 14, color) for color in GHOST_COLORS]
        self.dots = [(i * GRID_SIZE + GRID_SIZE // 2, j * GRID_SIZE + GRID_SIZE // 2) for j in range(21) for i in range(19) if self.maze[j][i] == ' ']
        self.power_dots = [(4 * GRID_SIZE + GRID_SIZE // 2, 2 * GRID_SIZE + GRID_SIZE // 2),
                           (14 * GRID_SIZE + GRID_SIZE // 2, 2 * GRID_SIZE + GRID_SIZE // 2),
                           (4 * GRID_SIZE + GRID_SIZE // 2, 18 * GRID_SIZE + GRID_SIZE // 2),
                           (14 * GRID_SIZE + GRID_SIZE // 2, 18 * GRID_SIZE + GRID_SIZE // 2)]
        self.score = 0
        self.lives = 3
        self.power_mode = False
        self.power_start_time = 0
        self.game_over = False
        self.win = False

    def reset(self):
        self.__init__()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    self.reset()
                elif not self.game_over:
                    if event.key == pygame.K_UP:
                        self.player.next_direction = (0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.player.next_direction = (0, 1)
                    elif event.key == pygame.K_LEFT:
                        self.player.next_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.player.next_direction = (1, 0)

    def update(self):
        if not self.game_over:
            self.player.direction = self.player.next_direction
            self.player.move(self.maze)
            for ghost in self.ghosts:
                ghost.move(self.maze)
            self.check_collisions()
            self.check_power_mode()

    def check_collisions(self):
        player_pos = (int(self.player.x // GRID_SIZE), int(self.player.y // GRID_SIZE))
        if self.maze[player_pos[1]][player_pos[0]] == ' ':
            self.maze[player_pos[1]] = self.maze[player_pos[1]][:player_pos[0]] + '-' + self.maze[player_pos[1]][player_pos[0] + 1:]
            self.dots.remove((self.player.x + GRID_SIZE // 2, self.player.y + GRID_SIZE // 2))
            self.score += 10
        elif self.maze[player_pos[1]][player_pos[0]] == 'O':
            self.maze[player_pos[1]] = self.maze[player_pos[1]][:player_pos[0]] + '-' + self.maze[player_pos[1]][player_pos[0] + 1:]
            self.power_dots.remove((self.player.x + GRID_SIZE // 2, self.player.y + GRID_SIZE // 2))
            self.score += 50
            self.power_mode = True
            self.power_start_time = pygame.time.get_ticks()

        for ghost in self.ghosts:
            if (int(ghost.x // GRID_SIZE), int(ghost.y // GRID_SIZE)) == player_pos:
                if self.power_mode:
                    ghost.reset()
                    self.score += 200
                else:
                    self.lives -= 1
                    if self.lives == 0:
                        self.game_over = True
                    else:
                        self.player.x, self.player.y = 9 * GRID_SIZE, 20 * GRID_SIZE
                        for ghost in self.ghosts:
                            ghost.reset()

        if not self.dots and not self.power_dots:
            self.win = True
            self.game_over = True

    def check_power_mode(self):
        if self.power_mode and pygame.time.get_ticks() - self.power_start_time > POWER_DURATION:
            self.power_mode = False

    def draw(self, surface):
        surface.fill(BLACK)
        for j in range(21):
            for i in range(19):
                color = WHITE if self.maze[j][i] == ''else BLACK
                pygame.draw.rect(surface, color, (i * GRID_SIZE + 100, j * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                if self.maze[j][i] == 'X':
                    pygame.draw.rect(surface, color, (i * GRID_SIZE + 100, j * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        for dot in self.dots:
            pygame.draw.circle(surface, WHITE, dot, 3)
        for power_dot in self.power_dots:
            pygame.draw.circle(surface, ORANGE, power_dot, 8)
        self.player.draw(surface)
        for ghost in self.ghosts:
            ghost.draw(surface)

        score_text = font.render(f"Score: {self.score}", True, WHITE)
        lives_text = font.render(f"Lives: {self.lives}", True, WHITE)
        dots_left_text = font.render(f"Dots Left: {len(self.dots)}", True, WHITE)
        surface.blit(score_text, (650, 50))
        surface.blit(lives_text, (650, 100))
        surface.blit(dots_left_text, (650, 150))

        if self.game_over:
            if self.win:
                game_over_text = font.render("You Win", True, WHITE)
            else:
                game_over_text = font.render("Game Over", True, WHITE)
            final_score_text = font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = font.render("Press R to Restart", True, WHITE)
            surface.blit(game_over_text, (650, 250))
            surface.blit(final_score_text, (650, 300))
            surface.blit(restart_text, (650, 350))

game = Game()

while True:
    game.handle_input()
    game.update()
    game.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)