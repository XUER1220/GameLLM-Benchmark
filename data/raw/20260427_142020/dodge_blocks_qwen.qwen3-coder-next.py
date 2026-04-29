import pygame
import random
import sys

# 常量定义
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 60
PLAYER_Y_MARGIN = 40
PLAYER_SPEED = 7
OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 40
OBSTACLE_MIN_SPEED = 4
OBSTACLE_MAX_SPEED = 8
OBSTACLE_SPAWN_RATE = 40  # frames
SCORE_PER_SECOND = 1

# 颜色定义
COLOR_BACKGROUND = (30, 30, 30)
COLOR_PLAYER = (0, 200, 100)
COLOR_OBSTACLE = (220, 50, 50)
COLOR_TEXT = (255, 255, 255)

# 初始化Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Dodge Blocks Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 32)

# 全局变量
running = True
game_active = True
score = 0
frames_elapsed = 0
obstacles = []
player_rect = pygame.Rect((WINDOW_WIDTH - PLAYER_WIDTH) // 2, WINDOW_HEIGHT - PLAYER_Y_MARGIN - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)

# 随机种子固定
random.seed(42)

def reset_game():
    global game_active, score, frames_elapsed, obstacles, player_rect
    game_active = True
    score = 0
    frames_elapsed = 0
    obstacles = []
    player_rect.x = (WINDOW_WIDTH - PLAYER_WIDTH) // 2
    player_rect.y = WINDOW_HEIGHT - PLAYER_Y_MARGIN - PLAYER_HEIGHT

def spawn_obstacle():
    x = random.randint(0, WINDOW_WIDTH - OBSTACLE_WIDTH)
    speed = random.randint(OBSTACLE_MIN_SPEED, OBSTACLE_MAX_SPEED)
    obstacles.append({
        'rect': pygame.Rect(x, -OBSTACLE_HEIGHT, OBSTACLE_WIDTH, OBSTACLE_HEIGHT),
        'speed': speed
    })

def check_collision():
    for obstacle in obstacles:
        if player_rect.colliderect(obstacle['rect']):
            return True
    return False

def update():
    global frames_elapsed, score, game_active

    if not game_active:
        return

    frames_elapsed += 1

    # 计分（每1秒+1分）
    if frames_elapsed % FPS == 0:
        score += SCORE_PER_SECOND

    # 生成障碍物
    if frames_elapsed % OBSTACLE_SPAWN_RATE == 0:
        spawn_obstacle()

    # 移动障碍物
    for obstacle in obstacles[:]:
        obstacle['rect'].y += obstacle['speed']
        # 移除超出屏幕的障碍物
        if obstacle['rect'].top > WINDOW_HEIGHT:
            obstacles.remove(obstacle)

    # 碰撞检测
    if check_collision():
        game_active = False

def draw():
    screen.fill(COLOR_BACKGROUND)

    # 绘制玩家
    pygame.draw.rect(screen, COLOR_PLAYER, player_rect)

    # 绘制障碍物
    for obstacle in obstacles:
        pygame.draw.rect(screen, COLOR_OBSTACLE, obstacle['rect'])

    # HUD：分数和存活时间
    score_text = font.render(f"Score: {score}", True, COLOR_TEXT)
    screen.blit(score_text, (20, 20))
    
    # 游戏结束界面
    if not game_active:
        game_over_text = font.render("Game Over", True, (255, 80, 80))
        final_score_text = small_font.render(f"Final Score: {score}", True, COLOR_TEXT)
        restart_text = small_font.render("Press R to Restart or ESC to Exit", True, COLOR_TEXT)

        # 居中绘制
        screen.blit(game_over_text, ((WINDOW_WIDTH - game_over_text.get_width()) // 2, 
                                      WINDOW_HEIGHT // 2 - 80))
        screen.blit(final_score_text, ((WINDOW_WIDTH - final_score_text.get_width()) // 2, 
                                        WINDOW_HEIGHT // 2 + 20))
        screen.blit(restart_text, ((WINDOW_WIDTH - restart_text.get_width()) // 2, 
                                    WINDOW_HEIGHT // 2 + 70))

    pygame.display.flip()

def handle_input(keys):
    global player_rect
    if game_active:
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_rect.x += PLAYER_SPEED

        # 边界限制
        player_rect.left = max(0, player_rect.left)
        player_rect.right = min(WINDOW_WIDTH, player_rect.right)

def handle_event(event):
    global running, game_active
    if event.type == pygame.QUIT:
        running = False
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            running = False
        elif event.key == pygame.K_r and not game_active:
            reset_game()

# 主循环
reset_game()
while running:
    # 事件处理
    for event in pygame.event.get():
        handle_event(event)
    
    # 键盘输入
    keys = pygame.key.get_pressed()
    handle_input(keys)
    
    # 更新逻辑
    update()
    
    # 绘制画面
    draw()
    
    # 控制帧率
    clock.tick(FPS)

pygame.quit()
sys.exit()