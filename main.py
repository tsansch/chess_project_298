import pygame
import chess
import chess.engine
import sys
import threading
import queue
import random

# Configuration
BOARD_SIZE = 512
SIDE_PANEL = 120
BOARD_X = SIDE_PANEL
WIDTH = BOARD_SIZE + SIDE_PANEL * 2
HEIGHT = 512
BANNER_HEIGHT = 60
WINDOW_HEIGHT = HEIGHT + BANNER_HEIGHT
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60 
IMAGES = {}
MODE_PVP = "pvp"
MODE_AI = "ai"
STATE_MENU = "menu"
STATE_PLAYING = "playing"

MENU_BUTTON_RECT = pygame.Rect(WIDTH - SIDE_PANEL + 22, 12, 76, 36)

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

def get_screen_pos(square, player_color):
    file = chess.square_file(square)
    rank = chess.square_rank(square)
    
    if player_color == chess.BLACK:
        col = 7 - file
        row_py = rank
    else:
        col = file
        row_py = 7 - rank
        
    return BOARD_X + col * SQ_SIZE, BANNER_HEIGHT + row_py * SQ_SIZE

def draw_pieces(screen, board, player_color, selected_square=None, mouse_pos=None):
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
                x, y = get_screen_pos(i, player_color)
                screen.blit(
                    IMAGES[piece_name],
                    pygame.Rect(x, y, SQ_SIZE, SQ_SIZE)
                )
                            
    # Draw over everything
    if dragged_image and dragged_rect:
        screen.blit(dragged_image, dragged_rect)

# Turns mouse x y into square number based on perspective
def get_square_from_mouse(pos, player_color):
    x, y = pos
    x -= BOARD_X
    y -= BANNER_HEIGHT
    if x < 0 or x >= BOARD_SIZE or y < 0 or y >= BOARD_SIZE:
        return None
    col = x // SQ_SIZE
    row_py = y // SQ_SIZE
    
    if player_color == chess.BLACK:
        file = 7 - col
        rank = row_py
    else:
        file = col
        rank = 7 - row_py
        
    return chess.square(file, rank)

# Show possible moves
def draw_possible_moves(screen, board, selected_square, player_color):
    for move in board.legal_moves:
        if move.from_square == selected_square:
            x, y = get_screen_pos(move.to_square, player_color)
            pygame.draw.rect(
                screen,
                "lightblue",
                (x, y, SQ_SIZE, SQ_SIZE)
            )

