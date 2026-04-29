import pygame
import random
import sys

# 初始化
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders Medium")
clock = pygame.time.Clock()
FPS = 60
random.seed(42)

# 颜色定义
BACKGROUND_COLOR = (10, 10, 40)
PLAYER_COLOR = (50, 200, 50)
ENEMY_COLOR = (220, 80, 80)
PLAYER_BULLET_COLOR = (100, 255, 255)
ENEMY_BULLET_COLOR = (255, 255, 100)
HUD_COLOR = (255, 255, 255)
GAME_OVER_COLOR = (255, 100, 100)
GAME_WIN_COLOR = (100, 255, 100)

# 游戏常量
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 32
PLAYER_SPEED = 6
PLAYER_START_X = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
PLAYER_START_Y = SCREEN_HEIGHT - PLAYER_HEIGHT - 40
PLAYER_BULLET_WIDTH = 6
PLAYER_BULLET_HEIGHT = 16
PLAYER_BULLET_SPEED = 8
PLAYER_LIVES = 3

ENEMY_ROWS = 4
ENEMY_COLS = 8
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 30
ENEMY_SPACING_X = 70
ENEMY_SPACING_Y = 50
ENEMY_START_OFFSET_Y = 80
ENEMY_SPEED_X = 1.2
ENEMY_DROP_DISTANCE = 20

ENEMY_BULLET_WIDTH = 6
ENEMY_BULLET_HEIGHT = 16
ENEMY_BULLET_SPEED = 4
ENEMY_SHOOT_CHANCE = 0.002  # 每帧每个敌人射击概率

SCORE_PER_ENEMY = 10

# 游戏状态变量
player_x = PLAYER_START_X
player_lives = PLAYER_LIVES
score = 0
game_over = False
game_won = False
player_bullets = []
enemy_bullets = []
enemies = []

def reset_game():
    global player_x, player_lives, score, game_over, game_won, player_bullets, enemy_bullets, enemies
    player_x = PLAYER_START_X
    player_lives = PLAYER_LIVES
    score = 0
    game_over = False
    game_won = False
    player_bullets = []
    enemy_bullets = []
    enemies = []
    # 初始化敌人
    for row in range(ENEMY_ROWS):
        for col in range(ENEMY_COLS):
            x = col * ENEMY_SPACING_X + (SCREEN_WIDTH - (ENEMY_COLS-1)*ENEMY_SPACING_X) // 2
            y = row * ENEMY_SPACING_Y + ENEMY_START_OFFSET_Y
            enemies.append(pygame.Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT))
    # 初始化敌人移动方向
    global enemy_direction
    enemy_direction = 1

reset_game()
enemy_direction = 1

# 字体
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 64)

def draw_player():
    points = [
        (player_x + PLAYER_WIDTH // 2, PLAYER_START_Y),
        (player_x, PLAYER_START_Y + PLAYER_HEIGHT),
        (player_x + PLAYER_WIDTH, PLAYER_START_Y + PLAYER_HEIGHT)
    ]
    pygame.draw.polygon(screen, PLAYER_COLOR, points)

def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(screen, ENEMY_COLOR, enemy)

def draw_bullets():
    for bullet in player_bullets:
        pygame.draw.rect(screen, PLAYER_BULLET_COLOR, bullet)
    for bullet in enemy_bullets:
        pygame.draw.rect(screen, ENEMY_BULLET_COLOR, bullet)

def draw_hud():
    score_text = font.render(f"Score: {score}", True, HUD_COLOR)
    lives_text = font.render(f"Lives: {player_lives}", True, HUD_COLOR)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 10, 10))

def draw_game_over():
    if game_over:
        text = big_font.render("GAME OVER", True, GAME_OVER_COLOR)
    else:
        text = big_font.render("YOU WIN!", True, GAME_WIN_COLOR)
    screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
    restart_text = font.render("Press R to Restart", True, HUD_COLOR)
    screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 20))

def update_enemies():
    global enemy_direction, game_over
    if not enemies:
        return
    # 检查是否需要改变方向
    move_down = False
    leftmost = min(e.left for e in enemies)
    rightmost = max(e.right for e in enemies)
    if (enemy_direction == 1 and rightmost >= SCREEN_WIDTH) or (enemy_direction == -1 and leftmost <= 0):
        enemy_direction *= -1
        move_down = True
    # 移动敌人
    for enemy in enemies:
        enemy.x += enemy_direction * ENEMY_SPEED_X
        if move_down:
            enemy.y += ENEMY_DROP_DISTANCE
        # 检查是否到达玩家高度
        if enemy.bottom >= PLAYER_START_Y:
            game_over = True

def update_bullets():
    global score
    # 玩家子弹
    for bullet in player_bullets[:]:
        bullet.y -= PLAYER_BULLET_SPEED
        if bullet.bottom < 0:
            player_bullets.remove(bullet)
            continue
        # 检测与敌人的碰撞
        for enemy in enemies[:]:
            if bullet.colliderect(enemy):
                if bullet in player_bullets:
                    player_bullets.remove(bullet)
                if enemy in enemies:
                    enemies.remove(enemy)
                    score += SCORE_PER_ENEMY
                break
    # 敌人子弹
    for bullet in enemy_bullets[:]:
        bullet.y += ENEMY_BULLET_SPEED
        if bullet.top > SCREEN_HEIGHT:
            enemy_bullets.remove(bullet)

def check_collisions():
    global player_lives, game_over
    # 敌人子弹与玩家碰撞
    player_rect = pygame.Rect(player_x, PLAYER_START_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
    for bullet in enemy_bullets[:]:
        if bullet.colliderect(player_rect):
            enemy_bullets.remove(bullet)
            player_lives -= 1
            if player_lives <= 0:
                game_over = True

def enemy_shoot():
    if not enemies:
        return
    for enemy in enemies:
        if random.random() < ENEMY_SHOOT_CHANCE:
            bullet_x = enemy.centerx - ENEMY_BULLET_WIDTH // 2
            bullet_y = enemy.bottom
            enemy_bullets.append(pygame.Rect(bullet_x, bullet_y, ENEMY_BULLET_WIDTH, ENEMY_BULLET_HEIGHT))

def main():
    global player_x, player_lives, score, game_over, game_won, enemies
    running = True
    while running:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    reset_game()
                if not game_over and not game_won and event.key == pygame.K_SPACE:
                    if len(player_bullets) < 3:  # 限制同时存在的子弹数量
                        bullet_x = player_x + PLAYER_WIDTH // 2 - PLAYER_BULLET_WIDTH // 2
                        bullet_y = PLAYER_START_Y - PLAYER_BULLET_HEIGHT
                        player_bullets.append(pygame.Rect(bullet_x, bullet_y, PLAYER_BULLET_WIDTH, PLAYER_BULLET_HEIGHT))
        
        if not game_over and not game_won:
            # 玩家移动
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player_x > 0:
                player_x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] and player_x + PLAYER_WIDTH < SCREEN_WIDTH:
                player_x += PLAYER_SPEED
            
            # 更新游戏逻辑
            update_enemies()
            update_bullets()
            check_collisions()
            enemy_shoot()
            
            # 检查胜利条件
            if len(enemies) == 0:
                game_won = True
        
        # 绘制
        screen.fill(BACKGROUND_COLOR)
        draw_player()
        draw_enemies()
        draw_bullets()
        draw_hud()
        
        if game_over or game_won:
            draw_game_over()
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()