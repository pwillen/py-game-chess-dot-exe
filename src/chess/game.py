from dataclasses import dataclass
from enum import Enum

from chess.board import ChessBoard, Position
from chess.moves import MoveGenerator
from chess.pieces import Color


class GameStatus(Enum):
    ACTIVE = "active"
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    DRAW = "draw"
    RESIGNED = "resigned"


@dataclass(frozen=True)
class CastlingRights:
    white_king_side: bool = True
    white_queen_side: bool = True
    black_king_side: bool = True
    black_queen_side: bool = True


class ChessGame:
    def __init__(self):
        self.board = ChessBoard()
        self.side_to_move = Color.WHITE
        self.status = GameStatus.ACTIVE
        self.last_move: tuple[Position, Position] | None = None
        self.castling_rights = CastlingRights()
        self.en_passant_target: Position | None = None

    def move(self, from_position: Position, to_position: Position) -> bool:
        piece = self.board.get_piece(from_position)
        if piece and piece.color == self.side_to_move:
            valid_moves = MoveGenerator.generate_piece_moves(self.board, from_position, piece)
            if any(move.to_position == to_position for move in valid_moves):
                self.board.set_piece(to_position, piece)
                self.board.set_piece(from_position, None)
                self.last_move = (from_position, to_position)
                self.en_passant_target = None
                self.side_to_move = Color.BLACK if self.side_to_move == Color.WHITE else Color.WHITE
                return True
        return False