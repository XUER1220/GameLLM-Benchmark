import pygame
import random
import sys

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 32
MAP_COLS = 21
MAP_ROWS = 15
MAP_WIDTH = MAP_COLS * TILE_SIZE
MAP_HEIGHT = MAP_ROWS * TILE_SIZE
MAP_OFFSET_X = (SCREEN_WIDTH - MAP_WIDTH) // 2
MAP_OFFSET_Y = (SCREEN_HEIGHT - MAP_HEIGHT) // 2

# Colors
COLOR_BG = (10, 10, 30)
COLOR_WALL = (90, 90, 120)
COLOR_FLOOR = (40, 30, 50)
COLOR_PLAYER = (220, 220, 80)
COLOR_ENEMY = (220, 80, 80)
COLOR_POTION = (80, 220, 120)
COLOR_WEAPON = (80, 150, 220)
COLOR_EXIT = (180, 80, 220)
COLOR_TEXT = (240, 240, 240)
COLOR_HUD_BG = (20, 20, 40, 200)

# Gameplay constants
PLAYER_HP_INIT = 20
PLAYER_ATK_INIT = 5
PLAYER_LV_INIT = 1
PLAYER_EXP_INIT = 0
ENEMY_HP_INIT = 8
ENEMY_ATK_INIT = 3
ENEMY_COUNT = 4
POTION_COUNT = 2
WEAPON_COUNT = 1
POTION_HEAL = 8
WEAPON_BONUS = 2
EXP_PER_KILL = 5
EXP_TO_LEVEL = 10
LEVEL_HP_BONUS = 5
LEVEL_ATK_BONUS = 1

# Seed for reproducibility
random.seed(42)

class Entity:
    def __init__(self, x, y, hp=1, atk=1):
        self.x = x
        self.y = y
        self.max_hp = hp
        self.hp = hp
        self.atk = atk

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_HP_INIT, PLAYER_ATK_INIT)
        self.lv = PLAYER_LV_INIT
        self.exp = PLAYER_EXP_INIT
        self.floor = 1

    def move(self, dx, dy, walls):
        new_x, new_y = self.x + dx, self.y + dy
        if not walls[new_y][new_x]:
            self.x, self.y = new_x, new_y
            return True
        return False

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def gain_exp(self, amount):
        self.exp += amount
        while self.exp >= EXP_TO_LEVEL:
            self.exp -= EXP_TO_LEVEL
            self.lv += 1
            self.max_hp += LEVEL_HP_BONUS
            self.hp = self.max_hp
            self.atk += LEVEL_ATK_BONUS

class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, ENEMY_HP_INIT, ENEMY_ATK_INIT)

