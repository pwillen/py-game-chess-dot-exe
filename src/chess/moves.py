from dataclasses import dataclass
from enum import Enum

from chess.board import ChessBoard, Position
from chess.pieces import Bishop, Color, King, Knight, Pawn, Piece, Queen, Rook


class Promotion(Enum):
    QUEEN = "Q"
    KNIGHT = "N"
    ROOK = "R"
    BISHOP = "B"


@dataclass(frozen=True)
class Move:
    from_position: Position
    to_position: Position
    promotion: Promotion | None = None


class MoveGenerator:
    KNIGHT_OFFSETS = (-17, -15, -10, -6, 6, 10, 15, 17)
    KING_OFFSETS = (-9, -8, -7, -1, 1, 7, 8, 9)
    BISHOP_DIRS = (-9, -7, 7, 9)
    ROOK_DIRS = (-8, -1, 1, 8)
    QUEEN_DIRS = (-9, -8, -7, -1, 1, 7, 8, 9)

    @staticmethod
    def in_bounds(index: int) -> bool:
        return 0 <= index < 64

    @staticmethod
    def same_file(a: Position, b: Position) -> bool:
        return a.col == b.col

    @staticmethod
    def same_rank(a: Position, b: Position) -> bool:
        return a.row == b.row

    @staticmethod
    def generate_piece_moves(board: ChessBoard, from_position: Position, piece: Piece) -> list[Move]:
        if isinstance(piece, Pawn):
            return MoveGenerator._pawn_moves(board, from_position, piece)
        if isinstance(piece, Knight):
            return MoveGenerator._knight_moves(board, from_position, piece)
        if isinstance(piece, Bishop):
            return MoveGenerator._ray_moves(board, from_position, piece, MoveGenerator.BISHOP_DIRS)
        if isinstance(piece, Rook):
            return MoveGenerator._ray_moves(board, from_position, piece, MoveGenerator.ROOK_DIRS)
        if isinstance(piece, Queen):
            return MoveGenerator._ray_moves(board, from_position, piece, MoveGenerator.QUEEN_DIRS)
        if isinstance(piece, King):
            return MoveGenerator._king_moves(board, from_position, piece)
        return []

    @staticmethod
    def generate_all_moves(board: ChessBoard, color: Color) -> list[Move]:
        moves: list[Move] = []
        for index in range(64):
            from_position = Position(index)
            piece = board.get_piece(from_position)
            if piece and piece.color == color:
                moves.extend(MoveGenerator.generate_piece_moves(board, from_position, piece))
        return moves

    @staticmethod
    def generate_legal_moves(board: ChessBoard, color: Color) -> list[Move]:
        return MoveGenerator.generate_all_moves(board, color)

    @staticmethod
    def is_in_check(board: ChessBoard, color: Color) -> bool:
        king_position = MoveGenerator._find_king(board, color)
        if king_position is None:
            return False

        opponent = Color.DARK if color == Color.LIGHT else Color.LIGHT
        for move in MoveGenerator.generate_all_moves(board, opponent):
            if move.to_position == king_position:
                return True
        return False

    @staticmethod
    def _find_king(board: ChessBoard, color: Color) -> Position | None:
        for index in range(64):
            position = Position(index)
            piece = board.get_piece(position)
            if isinstance(piece, King) and piece.color == color:
                return position
        return None

    @staticmethod
    def _pawn_moves(board: ChessBoard, from_position: Position, piece: Pawn) -> list[Move]:
        moves: list[Move] = []
        direction = 8 if piece.color == Color.LIGHT else -8
        start_row = 1 if piece.color == Color.LIGHT else 6
        promotion_row = 7 if piece.color == Color.LIGHT else 0

        one_forward_index = from_position.index + direction
        if MoveGenerator.in_bounds(one_forward_index):
            one_forward = Position(one_forward_index)
            if board.get_piece(one_forward) is None:
                moves.extend(MoveGenerator._promotion_or_single(from_position, one_forward, promotion_row))

                two_forward_index = from_position.index + (direction * 2)
                if from_position.row == start_row and MoveGenerator.in_bounds(two_forward_index):
                    two_forward = Position(two_forward_index)
                    if board.get_piece(two_forward) is None:
                        moves.append(Move(from_position=from_position, to_position=two_forward))

        capture_offsets = (7, 9) if piece.color == Color.LIGHT else (-7, -9)
        for offset in capture_offsets:
            capture_index = from_position.index + offset
            if not MoveGenerator.in_bounds(capture_index):
                continue
            if abs(Position(capture_index).col - from_position.col) != 1:
                continue
            capture_position = Position(capture_index)
            target = board.get_piece(capture_position)
            if target and target.color != piece.color:
                moves.extend(MoveGenerator._promotion_or_single(from_position, capture_position, promotion_row))

        return moves

    @staticmethod
    def _promotion_or_single(from_position: Position, to_position: Position, promotion_row: int) -> list[Move]:
        if to_position.row != promotion_row:
            return [Move(from_position=from_position, to_position=to_position)]

        return [
            Move(from_position=from_position, to_position=to_position, promotion=promotion)
            for promotion in (
                Promotion.QUEEN,
                Promotion.ROOK,
                Promotion.BISHOP,
                Promotion.KNIGHT,
            )
        ]

    @staticmethod
    def _knight_moves(board: ChessBoard, from_position: Position, piece: Knight) -> list[Move]:
        moves: list[Move] = []
        for offset in MoveGenerator.KNIGHT_OFFSETS:
            target_index = from_position.index + offset
            if not MoveGenerator.in_bounds(target_index):
                continue
            if abs(Position(target_index).col - from_position.col) not in (1, 2):
                continue
            if abs(Position(target_index).row - from_position.row) not in (1, 2):
                continue
            target_position = Position(target_index)
            target = board.get_piece(target_position)
            if target is None or target.color != piece.color:
                moves.append(Move(from_position=from_position, to_position=target_position))
        return moves

    @staticmethod
    def _king_moves(board: ChessBoard, from_position: Position, piece: King) -> list[Move]:
        moves: list[Move] = []
        for offset in MoveGenerator.KING_OFFSETS:
            target_index = from_position.index + offset
            if not MoveGenerator.in_bounds(target_index):
                continue
            target_position = Position(target_index)
            if max(abs(target_position.col - from_position.col), abs(target_position.row - from_position.row)) != 1:
                continue
            target = board.get_piece(target_position)
            if target is None or target.color != piece.color:
                moves.append(Move(from_position=from_position, to_position=target_position))
        return moves

    @staticmethod
    def _ray_moves(
        board: ChessBoard,
        from_position: Position,
        piece: Piece,
        directions: tuple[int, ...],
    ) -> list[Move]:
        moves: list[Move] = []
        for direction in directions:
            current = from_position.index
            while True:
                next_index = current + direction
                if not MoveGenerator.in_bounds(next_index):
                    break

                if direction in (-1, 1) and Position(next_index).row != Position(current).row:
                    break
                if direction in (-9, 7) and abs(Position(next_index).col - Position(current).col) != 1:
                    break
                if direction in (-7, 9) and abs(Position(next_index).col - Position(current).col) != 1:
                    break

                target_position = Position(next_index)
                target = board.get_piece(target_position)
                if target is None:
                    moves.append(Move(from_position=from_position, to_position=target_position))
                    current = next_index
                    continue

                if target.color != piece.color:
                    moves.append(Move(from_position=from_position, to_position=target_position))
                break
        return moves