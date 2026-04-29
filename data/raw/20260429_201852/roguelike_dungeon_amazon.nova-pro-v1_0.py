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
WHITE, BLACK, RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (128, 0, 128), (255, 165, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roguelike Dungeon Hard")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

class Entity:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, GREEN)
        self.hp = 20
        self.max_hp = 20
        self.atk = 5
        self.lv = 1
        self.exp = 0
        self.floor = 1

    def move(self, dx, dy, map):
        if 0 <= self.x + dx < MAP_WIDTH and 0 <= self.y + dy < MAP_HEIGHT and map[self.y + dy][self.x + dx]!= 1:
            self.x += dx
            self.y += dy
            return True
        return False

    def attack(self, target):
        target.hp -= self.atk
        if target.hp <= 0:
            self.exp += 5
            if self.exp >= 10:
                self.lv += 1
                self.exp -= 10
                self.max_hp += 5
                self.hp = self.max_hp
                self.atk += 1

class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, RED)
        self.hp = 8
        self.atk = 3

    def move(self, player, map):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(directions)
        for dx, dy in directions:
            if 0 <= self.x + dx < MAP_WIDTH and 0 <= self.y + dy < MAP_HEIGHT:
                if map[self.y + dy][self.x + dx]!= 1:
                    if self.x + dx == player.x and self.y + dy == player.y:
                        player.hp -= self.atk
                        if player.hp <= 0:
                            pygame.quit()
                            sys.exit()
                    else:
                        self.x += dx
                        self.y += dy
                        break

class Item(Entity):
    def __init__(self, x, y, color, effect):
        super().__init__(x, y, color)
        self.effect = effect

    def use(self, player):
        if self.effect == "heal":
            player.hp = min(player.hp + 8, player.max_hp)
        elif self.effect == "atk":
            player.atk += 2

def generate_map():
    map = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    rooms = []
    for _ in range(6):
        w = random.randint(4, 6)
        h = random.randint(4, 6)
        x = random.randint(1, MAP_WIDTH - w - 1)
        y = random.randint(1, MAP_HEIGHT - h - 1)
        for i in range(x, x + w):
            for j in range(y, y + h):
                map[j][i] = 0
        rooms.append((x, y, w, h))
    
    for i in range(1, len(rooms)):
        start_x, start_y, _, _ = rooms[i-1]
        end_x, end_y, _, _ = rooms[i]
        while start_x!= end_x or start_y!= end_y:
            if start_x < end_x:
                start_x += 1
            elif start_x > end_x:
                start_x -= 1
            elif start_y < end_y:
                start_y += 1
            elif start_y > end_y:
                start_y -= 1
            map[start_y][start_x] = 0
    
    for i in range(MAP_HEIGHT):
        for j in range(MAP_WIDTH):
            if map[i][j] == 0:
                map[i][j] = -1
    
    return map

def place_entities(map, player):
    enemies = []
    items = []
    exit = None
    for i in range(MAP_HEIGHT):
        for j in range(MAP_WIDTH):
            if map[i][j] == -1:
                if random.random() < 0.1:
                    enemies.append(Enemy(j, i))
                elif random.random() < 0.05:
                    if random.random() < 0.5:
                        items.append(Item(j, i, YELLOW, "heal"))
                    else:
                        items.append(Item(j, i, PURPLE, "atk"))
                elif not exit and random.random() < 0.01:
                    exit = Entity(j, i, ORANGE)
                map[i][j] = 0
    return enemies, items, exit

def draw_map(map, player, enemies, items, exit):
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if map[y][x] == 1:
                pygame.draw.rect(screen, BLACK, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            else:
                pygame.draw.rect(screen, WHITE, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    for item in items:
        item.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)
    if exit:
        exit.draw(screen)
    player.draw(screen)

def draw_hud(player):
    hp_text = font.render(f"HP: {player.hp}/{player.max_hp}", True, BLACK)
    atk_text = font.render(f"ATK: {player.atk}", True, BLACK)
    lv_text = font.render(f"LV: {player.lv}", True, BLACK)
    exp_text = font.render(f"EXP: {player.exp}", True, BLACK)
    floor_text = font.render(f"Floor: {player.floor}", True, BLACK)
    screen.blit(hp_text, (10, 10))
    screen.blit(atk_text, (10, 30))
    screen.blit(lv_text, (10, 50))
    screen.blit(exp_text, (10, 70))
    screen.blit(floor_text, (10, 90))

def main():
    player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
    map = generate_map()
    enemies, items, exit = place_entities(map, player)
    
    running = True
    game_over = False
    while running:
        screen.fill(WHITE)
        draw_map(map, player, enemies, items, exit)
        draw_hud(player)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
                    map = generate_map()
                    enemies, items, exit = place_entities(map, player)
                    game_over = False
                elif not game_over:
                    if event.key == pygame.K_UP:
                        player.move(0, -1, map)
                    elif event.key == pygame.K_DOWN:
                        player.move(0, 1, map)
                    elif event.key == pygame.K_LEFT:
                        player.move(-1, 0, map)
                    elif event.key == pygame.K_RIGHT:
                        player.move(1, 0, map)
        
        if not game_over:
            for enemy in enemies:
                enemy.move(player, map)
                if enemy.x == player.x and enemy.y == player.y:
                    player.hp -= enemy.atk
                    if player.hp <= 0:
                        game_over = True
                        over_text = font.render("Game Over! Press R to Restart", True, BLACK)
                        screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2 - over_text.get_height() // 2))
            
            for item in items[:]:
                if item.x == player.x and item.y == player.y:
                    item.use(player)
                    items.remove(item)
            
            if exit and player.x == exit.x and player.y == exit.y:
                player.floor += 1
                map = generate_map()
                enemies, items, exit = place_entities(map, player)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()