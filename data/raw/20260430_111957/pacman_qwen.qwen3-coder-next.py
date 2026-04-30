import pygame
import random
import sys

# 初始化
pygame.init()

# 固定参数
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 24
MAP_COLS = 19
MAP_ROWS = 21
GAME_WIDTH = TILE_SIZE * MAP_COLS
GAME_HEIGHT = TILE_SIZE * MAP_ROWS
X_OFFSET = (SCREEN_WIDTH - GAME_WIDTH) // 2 - 4  # 居中偏左
Y_OFFSET = (SCREEN_HEIGHT - GAME_HEIGHT) // 2

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
LIGHT_BROWN = (210, 180, 140)

# 方向定义
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0, 0)

# 固定迷宫: '#' 墙, '.' 普通豆, 'O' 能量豆, 'P' 玩家, 'G1' 'G2' 'G3' 'G4' 幽灵出生点, ' ' 通路
# 使用 19x21 迷宫
maze_layout = [
    "###################",
    "#...#...#...#...#..",
    "#.###.#.#.#.#.###.#",
    "#o#...#.#.#.#...#o#",
    "#.###.#.#.#.#.###.#",
    "#...#.......#...#.#",
    "#.###.#.###.#.###.#",
    "#...#.#.#.#.#...#.#",
    "#.###.#.#.#.#.###.#",
    "#...#.......#...#.#",
    "#.###.#.###.#.###.#",
    "#...#.#.#.#.#...#.#",
    "#.###.#.#.#.#.###.#",
    "#o..#...#...#..o#.#",
    "#.###.#.#.#.#.###.#",
    "#...#.......#...#.#",
    "#.###.#.###.#.###.#",
    "#...#.#.#.#.#...#.#",
    "#.###.#.#.#.#.###.#",
    "#...#...#...#...#P#",
    "###################"
]

# 修正迷宫：确保长度正确
maze = [list(row) for row in maze_layout]
for i, row in enumerate(maze):
    while len(row) < MAP_COLS:
        row.append('#')
    while len(row) > MAP_COLS:
        row.pop()

# 寻找出生点
player_start = None
ghost_spawns = []
for r in range(MAP_ROWS):
    for c in range(MAP_COLS):
        if maze[r][c] == 'P':
            player_start = (c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2)
            maze[r][c] = '.'
        elif maze[r][c] in ['G1', 'G2', 'G3', 'G4']:
            ghost_spawns.append((c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2))
            maze[r][c] = '.'

