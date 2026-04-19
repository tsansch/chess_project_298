import pygame
import chess
import chess.engine
import sys

# Configuration
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

# Check Stockfish path
if sys.platform == "win32":
    STOCKFISH_PATH = "stockfish.exe"
else:
    STOCKFISH_PATH = "stockfish"

def load_images():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        image = pygame.image.load(f"assets/{piece}.png")
        IMAGES[piece] = pygame.transform.scale(image, (SQ_SIZE, SQ_SIZE))

def draw_board(screen):
    colors = ["black", "white"]
    
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board):
    for i in range(64):
        piece = board.piece_at(i)
        if piece:
            symbol = piece.symbol()
            
            if piece.color == chess.WHITE:
                color_prefix = 'w'
            else:
                color_prefix = 'b'
                
            piece_name = color_prefix + symbol.upper()
            
            # coordinates for pygame
            col = i % 8
            row = 7 - (i // 8) 
            
            screen.blit(IMAGES[piece_name], pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def main():
    # Initialize Pygame and set up window
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Player vs Stockfish")
    clock = pygame.time.Clock()
    
    board = chess.Board()
    load_images()
        
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
        draw_pieces(screen, board)
        
        pygame.display.flip()
        clock.tick(MAX_FPS)

    engine.quit()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()