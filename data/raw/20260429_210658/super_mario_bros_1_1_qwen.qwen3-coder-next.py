import pygame
import sys

# 初始化pygame
pygame.init()
pygame.font.init()

# 常量定义
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
LEVEL_WIDTH, LEVEL_HEIGHT = 3200, 600
FPS = 60
PLAYER_SIZE = (32, 48)
PLAYER_SPEED_X = 5
PLAYER_JUMP_FORCE = -12
GRAVITY = 0.5
COIN_SIZE = (18, 18)
ENEMY_SIZE = (32, 32)
NUM_LIVES = 3
SCORE_COIN = 100
SCORE_ENEMY_STOMP = 200

# 颜色定义
COLOR_PLAYER = (255, 87, 34)     # Mario red
COLOR_GROUND = (139, 69, 19)    # Brown
COLOR_BRICK = (160, 82, 45)     # Brick red
COLOR_QUESTION_BLOCK = (255, 215, 0)  # Gold
COLOR_PIPE = (34, 139, 34)      # Green
COLOR_ENEMY = (160, 82, 45)     # Goomba brown
COLOR_COIN = (255, 215, 0)      # Gold
COLOR_FLAG_POLE = (238, 238, 238)  # Silver
COLOR_FLAG_TOP = (255, 0, 0)    # Red
COLOR_FLAG_CLOTH = (255, 255, 255)  # White

# 关卡：地砖
platforms = []

# 地面：从x=0到x=3200，y=550~600（高度50）
for x in range(0, 3200, 50):
    if (500 <= x < 800) or (1300 <= x < 1500) or (2100 <= x < 2300):  # 坑洞
        continue
    platforms.append(pygame.Rect(x, 550, 50, 50))

# 块与问号块
blocks = []
blocks.append(pygame.Rect(200, 400, 40, 40))   # 砖块
blocks.append(pygame.Rect(300, 400, 40, 40))   # 砖块
blocks.append(pygame.Rect(340, 400, 40, 40))  # 砖块
blocks.append(pygame.Rect(380, 400, 40, 40))  # 砖块
blocks.append(pygame.Rect(300, 200, 40, 40))  # 问号块上面
blocks.append(pygame.Rect(340, 200, 40, 40))  # 砖块
blocks.append(pygame.Rect(380, 200, 40, 40))  # 砖块
blocks.append(pygame.Rect(600, 400, 40, 40))  # 问号块
blocks.append(pygame.Rect(640, 400, 40, 40))  # 砖块
blocks.append(pygame.Rect(680, 400, 40, 40))  # 砖块
blocks.append(pygame.Rect(1100, 400, 40, 40))  # 砖块
blocks.append(pygame.Rect(1140, 400, 40, 40))  # 问号块
blocks.append(pygame.Rect(1180, 400, 40, 40))  # 砖块

# 金币
coins = []
coins.append(pygame.Rect(220, 350, 18, 18))
coins.append(pygame.Rect(260, 350, 18, 18))
coins.append(pygame.Rect(320, 350, 18, 18))
coins.append(pygame.Rect(1320, 400, 18, 18))
coins.append(pygame.Rect(1360, 400, 18, 18))
coins.append(pygame.Rect(1400, 400, 18, 18))
coins.append(pygame.Rect(1540, 400, 18, 18))
coins.append(pygame.Rect(1580, 400, 18, 18))
coins.append(pygame.Rect(1620, 400, 18, 18))
coins.append(pygame.Rect(2000, 350, 18, 18))
coins.append(pygame.Rect(2040, 350, 18, 18))
coins.append(pygame.Rect(2900, 400, 18, 18))

# 管道
pipes = []
pipes.append(pygame.Rect(850, 500, 60, 50))  # 管道高50
pipes.append(pygame.Rect(950, 470, 60, 80))  # 管道高80
pipes.append(pygame.Rect(1750, 520, 60, 30))  # 小管道
pipes.append(pygame.Rect(2400, 480, 60, 70))  # 管道高70

# 敌人（巡逻敌人）
enemies = []
enemy_positions = [700, 1200, 2500]
for i, pos in enumerate(enemy_positions):
    enemies.append({
        "rect": pygame.Rect(pos, 518, 32, 32),
        "dir": 1,
        "speed": 1
    })

# 旗杆终点
flag_pole = pygame.Rect(3100, 200, 8, 350)  # 杆子
flag_top = pygame.Rect(3092, 190, 24, 20)   # 旗球
flag_cloth = pygame.Rect(3100, 250, 60, 40)  # 旗布

# 安全点（出生点、重生点）
checkpoint = pygame.Rect(0, 520, 40, 80)


def create_player():
    rect = pygame.Rect(50, 520, PLAYER_SIZE[0], PLAYER_SIZE[1])
    return {
        "rect": rect,
        "vy": 0,
        "is_jumping": False,
        "x": 50,
        "y": 520,
        "dead": False
    }