# 如果没有找到出生点，创建默认
if not player_start:
    player_start = (10 * TILE_SIZE + TILE_SIZE // 2, 17 * TILE_SIZE + TILE_SIZE // 2)
if not ghost_spawns:
    ghost_spawns = [(10 * TILE_SIZE + TILE_SIZE // 2, 10 * TILE_SIZE + TILE_SIZE // 2)] * 4
while len(ghost_spawns) < 4:
    ghost_spawns.append(ghost_spawns[-1])

# 能量豆位置
energy_dots_pos = []
for r in range(MAP_ROWS):
    for c in range(MAP_COLS):
        if maze[r][c] == 'o':
            energy_dots_pos.append((c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2))

# 随机种子
random.seed(42)

# 菜单文本字体
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)


def check_collision(rect, direction):
    """检查在指定方向上是否碰撞墙体"""
    dx, dy = direction
    next_x = rect.x + dx * TILE_SIZE
    next_y = rect.y + dy * TILE_SIZE
    rect_test = pygame.Rect(next_x, next_y, TILE_SIZE, TILE_SIZE)
    # 检查四角是否在墙内
    corners = [
        (rect_test.left + 2, rect_test.top + 2),
        (rect_test.right - 2, rect_test.top + 2),
        (rect_test.left + 2, rect_test.bottom - 2),
        (rect_test.right - 2, rect_test.bottom - 2)
    ]
    for x, y in corners:
        c = x // TILE_SIZE
        r = y // TILE_SIZE
        if 0 <= r < MAP_ROWS and 0 <= c < MAP_COLS:
            if maze[r][c] == '#':
                return True
    return False


def is_tile_in_wall(x, y):
    c = x // TILE_SIZE
    r = y // TILE_SIZE
    if 0 <= r < MAP_ROWS and 0 <= c < MAP_COLS:
        return maze[r][c] == '#'
    return True


def get_valid_directions(rect, current_dir=STOP):
    directions = [UP, DOWN, LEFT, RIGHT]
    valid = []
    for d in directions:
        if d == STOP:
            continue
        # 检查反方向（除非正在反方向上移动）
        if d[0] == -current_dir[0] and d[1] == -current_dir[1]:
            # 允许立即转弯，不阻止反方向
            pass
        if not check_collision(rect, d):
            valid.append(d)
    return valid


class Pacman:
    def __init__(self):
        self.x, self.y = player_start
        self.rect = pygame.Rect(self.x - TILE_SIZE // 2, self.y - TILE_SIZE // 2, TILE_SIZE, TILE_SIZE)
        self.direction = STOP
        self.next_direction = STOP
        self.speed = 3
        self.radius = TILE_SIZE // 2 - 2
        self.score = 0
        self.lives = 3
        self.mouth_open = 0
        self.mouth_direction = 1
        self.mouth_angle = 0.2

    def reset_position(self):
        self.x, self.y = player_start
        self.rect = pygame.Rect(self.x - TILE_SIZE // 2, self.y - TILE_SIZE // 2, TILE_SIZE, TILE_SIZE)
        self.direction = STOP
        self.next_direction = STOP

    def update(self):
        if self.next_direction != STOP and not check_collision(self.rect, self.next_direction):
            self.direction = self.next_direction
            self.next_direction = STOP

        dx, dy = self.direction
        if dx != 0 or dy != 0:
            if not check_collision(self.rect, self.direction):
                self.x += dx * self.speed
                self.y += dy * self.speed

        self.rect.x = int(self.x - TILE_SIZE // 2)
        self.rect.y = int(self.y - TILE_SIZE // 2)

        # 隧道处理
        if self.rect.left > GAME_WIDTH + X_OFFSET - TILE_SIZE:
            self.rect.right = X_OFFSET
        elif self.rect.right < X_OFFSET:
            self.rect.left = GAME_WIDTH + X_OFFSET

        # 更新嘴巴动画
        self.mouth_angle += 0.1 * self.mouth_direction
        if self.mouth_angle > 0.25 * 3.14159 or self.mouth_angle < 0.25 * 0.2:
            self.mouth_direction = -self.mouth_direction

    def draw(self, screen):
        # 绘制吃豆人
        angle = 0
        if self.direction == UP:
            angle = -1.5708
        elif self.direction == DOWN:
            angle = 1.5708
        elif self.direction == LEFT:
            angle = 3.14159
        elif self.direction == RIGHT:
            angle = 0
        mouth = self.mouth_angle
        points = []
        cx, cy = self.x, self.y
        for i in range(3):
            if i == 0:
                points.append(
                    (cx + self.radius * (0.9 * 0.5 * mouth * 2), cy + self.radius * (0.5 * mouth * 2)))
            elif i == 1:
                points.append(
                    (cx + self.radius * (0.9 * 0.5 * mouth * 2), cy - self.radius * (0.5 * mouth * 2)))
            else:
                points.append((cx, cy))
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)
        if self.direction != STOP:
            mouth_points = [
                (cx + self.radius * 0.9 * 0.5 * mouth * 2, cy + self.radius * 0.9 * (0.5 * mouth * 2)),
                (cx, cy),
                (cx + self.radius * 0.9 * 0.5 * mouth * 2, cy - self.radius * 0.9 * (0.5 * mouth * 2))
            ]
            if self.direction == UP:
                mouth_points = [
                    (cx + self.radius * 0.9 * (0.5 * mouth * 2), cy - self.radius * 0.9 * 0.5 * mouth * 2),
                    (cx, cy),
                    (cx - self.radius * 0.9 * (0.5 * mouth * 2), cy - self.radius * 0.9 * 0.5 * mouth * 2)
                ]
            elif self.direction == LEFT:
                mouth_points = [
                    (cx - self.radius * 0.9 * (0.5 * mouth * 2), cy - self.radius * 0.9 * 0.5 * mouth * 2),
                    (cx, cy),
                    (cx - self.radius * 0.9 * (0.5 * mouth * 2), cy + self.radius * 0.9 * 0.5 * mouth * 2)
                ]
            elif self.direction == DOWN:
                mouth_points = [
                    (cx - self.radius * 0.9 * (0.5 * mouth * 2), cy + self.radius * 0.9 * 0.5 * mouth * 2),
                    (cx, cy),
                    (cx + self.radius * 0.9 * (0.5 * mouth * 2), cy + self.radius * 0.9 * 0.5 * mouth * 2)
                ]
            pygame.draw.polygon(screen, BLACK, mouth_points)


class Ghost:
    def __init__(self, x, y, color, spawn_x, spawn_y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x - TILE_SIZE // 2, self.y - TILE_SIZE // 2, TILE_SIZE, TILE_SIZE)
        self.original_color = color
        self.color = color
        self.speed = 2
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.spawn_x = spawn_x
        self.spawn_y = spawn_y
        self.is_frightened = False
        self.frightened_timer = 0
        self.eaten = False
        self.target_direction = None

    def update(self, player, dt):
        # 检查是否在出生点附近，如果是则离开
        if self.x == self.spawn_x and self.y == self.spawn_y and self.direction == STOP:
            self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

        # 移动幽灵
        dx, dy = self.direction
        self.x += dx * self.speed
        self.y += dy * self.speed

        # 隧道处理
        if self.rect.left > GAME_WIDTH + X_OFFSET - TILE_SIZE:
            self.rect.right = X_OFFSET
        elif self.rect.right < X_OFFSET:
            self.rect.left = GAME_WIDTH + X_OFFSET

        # 更新位置
        self.rect.x = int(self.x - TILE_SIZE // 2)
        self.rect.y = int(self.y - TILE_SIZE // 2)

        # 检查是否需要换方向
        if self.x % TILE_SIZE == self.spawn_x % TILE_SIZE and self.y % TILE_SIZE == self.spawn_y % TILE_SIZE and \
                (self.x - self.spawn_x === 0 or self.y - self.spawn_y == 0):
            pass  # 在出生点不换向
        if self.x % TILE_SIZE == TILE_SIZE // 2 and self.y % TILE_SIZE == TILE_SIZE // 2:
            # 在网格中心，可以换方向
            valid_dirs = get_valid_directions(self.rect, self.direction)
            if len(valid_dirs) > 1:
                # 除当前方向外的合法方向
                all_dirs = [UP, DOWN, LEFT, RIGHT]
                others = [d for d in valid_dirs if d != self.direction or len(valid_dirs) == 1]
                if others:
                    # 如果玩家不是恐惧状态，优先朝向玩家
                    if not self.is_frightened:
                        # 选择最接近玩家的方向
                        best_dir = None
                        min_dist = float('inf')
                        for d in others:
                            test_x = self.x + d[0] * TILE_SIZE
                            test_y = self.y + d[1] * TILE_SIZE
                            dist = ((test_x - player.x) ** 2 + (test_y - player.y) ** 2) ** 0.5
                            if dist < min_dist:
                                min_dist = dist
                                best_dir = d
                        if best_dir:
                            self.direction = best_dir
                        else:
                            self.direction = random.choice(valid_dirs)
                    else:
                        self.direction = random.choice(valid_dirs)
            elif len(valid_dirs) == 1:
                self.direction = valid_dirs[0]
            elif len(valid_dirs) == 0:
                # 只能掉头
                self.direction = (-self.direction[0], -self.direction[1])

    def draw(self, screen):
        if self.eaten:
            return
        color = CYAN if self.is_frightened else self.original_color
        x, y = int(self.x), int(self.y)
        # 幽灵主体
        pygame.draw.circle(screen, color, (x, y), TILE_SIZE // 2)
        # 幽灵眼睛
        if not self.is_frightened:
            # 白色眼白
            pygame.draw.circle(screen, WHITE, (x - 4, y - 4), 4)
            pygame.draw.circle(screen, WHITE, (x + 4, y - 4), 4)
            # 黑色瞳孔
            pygame.draw.circle(screen, BLACK, (x - 4, y - 4), 2)
            pygame.draw.circle(screen, BLACK, (x + 4, y - 4), 2)
        else:
            # 恐惧状态，皱眉
            pygame.draw.line(screen, BLACK, (x - 6, y - 4), (x - 2, y - 2), 2)
            pygame.draw.line(screen, BLACK, (x + 2, y - 2), (x + 6, y - 4), 2)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.pacman = Pacman()
        self.ghosts = [
            Ghost(ghost_spawns[0][0], ghost_spawns[0][1], RED, ghost_spawns[0][0], ghost_spawns[0][1]),
            Ghost(ghost_spawns[1][0], ghost_spawns[1][1], ORANGE, ghost_spawns[1][0], ghost_spawns[1][1]),
            Ghost(ghost_spawns[2][0], ghost_spawns[2][1], PINK, ghost_spawns[2][0], ghost_spawns[2][1]),
            Ghost(ghost_spawns[3][0], ghost_spawns[3][1], CYAN, ghost_spawns[3][0], ghost_spawns[3][1])
        ]
        self.energy_dots = list(energy_dots_pos)
        self.dots = []
        for r in range(MAP_ROWS):
            for c in range(MAP_COLS):
                if maze[r][c] == '.':
                    self.dots.append((c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2))
        self.game_state = "PLAYING"
        self.game_over_message = ""
        self.frightened_time = 0

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_r and self.game_state in ["GAME_OVER", "WIN"]:
                        self.reset_game()
                    if self.game_state == "PLAYING":
                        if event.key == pygame.K_UP:
                            self.pacman.next_direction = UP
                        elif event.key == pygame.K_DOWN:
                            self.pacman.next_direction = DOWN
                        elif event.key == pygame.K_LEFT:
                            self.pacman.next_direction = LEFT
                        elif event.key == pygame.K_RIGHT:
                            self.pacman.next_direction = RIGHT

            if self.game_state == "PLAYING":
                self.update()
            self.draw()
            self.clock.tick(FPS)

    def update(self):
        self.pacman.update()

        # 更新能量豆状态
        if self.frightened_time > 0:
            self.frightened_time -= 1 / FPS
            if self.frightened_time <= 0:
                for ghost in self.ghosts:
                    ghost.is_frightened = False

        # 检测豆子碰撞
        for i, dot in enumerate(self.dots):
            if abs(self.pacman.x - dot[0]) < TILE_SIZE // 2 and abs(self.pacman.y - dot[1]) < TILE_SIZE // 2:
                self.dots.pop(i)
                self.score += 10
                if len(self.dots) == 0 and len(self.energy_dots) == 0:
                    self.game_state = "WIN"
                    self.game_over_message = "YOU WIN!"
                break

        # 检测能量豆碰撞
        for i, dot in enumerate(self.energy_dots):
            if abs(self.pacman.x - dot[0]) < TILE_SIZE // 2 and abs(self.pacman.y - dot[1]) < TILE_SIZE // 2:
                self.energy_dots.pop(i)
                self.score += 50
                self.frightened_time = 6  # 6 秒
                for ghost in self.ghosts:
                    ghost.is_frightened = True

        # 更新幽灵
        for ghost in self.ghosts:
            ghost.update(self.pacman, self.clock.get_time())

        # 检测幽灵碰撞
        for ghost in self.ghosts:
            if self.pacman.rect.colliderect(ghost.rect):
                if ghost.is_frightened and not ghost.eaten:
                    # 吃掉幽灵
                    ghost.eaten = True
                    ghost.x, ghost.y = ghost.spawn_x, ghost.spawn_y
                    ghost.rect.x = int(ghost.x - TILE_SIZE // 2)
                    ghost.rect.y = int(ghost.y - TILE_SIZE // 2)
                    ghost.eaten = False
                    ghost.is_frightened = False
                    self.score += 200
                else:
                    # 被幽灵吃掉
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_state = "GAME_OVER"
                        self.game_over_message = "GAME OVER"
                    else:
                        self.pacman.reset_position()
                        for ghost in self.ghosts:
                            ghost.x = ghost.spawn_x
                            ghost.y = ghost.spawn_y
                            ghost.rect.x = int(ghost.x - TILE_SIZE // 2)
                            ghost.rect.y = int(ghost.y - TILE_SIZE // 2)
                            ghost.direction = STOP

    def draw(self):
        self.screen.fill(BLACK)
        # 绘制迷宫
        for r in range(MAP_ROWS):
            for c in range(MAP_COLS):
                if maze[r][c] == '#':
                    pygame.draw.rect(self.screen, BLUE, (X_OFFSET + c * TILE_SIZE, Y_OFFSET + r * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                elif maze[r][c] == '.':
                    dot_x = X_OFFSET + c * TILE_SIZE + TILE_SIZE // 2
                    dot_y = Y_OFFSET + r * TILE_SIZE + TILE_SIZE // 2
                    pygame.draw.circle(self.screen, WHITE, (dot_x, dot_y), 3)

        # 绘制能量豆
        for dot_x, dot_y in self.energy_dots:
            pygame.draw.circle(self.screen, YELLOW, (int(dot_x + X_OFFSET), int(dot_y + Y_OFFSET)), 8)

        # 绘制玩家和幽灵
        self.pacman.draw(self.screen)
        for ghost in self.ghosts:
            ghost.draw(self.screen)

        # HUD 区域
        hud_x = X_OFFSET + GAME_WIDTH + 10
        pygame.draw.rect(self.screen, LIGHT_BROWN, (hud_x, Y_OFFSET, SCREEN_WIDTH - hud_x, GAME_HEIGHT))
        score_text = font.render(f"Score: {self.score}", True, BLACK)
        lives_text = font.render(f"Lives: {self.lives}", True, BLACK)
        dots_left = len(self.dots) + len(self.energy_dots)
        dots_text = font.render(f"Dots: {dots_left}", True, BLACK)
        self.screen.blit(score_text, (hud_x + 10, Y_OFFSET + 20))
        self.screen.blit(lives_text, (hud_x + 10, Y_OFFSET + 60))
        self.screen.blit(dots_text, (hud_x + 10, Y_OFFSET + 100))

        # 胜负提示
        if self.game_state in ["GAME_OVER", "WIN"]:
            pygame.draw.rect(self.screen, BLACK, (0, 200, SCREEN_WIDTH, 200))
            msg_text = font.render(self.game_over_message, True, GREEN if self.game_state == "WIN" else RED)
            score_text2 = font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = small_font.render("Press R to Restart", True, WHITE)
            self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, 220))
            self.screen.blit(score_text2, (SCREEN_WIDTH // 2 - score_text2.get_width() // 2, 260))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 300))

        pygame.display.flip()


if __name__ == "__main__":
    Game().run()