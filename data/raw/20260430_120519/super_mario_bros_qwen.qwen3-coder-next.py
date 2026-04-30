import pygame
import sys
import random

# 初始化 Pygame
pygame.init()

# 常量定义
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
LEVEL_WIDTH, LEVEL_HEIGHT = 3200, 600
FPS = 60
PLAYER_WIDTH, PLAYER_HEIGHT = 32, 48
PLAYER_SPEED_X = 5
PLAYER_JUMP_SPEED = -12
GRAVITY = 0.5
ENEMY_SPEED = 2
ENEMY_WIDTH, ENEMY_HEIGHT = 32, 32
COIN_WIDTH, COIN_HEIGHT = 18, 18
PLAYER_LIVES = 3

# 颜色定义
COLOR_SKY = (135, 206, 235)
COLOR_GROUND = (76, 153, 0)
COLOR_BRICK = (165, 42, 42)
COLOR_QUESTION = (255, 215, 0)
COLOR_PIPE = (0, 128, 0)
COLOR_PIPE_LIP = (102, 204, 0)
COLOR_ENEMY = (210, 105, 30)
COLOR_COIN = (255, 215, 0)
COLOR_FLAG_POLE = (255, 255, 255)
COLOR_FLAG_TOP = (255, 0, 0)
COLOR_HUD_TEXT = (255, 255, 255)
COLOR_UI_BG = (0, 0, 0)
COLOR_EXIT_MESSAGE = (255, 255, 0)

# 设置显示窗口和时钟
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario Bros Medium")
clock = pygame.time.Clock()

# 全局变量
level_data = {
    'ground_rects': [],
    'brick_rects': [],
    'brick_positions': [],
    'question_rects': [],
    'question_positions': [],
    'pipe_rects': [],
    'pipe_positions': [],
    'step_rects': [],
    'step_positions': [],
    'enemy_rects': [],
    'enemy_positions': [],
    'enemy_directions': [],
    'coin_rects': [],
    'coin_positions': [],
    'flag_pole_rect': None,
    'flag_ball_rect': None,
    'start_pos': (100, 450),
    'safe_positions': [(100, 450)],
    '坑洞位置': [(700, 820), (1500, 1650)]
}

player = {}
camera = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
game_state = "PLAYING"  # "PLAYING", "WIN", "LOST"
score = 0
coins = 0
lives = PLAYER_LIVES

