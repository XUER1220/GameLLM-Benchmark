import pygame
import random

# 固定常量
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
PADDLE_WIDTH = 18
PADDLE_HEIGHT = 100
BALL_SIZE = 18
PADDLE_SPEED = 7
BALL_SPEED_X = 5
BALL_SPEED_Y = 5
WINNING_SCORE = 7

# 颜色常量
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pong Easy")
    clock = pygame.time.Clock()
    random.seed(42)
    
    # 字体设置
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 36)
    
    def reset_game():
        paddle_left_y = (WINDOW_HEIGHT - PADDLE_HEIGHT) // 2
        paddle_right_y = (WINDOW_HEIGHT - PADDLE_HEIGHT) // 2
        ball_x = (WINDOW_WIDTH - BALL_SIZE) // 2
        ball_y = (WINDOW_HEIGHT - BALL_SIZE) // 2
        
        # 随机决定发球方向（左或右）
        direction = random.choice([-1, 1])
        return {
            'left_score': 0,
            'right_score': 0,
            'game_over': False,
            'winner': None,
            'paddle_left_y': paddle_left_y,
            'paddle_right_y': paddle_right_y,
            'ball_x': ball_x,
            'ball_y': ball_y,
            'ball_speed_x': BALL_SPEED_X * direction,
            'ball_speed_y': BALL_SPEED_Y * random.choice([-1, 1])
        }
    
    game_state = reset_game()
    
    # 键盘状态追踪
    keys_pressed = set()
    
    running = True
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                keys_pressed.add(event.key)
                if event.key == pygame.K_r:
                    game_state = reset_game()
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.KEYUP:
                keys_pressed.discard(event.key)
        
        # 游戏逻辑更新
        if not game_state['game_over']:
            # 左侧球拍移动
            if pygame.K_w in keys_pressed:
                game_state['paddle_left_y'] = max(0, game_state['paddle_left_y'] - PADDLE_SPEED)
            if pygame.K_s in keys_pressed:
                game_state['paddle_left_y'] = min(WINDOW_HEIGHT - PADDLE_HEIGHT, game_state['paddle_left_y'] + PADDLE_SPEED)
            
            # 右侧球拍移动
            if pygame.K_UP in keys_pressed:
                game_state['paddle_right_y'] = max(0, game_state['paddle_right_y'] - PADDLE_SPEED)
            if pygame.K_DOWN in keys_pressed:
                game_state['paddle_right_y'] = min(WINDOW_HEIGHT - PADDLE_HEIGHT, game_state['paddle_right_y'] + PADDLE_SPEED)
            
            # 小球移动
            game_state['ball_x'] += game_state['ball_speed_x']
            game_state['ball_y'] += game_state['ball_speed_y']
            
            # 上下边界反弹
            if game_state['ball_y'] <= 0 or game_state['ball_y'] + BALL_SIZE >= WINDOW_HEIGHT:
                game_state['ball_speed_y'] = -game_state['ball_speed_y']
            
            # 球拍碰撞检测
            # 左球拍
            if (game_state['ball_x'] <= PADDLE_WIDTH and
                game_state['paddle_left_y'] <= game_state['ball_y'] + BALL_SIZE - 1 and
                game_state['ball_y'] <= game_state['paddle_left_y'] + PADDLE_HEIGHT - 1):
                game_state['ball_speed_x'] = abs(game_state['ball_speed_x'])
                game_state['ball_x'] = PADDLE_WIDTH  # 修正位置避免卡住
                
            # 右球拍
            if (game_state['ball_x'] + BALL_SIZE >= WINDOW_WIDTH - PADDLE_WIDTH and
                game_state['paddle_right_y'] <= game_state['ball_y'] + BALL_SIZE - 1 and
                game_state['ball_y'] <= game_state['paddle_right_y'] + PADDLE_HEIGHT - 1):
                game_state['ball_speed_x'] = -abs(game_state['ball_speed_x'])
                game_state['ball_x'] = WINDOW_WIDTH - PADDLE_WIDTH - BALL_SIZE  # 修正位置
    
            # 得分检测
            if game_state['ball_x'] < 0:
                game_state['right_score'] += 1
                if game_state['right_score'] >= WINNING_SCORE:
                    game_state['game_over'] = True
                    game_state['winner'] = 'Right'
                game_state = reset_game()
                # 重新设置分数以保留当前得分
                game_state['left_score'] = game_state['left_score'] if 'left_score' in game_state else 0
                game_state['right_score'] = game_state['right_score'] if 'right_score' in game_state else 0
                
            elif game_state['ball_x'] > WINDOW_WIDTH:
                game_state['left_score'] += 1
                if game_state['left_score'] >= WINNING_SCORE:
                    game_state['game_over'] = True
                    game_state['winner'] = 'Left'
                game_state = reset_game()
                # 重新设置分数以保留当前得分
                game_state['left_score'] = game_state['left_score'] if 'left_score' in game_state else 0
                game_state['right_score'] = game_state['right_score'] if 'right_score' in game_state else 0
        
        # 绘制
        screen.fill(BLACK)
        
        # 绘制中线
        pygame.draw.rect(screen, GRAY, (WINDOW_WIDTH // 2 - 2, 0, 4, WINDOW_HEIGHT))
        
        # 绘制左侧球拍
        pygame.draw.rect(screen, WHITE, (0, game_state['paddle_left_y'], PADDLE_WIDTH, PADDLE_HEIGHT))
        
        # 绘制右侧球拍
        pygame.draw.rect(screen, WHITE, (WINDOW_WIDTH - PADDLE_WIDTH, game_state['paddle_right_y'], PADDLE_WIDTH, PADDLE_HEIGHT))
        
        # 绘制小球
        pygame.draw.rect(screen, WHITE, (game_state['ball_x'], game_state['ball_y'], BALL_SIZE, BALL_SIZE))
        
        # 绘制分数
        score_text = font.render(f"{game_state['left_score']}   {game_state['right_score']}", True, WHITE)
        screen.blit(score_text, ((WINDOW_WIDTH - score_text.get_width()) // 2, 20))
        
        # 游戏结束显示
        if game_state['game_over']:
            winner_text = font.render(f"{game_state['winner']} Wins!", True, WHITE)
            restart_text = small_font.render("Press R to Restart", True, WHITE)
            
            # 居中显示
            screen.blit(winner_text, ((WINDOW_WIDTH - winner_text.get_width()) // 2, WINDOW_HEIGHT // 2 - 60))
            screen.blit(restart_text, ((WINDOW_WIDTH - restart_text.get_width()) // 2, WINDOW_HEIGHT // 2 + 10))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()