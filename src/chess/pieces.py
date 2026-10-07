from abc import ABC, abstractmethod
from enum import StrEnum


class Color(StrEnum):
    LIGHT = "l"
    DARK = "d"


class Piece(ABC):
    """
    Abstract base class for chess pieces.
    Each piece has a color (light or dark) and a symbol representing it.
    """
    def __init__(self, color: Color):
        self.color = color

    @property
    @abstractmethod
    def symbol(self) -> str:
        raise NotImplementedError

    @property
    def is_light(self) -> bool:
        return self.color == Color.LIGHT

    @property
    def is_dark(self) -> bool:
        return self.color == Color.DARK

    @property
    def sprite_filename(self) -> str:
        return f"Chess_{self.symbol}{self.color.value}t160.png"

    def __str__(self) -> str:
        return self.symbol

    def __repr__(self) -> str:
        return f"{self.color.name} {self.__class__.__name__}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Piece) and type(self) is type(other) and self.color == other.color

    def __hash__(self) -> int:
        return hash((type(self), self.color))


class Pawn(Piece):
    @property
    def symbol(self) -> str:
        return 'p'


class Rook(Piece):
    @property
    def symbol(self) -> str:
        return 'r'


class Knight(Piece):
    @property
    def symbol(self) -> str:
        return 'n'


class Bishop(Piece):
    @property
    def symbol(self) -> str:
        return 'b'


class Queen(Piece):
    @property
    def symbol(self) -> str:
        return 'q'


class King(Piece):
    @property
    def symbol(self) -> str:
        return 'k'


PIECES = {Pawn, Knight, Bishop, Rook, Queen, King}
PIECE_VARIANTS = {piece_type(color) for piece_type in PIECES for color in Color}