def init_level():
    global level_data, player, camera, score, coins, lives, game_state
    score = 0
    coins = 0
    lives = PLAYER_LIVES
    game_state = "PLAYING"
    
    level_data['ground_rects'] = []
    level_data['brick_rects'] = []
    level_data['brick_positions'] = []
    level_data['question_rects'] = []
    level_data['question_positions'] = []
    level_data['pipe_rects'] = []
    level_data['pipe_positions'] = []
    level_data['step_rects'] = []
    level_data['step_positions'] = []
    level_data['enemy_rects'] = []
    level_data['enemy_positions'] = []
    level_data['enemy_directions'] = []
    level_data['coin_rects'] = []
    level_data['coin_positions'] = []
    level_data['flag_pole_rect'] = None
    level_data['flag_ball_rect'] = None
    level_data['safe_positions'] = [(100, 450)]

    # 地面分段，避开坑洞
    ground_segments = [
        (0, 500, 700, 100),      # 起始平地
        (820, 500, 680, 100),    # 第一坑洞后
        (1650, 500, 350, 100),   # 第二坑洞后
        (2000, 500, 300, 100),   # 最近终点
        (2300, 500, 900, 100)    # 终点区域延伸
    ]
    for seg in ground_segments:
        level_data['ground_rects'].append(pygame.Rect(seg))

    # 砖块区域
    brick_layout = [
        (200, 400), (230, 400), (260, 400),
        (250, 300),  # 悬挂的3块
        (420, 400), (450, 400), (480, 400),
        (550, 300), (580, 300), (610, 300),
        (1100, 400), (1130, 400), (1160, 400)
    ]
    for x, y in brick_layout:
        rect = pygame.Rect(x, y, 30, 30)
        level_data['brick_rects'].append(rect)
        level_data['brick_positions'].append((x, y))

    # 问号块区域
    question_layout = [
        (220, 300),  # 中间夹在砖块之间
        (440, 300),
        (550, 200), (580, 200), (610, 200),
        (1110, 300)
    ]
    for x, y in question_layout:
        rect = pygame.Rect(x, y, 30, 30)
        level_data['question_rects'].append(rect)
        level_data['question_positions'].append((x, y))

    # 管道区域
    pipe_layout = [
        (600, 450, 48, 50),  # 小管道
        (1200, 425, 48, 75), # 中等管道
        (1700, 400, 48, 100), # 高管道
        (1950, 450, 48, 50)   # 小管道
    ]
    for x, y, w, h in pipe_layout:
        rect = pygame.Rect(x, y, w, h)
        level_data['pipe_rects'].append(rect)
        level_data['pipe_positions'].append((x, y, w, h))

    # 台阶区域
    step_layout = [
        (2100, 440, 30, 60),
        (2130, 400, 30, 60),
        (2160, 360, 30, 60),
        (2190, 320, 30, 60),
        (2220, 280, 30, 60),
        (2250, 240, 30, 60),
        (2280, 200, 30, 60)
    ]
    for x, y, w, h in step_layout:
        rect = pygame.Rect(x, y, w, h)
        level_data['step_rects'].append(rect)
        level_data['step_positions'].append((x, y, w, h))

    # 敌人区域
    enemy_layout = [
        (400, 450), (900, 450), (1400, 450)
    ]
    for x, y in enemy_layout:
        rect = pygame.Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT)
        level_data['enemy_rects'].append(rect)
        level_data['enemy_positions'].append((x, y))
        level_data['enemy_directions'].append(1)  # 正右方向

    # 金币区域
    coin_layout = [
        (210, 380), (270, 380),
        (430, 380), (490, 380),
        (560, 280), (590, 280), (620, 280),
        (1120, 380), (1170, 380),
        (1800, 400), (1850, 400), (1900, 400)
    ]
    for x, y in coin_layout:
        rect = pygame.Rect(x, y, COIN_WIDTH, COIN_HEIGHT)
        level_data['coin_rects'].append(rect)
        level_data['coin_positions'].append((x, y))

    # 终点旗杆
    flag_x = 2800
    flag_y = 150
    level_data['flag_pole_rect'] = pygame.Rect(flag_x, flag_y, 10, 350)
    level_data['flag_ball_rect'] = pygame.Rect(flag_x + 10, flag_y, 30, 30)

    # 玩家状态
    player = {
        'rect': pygame.Rect(100, 450, PLAYER_WIDTH, PLAYER_HEIGHT),
        'vel_x': 0,
        'vel_y': 0,
        'is_jumping': False,
        'on_ground': False,
        'safe_index': 0
    }

# 带缓存的地面检测函数
def get_ground_collisions(player_rect):
    collisions = []
    # 检查地面、砖块、问号块、管道、台阶
    for rect in level_data['ground_rects'] + level_data['brick_rects'] + level_data['question_rects'] + level_data['pipe_rects'] + level_data['step_rects']:
        if player_rect.colliderect(rect):
            collisions.append((rect, 'solid'))
    return collisions

