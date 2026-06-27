import json
import os


class JSONManager:
    """Single point of contact for all JSON storage operations.

    Never read or write the records file anywhere else in the project —
    route every storage operation through this class.
    """

    VALID_SYMBOLS = {"X", "O"}
    VALID_RESULTS = {"win", "loss", "draw"}

    _EMPTY_SYMBOL_RECORD = {"Wins": 0, "Losses": 0, "Draws": 0}

    def __init__(self, filepath: str):
        """
        Args:
            filepath: Path to the JSON file (created automatically if absent).
        """
        self.filepath = filepath
        if not os.path.exists(filepath):
            self._initialize_file()

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def load_records(self) -> dict:
        """Return the full records dictionary from disk."""
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_records(self, data: dict) -> None:
        """Overwrite the records file with *data*."""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def create_player(self, player_id: str) -> None:
        """Add a new player entry with zeroed stats for both symbols.

        Does nothing if the player already exists (no overwrite).

        Raises:
            ValueError: if player_id is an empty string.
        """
        if not player_id or not player_id.strip():
            raise ValueError("player_id must not be empty.")

        data = self.load_records()
        if player_id not in data:
            data[player_id] = {
                "X": dict(self._EMPTY_SYMBOL_RECORD),
                "O": dict(self._EMPTY_SYMBOL_RECORD),
            }
            self.save_records(data)

    def update_record(self, player_id: str, symbol: str, result: str) -> None:
        """Increment the appropriate stat for *player_id*.

        Args:
            player_id: Must already exist in the records.
            symbol:    "X" or "O".
            result:    "win", "loss", or "draw".

        Raises:
            KeyError:   if player_id is not found.
            ValueError: if symbol or result is invalid.
        """
        if symbol not in self.VALID_SYMBOLS:
            raise ValueError(f"Invalid symbol '{symbol}'. Must be 'X' or 'O'.")
        if result not in self.VALID_RESULTS:
            raise ValueError(
                f"Invalid result '{result}'. Must be 'win', 'loss', or 'draw'."
            )

        data = self.load_records()

        if player_id not in data:
            raise KeyError(
                f"Player '{player_id}' not found. Call create_player() first."
            )

        stat_key = result.capitalize()   # "win" → "Wins", etc.
        # result.capitalize() gives "Win"/"Loss"/"Draw" — append 's' for key
        stat_key = {"win": "Wins", "loss": "Losses", "draw": "Draws"}[result]

        data[player_id][symbol][stat_key] += 1
        self.save_records(data)

    def delete_player(self, player_id: str) -> None:
        """Permanently remove a player and all their records.

        Raises:
            KeyError: if player_id does not exist.
        """
        data = self.load_records()
        if player_id not in data:
            raise KeyError(f"Player '{player_id}' not found.")
        del data[player_id]
        self.save_records(data)

    def wipe_all_records(self) -> None:
        """Delete every player and reset the file to an empty state.

        This is the nuclear option — used by the leaderboard reset button.
        """
        self.save_records({})

    # ------------------------------------------------------------------ #
    # Private                                                              #
    # ------------------------------------------------------------------ #

    def _initialize_file(self) -> None:
        """Write an empty records object to disk."""
        os.makedirs(os.path.dirname(self.filepath) or ".", exist_ok=True)
        self.save_records({})