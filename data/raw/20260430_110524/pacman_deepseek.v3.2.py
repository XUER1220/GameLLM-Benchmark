import pygame
import random

pygame.init()
random.seed(42)

# 窗口设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 24
MAZE_WIDTH = 19
MAZE_HEIGHT = 21
MAZE_PX_WIDTH = MAZE_WIDTH * TILE_SIZE
MAZE_PX_HEIGHT = MAZE_HEIGHT * TILE_SIZE
MAZE_OFFSET_X = 50
MAZE_OFFSET_Y = (SCREEN_HEIGHT - MAZE_PX_HEIGHT) // 2
FPS = 60

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WALL_COLOR = (33, 33, 222)
PATH_COLOR = (0, 0, 0)
PELLET_COLOR = (222, 222, 222)
POWER_PELLET_COLOR = (222, 222, 222)
PACMAN_COLOR = (255, 255, 0)
GHOST_COLORS = [
    (255, 0, 0),    # 红
    (0, 255, 255),  # 青
    (255, 184, 255),# 粉
    (255, 184, 0)   # 橙
]
HUD_BG = (40, 40, 40)
HUD_TEXT = (255, 255, 255)
GAME_OVER_COLOR = (255, 50, 50)
WIN_COLOR = (50, 255, 50)

# 游戏常量
PACMAN_SPEED = 3
GHOST_SPEED = 2
POWER_DURATION = 6 * FPS  # 6 seconds
PELLET_SCORE = 10
POWER_SCORE = 50
GHOST_SCORE = 200
LIVES = 3
PACMAN_START = (9, 15)
GHOST_START = (9, 9)

# 迷宫定义 (W=墙, .=豆子, P=能量豆, ' '=通路, G=幽灵出生区, S=玩家出生点)
MAZE_LAYOUT = [
    "WWWWWWWWWWWWWWWWWWW",
    "W.........W.........W",
    "W.WWW.WWW.W.WWW.WWW.W",
    "WPWWW.WWW.W.WWW.WWWPW",
    "W.........W.........W",
    "W.WW.WWWWWWWWWWW.WW.W",
    "W...W....W.W....W...W",
    "WWW.WWWW.W.W.WWW.WWWW",
    "   W.WWWWWWWWWWW.W   ",
    "WWW.W.WG G G G.W.WWW",
    "   ...  GGGG  ...   ",
    "WWW.W.WWWWWWWWWW.W.WWW",
    "   W.............W   ",
    "WWW.W.WWWWWWWWWW.W.WWW",
    "W.........W.........W",
    "W.WWW.WWW.W.WWW.WWW.W",
    "WP...W.....S....W...PW",
    "WWWWW.W.WWWWW.W.WWWWW",
    "W.........W.........W",
    "W.WWWWWWW.W.WWWWWWW.W",
    "W...................W",
    "WWWWWWWWWWWWWWWWWWWWW"
]

