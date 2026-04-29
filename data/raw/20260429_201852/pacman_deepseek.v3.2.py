import pygame, sys, random

# 游戏参数常量
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
CELL_SIZE = 24
GRID_WIDTH = 19
GRID_HEIGHT = 21
MAZE_WIDTH = GRID_WIDTH * CELL_SIZE
MAZE_HEIGHT = GRID_HEIGHT * CELL_SIZE
MAZE_OFFSET_X = 50
MAZE_OFFSET_Y = (WINDOW_HEIGHT - MAZE_HEIGHT) // 2

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WALL_COLOR = (33, 33, 222)
PATH_COLOR = (0, 0, 0)
DOT_COLOR = (255, 255, 200)
POWER_DOT_COLOR = (255, 255, 0)
PLAYER_COLOR = (255, 255, 0)
GHOST_COLORS = [
    (255, 0, 0),     # 红
    (255, 182, 255), # 粉
    (0, 255, 255),   # 青
    (255, 184, 82)   # 橙
]
TEXT_COLOR = (255, 255, 255)
HUD_BG_COLOR = (50, 50, 80)

# 游戏逻辑常量
PLAYER_SPEED = 3
GHOST_SPEED = 2
POWER_DURATION = 6 * FPS  # 6 seconds
DOT_SCORE = 10
POWER_DOT_SCORE = 50
GHOST_SCORE = 200
INITIAL_LIVES = 3

# 固定随机种子
random.seed(42)

# 迷宫定义
# '#' 墙, '.' 豆子, 'P' 玩家出生点, 'G' 幽灵出生区, ' ' 通路, 'O' 能量豆, '-' 隧道
MAZE_MAP = [
    "###################",
    "#........#........#",
    "#O##.###.#.###.##O#",
    "#.................#",
    "#.##.#.#####.#.##.#",
    "#....#...#...#....#",
    "#.####.## ##.####.#",
    "#......#   #......#",
    "####.# # G # #.####",
    "     # #GGG# #     ",
    "     # #   # #     ",
    "     # #   # #     ",
    "####.# #   # #.####",
    "#........#........#",
    "#.##.###.#.###.##.#",
    "#O.#.....P.....#.O#",
    "##.#.#.#####.#.#.##",
    "#....#...#...#....#",
    "#.######.#.######.#",
    "#.................#",
    "###################"
]

class PacManGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pac-Man Medium")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.reset_game()

    def reset_game(self):
        self.game_over = False
        self.game_won = False
        self.score = 0
        self.lives = INITIAL_LIVES
        self.dots_left = 0
        self.power_mode = 0  # 倒计时帧数
        self.power_blink = 0
        self.ghosts_eatable = False

        # 解析迷宫
        self.walls = []
        self.dots = []
        self.power_dots = []
        self.player_start = (0, 0)
        self.ghost_start_area = []
        self.tunnels = []

        for y, row in enumerate(MAZE_MAP):
            for x, cell in enumerate(row):
                real_x = MAZE_OFFSET_X + x * CELL_SIZE
                real_y = MAZE_OFFSET_Y + y * CELL_SIZE
                rect = pygame.Rect(real_x, real_y, CELL_SIZE, CELL_SIZE)
                if cell == '#':
                    self.walls.append(rect)
                elif cell == 'P':
                    self.player_start = (real_x + CELL_SIZE//2, real_y + CELL_SIZE//2)
                elif cell == 'G':
                    self.ghost_start_area.append((real_x + CELL_SIZE//2, real_y + CELL_SIZE//2))
                elif cell == 'O':
                    self.power_dots.append(rect)
                elif cell == '.':
                    self.dots.append(rect)
                elif cell == '-':
                    self.tunnels.append((x, y))
        self.dots_left = len(self.dots) + len(self.power_dots)

        # 初始化玩家
        self.player = pygame.Rect(0, 0, CELL_SIZE-6, CELL_SIZE-6)
        self.player.center = self.player_start
        self.direction = (0, 0)
        self.next_direction = (0, 0)

        # 初始化幽灵
        self.ghosts = []
        for i in range(4):
            ghost = {
                'rect': pygame.Rect(0, 0, CELL_SIZE-4, CELL_SIZE-4),
                'color': GHOST_COLORS[i],
                'direction': (0, 0),
                'speed': GHOST_SPEED,
                'eaten': False,
                'respawn_timer': 0
            }
            if i < len(self.ghost_start_area):
                ghost['rect'].center = self.ghost_start_area[i]
            else:
                ghost['rect'].center = self.ghost_start_area[0]
            self.ghosts.append(ghost)

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
                    self.reset_game()
                if not self.game_over and not self.game_won:
                    if event.key == pygame.K_UP:
                        self.next_direction = (0, -1)
                    if event.key == pygame.K_DOWN:
                        self.next_direction = (0, 1)
                    if event.key == pygame.K_LEFT:
                        self.next_direction = (-1, 0)
                    if event.key == pygame.K_RIGHT:
                        self.next_direction = (1, 0)
        # 平滑转向
        next_rect = self.player.move(
            self.next_direction[0] * PLAYER_SPEED,
            self.next_direction[1] * PLAYER_SPEED
        )
        if not self.check_wall_collision(next_rect):
            self.direction = self.next_direction

    def check_wall_collision(self, rect):
        for wall in self.walls:
            if rect.colliderect(wall):
                return True
        return False

    def move_player(self):
        if self.game_over or self.game_won:
            return
        new_rect = self.player.move(
            self.direction[0] * PLAYER_SPEED,
            self.direction[1] * PLAYER_SPEED
        )
        if not self.check_wall_collision(new_rect):
            self.player = new_rect
        # 隧道循环
        if self.player.right < MAZE_OFFSET_X:
            self.player.left = MAZE_OFFSET_X + MAZE_WIDTH - CELL_SIZE
        elif self.player.left > MAZE_OFFSET_X + MAZE_WIDTH:
            self.player.right = MAZE_OFFSET_X + CELL_SIZE

    def move_ghost(self, ghost):
        if ghost['respawn_timer'] > 0:
            ghost['respawn_timer'] -= 1
            if ghost['respawn_timer'] == 0:
                ghost['eaten'] = False
                ghost['rect'].center = random.choice(self.ghost_start_area)
            return

        # 简单目标追逐逻辑
        if ghost['eaten']:
            target = random.choice(self.ghost_start_area)
        elif self.power_mode > 0 and not self.ghosts_eatable:
            # 逃离模式
            target = (MAZE_OFFSET_X + MAZE_WIDTH//2, MAZE_OFFSET_Y + MAZE_HEIGHT//2)
        else:
            target = self.player.center

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        # 优先保持原方向
        if ghost['direction'] != (0, 0):
            directions.remove(ghost['direction'])
            directions.insert(0, ghost['direction'])

        best_dir = ghost['direction']
        best_dist = float('inf')
        for dx, dy in directions:
            if dx == -ghost['direction'][0] and dy == -ghost['direction'][1]:
                continue  # 避免立即回头
            test_rect = ghost['rect'].move(dx * ghost['speed'], dy * ghost['speed'])
            if not self.check_wall_collision(test_rect):
                dist = ((test_rect.centerx - target[0])**2 + (test_rect.centery - target[1])**2)**0.5
                if dist < best_dist:
                    best_dist = dist
                    best_dir = (dx, dy)
        ghost['direction'] = best_dir
        new_rect = ghost['rect'].move(
            ghost['direction'][0] * ghost['speed'],
            ghost['direction'][1] * ghost['speed']
        )
        if not self.check_wall_collision(new_rect):
            ghost['rect'] = new_rect
        # 幽灵隧道循环
        if ghost['rect'].right < MAZE_OFFSET_X:
            ghost['rect'].left = MAZE_OFFSET_X + MAZE_WIDTH - CELL_SIZE
        elif ghost['rect'].left > MAZE_OFFSET_X + MAZE_WIDTH:
            ghost['rect'].right = MAZE_OFFSET_X + CELL_SIZE

    def update(self):
        if self.game_over or self.game_won:
            return

        self.move_player()

        # 吃豆子
        for dot in self.dots[:]:
            if self.player.colliderect(dot):
                self.dots.remove(dot)
                self.score += DOT_SCORE
                self.dots_left -= 1
        for pdot in self.power_dots[:]:
            if self.player.colliderect(pdot):
                self.power_dots.remove(pdot)
                self.score += POWER_DOT_SCORE
                self.dots_left -= 1
                self.power_mode = POWER_DURATION
                self.ghosts_eatable = True

        # 能量模式倒计时
        if self.power_mode > 0:
            self.power_mode -= 1
            self.power_blink = (self.power_blink + 1) % 10
            if self.power_mode == 0:
                self.ghosts_eatable = False
        else:
            self.power_blink = 0

        # 移动幽灵
        for ghost in self.ghosts:
            self.move_ghost(ghost)

        # 碰撞检测
        for ghost in self.ghosts:
            if self.player.colliderect(ghost['rect']):
                if self.ghosts_eatable and not ghost['eaten']:
                    # 吃幽灵
                    self.score += GHOST_SCORE
                    ghost['eaten'] = True
                    ghost['respawn_timer'] = 3 * FPS
                elif not ghost['eaten']:
                    # 玩家死亡
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        # 重置位置
                        self.player.center = self.player_start
                        self.direction = (0, 0)
                        self.next_direction = (0, 0)
                        for g in self.ghosts:
                            g['rect'].center = random.choice(self.ghost_start_area)
                            g['eaten'] = False
                            g['respawn_timer'] = 0
                    break

        # 胜利条件
        if self.dots_left == 0:
            self.game_won = True

    def draw(self):
        self.screen.fill(BLACK)
        # 绘制迷宫背景
        maze_surface = pygame.Surface((MAZE_WIDTH, MAZE_HEIGHT))
        maze_surface.fill(PATH_COLOR)
        pygame.draw.rect(maze_surface, HUD_BG_COLOR, (0, 0, MAZE_WIDTH, MAZE_HEIGHT), 4)
        self.screen.blit(maze_surface, (MAZE_OFFSET_X, MAZE_OFFSET_Y))

        # 绘制墙体
        for wall in self.walls:
            pygame.draw.rect(self.screen, WALL_COLOR, wall)

        # 绘制豆子
        for dot in self.dots:
            pygame.draw.circle(self.screen, DOT_COLOR, dot.center, 3)
        for pdot in self.power_dots:
            if self.power_blink < 5 or self.power_mode < 2 * FPS:
                pygame.draw.circle(self.screen, POWER_DOT_COLOR, pdot.center, 6)

        # 绘制幽灵
        for ghost in self.ghosts:
            color = ghost['color']
            if ghost['eaten']:
                color = (100, 100, 100)
            elif self.ghosts_eatable:
                if self.power_blink < 5:
                    color = (100, 100, 255)  # 闪烁蓝色
                else:
                    color = (255, 255, 255)
            pygame.draw.circle(self.screen, color, ghost['rect'].center, ghost['rect'].width//2)
            # 眼睛
            eye_color = WHITE if not ghost['eaten'] else BLACK
            pygame.draw.circle(self.screen, eye_color, (
                ghost['rect'].centerx + ghost['direction'][0]*3,
                ghost['rect'].centery + ghost['direction'][1]*3
            ), 4)
            pygame.draw.circle(self.screen, BLACK, (
                ghost['rect'].centerx + ghost['direction'][0]*5,
                ghost['rect'].centery + ghost['direction'][1]*5
            ), 2)

        # 绘制玩家
        pygame.draw.circle(self.screen, PLAYER_COLOR, self.player.center, self.player.width//2)
        # 嘴巴
        if self.direction != (0, 0):
            mouth_points = [
                self.player.center,
                (
                    self.player.centerx + self.direction[0]*self.player.width//2,
                    self.player.centery - self.direction[1]*self.player.height//3
                ),
                (
                    self.player.centerx + self.direction[0]*self.player.width//2,
                    self.player.centery + self.direction[1]*self.player.height//3
                )
            ]
            if self.direction[0] != 0:  # 左右方向，交换y坐标
                mouth_points[1], mouth_points[2] = mouth_points[2], mouth_points[1]
            pygame.draw.polygon(self.screen, BLACK, mouth_points)

        # HUD区域
        hud_x = MAZE_OFFSET_X + MAZE_WIDTH + 20
        pygame.draw.rect(self.screen, HUD_BG_COLOR, (hud_x-10, MAZE_OFFSET_Y, 250, MAZE_HEIGHT))
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (hud_x, MAZE_OFFSET_Y + 30))
        lives_text = self.font.render(f"Lives: {self.lives}", True, TEXT_COLOR)
        self.screen.blit(lives_text, (hud_x, MAZE_OFFSET_Y + 80))
        dots_text = self.small_font.render(f"Dots Left: {self.dots_left}", True, TEXT_COLOR)
        self.screen.blit(dots_text, (hud_x, MAZE_OFFSET_Y + 130))
        if self.power_mode > 0:
            power_text = self.small_font.render(f"POWER: {self.power_mode//FPS}", True, (0, 255, 255))
            self.screen.blit(power_text, (hud_x, MAZE_OFFSET_Y + 180))

        # 游戏结束提示
        if self.game_over:
            go_text = self.font.render("GAME OVER", True, (255, 50, 50))
            self.screen.blit(go_text, (WINDOW_WIDTH//2 - go_text.get_width()//2, WINDOW_HEIGHT//2 - 50))
            score_text = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            self.screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, WINDOW_HEIGHT//2))
            restart_text = self.font.render("Press R to Restart", True, (100, 255, 100))
            self.screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, WINDOW_HEIGHT//2 + 60))
        elif self.game_won:
            win_text = self.font.render("YOU WIN!", True, (50, 255, 50))
            self.screen.blit(win_text, (WINDOW_WIDTH//2 - win_text.get_width()//2, WINDOW_HEIGHT//2 - 50))
            score_text = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            self.screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, WINDOW_HEIGHT//2))
            restart_text = self.font.render("Press R to Restart", True, (100, 255, 100))
            self.screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, WINDOW_HEIGHT//2 + 60))

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = PacManGame()
    game.run()