# 碰撞处理
def resolve_collision(player_rect, vel_x, vel_y):
    player_rect.x += vel_x
    collisions_x = get_ground_collisions(player_rect)
    for rect, _ in collisions_x:
        if vel_x > 0:  # 向右碰撞
            player_rect.right = rect.left
        elif vel_x < 0:  # 向左碰撞
            player_rect.left = rect.right
    
    player_rect.y += vel_y
    collisions_y = get_ground_collisions(player_rect)
    player['on_ground'] = False
    for rect, _ in collisions_y:
        if vel_y > 0:  # 下落
            player_rect.bottom = rect.top
            player['on_ground'] = True
            player['is_jumping'] = False
            player['vel_y'] = 0
        elif vel_y < 0:  # 顶头
            player_rect.top = rect.bottom
            player['vel_y'] = 0
    
    # 检查敌人碰撞（仅在垂直方向）
    for i, enemy_rect in enumerate(level_data['enemy_rects']):
        if player_rect.colliderect(enemy_rect):
            if vel_y > 0 and player_rect.bottom - 10 <= enemy_rect.top:
                # 踩扁敌人
                level_data['enemy_rects'].pop(i)
                level_data['enemy_positions'].pop(i)
                level_data['enemy_directions'].pop(i)
                score_add(200)
                return True
            else:
                # 被敌人碰到
                handle_death()
                return False
    
    return True

def handle_death():
    global lives, game_state, player, camera
    
    lives -= 1
    if lives <= 0:
        game_state = "LOST"
        player['rect'] = pygame.Rect(-100, -100, PLAYER_WIDTH, PLAYER_HEIGHT)
        return
    
    # 回到最近安全位置
    safe_x, safe_y = level_data['safe_positions'][player['safe_index']]
    player['rect'].x = safe_x
    player['rect'].y = safe_y
    player['vel_x'] = 0
    player['vel_y'] = 0
    player['is_jumping'] = False
    player['on_ground'] = True

def score_add(points):
    global score
    score += points

def update_player():
    global player
    
    keys = pygame.key.get_pressed()
    
    # 水平移动
    if keys[pygame.K_LEFT]:
        player['vel_x'] = -PLAYER_SPEED_X
    elif keys[pygame.K_RIGHT]:
        player['vel_x'] = PLAYER_SPEED_X
    else:
        player['vel_x'] = 0
    
    # 跳跃
    if keys[pygame.K_SPACE] and player['on_ground']:
        player['vel_y'] = PLAYER_JUMP_SPEED
        player['is_jumping'] = True
    
    # 应用重力
    if not player['on_ground']:
        player['vel_y'] += GRAVITY
    
    # 保存旧位置用于回退
    old_x, old_y = player['rect'].x, player['rect'].y
    
    # 碰撞解决
    if not resolve_collision(player['rect'], player['vel_x'], player['vel_y']):
        return  # 如果死亡，提前返回
    
    # 检查是否掉落坑洞
    if player['rect'].y > LEVEL_HEIGHT - 20:
        handle_death()
        return
    
    # 更新摄像机
    camera.x = player['rect'].x - SCREEN_WIDTH // 2
    camera.clamp_ip(pygame.Rect(0, 0, LEVEL_WIDTH, LEVEL_HEIGHT))

def update_enemies():
    for i, enemy_rect in enumerate(level_data['enemy_rects']):
        dir = level_data['enemy_directions'][i]
        enemy_rect.x += dir * ENEMY_SPEED
        
        # 检查碰撞地面边界（只做简单处理）
        ground_rects = level_data['ground_rects'] + level_data['brick_rects'] + level_data['question_rects'] + level_data['pipe_rects'] + level_data['step_rects']
        collided = False
        for ground in ground_rects:
            if enemy_rect.colliderect(ground) and enemy_rect.bottom == ground.top:
                # 在平台上滚动，不处理（继续）
                pass
            elif enemy_rect.colliderect(ground):
                if dir > 0:
                    enemy_rect.right = ground.left
                    level_data['enemy_directions'][i] = -1
                else:
                    enemy_rect.left = ground.right
                    level_data['enemy_directions'][i] = 1
                collided = True
                break
        
        # 如果没有碰到边界，检查是否掉落
        if not collided:
            test_y = enemy_rect.copy()
            test_y.y += 1
            under_grounds = level_data['ground_rects'] + level_data['brick_rects'] + level_data['question_rects'] + level_data['pipe_rects'] + level_data['step_rects']
            if not any(test_y.colliderect(g) for g in under_grounds):
                # 将敌人回溯一步
                enemy_rect.x -= dir * ENEMY_SPEED

