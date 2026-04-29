import pygame
import sys
import random

# === 常量定义 ===
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 24
MAP_COLS = 19
MAP_ROWS = 21
HUD_WIDTH = WINDOW_WIDTH - (MAP_COLS * GRID_SIZE)  # HUD区域宽度
FPS = 60

# 坐标偏移使迷宫居中
MAP_X_OFFSET = (WINDOW_WIDTH - HUD_WIDTH - MAP_COLS * GRID_SIZE) // 2 + HUD_WIDTH // 2
MAP_Y_OFFSET = (WINDOW_HEIGHT - MAP_ROWS * GRID_SIZE) // 2

# 游戏参数
PLAYER_SPEED = 3
GHOST_SPEED = 2  # 稍慢于玩家
ENERGY_DURATION = 6 * FPS  # 6秒（按60FPS计）
SCORE_NORMAL_BEAN = 10
SCORE_POWER_BEAN = 50
SCORE_GHOST_EAT = 200
LIVES = 3

# 颜色定义
COLOR_WALL = (33, 33, 191)       # 深蓝
COLOR_PATH = (0, 0, 0)           # 黑底
COLOR_BEAN = (255, 255, 200)     # 白色小点
COLOR_POWER_BEAN = (255, 255, 255)  # 闪光能量豆
COLOR_PLAYER = (255, 255, 0)     # 黄色
COLOR_GHOSTS = [(255, 0, 0), (255, 184, 255), (0, 255, 255), (255, 184, 82)]  # 红、粉、青、橙
COLOR_FRIGHTENED = (0, 0, 255)        # 蓝
COLOR_SCARED = (255, 255, 255)        # 白色（快结束时闪烁）

# 迷宫布局（1=墙,0=通路,2=普通豆,3=能量豆,4=玩家出生,5=幽灵出生）
# 19列x21行
MAP_LAYOUT = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,2,1],
    [1,3,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,3,1],
    [1,2,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,2,1,2,1,1,1,1,1,2,1,2,1,1,2,1],
    [1,2,1,1,2,1,2,1,1,1,1,1,2,1,2,1,1,2,1],
    [1,2,2,2,2,1,2,2,2,5,2,2,2,1,2,2,2,2,1],
    [1,1,1,1,2,1,1,1,0,0,0,1,1,1,2,1,1,1,1],
    [1,1,1,1,2,1,0,0,0,0,0,0,0,1,2,1,1,1,1],
    [1,1,1,1,2,1,0,2,2,4,2,2,0,1,2,1,1,1,1],
    [1,2,2,2,2,0,0,2,2,2,2,2,0,0,2,2,2,2,1],
    [1,2,1,1,2,1,0,1,1,1,1,1,0,1,2,1,1,2,1],
    [1,2,1,1,2,1,0,1,1,1,1,1,0,1,2,1,1,2,1],
    [1,3,2,1,2,2,2,2,2,0,2,2,2,2,2,1,2,3,1],
    [1,1,2,1,2,1,1,1,2,1,2,1,1,1,2,1,2,1,1],
    [1,2,2,2,2,1,2,2,2,1,2,2,2,1,2,2,2,2,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

# 方向枚举
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0, 0)


class PacmanGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pac-Man Medium")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.reset_game()

    def reset_game(self):
        self.score = 0
        self.lives = LIVES
        self.map = [row[:] for row in MAP_LAYOUT]
        self.total_beans = 0
        self.power_bean_count = 0
        self.energy_timeout = 0
        self.game_over = False
        self.win = False

        # 初始化玩家
        self.player = Pacman(0, 0)
        # 初始化幽灵
        self.ghosts = []
        # 找到出生点
        player_start = None
        ghost_starts = []
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                if self.map[y][x] == 4:
                    player_start = (x, y)
                    self.map[y][x] = 0  # 清除出生点标记
                elif self.map[y][x] == 5:
                    ghost_starts.append((x, y))
                    self.map[y][x] = 0

        if player_start:
            self.player.rect.x = player_start[0] * GRID_SIZE
            self.player.rect.y = player_start[1] * GRID_SIZE
            self.player.grid_x = player_start[0]
            self.player.grid_y = player_start[1]
            self.player.next_direction = RIGHT
            self.player.current_direction = RIGHT

        for i, (gx, gy) in enumerate(ghost_starts):
            ghost = Ghost(gx * GRID_SIZE, gy * GRID_SIZE, COLOR_GHOSTS[i % len(COLOR_GHOSTS)])
            self.ghosts.append(ghost)

        # 统计豆子数量
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                if self.map[y][x] == 2:
                    self.total_beans += 1
                elif self.map[y][x] == 3:
                    self.power_bean_count += 1
                    self.total_beans += 1

    def update(self):
        if self.game_over:
            return

        # 更新能量豆状态
        if self.energy_timeout > 0:
            self.energy_timeout -= 1
            if self.energy_timeout == 0:
                for g in self.ghosts:
                    g.scared = False

        # 更新玩家
        self.player.update(self.map)

        # 检查是否吃到豆子
        player_grid_x = self.player.rect.x // GRID_SIZE
        player_grid_y = self.player.rect.y // GRID_SIZE

        if 0 <= player_grid_x < MAP_COLS and 0 <= player_grid_y < MAP_ROWS:
            cell = self.map[player_grid_y][player_grid_x]
            if cell == 2:
                self.score += SCORE_NORMAL_BEAN
                self.total_beans -= 1
                self.map[player_grid_y][player_grid_x] = 0
                if self.total_beans == 0:
                    self.win = True
                    self.end_game()
            elif cell == 3:
                self.score += SCORE_POWER_BEAN
                self.total_beans -= 1
                self.map[player_grid_y][player_grid_x] = 0
                self.energy_timeout = ENERGY_DURATION
                for g in self.ghosts:
                    g.scared = True

        # 更新幽灵
        for ghost in self.ghosts:
            ghost.update(self.map, (self.player.rect.x // GRID_SIZE, self.player.rect.y // GRID_SIZE), self.energy_timeout > 0)

        # 检查玩家与幽灵碰撞
        for ghost in self.ghosts:
            if self.player.rect.colliderect(ghost.rect):
                if self.energy_timeout > 0 and ghost.scared:
                    # 吃掉幽灵
                    self.score += SCORE_GHOST_EAT
                    ghost.reset()
                else:
                    # 玩家死亡
                    self.lives -= 1
                    if self.lives <= 0:
                        self.win = False
                        self.end_game()
                    else:
                        self.reset_positions()

    def reset_positions(self):
        # 重置玩家
        player_start = None
        ghost_starts = []
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                if self.map[y][x] == 4:
                    player_start = (x, y)
                elif self.map[y][x] == 5:
                    ghost_starts.append((x, y))

        if player_start:
            self.player.rect.x = player_start[0] * GRID_SIZE
            self.player.rect.y = player_start[1] * GRID_SIZE
            self.player.grid_x = player_start[0]
            self.player.grid_y = player_start[1]
            self.player.next_direction = RIGHT
            self.player.current_direction = RIGHT

        for i, ghost in enumerate(self.ghosts):
            gx, gy = ghost_starts[i % len(ghost_starts)]
            ghost.rect.x = gx * GRID_SIZE
            ghost.rect.y = gy * GRID_SIZE
            ghost.scared = False
            ghost.current_direction = (0, 0)

    def end_game(self):
        self.game_over = True

    def draw(self):
        self.screen.fill(COLOR_PATH)

        # 绘制迷宫
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                cell = self.map[y][x]
                rect = pygame.Rect(MAP_X_OFFSET + x * GRID_SIZE, MAP_Y_OFFSET + y * GRID_SIZE,
                                   GRID_SIZE, GRID_SIZE)

                if cell == 1:  # 墙
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)

        # 绘制豆子
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                cell = self.map[y][x]
                if cell in [2, 3]:
                    cx = MAP_X_OFFSET + x * GRID_SIZE + GRID_SIZE // 2
                    cy = MAP_Y_OFFSET + y * GRID_SIZE + GRID_SIZE // 2
                    if cell == 2:  # 普通豆
                        pygame.draw.circle(self.screen, COLOR_BEAN, (cx, cy), 4)
                    elif cell == 3:  # 能量豆
                        radius = 10 if (self.clock.get_time() // 200) % 2 == 0 else 12
                        pygame.draw.circle(self.screen, COLOR_POWER_BEAN, (cx, cy), radius)

        # 绘制玩家
        self.player.draw(self.screen, MAP_X_OFFSET, MAP_Y_OFFSET)

        # 绘制幽灵
        for ghost in self.ghosts:
            ghost.draw(self.screen, MAP_X_OFFSET, MAP_Y_OFFSET)

        # HUD绘制
        hud_rect = pygame.Rect(MAP_X_OFFSET - HUD_WIDTH // 2 - 5, MAP_Y_OFFSET, HUD_WIDTH, MAP_ROWS * GRID_SIZE)
        pygame.draw.rect(self.screen, (40, 40, 40), hud_rect)

        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        lives_text = self.font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        beans_text = self.font.render(f"Beans: {self.total_beans}", True, (255, 255, 255))

        self.screen.blit(score_text, (hud_rect.left + 10, hud_rect.top + 20))
        self.screen.blit(lives_text, (hud_rect.left + 10, hud_rect.top + 60))
        self.screen.blit(beans_text, (hud_rect.left + 10, hud_rect.top + 100))

        # 时间显示
        if self.energy_timeout > 0:
            time_text = self.small_font.render(f"Power: {self.energy_timeout // FPS}s", True, (255, 255, 0))
            self.screen.blit(time_text, (hud_rect.left + 10, hud_rect.top + 140))

        # 游戏结束提示
        if self.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            if self.win:
                msg = "You Win!"
            else:
                msg = "Game Over"
            msg_text = self.font.render(msg, True, (255, 255, 0))
            score_end_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            restart_text = self.small_font.render("Press R to Restart", True, (255, 255, 255))

            self.screen.blit(msg_text, ((WINDOW_WIDTH - msg_text.get_width()) // 2,
                                        WINDOW_HEIGHT // 3 - 20))
            self.screen.blit(score_end_text, ((WINDOW_WIDTH - score_end_text.get_width()) // 2,
                                              WINDOW_HEIGHT // 3 + 30))
            self.screen.blit(restart_text, ((WINDOW_WIDTH - restart_text.get_width()) // 2,
                                            WINDOW_HEIGHT // 3 + 80))

        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset_game()
                    elif self.player and not self.game_over:
                        if event.key == pygame.K_UP:
                            self.player.set_direction(UP)
                        elif event.key == pygame.K_DOWN:
                            self.player.set_direction(DOWN)
                        elif event.key == pygame.K_LEFT:
                            self.player.set_direction(LEFT)
                        elif event.key == pygame.K_RIGHT:
                            self.player.set_direction(RIGHT)

            self.update()
            self.draw()


class Pacman:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        self.grid_x = x // GRID_SIZE
        self.grid_y = y // GRID_SIZE
        self.next_direction = RIGHT
        self.current_direction = STOP

    def set_direction(self, direction):
        self.next_direction = direction

    def update(self, map_grid):
        # 尝试转向
        if self.next_direction != STOP:
            next_pos = (self.grid_x + self.next_direction[0],
                        self.grid_y + self.next_direction[1])

            if 0 <= next_pos[0] < MAP_COLS and 0 <= next_pos[1] < MAP_ROWS:
                if map_grid[next_pos[1]][next_pos[0]] != 1:  # 不是墙
                    self.current_direction = self.next_direction
                    self.next_direction = STOP

        # 移动
        new_rect = self.rect.move(self.current_direction[0] * PLAYER_SPEED,
                                  self.current_direction[1] * PLAYER_SPEED)

        # 计算移动后是否完全在合法格子内
        # 检查四个角对应的格子
        corners = [
            (new_rect.x // GRID_SIZE, new_rect.y // GRID_SIZE),
            ((new_rect.x + GRID_SIZE - 1) // GRID_SIZE, new_rect.y // GRID_SIZE),
            (new_rect.x // GRID_SIZE, (new_rect.y + GRID_SIZE - 1) // GRID_SIZE),
            ((new_rect.x + GRID_SIZE - 1) // GRID_SIZE, (new_rect.y + GRID_SIZE - 1) // GRID_SIZE)
        ]

        valid = True
        for gx, gy in corners:
            if 0 <= gy < MAP_ROWS and 0 <= gx < MAP_COLS:
                if map_grid[gy][gx] == 1:
                    valid = False
                    break
            else:
                # 边界处视为墙
                valid = False
                break

        if valid:
            self.rect = new_rect
            self.grid_x = self.rect.x // GRID_SIZE
            self.grid_y = self.rect.y // GRID_SIZE

        # 隧道处理：从左侧/右侧出去从另一侧返回
        if self.rect.x < 0:
            self.rect.x = (MAP_COLS - 1) * GRID_SIZE
        elif self.rect.x > (MAP_COLS - 1) * GRID_SIZE:
            self.rect.x = 0

    def draw(self, screen, x_offset, y_offset):
        rect = pygame.Rect(self.rect.x + x_offset, self.rect.y + y_offset, GRID_SIZE, GRID_SIZE)
        pygame.draw.circle(screen, COLOR_PLAYER, rect.center, GRID_SIZE // 2 - 2)


class Ghost:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        self.start_rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        self.color = color
        self.scared = False
        self.scared_timer = 0
        self.current_direction = (0, 0)
        self.move_counter = 0

    def reset(self):
        self.rect.x = self.start_rect.x
        self.rect.y = self.start_rect.y
        self.scared = False

    def get_valid_directions(self, map_grid, grid_pos):
        valid = []
        for direction in [UP, DOWN, LEFT, RIGHT]:
            nx = grid_pos[0] + direction[0]
            ny = grid_pos[1] + direction[1]
            if 0 <= ny < MAP_ROWS and 0 <= nx < MAP_COLS:
                if map_grid[ny][nx] != 1:
                    valid.append(direction)
        return valid

    def update(self, map_grid, player_pos, player_scared):
        self.move_counter += 1

        # 每3帧移动一次（降低速度以匹配GhostSpeed）
        if self.move_counter % (PLAYER_SPEED // GHOST_SPEED) != 0:
            return

        current_grid_x = self.rect.x // GRID_SIZE
        current_grid_y = self.rect.y // GRID_SIZE
        current_pos = (current_grid_x, current_grid_y)

        # 获取可选方向（不能反向）
        valid_directions = self.get_valid_directions(map_grid, current_pos)
        # 排除反向
        if self.current_direction != (0, 0):
            reverse = (-self.current_direction[0], -self.current_direction[1])
            if reverse in valid_directions:
                valid_directions.remove(reverse)

        if not valid_directions:
            # 死路则反向
            reverse = (-self.current_direction[0], -self.current_direction[1])
            if reverse != (0, 0) and reverse in self.get_valid_directions(map_grid, current_pos):
                self.current_direction = reverse
            else:
                self.current_direction = (0, 0)  # 停止
        else:
            # 决策方向
            if player_scared:
                # 远离玩家
                best_direction = None
                max_dist = -1
                for d in valid_directions:
                    nx = current_pos[0] + d[0]
                    ny = current_pos[1] + d[1]
                    dist = abs(nx - player_pos[0]) + abs(ny - player_pos[1])
                    if dist > max_dist:
                        max_dist = dist
                        best_direction = d
                self.current_direction = best_direction or random.choice(valid_directions)
            else:
                # 向玩家移动（贪婪算法）
                best_direction = None
                min_dist = float('inf')
                for d in valid_directions:
                    nx = current_pos[0] + d[0]
                    ny = current_pos[1] + d[1]
                    dist = abs(nx - player_pos[0]) + abs(ny - player_pos[1])
                    if dist < min_dist:
                        min_dist = dist
                        best_direction = d
                self.current_direction = best_direction or random.choice(valid_directions)

        # 移动
        move_x = self.current_direction[0] * GHOST_SPEED
        move_y = self.current_direction[1] * GHOST_SPEED
        new_rect = self.rect.move(move_x, move_y)

        # 检查是否出界或撞墙
        valid = True
        corners = [
            (new_rect.x // GRID_SIZE, new_rect.y // GRID_SIZE),
            ((new_rect.x + GRID_SIZE - 1) // GRID_SIZE, new_rect.y // GRID_SIZE),
            (new_rect.x // GRID_SIZE, (new_rect.y + GRID_SIZE - 1) // GRID_SIZE),
            ((new_rect.x + GRID_SIZE - 1) // GRID_SIZE, (new_rect.y + GRID_SIZE - 1) // GRID_SIZE)
        ]

        for gx, gy in corners:
            if 0 <= gy < MAP_ROWS and 0 <= gx < MAP_COLS:
                if map_grid[gy][gx] == 1:
                    valid = False
                    break
            else:
                valid = False
                break

        if valid:
            self.rect = new_rect
        else:
            # 走不通则选其他方向
            valid_directions = self.get_valid_directions(map_grid, current_pos)
            # 移除当前方向反向
            if self.current_direction != (0, 0):
                reverse = (-self.current_direction[0], -self.current_direction[1])
                if reverse in valid_directions:
                    valid_directions.remove(reverse)

            # 重新尝试所有方向
            for d in valid_directions:
                test_rect = self.rect.move(d[0] * GHOST_SPEED, d[1] * GHOST_SPEED)
                test_corners = [
                    (test_rect.x // GRID_SIZE, test_rect.y // GRID_SIZE),
                    ((test_rect.x + GRID_SIZE - 1) // GRID_SIZE, test_rect.y // GRID_SIZE),
                    (test_rect.x // GRID_SIZE, (test_rect.y + GRID_SIZE - 1) // GRID_SIZE),
                    ((test_rect.x + GRID_SIZE - 1) // GRID_SIZE, (test_rect.y + GRID_SIZE - 1) // GRID_SIZE)
                ]

                all_valid = all(0 <= gy < MAP_ROWS and 0 <= gx < MAP_COLS and map_grid[gy][gx] != 1
                                for gx, gy in test_corners)

                if all_valid:
                    self.rect = test_rect
                    self.current_direction = d
                    break

        # 隧道处理
        if self.rect.x < 0:
            self.rect.x = (MAP_COLS - 1) * GRID_SIZE
        elif self.rect.x > (MAP_COLS - 1) * GRID_SIZE:
            self.rect.x = 0

    def draw(self, screen, x_offset, y_offset):
        rect = pygame.Rect(self.rect.x + x_offset, self.rect.y + y_offset, GRID_SIZE, GRID_SIZE)

        if self.scared:
            # 震动效果
            if (self.scared_timer // 20) % 2 == 0:
                color = COLOR_FRIGHTENED
            else:
                color = COLOR_SCARED
        else:
            color = self.color

        # 绘制幽灵身体（圆顶）
        pygame.draw.circle(screen, color, rect.center, GRID_SIZE // 2 - 2)

        # 绘制眼睛
        eye_offset = GRID_SIZE // 6
        left_eye = (rect.centerx - eye_offset, rect.centery - 4)
        right_eye = (rect.centerx + eye_offset, rect.centery - 4)
        pygame.draw.circle(screen, (255, 255, 255), left_eye, 3)
        pygame.draw.circle(screen, (255, 255, 255), right_eye, 3)


if __name__ == "__main__":
    random.seed(42)
    game = PacmanGame()
    game.run()