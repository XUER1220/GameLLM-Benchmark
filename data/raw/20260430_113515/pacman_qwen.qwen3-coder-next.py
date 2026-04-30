import pygame
import random
import sys

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
TILE_SIZE = 24
ROWS, COLS = 21, 19
MAP_X = (SCREEN_WIDTH - COLS * TILE_SIZE) // 2
MAP_Y = (SCREEN_HEIGHT - ROWS * TILE_SIZE) // 2
FPS = 60

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
BROWN = (160, 82, 45)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)

# Game constants
PACMAN_SPEED = 3
GHOST_SPEED = 2
POWER_MODE_DURATION = 6 * FPS  # 6 seconds at 60 FPS

# Seed
random.seed(42)

# Maze layout: '#'=wall, '.'=dot, 'o'=power pellet, ' '=path, 'P'=pacman start, 'G'=ghost start
MAZE_LAYOUT = [
    "###################",
    "#o........#........o#",
    "#.###.###.#.###.###.#",
    "#.#...#...#...#...#.#",
    "#.###.###.#.###.###.#",
    "#.............P.....#",
    "#.###.#.#####.#.###.#",
    "#...#.#..P...#.#...#",
    "#####.#.#####.#.#####",
    "     #.P.G.P.G.P#    ",
    "#####.#.#####.#.#####",
    "#...#.#..P...#.#...#",
    "#.###.#.#####.#.###.#",
    "#.............P.....#",
    "#.###.###.#.###.###.#",
    "#.#...#...#...#...#.#",
    "#.###.###.#.###.###.#",
    "#o........#........o#",
    "###################"
]

# Determine actual rows from layout
ROWS = len(MAZE_LAYOUT)
COLS = len(MAZE_LAYOUT[0]) if MAZE_LAYOUT else 0

# Calculate positions for Pac-Man and ghosts from the maze layout
def find_positions(maze):
    pacman_start = None
    ghost_starts = []
    for r in range(len(maze)):
        for c in range(len(maze[r])):
            if maze[r][c] == 'P':
                pacman_start = (c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2)
            elif maze[r][c] == 'G':
                ghost_starts.append((c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2))
    return pacman_start, ghost_starts

