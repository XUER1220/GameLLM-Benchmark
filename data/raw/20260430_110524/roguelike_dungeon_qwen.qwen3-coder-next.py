import pygame
import random

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
MAP_COLS, MAP_ROWS = 21, 15
TILE_SIZE = 32
MAP_WIDTH = MAP_COLS * TILE_SIZE
MAP_HEIGHT = MAP_ROWS * TILE_SIZE
FPS = 60
SEED = 42

# Colors
COLOR_WALL = (64, 64, 64)
COLOR_FLOOR = (200, 200, 200)
COLOR_PLAYER = (0, 0, 255)
COLOR_ENEMY = (255, 0, 0)
COLOR_POTION = (0, 255, 0)
COLOR_WEAPON = (255, 165, 0)
COLOR_EXIT = (255, 255, 0)
COLOR_HUD_BG = (0, 0, 0)
COLOR_HUD_TEXT = (255, 255, 255)
COLOR_MSG = (255, 255, 255)

# Game parameters
PLAYER_BASE_HP = 20
PLAYER_BASE_ATK = 5
PLAYER_BASE_LV = 1
PLAYER_BASE_EXP = 0
ENEMY_NUM = 4
ENEMY_HP = 8
ENEMY_ATK = 3
POTION_COUNT = 2
WEAPON_COUNT = 1
POTION_HEAL = 8
WEAPON_ATK_BONUS = 2
ENEMY_EXP_GIVEN = 5
EXP_TO_LEVEL = 10

# HUD padding
HUD_PADDING = 20
HUD_TOP = 0
HUD_BOTTOM = SCREEN_HEIGHT - HUD_PADDING

# Room and corridor generation parameters
MAX_ROOMS = 6
MIN_ROOM_SIZE = 3
MAX_ROOM_SIZE = 7

class Room:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return center_x, center_y

    def intersect(self, other):
        return (
            self.x1 <= other.x2 and
            self.x2 >= other.x1 and
            self.y1 <= other.y2 and
            self.y2 >= other.y1
        )

