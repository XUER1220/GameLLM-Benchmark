import pygame
import random

# 常量定义
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
LEVEL_WIDTH, LEVEL_HEIGHT = 3200, 600
FPS = 60

# 玩家参数
PLAYER_WIDTH, PLAYER_HEIGHT = 32, 48
PLAYER_SPEED_X = 5
PLAYER_JUMP_FORCE = -12
GRAVITY = 0.5
PLAYER_MAX_LIVES = 3

# 游戏常量
SCORE_PER_COIN = 100
SCORE_PER_ENEMY_STOMP = 200
COIN_WIDTH, COIN_HEIGHT = 18, 18
ENEMY_WIDTH, ENEMY_HEIGHT = 32, 32
FLAG_WIDTH, FLAG_HEIGHT = 20, 480

# 颜色定义
COLOR_PLAYER = (255, 0, 0)
COLOR_GROUND = (100, 80, 0)
COLOR_BRICK = (160, 82, 45)
COLOR_QUESTION_BLOCK = (255, 215, 0)
COLOR_PIPE = (0, 128, 0)
COLOR_ENEMY = (139, 69, 19)
COLOR_COIN = (255, 215, 0)
COLOR_FLAG_POLE = (255, 255, 255)
COLOR_FLAG_TOP = (255, 0, 0)
COLOR_HUD_TEXT = (255, 255, 255)
COLOR_GAME_TEXT = (255, 215, 0)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Super Mario Bros Medium")
    clock = pygame.time.Clock()
    random.seed(42)

    # 创建字体
    font_hud = pygame.font.SysFont(None, 24)
    font_game = pygame.font.SysFont(None, 48)

    # 游戏状态
    def reset_game():
        player = {
            'x': 50,
            'y': LEVEL_HEIGHT - PLAYER_HEIGHT - 50,
            'vx': 0,
            'vy': 0,
            'grounded': False,
            'lives': PLAYER_MAX_LIVES,
            'score': 0,
            'coins': 0,
            'last_safe_x': 50,
            'last_safe_y': LEVEL_HEIGHT - PLAYER_HEIGHT - 50,
            'alive': True
        }

        # 构建关卡：平台、砖块、问号块
        platforms = []
        # 地面
        platforms.extend([pygame.Rect(i * 64, LEVEL_HEIGHT - 64, 64, 64) for i in range(0, 4)])
        platforms.extend([pygame.Rect(i * 64 + 128, LEVEL_HEIGHT - 64, 64, 64) for i in range(4, 12)])
        platforms.extend([pygame.Rect(i * 64 + 448, LEVEL_HEIGHT - 64, 64, 64) for i in range(12, 26)])
        platforms.extend([pygame.Rect(i * 64 + 832, LEVEL_HEIGHT - 64, 64, 64) for i in range(26, 50)])
        platforms.extend([pygame.Rect(i * 64 + 1088, LEVEL_HEIGHT - 64, 64, 64) for i in range(50, 64)])
        
        # 平台、砖块和问号块
        platforms.append(pygame.Rect(150, LEVEL_HEIGHT - 200, 64, 64))  # 独立砖块
        platforms.append(pygame.Rect(300, LEVEL_HEIGHT - 200, 64, 64))
        platforms.append(pygame.Rect(450, LEVEL_HEIGHT - 200, 64, 64))
        platforms.append(pygame.Rect(600, LEVEL_HEIGHT - 200, 64, 64))
        platforms.append(pygame.Rect(750, LEVEL_HEIGHT - 200, 64, 64))
        platforms.append(pygame.Rect(900, LEVEL_HEIGHT - 250, 64, 64))
        platforms.append(pygame.Rect(1050, LEVEL_HEIGHT - 250, 64, 64))
        platforms.append(pygame.Rect(1200, LEVEL_HEIGHT - 250, 64, 64))
        platforms.append(pygame.Rect(1350, LEVEL_HEIGHT - 200, 64, 64))
        platforms.append(pygame.Rect(1500, LEVEL_HEIGHT - 200, 64, 64))
        platforms.append(pygame.Rect(1650, LEVEL_HEIGHT - 200, 64, 64))
        platforms.append(pygame.Rect(1800, LEVEL_HEIGHT - 200, 64, 64))

        # 问号块（用特殊标记）
        question_blocks = [
            pygame.Rect(150, LEVEL_HEIGHT - 350, 64, 64),
            pygame.Rect(450, LEVEL_HEIGHT - 350, 64, 64),
            pygame.Rect(1050, LEVEL_HEIGHT - 350, 64, 64),
            pygame.Rect(1350, LEVEL_HEIGHT - 350, 64, 64),
            pygame.Rect(1650, LEVEL_HEIGHT - 350, 64, 64)
        ]

        # 管道障碍（作为平台）
        pipes = [
            pygame.Rect(600, LEVEL_HEIGHT - 128 - 64, 64, 128),   # 短管道
            pygame.Rect(1000, LEVEL_HEIGHT - 192 - 96, 96, 192), # 中管道
            pygame.Rect(1800, LEVEL_HEIGHT - 128 - 64, 64, 128), # 短管道
            pygame.Rect(2200, LEVEL_HEIGHT - 128, 64, 128),      # 稍微靠上的平台当作管道替代
        ]

        # 台阶
        platforms.append(pygame.Rect(2600, LEVEL_HEIGHT - 96, 64, 96))
        platforms.append(pygame.Rect(2664, LEVEL_HEIGHT - 160, 64, 160))
        platforms.append(pygame.Rect(2728, LEVEL_HEIGHT - 224, 64, 224))
        platforms.append(pygame.Rect(2792, LEVEL_HEIGHT - 288, 64, 288))
        platforms.append(pygame.Rect(2856, LEVEL_HEIGHT - 352, 64, 352))
        platforms.append(pygame.Rect(2920, LEVEL_HEIGHT - 416, 64, 416))

        # 金币
        coins = [
            pygame.Rect(160 + 18, LEVEL_HEIGHT - 368, COIN_WIDTH, COIN_HEIGHT),
            pygame.Rect(460 + 18, LEVEL_HEIGHT - 368, COIN_WIDTH, COIN_HEIGHT),
            pygame.Rect(1060 + 18, LEVEL_HEIGHT - 368, COIN_WIDTH, COIN_HEIGHT),
            pygame.Rect(1360 + 18, LEVEL_HEIGHT - 368, COIN_WIDTH, COIN_HEIGHT),
            pygame.Rect(1660 + 18, LEVEL_HEIGHT - 368, COIN_WIDTH, COIN_HEIGHT),
            pygame.Rect(300 + 18, LEVEL_HEIGHT - 218, COIN_WIDTH, COIN_HEIGHT),
            pygame.Rect(450 + 18, LEVEL_HEIGHT - 218, COIN_WIDTH, COIN_HEIGHT),
            pygame.Rect(1200 + 18, LEVEL_HEIGHT - 218, COIN_WIDTH, COIN_HEIGHT),
            pygame.Rect(1500 + 18, LEVEL_HEIGHT - 218, COIN_WIDTH, COIN_HEIGHT),
            pygame.Rect(1650 + 18, LEVEL_HEIGHT - 218, COIN_WIDTH, COIN_HEIGHT),
            pygame.Rect(2730 + 18, LEVEL_HEIGHT - 224 + 100, COIN_WIDTH, COIN_HEIGHT),
            pygame.Rect(2900 + 18, LEVEL_HEIGHT - 434, COIN_WIDTH, COIN_HEIGHT),
        ]

        # 敌人
        enemies = [
            {'rect': pygame.Rect(800, LEVEL_HEIGHT - 64 - ENEMY_HEIGHT, ENEMY_WIDTH, ENEMY_HEIGHT), 'vx': -1, 'dead': False},
            {'rect': pygame.Rect(1500, LEVEL_HEIGHT - 64 - ENEMY_HEIGHT, ENEMY_WIDTH, ENEMY_HEIGHT), 'vx': -1, 'dead': False},
            {'rect': pygame.Rect(2100, LEVEL_HEIGHT - 64 - ENEMY_HEIGHT, ENEMY_WIDTH, ENEMY_HEIGHT), 'vx': 1, 'dead': False},
        ]

        # 终点旗杆
        flag = {
            'x': 3050,
            'y': LEVEL_HEIGHT - FLAG_HEIGHT,
            'rect': pygame.Rect(3050, LEVEL_HEIGHT - FLAG_HEIGHT, FLAG_WIDTH, FLAG_HEIGHT),
            'top_rect': pygame.Rect(3050, LEVEL_HEIGHT - FLAG_HEIGHT - 20, 40, 20)
        }

        return player, platforms, question_blocks, pipes, coins, enemies, flag

    player, platforms, question_blocks, pipes, coins, enemies, flag = reset_game()
    game_state = "running"  # running, gameover, win

    # 摄像机
    camera_x = 0

    # 输入处理
    keys = pygame.key.get_pressed()
    left_pressed = False
    right_pressed = False
    jump_pressed = False

    while True:
        # 事件循环
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                if event.key == pygame.K_r and game_state != "running":
                    player, platforms, question_blocks, pipes, coins, enemies, flag = reset_game()
                    camera_x = 0
                    game_state = "running"
                if event.key == pygame.K_LEFT:
                    left_pressed = True
                if event.key == pygame.K_RIGHT:
                    right_pressed = True
                if event.key == pygame.K_SPACE and player['grounded'] and game_state == "running":
                    player['vy'] = PLAYER_JUMP_FORCE
                    player['grounded'] = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    left_pressed = False
                if event.key == pygame.K_RIGHT:
                    right_pressed = False

        if game_state == "running":
            # 玩家移动
            player['vx'] = 0
            if left_pressed:
                player['vx'] = -PLAYER_SPEED_X
            if right_pressed:
                player['vx'] = PLAYER_SPEED_X

            # 物理
            player['vy'] += GRAVITY
            player['x'] += player['vx']
            player['y'] += player['vy']

            # 玩家与平台碰撞（地面、砖块、问号块、平台）
            player_rect = pygame.Rect(player['x'], player['y'], PLAYER_WIDTH, PLAYER_HEIGHT)
            player['grounded'] = False
            on_platform = False

            # 所有静态障碍物合并处理
            all_platforms = platforms + pipes + question_blocks
            for p in all_platforms:
                if player_rect.colliderect(p):
                    if player['vy'] > 0 and player['y'] - player['vy'] + PLAYER_HEIGHT <= p.top + 2:
                        player['y'] = p.top - PLAYER_HEIGHT
                        player['vy'] = 0
                        player['grounded'] = True
                    elif player['vy'] < 0 and player['y'] - player['vy'] >= p.bottom - 2:
                        player['y'] = p.bottom
                        player['vy'] = 0

            # 管道与平台边界处理（左右碰撞避免穿模）
            for p in all_platforms:
                if player_rect.colliderect(p):
                    if player['vx'] > 0:
                        player['x'] = p.left - PLAYER_WIDTH
                    elif player['vx'] < 0:
                        player['x'] = p.right

            # 坑洞检测（掉落）
            if player['y'] > LEVEL_HEIGHT:
                player['lives'] -= 1
                player['x'] = player['last_safe_x']
                player['y'] = player['last_safe_y']
                player['vy'] = 0
                if player['lives'] == 0:
                    game_state = "gameover"

            # 挖掘机式边界限制
            if player['x'] < 0:
                player['x'] = 0

            # 保存安全位置
            player['last_safe_x'] = player['x']
            player['last_safe_y'] = player['y']

            # 敌人更新
            for enemy in enemies:
                if enemy['dead']:
                    continue
                enemy['rect'].x += enemy['vx']
                # 地面检测
                ground_y = LEVEL_HEIGHT - 64
                enemy_y_below = enemy['rect'].bottom
                if enemy_y_below <= ground_y + 1 and enemy_y_below + 1 > ground_y:
                    # 简单水平巡逻（无平台跳跃）
                    # 简单边界检测：遇到障碍回头（用平台边界限制）
                    for p in all_platforms:
                        if enemy['rect'].colliderect(p):
                            enemy['vx'] = -enemy['vx']
                            enemy['rect'].x += enemy['vx']
                            break
                # 限制巡逻范围（粗略）
                if enemy['rect'].left < 600 or enemy['rect'].right > 900:
                    enemy['vx'] = -enemy['vx']
                elif enemy['rect'].left < 1600 or enemy['rect'].right > 1800:
                    enemy['vx'] = -enemy['vx']
                elif enemy['rect'].left < 2200 or enemy['rect'].right > 2400:
                    enemy['vx'] = -enemy['vx']

            # 敌人与玩家碰撞
            for enemy in enemies:
                if enemy['dead']:
                    continue
                if player_rect.colliderect(enemy['rect']):
                    # 踩到敌人（从上方下落，且敌人在下方）
                    if player['vy'] > 0 and player['y'] - player['vy'] + PLAYER_HEIGHT <= enemy['rect'].top + 2:
                        player['score'] += SCORE_PER_ENEMY_STOMP
                        player['vy'] = PLAYER_JUMP_FORCE * 0.6
                        enemy['dead'] = True
                    else:
                        # 碰到敌人侧面
                        player['lives'] -= 1
                        player['x'] = player['last_safe_x']
                        player['y'] = player['last_safe_y']
                        player['vy'] = 0
                        if player['lives'] == 0:
                            game_state = "gameover"
                        break

            # 金币收集
            for i, coin in enumerate(coins):
                if coin and player_rect.colliderect(coin):
                    player['score'] += SCORE_PER_COIN
                    player['coins'] += 1
                    coins[i] = None

            # 清除空金币
            coins = [c for c in coins if c is not None]

            # 终点旗杆检测
            if (player_rect.colliderect(flag['rect']) or 
                player_rect.colliderect(flag['top_rect'])):
                game_state = "win"

            # 摄像机跟随
            camera_x = player['x'] - SCREEN_WIDTH // 2
            if camera_x < 0:
                camera_x = 0
            if camera_x > LEVEL_WIDTH - SCREEN_WIDTH:
                camera_x = LEVEL_WIDTH - SCREEN_WIDTH

        # 绘制
        screen.fill((135, 206, 235))  # 天空蓝

        # 地面
        for p in platforms:
            if p.y >= LEVEL_HEIGHT - 64 and p.h == 64 and p.w == 64:  # 地面块
                pygame.draw.rect(screen, COLOR_GROUND, (p.x - camera_x, p.y, p.w, p.h))
                # 地面细节
                pygame.draw.rect(screen, (90, 70, 0), 
                                 (p.x - camera_x, p.y + 56, p.w, 8))

        # 管道
        for p in pipes:
            if p not in platforms:
                pygame.draw.rect(screen, COLOR_PIPE, (p.x - camera_x, p.y, p.w, p.h))
                # 管道顶部边缘
                pygame.draw.rect(screen, (0, 100, 0), 
                                 (p.x - camera_x, p.y, p.w, 8))
                # 管道凹槽线
                pygame.draw.rect(screen, (0, 150, 0), 
                                 (p.x - camera_x + 4, p.y + 16, p.w - 8, 4))

        # 砖块
        for p in platforms:
            if LEVEL_HEIGHT - 64 != p.y:
                pygame.draw.rect(screen, COLOR_BRICK, (p.x - camera_x, p.y, p.w, p.h))
                # 砖块纹理
                pygame.draw.rect(screen, (140, 60, 30), 
                                 (p.x - camera_x, p.y + 10, p.w, 2))
                pygame.draw.rect(screen, (140, 60, 30), 
                                 (p.x - camera_x + p.w // 2, p.y, 2, p.h))

        # 问号块
        for p in question_blocks:
            pygame.draw.rect(screen, COLOR_QUESTION_BLOCK, (p.x - camera_x, p.y, p.w, p.h))
            pygame.draw.rect(screen, (139, 69, 19), (p.x - camera_x, p.y, p.w, p.h), 2)
            font_q = pygame.font.SysFont(None, 32)
            text_q = font_q.render("?", True, (0, 0, 0))
            screen.blit(text_q, (p.x - camera_x + p.w // 3, p.y + p.h // 4))

        # 金币
        for coin in coins:
            if coin:
                pygame.draw.ellipse(screen, COLOR_COIN, 
                                    (coin.x - camera_x, coin.y, coin.w, coin.h))
                pygame.draw.ellipse(screen, (255, 165, 0), 
                                    (coin.x - camera_x + 2, coin.y + 2, coin.w - 4, coin.h - 4), 2)

        # 敌人
        for enemy in enemies:
            if not enemy['dead']:
                e_rect = enemy['rect']
                pygame.draw.ellipse(screen, COLOR_ENEMY, 
                                    (e_rect.x - camera_x, e_rect.y, e_rect.w, e_rect.h))
                # 简单眼睛
                pygame.draw.circle(screen, (255, 255, 255), 
                                   (e_rect.x - camera_x + 8, e_rect.y + 8), 3)
                pygame.draw.circle(screen, (0, 0, 0), 
                                   (e_rect.x - camera_x + 8, e_rect.y + 8), 1)
                pygame.draw.circle(screen, (255, 255, 255), 
                                   (e_rect.x - camera_x + 24, e_rect.y + 8), 3)
                pygame.draw.circle(screen, (0, 0, 0), 
                                   (e_rect.x - camera_x + 24, e_rect.y + 8), 1)

        # 玩家
        if player['alive'] and game_state == "running":
            pygame.draw.rect(screen, COLOR_PLAYER, 
                             (player['x'] - camera_x, player['y'], player['width'], player['height']))
            # 简单帽子（红色）
            pygame.draw.rect(screen, (255, 0, 0), 
                             (player['x'] - camera_x - 2, player['y'], player['width'] + 4, 8))
            # 简单眼睛
            pygame.draw.circle(screen, (0, 0, 0), 
                               (player['x'] - camera_x + 16, player['y'] + 12), 2)

        # 旗杆
        # 旗杆主体
        pygame.draw.rect(screen, COLOR_FLAG_POLE, 
                         (flag['rect'].x - camera_x, flag['rect'].y, flag['rect'].w, flag['rect'].h))
        # 旗杆顶部球
        pygame.draw.circle(screen, COLOR_FLAG_TOP, 
                           (flag['rect'].x - camera_x + 10, flag['rect'].y - 10), 10)
        # 旗帜
        if game_state != "win":
            pygame.draw.polygon(screen, COLOR_FLAG_TOP, [
                (flag['rect'].x - camera_x + 20, flag['rect'].y + 20),
                (flag['rect'].x - camera_x + 60, flag['rect'].y + 40),
                (flag['rect'].x - camera_x + 20, flag['rect'].y + 60)
            ])

        # HUD（固定屏幕上方）
        hud_text = f"Score: {player['score']}     Coins: {player['coins']}     Lives: {player['lives']}"
        hud_surface = font_hud.render(hud_text, True, COLOR_HUD_TEXT)
        screen.blit(hud_surface, (10, 10))

        if game_state == "gameover":
            game_over_text = font_game.render("Game Over", True, COLOR_GAME_TEXT)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT // 2 - 50))
            final_score_text = font_game.render(f"Final Score: {player['score']}", True, COLOR_GAME_TEXT)
            screen.blit(final_score_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 10))
            restart_text = font_game.render("Press R to Restart", True, COLOR_GAME_TEXT)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 240, SCREEN_HEIGHT // 2 + 70))
        elif game_state == "win":
            win_text = font_game.render("You Win!", True, COLOR_GAME_TEXT)
            screen.blit(win_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 50))
            final_score_text = font_game.render(f"Score: {player['score']}", True, COLOR_GAME_TEXT)
            screen.blit(final_score_text, (SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT // 2 + 10))
            restart_text = font_game.render("Press R to Restart", True, COLOR_GAME_TEXT)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 240, SCREEN_HEIGHT // 2 + 70))

        pygame.display.flip()
        clock.tick(FPS)

    return pygame.quit()

if __name__ == "__main__":
    main()