# 初始化游戏状态
def initialize_game_state():
    pellets = []
    power_pellets = []
    walls = []
    for y, row in enumerate(MAZE_LAYOUT):
        for x, cell in enumerate(row):
            pos = (x * TILE_SIZE + TILE_SIZE//2, y * TILE_SIZE + TILE_SIZE//2)
            if cell == 'W':
                walls.append(pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif cell == '.':
                pellets.append(pos)
            elif cell == 'P':
                power_pellets.append(pos)
    return pellets, power_pellets, walls

class PacMan:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.x = PACMAN_START[0] * TILE_SIZE + TILE_SIZE//2
        self.y = PACMAN_START[1] * TILE_SIZE + TILE_SIZE//2
        self.dx = 0
        self.dy = 0
        self.radius = TILE_SIZE//2 - 2
        self.next_direction = (0, 0)
    
    def move(self, walls):
        # 预计算下一个位置
        next_x = self.x + self.next_direction[0] * PACMAN_SPEED
        next_y = self.y + self.next_direction[1] * PACMAN_SPEED
        temp_rect = pygame.Rect(next_x - self.radius, next_y - self.radius, self.radius*2, self.radius*2)
        can_move = True
        for wall in walls:
            if temp_rect.colliderect(wall):
                can_move = False
                break
        
        if can_move:
            self.dx, self.dy = self.next_direction
        
        # 实际移动
        next_x = self.x + self.dx * PACMAN_SPEED
        next_y = self.y + self.dy * PACMAN_SPEED
        temp_rect = pygame.Rect(next_x - self.radius, next_y - self.radius, self.radius*2, self.radius*2)
        can_move = True
        for wall in walls:
            if temp_rect.colliderect(wall):
                can_move = False
                break
        
        if can_move:
            self.x = next_x
            self.y = next_y
        
        # 隧道循环
        if self.x < 0:
            self.x = MAZE_PX_WIDTH - 1
        elif self.x >= MAZE_PX_WIDTH:
            self.x = 1

class Ghost:
    def __init__(self, color, start_pos):
        self.color = color
        self.start_x, self.start_y = start_pos
        self.reset()
        self.radius = TILE_SIZE//2 - 3
        self.directions = [(1,0), (-1,0), (0,1), (0,-1)]
        self.current_dir = random.choice(self.directions)
    
    def reset(self):
        self.x = self.start_x * TILE_SIZE + TILE_SIZE//2
        self.y = self.start_y * TILE_SIZE + TILE_SIZE//2
        self.active = True
        self.frightened = False
        self.frightened_timer = 0
    
    def move(self, pacman_x, pacman_y, walls):
        if not self.active:
            return
        
        # 被吓状态随机移动
        if self.frightened:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.frightened = False
        
        choices = []
        for dx, dy in self.directions:
            if (dx, dy) == (-self.current_dir[0], -self.current_dir[1]):
                continue  # 不能直接掉头
            
            next_x = self.x + dx * GHOST_SPEED
            next_y = self.y + dy * GHOST_SPEED
            temp_rect = pygame.Rect(next_x - self.radius, next_y - self.radius, self.radius*2, self.radius*2)
            collision = False
            for wall in walls:
                if temp_rect.colliderect(wall):
                    collision = True
                    break
            if not collision:
                choices.append((dx, dy))
        
        if not choices:
            return
        
        if self.frightened:
            self.current_dir = random.choice(choices)
        else:
            # 选择接近玩家的方向
            best_dist = float('inf')
            best_dir = choices[0]
            for dx, dy in choices:
                next_x = self.x + dx * GHOST_SPEED
                next_y = self.y + dy * GHOST_SPEED
                dist = ((next_x - pacman_x)**2 + (next_y - pacman_y)**2)**0.5
                if dist < best_dist:
                    best_dist = dist
                    best_dir = (dx, dy)
            self.current_dir = best_dir
        
        self.x += self.current_dir[0] * GHOST_SPEED
        self.y += self.current_dir[1] * GHOST_SPEED
        
        # 隧道循环
        if self.x < 0:
            self.x = MAZE_PX_WIDTH - 1
        elif self.x >= MAZE_PX_WIDTH:
            self.x = 1

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Man Medium")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 72)
        self.reset_game()
    
    def reset_game(self):
        self.pellets, self.power_pellets, self.walls = initialize_game_state()
        self.pacman = PacMan()
        
        # 初始化幽灵
        ghost_positions = [
            (8, 9), (9, 9), (10, 9), (11, 9)
        ]
        self.ghosts = []
        for i, pos in enumerate(ghost_positions):
            self.ghosts.append(Ghost(GHOST_COLORS[i], pos))
        
        self.score = 0
        self.lives = LIVES
        self.game_over = False
        self.win = False
        self.power_timer = 0
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r:
                    self.reset_game()
                if not self.game_over and not self.win:
                    if event.key == pygame.K_UP:
                        self.pacman.next_direction = (0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.pacman.next_direction = (0, 1)
                    elif event.key == pygame.K_LEFT:
                        self.pacman.next_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.pacman.next_direction = (1, 0)
        
        return True
    
    def update(self):
        if self.game_over or self.win:
            return
        
        self.pacman.move(self.walls)
        
        # 吃豆子
        for pellet in self.pellets[:]:
            px, py = pellet
            dist = ((self.pacman.x - px)**2 + (self.pacman.y - py)**2)**0.5
            if dist < TILE_SIZE//2:
                self.pellets.remove(pellet)
                self.score += PELLET_SCORE
        
        # 吃能量豆
        for power in self.power_pellets[:]:
            px, py = power
            dist = ((self.pacman.x - px)**2 + (self.pacman.y - py)**2)**0.5
            if dist < TILE_SIZE//2:
                self.power_pellets.remove(power)
                self.score += POWER_SCORE
                self.power_timer = POWER_DURATION
                for ghost in self.ghosts:
                    ghost.frightened = True
                    ghost.frightened_timer = POWER_DURATION
        
        # 更新幽灵
        for ghost in self.ghosts:
            ghost.move(self.pacman.x, self.pacman.y, self.walls)
            
            # 碰撞检测
            dist = ((self.pacman.x - ghost.x)**2 + (self.pacman.y - ghost.y)**2)**0.5
            if dist < TILE_SIZE//2:
                if ghost.frightened and ghost.active:
                    ghost.active = False
                    self.score += GHOST_SCORE
                    ghost.reset()
                elif not ghost.frightened and ghost.active:
                    self.lives -= 1
                    self.pacman.reset()
                    for g in self.ghosts:
                        g.reset()
                    if self.lives <= 0:
                        self.game_over = True
                    break
        
        # 能量状态倒计时
        if self.power_timer > 0:
            self.power_timer -= 1
        
        # 胜利条件
        if len(self.pellets) == 0 and len(self.power_pellets) == 0:
            self.win = True
    
    def draw_maze(self):
        # 绘制背景
        maze_rect = pygame.Rect(MAZE_OFFSET_X, MAZE_OFFSET_Y, MAZE_PX_WIDTH, MAZE_PX_HEIGHT)
        pygame.draw.rect(self.screen, BLACK, maze_rect)
        
        # 绘制墙壁
        for y, row in enumerate(MAZE_LAYOUT):
            for x, cell in enumerate(row):
                rect = pygame.Rect(
                    MAZE_OFFSET_X + x * TILE_SIZE,
                    MAZE_OFFSET_Y + y * TILE_SIZE,
                    TILE_SIZE, TILE_SIZE
                )
                if cell == 'W':
                    pygame.draw.rect(self.screen, WALL_COLOR, rect)
        
        # 绘制豆子
        for px, py in self.pellets:
            pos = (MAZE_OFFSET_X + px, MAZE_OFFSET_Y + py)
            pygame.draw.circle(self.screen, PELLET_COLOR, pos, 3)
        
        # 绘制能量豆
        for px, py in self.power_pellets:
            pos = (MAZE_OFFSET_X + px, MAZE_OFFSET_Y + py)
            pygame.draw.circle(self.screen, POWER_PELLET_COLOR, pos, 7)
    
    def draw_hud(self):
        hud_x = MAZE_OFFSET_X + MAZE_PX_WIDTH + 20
        hud_width = SCREEN_WIDTH - hud_x - 20
        hud_rect = pygame.Rect(hud_x, MAZE_OFFSET_Y, hud_width, MAZE_PX_HEIGHT)
        pygame.draw.rect(self.screen, HUD_BG, hud_rect)
        
        y_offset = MAZE_OFFSET_Y + 30
        
        # 分数
        score_text = self.font.render(f"Score: {self.score}", True, HUD_TEXT)
        self.screen.blit(score_text, (hud_x + 20, y_offset))
        y_offset += 50
        
        # 生命
        lives_text = self.font.render(f"Lives: {self.lives}", True, HUD_TEXT)
        self.screen.blit(lives_text, (hud_x + 20, y_offset))
        y_offset += 50
        
        # 剩余豆子
        pellets_text = self.font.render(f"Pellets: {len(self.pellets)}", True, HUD_TEXT)
        self.screen.blit(pellets_text, (hud_x + 20, y_offset))
        y_offset += 50
        
        # 能量豆
        power_text = self.font.render(f"Power: {len(self.power_pellets)}", True, HUD_TEXT)
        self.screen.blit(power_text, (hud_x + 20, y_offset))
        y_offset += 80
        
        # 操作提示
        controls = [
            "Controls:",
            "Arrow Keys - Move",
            "R - Restart Game",
            "ESC - Quit"
        ]
        for line in controls:
            control_text = self.small_font.render(line, True, HUD_TEXT)
            self.screen.blit(control_text, (hud_x + 20, y_offset))
            y_offset += 30
    
    def draw_characters(self):
        # 绘制吃豆人
        pac_pos = (
            MAZE_OFFSET_X + self.pacman.x,
            MAZE_OFFSET_Y + self.pacman.y
        )
        pygame.draw.circle(self.screen, PACMAN_COLOR, pac_pos, self.pacman.radius)
        
        # 绘制幽灵
        for ghost in self.ghosts:
            if not ghost.active:
                continue
            ghost_pos = (
                MAZE_OFFSET_X + ghost.x,
                MAZE_OFFSET_Y + ghost.y
            )
            color = WHITE if ghost.frightened else ghost.color
            pygame.draw.circle(self.screen, color, ghost_pos, ghost.radius)
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        if self.win:
            text = self.big_font.render("YOU WIN!", True, WIN_COLOR)
        else:
            text = self.big_font.render("GAME OVER", True, GAME_OVER_COLOR)
        
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(text, text_rect)
        
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        self.screen.blit(score_text, score_rect)
        
        restart_text = self.font.render("Press R to Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70))
        self.screen.blit(restart_text, restart_rect)
    
    def draw(self):
        self.screen.fill(BLACK)
        self.draw_maze()
        self.draw_characters()
        self.draw_hud()
        
        if self.game_over or self.win:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()