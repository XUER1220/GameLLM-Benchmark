import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
MAP_WIDTH, MAP_HEIGHT = 21, 15
TILE_SIZE = 32
FPS = 60
WHITE, BLACK, RED, GREEN, BLUE, YELLOW, PURPLE = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (128, 0, 128)

class Player:
    def __init__(self):
        self.x, self.y = 1, 1
        self.hp, self.max_hp = 20, 20
        self.atk = 5
        self.lv = 1
        self.exp = 0
        self.floor = 1

    def move(self, dx, dy):
        if 0 <= self.x + dx < MAP_WIDTH and 0 <= self.y + dy < MAP_HEIGHT and dungeon[self.y + dy][self.x + dx]!= 'W':
            self.x += dx
            self.y += dy
            return True
        return False

    def level_up(self):
        self.exp -= 10
        self.lv += 1
        self.max_hp += 5
        self.hp = self.max_hp
        self.atk += 1

class Enemy:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.hp = 8
        self.atk = 3

    def move(self, player):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(directions)
        for dx, dy in directions:
            if 0 <= self.x + dx < MAP_WIDTH and 0 <= self.y + dy < MAP_HEIGHT and dungeon[self.y + dy][self.x + dx]!= 'W':
                self.x += dx
                self.y += dy
                break

def generate_dungeon():
    global dungeon
    dungeon = [[' ' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    rooms = []
    for _ in range(6):
        w = random.randint(4, 6)
        h = random.randint(4, 6)
        x = random.randint(1, MAP_WIDTH - w - 1)
        y = random.randint(1, MAP_HEIGHT - h - 1)
        for i in range(w):
            for j in range(h):
                dungeon[y + j][x + i] = ' '
        rooms.append((x, y, w, h))
    for i in range(len(rooms) - 1):
        connect_rooms(rooms[i], rooms[i + 1])
    place_objects()
    place_exit()

def connect_rooms(room1, room2):
    x1, y1, w1, h1 = room1
    x2, y2, w2, h2 = room2
    cx1, cy1 = x1 + w1 // 2, y1 + h1 // 2
    cx2, cy2 = x2 + w2 // 2, y2 + h2 // 2
    for x in range(min(cx1, cx2), max(cx1, cx2) + 1):
        for y in range(min(cy1, cy2), max(cy1, cy2) + 1):
            if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                dungeon[y][x] = ' '

def place_objects():
    for _ in range(2):
        x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
        if dungeon[y][x] =='':
            dungeon[y][x] = 'H'
    x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
    if dungeon[y][x] =='':
        dungeon[y][x] = 'W'

def place_exit():
    x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
    if dungeon[y][x] == ' ':
        dungeon[y][x] = 'E'

def draw_dungeon():
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            color = WHITE if dungeon[y][x] == ''else BLACK
            if dungeon[y][x] == 'H':
                color = GREEN
            elif dungeon[y][x] == 'W':
                color = YELLOW
            elif dungeon[y][x] == 'E':
                color = PURPLE
            pygame.draw.rect(screen, color, (x * TILE_SIZE + (SCREEN_WIDTH - MAP_WIDTH * TILE_SIZE) // 2, y * TILE_SIZE + (SCREEN_HEIGHT - MAP_HEIGHT * TILE_SIZE) // 2, TILE_SIZE, TILE_SIZE))

def draw_player():
    pygame.draw.rect(screen, RED, (player.x * TILE_SIZE + (SCREEN_WIDTH - MAP_WIDTH * TILE_SIZE) // 2, player.y * TILE_SIZE + (SCREEN_HEIGHT - MAP_HEIGHT * TILE_SIZE) // 2, TILE_SIZE, TILE_SIZE))

def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(screen, BLUE, (enemy.x * TILE_SIZE + (SCREEN_WIDTH - MAP_WIDTH * TILE_SIZE) // 2, enemy.y * TILE_SIZE + (SCREEN_HEIGHT - MAP_HEIGHT * TILE_SIZE) // 2, TILE_SIZE, TILE_SIZE))

def draw_hud():
    font = pygame.font.Font(None, 36)
    hp_text = font.render(f"HP: {player.hp}/{player.max_hp}", True, RED)
    atk_text = font.render(f"ATK: {player.atk}", True, RED)
    lv_text = font.render(f"LV: {player.lv}", True, RED)
    exp_text = font.render(f"EXP: {player.exp}", True, RED)
    floor_text = font.render(f"Floor: {player.floor}", True, RED)
    screen.blit(hp_text, (10, 10))
    screen.blit(atk_text, (10, 50))
    screen.blit(lv_text, (10, 90))
    screen.blit(exp_text, (10, 130))
    screen.blit(floor_text, (10, 170))

def game_over():
    font = pygame.font.Font(None, 74)
    text = font.render('Game Over', True, RED)
    screen.blit(text, (250, 250))
    font = pygame.font.Font(None, 36)
    text = font.render('Press R to Restart', True, RED)
    screen.blit(text, (250, 350))

def game_win():
    font = pygame.font.Font(None, 74)
    text = font.render('You Win!', True, RED)
    screen.blit(text, (250, 250))
    font = pygame.font.Font(None, 36)
    text = font.render('Press R to Restart', True, RED)
    screen.blit(text, (250, 350))

def player_attack(enemies):
    for enemy in enemies:
        if abs(player.x - enemy.x) <= 1 and abs(player.y - enemy.y) <= 1:
            enemy.hp -= player.atk
            if enemy.hp <= 0:
                enemies.remove(enemy)
                player.exp += 5
                if player.exp >= 10:
                    player.level_up()

def check_game_over():
    if player.hp <= 0:
        return True
    return False

def check_game_win():
    if dungeon[player.y][player.x] == 'E':
        return True
    return False

def main():
    global running, screen, player, enemies
    running = True
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    player = Player()
    enemies = [Enemy(random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)) for _ in range(4)]
    generate_dungeon()
    game_over_flag = False
    game_win_flag = False

    while running:
        screen.fill(BLACK)
        draw_dungeon()
        draw_player()
        draw_enemies()
        draw_hud()

        if game_over_flag:
            game_over()
        elif game_win_flag:
            game_win()
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        main()
                        return
                    elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                        dx, dy = 0, 0
                        if event.key == pygame.K_UP:
                            dy = -1
                        elif event.key == pygame.K_DOWN:
                            dy = 1
                        elif event.key == pygame.K_LEFT:
                            dx = -1
                        elif event.key == pygame.K_RIGHT:
                            dx = 1
                        if player.move(dx, dy):
                            player_attack(enemies)
                            for enemy in enemies:
                                enemy.move(player)
                            if dungeon[player.y][player.x] == 'H':
                                player.hp = min(player.hp + 8, player.max_hp)
                                dungeon[player.y][player.x] = ' '
                            elif dungeon[player.y][player.x] == 'W':
                                player.atk += 2
                                dungeon[player.y][player.x] =''
                            game_over_flag = check_game_over()
                            if not game_over_flag:
                                game_win_flag = check_game_win()
                                if game_win_flag:
                                    player.floor += 1
                                    generate_dungeon()
                                    enemies = [Enemy(random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)) for _ in range(4)]

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()