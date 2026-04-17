import pygame
import sys

# Configuration
WIDTH = HEIGHT = 512
MAX_FPS = 15

def main():
    # Initialize Pygame and set up window
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Player vs Stockfish")
    clock = pygame.time.Clock()
    
    running = True
    
    # Main application loop
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Rendering
        screen.fill((50, 50, 50))
        
        pygame.display.flip()
        clock.tick(MAX_FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()