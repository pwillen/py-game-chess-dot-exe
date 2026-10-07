import pygame

from ui.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from ui.game_window import ChessUI


def main():
    pygame.init()
    pygame.display.set_caption("Chess")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    ui = ChessUI()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                ui.handle_click(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                ui.handle_hover(event.pos)

        # Render the new frame based on game state and user interactions
        ui.draw_frame(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()