import pygame

from chess.ui import ChessUI, WINDOW_HEIGHT, WINDOW_WIDTH


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

        ui.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
