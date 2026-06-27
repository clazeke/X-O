class Player:
    """Represents a human or AI participant.

    Symbol is intentionally separate from construction — in the GUI flow
    the player is created first, then a button click assigns the symbol.
    """

    VALID_SYMBOLS = {"X", "O"}

    def __init__(self, player_id: str, is_computer: bool = False):
        self.player_id: str = player_id
        self.is_computer: bool = is_computer
        self.symbol: str | None = None   # assigned later via set_symbol()

    def set_symbol(self, symbol: str) -> None:
        """Assign a symbol to this player.

        Raises:
            ValueError – if symbol is not "X" or "O".
        """
        if symbol not in self.VALID_SYMBOLS:
            raise ValueError(
                f"Invalid symbol '{symbol}'. Must be one of {self.VALID_SYMBOLS}."
            )
        self.symbol = symbol

    def has_symbol(self) -> bool:
        """Return True if a symbol has been assigned."""
        return self.symbol is not None

    def __repr__(self) -> str:
        kind = "Computer" if self.is_computer else "Human"
        sym = self.symbol if self.symbol else "unassigned"
        return f"Player(id={self.player_id!r}, symbol={sym!r}, type={kind})"