import pygame
import sys
import random
import math

# 固定参数
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 24
MAZE_COLS = 19
MAZE_ROWS = 21
MAZE_WIDTH = MAZE_COLS * GRID_SIZE
MAZE_HEIGHT = MAZE_ROWS * GRID_SIZE
MAZE_X = (SCREEN_WIDTH - MAZE_WIDTH) // 4
MAZE_Y = (SCREEN_HEIGHT - MAZE_HEIGHT) // 2
FPS = 60
PLAYER_SPEED = 3
GHOST_SPEED = 2
POWER_DURATION = 6 * FPS  # 6秒
PLAYER_LIVES = 3
SCORE_DOT = 10
SCORE_POWER = 50
SCORE_GHOST = 200

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WALL_COLOR = (33, 33, 222)
PATH_COLOR = BLACK
DOT_COLOR = (255, 255, 150)
POWER_DOT_COLOR = (255, 200, 0)
PLAYER_COLOR = (255, 255, 0)
GHOST_COLORS = [
    (255, 0, 0),    # 红
    (0, 255, 255),  # 青
    (255, 182, 255),# 粉
    (255, 182, 85)  # 橙
]
TEXT_COLOR = WHITE
HUD_BG = (50, 50, 80)

# 迷宫定义
MAZE_LAYOUT = [
    "WWWWWWWWWWWWWWWWWWW",
    "W........W........W",
    "W.WW.WWW.W.WWW.WW.W",
    "W*W.....P.....W*W.W",
    "W.W.WWW.WWW.WWW.W.W",
    "W...W...W...W...W.W",
    "WWW.WWW.WWW.WWW.WWW",
    "   W...G   G...W   ",
    "WWW.WWW.WWW.WWW.WWW",
    "W...W...W...W...W.W",
    "W.WWW.WWW.WWW.WWW.W",
    "W*W.....P.....W*W.W",
    "W.W.WWW.WWW.WWW.W.W",
    "W...W...W...W...W.W",
    "WWW.WWW.WWW.WWW.WWW",
    "   W...G   G...W   ",
    "WWW.WWW.WWW.WWW.WWW",
    "W........W........W",
    "W.WW.WWW.W.WWW.WW.W",
    "W*W...........W*W.W",
    "WWWWWWWWWWWWWWWWWWW"
]

