import pygame
import random
import sys

pygame.init()
random.seed(42)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
MAP_WIDTH, MAP_HEIGHT = 21, 15
TILE_SIZE = 32
MAP_DISPLAY_WIDTH, MAP_DISPLAY_HEIGHT = MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roguelike Dungeon Hard")
clock = pygame.time.Clock()

class Entity:
    def __init__(self, x, y, color, hp, atk):
        self.x, self.y = x, y
        self.color = color
        self.hp = hp
        self.atk = atk

    def move(self, dx, dy, dungeon):
        nx, ny = self.x + dx, self.y + dy
        if dungeon.is_walkable(nx, ny):
            self.x, self.y = nx, ny

    def attack(self, target):
        target.hp -= self.atk

class Player(Entity):
    def __init__(self):
        super().__init__(1, 1, GREEN, 20, 5)
        self.level = 1
        self.exp = 0
        self.floor = 1

    def gain_exp(self, exp):
        self.exp += exp
        while self.exp >= 10:
            self.exp -= 10
            self.level_up()

    def level_up(self):
        self.level += 1
        self.hp += 5
        self.atk += 1

class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, RED, 8, 3)

class Item:
    def __init__(self, x, y, color, effect):
        self.x, self.y = x, y
        self.color = color
        self.effect = effect

    def use(self, player):
        if self.effect == "heal":
            player.hp = min(player.hp + 8, 20 + 5 * (player.level - 1))
        elif self.effect == "atk":
            player.atk += 2

