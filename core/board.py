import numpy as np


class Board:
    """Manages a 3x3 Tic-Tac-Toe board using a numpy array."""

    def __init__(self):
        self.grid: np.ndarray = np.full((3, 3), "", dtype="U1")

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def place_symbol(self, row: int, col: int, symbol: str) -> bool:
        """Place *symbol* at (row, col).

        Returns:
            True  – cell was empty and the symbol was placed.
            False – cell is already occupied; board unchanged.

        Raises:
            ValueError – if (row, col) is outside [0, 2] x [0, 2].
        """
        self._validate_position(row, col)
        if self.grid[row, col] != "":
            return False
        self.grid[row, col] = symbol
        return True

    def is_full(self) -> bool:
        """Return True when every cell contains a symbol."""
        return bool(np.all(self.grid != ""))

    def reset_board(self) -> None:
        """Clear every cell, returning the board to its initial state."""
        self.grid[:] = ""

    def get_empty_cells(self) -> list[tuple[int, int]]:
        """Return a list of (row, col) tuples for every unoccupied cell."""
        rows, cols = np.where(self.grid == "")
        return list(zip(rows.tolist(), cols.tolist()))

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _validate_position(self, row: int, col: int) -> None:
        if not (0 <= row <= 2 and 0 <= col <= 2):
            raise ValueError(
                f"Position ({row}, {col}) is out of bounds. "
                "Row and column must each be in range [0, 2]."
            )

    def __repr__(self) -> str:  # handy for debugging
        display = np.where(self.grid == "", ".", self.grid)
        rows = [" | ".join(row) for row in display]
        return "\n---------\n".join(rows)