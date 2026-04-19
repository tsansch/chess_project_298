import pygame
import chess
import chess.engine
import sys

# Configuration
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15

# Check Stockfish path
if sys.platform == "win32":
    STOCKFISH_PATH = "stockfish.exe"
else:
    STOCKFISH_PATH = "stockfish"

def draw_board(screen):
    colors = ["black","white"]
    
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def main():
    # Initialize Pygame and set up window
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Player vs Stockfish")
    clock = pygame.time.Clock()
    
    board = chess.Board()
        
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    running = True
    
    # Main application loop
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Rendering
        draw_board(screen)
        
        pygame.display.flip()
        clock.tick(MAX_FPS)

    engine.quit()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()