def reset_game():
    player = create_player()
    coins_remaining = coins.copy()
    enemies_remaining = [dict(e) for e in enemies]
    coins_collected = 0
    score = 0
    lives = NUM_LIVES
    return player, coins_remaining, enemies_remaining, coins_collected, score, lives


def check_collisions(player, platforms, blocks, pipes):
    player_rect = player["rect"]
    old_x = player_rect.x
    old_y = player_rect.y

    # 水平碰撞检测
    player_rect.x = old_x + (player["vx"] if "vx" in player else 0) * player["dir"]

    # 地面/平台/块/管道检测
    for rect in platforms + blocks + pipes:
        if player_rect.colliderect(rect):
            if player["vx"] > 0:
                player_rect.right = rect.left
            elif player["vx"] < 0:
                player_rect.left = rect.right

    # 垂直碰撞检测
    player_rect.y = old_y + player["vy"]
    player["is_jumping"] = True
    for rect in platforms + blocks + pipes:
        if player_rect.colliderect(rect):
            if player["vy"] > 0:
                player_rect.bottom = rect.top
                player["is_jumping"] = False
                player["vy"] = 0
            elif player["vy"] < 0:
                player_rect.top = rect.bottom
                player["vy"] = 0

    # 更新x,y
    player["x"] = player_rect.x
    player["y"] = player_rect.y

    return player


def move_enemies(enemies_remaining, platforms, pipes):
    for enemy in enemies_remaining:
        rect = enemy["rect"]
        old_x = rect.x
        new_rect = rect.copy()
        new_rect.x += enemy["speed"] * enemy["dir"]

        # 碰撞检测（仅水平）
        collided = False
        for rect2 in platforms + pipes:
            if new_rect.colliderect(rect2):
                collided = True
                if enemy["dir"] > 0:
                    rect.right = rect2.left
                else:
                    rect.left = rect2.right
                break
        if not collided:
            rect.x += enemy["dir"] * enemy["speed"]

        # 巡逻边界（简单：到障碍后转向）
        # 为简单起见，添加边界检测（仅简单实现）
        if rect.left <= 200 or rect.right >= 3200:
            enemy["dir"] *= -1
        elif rect.left <= 0:
            rect.left = 0
            enemy["dir"] *= -1


