import pygame

from chess.board import Position
from chess.game import ChessGame
from chess.moves import MoveGenerator
from chess.pieces import Bishop, King, Knight, Pawn, Queen, Rook, Color, Piece


BOARD_SIZE = 640
SQUARE_SIZE = BOARD_SIZE // 8
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 720
BOARD_LEFT = 20
BOARD_TOP = 20
PANEL_LEFT = BOARD_LEFT + BOARD_SIZE + 20

LIGHT_SQUARE = pygame.Color("#f0d9b5")
DARK_SQUARE = pygame.Color("#b58863")
HIGHLIGHT_SQUARE = pygame.Color(255, 215, 0, 120)
SELECTED_SQUARE = pygame.Color(80, 180, 255, 140)
MOVE_DOT = pygame.Color(40, 40, 40, 180)
TEXT_COLOR = pygame.Color("white")
BACKGROUND = pygame.Color("#1f1f1f")


class ChessUI:
    def __init__(self):
        self.game = ChessGame()
        self.selected_position: Position | None = None
        self.legal_moves: list = []
        self.font = pygame.font.SysFont("arial", 34, bold=True)
        self.small_font = pygame.font.SysFont("arial", 22)

    def handle_click(self, mouse_pos: tuple[int, int]):
        position = self._mouse_to_position(mouse_pos)
        if position is None:
            self.selected_position = None
            self.legal_moves = []
            return

        piece = self.game.board.get_piece(position)
        if self.selected_position is None:
            if piece and piece.color == self.game.side_to_move:
                self.selected_position = position
                self.legal_moves = MoveGenerator.generate_piece_moves(self.game.board, position, piece)
            return

        if position == self.selected_position:
            self.selected_position = None
            self.legal_moves = []
            return

        if any(move.to_position == position for move in self.legal_moves):
            self.game.move(self.selected_position, position)
        elif piece and piece.color == self.game.side_to_move:
            self.selected_position = position
            self.legal_moves = MoveGenerator.generate_piece_moves(self.game.board, position, piece)
            return

        self.selected_position = None
        self.legal_moves = []

    def draw(self, screen: pygame.Surface):
        screen.fill(BACKGROUND)
        self._draw_board(screen)
        self._draw_highlights(screen)
        self._draw_pieces(screen)
        self._draw_sidebar(screen)

    def _draw_board(self, screen: pygame.Surface):
        for row in range(8):
            for col in range(8):
                rect = pygame.Rect(
                    BOARD_LEFT + (col * SQUARE_SIZE),
                    BOARD_TOP + (row * SQUARE_SIZE),
                    SQUARE_SIZE,
                    SQUARE_SIZE,
                )
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(screen, color, rect)

    def _draw_highlights(self, screen: pygame.Surface):
        overlay = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)

        if self.selected_position is not None:
            self._fill_square(overlay, self.selected_position, SELECTED_SQUARE)

        for move in self.legal_moves:
            self._fill_square(overlay, move.to_position, HIGHLIGHT_SQUARE)
            self._draw_move_dot(overlay, move.to_position)

        screen.blit(overlay, (BOARD_LEFT, BOARD_TOP))

    def _fill_square(self, surface: pygame.Surface, position: Position, color: pygame.Color):
        rect = pygame.Rect(
            position.col * SQUARE_SIZE,
            position.row * SQUARE_SIZE,
            SQUARE_SIZE,
            SQUARE_SIZE,
        )
        pygame.draw.rect(surface, color, rect)

    def _draw_move_dot(self, surface: pygame.Surface, position: Position):
        center = (
            position.col * SQUARE_SIZE + (SQUARE_SIZE // 2),
            position.row * SQUARE_SIZE + (SQUARE_SIZE // 2),
        )
        pygame.draw.circle(surface, MOVE_DOT, center, 10)

    def _draw_pieces(self, screen: pygame.Surface):
        for index in range(64):
            position = Position(index)
            piece = self.game.board.get_piece(position)
            if piece is None:
                continue
            center = self._square_center(position)
            self._draw_piece(screen, piece, center)

    def _draw_piece(self, screen: pygame.Surface, piece: Piece, center: tuple[int, int]):
        label = self._piece_label(piece)
        color = pygame.Color("white") if piece.color == Color.WHITE else pygame.Color("black")
        outline = pygame.Color("black") if piece.color == Color.WHITE else pygame.Color("white")
        text = self.font.render(label, True, color)
        shadow = self.font.render(label, True, outline)
        shadow_rect = shadow.get_rect(center=(center[0] + 2, center[1] + 2))
        text_rect = text.get_rect(center=center)
        screen.blit(shadow, shadow_rect)
        screen.blit(text, text_rect)

    def _piece_label(self, piece: Piece) -> str:
        labels = {
            Pawn: "P",
            Knight: "N",
            Bishop: "B",
            Rook: "R",
            Queen: "Q",
            King: "K",
        }
        return labels[type(piece)]

    def _draw_sidebar(self, screen: pygame.Surface):
        title = self.small_font.render("Chess", True, TEXT_COLOR)
        turn = self.small_font.render(f"Turn: {self.game.side_to_move.name}", True, TEXT_COLOR)
        status = self.small_font.render(f"Status: {self.game.status.name}", True, TEXT_COLOR)
        screen.blit(title, (PANEL_LEFT, 30))
        screen.blit(turn, (PANEL_LEFT, 70))
        screen.blit(status, (PANEL_LEFT, 100))
        if self.selected_position is not None:
            selected = self.small_font.render(f"Selected: {self.selected_position.name}", True, TEXT_COLOR)
            screen.blit(selected, (PANEL_LEFT, 140))

    def _square_center(self, position: Position) -> tuple[int, int]:
        return (
            BOARD_LEFT + (position.col * SQUARE_SIZE) + (SQUARE_SIZE // 2),
            BOARD_TOP + (position.row * SQUARE_SIZE) + (SQUARE_SIZE // 2),
        )

    def _mouse_to_position(self, mouse_pos: tuple[int, int]) -> Position | None:
        x, y = mouse_pos
        if x < BOARD_LEFT or y < BOARD_TOP:
            return None
        board_x = x - BOARD_LEFT
        board_y = y - BOARD_TOP
        if board_x >= BOARD_SIZE or board_y >= BOARD_SIZE:
            return None
        col = board_x // SQUARE_SIZE
        row = board_y // SQUARE_SIZE
        return Position.from_row_col(row, col)
