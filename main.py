import pygame
import chess
import chess.engine
import sys

# Configuration
BOARD_SIZE = 512
SIDE_PANEL = 120
BOARD_X = SIDE_PANEL
WIDTH = BOARD_SIZE + SIDE_PANEL * 2
HEIGHT = 512
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
    colors = ["tan", "white"]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            pygame.draw.rect(
                screen,
                color,
                pygame.Rect(BOARD_X + col * SQ_SIZE, row * SQ_SIZE + BANNER_HEIGHT, SQ_SIZE, SQ_SIZE)
            )

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
                screen.blit(
                    IMAGES[piece_name],
                    pygame.Rect(BOARD_X + col * SQ_SIZE, row * SQ_SIZE + BANNER_HEIGHT, SQ_SIZE, SQ_SIZE)
                )
                            
    # Draw over everything
    if dragged_image and dragged_rect:
        screen.blit(dragged_image, dragged_rect)

# Turns mouse x y into square number
def get_square_from_mouse(pos):
    x, y = pos
    x -= BOARD_X
    y -= BANNER_HEIGHT
    if x < 0 or x >= BOARD_SIZE or y < 0 or y >= BOARD_SIZE:
        return None
    col = x // SQ_SIZE
    row = 7 - (y // SQ_SIZE)
    return chess.square(col, row)

# Show possible moves
def draw_possible_moves(screen, board, selected_square):
    for move in board.legal_moves:
        if move.from_square == selected_square:
            col = chess.square_file(move.to_square)
            row = 7 - chess.square_rank(move.to_square)
            pygame.draw.rect(
                screen,
                "lightblue",
                (BOARD_X + col * SQ_SIZE, row * SQ_SIZE + BANNER_HEIGHT, SQ_SIZE, SQ_SIZE)
            )

BANNER_HEIGHT = 60
def info_banner(screen, font, board):
    pygame.draw.rect(screen, "gray20", (0, 0, WIDTH, BANNER_HEIGHT))
    turn_text = "Player" if board.turn == chess.WHITE else "AI"
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            text = "Checkmate! You Lose"
        else:
            text = "Checkmate! You Win"
    elif board.is_stalemate():
        text = "Stalemate! You Tied"
    else:
        text = f"Turn: {turn_text}"
    text_surface = font.render(text, True, "white")
    text_rect = text_surface.get_rect(center=(WIDTH // 2, BANNER_HEIGHT // 2))
    screen.blit(text_surface, text_rect)

# Detects which pieces have been captured
def get_captured_pieces(board):
    starting_white = ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'R', 'R', 'N', 'N', 'B', 'B', 'Q']
    starting_black = ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'r', 'r', 'n', 'n', 'b', 'b', 'q']
    current_white = []
    current_black = []

    for i in range(64):
        piece = board.piece_at(i)
        if piece:
            if piece.color == chess.WHITE and piece.symbol().upper() != 'K':
                current_white.append(piece.symbol().upper())
            elif piece.color == chess.BLACK and piece.symbol().lower() != 'k':
                current_black.append(piece.symbol().lower())

    captured_white = starting_white.copy()
    for piece in current_white:
        if piece in captured_white:
            captured_white.remove(piece)

    captured_black = starting_black.copy()
    for piece in current_black:
        if piece in captured_black:
            captured_black.remove(piece)

    return captured_white, captured_black

# Draws the captured pieces
def draw_captured_pieces(screen, board):
    captured_white, captured_black = get_captured_pieces(board)

    font = pygame.font.SysFont(None, 24)

    small_size = 30
    left_x = 20
    right_x = WIDTH - 20 - small_size

    left_label = font.render("Captured ", True, "white")
    right_label = font.render("Captured", True, "white")
    screen.blit(left_label, (10, BANNER_HEIGHT + 5))
    screen.blit(right_label, (WIDTH - SIDE_PANEL + 10, BANNER_HEIGHT + 5))

    for index, piece in enumerate(captured_black):
        piece_name = 'b' + piece.upper()
        image = pygame.transform.scale(IMAGES[piece_name], (small_size, small_size))
        y = BANNER_HEIGHT + 30 + index * 35
        screen.blit(image, (left_x, y))

    for index, piece in enumerate(captured_white):
        piece_name = 'w' + piece.upper()
        image = pygame.transform.scale(IMAGES[piece_name], (small_size, small_size))
        y = BANNER_HEIGHT + 30 + index * 35
        screen.blit(image, (right_x, y))

def main():
    # Initialize Pygame and set up window
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT+BANNER_HEIGHT))
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
                    if clicked_square is not None and board.piece_at(clicked_square):
                        selected_square = clicked_square
                        dragging = True
            
            # Drop piece
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging:
                    drop_square = get_square_from_mouse(mouse_pos)
                    if drop_square is not None:
                        move = chess.Move(selected_square, drop_square)

                        if move not in board.legal_moves:
                            move = chess.Move(selected_square, drop_square, promotion=chess.QUEEN)
                    
                        if move in board.legal_moves:
                            board.push(move)
                        
                    selected_square = None
                    dragging = False

        # Rendering
        screen.fill("gray30")
        font = pygame.font.SysFont(None, 36)
        info_banner(screen=screen,font=font,board=board)#Rending the turn/info banner
        draw_board(screen)
        draw_possible_moves(screen, board, selected_square)
        
        if dragging:
            draw_pieces(screen, board, selected_square, mouse_pos)
        else:
            draw_pieces(screen, board)

        draw_captured_pieces(screen, board)
        
        pygame.display.flip()
        clock.tick(MAX_FPS)

    engine.quit()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()