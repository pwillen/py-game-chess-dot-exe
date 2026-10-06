from abc import ABC, abstractmethod
from enum import Enum


class Color(Enum):
    WHITE = 1
    BLACK = 2


class Piece(ABC):
    def __init__(self, color: Color):
        self.color = color

    @property
    @abstractmethod
    def symbol(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.symbol

    def __repr__(self) -> str:
        return f"{self.color.name} {self.__class__.__name__}"


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


Pieces = {Pawn, Knight, Bishop, Rook, Queen, King}