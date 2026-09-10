from enum import Enum


class Color(Enum):
    WHITE = 1
    BLACK = 2

class Piece:
    def __init__(self, color: Color):
        self.color = color

class Pawn(Piece):
    pass

class Rook(Piece):
    pass

class Knight(Piece):
    pass

class Bishop(Piece):
    pass

class Queen(Piece):
    pass

class King(Piece):
    pass