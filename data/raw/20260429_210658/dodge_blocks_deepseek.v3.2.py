import pygame
import random
import sys

# 初始化
pygame.init()
random.seed(42)

# 常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 60
PLAYER_Y = SCREEN_HEIGHT - PLAYER_HEIGHT - 40
PLAYER_SPEED = 7
OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 40
OBSTACLE_SPAWN_RATE = 40
MIN_SPEED = 4
MAX_SPEED = 8

# 颜色定义
BACKGROUND_COLOR = (30, 30, 50)
PLAYER_COLOR = (70, 200, 100)
OBSTACLE_COLOR = (220, 80, 60)
TEXT_COLOR = (240, 240, 240)
GAME_OVER_COLOR = (220, 60, 60)
HUD_BG_COLOR = (20, 20, 40, 200)

# 设置窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge Blocks Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

class Player:
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = PLAYER_Y
        self.speed = PLAYER_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)

class Obstacle:
    def __init__(self):
        self.width = OBSTACLE_WIDTH
        self.height = OBSTACLE_HEIGHT
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = -self.height
        self.speed = random.uniform(MIN_SPEED, MAX_SPEED)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.y += self.speed
        self.rect.topleft = (self.x, self.y)

    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

    def draw(self, surface):
        pygame.draw.rect(surface, OBSTACLE_COLOR, self.rect)
        pygame.draw.rect(surface, (255, 200, 200), self.rect, 2)

def draw_hud(score, elapsed_time):
    hud_rect = pygame.Rect(10, 10, 250, 80)
    s = pygame.Surface((hud_rect.width, hud_rect.height), pygame.SRCALPHA)
    s.fill(HUD_BG_COLOR)
    screen.blit(s, hud_rect)
    score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
    time_text = font.render(f"Time: {elapsed_time:.1f}s", True, TEXT_COLOR)
    screen.blit(score_text, (20, 20))
    screen.blit(time_text, (20, 55))

def draw_game_over(final_score, elapsed_time):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    game_over_text = big_font.render("GAME OVER", True, GAME_OVER_COLOR)
    screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 150))

    score_text = font.render(f"Final Score: {final_score}", True, TEXT_COLOR)
    screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 250))

    time_text = font.render(f"Survived: {elapsed_time:.1f} seconds", True, TEXT_COLOR)
    screen.blit(time_text, (SCREEN_WIDTH//2 - time_text.get_width()//2, 300))

    restart_text = font.render("Press R to Restart, ESC to Quit", True, TEXT_COLOR)
    screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 380))

def main():
    player = Player()
    obstacles = []
    frame_counter = 0
    score = 0
    start_ticks = pygame.time.get_ticks()
    running = True
    game_over = False

    while running:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r and game_over:
                    # 重启游戏
                    player = Player()
                    obstacles = []
                    frame_counter = 0
                    score = 0
                    start_ticks = pygame.time.get_ticks()
                    game_over = False

        if not game_over:
            # 控制
            keys = pygame.key.get_pressed()
            player.update(keys)

            # 生成障碍物
            frame_counter += 1
            if frame_counter >= OBSTACLE_SPAWN_RATE:
                frame_counter = 0
                obstacles.append(Obstacle())

            # 更新障碍物
            new_obstacles = []
            for obs in obstacles:
                obs.update()
                if not obs.is_off_screen():
                    new_obstacles.append(obs)
            obstacles = new_obstacles

            # 碰撞检测
            for obs in obstacles:
                if player.rect.colliderect(obs.rect):
                    game_over = True
                    break

            # 分数计算: 每存活1秒加1分
            elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000.0
            score = int(elapsed_time)

        # 绘制
        screen.fill(BACKGROUND_COLOR)

        # 绘制玩家
        player.draw(screen)

        # 绘制障碍物
        for obs in obstacles:
            obs.draw(screen)

        # 绘制HUD
        elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000.0
        draw_hud(score, elapsed_time)

        # 游戏结束画面
        if game_over:
            draw_game_over(score, elapsed_time)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()