# 固定随机种子
random.seed(42)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Man Medium")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.big_font = pygame.font.Font(None, 64)
        self.reset_game()

    def reset_game(self):
        self.score = 0
        self.lives = PLAYER_LIVES
        self.dots_count = 0
        self.power_timer = 0
        self.game_over = False
        self.win = False
        self.dots = []
        self.power_dots = []
        self.walls = []
        self.ghosts = []
        self.player = None
        self.ghost_spawns = []
        self.player_spawn = None
        self.parse_maze()
        self.spawn_player()
        self.spawn_ghosts()

    def parse_maze(self):
        self.walls = []
        self.dots = []
        self.power_dots = []
        self.ghost_spawns = []
        for y, row in enumerate(MAZE_LAYOUT):
            for x, cell in enumerate(row):
                rect = pygame.Rect(MAZE_X + x * GRID_SIZE, MAZE_Y + y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                if cell == 'W':
                    self.walls.append(rect)
                elif cell == '.':
                    self.dots.append(rect)
                    self.dots_count += 1
                elif cell == '*':
                    self.power_dots.append(rect)
                    self.dots_count += 1
                elif cell == 'P':
                    self.player_spawn = (x, y)
                elif cell == 'G':
                    self.ghost_spawns.append((x, y))
                # 空白字符 ' ' 表示通路（无豆子）

    def spawn_player(self):
        px, py = self.player_spawn
        self.player = pygame.Rect(
            MAZE_X + px * GRID_SIZE + GRID_SIZE // 2,
            MAZE_Y + py * GRID_SIZE + GRID_SIZE // 2,
            GRID_SIZE - 4,
            GRID_SIZE - 4
        )
        self.player_direction = (0, 0)
        self.next_direction = (0, 0)

    def spawn_ghosts(self):
        self.ghosts = []
        for i, (gx, gy) in enumerate(self.ghost_spawns):
            ghost = {
                'rect': pygame.Rect(
                    MAZE_X + gx * GRID_SIZE + GRID_SIZE // 2,
                    MAZE_Y + gy * GRID_SIZE + GRID_SIZE // 2,
                    GRID_SIZE - 4,
                    GRID_SIZE - 4
                ),
                'color': GHOST_COLORS[i % len(GHOST_COLORS)],
                'direction': (0, 0),
                'speed': GHOST_SPEED,
                'eaten': False,
                'frightened': False,
                'spawn': (gx, gy)
            }
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
                if not self.game_over and not self.win:
                    if event.key == pygame.K_UP:
                        self.next_direction = (0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.next_direction = (0, 1)
                    elif event.key == pygame.K_LEFT:
                        self.next_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.next_direction = (1, 0)

    def move_player(self):
        if self.game_over or self.win:
            return
        # 尝试应用下一个方向
        test_rect = self.player.copy()
        test_rect.x += self.next_direction[0] * PLAYER_SPEED
        test_rect.y += self.next_direction[1] * PLAYER_SPEED
        if not self.check_wall_collision(test_rect):
            self.player_direction = self.next_direction
        # 按当前方向移动
        new_rect = self.player.copy()
        new_rect.x += self.player_direction[0] * PLAYER_SPEED
        new_rect.y += self.player_direction[1] * PLAYER_SPEED
        # 隧道穿行
        if new_rect.left < MAZE_X:
            new_rect.right = MAZE_X + MAZE_WIDTH
        elif new_rect.right > MAZE_X + MAZE_WIDTH:
            new_rect.left = MAZE_X
        if not self.check_wall_collision(new_rect):
            self.player = new_rect
        # 吃豆子
        self.collect_dots()

    def check_wall_collision(self, rect):
        for wall in self.walls:
            if rect.colliderect(wall):
                return True
        return False

    def collect_dots(self):
        # 普通豆子
        for dot in self.dots[:]:
            if self.player.colliderect(dot):
                self.dots.remove(dot)
                self.score += SCORE_DOT
                self.dots_count -= 1
        # 能量豆
        for pdot in self.power_dots[:]:
            if self.player.colliderect(pdot):
                self.power_dots.remove(pdot)
                self.score += SCORE_POWER
                self.dots_count -= 1
                self.power_timer = POWER_DURATION
                for ghost in self.ghosts:
                    ghost['frightened'] = True
                    ghost['eaten'] = False

    def move_ghosts(self):
        for ghost in self.ghosts:
            if ghost['eaten']:
                # 返回出生点
                gx, gy = ghost['spawn']
                target_x = MAZE_X + gx * GRID_SIZE + GRID_SIZE // 2
                target_y = MAZE_Y + gy * GRID_SIZE + GRID_SIZE // 2
                if ghost['rect'].x < target_x:
                    ghost['rect'].x += ghost['speed']
                elif ghost['rect'].x > target_x:
                    ghost['rect'].x -= ghost['speed']
                if ghost['rect'].y < target_y:
                    ghost['rect'].y += ghost['speed']
                elif ghost['rect'].y > target_y:
                    ghost['rect'].y -= ghost['speed']
                if abs(ghost['rect'].x - target_x) < ghost['speed'] and abs(ghost['rect'].y - target_y) < ghost['speed']:
                    ghost['eaten'] = False
                    ghost['frightened'] = False
                continue

            # 方向选择: 优先朝玩家方向
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            # 随机但确定性的选择顺序
            random.shuffle(directions)
            best_dir = ghost['direction']
            best_dist = float('inf')
            for dx, dy in directions:
                # 避免反向立刻回头
                if dx == -ghost['direction'][0] and dy == -ghost['direction'][1]:
                    continue
                test_rect = ghost['rect'].copy()
                test_rect.x += dx * ghost['speed']
                test_rect.y += dy * ghost['speed']
                if self.check_wall_collision(test_rect):
                    continue
                # 计算到玩家的距离
                dist = math.hypot(test_rect.centerx - self.player.centerx, test_rect.centery - self.player.centery)
                if dist < best_dist:
                    best_dist = dist
                    best_dir = (dx, dy)
            # 移动
            new_rect = ghost['rect'].copy()
            new_rect.x += best_dir[0] * ghost['speed']
            new_rect.y += best_dir[1] * ghost['speed']
            # 隧道穿行
            if new_rect.left < MAZE_X:
                new_rect.right = MAZE_X + MAZE_WIDTH
            elif new_rect.right > MAZE_X + MAZE_WIDTH:
                new_rect.left = MAZE_X
            if not self.check_wall_collision(new_rect):
                ghost['rect'] = new_rect
                ghost['direction'] = best_dir

    def update(self):
        if self.game_over or self.win:
            return
        self.move_player()
        if self.power_timer > 0:
            self.power_timer -= 1
            if self.power_timer == 0:
                for ghost in self.ghosts:
                    ghost['frightened'] = False
        self.move_ghosts()
        # 碰撞检测
        for ghost in self.ghosts:
            if ghost['rect'].colliderect(self.player):
                if ghost['frightened'] and not ghost['eaten']:
                    # 吃掉幽灵
                    ghost['eaten'] = True
                    self.score += SCORE_GHOST
                elif not ghost['eaten'] and not ghost['frightened']:
                    # 碰到普通幽灵
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        self.spawn_player()
                        self.spawn_ghosts()
        # 胜利条件
        if self.dots_count == 0:
            self.win = True

    def draw(self):
        self.screen.fill(BLACK)
        # 绘制迷宫背景
        pygame.draw.rect(self.screen, PATH_COLOR, (MAZE_X, MAZE_Y, MAZE_WIDTH, MAZE_HEIGHT))
        # 绘制墙体
        for wall in self.walls:
            pygame.draw.rect(self.screen, WALL_COLOR, wall)
        # 绘制豆子
        for dot in self.dots:
            pygame.draw.circle(self.screen, DOT_COLOR, dot.center, 3)
        for pdot in self.power_dots:
            pygame.draw.circle(self.screen, POWER_DOT_COLOR, pdot.center, 6)
        # 绘制幽灵
        for ghost in self.ghosts:
            color = (255, 255, 255) if ghost['frightened'] else ghost['color']
            if ghost['eaten']:
                color = (100, 100, 100)
            pygame.draw.rect(self.screen, color, ghost['rect'], border_radius=10)
        # 绘制玩家
        pygame.draw.circle(self.screen, PLAYER_COLOR, self.player.center, self.player.width // 2)
        # 绘制HUD背景
        hud_x = MAZE_X + MAZE_WIDTH + 20
        hud_width = SCREEN_WIDTH - hud_x - 20
        pygame.draw.rect(self.screen, HUD_BG, (hud_x, MAZE_Y, hud_width, MAZE_HEIGHT))
        # 绘制HUD文字
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        lives_text = self.font.render(f"Lives: {self.lives}", True, TEXT_COLOR)
        dots_text = self.font.render(f"Dots left: {self.dots_count}", True, TEXT_COLOR)
        power_text = self.font.render(f"Power: {self.power_timer // FPS}", True, TEXT_COLOR)
        self.screen.blit(score_text, (hud_x + 10, MAZE_Y + 30))
        self.screen.blit(lives_text, (hud_x + 10, MAZE_Y + 70))
        self.screen.blit(dots_text, (hud_x + 10, MAZE_Y + 110))
        self.screen.blit(power_text, (hud_x + 10, MAZE_Y + 150))
        # 游戏结束/胜利提示
        if self.game_over:
            text = self.big_font.render("GAME OVER", True, (255, 50, 50))
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            restart_text = self.font.render("Press R to Restart", True, TEXT_COLOR)
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        elif self.win:
            text = self.big_font.render("YOU WIN!", True, (50, 255, 50))
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            restart_text = self.font.render("Press R to Restart", True, TEXT_COLOR)
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        # 操作提示
        controls_text = self.font.render("Arrow Keys: Move", True, TEXT_COLOR)
        restart_help = self.font.render("R: Restart, ESC: Quit", True, TEXT_COLOR)
        self.screen.blit(controls_text, (hud_x + 10, MAZE_Y + MAZE_HEIGHT - 80))
        self.screen.blit(restart_help, (hud_x + 10, MAZE_Y + MAZE_HEIGHT - 40))

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