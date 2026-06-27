from dataclasses import dataclass


@dataclass
class LeaderboardEntry:
    """Represents one row of leaderboard data."""
    rank: int
    player_id: str
    wins: int
    losses: int
    draws: int
    win_rate: float

    def __repr__(self) -> str:
        return (
            f"#{self.rank} {self.player_id} | "
            f"W:{self.wins} L:{self.losses} D:{self.draws} | "
            f"{self.win_rate:.1f}%"
        )


class Leaderboard:
    """Analyzes player records and produces ranked standings.

    Does not own or touch the file — pass in the dict from JSONManager.

    Example:
        records = json_manager.load_records()
        lb = Leaderboard(records)
        rankings = lb.generate_rankings()
    """

    def __init__(self, records: dict):
        self.records = records

    # ------------------------------------------------------------------ #
    # Per-player stats                                                     #
    # ------------------------------------------------------------------ #

    def get_total_wins(self, player_id: str) -> int:
        """X Wins + O Wins."""
        self._require_player(player_id)
        p = self.records[player_id]
        return p["X"]["Wins"] + p["O"]["Wins"]

    def get_total_losses(self, player_id: str) -> int:
        """X Losses + O Losses."""
        self._require_player(player_id)
        p = self.records[player_id]
        return p["X"]["Losses"] + p["O"]["Losses"]

    def get_total_draws(self, player_id: str) -> int:
        """X Draws + O Draws."""
        self._require_player(player_id)
        p = self.records[player_id]
        return p["X"]["Draws"] + p["O"]["Draws"]

    def get_total_games(self, player_id: str) -> int:
        """Wins + Losses + Draws."""
        return (
            self.get_total_wins(player_id)
            + self.get_total_losses(player_id)
            + self.get_total_draws(player_id)
        )

    def calculate_win_rate(self, player_id: str) -> float:
        """Wins / Total Games * 100, rounded to 1 decimal place.

        Returns 0.0 if the player has played no games yet.
        """
        self._require_player(player_id)
        total = self.get_total_games(player_id)
        if total == 0:
            return 0.0
        return round(self.get_total_wins(player_id) / total * 100, 1)

    # ------------------------------------------------------------------ #
    # Rankings                                                             #
    # ------------------------------------------------------------------ #

    def generate_rankings(self) -> list[LeaderboardEntry]:
        """Return all players sorted by win rate descending, then by total
        wins descending as a tiebreaker.

        Returns:
            list[LeaderboardEntry] — rank 1 is the best player.
        """
        unsorted = [
            (pid, self.calculate_win_rate(pid), self.get_total_wins(pid))
            for pid in self.records
        ]

        # primary sort: win_rate desc; tiebreaker: total wins desc
        sorted_players = sorted(unsorted, key=lambda x: (x[1], x[2]), reverse=True)

        return [
            LeaderboardEntry(
                rank=i + 1,
                player_id=pid,
                wins=self.get_total_wins(pid),
                losses=self.get_total_losses(pid),
                draws=self.get_total_draws(pid),
                win_rate=win_rate,
            )
            for i, (pid, win_rate, _) in enumerate(sorted_players)
        ]

    # ------------------------------------------------------------------ #
    # Private                                                              #
    # ------------------------------------------------------------------ #

    def _require_player(self, player_id: str) -> None:
        if player_id not in self.records:
            raise KeyError(f"Player '{player_id}' not found in records.")