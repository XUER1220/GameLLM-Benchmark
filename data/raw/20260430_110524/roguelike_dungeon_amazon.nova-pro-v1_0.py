import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
TILE_SIZE = 32
DUNGEON_WIDTH, DUNGEON_HEIGHT = 21, 15
MAP_WIDTH, MAP_HEIGHT = DUNGEON_WIDTH * TILE_SIZE, DUNGEON_HEIGHT * TILE_SIZE
PLAYER_START_HP, PLAYER_START_ATK, PLAYER_START_LV, PLAYER_START_EXP, PLAYER_START_FLOOR = 20, 5, 1, 0, 1
ENEMY_HP, ENEMY_ATK = 8, 3
POTION_HEAL = 8
WEAPON_ATK_BOOST = 2
EXP_PER_ENEMY = 5
EXP_PER_LEVEL = 10
LEVEL_HP_BOOST = 5
LEVEL_ATK_BOOST = 1

WHITE, BLACK, RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (128, 0, 128), (255, 165, 0)

class Entity:
    def __init__(self, x, y, hp, atk, color):
        self.x, self.y = x, y
        self.hp, self.atk = hp, atk
        self.color = color

class Player(Entity):
    def __init__(self):
        super().__init__(1, 1, PLAYER_START_HP, PLAYER_START_ATK, GREEN)
        self.lv = PLAYER_START_LV
        self.exp = PLAYER_START_EXP
        self.floor = PLAYER_START_FLOOR
        self.max_hp = PLAYER_START_HP

class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, ENEMY_HP, ENEMY_ATK, RED)

class Item:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color

class Potion(Item):
    def __init__(self, x, y):
        super().__init__(x, y, BLUE)

class Weapon(Item):
    def __init__(self, x, y):
        super().__init__(x, y, YELLOW)

class Exit(Item):
    def __init__(self, x, y):
        super().__init__(x, y, PURPLE)

def generate_dungeon():
    dungeon = [[0] * DUNGEON_WIDTH for _ in range(DUNGEON_HEIGHT)]
    rooms = []
    for _ in range(6):
        w = random.randint(4, 6)
        h = random.randint(4, 6)
        x = random.randint(1, DUNGEON_WIDTH - w - 1)
        y = random.randint(1, DUNGEON_HEIGHT - h - 1)
        if not any(check_overlap(x, y, w, h, rx, ry, rw, rh) for rx, ry, rw, rh in rooms):
            rooms.append((x, y, w, h))
            for i in range(w):
                for j in range(h):
                    dungeon[y + j][x + i] = 1
    for (x, y, w, h) in rooms:
        connect_rooms(dungeon, rooms, x, y, w, h)
    return dungeon

def check_overlap(x1, y1, w1, h1, x2, y2, w2, h2):
    return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)

def connect_rooms(dungeon, rooms, x, y, w, h):
    if len(rooms) > 1:
        target = random.choice(rooms)
        while target == (x, y, w, h):
            target = random.choice(rooms)
        tx, ty, tw, th = target
        sx, sy = x + w // 2, y + h // 2
        tx, ty = tx + tw // 2, ty + th // 2
        while sx!= tx or sy!= ty:
            if sx < tx:
                sx += 1
            elif sx > tx:
                sx -= 1
            if sy < ty:
                sy += 1
            elif sy > ty:
                sy -= 1
            dungeon[sy][sx] = 1

def place_entities(dungeon):
    free_spaces = [(x, y) for y in range(DUNGEON_HEIGHT) for x in range(DUNGEON_WIDTH) if dungeon[y][x] == 1]
    random.shuffle(free_spaces)
    player = Player()
    enemies = [Enemy(*free_spaces.pop()) for _ in range(4)]
    potions = [Potion(*free_spaces.pop()) for _ in range(2)]
    weapon = Weapon(*free_spaces.pop())
    exit_ = Exit(*free_spaces.pop())
    return player, enemies, potions, weapon, exit_