def check_items():
    global coins, score
    # 金币收集
    player_rect = player['rect']
    for i in range(len(level_data['coin_rects']) - 1, -1, -1):
        coin_rect = level_data['coin_rects'][i]
        if player_rect.colliderect(coin_rect):
            level_data['coin_rects'].pop(i)
            level_data['coin_positions'].pop(i)
            coins += 1
            score_add(100)
    
    # 旗杆判定
    if level_data['flag_pole_rect'] and player_rect.colliderect(level_data['flag_pole_rect']):
        # 检查是否还在游戏进行中
        if game_state == "PLAYING":
            game_state = "WIN"

def draw():
    screen.fill(COLOR_SKY)
    
    # 绘制关卡元素（相对摄像机）
    camera_x, camera_y = camera.topleft
    
    # 绘制地面
    for rect in level_data['ground_rects']:
        pygame.draw.rect(screen, COLOR_GROUND, rect.move(-camera_x, -camera_y))
        # 给地面加边框
        pygame.draw.rect(screen, (59, 111, 0), rect.move(-camera_x, -camera_y), 2)
    
    # 绘制砖块
    for rect in level_data['brick_rects']:
        pygame.draw.rect(screen, COLOR_BRICK, rect.move(-camera_x, -camera_y))
        pygame.draw.rect(screen, (100, 20, 10), rect.move(-camera_x, -camera_y), 2)
    
    # 绘制问号块
    for rect in level_data['question_rects']:
        pygame.draw.rect(screen, COLOR_QUESTION, rect.move(-camera_x, -camera_y))
        pygame.draw.rect(screen, (165, 132, 0), rect.move(-camera_x, -camera_y), 2)
        font = pygame.font.SysFont(None, 20)
        text = font.render('?', True, (0, 0, 0))
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect.move(-camera_x, -camera_y))
    
    # 绘制管道
    for x, y, w, h in level_data['pipe_positions']:
        pipe_rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(screen, COLOR_PIPE, pipe_rect.move(-camera_x, -camera_y))
        # 管道顶部边框
        pygame.draw.rect(screen, COLOR_PIPE_LIP, (pipe_rect.x, pipe_rect.y, pipe_rect.width, 10).move(-camera_x, -camera_y))
        pygame.draw.rect(screen, (0, 80, 0), pipe_rect.move(-camera_x, -camera_y), 2)
    
    # 绘制台阶
    for x, y, w, h in level_data['step_positions']:
        step_rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(screen, COLOR_BRICK, step_rect.move(-camera_x, -camera_y))
        pygame.draw.rect(screen, (100, 20, 10), step_rect.move(-camera_x, -camera_y), 2)
    
    # 绘制敌人
    for rect in level_data['enemy_rects']:
        pygame.draw.ellipse(screen, COLOR_ENEMY, rect.move(-camera_x, -camera_y))
        # 简单的脸部
        pygame.draw.circle(screen, (255, 255, 255), (rect.left - camera_x + 8, rect.top - camera_y + 8), 3)
        pygame.draw.circle(screen, (255, 255, 255), (rect.left - camera_x + 24, rect.top - camera_y + 8), 3)
        pygame.draw.circle(screen, (0, 0, 0), (rect.left - camera_x + 8, rect.top - camera_y + 8), 1)
        pygame.draw.circle(screen, (0, 0, 0), (rect.left - camera_x + 24, rect.top - camera_y + 8), 1)
    
    # 绘制金币
    for rect in level_data['coin_rects']:
        pygame.draw.ellipse(screen, COLOR_COIN, rect.move(-camera_x, -camera_y))
        pygame.draw.circle(screen, (255, 215, 0), (rect.left - camera_x + COIN_WIDTH // 2, rect.top - camera_y + COIN_HEIGHT // 2), 8)
    
    # 绘制旗杆
    if level_data['flag_pole_rect']:
        pole = level_data['flag_pole_rect'].move(-camera_x, -camera_y)
        pygame.draw.rect(screen, COLOR_FLAG_POLE, pole)
        # 底部平台
        platform = pygame.Rect(pole.x - 10, pole.bottom - 20, 30, 10)
        pygame.draw.rect(screen, COLOR_GROUND, platform)
        pygame.draw.rect(screen, (59, 111, 0), platform, 2)
    
    # 绘制旗球
    if level_data['flag_ball_rect']:
        ball = level_data['flag_ball_rect'].move(-camera_x, -camera_y)
        pygame.draw.circle(screen, COLOR_FLAG_TOP, (ball.left + 15, ball.top + 15), 10)
        # 简单旗帜
        pygame.draw.polygon(screen, COLOR_FLAG_TOP, [
            (ball.left + 30, ball.top - 10),
            (ball.left + 60, ball.top),
            (ball.left + 30, ball.top + 10)
        ])
    
    # 绘制玩家
    if game_state == "PLAYING" or lives > 0:
        p_rect = player['rect'].move(-camera_x, -camera_y)
        # 简单马里奥风格图形
        # 身体
        pygame.draw.rect(screen, (255, 0, 0), p_rect)
        # 帽子
        pygame.draw.rect(screen, (200, 0, 0), (p_rect.x, p_rect.y - 5, p_rect.width, 8))
        # 眼睛（方向判断）
        if player['vel_x'] >= 0:
            pygame.draw.circle(screen, (255, 255, 255), (p_rect.x + 22, p_rect.y + 12), 3)
            pygame.draw.circle(screen, (0, 0, 0), (p_rect.x + 24, p_rect.y + 12), 1)
        else:
            pygame.draw.circle(screen, (255, 255, 255), (p_rect.x + 10, p_rect.y + 12), 3)
            pygame.draw.circle(screen, (0, 0, 0), (p_rect.x + 8, p_rect.y + 12), 1)
    
    # HUD
    hud_font = pygame.font.SysFont(None, 36)
    score_text = hud_font.render(f"SCORE: {score}", True, COLOR_HUD_TEXT)
    coin_text = hud_font.render(f"COINS: {coins}", True, COLOR_HUD_TEXT)
    lives_text = hud_font.render(f"LIVES: {lives}", True, COLOR_HUD_TEXT)
    
    screen.blit(score_text, (20, 20))
    screen.blit(coin_text, (250, 20))
    screen.blit(lives_text, (480, 20))
    
    # 游戏结束或胜利信息
    if game_state in ["WIN", "LOST"]:
        screen.fill(COLOR_UI_BG, (0, 200, SCREEN_WIDTH, 200))
        
        if game_state == "WIN":
            end_text1 = hud_font.render("YOU WIN!", True, COLOR_EXIT_MESSAGE)
            end_text2 = hud_font.render(f"FINAL SCORE: {score}   COINS: {coins}", True, COLOR_HUD_TEXT)
            end_text3 = hud_font.render("Press R to Restart", True, COLOR_HUD_TEXT)
        else:
            end_text1 = hud_font.render("GAME OVER", True, COLOR_EXIT_MESSAGE)
            end_text2 = hud_font.render(f"FINAL SCORE: {score}   COINS: {coins}", True, COLOR_HUD_TEXT)
            end_text3 = hud_font.render("Press R to Restart", True, COLOR_HUD_TEXT)
        
        screen.blit(end_text1, (SCREEN_WIDTH // 2 - end_text1.get_width() // 2, 220))
        screen.blit(end_text2, (SCREEN_WIDTH // 2 - end_text2.get_width() // 2, 270))
        screen.blit(end_text3, (SCREEN_WIDTH // 2 - end_text3.get_width() // 2, 320))
    
    pygame.display.flip()

def main():
    global player, game_state
    random.seed(42)
    init_level()
    
    while True:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    if game_state in ["WIN", "LOST"]:
                        init_level()
        
        if game_state == "PLAYING":
            update_player()
            update_enemies()
            check_items()
        
        draw()
        clock.tick(FPS)

if __name__ == "__main__":
    main()