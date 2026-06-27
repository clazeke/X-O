import numpy as np
from referee import Referee
from board import Board


class MinimaxAI:
    """Determines the optimal move using Minimax with alpha-beta pruning.

    Responsibilities:
        - analyse the board state
        - return the best (row, col) move

    Does NOT:
        - update the GUI
        - write JSON
        - manage turns
        - re-implement winner checking or empty-cell logic (delegates to
          Referee and Board respectively)

    Usage:
        ai = MinimaxAI()
        row, col = ai.get_best_move(board, ai_symbol="O")
    """

    def __init__(self):
        self._referee = Referee()

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def get_best_move(self, board: Board, ai_symbol: str) -> tuple[int, int]:
        """Return the optimal (row, col) for the AI to play.

        Args:
            board:     The current Board object.
            ai_symbol: "X" or "O" — the symbol the AI is playing as.

        Returns:
            (row, col) of the best available move.

        Raises:
            ValueError: if the board is full (no move available).
        """
        empty_cells = board.get_empty_cells()
        if not empty_cells:
            raise ValueError("No moves available — board is full.")

        opponent = "O" if ai_symbol == "X" else "X"
        best_score = float("-inf")
        best_move = empty_cells[0]

        for row, col in empty_cells:
            board.grid[row, col] = ai_symbol
            score = self._minimax(
                board, ai_symbol, opponent,
                is_maximising=False,
                alpha=float("-inf"),
                beta=float("inf"),
            )
            board.grid[row, col] = ""

            if score > best_score:
                best_score = score
                best_move = (row, col)

        return best_move

    # ------------------------------------------------------------------ #
    # Private                                                              #
    # ------------------------------------------------------------------ #

    def _minimax(
        self,
        board: Board,
        ai_symbol: str,
        opponent: str,
        is_maximising: bool,
        alpha: float,
        beta: float,
    ) -> int:
        """Recursively score every possible game continuation with pruning.

        Returns:
             1  — AI wins
            -1  — opponent wins
             0  — draw
        """
        winner = self._referee.check_winner(board.grid)
        if winner == ai_symbol:
            return 1
        if winner == opponent:
            return -1
        empty = board.get_empty_cells()
        if not empty:
            return 0

        if is_maximising:
            best = float("-inf")
            for row, col in empty:
                board.grid[row, col] = ai_symbol
                score = self._minimax(board, ai_symbol, opponent, False, alpha, beta)
                board.grid[row, col] = ""
                best = max(best, score)
                alpha = max(alpha, best)
                if beta <= alpha:
                    break
            return best
        else:
            best = float("inf")
            for row, col in empty:
                board.grid[row, col] = opponent
                score = self._minimax(board, ai_symbol, opponent, True, alpha, beta)
                board.grid[row, col] = ""
                best = min(best, score)
                beta = min(beta, best)
                if beta <= alpha:
                    break
            return best