import pygame
import chess
import chess.engine
import sys

# Configuration
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60 
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

def draw_pieces(screen, board, selected_square=None, mouse_pos=None):
    dragged_image = None
    dragged_rect = None

    for i in range(64):
        piece = board.piece_at(i)
        if piece:
            symbol = piece.symbol()
            
            if piece.color == chess.WHITE:
                color_prefix = 'w'
            else:
                color_prefix = 'b'
                
            piece_name = color_prefix + symbol.upper()
            
            # Save dragged piece for later so it draws on top
            if i == selected_square:
                dragged_image = IMAGES[piece_name]
                dragged_rect = dragged_image.get_rect(center=mouse_pos)
            else:
                col = i % 8
                row = 7 - (i // 8) 
                screen.blit(IMAGES[piece_name], pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            
    # Draw over everything
    if dragged_image and dragged_rect:
        screen.blit(dragged_image, dragged_rect)

# Turns mouse x y into square number
def get_square_from_mouse(pos):
    x, y = pos
    col = x // SQ_SIZE
    row = 7 - (y // SQ_SIZE)
    return chess.square(col, row)

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
    selected_square = None
    dragging = False
    
    # Main application loop
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Drag piece
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    clicked_square = get_square_from_mouse(mouse_pos)
                    if board.piece_at(clicked_square):
                        selected_square = clicked_square
                        dragging = True
            
            # Drop piece
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging:
                    drop_square = get_square_from_mouse(mouse_pos)
                    move = chess.Move(selected_square, drop_square)
                    
                    if move not in board.legal_moves:
                        move = chess.Move(selected_square, drop_square, promotion=chess.QUEEN)
                    
                    if move in board.legal_moves:
                        board.push(move)
                        
                    selected_square = None
                    dragging = False

        # Rendering
        draw_board(screen)
        
        if dragging:
            draw_pieces(screen, board, selected_square, mouse_pos)
        else:
            draw_pieces(screen, board)
        
        pygame.display.flip()
        clock.tick(MAX_FPS)

    engine.quit()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()