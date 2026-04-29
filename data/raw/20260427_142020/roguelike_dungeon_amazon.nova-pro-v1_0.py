import pygame
import random
import sys

pygame.init()
random.seed(42)

WINDOW_SIZE = (800, 600)
FPS = 60
TILE_SIZE = 32
MAP_WIDTH = 21
MAP_HEIGHT = 15
MAP_SIZE = (MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE)
PLAYER_SPEED = 1
PLAYER_HP = 20
PLAYER_ATK = 5
PLAYER_EXP = 0
PLAYER_LV = 1
PLAYER_FLOOR = 1
ENEMY_HP = 8
ENEMY_ATK = 3
POTION_HEAL = 8
WEAPON_ATK_BONUS = 2
EXP_PER_ENEMY = 5
EXP_TO_LEVEL_UP = 10
LEVEL_UP_HP_BONUS = 5
LEVEL_UP_ATK_BONUS = 1

WALL_COLOR = (128, 128, 128)
FLOOR_COLOR = (64, 64, 64)
PLAYER_COLOR = (0, 255, 0)
ENEMY_COLOR = (255, 0, 0)
POTION_COLOR = (0, 0, 255)
WEAPON_COLOR = (255, 255, 0)
EXIT_COLOR = (255, 255, 255)
HUD_COLOR = (0, 0, 0)
BG_COLOR = (32, 32, 32)

screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Roguelike Dungeon Hard")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

class Entity:
    def __init__(self, x, y, hp, atk, color):
        self.x = x
        self.y = y
        self.hp = hp
        self.atk = atk
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

class Player(Entity):
    def __init__(self, x, y, hp, atk, color):
        super().__init__(x, y, hp, atk, color)
        self.lv = PLAYER_LV
        self.exp = PLAYER_EXP
        self.floor = PLAYER_FLOOR

    def move(self, dx, dy, walls):
        if 0 <= self.x + dx < MAP_WIDTH and 0 <= self.y + dy < MAP_HEIGHT and not walls[self.y + dy][self.x + dx]:
            self.x += dx
            self.y += dy
            return True
        return False

    def attack(self, enemy):
        enemy.hp -= self.atk
        if enemy.hp <= 0:
            self.exp += EXP_PER_ENEMY
            if self.exp >= EXP_TO_LEVEL_UP:
                self.level_up()

    def level_up(self):
        self.exp -= EXP_TO_LEVEL_UP
        self.lv += 1
        self.hp += LEVEL_UP_HP_BONUS
        self.atk += LEVEL_UP_ATK_BONUS

    def pick_up(self, item):
        if isinstance(item, Potion):
            self.hp = min(self.hp + POTION_HEAL, self.lv * LEVEL_UP_HP_BONUS + PLAYER_HP)
        elif isinstance(item, Weapon):
            self.atk += WEAPON_ATK_BONUS

class Enemy(Entity):
    pass

class Item:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

class Potion(Item):
    pass

class Weapon(Item):
    pass

class Exit(Item):
    pass

