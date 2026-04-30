import pygame
import random
import sys

# 初始化 pygame
pygame.init()
random.seed(42)

# 常量定义
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_ROWS, GRID_COLS = 21, 19
CELL_SIZE = 24
MAP_WIDTH, MAP_HEIGHT = GRID_COLS * CELL_SIZE, GRID_ROWS * CELL_SIZE
OFFSET_X = (SCREEN_WIDTH - MAP_WIDTH) // 2
OFFSET_Y = (SCREEN_HEIGHT - MAP_HEIGHT) // 2
FPS = 60
PLAYER_SPEED = 3
GHOST_SPEED = 2
ENERGY_DURATION = 360  # 6 秒 * 60 FPS

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)

# UI 字体
FONT = pygame.font.SysFont(None, 32)
BIG_FONT = pygame.font.SysFont(None, 72)

# 迷宫地图（0:空地,1:墙,2:豆子,3:能量豆,4:玩家出生点,5:幽灵出生点）
# 19列 x 21行
MAP_LAYOUT = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,3,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,3,1],
    [1,0,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,0,1],
    [1,0,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,0,1],
    [1,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,1],
    [1,1,1,1,0,1,1,1,4,1,4,1,1,1,0,1,1,1,1],
    [1,0,0,0,0,1,4,5,5,5,5,5,4,1,0,0,0,0,1],
    [1,1,1,1,0,1,4,1,1,5,1,1,4,1,0,1,1,1,1],
    [1,0,0,0,0,0,0,1,4,5,4,1,0,0,0,0,0,0,1],
    [1,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,0,1],
    [1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1],
    [1,1,0,1,0,1,0,1,1,1,1,1,0,1,0,1,0,1,1],
    [1,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,0,1,0,1,1,1,1,1,1,0,1],
    [1,3,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,3,1],
    [1,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,1]
]

