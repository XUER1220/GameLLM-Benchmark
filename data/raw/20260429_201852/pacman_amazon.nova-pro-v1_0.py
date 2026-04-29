import pygame
import sys
import random
import math

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
MAZE_WIDTH, MAZE_HEIGHT = 19, 21
CELL_SIZE = 24
MAZE_DISPLAY_WIDTH, MAZE_DISPLAY_HEIGHT = MAZE_WIDTH * CELL_SIZE, MAZE_HEIGHT * CELL_SIZE
PLAYER_SPEED = 3

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
PINK = (255, 192, 203)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)

maze = [
    "1111111111111111111",
    "1000000000000000001",
    "1011111110111111101",
    "1010000000000100101",
    "1010111111111010101",
    "1010100000001010101",
    "1010101111101010101",
    "1010101000101010101",
    "1010101011101010101",
    "1010101000101010101",
    "1010101111101010101",
    "1010000000000100101",
    "1011111110111111101",
    "1000000000000000001",
    "1111111111111111111",
]

player_start = (1, 1)
ghost_start = [(1, 14), (2, 14), (3, 14), (4, 14)]
energizer_positions = [(7, 1), (11, 1), (7, 19), (11, 19)]

class Player:
    def __init__(self):
        self.x, self.y = player_start
        self.direction = (0, 0)
        self.rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

    def move(self):
        new_x, new_y = self.x + self.direction[0], self.y + self.direction[1]
        if maze[new_y][new_x]!= "1":
            self.x, self.y = new_x, new_y
            self.rect.topleft = (self.x * CELL_SIZE, self.y * CELL_SIZE)

class Ghost:
    def __init__(self, start_pos):
        self.x, self.y = start_pos
        self.rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        self.target = (0, 0)
        self.frightened = False

    def move(self):
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        valid_moves = [(dx, dy) for dx, dy in directions if maze[self.y + dy][self.x + dx]!= "1"]
        if valid_moves:
            self.x += valid_moves[0][0]
            self.y += valid_moves[0][1]
            self.rect.topleft = (self.x * CELL_SIZE, self.y * CELL_SIZE)

    def update_target(self, player):
        self.target = (player.x, player.y)

def draw_maze(screen):
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == "1":
                pygame.draw.rect(screen, WHITE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif cell == "0":
                pygame.draw.rect(screen, BLACK, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pygame.draw.circle(screen, YELLOW, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), 2)
            elif cell == "2":
                pygame.draw.rect(screen, BLACK, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pygame.draw.circle(screen, CYAN, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), 8)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pac-Man Medium")
    clock = pygame.time.Clock()

    player = Player()
    ghosts = [Ghost(pos) for pos in ghost_start]
    score = 0
    lives = 3
    beans_left = sum(row.count("0") for row in maze)
    energizer_timer = 0

    def reset_game():
        nonlocal player, ghosts, score, lives, beans_left, energizer_timer
        player = Player()
        ghosts = [Ghost(pos) for pos in ghost_start]
        score = 0
        lives = 3
        beans_left = sum(row.count("0") for row in maze)
        energizer_timer = 0

    running = True
    game_over = False
    while running:
        screen.fill(BLACK)
        draw_maze(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    reset_game()
                    game_over = False

        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                player.direction = (0, -1)
            elif keys[pygame.K_DOWN]:
                player.direction = (0, 1)
            elif keys[pygame.K_LEFT]:
                player.direction = (-1, 0)
            elif keys[pygame.K_RIGHT]:
                player.direction = (1, 0)

            player.move()

            for ghost in ghosts:
                ghost.update_target(player)
                ghost.move()

            if maze[player.y][player.x] == "0":
                maze[player.y] = maze[player.y][:player.x] + " " + maze[player.y][player.x + 1:]
                score += 10
                beans_left -= 1

            if (player.x, player.y) in energizer_positions:
                maze[player.y] = maze[player.y][:player.x] + " " + maze[player.y][player.x + 1:]
                score += 50
                energizer_timer = 360
                energizer_positions.remove((player.x, player.y))

            if energizer_timer > 0:
                energizer_timer -= 1
                for ghost in ghosts:
                    ghost.frightened = True
            else:
                for ghost in ghosts:
                    ghost.frightened = False

            for ghost in ghosts:
                if player.rect.colliderect(ghost.rect):
                    if ghost.frightened:
                        ghost.x, ghost.y = ghost_start[ghosts.index(ghost)]
                        score += 200
                    else:
                        lives -= 1
                        player.x, player.y = player_start
                        for g in ghosts:
                            g.x, g.y = ghost_start[ghosts.index(g)]

            if beans_left == 0:
                game_over = True
                font = pygame.font.SysFont(None, 55)
                text = font.render("You Win", True, WHITE)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
                text = font.render(f"Score: {score}", True, WHITE)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
                text = font.render("Press R to Restart", True, WHITE)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + text.get_height()))

            if lives == 0:
                game_over = True
                font = pygame.font.SysFont(None, 55)
                text = font.render("Game Over", True, WHITE)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
                text = font.render(f"Score: {score}", True, WHITE)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
                text = font.render("Press R to Restart", True, WHITE)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + text.get_height()))

        pygame.draw.rect(screen, WHITE, (MAZE_DISPLAY_WIDTH, 0, SCREEN_WIDTH - MAZE_DISPLAY_WIDTH, SCREEN_HEIGHT))
        font = pygame.font.SysFont(None, 30)
        text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(text, (MAZE_DISPLAY_WIDTH + 10, 10))
        text = font.render(f"Lives: {lives}", True, BLACK)
        screen.blit(text, (MAZE_DISPLAY_WIDTH + 10, 40))
        text = font.render(f"Beans Left: {beans_left}", True, BLACK)
        screen.blit(text, (MAZE_DISPLAY_WIDTH + 10, 70))

        pygame.draw.rect(screen, YELLOW, player.rect)
        for ghost in ghosts:
            pygame.draw.rect(screen, MAGENTA if ghost.frightened else RED, ghost.rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()