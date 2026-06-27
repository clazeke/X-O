import numpy as np


class Referee:
    """Stateless game-state evaluator for Tic-Tac-Toe.

    All methods are pure functions of the board — no GUI logic, no state.
    """

    # Eight winning lines: 3 rows, 3 cols, 2 diagonals
    _LINES: list[list[tuple[int, int]]] = [
        # rows
        [(0, 0), (0, 1), (0, 2)],
        [(1, 0), (1, 1), (1, 2)],
        [(2, 0), (2, 1), (2, 2)],
        # cols
        [(0, 0), (1, 0), (2, 0)],
        [(0, 1), (1, 1), (2, 1)],
        [(0, 2), (1, 2), (2, 2)],
        # diagonals
        [(0, 0), (1, 1), (2, 2)],
        [(0, 2), (1, 1), (2, 0)],
    ]

    def check_winner(self, board: np.ndarray) -> str | None:
        """Return "X" or "O" if that symbol occupies a full line, else None."""
        for line in self._LINES:
            cells = [board[r, c] for r, c in line]
            if cells[0] != "" and cells[0] == cells[1] == cells[2]:
                return cells[0]
        return None

    def is_draw(self, board: np.ndarray) -> bool:
        """Return True when the board is full and no winner exists."""
        board_full = bool(np.all(board != ""))
        return board_full and self.check_winner(board) is None