class Dungeon:
    def __init__(self):
        self.walls = []
        self.rooms = []
        self.player_start = (0, 0)
        self.exit_pos = (0, 0)
        self.enemy_positions = []
        self.potion_positions = []
        self.weapon_positions = []

    def generate(self, floor):
        self.walls = [[True for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
        self.rooms = []
        self.enemy_positions = []
        self.potion_positions = []
        self.weapon_positions = []

        def carve_room(x, y, w, h):
            for j in range(y, y + h):
                for i in range(x, x + w):
                    if 0 <= i < MAP_COLS and 0 <= j < MAP_ROWS:
                        self.walls[j][i] = False

        def create_room():
            w = random.randint(4, 7)
            h = random.randint(3, 5)
            x = random.randint(1, MAP_COLS - w - 1)
            y = random.randint(1, MAP_ROWS - h - 1)
            carve_room(x, y, w, h)
            self.rooms.append((x, y, w, h))
            return (x + w // 2, y + h // 2)

        # Generate rooms
        room_centers = []
        for _ in range(6):
            center = create_room()
            room_centers.append(center)

        # Connect rooms with corridors
        for i in range(len(room_centers) - 1):
            cx1, cy1 = room_centers[i]
            cx2, cy2 = room_centers[i + 1]
            # Horizontal first
            for x in range(min(cx1, cx2), max(cx1, cx2) + 1):
                if 0 <= x < MAP_COLS and 0 <= cy1 < MAP_ROWS:
                    self.walls[cy1][x] = False
            # Then vertical
            for y in range(min(cy1, cy2), max(cy1, cy2) + 1):
                if 0 <= cx2 < MAP_COLS and 0 <= y < MAP_ROWS:
                    self.walls[y][cx2] = False

        # Ensure all reachable
        def flood_fill(sx, sy):
            stack = [(sx, sy)]
            visited = [[False] * MAP_COLS for _ in range(MAP_ROWS)]
            visited[sy][sx] = True
            count = 0
            while stack:
                x, y = stack.pop()
                count += 1
                for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < MAP_COLS and 0 <= ny < MAP_ROWS:
                        if not self.walls[ny][nx] and not visited[ny][nx]:
                            visited[ny][nx] = True
                            stack.append((nx, ny))
            return count

        # Ensure at least 80% floor tiles reachable from start
        start_room = room_centers[0]
        while True:
            reachable = flood_fill(start_room[0], start_room[1])
            total_floor = sum(1 for row in self.walls for cell in row if not cell)
            if reachable >= total_floor * 0.8:
                break
            # Carve extra paths
            for _ in range(3):
                x = random.randint(1, MAP_COLS - 2)
                y = random.randint(1, MAP_ROWS - 2)
                self.walls[y][x] = False

        # Set player start and exit
        self.player_start = room_centers[0]
        self.exit_pos = room_centers[-1]

        # Place enemies
        floor_tiles = [(x, y) for y in range(MAP_ROWS) for x in range(MAP_COLS)
                       if not self.walls[y][x] and (x, y) != self.player_start and (x, y) != self.exit_pos]
        random.shuffle(floor_tiles)
        for i in range(min(ENEMY_COUNT + floor, len(floor_tiles))):
            self.enemy_positions.append(floor_tiles[i])

        # Place potions
        for i in range(POTION_COUNT):
            if i < len(floor_tiles):
                self.potion_positions.append(floor_tiles[-i-1])

        # Place weapon
        if floor_tiles:
            self.weapon_positions.append(floor_tiles[len(floor_tiles)//2])

        return self

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Roguelike Dungeon Hard")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 48)
        self.reset()

    def reset(self):
        self.floor = 1
        self.dungeon = Dungeon().generate(self.floor)
        self.player = Player(*self.dungeon.player_start)
        self.player.floor = self.floor
        self.enemies = [Enemy(x, y) for x, y in self.dungeon.enemy_positions]
        self.potions = list(self.dungeon.potion_positions)
        self.weapons = list(self.dungeon.weapon_positions)
        self.exit = self.dungeon.exit_pos
        self.game_over = False
        self.victory = False
        self.turn_processed = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    self.reset()
                    return
                if not self.game_over and not self.victory:
                    dx, dy = 0, 0
                    if event.key == pygame.K_UP:
                        dy = -1
                    elif event.key == pygame.K_DOWN:
                        dy = 1
                    elif event.key == pygame.K_LEFT:
                        dx = -1
                    elif event.key == pygame.K_RIGHT:
                        dx = 1
                    if dx or dy:
                        moved = self.player.move(dx, dy, self.dungeon.walls)
                        if moved:
                            self.turn_processed = True

    def update(self):
        if self.game_over or self.victory:
            return

        # Check pickup
        player_pos = (self.player.x, self.player.y)
        if player_pos in self.potions:
            self.potions.remove(player_pos)
            self.player.heal(POTION_HEAL)
        if player_pos in self.weapons:
            self.weapons.remove(player_pos)
            self.player.atk += WEAPON_BONUS

        # Check exit
        if player_pos == self.exit:
            if self.floor >= 2:
                self.victory = True
            else:
                self.floor += 1
                self.dungeon = Dungeon().generate(self.floor)
                self.player.x, self.player.y = self.dungeon.player_start
                self.player.floor = self.floor
                self.enemies = [Enemy(x, y) for x, y in self.dungeon.enemy_positions]
                self.potions = list(self.dungeon.potion_positions)
                self.weapons = list(self.dungeon.weapon_positions)
                self.exit = self.dungeon.exit_pos

        # Enemy turn
        if self.turn_processed:
            for enemy in self.enemies[:]:
                # Move toward player if far
                dist_x = self.player.x - enemy.x
                dist_y = self.player.y - enemy.y
                if abs(dist_x) + abs(dist_y) > 1:
                    dx = 0
                    dy = 0
                    if abs(dist_x) > abs(dist_y):
                        dx = 1 if dist_x > 0 else -1
                    else:
                        dy = 1 if dist_y > 0 else -1
                    new_x, new_y = enemy.x + dx, enemy.y + dy
                    if not self.dungeon.walls[new_y][new_x]:
                        can_move = True
                        for e in self.enemies:
                            if e is not enemy and e.x == new_x and e.y == new_y:
                                can_move = False
                                break
                        if can_move:
                            enemy.x, enemy.y = new_x, new_y

                # Attack if adjacent
                if abs(enemy.x - self.player.x) + abs(enemy.y - self.player.y) == 1:
                    self.player.take_damage(enemy.atk)
                    if self.player.hp <= 0:
                        self.game_over = True

            self.turn_processed = False

        # Player attacks enemies
        for enemy in self.enemies[:]:
            if abs(enemy.x - self.player.x) + abs(enemy.y - self.player.y) == 1:
                enemy.take_damage(self.player.atk)
                if enemy.hp <= 0:
                    self.enemies.remove(enemy)
                    self.player.gain_exp(EXP_PER_KILL)

    def draw(self):
        self.screen.fill(COLOR_BG)

        # Draw map
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                rect = pygame.Rect(
                    MAP_OFFSET_X + x * TILE_SIZE,
                    MAP_OFFSET_Y + y * TILE_SIZE,
                    TILE_SIZE, TILE_SIZE
                )
                if self.dungeon.walls[y][x]:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_FLOOR, rect)
                    pygame.draw.rect(self.screen, COLOR_BG, rect, 1)

        # Draw exit
        exit_rect = pygame.Rect(
            MAP_OFFSET_X + self.exit[0] * TILE_SIZE,
            MAP_OFFSET_Y + self.exit[1] * TILE_SIZE,
            TILE_SIZE, TILE_SIZE
        )
        pygame.draw.rect(self.screen, COLOR_EXIT, exit_rect)
        pygame.draw.rect(self.screen, (255,255,255), exit_rect, 2)

        # Draw potions
        for x, y in self.potions:
            rect = pygame.Rect(
                MAP_OFFSET_X + x * TILE_SIZE,
                MAP_OFFSET_Y + y * TILE_SIZE,
                TILE_SIZE, TILE_SIZE
            )
            pygame.draw.rect(self.screen, COLOR_POTION, rect)
            pygame.draw.rect(self.screen, (255,255,255), rect, 1)

        # Draw weapons
        for x, y in self.weapons:
            rect = pygame.Rect(
                MAP_OFFSET_X + x * TILE_SIZE,
                MAP_OFFSET_Y + y * TILE_SIZE,
                TILE_SIZE, TILE_SIZE
            )
            pygame.draw.rect(self.screen, COLOR_WEAPON, rect)
            pygame.draw.rect(self.screen, (255,255,255), rect, 1)

        # Draw enemies
        for enemy in self.enemies:
            rect = pygame.Rect(
                MAP_OFFSET_X + enemy.x * TILE_SIZE,
                MAP_OFFSET_Y + enemy.y * TILE_SIZE,
                TILE_SIZE, TILE_SIZE
            )
            pygame.draw.rect(self.screen, COLOR_ENEMY, rect)
            pygame.draw.rect(self.screen, (255,255,255), rect, 1)

        # Draw player
        player_rect = pygame.Rect(
            MAP_OFFSET_X + self.player.x * TILE_SIZE,
            MAP_OFFSET_Y + self.player.y * TILE_SIZE,
            TILE_SIZE, TILE_SIZE
        )
        pygame.draw.rect(self.screen, COLOR_PLAYER, player_rect)
        pygame.draw.rect(self.screen, (255,255,255), player_rect, 2)

        # Draw HUD background
        hud_rect = pygame.Rect(10, 10, SCREEN_WIDTH - 20, 80)
        pygame.draw.rect(self.screen, COLOR_HUD_BG, hud_rect)
        pygame.draw.rect(self.screen, COLOR_TEXT, hud_rect, 2)

        # Draw HUD text
        texts = [
            f"HP: {self.player.hp}/{self.player.max_hp}",
            f"ATK: {self.player.atk}",
            f"LV: {self.player.lv}",
            f"EXP: {self.player.exp}/{EXP_TO_LEVEL}",
            f"Floor: {self.player.floor}",
            f"Enemies: {len(self.enemies)}"
        ]
        for i, text in enumerate(texts):
            label = self.font.render(text, True, COLOR_TEXT)
            self.screen.blit(label, (20, 20 + i * 25))

        # Game over / Victory
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            game_over_text = self.big_font.render("GAME OVER", True, (255, 50, 50))
            restart_text = self.font.render("Press R to Restart", True, COLOR_TEXT)
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        elif self.victory:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            victory_text = self.big_font.render("VICTORY!", True, (50, 255, 100))
            restart_text = self.font.render("Press R to Restart", True, COLOR_TEXT)
            self.screen.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()