def draw_dungeon(screen, dungeon, entities):
    for y in range(DUNGEON_HEIGHT):
        for x in range(DUNGEON_WIDTH):
            color = WHITE if dungeon[y][x] == 1 else BLACK
            pygame.draw.rect(screen, color, (MAP_X + x * TILE_SIZE, MAP_Y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    for entity in entities:
        pygame.draw.rect(screen, entity.color, (MAP_X + entity.x * TILE_SIZE, MAP_Y + entity.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

def draw_hud(screen, player):
    font = pygame.font.Font(None, 36)
    hp_text = font.render(f'HP: {player.hp}/{player.max_hp}', True, WHITE)
    atk_text = font.render(f'ATK: {player.atk}', True, WHITE)
    lv_text = font.render(f'LV: {player.lv}', True, WHITE)
    exp_text = font.render(f'EXP: {player.exp}/{EXP_PER_LEVEL}', True, WHITE)
    floor_text = font.render(f'Floor: {player.floor}', True, WHITE)
    screen.blit(hp_text, (10, 10))
    screen.blit(atk_text, (10, 50))
    screen.blit(lv_text, (10, 90))
    screen.blit(exp_text, (10, 130))
    screen.blit(floor_text, (10, 170))

def game_over(screen, player):
    font = pygame.font.Font(None, 72)
    result_text = font.render('Game Over' if player.hp <= 0 else 'You Win!', True, ORANGE)
    restart_text = font.render('Press R to Restart', True, ORANGE)
    screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, SCREEN_HEIGHT // 2 - result_text.get_height() // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

def main():
    global MAP_X, MAP_Y
    MAP_X, MAP_Y = (SCREEN_WIDTH - MAP_WIDTH) // 2, (SCREEN_HEIGHT - MAP_HEIGHT) // 2
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Roguelike Dungeon Hard')
    clock = pygame.time.Clock()
    running = True
    restart = True

    while running:
        if restart:
            dungeon = generate_dungeon()
            player, enemies, potions, weapon, exit_ = place_entities(dungeon)
            restart = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    restart = True

        keys = pygame.key.get_pressed()
        moved = False
        if keys[pygame.K_UP] and dungeon[player.y - 1][player.x] == 1:
            player.y -= 1
            moved = True
        elif keys[pygame.K_DOWN] and dungeon[player.y + 1][player.x] == 1:
            player.y += 1
            moved = True
        elif keys[pygame.K_LEFT] and dungeon[player.y][player.x - 1] == 1:
            player.x -= 1
            moved = True
        elif keys[pygame.K_RIGHT] and dungeon[player.y][player.x + 1] == 1:
            player.x += 1
            moved = True

        if moved:
            for enemy in enemies:
                if abs(enemy.x - player.x) <= 1 and abs(enemy.y - player.y) <= 1:
                    player.hp -= enemy.atk
                if enemy.x < player.x and dungeon[enemy.y][enemy.x + 1] == 1:
                    enemy.x += 1
                elif enemy.x > player.x and dungeon[enemy.y][enemy.x - 1] == 1:
                    enemy.x -= 1
                elif enemy.y < player.y and dungeon[enemy.y + 1][enemy.x] == 1:
                    enemy.y += 1
                elif enemy.y > player.y and dungeon[enemy.y - 1][enemy.x] == 1:
                    enemy.y -= 1

                if abs(enemy.x - player.x) <= 1 and abs(enemy.y - player.y) <= 1:
                    player.hp -= enemy.atk

            if (player.x, player.y) == (weapon.x, weapon.y):
                player.atk += WEAPON_ATK_BOOST
                weapon = None
            for potion in potions:
                if (player.x, player.y) == (potion.x, potion.y):
                    player.hp = min(player.hp + POTION_HEAL, player.max_hp)
                    potions.remove(potion)
                    break

            if (player.x, player.y) == (exit_.x, exit_.y):
                restart = True
                player.floor += 1

            for enemy in enemies:
                if enemy.hp <= 0:
                    enemies.remove(enemy)
                    player.exp += EXP_PER_ENEMY
                    if player.exp >= EXP_PER_LEVEL:
                        player.lv += 1
                        player.exp -= EXP_PER_LEVEL
                        player.max_hp += LEVEL_HP_BOOST
                        player.hp = player.max_hp
                        player.atk += LEVEL_ATK_BOOST

        screen.fill(BLACK)
        draw_dungeon(screen, dungeon, [player] + enemies + potions + ([weapon] if weapon else []) + [exit_])
        draw_hud(screen, player)
        if player.hp <= 0 or not enemies:
            game_over(screen, player)
            if keys[pygame.K_r]:
                restart = True
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()