def draw_button(screen, rect, text, font, active=False, disabled=False):
    if disabled:
        button_color = "gray35"
        text_color = "gray65"
    elif active:
        button_color = "steelblue"
        text_color = "white"
    else:
        button_color = "gray55"
        text_color = "white"

    pygame.draw.rect(screen, button_color, rect, border_radius=6)
    pygame.draw.rect(screen, "gray15", rect, 2, border_radius=6)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def get_menu_buttons():
    button_width = 230
    button_height = 52
    center_x = WIDTH // 2
    return {
        MODE_PVP: pygame.Rect(center_x - button_width - 12, 170, button_width, button_height),
        MODE_AI: pygame.Rect(center_x + 12, 170, button_width, button_height),
        "Play White": pygame.Rect(center_x - 160, 250, 100, 40),
        "Play Random": pygame.Rect(center_x - 50, 250, 100, 40), 
        "Play Black": pygame.Rect(center_x + 60, 250, 100, 40),
        "Start AI": pygame.Rect(center_x - button_width // 2, 400, button_width, button_height),
    }

def draw_slider(screen, font, rect, value):
    # Draw track
    pygame.draw.rect(screen, "gray50", rect, border_radius=5)
    
    # Calculate knob position
    percent = value / 20.0
    knob_x = rect.x + int(percent * rect.width)
    knob_rect = pygame.Rect(knob_x - 10, rect.y - 15, 20, 40)
    
    # Draw filled portion
    fill_rect = pygame.Rect(rect.x, rect.y, knob_x - rect.x, rect.height)
    if fill_rect.width > 0:
        pygame.draw.rect(screen, "steelblue", fill_rect, border_radius=5)
    
    # Draw knob
    pygame.draw.rect(screen, "white", knob_rect, border_radius=5)
    pygame.draw.rect(screen, "gray20", knob_rect, 2, border_radius=5)
    
    # Draw text
    text = font.render(f"Stockfish Skill Level: {value}", True, "white")
    screen.blit(text, text.get_rect(center=(WIDTH // 2, rect.y - 30)))

def draw_menu(screen, title_font, font, small_font, selected_mode, error_message, skill_level, slider_rect, selected_color):
    screen.fill("gray30")
    title_surface = title_font.render("Choose Game Mode", True, "white")
    title_rect = title_surface.get_rect(center=(WIDTH // 2, 105))
    screen.blit(title_surface, title_rect)

    buttons = get_menu_buttons()
    draw_button(screen, buttons[MODE_PVP], "Player vs Player", font, selected_mode == MODE_PVP)
    draw_button(screen, buttons[MODE_AI], "Player vs AI", font, selected_mode == MODE_AI)

    if selected_mode == MODE_AI:
        # Re-center random button based on logic
        buttons["Play Random"] = pygame.Rect(WIDTH // 2 - 50, 250, 100, 40)
        
        draw_button(screen, buttons["Play White"], "White", small_font, selected_color == "White")
        draw_button(screen, buttons["Play Random"], "Random", small_font, selected_color == "Random")
        draw_button(screen, buttons["Play Black"], "Black", small_font, selected_color == "Black")
        
        draw_slider(screen, font, slider_rect, skill_level)
        draw_button(screen, buttons["Start AI"], "Start Match", font)

    if error_message:
        error_surface = small_font.render(error_message, True, "tomato")
        error_rect = error_surface.get_rect(center=(WIDTH // 2, WINDOW_HEIGHT - 45))
        screen.blit(error_surface, error_rect)

def info_banner(screen, font, small_font, board, game_mode, skill_level, player_color):
    pygame.draw.rect(screen, "gray20", (0, 0, WIDTH, BANNER_HEIGHT))

    if board.is_checkmate():
        if game_mode == MODE_AI:
            text = "Checkmate! You Lose" if board.turn == player_color else "Checkmate! You Win"
        else:
            winner = "Black" if board.turn == chess.WHITE else "White"
            text = f"Checkmate! {winner} Wins"
    elif board.is_stalemate():
        text = "Stalemate! You Tied"
    else:
        if game_mode == MODE_AI:
            turn_text = "Player" if board.turn == player_color else "AI"
            if skill_level is not None:
                turn_text += f" (Lvl {skill_level})" if board.turn != player_color else ""
        else:
            turn_text = "White" if board.turn == chess.WHITE else "Black"
        text = f"Turn: {turn_text}"

    text_surface = font.render(text, True, "white")
    text_rect = text_surface.get_rect(center=(WIDTH // 2, BANNER_HEIGHT // 2))
    screen.blit(text_surface, text_rect)
    draw_button(screen, MENU_BUTTON_RECT, "Menu", small_font)

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

    left_label = font.render("Captured", True, "white")
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

def start_new_game(game_mode, skill_level):
    board = chess.Board()
    engine = None

    if game_mode == MODE_AI:
        try:
            engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
            try:
                engine.configure({"Skill Level": skill_level})
            except chess.engine.EngineError:
                pass
        except Exception:
            return None, None, "Could not start Stockfish. Check STOCKFISH_PATH."

    return board, engine, ""

def close_engine(engine):
    if engine:
        try:
            engine.quit()
        except Exception:
            pass

def player_can_move(board, game_mode, ai_thinking, player_color):
    return not board.is_game_over() and not ai_thinking and (game_mode == MODE_PVP or board.turn == player_color)

def player_active(board, game_mode, piece, player_color):
    if not piece or piece.color != board.turn:
        return False
    return game_mode == MODE_PVP or piece.color == player_color

def fetch_ai_move(board, engine, skill_level, move_queue):
    """Calculates the AI move in a background thread."""
    try:
        think_time = 0.1 + (skill_level * 0.05)
        limit = chess.engine.Limit(time=think_time)
        result = engine.play(board, limit)
        if result.move:
            move_queue.put(result.move)
    except Exception as e:
        move_queue.put(e) # Pass the crash back to the main thread safely

def main():
    # Initialize Pygame and set up window
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Chess")
    clock = pygame.time.Clock()

    load_images()

    running = True
    app_state = STATE_MENU
    board = None
    engine = None
    game_mode = None
    selected_mode = None
    menu_error = ""
    
    selected_square = None
    dragging = False

    # AI and Slider Variables
    skill_level = 10 
    slider_rect = pygame.Rect(WIDTH // 2 - 150, 340, 300, 10)
    slider_dragging = False
    ai_queue = queue.Queue()
    ai_thinking = False
    
    selected_color = "White"
    game_player_color = chess.WHITE
    # Main application loop
    while running:
        mouse_pos = pygame.mouse.get_pos()
        font = pygame.font.SysFont(None, 36)
        title_font = pygame.font.SysFont(None, 48)
        small_font = pygame.font.SysFont(None, 24)
        
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif app_state == STATE_MENU:
                buttons = get_menu_buttons()
                buttons["Play Random"] = pygame.Rect(WIDTH // 2 - 50, 250, 100, 40)
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if buttons[MODE_PVP].collidepoint(event.pos):
                        selected_mode = MODE_PVP
                        board, engine, menu_error = start_new_game(MODE_PVP, None)
                        if board:
                            app_state = STATE_PLAYING
                            game_mode = MODE_PVP
                            game_player_color = chess.WHITE # Default orientation for PvP
                            
                    elif buttons[MODE_AI].collidepoint(event.pos):
                        selected_mode = MODE_AI
                        menu_error = ""
                        
                    elif selected_mode == MODE_AI:
                        # Check color buttons
                        if buttons["Play White"].collidepoint(event.pos):
                            selected_color = "White"
                        elif buttons["Play Random"].collidepoint(event.pos):
                            selected_color = "Random"
                        elif buttons["Play Black"].collidepoint(event.pos):
                            selected_color = "Black"
                            
                        # Check if clicking the slider knob
                        percent = skill_level / 20.0
                        knob_x = slider_rect.x + int(percent * slider_rect.width)
                        knob_rect = pygame.Rect(knob_x - 10, slider_rect.y - 15, 20, 40)
                        
                        if knob_rect.collidepoint(event.pos) or slider_rect.collidepoint(event.pos):
                            slider_dragging = True
                            
                        # Check if clicking Start Game
                        elif buttons["Start AI"].collidepoint(event.pos):
                            if selected_color == "Random":
                                game_player_color = random.choice([chess.WHITE, chess.BLACK])
                            elif selected_color == "Black":
                                game_player_color = chess.BLACK
                            else:
                                game_player_color = chess.WHITE
                                
                            board, engine, menu_error = start_new_game(MODE_AI, skill_level)
                            if board:
                                app_state = STATE_PLAYING
                                game_mode = MODE_AI

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    slider_dragging = False

                elif event.type == pygame.MOUSEMOTION:
                    if slider_dragging:
                        relative_x = event.pos[0] - slider_rect.x
                        percentage = max(0, min(1, relative_x / slider_rect.width))
                        skill_level = int(percentage * 20)

            elif app_state == STATE_PLAYING:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if MENU_BUTTON_RECT.collidepoint(event.pos):
                        close_engine(engine)
                        engine = None
                        board = None
                        app_state = STATE_MENU
                        selected_square = None
                        dragging = False
                        ai_thinking = False
                        # Clear old AI moves
                        while not ai_queue.empty():
                            ai_queue.get()
                        continue

                    # Drag piece
                    clicked_square = get_square_from_mouse(event.pos, game_player_color)
                    if clicked_square is not None and player_can_move(board, game_mode, ai_thinking, game_player_color):
                        piece = board.piece_at(clicked_square)
                        if player_active(board, game_mode, piece, game_player_color):
                            selected_square = clicked_square
                            dragging = True

                # Drop piece
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and dragging:
                        drop_square = get_square_from_mouse(event.pos, game_player_color)
                        if drop_square is not None:
                            move = chess.Move(selected_square, drop_square)

                            if move not in board.legal_moves:
                                move = chess.Move(selected_square, drop_square, promotion=chess.QUEEN)

                            if move in board.legal_moves:
                                board.push(move)

                        selected_square = None
                        dragging = False

        # AI Auto-Start 
        if app_state == STATE_PLAYING and game_mode == MODE_AI and not board.is_game_over():
            if board.turn != game_player_color and not ai_thinking:
                ai_thinking = True
                threading.Thread(
                    target=fetch_ai_move,
                    args=(board.copy(), engine, skill_level, ai_queue),
                    daemon=True
                ).start()

        # Check if the AI thread has finished thinking
        if ai_thinking and not ai_queue.empty():
            ai_result = ai_queue.get()
            
            if isinstance(ai_result, Exception):
                close_engine(engine)
                engine = None
                board = None
                app_state = STATE_MENU
                menu_error = "Stockfish stopped. Returning to menu."
            else:
                board.push(ai_result)
                
            ai_thinking = False

        # Rendering
        if app_state == STATE_MENU:
            draw_menu(screen, title_font, font, small_font, selected_mode, menu_error, skill_level, slider_rect, selected_color)
        else:
            screen.fill("gray30")
            info_banner(screen, font, small_font, board, game_mode, skill_level if game_mode == MODE_AI else None, game_player_color)
            draw_board(screen)
            draw_possible_moves(screen, board, selected_square, game_player_color)
            
            if dragging:
                draw_pieces(screen, board, game_player_color, selected_square, mouse_pos)
            else:
                draw_pieces(screen, board, game_player_color)

            draw_captured_pieces(screen, board)
        
        pygame.display.flip()
        clock.tick(MAX_FPS)

    close_engine(engine)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()