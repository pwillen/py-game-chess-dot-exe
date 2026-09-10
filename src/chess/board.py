from dataclasses import dataclass

from chess.pieces import Bishop, Color, King, Knight, Pawn, Piece, Queen, Rook


@dataclass(frozen=True)
class Position:
    index: int

    @property
    def row(self) -> int:
        return self.index // 8

    @property
    def col(self) -> int:
        return self.index % 8

    @staticmethod
    def from_row_col(row: int, col: int) -> "Position":
        return Position((row * 8) + col)

    @property
    def file(self) -> str:
        return chr(self.col + ord('a'))

    @property
    def rank(self) -> str:
        return str(8 - self.row)

    @property
    def name(self) -> str:
        return f"{self.file}{self.rank}"

    @staticmethod
    def from_name(name: str) -> "Position":
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
    def __init__(self, position: Position, piece: Piece | None = None):
        self.position = position
        self.piece = piece

    def set_piece(self, piece: Piece | None):
        self.piece = piece

    @property
    def is_occupied(self) -> bool:
        return self.piece is not None

class ChessBoard:
    def __init__(self):
        self.board = None
        self.setup_board()

    def setup_board(self):
        self.board = [
            [
                Square(position=Position.from_row_col(0, 0), piece=Rook(color=Color.WHITE)),
                Square(position=Position.from_row_col(0, 1), piece=Knight(color=Color.WHITE)),
                Square(position=Position.from_row_col(0, 2), piece=Bishop(color=Color.WHITE)),
                Square(position=Position.from_row_col(0, 3), piece=Queen(color=Color.WHITE)),
                Square(position=Position.from_row_col(0, 4), piece=King(color=Color.WHITE)),
                Square(position=Position.from_row_col(0, 5), piece=Bishop(color=Color.WHITE)),
                Square(position=Position.from_row_col(0, 6), piece=Knight(color=Color.WHITE)),
                Square(position=Position.from_row_col(0, 7), piece=Rook(color=Color.WHITE)),
            ],
            [Square(position=Position.from_row_col(1, i), piece=Pawn(color=Color.WHITE)) for i in range(8)],
            [Square(position=Position.from_row_col(2, i)) for i in range(8)],
            [Square(position=Position.from_row_col(3, i)) for i in range(8)],
            [Square(position=Position.from_row_col(4, i)) for i in range(8)],
            [Square(position=Position.from_row_col(5, i)) for i in range(8)],
            [Square(position=Position.from_row_col(6, i), piece=Pawn(color=Color.BLACK)) for i in range(8)],
            [
                Square(position=Position.from_row_col(7, 0), piece=Rook(color=Color.BLACK)),
                Square(position=Position.from_row_col(7, 1), piece=Knight(color=Color.BLACK)),
                Square(position=Position.from_row_col(7, 2), piece=Bishop(color=Color.BLACK)),
                Square(position=Position.from_row_col(7, 3), piece=Queen(color=Color.BLACK)),
                Square(position=Position.from_row_col(7, 4), piece=King(color=Color.BLACK)),
                Square(position=Position.from_row_col(7, 5), piece=Bishop(color=Color.BLACK)),
                Square(position=Position.from_row_col(7, 6), piece=Knight(color=Color.BLACK)),
                Square(position=Position.from_row_col(7, 7), piece=Rook(color=Color.BLACK)),
            ],
        ]

    def get_piece(self, position: Position) -> Piece | None:
        square = self.board[position.row][position.col]
        return square.piece

    def set_piece(self, position: Position, piece: Piece | None):
        square = self.board[position.row][position.col]
        square.set_piece(piece)