PACMAN_START, GHOST_STARTS = find_positions(MAZE_LAYOUT)
if not PACMAN_START or not GHOST_STARTS:
    GHOST_STARTS = [(MAP_X + 9 * TILE_SIZE + TILE_SIZE//2, MAP_Y + 10 * TILE_SIZE + TILE_SIZE//2),
                    (MAP_X + 9 * TILE_SIZE + TILE_SIZE//2, MAP_Y + 9 * TILE_SIZE + TILE_SIZE//2),
                    (MAP_X + 9 * TILE_SIZE + TILE_SIZE//2, MAP_Y + 11 * TILE_SIZE + TILE_SIZE//2),
                    (MAP_X + 8 * TILE_SIZE + TILE_SIZE//2, MAP_Y + 10 * TILE_SIZE + TILE_SIZE//2)]
    if not PACMAN_START:
        PACMAN_START = (MAP_X + 9 * TILE_SIZE + TILE_SIZE//2, MAP_Y + 6 * TILE_SIZE + TILE_SIZE//2)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0, 0)

# --- Classes ---

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.reset_game()
    
    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.game_state = "running"  # running, won, lost
        self.power_mode = False
        self.power_timer = 0
        self.dots_remaining = self.count_dots()
        self.maze = [list(row) for row in MAZE_LAYOUT]
        self.pacman = Pacman(PACMAN_START[0], PACMAN_START[1])
        self.ghosts = [Ghost(GHOST_STARTS[i % len(GHOST_STARTS)][0], 
                              GHOST_STARTS[i % len(GHOST_STARTS)][1],
                              (RED if i == 0 else PINK if i == 1 else CYAN if i == 2 else ORANGE))
                       for i in range(4)]
    
    def count_dots(self):
        count = 0
        for row in self.maze:
            count += row.count('.') + row.count('o')
        return count
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r and self.game_state != "running":
                    self.reset_game()
                elif self.game_state == "running":
                    if event.key == pygame.K_UP:
                        self.pacman.set_next_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        self.pacman.set_next_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.pacman.set_next_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.pacman.set_next_direction(RIGHT)
        return True
    
    def update(self):
        if self.game_state != "running":
            return
        
        # Update power mode timer
        if self.power_mode:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.power_mode = False
                for ghost in self.ghosts:
                    ghost.set_normal()
                    ghost.direction = ghost.get_new_direction()
        
        # Move Pac-Man
        self.pacman.update(self.maze)
        
        # Move ghosts
        for ghost in self.ghosts:
            ghost.update(self.maze, self.pacman, self.power_mode)
        
        # Check collisions
        self.check_collisions()
    
    def check_collisions(self):
        px, py = self.pacman.get_center()
        cx, cy = self.pacman.get_grid_pos()
        
        # Check dot consumption
        if 0 <= cy < len(self.maze) and 0 <= cx < len(self.maze[0]):
            cell = self.maze[cy][cx]
            if cell == '.':
                self.maze[cy] = self.maze[cy][:cx] + ' ' + self.maze[cy][cx+1:]
                self.score += 10
                self.dots_remaining -= 1
            elif cell == 'o':
                self.maze[cy] = self.maze[cy][:cx] + ' ' + self.maze[cy][cx+1:]
                self.score += 50
                self.dots_remaining -= 1
                self.power_mode = True
                self.power_timer = POWER_MODE_DURATION
                for ghost in self.ghosts:
                    ghost.set_scared()
        
        # Check Ghost collisions
        for ghost in self.ghosts:
            gx, gy = ghost.get_center()
            dist_sq = (px - gx)**2 + (py - gy)**2
            if dist_sq < TILE_SIZE**2:
                if self.power_mode and ghost.is_scared:
                    self.score += 200
                    ghost.reset_position()
                    ghost.set_normal()
                elif not self.power_mode and not ghost.is_scared:
                    self.handle_death()
    
    def handle_death(self):
        self.lives -= 1
        if self.lives <= 0:
            self.game_state = "lost"
        else:
            self.pacman.reset_position()
            for ghost in self.ghosts:
                ghost.reset_position()
            self.power_mode = False
    
    def get_dot_coords(self):
        coords = []
        for r in range(len(self.maze)):
            for c in range(len(self.maze[r])):
                if self.maze[r][c] == '.':
                    coords.append((MAP_X + c * TILE_SIZE + TILE_SIZE//2, MAP_Y + r * TILE_SIZE + TILE_SIZE//2))
                elif self.maze[r][c] == 'o':
                    coords.append((MAP_X + c * TILE_SIZE + TILE_SIZE//2, MAP_Y + r * TILE_SIZE + TILE_SIZE//2))
        return coords
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw maze
        for r in range(len(self.maze)):
            for c in range(len(self.maze[r])):
                ch = self.maze[r][c]
                x, y = MAP_X + c * TILE_SIZE, MAP_Y + r * TILE_SIZE
                
                if ch == '#':
                    # Wall
                    pygame.draw.rect(self.screen, BLUE, (x, y, TILE_SIZE, TILE_SIZE))
                elif ch == '.':
                    # Dot
                    pygame.draw.circle(self.screen, WHITE, (x + TILE_SIZE//2, y + TILE_SIZE//2), 3)
                elif ch == 'o':
                    # Power Pellet
                    if self.power_timer // 10 % 2 == 0:
                        pygame.draw.circle(self.screen, YELLOW, (x + TILE_SIZE//2, y + TILE_SIZE//2), 6)
        
        # Draw Pac-Man
        self.pacman.draw(self.screen)
        
        # Draw Ghosts
        for ghost in self.ghosts:
            ghost.draw(self.screen)
        
        # Draw HUD
        hud_text = f"Score: {self.score}   Lives: {self.lives}   Dots: {self.dots_remaining}"
        text_surface = self.small_font.render(hud_text, True, WHITE)
        self.screen.blit(text_surface, (MAP_X + COLS * TILE_SIZE + 20, 40))
        
        # Draw game-over or win messages
        if self.game_state == "lost":
            msg = "GAME OVER"
            sub_msg = f"Final Score: {self.score} - Press R to Restart"
            text = self.font.render(msg, True, RED)
            sub_text = self.small_font.render(sub_msg, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 40))
            self.screen.blit(sub_text, (SCREEN_WIDTH//2 - sub_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        elif self.game_state == "won":
            msg = "YOU WIN!"
            sub_msg = f"Final Score: {self.score} - Press R to Restart"
            text = self.font.render(msg, True, GREEN)
            sub_text = self.small_font.render(sub_msg, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 40))
            self.screen.blit(sub_text, (SCREEN_WIDTH//2 - sub_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


class Pacman:
    def __init__(self, x, y):
        self.start_x, self.start_y = x, y
        self.x, self.y = x, y
        self.direction = STOP
        self.next_direction = STOP
        self.radius = TILE_SIZE // 2 - 1
        self.mouth_open = 0
        self.mouth_direction = 0
        self.mouth_speed = 0.25
    
    def reset_position(self):
        self.x, self.y = self.start_x, self.start_y
        self.direction = STOP
        self.next_direction = STOP
    
    def set_next_direction(self, dir):
        self.next_direction = dir
    
    def get_center(self):
        return self.x, self.y
    
    def get_grid_pos(self):
        col = int((self.x - MAP_X) // TILE_SIZE)
        row = int((self.y - MAP_Y) // TILE_SIZE)
        return col, row
    
    def update(self, maze):
        # Try to change direction if possible
        if self.next_direction != STOP:
            if self.can_move(maze, self.next_direction):
                self.direction = self.next_direction
                self.next_direction = STOP
        
        # Move in current direction if possible
        if self.can_move(maze, self.direction):
            self.x += self.direction[0] * PACMAN_SPEED
            self.y += self.direction[1] * PACMAN_SPEED
            
            # Tunnel
            if self.x < 0:
                self.x = SCREEN_WIDTH
            elif self.x > SCREEN_WIDTH:
                self.x = 0
            
            # Mouth animation
            self.mouth_open += self.mouth_speed
            if self.mouth_open > 1.0 or self.mouth_open < 0.0:
                self.mouth_speed = -self.mouth_speed
        else:
            # Stop at wall
            # Snap to center of tile in the other axis
            if self.direction != STOP:
                grid_col = int((self.x - MAP_X + TILE_SIZE//2) // TILE_SIZE)
                grid_row = int((self.y - MAP_Y + TILE_SIZE//2) // TILE_SIZE)
                ideal_x = MAP_X + grid_col * TILE_SIZE + TILE_SIZE//2
                ideal_y = MAP_Y + grid_row * TILE_SIZE + TILE_SIZE//2
                self.x, self.y = ideal_x, ideal_y
                self.direction = STOP
    
    def can_move(self, maze, direction):
        if direction == STOP:
            return True
        
        # Calculate the next position after move
        next_x = self.x + direction[0] * PACMAN_SPEED
        next_y = self.y + direction[1] * PACMAN_SPEED
        
        # Get grid position of the new tile (use center point)
        cols, rows = int((next_x - TILE_SIZE//2) // TILE_SIZE), int((next_y - TILE_SIZE//2) // TILE_SIZE)
        cols2, rows2 = int((next_x + TILE_SIZE//2) // TILE_SIZE), int((next_y + TILE_SIZE//2) // TILE_SIZE)
        
        # Check boundaries
        if rows < 0 or rows >= ROWS or rows2 >= ROWS or cols < 0 or cols >= COLS or cols2 >= COLS:
            return True  # Allow tunnel
        
        # Check walls
        if maze[rows][cols] == '#' or maze[rows][cols2] == '#' or \
           maze[rows2][cols] == '#' or maze[rows2][cols2] == '#':
            return False
        
        return True
    
    def draw(self, surface):
        # Angle based on direction and mouth animation
        angle = 0
        if self.direction == UP:
            angle = -0.5 * pygame.math.pi
        elif self.direction == DOWN:
            angle = 0.5 * pygame.math.pi
        elif self.direction == LEFT:
            angle = 1.0 * pygame.math.pi
        elif self.direction == RIGHT:
            angle = 0.0
        
        # Draw Pac-Man
        mouth_size = 0.2 * self.mouth_open if self.mouth_open < 0.5 else 0.2 * (1 - self.mouth_open)
        mouth_size = max(0.05, min(0.2, mouth_size))
        
        if self.direction == STOP:
            mouth_size = 0.15
        
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.radius)
        if self.direction != STOP:
            pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius, 0)
            # Draw mouth
            start_angle = angle + mouth_size
            end_angle = angle - mouth_size + 2 * pygame.math.pi
            # Correct for mouth rotation
            points = [(int(self.x), int(self.y))]
            for deg in range(int(angle + mouth_size * 20), int(angle - mouth_size * 20 + 360), 5):
                r = self.radius
                if deg > angle + mouth_size * 180 and deg < angle - mouth_size * 180 + 360:
                    r = 0
                rad = deg * pygame.math.pi / 180
                points.append((int(self.x + r * pygame.math.cos(rad)),
                               int(self.y + r * pygame.math.sin(rad))))
            pygame.draw.polygon(surface, BLACK, points)


class Ghost:
    def __init__(self, x, y, color):
        self.start_x, self.start_y = x, y
        self.x, self.y = x, y
        self.color = color
        self.direction = STOP
        self.scared = False
        self.scared_timer = 0
    
    def reset_position(self):
        self.x, self.y = self.start_x, self.start_y
        self.direction = STOP
    
    def set_scared(self):
        self.scared = True
        self.scared_timer = POWER_MODE_DURATION
    
    def set_normal(self):
        self.scared = False
    
    def is_scared(self):
        return self.scared
    
    def get_center(self):
        return self.x, self.y
    
    def update(self, maze, pacman, power_mode_active):
        if self.direction == STOP:
            self.direction = self.get_new_direction(maze, pacman)
        
        # Move in current direction
        if self.can_move(maze, self.direction):
            dx, dy = self.direction
            self.x += dx * GHOST_SPEED
            self.y += dy * GHOST_SPEED
            
            # Tunnel
            if self.x < 0:
                self.x = SCREEN_WIDTH
            elif self.x > SCREEN_WIDTH:
                self.x = 0
        else:
            # Change direction when hitting a wall
            self.direction = self.get_new_direction(maze, pacman)
    
    def can_move(self, maze, direction):
        if direction == STOP:
            return True
        
        next_x = self.x + direction[0] * GHOST_SPEED
        next_y = self.y + direction[1] * GHOST_SPEED
        
        # Check boundaries
        cols, rows = int((next_x - TILE_SIZE//2) // TILE_SIZE), int((next_y - TILE_SIZE//2) // TILE_SIZE)
        cols2, rows2 = int((next_x + TILE_SIZE//2) // TILE_SIZE), int((next_y + TILE_SIZE//2) // TILE_SIZE)
        
        if rows < 0 or rows >= ROWS or rows2 >= ROWS or cols < 0 or cols >= COLS or cols2 >= COLS:
            return True  # Allow tunnel
        
        # Check walls
        if maze[rows][cols] == '#' or maze[rows][cols2] == '#' or \
           maze[rows2][cols] == '#' or maze[rows2][cols2] == '#':
            return False
        
        return True
    
    def get_new_direction(self, maze, pacman):
        x, y = self.x, self.y
        grid_col = int((x - MAP_X) // TILE_SIZE)
        grid_row = int((y - MAP_Y) // TILE_SIZE)
        
        # Available directions
        possible_directions = []
        for dir in [UP, DOWN, LEFT, RIGHT]:
            # Don't reverse direction immediately unless no options
            if self.direction != STOP and dir == (-self.direction[0], -self.direction[1]):
                continue
            if self.can_move(maze, dir):
                possible_directions.append(dir)
        
        # If stuck, allow reversing
        if not possible_directions:
            for dir in [UP, DOWN, LEFT, RIGHT]:
                if self.can_move(maze, dir):
                    possible_directions.append(dir)
        
        if not possible_directions:
            return STOP
        
        # Decide which direction to take
        best_dir = possible_directions[0]
        
        # If scared, minimize distance to Pacman
        # Otherwise, try to be near Pacman (but not too close to avoid immediate capture)
        if len(possible_directions) == 1:
            best_dir = possible_directions[0]
        else:
            min_dist = float('inf')
            max_dist = -1
            for d in possible_directions:
                next_x = x + d[0] * TILE_SIZE
                next_y = y + d[1] * TILE_SIZE
                dist_sq = (next_x - pacman.x)**2 + (next_y - pacman.y)**2
                
                if self.scared:
                    if dist_sq > max_dist:
                        max_dist = dist_sq
                        best_dir = d
                else:
                    if dist_sq < min_dist:
                        min_dist = dist_sq
                        best_dir = d
        
        return best_dir
    
    def draw(self, surface):
        color = PURPLE if self.scared else self.color  # Fallback to purple if not defined
        
        color_map = {RED: RED, PINK: PINK, CYAN: CYAN, ORANGE: ORANGE}
        if self.scared:
            color = BLUE if self.scared_timer > 180 else WHITE  # Flash white near end of scared period
        
        # Draw ghost
        pygame.draw.circle(surface, color_map.get(self.color, self.color) if not self.scared else (BLUE if self.scared_timer > 180 else WHITE), (int(self.x), int(self.y)), TILE_SIZE//2 - 1)
        
        # Draw eyes
        if not self.scared:
            eye_offset = TILE_SIZE//4
            pygame.draw.circle(surface, WHITE, (int(self.x - eye_offset), int(self.y - eye_offset)), 3)
            pygame.draw.circle(surface, WHITE, (int(self.x + eye_offset), int(self.y - eye_offset)), 3)
            pygame.draw.circle(surface, BLACK, (int(self.x - eye_offset + (self.direction[0] * 1)), int(self.y - eye_offset + (self.direction[1] * 1))), 1)
            pygame.draw.circle(surface, BLACK, (int(self.x + eye_offset + (self.direction[0] * 1)), int(self.y - eye_offset + (self.direction[1] * 1))), 1)
        
        # Draw bottom of ghost
        bottom_rect = pygame.Rect(int(self.x - TILE_SIZE//2 + 1), int(self.y + TILE_SIZE//2 - TILE_SIZE//4), TILE_SIZE - 2, TILE_SIZE//4)
        if not self.scared:
            pygame.draw.rect(surface, color_map.get(self.color, self.color), bottom_rect)
        else:
            pygame.draw.rect(surface, (255, 0, 0 if self.scared_timer > 180 else 255), bottom_rect)


if __name__ == "__main__":
    # Define purple for scared ghost fallback
    global PURPLE
    PURPLE = (128, 0, 128)
    
    game = Game()
    game.run()