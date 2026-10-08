from dataclasses import dataclass
from enum import Enum

from chess.board import ChessBoard, Position
from chess.moves import Move, MoveGenerator
from chess.pieces import Color, Queen


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
    """
    Represents a chess game, managing the state of the board, active player, game status, and moves.
    """
    def __init__(self):
        self.board = ChessBoard()
        self.active_player = Color.LIGHT
        self.status = GameStatus.ACTIVE
        self.last_move: tuple[Position, Position] | None = None
        self.castling_rights = CastlingRights()
        self.en_passant_target: Position | None = None

    def move(self, from_position: Position, to_position: Position) -> bool:
        """
        Executes a move from the specified starting position to the target position if it's valid.
        Args:
            from_position: The starting position of the piece to move.
            to_position: The target position to move the piece to.

        Returns:
            True if the move was successfully executed, False otherwise.

        """
        piece = self.board.get_piece(from_position)
        if piece and piece.color is self.active_player:
            valid_moves = MoveGenerator.generate_legal_piece_moves(self.board, from_position, piece)
            selected_move = self._resolve_move_to_destination(valid_moves, to_position)
            if selected_move is not None:
                MoveGenerator.apply_move_on_board(self.board, selected_move, piece)
                self.last_move = (from_position, to_position)
                self.en_passant_target = None
                self.active_player = Color.DARK if self.active_player is Color.LIGHT else Color.LIGHT
                return True
        return False

    @staticmethod
    def _resolve_move_to_destination(moves: list[Move], to_position: Position) -> Move | None:
        destination_moves = [move for move in moves if move.to_position == to_position]
        if not destination_moves:
            return None

        for move in destination_moves:
            if move.promotion_piece_type is Queen:
                return move
        return destination_moves[0]