# 移动方向枚举
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0, 0)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        self.total_dots = 0
        self.remaining_dots = 0
        self.dots_map = []
        self.energizers_map = []
        self.walls = []
        self.ghost_spawns = []
        self.player_spawn = None
        self.player = Player(*self._find_player_spawn())
        self.ghosts = []
        self.parse_map()
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.game_won = False
        self.energizer_active = False
        self.energizer_timer = 0

    def _find_player_spawn(self):
        for y, row in enumerate(MAP_LAYOUT):
            for x, cell in enumerate(row):
                if cell == 4:
                    return x, y
        return 9, 10  # fallback

    def parse_map(self):
        self.walls = []
        self.ghost_spawns = []
        self.energizers = []
        self.dots = []
        self.player_spawn = self._find_player_spawn()
        
        # 重新生成对象
        self.dots_map = [[0]*GRID_COLS for _ in range(GRID_ROWS)]
        self.energizers_map = [[False]*GRID_COLS for _ in range(GRID_ROWS)]
        self.total_dots = 0
        self.remaining_dots = 0
        
        for y in range(GRID_ROWS):
            row_dots = [0]*GRID_COLS
            row_energizers = [False]*GRID_COLS
            for x in range(GRID_COLS):
                cell = MAP_LAYOUT[y][x]
                if cell == 1:
                    self.walls.append((x, y))
                elif cell == 2:
                    row_dots[x] = 1
                    self.total_dots += 1
                    self.remaining_dots += 1
                elif cell == 3:
                    row_energizers[x] = True
                    self.energizers.append((x, y))
                elif cell == 4:
                    self.player_spawn = (x, y)
                elif cell == 5:
                    self.ghost_spawns.append((x, y))
            self.dots_map.append(row_dots)
            self.energizers_map.append(row_energizers)

        # 初始化幽灵
        self.ghosts = [
            Ghost(self.ghost_spawns[0][0], self.ghost_spawns[0][1], RED),
            Ghost(self.ghost_spawns[1][0], self.ghost_spawns[1][1], PINK),
            Ghost(self.ghost_spawns[2][0], self.ghost_spawns[2][1], CYAN),
            Ghost(self.ghost_spawns[3][0], self.ghost_spawns[3][1], ORANGE)
        ]

    def update(self):
        if self.game_over or self.game_won:
            return

        # 更新玩家
        self.player.update(self.walls)

        # 检查吃豆子
        px, py = self.player.x // CELL_SIZE, self.player.y // CELL_SIZE
        # 检查普通豆子
        if 0 <= py < GRID_ROWS and 0 <= px < GRID_COLS and self.dots_map[py][px] == 1:
            self.dots_map[py][px] = 0
            self.score += 10
            self.remaining_dots -= 1
        # 检查能量豆
        if 0 <= py < GRID_ROWS and 0 <= px < GRID_COLS and self.energizers_map[py][px]:
            self.energizers_map[py][px] = False
            self.score += 50
            self.energizer_active = True
            self.energizer_timer = ENERGY_DURATION
            for ghost in self.ghosts:
                ghost.is_scared = True

        # 更新能量状态计时器
        if self.energizer_active:
            self.energizer_timer -= 1
            if self.energizer_timer <= 0:
                self.energizer_active = False
                for ghost in self.ghosts:
                    ghost.is_scared = False

        # 更新幽灵
        for ghost in self.ghosts:
            ghost.update(self.walls, self.player, self.energizer_active)

        # 检查与幽灵碰撞
        for ghost in self.ghosts:
            if self.check_collision(self.player, ghost):
                if self.energizer_active and ghost.is_scared:
                    ghost.respawn()
                    self.score += 200
                else:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        self.reset_positions()

        # 检查胜利
        if self.remaining_dots == 0:
            self.game_won = True

    def check_collision(self, player, ghost):
        dx = abs(player.x - ghost.x)
        dy = abs(player.y - ghost.y)
        return dx < CELL_SIZE // 2 and dy < CELL_SIZE // 2

    def reset_positions(self):
        self.player.respawn()
        for ghost in self.ghosts:
            ghost.respawn()

    def draw(self):
        self.screen.fill(BLACK)

        # 绘制迷宫
        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                px = OFFSET_X + x * CELL_SIZE
                py = OFFSET_Y + y * CELL_SIZE
                cell = MAP_LAYOUT[y][x]
                if cell == 1:  # 墙体
                    pygame.draw.rect(self.screen, BLUE, (px, py, CELL_SIZE, CELL_SIZE))
                elif cell == 2 or (self.dots_map[y][x] == 1):  # 普通豆子
                    pygame.draw.circle(self.screen, WHITE,
                                       (px + CELL_SIZE // 2, py + CELL_SIZE // 2), 3)
                elif cell == 3 and self.energizers_map[y][x]:  # 能量豆
                    pygame.draw.circle(self.screen, YELLOW,
                                       (px + CELL_SIZE // 2, py + CELL_SIZE // 2), 8)

        # 绘制玩家
        self.player.draw(self.screen)

        # 绘制幽灵
        for ghost in self.ghosts:
            ghost.draw(self.screen)

        # HUD
        hud_x = OFFSET_X + MAP_WIDTH + 20
        FONT = pygame.font.SysFont(None, 32)
        text = FONT.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(text, (hud_x, OFFSET_Y + 20))
        text = FONT.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(text, (hud_x, OFFSET_Y + 60))
        text = FONT.render(f"Dots: {self.remaining_dots}", True, WHITE)
        self.screen.blit(text, (hud_x, OFFSET_Y + 100))

        # 游戏结束/胜利画面
        if self.game_won:
            text = BIG_FONT.render("YOU WIN!", True, GREEN)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, OFFSET_Y + MAP_HEIGHT // 2 - 50))
            self.screen.blit(text, rect)
            text = FONT.render(f"Final Score: {self.score}", True, WHITE)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, OFFSET_Y + MAP_HEIGHT // 2 + 20))
            self.screen.blit(text, rect)
            text = FONT.render("Press R to Restart", True, WHITE)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, OFFSET_Y + MAP_HEIGHT // 2 + 60))
            self.screen.blit(text, rect)
        elif self.game_over:
            text = BIG_FONT.render("GAME OVER", True, RED)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, OFFSET_Y + MAP_HEIGHT // 2 - 50))
            self.screen.blit(text, rect)
            text = FONT.render(f"Final Score: {self.score}", True, WHITE)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, OFFSET_Y + MAP_HEIGHT // 2 + 20))
            self.screen.blit(text, rect)
            text = FONT.render("Press R to Restart", True, WHITE)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, OFFSET_Y + MAP_HEIGHT // 2 + 60))
            self.screen.blit(text, rect)

        pygame.display.flip()


class Player:
    def __init__(self, x, y):
        self.start_x = x * CELL_SIZE + CELL_SIZE // 2
        self.start_y = y * CELL_SIZE + CELL_SIZE // 2
        self.respawn()
        self.dir = STOP
        self.next_dir = STOP

    def respawn(self):
        self.x = self.start_x
        self.y = self.start_y
        self.dir = STOP
        self.next_dir = STOP

    def update(self, walls):
        # 尝试转向
        if self.next_dir != STOP:
            # 检查是否可以转向
            if self._can_move(self.next_dir, walls):
                self.dir = self.next_dir
                self.next_dir = STOP
        # 移动
        if self.dir != STOP:
            if self._can_move(self.dir, walls):
                self.x += self.dir[0] * PLAYER_SPEED
                self.y += self.dir[1] * PLAYER_SPEED
                # 隧道处理（左右贯通）
                if self.x < 0:
                    self.x = SCREEN_WIDTH
                elif self.x > SCREEN_WIDTH:
                    self.x = 0

    def _can_move(self, direction, walls):
        # 确保移动后不会撞墙
        x = self.x + direction[0] * (CELL_SIZE // 2 + 1)
        y = self.y + direction[1] * (CELL_SIZE // 2 + 1)
        bx = int(x // CELL_SIZE)
        by = int(y // CELL_SIZE)
        if 0 <= by < GRID_ROWS and 0 <= bx < GRID_COLS:
            if MAP_LAYOUT[by][bx] == 1:
                return False
        # 边界检查（防止出界）
        if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
            return True
        return False

    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), 10)


class Ghost:
    def __init__(self, x, y, color):
        self.start_x = x * CELL_SIZE + CELL_SIZE // 2
        self.start_y = y * CELL_SIZE + CELL_SIZE // 2
        self.color = color
        self.respawn()

    def respawn(self):
        self.x = self.start_x
        self.y = self.start_y
        self.dir = random.choice([UP, DOWN, LEFT, RIGHT])
        self.is_scared = False

    def update(self, walls, player, energizer_active):
        # 检查是否到达交叉点（网格中心）
        if self._is_at_intersection():
            # 选择方向
            self._choose_direction(walls, player, energizer_active)

        # 移动 (较慢)
        self.x += self.dir[0] * GHOST_SPEED
        self.y += self.dir[1] * GHOST_SPEED
        
        # 隧道处理（左右贯通）
        if self.x < 0:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0

    def _is_at_intersection(self):
        # 判断是否在网格中心点附近
        return (self.x % CELL_SIZE == CELL_SIZE // 2 and 
                self.y % CELL_SIZE == CELL_SIZE // 2)

    def _choose_direction(self, walls, player, energizer_active):
        possible_dirs = []
        for d in [UP, DOWN, LEFT, RIGHT]:
            if d == (-self.dir[0], -self.dir[1]):  # 不能原路返回
                continue
            nx = (self.x + d[0] * (CELL_SIZE // 2 + 1)) // CELL_SIZE
            ny = (self.y + d[1] * (CELL_SIZE // 2 + 1)) // CELL_SIZE
            if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS:
                if MAP_LAYOUT[ny][nx] != 1:
                    possible_dirs.append(d)
        
        if not possible_dirs:
            possible_dirs = [(-self.dir[0], -self.dir[1])]

        # 选择方向
        if energizer_active and self.is_scared:
            # 随机移动（逃窜模式）
            self.dir = random.choice(possible_dirs)
        else:
            # 追逐模式：优先朝玩家方向移动
            best_dir = None
            min_dist = float('inf')
            px, py = player.x // CELL_SIZE, player.y // CELL_SIZE
            for d in possible_dirs:
                nx = (self.x + d[0] * CELL_SIZE) // CELL_SIZE
                ny = (self.y + d[1] * CELL_SIZE) // CELL_SIZE
                dist = abs(nx - px) + abs(ny - py)
                if dist < min_dist:
                    min_dist = dist
                    best_dir = d
            if best_dir:
                self.dir = best_dir
            else:
                self.dir = random.choice(possible_dirs)

    def draw(self, screen):
        color = (100, 100, 255) if self.is_scared else self.color
        # 绘制幽灵身体
        radius = 10
        center = (int(self.x), int(self.y))
        pygame.draw.circle(screen, color, center, radius)
        # 眼睛
        if not self.is_scared:
            eye_offset = 3
            pygame.draw.circle(screen, WHITE, (center[0] - eye_offset, center[1] - 2), 3)
            pygame.draw.circle(screen, WHITE, (center[0] + eye_offset, center[1] - 2), 3)
            pygame.draw.circle(screen, BLACK, (center[0] - eye_offset, center[1] - 2), 1.5)
            pygame.draw.circle(screen, BLACK, (center[0] + eye_offset, center[1] - 2), 1.5)
        else:
            # 可怕幽灵的嘴
            pygame.draw.arc(screen, WHITE, (center[0] - 8, center[1] - 5, 16, 8), 3.14, 6.28, 1)


def main():
    game = Game()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and (game.game_over or game.game_won):
                    game.reset_game()
                elif not game.game_over and not game.game_won:
                    if event.key == pygame.K_UP:
                        game.player.next_dir = UP
                    elif event.key == pygame.K_DOWN:
                        game.player.next_dir = DOWN
                    elif event.key == pygame.K_LEFT:
                        game.player.next_dir = LEFT
                    elif event.key == pygame.K_RIGHT:
                        game.player.next_dir = RIGHT

        game.update()
        game.draw()
        game.clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()