class Entity:
    def __init__(self, x, y, name, hp, atk):
        self.x = x
        self.y = y
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.atk = atk

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Roguelike Dungeon Hard")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.large_font = pygame.font.SysFont(None, 36)
        self.running = True
        self.game_over = False
        self.level = 1
        self.seed = SEED
        random.seed(self.seed)
        self.reset_game()

    def reset_game(self):
        random.seed(self.seed)
        self.level = 1
        self.player = Entity(
            10, 7,
            "Player",
            PLAYER_BASE_HP,
            PLAYER_BASE_ATK
        )
        self.player.exp = PLAYER_BASE_EXP
        self.player.level = PLAYER_BASE_LV
        self.player.max_level_hp = PLAYER_BASE_HP
        self.enemies = []
        self.items = []
        self.exit_pos = None
        self.generate_level()
        self.game_over = False

    def generate_level(self):
        # Reset map
        self.dungeon = [[1 for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
        self.rooms = []
        self.enemies = []
        self.items = []
        self.exit_pos = None

        # Generate rooms
        num_rooms = 0
        for _ in range(100):
            w = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
            h = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
            x = random.randint(1, MAP_COLS - w - 1)
            y = random.randint(1, MAP_ROWS - h - 1)

            new_room = Room(x, y, w, h)
            failed = False
            for other in self.rooms:
                if new_room.intersect(other):
                    failed = True
                    break

            if not failed:
                self.create_room(new_room)
                if num_rooms == 0:
                    self.player.x, self.player.y = new_room.center()
                else:
                    prev_room = self.rooms[-1]
                    self.create_tunnel(prev_room, new_room)

                    # Place exit in the last room
                    if num_rooms == MAX_ROOMS - 1:
                        self.exit_pos = new_room.center()

                self.rooms.append(new_room)
                num_rooms += 1
                if num_rooms == MAX_ROOMS:
                    break

        # Place enemies
        empty_tiles = []
        for i in range(MAP_ROWS):
            for j in range(MAP_COLS):
                if self.dungeon[i][j] == 0:
                    empty_tiles.append((j, i))

        random.shuffle(empty_tiles)
        placed_enemies = 0
        placed_potions = 0
        placed_weapons = 0

        # Place enemies
        while placed_enemies < ENEMY_NUM and len(empty_tiles) > 0:
            x, y = empty_tiles.pop()
            if (x, y) != (self.player.x, self.player.y):
                self.enemies.append(Entity(x, y, "Enemy", ENEMY_HP, ENEMY_ATK))
                placed_enemies += 1

        # Place potions
        while placed_potions < POTION_COUNT and len(empty_tiles) > 0:
            x, y = empty_tiles.pop()
            self.items.append({"x": x, "y": y, "type": "potion"})
            placed_potions += 1

        # Place weapon
        while placed_weapons < WEAPON_COUNT and len(empty_tiles) > 0:
            x, y = empty_tiles.pop()
            self.items.append({"x": x, "y": y, "type": "weapon"})
            placed_weapons += 1

        # Place exit if not placed
        if self.exit_pos is None:
            # Try to find last room's center
            if len(self.rooms) > 0:
                self.exit_pos = self.rooms[-1].center()
            else:
                # Fallback - placed randomly in floor
                while len(empty_tiles) > 0:
                    x, y = empty_tiles.pop()
                    if self.dungeon[y][x] == 0:
                        self.exit_pos = (x, y)
                        break

    def create_room(self, room):
        for y in range(room.y1, room.y2):
            for x in range(room.x1, room.x2):
                self.dungeon[y][x] = 0

    def create_tunnel(self, room1, room2):
        x1, y1 = room1.center()
        x2, y2 = room2.center()
        # Horizontal then vertical
        if random.randint(0, 1) == 1:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.dungeon[y1][x] = 0
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.dungeon[y][x2] = 0
        else:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.dungeon[y][x1] = 0
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.dungeon[y2][x] = 0

    def player_move(self, dx, dy):
        if self.game_over:
            return

        new_x = self.player.x + dx
        new_y = self.player.y + dy

        # Check bounds and walls
        if new_y < 0 or new_y >= MAP_ROWS or new_x < 0 or new_x >= MAP_COLS:
            return
        if self.dungeon[new_y][new_x] == 1:
            return

        # Check enemy blocking
        enemy = None
        for e in self.enemies:
            if e.x == new_x and e.y == new_y:
                enemy = e
                break

        if enemy:
            self.player_attack(enemy)
        else:
            # Move player
            self.player.x = new_x
            self.player.y = new_y
            # Check item pickup
            self.check_item_pickup()

            # Check exit
            if self.exit_pos and self.player.x == self.exit_pos[0] and self.player.y == self.exit_pos[1]:
                self.next_level()

        # Enemy turns
        self.enemy_turn()

    def player_attack(self, enemy):
        damage = self.player.atk
        enemy.hp -= damage
        if enemy.hp <= 0:
            self.enemies.remove(enemy)
            self.player.exp += ENEMY_EXP_GIVEN
            self.check_level_up()

    def enemy_turn(self):
        for enemy in self.enemies:
            dx = self.player.x - enemy.x
            dy = self.player.y - enemy.y
            if abs(dx) + abs(dy) <= 1:
                # Adjacent - attack
                self.player.hp -= enemy.atk
                if self.player.hp <= 0:
                    self.player.hp = 0
                    self.game_over = True
            elif abs(dx) + abs(dy) <= 6:
                # Move toward player (simple pathfinding)
                move_x = 0
                move_y = 0
                if abs(dx) > abs(dy):
                    if dx > 0:
                        move_x = 1
                    else:
                        move_x = -1
                else:
                    if dy > 0:
                        move_y = 1
                    else:
                        move_y = -1

                new_x = enemy.x + move_x
                new_y = enemy.y + move_y
                if (
                    0 <= new_x < MAP_COLS and
                    0 <= new_y < MAP_ROWS and
                    self.dungeon[new_y][new_x] == 0 and
                    not any(e.x == new_x and e.y == new_y for e in self.enemies) and
                    (new_x, new_y) != (self.player.x, self.player.y)
                ):
                    enemy.x = new_x
                    enemy.y = new_y

    def check_item_pickup(self):
        for item in self.items[:]:
            if item["x"] == self.player.x and item["y"] == self.player.y:
                if item["type"] == "potion":
                    heal = min(POTION_HEAL, self.player.max_level_hp - self.player.hp)
                    self.player.hp += heal
                elif item["type"] == "weapon":
                    self.player.atk += WEAPON_ATK_BONUS
                self.items.remove(item)
                break

    def check_level_up(self):
        if self.player.exp >= EXP_TO_LEVEL:
            self.player.level += 1
            self.player.exp -= EXP_TO_LEVEL
            self.player.max_level_hp += 5
            self.player.hp = self.player.max_level_hp
            self.player.atk += 1

    def next_level(self):
        self.level += 1
        self.generate_level()

    def draw(self):
        self.screen.fill(COLOR_WALL)
        # Center the map
        map_x = (SCREEN_WIDTH - MAP_WIDTH) // 2
        map_y = (SCREEN_HEIGHT - MAP_HEIGHT) // 2

        # Draw map
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                if self.dungeon[y][x] == 0:
                    color =(COLOR_FLOOR,)
                else:
                    color = COLOR_WALL
                rect = pygame.Rect(map_x + x * TILE_SIZE, map_y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

        # Draw items
        for item in self.items:
            rect = pygame.Rect(map_x + item["x"] * TILE_SIZE + 4, map_y + item["y"] * TILE_SIZE + 4, TILE_SIZE - 8, TILE_SIZE - 8)
            if item["type"] == "potion":
                pygame.draw.rect(self.screen, COLOR_POTION, rect)
            elif item["type"] == "weapon":
                pygame.draw.rect(self.screen, COLOR_WEAPON, rect)

        # Draw exit
        if self.exit_pos:
            rect = pygame.Rect(map_x + self.exit_pos[0] * TILE_SIZE + 2, map_y + self.exit_pos[1] * TILE_SIZE + 2, TILE_SIZE - 4, TILE_SIZE - 4)
            pygame.draw.rect(self.screen, COLOR_EXIT, rect)

        # Draw enemies
        for enemy in self.enemies:
            rect = pygame.Rect(map_x + enemy.x * TILE_SIZE, map_y + enemy.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.screen, COLOR_ENEMY, rect)

        # Draw player
        rect = pygame.Rect(map_x + self.player.x * TILE_SIZE, map_y + self.player.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(self.screen, COLOR_PLAYER, rect)

        # Draw HUD
        hud_rect = pygame.Rect(0, 0, SCREEN_WIDTH, HUD_TOP + 100)
        hud_rect = hud_rect.inflate(0, HUD_PADDING)
        hud_rect.bottom = SCREEN_HEIGHT
        pygame.draw.rect(self.screen, COLOR_HUD_BG, hud_rect)

        # Player stats text
        stats_text = [
            f"HP: {self.player.hp}/{self.player.max_level_hp}",
            f"ATK: {self.player.atk}",
            f"LV: {self.player.level}",
            f"EXP: {self.player.exp}/{EXP_TO_LEVEL}",
            f"Floor: {self.level}"
        ]

        y_offset = hud_rect.top + 10
        for stat in stats_text:
            text = self.font.render(stat, True, COLOR_HUD_TEXT)
            self.screen.blit(text, (10, y_offset))
            y_offset += 25

        # Game status or message
        if self.game_over:
            text = self.large_font.render("GAME OVER! Press R to Restart", True, COLOR_MSG)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, hud_rect.top + 70))
            self.screen.blit(text, rect)

        if self.level > 5:
            text = self.large_font.render("YOU WIN!", True, COLOR_MSG)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, hud_rect.top + 70))
            self.screen.blit(text, rect)
            self.game_over = True

        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_UP:
                        self.player_move(0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.player_move(0, 1)
                    elif event.key == pygame.K_LEFT:
                        self.player_move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.player_move(1, 0)

            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()