import random

from board import Board
from player import Player
from referee import Referee


class Game:
    """Director class — controls turn order, gameplay loop, and match lifecycle.

    The GUI layer (when added) should call:
        start_new_game()  → on game start / rematch
        make_move(r, c)   → on cell click
        check_game_state()→ after every move to decide what to show next
    """

    def __init__(self, player_1: Player, player_2: Player):
        self.board: Board = Board()
        self.player_1: Player = player_1
        self.player_2: Player = player_2
        self.current_player: Player = player_1   # overwritten by start_new_game
        self.referee: Referee = Referee()
        self._game_over: bool = False

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def start_new_game(self) -> None:
        """Reset the board and randomly pick who moves first."""
        self.board.reset_board()
        self.current_player = random.choice([self.player_1, self.player_2])
        self._game_over = False

    def switch_turns(self) -> None:
        """Hand control to the other player."""
        if self.current_player is self.player_1:
            self.current_player = self.player_2
        else:
            self.current_player = self.player_1

    def make_move(self, row: int, col: int) -> bool:
        """Attempt to place the current player's symbol at (row, col).

        Returns:
            True  – move accepted; game state updated.
            False – invalid move (cell occupied, out of bounds, or game over).
        """
        if self._game_over:
            return False

        placed = self.board.place_symbol(row, col, self.current_player.symbol)
        if not placed:
            return False

        if self.check_game_state() == "continue":
            self.switch_turns()

        return True

    def check_game_state(self) -> str:
        """Inspect the board and return the current state.

        Returns:
            "win"      – current_player has a winning line.
            "draw"     – board full, no winner.
            "continue" – game still in progress.
        """
        if self.referee.check_winner(self.board.grid) is not None:
            self._game_over = True
            return "win"
        if self.referee.is_draw(self.board.grid):
            self._game_over = True
            return "draw"
        return "continue"

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    @property
    def game_over(self) -> bool:
        return self._game_over