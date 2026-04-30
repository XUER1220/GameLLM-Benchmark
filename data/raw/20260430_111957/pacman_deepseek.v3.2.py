import pygame, sys, random

pygame.init()
random.seed(42)

# 常量定义
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
MAZE_COLS, MAZE_ROWS = 19, 21
CELL_SIZE = 24
MAZE_DISPLAY_W = MAZE_COLS * CELL_SIZE
MAZE_DISPLAY_H = MAZE_ROWS * CELL_SIZE
MAZE_OFFSET_X = (SCREEN_WIDTH - MAZE_DISPLAY_W - 200) // 2
MAZE_OFFSET_Y = (SCREEN_HEIGHT - MAZE_DISPLAY_H) // 2
HUD_OFFSET_X = MAZE_OFFSET_X + MAZE_DISPLAY_W + 20

PLAYER_SPEED = 3
GHOST_SPEED = 2
POWER_DURATION = 6 * FPS
LIVES = 3

COLOR_BG = (0, 0, 0)
COLOR_WALL = (33, 33, 222)
COLOR_PATH = (0, 0, 0)
COLOR_DOT = (255, 255, 255)
COLOR_POWER_DOT = (255, 255, 0)
COLOR_PLAYER = (255, 255, 0)
COLOR_TEXT = (255, 255, 255)
GHOST_COLORS = [
    (255, 0, 0),    # 红
    (255, 184, 255),# 粉
    (0, 255, 255),  # 青
    (255, 184, 82)  # 橙
]

SCORE_DOT = 10
SCORE_POWER = 50
SCORE_GHOST = 200

# 迷宫定义 (W=墙,  .=豆子,  P=玩家出生, G=幽灵出生,  ' '=通路,  o=能量豆)
MAZE = [
    "WWWWWWWWWWWWWWWWWWW",
    "W.........W........W",
    "W.WWW.WWW.W.WWW.WW.W",
    "Wo..........o......W",
    "W.WWW.W.WWWWW.W.WW.W",
    "W....W....W...W....W",
    "WWWW.WWWW.W.WWW.WWWW",
    "   W.W.....W....W   ",
    "WWWW.W.WWWWWWWW.WWWW",
    "   .....   G   .....",
    "WWWW.W.WWWWWWWW.WWWW",
    "   W.W.....W....W   ",
    "WWWW.W.WWW.W.WWW.WWW",
    "W.........W........W",
    "W.WWW.WWW.W.WWW.WW.W",
    "Wo..........o......W",
    "W.WW.W.WWWWW.W.WWW.W",
    "W....W....W...W....W",
    "WWWW.WWWW.W.WWW.WWWW",
    "W.................P.W",
    "WWWWWWWWWWWWWWWWWWW"
]

