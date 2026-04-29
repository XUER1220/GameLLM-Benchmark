import pygame
import random
import sys

# 初始化 Pygame
pygame.init()

# 固定参数
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_WIDTH, PLAYER_HEIGHT = 60, 32
PLAYER_SPEED = 6
PLAYER_Y = HEIGHT - 40
PLAYER_BULLET_WIDTH, PLAYER_BULLET_HEIGHT = 6, 16
PLAYER_BULLET_SPEED = 8
ALIEN_ROWS, ALIEN_COLS = 4, 8
ALIEN_WIDTH, ALIEN_HEIGHT = 40, 30
ALIEN_MARGIN_X = 100
ALIEN_MARGIN_Y = 50
ALIEN_SPEED_X = 1.2
ALIEN_SPEED_Y = 20
MAX_LIFE = 3
SCORE_PER_KILL = 10

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)

# 设置窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders Medium")
clock = pygame.time.Clock()

# 全局变量重置函数
def reset_game():
    global player, alien_bullets, player_bullets, aliens, score, life, alien_direction, alien_move_timer, alien_fire_timer, game_over, game_result
    player_rect = pygame.Rect(WIDTH // 2 - PLAYER_WIDTH // 2, PLAYER_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
    player = {
        'rect': player_rect,
        'cooldown': 0,
        'max_cooldown': 30  # 约0.5秒（60fps）
    }
    aliens = []
    for row in range(ALIEN_ROWS):
        for col in range(ALIEN_COLS):
            alien_x = ALIEN_MARGIN_X + col * (ALIEN_WIDTH + 10)
            alien_y = ALIEN_MARGIN_Y + row * (ALIEN_HEIGHT + 15)
            aliens.append(pygame.Rect(alien_x, alien_y, ALIEN_WIDTH, ALIEN_HEIGHT))
    player_bullets = []  # (rect, speed)
    alien_bullets = []   # (rect, speed)
    score = 0
    life = MAX_LIFE
    alien_direction = 1  # 1: right, -1: left
    alien_move_timer = 0
    alien_fire_timer = 0
    game_over = False
    game_result = None

# 初始化随机种子
random.seed(42)

reset_game()

# 主循环
running = True
while running:
    dt = clock.tick(FPS)
    
    # 输入处理
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player['rect'].x = max(0, player['rect'].x - PLAYER_SPEED)
    if keys[pygame.K_RIGHT]:
        player['rect'].x = min(WIDTH - PLAYER_WIDTH, player['rect'].x + PLAYER_SPEED)
    if keys[pygame.K_SPACE] and player['cooldown'] <= 0 and not game_over:
        bullet_rect = pygame.Rect(player['rect'].x + PLAYER_WIDTH // 2 - PLAYER_BULLET_WIDTH // 2, player['rect'].y, PLAYER_BULLET_WIDTH, PLAYER_BULLET_HEIGHT)
        player_bullets.append([bullet_rect, PLAYER_BULLET_SPEED])
        player['cooldown'] = player['max_cooldown']
    if player['cooldown'] > 0:
        player['cooldown'] -= 1
    
    # 处理退出、R、ESC
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r and game_over:
                reset_game()
    
    # 游戏未结束时更新逻辑
    if not game_over:
        # 移动玩家子弹
        for i in range(len(player_bullets) - 1, -1, -1):
            player_bullets[i][0].y -= player_bullets[i][1]
            if player_bullets[i][0].y < -PLAYER_BULLET_HEIGHT:
                player_bullets.pop(i)
        
        # 移动敌人（集体移动）
        if not game_over:
            # 计算所有敌人边界
            alien_bounds = [alien.x for alien in aliens] + [alien.x + ALIEN_WIDTH for alien in aliens]
            min_x, max_x = min(alien_bounds), max(alien_bounds)
            
            # 检查边缘
            if max_x >= WIDTH - 10 and alien_direction > 0:
                alien_direction = -1
                for alien in aliens:
                    alien.y += ALIEN_SPEED_Y
            elif min_x <= 10 and alien_direction < 0:
                alien_direction = 1
                for alien in aliens:
                    alien.y += ALIEN_SPEED_Y
            
            # 每帧移动一小步
            for alien in aliens:
                alien.x += ALIEN_SPEED_X * alien_direction
            
            # 敌人尝试射击
            alien_fire_timer += 1
            # 平均每1-2秒随机发射一个子弹，基于帧率（60fps），确保频率低
            if alien_fire_timer >= random.randint(60, 120):
                if aliens:
                    shooter = random.choice(aliens)
                    bullet_rect = pygame.Rect(shooter.x + ALIEN_WIDTH // 2 - PLAYER_BULLET_WIDTH // 2, shooter.y + ALIEN_HEIGHT, PLAYER_BULLET_WIDTH, PLAYER_BULLET_HEIGHT)
                    alien_bullets.append([bullet_rect, PLAYER_BULLET_SPEED * 0.5])
                    alien_fire_timer = 0
        
        # 移动敌人子弹
        for i in range(len(alien_bullets) - 1, -1, -1):
            alien_bullets[i][0].y += alien_bullets[i][1]
            if alien_bullets[i][0].y > HEIGHT:
                alien_bullets.pop(i)
        
        # 碰撞检测：玩家子弹击中敌人
        for player_bullet in player_bullets:
            for alien in aliens[:]:
                if player_bullet[0].colliderect(alien):
                    player_bullets.remove(player_bullet)
                    aliens.remove(alien)
                    score += SCORE_PER_KILL
                    break
        
        # 碰撞检测：敌人子弹击中玩家
        for alien_bullet in alien_bullets:
            if alien_bullet[0].colliderect(player['rect']):
                alien_bullets.remove(alien_bullet)
                life -= 1
                if life <= 0:
                    game_over = True
                    game_result = 'GAME OVER'
        
        # 检查其他失败条件：敌人到达玩家高度或全灭胜利
        for alien in aliens:
            if alien.y + ALIEN_HEIGHT >= player['rect'].y:
                game_over = True
                game_result = 'GAME OVER'
                break
        if len(aliens) == 0:
            game_over = True
            game_result = 'YOU WIN!'
    
    # 渲染部分
    screen.fill(BLACK)
    
    # 绘制玩家
    pygame.draw.rect(screen, GREEN, player['rect'])
    
    # 绘制敌人
    for alien in aliens:
        pygame.draw.rect(screen, RED, alien)
        # 简单的眼睛
        pygame.draw.circle(screen, WHITE, (alien.x + 12, alien.y + 12), 4)
        pygame.draw.circle(screen, WHITE, (alien.x + 28, alien.y + 12), 4)
    
    # 绘制子弹
    for bullet in player_bullets:
        pygame.draw.rect(screen, BLUE, bullet[0])
    for bullet in alien_bullets:
        pygame.draw.rect(screen, GOLD, bullet[0])
    
    # HUD
    font = pygame.font.SysFont(None, 36)
    score_surf = font.render(f"Score: {score}", True, WHITE)
    life_surf = font.render(f"Life: {life}", True, WHITE)
    screen.blit(score_surf, (20, 20))
    screen.blit(life_surf, (WIDTH - life_surf.get_width() - 20, 20))
    
    # 胜利或失败界面
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        result_msg = 'YOU WIN!' if game_result == 'YOU WIN!' else 'GAME OVER'
        result_color = GREEN if game_result == 'YOU WIN!' else RED
        end_font = pygame.font.SysFont(None, 72)
        result_surf = end_font.render(result_msg, True, result_color)
        screen.blit(result_surf, (WIDTH // 2 - result_surf.get_width() // 2, HEIGHT // 2 - 50))
        restart_font = pygame.font.SysFont(None, 36)
        restart_surf = restart_font.render("Press R to Restart", True, WHITE)
        screen.blit(restart_surf, (WIDTH // 2 - restart_surf.get_width() // 2, HEIGHT // 2 + 50))
    
    pygame.display.flip()

pygame.quit()
sys.exit()