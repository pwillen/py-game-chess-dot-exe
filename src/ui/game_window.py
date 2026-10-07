import pygame

from chess.board import Position
from chess.game import ChessGame
from chess.moves import MoveGenerator
from chess.pieces import Piece, PIECE_VARIANTS
from settings import ASSETS_DIR
from ui.constants import BACKGROUND, BOARD_LEFT, BOARD_SIZE, BOARD_TOP, HIGHLIGHT_SQUARE, MOVE_DOT, PANEL_LEFT, SELECTED_SQUARE, SQUARE_SIZE, TEXT_COLOR
from ui.geometry import BoardGeometry, PixelPoint

PIECE_RENDER_SIZE = int(SQUARE_SIZE * 0.85)


class ChessUI:
    board_path = ASSETS_DIR / 'board' / 'board.png'
    pieces_dir = ASSETS_DIR / 'pieces'
    dark_dir = pieces_dir / 'dark'
    light_dir = pieces_dir / 'light'

    def __init__(self):
        self.game = ChessGame()
        self.geometry = BoardGeometry(BOARD_LEFT, BOARD_TOP, SQUARE_SIZE, BOARD_SIZE)
        self.selected_position: Position | None = None
        self.legal_moves: list = []
        self.hovered_position: Position | None = None
        self.hover_moves: list = []
        self.small_font = pygame.font.SysFont('Arial', 22)
        self.board_image = self._load_board_image()
        self.piece_surfaces = self._load_piece_surfaces()

    def handle_hover(self, mouse_pos: tuple[int, int]):
        """
        Handles mouse hover events to determine the currently hovered square and possible moves for the piece on that square.
        Args:
            mouse_pos: A tuple (x, y) representing the mouse position in pixels based on pygame event

        Returns:
            None

        """
        # Design choice: Hovering over other pieces while a piece is selected does not change the hover state
        if self.selected_position is not None:
            return

        position = self.geometry.mouse_to_position(mouse_pos)
        # Check if the mouse is outside the board area
        if position is None:
            self.hovered_position = None
            self.hover_moves = []
            return

        piece = self.game.board.get_piece(position)

        # Check if the hovered square contains a piece of the current player's color
        if piece and piece.color == self.game.side_to_move:
            self.hovered_position = position
            self.hover_moves = MoveGenerator.generate_piece_moves(self.game.board, position, piece)
            return

        # No change otherwise, reset hovered position and moves if the mouse is not over a valid piece
        self.hovered_position = None
        self.hover_moves = []

    def handle_click(self, mouse_pos: tuple[int, int]):
        """
        Handles mouse click events to select and move pieces on the chessboard.
        Args:
            mouse_pos: A tuple (x, y) representing the mouse position in pixels based on pygame event

        Returns:
            None
        """
        position = self.geometry.mouse_to_position(mouse_pos)

        # Check if the mouse is outside the board area
        if position is None:
            self.selected_position = None
            self.legal_moves = []
            self.hovered_position = None
            self.hover_moves = []
            return

        piece = self.game.board.get_piece(position)

        # If no piece is currently selected, select the piece on the clicked square if it belongs to the current player
        if self.selected_position is None:
            if piece and piece.color == self.game.side_to_move:
                self.selected_position = position
                self.legal_moves = MoveGenerator.generate_piece_moves(self.game.board, position, piece)
                self.hovered_position = None
                self.hover_moves = []
            return

        # If the clicked position is the same as the currently selected position, deselect it
        if position == self.selected_position:
            self.selected_position = None
            self.legal_moves = []
            # Hover state should be updated to reflect the current mouse position after deselecting
            self.handle_hover(mouse_pos)
            return

        # Check if the clicked position is a legal move for the selected piece
        if any(move.to_position == position for move in self.legal_moves):
            self.game.move(self.selected_position, position)
        elif piece and piece.color == self.game.side_to_move:
            self.selected_position = position
            self.legal_moves = MoveGenerator.generate_piece_moves(self.game.board, position, piece)
            return

        self.selected_position = None
        self.legal_moves = []
        self.handle_hover(mouse_pos)

    def draw_frame(self, screen: pygame.Surface):
        """
        Draws the entire chess UI FRAME to be specific on the given screen surface.
        Args:
            screen: A pygame.Surface object representing the screen to draw on.

        Returns:
            None
        """
        screen.fill(BACKGROUND)
        self._draw_board(screen)
        self._draw_highlights(screen)
        self._draw_pieces(screen)
        self._draw_sidebar(screen)

    def _draw_board(self, screen: pygame.Surface):
        """
        Draws the chessboard on the given screen surface.
        Args:
            screen: A pygame.Surface object representing the screen to draw on.

        Returns:
            None
        """
        screen.blit(self.board_image, (BOARD_LEFT, BOARD_TOP))

    def _draw_highlights(self, screen: pygame.Surface):
        """
        Draws highlights for the selected square and legal moves on the given screen surface.
        Args:
            screen: A pygame.Surface object representing the screen to draw on.

        Returns:
            None

        """
        # Create a transparent overlay surface to draw highlights without affecting the board image
        overlay = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)

        active_position = self.selected_position if self.selected_position is not None else self.hovered_position
        active_moves = self.legal_moves if self.selected_position is not None else self.hover_moves

        if active_position is not None:
            self._fill_square(overlay, active_position, SELECTED_SQUARE)

        for move in active_moves:
            self._fill_square(overlay, move.to_position, HIGHLIGHT_SQUARE)
            self._draw_move_dot(overlay, move.to_position)

        screen.blit(overlay, (BOARD_LEFT, BOARD_TOP))

    def _draw_pieces(self, screen: pygame.Surface):
        """
        Draw all the pieces on the board.
        Args:
            screen: A pygame.Surface object representing the screen to draw on.

        Returns:
            None
        """
        for position, piece in self.game.board.iter_pieces():
            center = self.geometry.square_center(position)
            self._draw_piece(screen, piece, center)

    def _draw_piece(self, screen: pygame.Surface, piece: Piece, center: PixelPoint):
        """
        Draws a single chess piece on the screen at the specified center position.
        Args:
            screen: A pygame.Surface object representing the screen to draw on.
            piece: The Piece object to be drawn.
            center: A PixelPoint representing the center position to draw the piece.

        Returns:
            None

        """
        image = self.piece_surfaces[piece]
        # Get the rectangle of the image for convenient placement and alignment
        rect = image.get_rect(center=(center.x, center.y))
        screen.blit(image, rect)

    def _draw_sidebar(self, screen: pygame.Surface):
        title = self.small_font.render('Chess', True, TEXT_COLOR)
        turn = self.small_font.render(f'Turn: {self.game.side_to_move.name}', True, TEXT_COLOR)
        status = self.small_font.render(f'Status: {self.game.status.name}', True, TEXT_COLOR)
        screen.blit(title, (PANEL_LEFT, 30))
        screen.blit(turn, (PANEL_LEFT, 70))
        screen.blit(status, (PANEL_LEFT, 100))
        if self.selected_position is not None:
            selected = self.small_font.render(f'Selected: {self.selected_position.name}', True, TEXT_COLOR)
            screen.blit(selected, (PANEL_LEFT, 140))

    def _fill_square(self, surface: pygame.Surface, position: Position, color: pygame.Color):
        rect = self.geometry.square_rect(position, local=True)
        pygame.draw.rect(surface, color, rect)

    def _draw_move_dot(self, surface: pygame.Surface, position: Position):
        center = self.geometry.square_center(position, local=True)
        pygame.draw.circle(surface, MOVE_DOT, (center.x, center.y), 10)

    def _load_board_image(self) -> pygame.Surface:
        """
        Loads the chessboard image from the specified path and scales it to the defined board size.
        Returns:
            A pygame.Surface object representing the scaled chessboard image.
        """
        board_image = pygame.image.load(self.board_path).convert_alpha()
        return pygame.transform.smoothscale(board_image, (BOARD_SIZE, BOARD_SIZE))

    def _load_piece_surfaces(self) -> dict[Piece, pygame.Surface]:
        """
        Loads and scales the images for all chess pieces, storing them in a dictionary for easy access.
        Returns:
            A dictionary mapping each Piece to its corresponding pygame.Surface image.
        """
        surfaces: dict[Piece, pygame.Surface] = {}
        for piece in PIECE_VARIANTS:
            source_dir = self.light_dir if piece.is_light else self.dark_dir
            source = pygame.image.load(source_dir / piece.sprite_filename).convert_alpha()
            scaled = pygame.transform.smoothscale(source, (PIECE_RENDER_SIZE, PIECE_RENDER_SIZE))
            surfaces[piece] = scaled
        return surfaces