from dataclasses import dataclass, field

from chess.board import ChessBoard, Position
from chess.pieces import Bishop, Color, King, Knight, Pawn, Piece, Queen, Rook


@dataclass(frozen=True)
class BoardMutation:
    from_position: Position
    to_position: Position
    piece: Piece

@dataclass(frozen=True)
class Move:
    from_position: Position
    to_position: Position
    promotion_piece_type: type[Piece] | None = None
    extra_mutations: tuple[BoardMutation, ...] = field(default_factory=tuple)

    @property
    def has_mutation(self) -> bool:
        return bool(self.extra_mutations)

    @property
    def is_promotion(self) -> bool:
        return self.promotion_piece_type is not None

class MoveGenerator:
    """
    A class responsible for generating and validating chess moves on a given chessboard.
    """
    KNIGHT_OFFSETS = (-17, -15, -10, -6, 6, 10, 15, 17)
    KING_OFFSETS = (-9, -8, -7, -1, 1, 7, 8, 9)
    BISHOP_DIRECTIONS = (-9, -7, 7, 9)
    ROOK_DIRECTIONS = (-8, -1, 1, 8)
    QUEEN_DIRECTIONS = (-9, -8, -7, -1, 1, 7, 8, 9)
    PROMOTION_PIECE_TYPES = (Queen, Rook, Bishop, Knight)

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
    def generate_legal_piece_moves(board: ChessBoard, from_position: Position, piece: Piece) -> list[Move]:
        """
        Generate all legal moves for a given piece from a specific position on the board, considering checks.
        This is the entry point game logic calls to kick piece moving.
        Args:
            board: The chessboard on which to generate moves.
            from_position: The position of the piece to move.
            piece: The piece for which to generate moves.

        Returns:
            A list of all legal moves for the given piece from the specified position, considering checks.

        """
        candidates = MoveGenerator._generate_pseudo_piece_moves(board, from_position, piece)
        return [move for move in candidates if MoveGenerator._is_legal_move(board, move)]

    @staticmethod
    def _generate_pseudo_piece_moves(board: ChessBoard, from_position: Position, piece: Piece) -> list[Move]:
        """
        Generate all possible moves for a given piece from a specific position on the board, without considering checks.
        Args:
            board: The chessboard on which to generate moves.
            from_position: The position of the piece to move.
            piece: The piece for which to generate moves.

        Returns:
            A list of all possible moves for the given piece from the specified position, without considering checks.

        """
        if isinstance(piece, Pawn):
            return MoveGenerator._pawn_moves(board, from_position, piece)
        if isinstance(piece, Knight):
            return MoveGenerator._knight_moves(board, from_position, piece)
        if isinstance(piece, Bishop):
            # Pass in the BISHOP_DIRECTIONS to the _ray_moves method for generating bishop moves
            return MoveGenerator._ray_moves(board, from_position, piece, MoveGenerator.BISHOP_DIRECTIONS)
        if isinstance(piece, Rook):
            # Pass in the ROOK_DIRECTIONS to the _ray_moves method for generating rook moves
            return MoveGenerator._ray_moves(board, from_position, piece, MoveGenerator.ROOK_DIRECTIONS)
        if isinstance(piece, Queen):
            # Pass in the QUEEN_DIRECTIONS to the _ray_moves method for generating queen moves
            return MoveGenerator._ray_moves(board, from_position, piece, MoveGenerator.QUEEN_DIRECTIONS)
        if isinstance(piece, King):
            return MoveGenerator._king_moves(board, from_position, piece)
        return []

    @staticmethod
    def generate_all_player_moves(board: ChessBoard, color: Color) -> list[Move]:
        """
        Generate all possible moves for the specified color on the given board.
        Args:
            board: The chessboard on which to generate moves.
            color: The color of the pieces for which to generate moves.

        Returns:
            A list of all possible moves for the specified color.
        """
        moves: list[Move] = []
        for from_position, piece in board.iter_pieces(color=color):
            moves.extend(MoveGenerator._generate_pseudo_piece_moves(board, from_position, piece))
        return moves

    @staticmethod
    def is_in_check(board: ChessBoard, piece: Piece) -> bool:
        """
        Determine if the king of the specified color is in check on the given board.
        Args:
            board: The chessboard on which to check for check.
            piece: The piece for which to check if its king is in check.

        Returns:
            True if the king of the specified color is in check, False otherwise.

        """
        # Find the position of the moving piece's king on the board
        king_position = MoveGenerator._find_king(board, piece.color)

        opponent = piece.opponent_color
        # Generate all possible moves for the opponent and check if any of them can capture the king
        for move in MoveGenerator.generate_all_player_moves(board, color=opponent):
            if move.to_position == king_position:
                return True
        return False

    @staticmethod
    def _find_king(board: ChessBoard, color: Color) -> Position:
        """
        Find the position of the king of the specified color on the board.
        Args:
            board: The chessboard on which to search for the king.
            color: The color of the king to find.

        Returns:
            The position of the king of the specified color.
        Raises:
            RuntimeError: If the king of the specified color is not found on the board.
        """
        for position, piece in board.iter_pieces(color=color):
            if isinstance(piece, King):
                return position
        raise RuntimeError(f"King of color {color} not found on the board.")

    @staticmethod
    def _pawn_moves(board: ChessBoard, from_position: Position, piece: Pawn) -> list[Move]:
        moves: list[Move] = []
        # Piece color holds forward orientation
        forward_step = piece.forward_direction * 8
        forward_left_capture = forward_step - 1
        forward_right_capture = forward_step + 1
        start_row = piece.start_row
        promotion_row = piece.promotion_row

        one_forward_index = from_position.index + forward_step
        if MoveGenerator.in_bounds(one_forward_index):
            one_forward = Position(one_forward_index)
            if board.get_piece(one_forward) is None:
                moves.extend(MoveGenerator._promotion_or_single(from_position, one_forward, promotion_row))

                # No pieces in front of pawn in order to move two squares forward
                two_forward_index = from_position.index + (forward_step * 2)
                if from_position.row == start_row:
                    two_forward = Position(two_forward_index)
                    if board.get_piece(two_forward) is None:
                        moves.append(Move(from_position=from_position, to_position=two_forward))

        capture_offsets = (forward_left_capture, forward_right_capture)
        for offset in capture_offsets:
            capture_index = from_position.index + offset
            if not MoveGenerator.in_bounds(capture_index):
                continue
            # Prevent board wrapping
            if abs(Position(capture_index).col - from_position.col) != 1:
                continue
            capture_position = Position(capture_index)
            target = board.get_piece(capture_position)
            # Capture piece logic. Has to capture to move diagonally. Cannot move diagonally to empty square
            if target and target.color != piece.color:
                moves.extend(MoveGenerator._promotion_or_single(from_position, capture_position, promotion_row))

        return moves

    @staticmethod
    def _promotion_or_single(from_position: Position, to_position: Position, promotion_row: int) -> list[Move]:
        if to_position.row != promotion_row:
            return [Move(from_position=from_position, to_position=to_position)]

        return [
            Move(
                from_position=from_position,
                to_position=to_position,
                promotion_piece_type=promotion_piece_type,
            )
            for promotion_piece_type in MoveGenerator.PROMOTION_PIECE_TYPES
        ]

    @staticmethod
    def _knight_moves(board: ChessBoard, from_position: Position, piece: Knight) -> list[Move]:
        moves: list[Move] = []
        for offset in MoveGenerator.KNIGHT_OFFSETS:
            target_index = from_position.index + offset
            if not MoveGenerator.in_bounds(target_index):
                continue
            # Prevent board wrapping for knight moves
            if abs(Position(target_index).col - from_position.col) not in (1, 2):
                continue
            # Prevent board wrapping for knight moves
            if abs(Position(target_index).row - from_position.row) not in (1, 2):
                continue
            target_position = Position(target_index)
            target = board.get_piece(target_position)
            # Square has to be empty or occupied by an opponent piece to be a valid move
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
            # Prevent board wrapping for king moves
            if max(abs(target_position.col - from_position.col), abs(target_position.row - from_position.row)) != 1:
                continue
            target = board.get_piece(target_position)
            # Square has to be empty or occupied by an opponent piece to be a valid move
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

                # Prevent board wrapping for ray moves (rook, bishop, queen)
                if direction in (-1, 1) and Position(next_index).row != Position(current).row:
                    break
                # Prevent board wrapping for ray moves (bishop, queen)
                if direction in (-9, 7) and abs(Position(next_index).col - Position(current).col) != 1:
                    break
                # Prevent board wrapping for ray moves (bishop, queen)
                if direction in (-7, 9) and abs(Position(next_index).col - Position(current).col) != 1:
                    break

                target_position = Position(next_index)
                target = board.get_piece(target_position)
                # Ray moves can continue until they hit a piece. If the piece is an opponent's piece, it can be captured, but the ray cannot continue past it.
                if target is None:
                    moves.append(Move(from_position=from_position, to_position=target_position))
                    current = next_index
                    continue

                # If the target square is occupied by a piece of the same color, the ray cannot continue past it.
                # If the target square is occupied by an opponent's piece, it can be captured, but the ray cannot continue past it.
                if target.color != piece.color:
                    moves.append(Move(from_position=from_position, to_position=target_position))
                break
        return moves

    @staticmethod
    def _is_legal_move(board: ChessBoard, move: Move) -> bool:
        """
        Check if a move is legal by applying it to the board and checking if the moving piece's color is in check.
        Args:
            board: The chess board on which the move is to be applied.
            move: The move to be checked for legality.

        Returns:
            True if the move is legal, False otherwise.

        """
        # Get the piece that is moving from the source position
        moving_piece = board.get_piece(move.from_position)

        # Fast check: If there's no piece at the source position, the move is illegal
        if moving_piece is None:
            return False

        rollback_snapshot = MoveGenerator._capture_rollback_snapshot(board, move)

        try:
            # Dry run the move on the board to check if it results in a check for the moving piece's color
            MoveGenerator.apply_move_on_board(board, move, moving_piece)
            in_check = MoveGenerator.is_in_check(board, moving_piece)
        finally:
            # Revert the move to restore the original board state
            MoveGenerator.revert_move_on_board(
                board=board,
                rollback_snapshot=rollback_snapshot,
            )
        return not in_check

    @staticmethod
    def apply_move_on_board(board: ChessBoard, move: Move, moving_piece: Piece):
        """
        Apply a move to the chessboard, updating the positions of the moving piece and any captured pieces.

        Args:
            board: The chess board on which the move is to be applied.
            move: The move to be applied.
            moving_piece: The piece that is moving.

        Returns:
            None
        """

        if board.get_piece(move.from_position) is None:
            raise RuntimeError(f"No piece at {move.from_position} to apply move.")

        # Remove the moving piece from its original position
        board.set_piece(move.from_position, None)

        # Proxy for moving piece to preserve moving piece properties in case of promotion
        placed_piece = moving_piece
        if move.is_promotion:
            # noinspection calling-non-callable
            placed_piece = move.promotion_piece_type(moving_piece.color)

        board.set_piece(move.to_position, placed_piece)
        # Apply any extra mutations associated with the move
        for mutation in move.extra_mutations:
            mutation_piece = board.get_piece(mutation.from_position)
            if mutation_piece is None:
                raise RuntimeError(f"Mutation source empty at {mutation.from_position}.")
            if mutation_piece != mutation.piece:
                raise RuntimeError(
                    f"Mutation piece mismatch at {mutation.from_position}: "
                    f"expected {mutation.piece}, found {mutation_piece}."
                )
            # Remove the piece from its original position
            board.set_piece(mutation.from_position, None)
            # Place the piece at its new position
            board.set_piece(mutation.to_position, mutation_piece)


    @staticmethod
    def revert_move_on_board(
        board: ChessBoard,
        rollback_snapshot: dict[Position, Piece | None],
    ):
        """
        Revert a move on the chessboard, restoring the positions of the moving piece and any captured pieces.
        Used for validating check states
        Args:
            board: The chess board on which the move is to be reverted.
            rollback_snapshot: Original contents of all impacted squares.

        Returns:
            None
        """
        for position, piece in rollback_snapshot.items():
            board.set_piece(position, piece)

    @staticmethod
    def _capture_rollback_snapshot(board: ChessBoard, move: Move) -> dict[Position, Piece | None]:
        """
        Capture the original contents of all squares impacted by a move
        Args:
            board: The chess board on which the move is to be applied.
            move: The move for which to capture the rollback snapshot.

        Returns:
            A dictionary mapping positions to their original pieces.
        """
        impacted_positions: set[Position] = {move.from_position, move.to_position}
        for mutation in move.extra_mutations:
            impacted_positions.add(mutation.from_position)
            impacted_positions.add(mutation.to_position)
        return {position: board.get_piece(position) for position in impacted_positions}