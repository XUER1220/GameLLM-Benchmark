import pygame
import random
import sys

pygame.init()
random.seed(42)

# 游戏常量
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_WIDTH, GRID_HEIGHT = 19, 21
CELL_SIZE = 24
MAZE_WIDTH = GRID_WIDTH * CELL_SIZE
MAZE_HEIGHT = GRID_HEIGHT * CELL_SIZE
MAZE_X = (SCREEN_WIDTH - MAZE_WIDTH) // 2 - 80
MAZE_Y = (SCREEN_HEIGHT - MAZE_HEIGHT) // 2
FPS = 60

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WALL_COLOR = (33, 33, 222)
PATH_COLOR = (0, 0, 0)
PLAYER_COLOR = (255, 255, 0)
GHOST_COLORS = [
    (255, 0, 0),     # 红
    (0, 255, 255),   # 青
    (255, 182, 255), # 粉
    (255, 184, 82)   # 橙
]
DOT_COLOR = (255, 255, 255)
ENERGY_DOT_COLOR = (255, 192, 203)
ENERGY_GHOST_COLOR = (0, 0, 255)
TEXT_COLOR = (255, 255, 255)

# 游戏参数
PLAYER_SPEED = 3
GHOST_SPEED = 2
ENERGY_DURATION = 6 * FPS  # 6秒
PLAYER_LIVES = 3
DOT_SCORE = 10
ENERGY_SCORE = 50
GHOST_SCORE = 200

# 迷宫定义
MAZE = [
    "###################",
    "#........#........#",
    "#.###.#.###.#.###.#",
    "#.................#",
    "#.###.#.###.#.###.#",
    "#.....#.....#.....#",
    "###.#.#.#.#.#.#.###",
    "  #.#.#.#.#.#.#.#  ",
    "###.#.#.#.#.#.#.###",
    "#........#........#",
    "#.###.#.###.#.###.#",
    "#....##.....##.....#",
    "###.#.###.###.#.###",
    "  #.#.........#.#  ",
    "###.#.### ###.#.###",
    "#........#........#",
    "#.###.#.###.#.###.#",
    "#.................#",
    "###################",
]

# 初始化迷宫数据
DOTS = []
ENERGY_DOTS = []
WALLS = []
GHOST_HOME = None
PLAYER_START = None

for y in range(GRID_HEIGHT):
    for x in range(GRID_WIDTH):
        char = MAZE[y][x]
        if char == '#':
            WALLS.append((x, y))
        elif char == '.':
            DOTS.append((x, y))
        elif char == 'O':
            ENERGY_DOTS.append((x, y))
        elif char == 'P':
            PLAYER_START = (x, y)
        elif char == 'G':
            GHOST_HOME = (x, y)

class Player:
    def __init__(self):
        self.x, self.y = PLAYER_START
        self.px = self.x * CELL_SIZE + MAZE_X
        self.py = self.y * CELL_SIZE + MAZE_Y
        self.dx, self.dy = 0, 0
        self.next_dx, self.next_dy = 0, 0
        self.radius = CELL_SIZE // 2 - 2

    def move(self):
        # 检查下一方向是否可行
        nx = self.x + self.next_dx
        ny = self.y + self.next_dy
        if (nx, ny) not in WALLS:
            self.dx, self.dy = self.next_dx, self.next_dy

        # 移动
        nx = self.x + self.dx
        ny = self.y + self.dy
        if (nx, ny) not in WALLS:
            self.x = nx
            self.y = ny
            self.px = self.x * CELL_SIZE + MAZE_X
            self.py = self.y * CELL_SIZE + MAZE_Y
        else:
            self.px += self.dx * PLAYER_SPEED
            self.py += self.dy * PLAYER_SPEED
            if abs(self.px - (self.x * CELL_SIZE + MAZE_X)) >= CELL_SIZE or abs(self.py - (self.y * CELL_SIZE + MAZE_Y)) >= CELL_SIZE:
                self.px = self.x * CELL_SIZE + MAZE_X
                self.py = self.y * CELL_SIZE + MAZE_Y

    def set_direction(self, dx, dy):
        if dx == -self.dx and dy == -self.dy:
            self.dx, self.dy = dx, dy
            self.next_dx, self.next_dy = 0, 0
        else:
            self.next_dx, self.next_dy = dx, dy

    def reset(self):
        self.__init__()

    def rect(self):
        return pygame.Rect(self.px - self.radius, self.py - self.radius, self.radius*2, self.radius*2)

