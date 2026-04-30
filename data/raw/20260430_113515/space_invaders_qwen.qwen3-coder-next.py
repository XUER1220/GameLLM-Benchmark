import pygame
import random
import sys

# 固定参数
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 32
PLAYER_Y = SCREEN_HEIGHT - 40
PLAYER_SPEED = 6
PLAYER_BULLET_WIDTH = 6
PLAYER_BULLET_HEIGHT = 16
PLAYER_BULLET_SPEED = 8
ALIEN_ROWS = 4
ALIEN_COLS = 8
ALIEN_WIDTH = 40
ALIEN_HEIGHT = 30
ALIEN_X_GAP = 15
ALIEN_Y_GAP = 15
ALIEN_INITIAL_X = 50
ALIEN_INITIAL_Y = 50
ALIEN_SPEED = 1.2
ALIEN_DROP_DISTANCE = 20
PLAYER_MAX_LIVES = 3
POINTS_PER_ALIEN = 10
ALIEN_SHOOT_PROBABILITY = 0.01  # 每帧触发概率

# 颜色定义
COLOR_BG = (0, 0, 0)
COLOR_PLAYER = (0, 255, 0)
COLOR_ALIEN = (255, 255, 0)
COLOR_PLAYER_BULLET = (255, 0, 0)
COLOR_ALIEN_BULLET = (255, 100, 100)
COLOR_TEXT = (255, 255, 255)
COLOR_HEALTH_BAR = (0, 255, 0)
COLOR_HEALTH_EMPTY = (255, 0, 0)