class Dungeon:
    def __init__(self):
        self.map = [[0] * MAP_WIDTH for _ in range(MAP_HEIGHT)]
        self.generate_dungeon()
        self.player = Player()
        self.enemies = [Enemy(random.randint(1, MAP_WIDTH-2), random.randint(1, MAP_HEIGHT-2)) for _ in range(4)]
        self.items = [
            Item(random.randint(1, MAP_WIDTH-2), random.randint(1, MAP_HEIGHT-2), YELLOW, "heal"),
            Item(random.randint(1, MAP_WIDTH-2), random.randint(1, MAP_HEIGHT-2), YELLOW, "heal"),
            Item(random.randint(1, MAP_WIDTH-2), random.randint(1, MAP_HEIGHT-2), CYAN, "atk")
        ]
        self.exit = (random.randint(1, MAP_WIDTH-2), random.randint(1, MAP_HEIGHT-2))

    def is_walkable(self, x, y):
        return 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT and self.map[y][x] == 0

    def generate_dungeon(self):
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if x == 0 or y == 0 or x == MAP_WIDTH-1 or y == MAP_HEIGHT-1:
                    self.map[y][x] = 1
        rooms = [(random.randint(1, MAP_WIDTH-10), random.randint(1, MAP_HEIGHT-5), random.randint(5, 8), random.randint(3, 5)) for _ in range(6)]
        for (rx, ry, rw, rh) in rooms:
            for y in range(ry, ry+rh):
                for x in range(rx, rx+rw):
                    self.map[y][x] = 0
        for i in range(1, len(rooms)):
            sx, sy = rooms[i-1][0]+rooms[i-1][2]//2, rooms[i-1][1]+rooms[i-1][3]//2
            ex, ey = rooms[i][0]+rooms[i][2]//2, rooms[i][1]+rooms[i][3]//2
            while sx!= ex or sy!= ey:
                if sx < ex: sx += 1
                elif sx > ex: sx -= 1
                if sy < ey: sy += 1
                elif sy > ey: sy -= 1
                self.map[sy][sx] = 0

    def draw(self):
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                color = WHITE if self.map[y][x] == 0 else BLACK
                pygame.draw.rect(screen, color, (x * TILE_SIZE + (SCREEN_WIDTH - MAP_DISPLAY_WIDTH) // 2, y * TILE_SIZE + (SCREEN_HEIGHT - MAP_DISPLAY_HEIGHT) // 2, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, self.player.color, (self.player.x * TILE_SIZE + (SCREEN_WIDTH - MAP_DISPLAY_WIDTH) // 2, self.player.y * TILE_SIZE + (SCREEN_HEIGHT - MAP_DISPLAY_HEIGHT) // 2, TILE_SIZE, TILE_SIZE))
        for enemy in self.enemies:
            pygame.draw.rect(screen, enemy.color, (enemy.x * TILE_SIZE + (SCREEN_WIDTH - MAP_DISPLAY_WIDTH) // 2, enemy.y * TILE_SIZE + (SCREEN_HEIGHT - MAP_DISPLAY_HEIGHT) // 2, TILE_SIZE, TILE_SIZE))
        for item in self.items:
            pygame.draw.rect(screen, item.color, (item.x * TILE_SIZE + (SCREEN_WIDTH - MAP_DISPLAY_WIDTH) // 2, item.y * TILE_SIZE + (SCREEN_HEIGHT - MAP_DISPLAY_HEIGHT) // 2, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, PURPLE, (self.exit[0] * TILE_SIZE + (SCREEN_WIDTH - MAP_DISPLAY_WIDTH) // 2, self.exit[1] * TILE_SIZE + (SCREEN_HEIGHT - MAP_DISPLAY_HEIGHT) // 2, TILE_SIZE, TILE_SIZE))

    def update(self):
        if self.player.hp <= 0:
            return "Game Over"
        if (self.player.x, self.player.y) == self.exit:
            self.floor += 1
            self.__init__()
            return "Next Floor"
        for enemy in self.enemies:
            if abs(enemy.x - self.player.x) <= 1 and abs(enemy.y - self.player.y) <= 1:
                enemy.attack(self.player)
                if self.player.hp <= 0:
                    return "Game Over"
        for item in self.items:
            if item.x == self.player.x and item.y == self.player.y:
                item.use(self.player)
                self.items.remove(item)
        for enemy in self.enemies[:]:
            if enemy.hp <= 0:
                self.player.gain_exp(5)
                self.enemies.remove(enemy)
        return ""

dungeon = Dungeon()

def draw_hud():
    font = pygame.font.Font(None, 36)
    screen.blit(font.render(f"HP: {dungeon.player.hp}", True, WHITE), (10, 10))
    screen.blit(font.render(f"ATK: {dungeon.player.atk}", True, WHITE), (10, 40))
    screen.blit(font.render(f"LV: {dungeon.player.level}", True, WHITE), (10, 70))
    screen.blit(font.render(f"EXP: {dungeon.player.exp}", True, WHITE), (10, 100))
    screen.blit(font.render(f"Floor: {dungeon.player.floor}", True, WHITE), (10, 130))

running = True
game_over = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                dungeon = Dungeon()
                game_over = False
            elif not game_over:
                if event.key == pygame.K_UP:
                    dungeon.player.move(0, -1, dungeon)
                elif event.key == pygame.K_DOWN:
                    dungeon.player.move(0, 1, dungeon)
                elif event.key == pygame.K_LEFT:
                    dungeon.player.move(-1, 0, dungeon)
                elif event.key == pygame.K_RIGHT:
                    dungeon.player.move(1, 0, dungeon)
                result = dungeon.update()
                if result == "Game Over":
                    game_over = True
                elif result == "Next Floor":
                    game_over = False

    screen.fill(BLACK)
    dungeon.draw()
    draw_hud()
    if game_over:
        font = pygame.font.Font(None, 74)
        text_surface = font.render('Game Over', True, WHITE)
        screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, SCREEN_HEIGHT // 2 - text_surface.get_height() // 2))
        font = pygame.font.Font(None, 36)
        text_surface = font.render('Press R to Restart', True, WHITE)
        screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, SCREEN_HEIGHT // 2 + text_surface.get_height() // 2))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()