def main():
    # 初始化显示
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Super Mario Bros 1-1 Style")
    clock = pygame.time.Clock()

    # 初始化游戏状态
    player, coins_remaining, enemies_remaining, coins_collected, score, lives = reset_game()

    # 游戏变量
    camera_x = 0
    game_state = "PLAYING"  # PLAYING, WIN, GAMEOVER
    font = pygame.font.SysFont("Arial", 24)
    large_font = pygame.font.SysFont("Arial", 48)
    seed = 42
    random = __import__("random")
    random.seed(seed)

    # 持续按键状态
    keys = pygame.key.get_pressed()

    # 主循环
    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_state != "PLAYING":
                    player, coins_remaining, enemies_remaining, coins_collected, score, lives = reset_game()
                    camera_x = 0
                    game_state = "PLAYING"
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE and game_state == "PLAYING" and not player["is_jumping"]:
                    player["vy"] = PLAYER_JUMP_FORCE
                    player["is_jumping"] = True
                elif event.key == pygame.K_SPACE and game_state != "PLAYING":
                    if game_state == "WIN" or game_state == "GAMEOVER":
                        player, coins_remaining, enemies_remaining, coins_collected, score, lives = reset_game()
                        camera_x = 0
                        game_state = "PLAYING"
                elif event.key == pygame.K_r:
                    player, coins_remaining, enemies_remaining, coins_collected, score, lives = reset_game()
                    camera_x = 0
                    game_state = "PLAYING"

        # 玩家输入（持续）
        keys = pygame.key.get_pressed()
        if game_state == "PLAYING":
            if keys[pygame.K_LEFT]:
                player["vx"] = -PLAYER_SPEED_X
                player["dir"] = -1
            elif keys[pygame.K_RIGHT]:
                player["vx"] = PLAYER_SPEED_X
                player["dir"] = 1
            else:
                if "vx" in player:
                    player["vx"] = 0

            # 应用重力
            player["vy"] += GRAVITY

            # 移动并碰撞
            player = check_collisions(player, platforms, blocks, pipes)

            # 更新敌人
            move_enemies(enemies_remaining, platforms, pipes)

            # 玩家与金币碰撞
            player_rect = player["rect"]
            for coin in coins_remaining[:]:
                if player_rect.colliderect(coin):
                    coins_remaining.remove(coin)
                    coins_collected += 1
                    score += SCORE_COIN

            # 玩家与敌人碰撞
            for enemy in enemies_remaining[:]:
                if player_rect.colliderect(enemy["rect"]):
                    # 从上方踩到敌人
                    if player["vy"] > 0 and player["rect"].bottom - enemy["rect"].top < 15:
                        enemies_remaining.remove(enemy)
                        score += SCORE_ENEMY_STOMP
                        player["vy"] = PLAYER_JUMP_FORCE * 0.6  # 弹跳效果
                        player["is_jumping"] = True
                    else:
                        # 被敌人撞到
                        lives -= 1
                        if lives <= 0:
                            game_state = "GAMEOVER"
                        else:
                            # 回到最近安全点（出生点）
                            player, coins_remaining, enemies_remaining, coins_collected, score, lives = reset_game()
                            camera_x = 0

            # 生命消耗：跌落
            if player["y"] >= LEVEL_HEIGHT:
                lives -= 1
                if lives <= 0:
                    game_state = "GAMEOVER"
                else:
                    player, coins_remaining, enemies_remaining, coins_collected, score, lives = reset_game()
                    camera_x = 0

            # 旗杆碰撞
            if player["rect"].colliderect(flag_pole) or player["rect"].colliderect(flag_top) or player["rect"].colliderect(flag_cloth):
                game_state = "WIN"

            # 更新摄像机
            camera_x = player["x"] - SCREEN_WIDTH // 2
            camera_x = max(0, min(camera_x, LEVEL_WIDTH - SCREEN_WIDTH))

        # ——渲染部分——
        screen.fill((135, 206, 235))  # Sky Blue

        # 绘制关卡元素（按摄像机偏移）
        offset_x = -camera_x
        for rect in platforms:
            pygame.draw.rect(screen, COLOR_GROUND, rect.move(offset_x, 0))
        for rect in blocks:
            if rect in [pygame.Rect(300, 200, 40, 40), pygame.Rect(600, 400, 40, 40), pygame.Rect(1140, 400, 40, 40)]:
                color = COLOR_QUESTION_BLOCK
            else:
                color = COLOR_BRICK
            pygame.draw.rect(screen, color, rect.move(offset_x, 0))
            # 边框
            pygame.draw.rect(screen, (0, 0, 0), rect.move(offset_x, 0), 2)
        for rect in pipes:
            pygame.draw.rect(screen, COLOR_PIPE, rect.move(offset_x, 0))
            pygame.draw.rect(screen, (0, 0, 0), rect.move(offset_x, 0), 2)
        for coin in coins_remaining:
            pygame.draw.ellipse(screen, COLOR_COIN, coin.move(offset_x, 0))
        for enemy in enemies_remaining:
            pygame.draw.rect(screen, COLOR_ENEMY, enemy["rect"].move(offset_x, 0))
            # 敌人眼睛
            eye1 = pygame.Rect(enemy["rect"].x + 6 + offset_x, enemy["rect"].y + 8, 6, 6)
            eye2 = pygame.Rect(enemy["rect"].x + 18 + offset_x, enemy["rect"].y + 8, 6, 6)
            pygame.draw.rect(screen, (255, 255, 255), eye1)
            pygame.draw.rect(screen, (255, 255, 255), eye2)
        pygame.draw.rect(screen, COLOR_FLAG_POLE, flag_pole.move(offset_x, 0))
        pygame.draw.ellipse(screen, COLOR_FLAG_TOP, flag_top.move(offset_x, 0))
        pygame.draw.rect(screen, COLOR_FLAG_CLOTH, flag_cloth.move(offset_x, 0))

        # 玩家
        pygame.draw.rect(screen, COLOR_PLAYER, player["rect"].move(offset_x, 0))
        # 玩家帽子
        pygame.draw.rect(screen, COLOR_PLAYER, pygame.Rect(player["rect"].x + 4 + offset_x, player["rect"].y + 2, 24, 4))
        # 玩家裤腿
        pygame.draw.rect(screen, (30, 144, 255), pygame.Rect(player["rect"].x + 4 + offset_x, player["rect"].y + 32, 8, 16))
        pygame.draw.rect(screen, (30, 144, 255), pygame.Rect(player["rect"].x + 20 + offset_x, player["rect"].y + 32, 8, 16))

        # HUD
        hud_text = font.render(f"SCORE: {score}", True, (255, 255, 255))
        screen.blit(hud_text, (10, 10))
        hud_text = font.render(f"WORLD: 1-1", True, (255, 255, 255))
        screen.blit(hud_text, (300, 10))
        hud_text = font.render(f"LIVES: {lives}", True, (255, 255, 255))
        screen.blit(hud_text, (550, 10))
        hud_text = font.render(f"COINS: {coins_collected}", True, (255, 255, 255))
        screen.blit(hud_text, (680, 10))

        # 游戏结束/胜利屏幕
        if game_state != "PLAYING":
            if game_state == "WIN":
                screen.fill((0, 0, 0))
                text = large_font.render("YOU WIN!", True, (0, 255, 0))
                screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 200))
                text = font.render(f"Final Score: {score}", True, (255, 255, 255))
                screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 260))
            else:
                screen.fill((100, 0, 0))
                text = large_font.render("GAME OVER", True, (255, 0, 0))
                screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 200))
                text = font.render(f"Final Score: {score}", True, (255, 255, 255))
                screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 260))
            
            text = font.render("Press R to Restart", True, (255, 255, 255))
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 320))
        
        pygame.display.flip()


if __name__ == "__main__":
    main()