random.seed(42)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Invaders")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    def create_aliens():
        aliens = []
        for row in range(ALIEN_ROWS):
            for col in range(ALIEN_COLS):
                x = ALIEN_INITIAL_X + col * (ALIEN_WIDTH + ALIEN_X_GAP)
                y = ALIEN_INITIAL_Y + row * (ALIEN_HEIGHT + ALIEN_Y_GAP)
                aliens.append({'rect': pygame.Rect(x, y, ALIEN_WIDTH, ALIEN_HEIGHT), 'alive': True})
        return aliens

    def reset_game():
        player_rect = pygame.Rect((SCREEN_WIDTH - PLAYER_WIDTH) // 2, PLAYER_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
        player_bullets = []
        alien_bullets = []
        aliens = create_aliens()
        score = 0
        lives = PLAYER_MAX_LIVES
        alien_direction = 1
        alien_last_shot = 0
        return {
            'player_rect': player_rect,
            'player_bullets': player_bullets,
            'alien_bullets': alien_bullets,
            'aliens': aliens,
            'score': score,
            'lives': lives,
            'alien_direction': alien_direction,
            'alien_last_shot': alien_last_shot,
            'game_state': 'playing'  # 'playing', 'won', 'lost'
        }

    state = reset_game()
    game_over_message = ""
    won = False

    while True:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (state['game_state'] == 'won' or state['game_state'] == 'lost'):
                    state = reset_game()
                    game_over_message = ""
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        if state['game_state'] == 'playing':
            keys = pygame.key.get_pressed()
            
            # 玩家移动
            if keys[pygame.K_LEFT] and state['player_rect'].x > 0:
                state['player_rect'].x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] and state['player_rect'].x < SCREEN_WIDTH - PLAYER_WIDTH:
                state['player_rect'].x += PLAYER_SPEED
            
            # 玩家发射子弹（冷却控制用帧间隔简单模拟）
            if keys[pygame.K_SPACE]:
                if (len([b for b in state['player_bullets'] if b.y >= state['player_rect'].y - PLAYER_BULLET_HEIGHT]) == 0 or
                    all(b.y < state['player_rect'].y - PLAYER_BULLET_HEIGHT for b in state['player_bullets'])):
                    state['player_bullets'].append(
                        pygame.Rect(state['player_rect'].x + PLAYER_WIDTH//2 - PLAYER_BULLET_WIDTH//2, 
                                    state['player_rect'].y, 
                                    PLAYER_BULLET_WIDTH, PLAYER_BULLET_HEIGHT)
                    )

            # 敌人移动
            alien_alive_count = len([a for a in state['aliens'] if a['alive']])
            if alien_alive_count > 0:
                max_x = max(a['rect'].x + a['rect'].width for a in state['aliens'] if a['alive'])
                min_x = min(a['rect'].x for a in state['aliens'] if a['alive'])
                
                # 检查左右边界
                if state['alien_direction'] == 1 and max_x >= SCREEN_WIDTH - 10:
                    state['alien_direction'] = -1
                    for a in state['aliens']:
                        if a['alive']:
                            a['rect'].y += ALIEN_DROP_DISTANCE
                elif state['alien_direction'] == -1 and min_x <= 10:
                    state['alien_direction'] = 1
                    for a in state['aliens']:
                        if a['alive']:
                            a['rect'].y += ALIEN_DROP_DISTANCE
                
                # 移动所有存活敌人
                for a in state['aliens']:
                    if a['alive']:
                        a['rect'].x += state['alien_direction'] * ALIEN_SPEED

                # 检查敌人是否到达玩家高度
                death_row = STATE_HEIGHT = PLAYER_Y + PLAYER_HEIGHT - 20
                for a in state['aliens']:
                    if a['alive'] and a['rect'].y + a['rect'].height >= PLAYER_Y:
                        state['game_state'] = 'lost'
                        game_over_message = "Game Over!"
                        won = False
                        break

                # 敌人射击（基于概率但确保有限频率）
                if random.random() < ALIEN_SHOOT_PROBABILITY and state['alien_last_shot'] + 20 < state['alien_last_shot'] + 1:
                    # 仅从存活的敌人中随机选择一个（且优先从最下方）
                    living_aliens = [a for a in state['aliens'] if a['alive']]
                    if living_aliens:
                        shooter = random.choice(living_aliens)
                        bullet_x = shooter['rect'].x + shooter['rect'].width // 2 - PLAYER_BULLET_WIDTH // 2
                        bullet_y = shooter['rect'].y + shooter['rect'].height
                        state['alien_bullets'].append(pygame.Rect(bullet_x, bullet_y, PLAYER_BULLET_WIDTH, PLAYER_BULLET_HEIGHT))
                state['alien_last_shot'] += 1

            # 更新玩家子弹
            for b in state['player_bullets'][:]:
                b.y -= PLAYER_BULLET_SPEED
                if b.y < -PLAYER_BULLET_HEIGHT:
                    state['player_bullets'].remove(b)

            # 更新敌人子弹
            for b in state['alien_bullets'][:]:
                b.y += PLAYER_BULLET_SPEED
                if b.y > SCREEN_HEIGHT:
                    state['alien_bullets'].remove(b)
                # 检查是否击中玩家
                if b.colliderect(state['player_rect']):
                    state['lives'] -= 1
                    state['alien_bullets'].remove(b)
                    if state['lives'] <= 0:
                        state['game_state'] = 'lost'
                        game_over_message = "Game Over!"
                        won = False

            # 玩家子弹击中敌人检测
            for b in state['player_bullets'][:]:
                for a in state['aliens']:
                    if a['alive'] and b.colliderect(a['rect']):
                        a['alive'] = False
                        state['player_bullets'].remove(b)
                        state['score'] += POINTS_PER_ALIEN
                        break

            # 检查胜利条件
            if alien_alive_count == 0 and all(not a['alive'] for a in state['aliens']):
                state['game_state'] = 'won'
                game_over_message = "You Win!"
                won = True

        # 绘制
        screen.fill(COLOR_BG)

        # 绘制玩家
        pygame.draw.rect(screen, COLOR_PLAYER, state['player_rect'])

        # 绘制敌人
        for a in state['aliens']:
            if a['alive']:
                pygame.draw.rect(screen, COLOR_ALIEN, a['rect'])

        # 绘制子弹
        for b in state['player_bullets']:
            pygame.draw.rect(screen, COLOR_PLAYER_BULLET, b)
        for b in state['alien_bullets']:
            pygame.draw.rect(screen, COLOR_ALIEN_BULLET, b)

        # 绘制HUD
        score_text = font.render(f"Score: {state['score']}", True, COLOR_TEXT)
        lives_text = font.render(f"Lives: {state['lives']}", True, COLOR_TEXT)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))

        # 剩余敌人数量（调试用，可选）
        # remaining_text = font.render(f"Remaining: {len([a for a in state['aliens'] if a['alive']])}", True, COLOR_TEXT)
        # screen.blit(remaining_text, (10, 90))

        # 游戏结束画面
        if state['game_state'] != 'playing':
            result_text = font.render(game_over_message, True, COLOR_TEXT)
            restart_text = font.render("Press R to Restart", True, COLOR_TEXT)
            result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            screen.blit(result_text, result_rect)
            screen.blit(restart_text, restart_rect)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()