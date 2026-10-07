from dataclasses import dataclass

from chess.pieces import Bishop, Color, King, Knight, Pawn, Piece, Queen, Rook


@dataclass(frozen=True)
class Position:
    """
    Represents a position on the chessboard using a single integer index (0-63).
    Includes methods to convert between row/column and algebraic notation (e.g., "e4").
    """
    index: int

    @property
    def row(self) -> int:
        return self.index // 8

    @property
    def col(self) -> int:
        return self.index % 8

    @staticmethod
    def from_row_col(row: int, col: int) -> "Position":
        """
        Creates a Position object from row and column indices.
        Args:
            row: The row index (0-7).
            col: The column index (0-7).

        Returns:
            A Position (0-63) object representing the specified row and column.
        """
        return Position((row * 8) + col)

    @property
    def file(self) -> str:
        """
        Returns the file (Chess notation for column) of the position in algebraic notation (a-h).
        Returns:
            A string representing the file (a-h).
        """
        return chr(self.col + ord('a'))

    @property
    def rank(self) -> str:
        """
        Returns the rank (Chess notation for row) of the position in algebraic notation (1-8).
        Returns:
            A string representing the rank (1-8).
        """
        return str(8 - self.row)

    @property
    def name(self) -> str:
        """
        Returns the Chess notation (e.g., "e4") for the position.
        Returns:
            A string representing the position in Chess notation.
        """
        return f"{self.file}{self.rank}"

    @staticmethod
    def from_name(name: str) -> "Position":
        """
        Creates a Position object from a Chess notation string (e.g., "e4").
        Args:
            name: A string representing the position in Chess notation.

        Returns:
            A Position (0-63) object representing the specified Chess notation.
        """
        if len(name) < 2:
            raise ValueError(f"Invalid position • {name}")

        file = ord(name[0].lower()) - ord("a")
        rank = int(name[1:])
        if not 0 <= file < 8:
            raise ValueError(f"Invalid file • {name[0]} in position • {name}")
        if not 1 <= rank <= 8:
            raise ValueError(f"Invalid rank • {name[1:]} in position • {name}")

        return Position.from_row_col(8 - rank, file)


class Square:
    """
    Represents a square on the chessboard, which can hold a piece or be empty.
    """
    def __init__(self, position: Position, piece: Piece | None = None):
        """
        Initializes a Square with a position and an optional piece.
        Args:
            position: The position i.e. 0-63 index of the square on the chessboard.
            piece: The piece occupying the square, or None if the square is empty.
        """
        self.position = position
        self.piece = piece

    def set_piece(self, piece: Piece | None):
        """
        Sets the piece on the square. If piece is None, the square becomes empty.
        Args:
            piece: The piece to place on the square, or None to empty the square.

        Returns:
            None
        """
        self.piece = piece

    @property
    def is_occupied(self) -> bool:
        return self.piece is not None

class ChessBoard:
    """
    Represents a chessboard with an 8x8 grid of squares. Each square can hold a piece or be empty.
    """

    STARTING_PIECES: tuple[tuple[Position, Piece], ...] = (
        # Light back rank
        (Position.from_row_col(0, 0), Rook(Color.LIGHT)),
        (Position.from_row_col(0, 1), Knight(Color.LIGHT)),
        (Position.from_row_col(0, 2), Bishop(Color.LIGHT)),
        (Position.from_row_col(0, 3), Queen(Color.LIGHT)),
        (Position.from_row_col(0, 4), King(Color.LIGHT)),
        (Position.from_row_col(0, 5), Bishop(Color.LIGHT)),
        (Position.from_row_col(0, 6), Knight(Color.LIGHT)),
        (Position.from_row_col(0, 7), Rook(Color.LIGHT)),
        # Light pawns
        *tuple((Position.from_row_col(1, col), Pawn(Color.LIGHT)) for col in range(8)),
        # Dark pawns
        *tuple((Position.from_row_col(6, col), Pawn(Color.DARK)) for col in range(8)),
        # Dark back rank
        (Position.from_row_col(7, 0), Rook(Color.DARK)),
        (Position.from_row_col(7, 1), Knight(Color.DARK)),
        (Position.from_row_col(7, 2), Bishop(Color.DARK)),
        (Position.from_row_col(7, 3), Queen(Color.DARK)),
        (Position.from_row_col(7, 4), King(Color.DARK)),
        (Position.from_row_col(7, 5), Bishop(Color.DARK)),
        (Position.from_row_col(7, 6), Knight(Color.DARK)),
        (Position.from_row_col(7, 7), Rook(Color.DARK)),
    )

    def __init__(self):
        """
        Initializes an empty chessboard and sets up the initial position of the pieces.
        """
        self.board = None
        self.setup_board()

    def setup_board(self):
        """
        Sets up the initial position of the chessboard with pieces in their starting squares.
        """
        # 1. create empty 8x8 board
        self.board = [
            [Square(position=Position.from_row_col(row, col)) for col in range(8)]
            for row in range(8)
        ]

        # 2. place starting pieces
        for position, piece in self.STARTING_PIECES:
            self.set_piece(position, piece)

    def iter_pieces(self):
        for row in self.board:
            for square in row:
                if square.piece is not None:
                    yield square.position, square.piece

    def get_piece(self, position: Position) -> Piece | None:
        """
        Retrieves the piece at the specified position on the chessboard.
        Args:
            position: The position (0-63) of the square on the chessboard.

        Returns:
            The piece at the specified position, or None if the square is empty.
        """
        square = self.board[position.row][position.col]
        return square.piece

    def set_piece(self, position: Position, piece: Piece | None):
        """
        Sets the piece at the specified position on the chessboard.
        Args:
            position: The position (0-63) of the square on the chessboard.
            piece: The piece to place on the square, or None to empty the square.

        Returns:
            None
        """
        square = self.board[position.row][position.col]
        square.set_piece(piece)