def generate_dungeon():
    walls = [[True for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    rooms = []
    for _ in range(6):
        w = random.randint(4, 6)
        h = random.randint(4, 6)
        x = random.randint(1, MAP_WIDTH - w - 1)
        y = random.randint(1, MAP_HEIGHT - h - 1)
        if all(walls[yy][xx] for yy in range(y, y + h) for xx in range(x, x + w)):
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    walls[yy][xx] = False
            rooms.append((x, y, w, h))

    for i in range(len(rooms) - 1):
        x1, y1, w1, h1 = rooms[i]
        x2, y2, w2, h2 = rooms[i + 1]
        cx1, cy1 = x1 + w1 // 2, y1 + h1 // 2
        cx2, cy2 = x2 + w2 // 2, y2 + h2 // 2
        for x in range(min(cx1, cx2), max(cx1, cx2) + 1):
            walls[min(cy1, cy2)][x] = False
        for y in range(min(cy1, cy2), max(cy1, cy2) + 1):
            walls[y][min(cx1, cx2)] = False

    player_x, player_y = rooms[0][0] + 1, rooms[0][1] + 1
    exit_x, exit_y = rooms[-1][0] + rooms[-1][2] - 2, rooms[-1][1] + rooms[-1][3] - 2
    walls[exit_y][exit_x] = False

    potions = []
    weapons = []
    for _ in range(2):
        x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
        while walls[y][x] or (x, y) in [(p.x, p.y) for p in potions]:
            x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
        potions.append(Potion(x, y, POTION_COLOR))
        walls[y][x] = False

    for _ in range(1):
        x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
        while walls[y][x] or (x, y) in [(w.x, w.y) for w in weapons] or (x, y) in [(p.x, p.y) for p in potions]:
            x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
        weapons.append(Weapon(x, y, WEAPON_COLOR))
        walls[y][x] = False

    enemies = []
    for _ in range(4):
        x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
        while walls[y][x] or (x, y) in [(e.x, e.y) for e in enemies] or (x, y) in [(p.x, p.y) for p in potions] or (x, y) in [(w.x, w.y) for w in weapons]:
            x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
        enemies.append(Enemy(x, y, ENEMY_HP, ENEMY_ATK, ENEMY_COLOR))
        walls[y][x] = False

    exit = Exit(exit_x, exit_y, EXIT_COLOR)
    return walls, player_x, player_y, enemies, potions, weapons, exit

def main():
    global running, player, enemies, potions, weapons, exit, walls, player_floor

    running = True
    player_floor = 1
    walls, player_x, player_y, enemies, potions, weapons, exit = generate_dungeon()
    player = Player(player_x, player_y, PLAYER_HP, PLAYER_ATK, PLAYER_COLOR)

    while running:
        screen.fill(BG_COLOR)
        map_surface = pygame.Surface(MAP_SIZE)
        map_surface.fill(FLOOR_COLOR)

        for wall in [(x, y) for y in range(MAP_HEIGHT) for x in range(MAP_WIDTH) if walls[y][x]]:
            pygame.draw.rect(map_surface, WALL_COLOR, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        player.draw(map_surface)
        for enemy in enemies:
            enemy.draw(map_surface)
        for potion in potions:
            potion.draw(map_surface)
        for weapon in weapons:
            weapon.draw(map_surface)
        exit.draw(map_surface)

        screen.blit(map_surface, ((WINDOW_SIZE[0] - MAP_SIZE[0]) // 2, (WINDOW_SIZE[1] - MAP_SIZE[1]) // 2))

        draw_text(f"HP: {player.hp}", font, HUD_COLOR, screen, 10, 10)
        draw_text(f"ATK: {player.atk}", font, HUD_COLOR, screen, 10, 40)
        draw_text(f"LV: {player.lv}", font, HUD_COLOR, screen, 10, 70)
        draw_text(f"EXP: {player.exp}/{EXP_TO_LEVEL_UP}", font, HUD_COLOR, screen, 10, 100)
        draw_text(f"Floor: {player_floor}", font, HUD_COLOR, screen, 10, 130)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    main()
                    return
                elif event.key == pygame.K_UP:
                    if player.move(0, -1, walls):
                        for enemy in enemies:
                            enemy.x, enemy.y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
                            while walls[enemy.y][enemy.x] or (enemy.x, enemy.y) in [(e.x, e.y) for e in enemies if e!= enemy] or (enemy.x, enemy.y) in [(p.x, p.y) for p in potions] or (enemy.x, enemy.y) in [(w.x, w.y) for w in weapons]:
                                enemy.x, enemy.y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
                elif event.key == pygame.K_DOWN:
                    if player.move(0, 1, walls):
                        for enemy in enemies:
                            enemy.x, enemy.y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
                            while walls[enemy.y][enemy.x] or (enemy.x, enemy.y) in [(e.x, e.y) for e in enemies if e!= enemy] or (enemy.x, enemy.y) in [(p.x, p.y) for p in potions] or (enemy.x, enemy.y) in [(w.x, w.y) for w in weapons]:
                                enemy.x, enemy.y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
                elif event.key == pygame.K_LEFT:
                    if player.move(-1, 0, walls):
                        for enemy in enemies:
                            enemy.x, enemy.y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
                            while walls[enemy.y][enemy.x] or (enemy.x, enemy.y) in [(e.x, e.y) for e in enemies if e!= enemy] or (enemy.x, enemy.y) in [(p.x, p.y) for p in potions] or (enemy.x, enemy.y) in [(w.x, w.y) for w in weapons]:
                                enemy.x, enemy.y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
                elif event.key == pygame.K_RIGHT:
                    if player.move(1, 0, walls):
                        for enemy in enemies:
                            enemy.x, enemy.y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
                            while walls[enemy.y][enemy.x] or (enemy.x, enemy.y) in [(e.x, e.y) for e in enemies if e!= enemy] or (enemy.x, enemy.y) in [(p.x, p.y) for p in potions] or (enemy.x, enemy.y) in [(w.x, w.y) for w in weapons]:
                                enemy.x, enemy.y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)

        for enemy in enemies:
            if abs(enemy.x - player.x) <= 1 and abs(enemy.y - player.y) <= 1:
                player.hp -= enemy.atk
                if player.hp <= 0:
                    draw_text("Game Over! Press R to Restart", font, HUD_COLOR, screen, 300, 280)
                    pygame.display.flip()
                    while True:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_r:
                                    main()
                                    return
            else:
                enemy.x, enemy.y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
                while walls[enemy.y][enemy.x] or (enemy.x, enemy.y) in [(e.x, e.y) for e in enemies if e!= enemy] or (enemy.x, enemy.y) in [(p.x, p.y) for p in potions] or (enemy.x, enemy.y) in [(w.x, w.y) for w in weapons]:
                    enemy.x, enemy.y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)

        for potion in potions:
            if potion.x == player.x and potion.y == player.y:
                player.pick_up(potion)
                potions.remove(potion)
                break

        for weapon in weapons:
            if weapon.x == player.x and weapon.y == player.y:
                player.pick_up(weapon)
                weapons.remove(weapon)
                break

        if player.x == exit.x and player.y == exit.y:
            player_floor += 1
            walls, player_x, player_y, enemies, potions, weapons, exit = generate_dungeon()
            player.x, player.y = player_x, player_y

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()