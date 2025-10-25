import pygame
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
FPS = 10

# Colors
class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    DARK_GREEN = (0, 200, 0)
    YELLOW = (255, 255, 0)
    GRAY = (128, 128, 128)

# Direction Enum
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

@dataclass
class Position:
    """Represents a position on the game grid"""
    x: int
    y: int
    
    def __add__(self, direction: Direction) -> 'Position':
        dx, dy = direction.value
        return Position(self.x + dx, self.y + dy)
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Food:
    """Represents food on the game board"""
    def __init__(self):
        self.position = self._generate_position()
    
    def _generate_position(self) -> Position:
        return Position(
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1)
        )
    
    def respawn(self):
        self.position = self._generate_position()
    
    def draw(self, surface):
        rect = pygame.Rect(
            self.position.x * GRID_SIZE,
            self.position.y * GRID_SIZE,
            GRID_SIZE,
            GRID_SIZE
        )
        pygame.draw.rect(surface, Color.RED, rect)
        pygame.draw.rect(surface, Color.YELLOW, rect, 2)

class Snake:
    """Represents the snake with OOP design"""
    def __init__(self):
        start_pos = Position(GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.body: List[Position] = [start_pos]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.grow_pending = False
    
    def update(self):
        """Update snake position"""
        self.direction = self.next_direction
        new_head = self.body[0] + self.direction
        
        # Check boundaries (wrap around)
        new_head.x = new_head.x % GRID_WIDTH
        new_head.y = new_head.y % GRID_HEIGHT
        
        self.body.insert(0, new_head)
        
        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False
    
    def grow(self):
        """Mark snake to grow on next update"""
        self.grow_pending = True
    
    def check_collision(self) -> bool:
        """Check if snake collides with itself"""
        head = self.body[0]
        return head in self.body[1:]
    
    def set_direction(self, direction: Direction):
        """Set next direction (prevent 180-degree turns)"""
        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        
        if direction != opposite[self.direction]:
            self.next_direction = direction
    
    def draw(self, surface):
        """Draw snake on surface"""
        for i, segment in enumerate(self.body):
            rect = pygame.Rect(
                segment.x * GRID_SIZE,
                segment.y * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE
            )
            # Head is darker green
            color = Color.DARK_GREEN if i == 0 else Color.GREEN
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, Color.WHITE, rect, 1)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3

class SnakeGame:
    """Main game controller using OOP principles"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game - Classic Arcade")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        self.state = GameState.MENU
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.high_score = 0
        self.running = True
    
    def handle_input(self):
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.start_game()
                
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_UP:
                        self.snake.set_direction(Direction.UP)
                    elif event.key == pygame.K_DOWN:
                        self.snake.set_direction(Direction.DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.snake.set_direction(Direction.LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.set_direction(Direction.RIGHT)
                
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        self.start_game()
                    elif event.key == pygame.K_q:
                        self.running = False
    
    def start_game(self):
        """Initialize a new game"""
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.state = GameState.PLAYING
    
    def update(self):
        """Update game logic"""
        if self.state != GameState.PLAYING:
            return
        
        self.snake.update()
        
        # Check food collision
        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.food.respawn()
            self.score += 10
        
        # Check self collision
        if self.snake.check_collision():
            self.state = GameState.GAME_OVER
            if self.score > self.high_score:
                self.high_score = self.score
    
    def draw(self):
        """Draw game elements"""
        self.screen.fill(Color.BLACK)
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_menu(self):
        """Draw main menu"""
        title = self.font_large.render("SNAKE", True, Color.GREEN)
        subtitle = self.font_medium.render("Classic Arcade Game", True, Color.YELLOW)
        start = self.font_small.render("Press SPACE to Start", True, Color.WHITE)
        
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 150))
        self.screen.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, 250))
        self.screen.blit(start, (WINDOW_WIDTH // 2 - start.get_width() // 2, 400))
    
    def draw_game(self):
        """Draw game board"""
        # Draw grid
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, Color.GRAY, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, Color.GRAY, (0, y), (WINDOW_WIDTH, y), 1)
        
        # Draw game objects
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        
        # Draw score
        score_text = self.font_small.render(f"Score: {self.score}", True, Color.WHITE)
        self.screen.blit(score_text, (10, 10))
        
        high_score_text = self.font_small.render(f"High Score: {self.high_score}", True, Color.YELLOW)
        self.screen.blit(high_score_text, (WINDOW_WIDTH - high_score_text.get_width() - 10, 10))
    
    def draw_game_over(self):
        """Draw game over screen"""
        self.draw_game()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(Color.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over = self.font_large.render("GAME OVER", True, Color.RED)
        final_score = self.font_medium.render(f"Score: {self.score}", True, Color.YELLOW)
        restart = self.font_small.render("Press SPACE to Restart or Q to Quit", True, Color.WHITE)
        
        self.screen.blit(game_over, (WINDOW_WIDTH // 2 - game_over.get_width() // 2, 150))
        self.screen.blit(final_score, (WINDOW_WIDTH // 2 - final_score.get_width() // 2, 280))
        self.screen.blit(restart, (WINDOW_WIDTH // 2 - restart.get_width() // 2, 400))
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        print(f"[v0] Game ended. Final Score: {self.score}, High Score: {self.high_score}")

if __name__ == "__main__":
    game = SnakeGame()
    game.run()