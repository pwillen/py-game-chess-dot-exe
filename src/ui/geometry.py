from dataclasses import dataclass

import pygame

from chess.board import Position


@dataclass(frozen=True)
class PixelPoint:
    """
    Represents a point in pixel coordinates on the screen.
    Attributes:
        x (int): The x-coordinate in pixels.
        y (int): The y-coordinate in pixels.
    """
    x: int
    y: int


class BoardGeometry:
    """
    Represents the geometry of the chessboard on the screen.
    """
    def __init__(self, left: int, top: int, square_size: int, board_size: int):
        """
        Initializes the BoardGeometry with the specified parameters.
        Args:
            left: The x-coordinate of the top-left corner of the board.
            top: The y-coordinate of the top-left corner of the board.
            square_size: The size of each square on the board in pixels.
            board_size: The total size of the board in pixels.
        """
        self.left = left
        self.top = top
        self.square_size = square_size
        self.board_size = board_size

    def square_center(self, position: Position, local: bool = False) -> PixelPoint:
        """
        Calculates the center pixel coordinates of a given square on the chessboard.
        Args:
            position: The position of the square on the chessboard.
            local: If True, returns coordinates relative to the board's top-left corner; otherwise, returns absolute screen coordinates.

        Returns:
            A PixelPoint representing the center of the square in pixels.
        """
        x = (position.col * self.square_size) + (self.square_size // 2)
        y = (position.row * self.square_size) + (self.square_size // 2)
        if local:
            return PixelPoint(x, y)
        return PixelPoint(self.left + x, self.top + y)

    def square_rect(self, position: Position, local: bool = False) -> pygame.Rect:
        """
        Calculates the rectangle representing a given square on the chessboard.
        Args:
            position: The position of the square on the chessboard.
            local: If True, returns coordinates relative to the board's top-left corner; otherwise, returns absolute screen coordinates.

        Returns:
            A pygame.Rect representing the square's position and size.
        """
        x = position.col * self.square_size
        y = position.row * self.square_size
        if not local:
            x += self.left
            y += self.top
        return pygame.Rect(x, y, self.square_size, self.square_size)

    def mouse_to_position(self, mouse_pos: tuple[int, int]) -> Position | None:
        """
        Converts mouse pixel coordinates to a chessboard position.
        Args:
            mouse_pos: A tuple (x, y) representing the mouse position in pixels.

        Returns:
            A Position object representing the corresponding square on the chessboard, or None if the mouse is outside the board.
        """
        x, y = mouse_pos
        if x < self.left or y < self.top:
            return None
        board_x = x - self.left
        board_y = y - self.top
        if board_x >= self.board_size or board_y >= self.board_size:
            return None
        col = board_x // self.square_size
        row = board_y // self.square_size
        return Position.from_row_col(row, col)