# 初始化 Pygame
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.score = 0
        self.lives = LIVES
        self.dots_left = 0
        self.power_timer = 0
        self.running = True
        self.win = False
        self.game_over = False
        self.maze_grid = []
        self.player = None
        self.ghosts = []
        self.load_maze()

    def load_maze(self):
        self.maze_grid = []
        self.dots_left = 0
        for y in range(MAZE_ROWS):
            row = []
            for x in range(MAZE_COLS):
                cell_char = MAZE[y][x]
                if cell_char == 'W':
                    row.append('W')
                elif cell_char == ' ':
                    row.append(' ')
                elif cell_char == '.':
                    row.append('.')
                    self.dots_left += 1
                elif cell_char == 'o':
                    row.append('o')
                    self.dots_left += 1
                elif cell_char == 'P':
                    row.append(' ')
                    self.player = Player(x, y)
                elif cell_char == 'G':
                    row.append(' ')
                    self.ghosts.append(Ghost(x, y, len(self.ghosts)))
                else:
                    row.append(' ')
            self.maze_grid.append(row)

    def update(self):
        if not self.running:
            return
        self.player.update(self.maze_grid)
        if self.player.eat_dot(self.maze_grid):
            self.score += SCORE_DOT
            self.dots_left -= 1
        if self.player.eat_power(self.maze_grid):
            self.score += SCORE_POWER
            self.dots_left -= 1
            self.power_timer = POWER_DURATION
        for ghost in self.ghosts:
            ghost.update(self.maze_grid, self.player)
            if self.power_timer > 0:
                if self.player.collide_with(ghost):
                    ghost.reset()
                    self.score += SCORE_GHOST
            else:
                if self.player.collide_with(ghost):
                    self.lives -= 1
                    self.player.reset()
                    for g in self.ghosts:
                        g.reset()
                    if self.lives <= 0:
                        self.game_over = True
                        self.running = False
                    break
        if self.power_timer > 0:
            self.power_timer -= 1
        if self.dots_left <= 0:
            self.win = True
            self.running = False

    def draw(self):
        screen.fill(COLOR_BG)
        for y in range(MAZE_ROWS):
            for x in range(MAZE_COLS):
                rect = pygame.Rect(
                    MAZE_OFFSET_X + x * CELL_SIZE,
                    MAZE_OFFSET_Y + y * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                cell = self.maze_grid[y][x]
                if cell == 'W':
                    pygame.draw.rect(screen, COLOR_WALL, rect)
                elif cell == '.':
                    pygame.draw.circle(screen, COLOR_DOT,
                                       rect.center, 4)
                elif cell == 'o':
                    pygame.draw.circle(screen, COLOR_POWER_DOT,
                                       rect.center, 8)
        for ghost in self.ghosts:
            ghost.draw(screen)
        self.player.draw(screen)
        self.draw_hud()

    def draw_hud(self):
        hud_x = HUD_OFFSET_X
        score_text = font.render(f"Score: {self.score}", True, COLOR_TEXT)
        lives_text = font.render(f"Lives: {self.lives}", True, COLOR_TEXT)
        dots_text = font.render(f"Dots Left: {self.dots_left}", True, COLOR_TEXT)
        power_text = font.render(f"Power: {self.power_timer // FPS}s", True, COLOR_TEXT)
        screen.blit(score_text, (hud_x, 100))
        screen.blit(lives_text, (hud_x, 150))
        screen.blit(dots_text, (hud_x, 200))
        screen.blit(power_text, (hud_x, 250))
        if self.win or self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            result = "You Win!" if self.win else "Game Over"
            result_surf = font.render(result, True, COLOR_TEXT)
            score_surf = font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
            restart_surf = font.render("Press R to Restart", True, COLOR_TEXT)
            screen.blit(result_surf,
                        (SCREEN_WIDTH//2 - result_surf.get_width()//2, SCREEN_HEIGHT//2 - 60))
            screen.blit(score_surf,
                        (SCREEN_WIDTH//2 - score_surf.get_width()//2, SCREEN_HEIGHT//2 - 20))
            screen.blit(restart_surf,
                        (SCREEN_WIDTH//2 - restart_surf.get_width()//2, SCREEN_HEIGHT//2 + 20))

class Player:
    def __init__(self, x, y):
        self.start_x = x
        self.start_y = y
        self.reset()

    def reset(self):
        self.x = self.start_x * CELL_SIZE + CELL_SIZE // 2
        self.y = self.start_y * CELL_SIZE + CELL_SIZE // 2
        self.dx = 0
        self.dy = 0
        self.next_dx = 0
        self.next_dy = 0

    def update(self, maze_grid):
        keys = pygame.key.get_pressed()
        self.next_dx, self.next_dy = 0, 0
        if keys[pygame.K_LEFT]:
            self.next_dx = -PLAYER_SPEED
        elif keys[pygame.K_RIGHT]:
            self.next_dx = PLAYER_SPEED
        elif keys[pygame.K_UP]:
            self.next_dy = -PLAYER_SPEED
        elif keys[pygame.K_DOWN]:
            self.next_dy = PLAYER_SPEED
        if self.can_move(self.next_dx, self.next_dy, maze_grid):
            self.dx, self.dy = self.next_dx, self.next_dy
        if not self.can_move(self.dx, self.dy, maze_grid):
            self.dx, self.dy = 0, 0
        self.x += self.dx
        self.y += self.dy
        self.handle_tunnel()

    def can_move(self, dx, dy, grid):
        check_x = self.x + dx
        check_y = self.y + dy
        grid_x = int((check_x) // CELL_SIZE)
        grid_y = int((check_y) // CELL_SIZE)
        if 0 <= grid_x < MAZE_COLS and 0 <= grid_y < MAZE_ROWS:
            return grid[grid_y][grid_x] != 'W'
        return False

    def handle_tunnel(self):
        if self.x < 0:
            self.x = MAZE_DISPLAY_W
        elif self.x > MAZE_DISPLAY_W:
            self.x = 0

    def eat_dot(self, grid):
        grid_x = int(self.x // CELL_SIZE)
        grid_y = int(self.y // CELL_SIZE)
        if grid[grid_y][grid_x] == '.':
            grid[grid_y][grid_x] = ' '
            return True
        return False

    def eat_power(self, grid):
        grid_x = int(self.x // CELL_SIZE)
        grid_y = int(self.y // CELL_SIZE)
        if grid[grid_y][grid_x] == 'o':
            grid[grid_y][grid_x] = ' '
            return True
        return False

    def collide_with(self, ghost):
        px, py = int(self.x // CELL_SIZE), int(self.y // CELL_SIZE)
        gx, gy = int(ghost.x // CELL_SIZE), int(ghost.y // CELL_SIZE)
        return px == gx and py == gy

    def draw(self, screen):
        center = (MAZE_OFFSET_X + self.x, MAZE_OFFSET_Y + self.y)
        pygame.draw.circle(screen, COLOR_PLAYER, center, CELL_SIZE // 2 - 2)

class Ghost:
    def __init__(self, x, y, index):
        self.start_x = x
        self.start_y = y
        self.color = GHOST_COLORS[index % len(GHOST_COLORS)]
        self.reset()

    def reset(self):
        self.x = self.start_x * CELL_SIZE + CELL_SIZE // 2
        self.y = self.start_y * CELL_SIZE + CELL_SIZE // 2
        self.direction = random.choice([(1,0), (-1,0), (0,1), (0,-1)])

    def update(self, grid, player):
        possible_dirs = []
        target_x, target_y = int(player.x // CELL_SIZE), int(player.y // CELL_SIZE)
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            if (dx, dy) != (-self.direction[0], -self.direction[1]):
                if self.can_move(dx, dy, grid):
                    possible_dirs.append((dx, dy))
        if not possible_dirs:
            self.direction = (-self.direction[0], -self.direction[1])
            possible_dirs = [self.direction]
        best_dir = None
        min_dist = float('inf')
        for dx, dy in possible_dirs:
            new_grid_x = int((self.x + dx * GHOST_SPEED) // CELL_SIZE)
            new_grid_y = int((self.y + dy * GHOST_SPEED) // CELL_SIZE)
            dist = abs(new_grid_x - target_x) + abs(new_grid_y - target_y)
            if dist < min_dist:
                min_dist = dist
                best_dir = (dx, dy)
        if best_dir:
            self.direction = best_dir
        self.x += self.direction[0] * GHOST_SPEED
        self.y += self.direction[1] * GHOST_SPEED
        self.handle_tunnel()

    def can_move(self, dx, dy, grid):
        check_x = self.x + dx * GHOST_SPEED
        check_y = self.y + dy * GHOST_SPEED
        grid_x = int(check_x // CELL_SIZE)
        grid_y = int(check_y // CELL_SIZE)
        if 0 <= grid_x < MAZE_COLS and 0 <= grid_y < MAZE_ROWS:
            return grid[grid_y][grid_x] != 'W'
        return False

    def handle_tunnel(self):
        if self.x < 0:
            self.x = MAZE_DISPLAY_W
        elif self.x > MAZE_DISPLAY_W:
            self.x = 0

    def draw(self, screen):
        center = (MAZE_OFFSET_X + self.x, MAZE_OFFSET_Y + self.y)
        pygame.draw.circle(screen, self.color, center, CELL_SIZE // 2 - 2)

def main():
    game = Game()
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
                    game.reset()
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()