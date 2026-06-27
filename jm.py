"""
jm.py
-----
Thin shim that gives all GUI frames a single stable import name.

All frames call jm.load_records(), jm.create_player() etc. rather than
instantiating JSONManager directly.  App constructs the JSONManager once
and calls jm.init(manager, ai) so the shim functions delegate to it.

Also exposes build_players() and build_game() so App.show_game() can
create the domain objects without importing them separately.
"""

from __future__ import annotations
import os
import sys

# Ensure the directory containing jm.py is on sys.path so that
# json_manager, player, game and minimax_ai are always importable
# regardless of the working directory Python was launched from.
#_HERE = os.path.dirname(os.path.abspath(__file__))
#if _HERE not in sys.path:
#    sys.path.insert(0, _HERE)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "core"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "storage"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ai"))

from json_manager import JSONManager
from player       import Player
from game         import Game
from minimax_ai   import MinimaxAI

# ---------------------------------------------------------------------------
# Module-level singletons — populated by init()
# ---------------------------------------------------------------------------
_jm: JSONManager | None = None
_ai: MinimaxAI   | None = None


def init(manager: JSONManager, ai: MinimaxAI) -> None:
    """Called once by App.__init__() to wire up the singletons."""
    global _jm, _ai
    _jm = manager
    _ai = ai


def _require() -> JSONManager:
    if _jm is None:
        raise RuntimeError("jm.init() has not been called yet.")
    return _jm


# ---------------------------------------------------------------------------
# JSONManager pass-throughs
# ---------------------------------------------------------------------------

def load_records() -> dict:
    return _require().load_records()

def create_player(player_id: str) -> None:
    _require().create_player(player_id)

def delete_player(player_id: str) -> None:
    _require().delete_player(player_id)

def update_record(player_id: str, symbol: str, result: str) -> None:
    _require().update_record(player_id, symbol, result)

def wipe_all_records() -> None:
    _require().wipe_all_records()


# ---------------------------------------------------------------------------
# Game-object factory — used by App.show_game()
# ---------------------------------------------------------------------------

def build_players(
    p1_id: str,
    p2_id: str,
    p1_symbol: str,
    p2_symbol: str,
    mode: str,
) -> tuple[Player, Player]:
    """Construct and return (player1, player2) with symbols assigned."""
    is_computer_id = "Nash's heir"
    p1 = Player(player_id=p1_id, is_computer=(p1_id == is_computer_id))
    p1.set_symbol(p1_symbol)
    p2 = Player(player_id=p2_id, is_computer=(p2_id == is_computer_id))
    p2.set_symbol(p2_symbol)
    return p1, p2


def build_game(p1: Player, p2: Player) -> Game:
    """Construct and return a Game for the two players."""
    return Game(p1, p2)


# ---------------------------------------------------------------------------
# AI — used by GridTopLevel.do_ai_turn()
# ---------------------------------------------------------------------------

def get_ai_move(board, ai_symbol: str) -> tuple[int, int] | None:
    """Return the best (row, col) for the AI, or None if the board is full."""
    global _ai
    if _ai is None:
        _ai = MinimaxAI()
    empty = board.get_empty_cells()
    if not empty:
        return None
    return _ai.get_best_move(board, ai_symbol)