class Ghost:
    def __init__(self, color_idx):
        self.x, self.y = GHOST_HOME
        self.px = self.x * CELL_SIZE + MAZE_X
        self.py = self.y * CELL_SIZE + MAZE_Y
        self.dx, self.dy = 0, 1
        self.color_idx = color_idx
        self.is_scared = False
        self.scared_timer = 0
        self.radius = CELL_SIZE // 2 - 2
        self.home_offset = color_idx * 2  # 区分出生位置

    def move(self, player_x, player_y):
        if self.is_scared:
            self.scared_timer -= 1
            if self.scared_timer <= 0:
                self.is_scared = False

        # 方向选择逻辑：尝试朝玩家方向移动
        directions = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx = self.x + dx
            ny = self.y + dy
            if (nx, ny) not in WALLS and not (dx == -self.dx and dy == -self.dy):
                directions.append((dx, dy))

        if not directions:
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx = self.x + dx
                ny = self.y + dy
                if (nx, ny) not in WALLS:
                    directions.append((dx, dy))

        best_dir = None
        if self.is_scared:
            # 受惊时远离玩家
            max_dist = -1
            for dx, dy in directions:
                nx, ny = self.x + dx, self.y + dy
                dist = (nx - player_x)**2 + (ny - player_y)**2
                if dist > max_dist:
                    max_dist = dist
                    best_dir = (dx, dy)
        else:
            # 普通状态接近玩家
            min_dist = float('inf')
            for dx, dy in directions:
                nx, ny = self.x + dx, self.y + dy
                dist = (nx - player_x)**2 + (ny - player_y)**2
                if dist < min_dist:
                    min_dist = dist
                    best_dir = (dx, dy)

        if best_dir:
            self.dx, self.dy = best_dir
            self.x += self.dx
            self.y += self.dy
            self.px = self.x * CELL_SIZE + MAZE_X
            self.py = self.y * CELL_SIZE + MAZE_Y

        # 隧道循环
        if self.x < 0:
            self.x = GRID_WIDTH - 1
        elif self.x >= GRID_WIDTH:
            self.x = 0
        self.px = self.x * CELL_SIZE + MAZE_X
        self.py = self.y * CELL_SIZE + MAZE_Y

    def set_scared(self):
        self.is_scared = True
        self.scared_timer = ENERGY_DURATION

    def reset(self):
        self.x = GHOST_HOME[0] + (self.home_offset % 3) - 1
        self.y = GHOST_HOME[1]
        self.px = self.x * CELL_SIZE + MAZE_X
        self.py = self.y * CELL_SIZE + MAZE_Y
        self.dx, self.dy = 0, 1
        self.is_scared = False
        self.scared_timer = 0

    def rect(self):
        return pygame.Rect(self.px - self.radius, self.py - self.radius, self.radius*2, self.radius*2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Man Medium")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.big_font = pygame.font.SysFont(None, 48)
        self.reset()

    def reset(self):
        self.player = Player()
        self.ghosts = [Ghost(i) for i in range(4)]
        self.dots = DOTS.copy()
        self.energy_dots = ENERGY_DOTS.copy()
        self.score = 0
        self.lives = PLAYER_LIVES
        self.game_over = False
        self.win = False

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
                if not self.game_over:
                    if event.key == pygame.K_UP:
                        self.player.set_direction(0, -1)
                    if event.key == pygame.K_DOWN:
                        self.player.set_direction(0, 1)
                    if event.key == pygame.K_LEFT:
                        self.player.set_direction(-1, 0)
                    if event.key == pygame.K_RIGHT:
                        self.player.set_direction(1, 0)

    def update(self):
        if self.game_over:
            return

        self.player.move()

        # 隧道循环
        if self.player.x < 0:
            self.player.x = GRID_WIDTH - 1
        elif self.player.x >= GRID_WIDTH:
            self.player.x = 0
        self.player.px = self.player.x * CELL_SIZE + MAZE_X
        self.player.py = self.player.y * CELL_SIZE + MAZE_Y

        # 吃豆子
        player_pos = (self.player.x, self.player.y)
        if player_pos in self.dots:
            self.dots.remove(player_pos)
            self.score += DOT_SCORE
        if player_pos in self.energy_dots:
            self.energy_dots.remove(player_pos)
            self.score += ENERGY_SCORE
            for ghost in self.ghosts:
                ghost.set_scared()

        # 幽灵移动
        for ghost in self.ghosts:
            ghost.move(self.player.x, self.player.y)

        # 碰撞检测
        player_rect = self.player.rect()
        for ghost in self.ghosts:
            ghost_rect = ghost.rect()
            if player_rect.colliderect(ghost_rect):
                if ghost.is_scared:
                    self.score += GHOST_SCORE
                    ghost.reset()
                else:
                    self.lives -= 1
                    self.player.reset()
                    for g in self.ghosts:
                        g.reset()
                    if self.lives <= 0:
                        self.game_over = True
                    break

        # 胜利条件
        if not self.dots and not self.energy_dots:
            self.win = True
            self.game_over = True

    def draw(self):
        self.screen.fill(BLACK)

        # 绘制迷宫
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * CELL_SIZE + MAZE_X, y * CELL_SIZE + MAZE_Y, CELL_SIZE, CELL_SIZE)
                if MAZE[y][x] == '#':
                    pygame.draw.rect(self.screen, WALL_COLOR, rect)
                else:
                    pygame.draw.rect(self.screen, PATH_COLOR, rect)

        # 绘制豆子
        for x, y in self.dots:
            center = (x * CELL_SIZE + MAZE_X + CELL_SIZE//2, y * CELL_SIZE + MAZE_Y + CELL_SIZE//2)
            pygame.draw.circle(self.screen, DOT_COLOR, center, 3)
        for x, y in self.energy_dots:
            center = (x * CELL_SIZE + MAZE_X + CELL_SIZE//2, y * CELL_SIZE + MAZE_Y + CELL_SIZE//2)
            pygame.draw.circle(self.screen, ENERGY_DOT_COLOR, center, 6)

        # 绘制幽灵
        for ghost in self.ghosts:
            color = ENERGY_GHOST_COLOR if ghost.is_scared else GHOST_COLORS[ghost.color_idx]
            pygame.draw.circle(self.screen, color, (int(ghost.px), int(ghost.py)), ghost.radius)

        # 绘制玩家
        pygame.draw.circle(self.screen, PLAYER_COLOR, (int(self.player.px), int(self.player.py)), self.player.radius)

        # HUD
        hud_x = MAZE_X + MAZE_WIDTH + 20
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        lives_text = self.font.render(f"Lives: {self.lives}", True, TEXT_COLOR)
        dots_text = self.font.render(f"Dots Left: {len(self.dots)+len(self.energy_dots)}", True, TEXT_COLOR)
        self.screen.blit(score_text, (hud_x, 100))
        self.screen.blit(lives_text, (hud_x, 140))
        self.screen.blit(dots_text, (hud_x, 180))

        # 游戏结束提示
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            if self.win:
                text = self.big_font.render("You Win!", True, TEXT_COLOR)
            else:
                text = self.big_font.render("Game Over", True, TEXT_COLOR)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(text, text_rect)
            score_text = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(score_text, score_rect)
            restart_text = self.font.render("Press R to Restart", True, TEXT_COLOR)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(restart_text, restart_rect)

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