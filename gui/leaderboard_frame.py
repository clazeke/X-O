"""
leaderboard_frame.py
--------------------
LeaderboardFrame — all-time ranked player stats table.

Displays every player's combined record (wins / losses / draws / win-rate),
ranked by descending win rate.  Data is loaded fresh every time the frame
is shown via on_show().

Dependencies:
    customtkinter
    tkinter (for the embedded ttk.Treeview table)
    jm — must expose:
        jm.load_records()           → dict[str, record]
        jm.wipe_all_records()       → None
    Leaderboard (from leaderboard module) — must expose:
        Leaderboard(records)
        .generate_rankings()        → list[RankEntry]
            RankEntry has: .rank, .player_id, .wins, .losses, .draws,
                           .win_rate  (float, 0–100)
    App — must expose:
        app.show_main_menu()
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

import jm


class LeaderboardFrame(ctk.CTkFrame):
    """All-time stats leaderboard.

    Layout (top-to-bottom, centred):
        ┌──────────────────────────────────────────────┐
        │               Leaderboard                    │  ← heading
        │  ┌──────────────────────────────────────┐   │
        │  │ Rank │ Player ID │ W │ L │ D │ WR%  │   │  ← table
        │  └──────────────────────────────────────┘   │
        │   [  Wipe All Records  ]   [  Back  ]        │  ← buttons
        └──────────────────────────────────────────────┘

    on_show() must be called by App immediately after packing this frame.
    """

    _BTN_WIDTH  = 180
    _BTN_HEIGHT = 38
    _COL_WIDTHS = {
        "Rank":       50,
        "Player ID": 160,
        "Wins":       60,
        "Losses":     60,
        "Draws":      60,
        "Win Rate %": 90,
    }

    def __init__(self, parent, app) -> None:
        super().__init__(parent, fg_color="transparent")
        self._app = app
        self._build_ui()

    # ── UI construction ──────────────────────────────────────────────── #

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)

        row = 0

        # ── Top spacer ────────────────────────────────────────────────── #
        ctk.CTkFrame(self, height=30, fg_color="transparent").grid(
            row=row, column=0
        )
        row += 1

        # ── Heading ───────────────────────────────────────────────────── #
        ctk.CTkLabel(
            self,
            text="Leaderboard",
            font=ctk.CTkFont(family="Courier", size=28, weight="bold"),
        ).grid(row=row, column=0, pady=(0, 16))
        row += 1

        # ── Table (ttk.Treeview) ──────────────────────────────────────── #
        table_frame = ctk.CTkFrame(self, fg_color="transparent")
        table_frame.grid(row=row, column=0, padx=40, pady=(0, 16), sticky="ew")
        table_frame.columnconfigure(0, weight=1)

        columns = list(self._COL_WIDTHS.keys())
        self._tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=10,
        )
        for col in columns:
            self._tree.heading(col, text=col)
            self._tree.column(col, width=self._COL_WIDTHS[col], anchor="center")

        # Scrollbar.
        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self._tree.yview
        )
        self._tree.configure(yscrollcommand=scrollbar.set)
        self._tree.grid(row=0, column=0, sticky="ew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        row += 1

        # ── Button row ────────────────────────────────────────────────── #
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=row, column=0, pady=(0, 20))

        self._wipe_btn = ctk.CTkButton(
            btn_row,
            text="Wipe All Records",
            font=ctk.CTkFont(family="Courier", size=13, weight="bold"),
            width=self._BTN_WIDTH,
            height=self._BTN_HEIGHT,
            fg_color="#c0392b",
            hover_color="#922b21",
            command=self._on_wipe,
        )
        self._wipe_btn.grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            btn_row,
            text="Back",
            font=ctk.CTkFont(family="Courier", size=13, weight="bold"),
            width=100,
            height=self._BTN_HEIGHT,
            command=self._on_back,
        ).grid(row=0, column=1, padx=10)

        row += 1

        # ── Bottom spacer ─────────────────────────────────────────────── #
        ctk.CTkFrame(self, height=20, fg_color="transparent").grid(
            row=row, column=0
        )

    # ── Lifecycle ────────────────────────────────────────────────────── #

    def on_show(self) -> None:
        """Call immediately after the frame is packed/shown by App.

        Loads fresh data and re-renders the table every time.
        """
        self._reload()

    # ── Data loading & rendering ─────────────────────────────────────── #

    def _reload(self) -> None:
        """Load records, rank them, and repopulate the table."""
        from leaderboard import Leaderboard   # deferred — module may not exist at startup
        records  = jm.load_records()
        lb       = Leaderboard(records)
        rankings = lb.generate_rankings()

        self._render_table(rankings)
        self._update_wipe_button(rankings)

    def _render_table(self, rankings: list) -> None:
        """Clear the treeview and insert fresh rows."""
        # Remove all existing rows.
        for item in self._tree.get_children():
            self._tree.delete(item)

        for entry in rankings:
            win_rate = f"{entry.win_rate:.1f}"
            self._tree.insert(
                "",
                "end",
                values=(
                    entry.rank,
                    entry.player_id,
                    entry.wins,
                    entry.losses,
                    entry.draws,
                    win_rate,
                ),
            )

    def _update_wipe_button(self, rankings: list) -> None:
        """Disable Wipe when table is empty; enable when it has rows."""
        state = "normal" if rankings else "disabled"
        self._wipe_btn.configure(state=state)

    # ── Button handlers ───────────────────────────────────────────────── #

    def _on_wipe(self) -> None:
        """Show a confirmation dialog; wipe if the user confirms."""
        dialog = ctk.CTkInputDialog(
            text=(
                "Are you sure you want to wipe all records?\n"
                "This cannot be undone."
            ),
            title="Confirm Wipe",
        )
        # CTkInputDialog doesn't support custom buttons natively, so we use
        # a custom CTkToplevel confirmation window instead.
        dialog.destroy()   # discard the input dialog immediately
        self._show_confirm_dialog()

    def _show_confirm_dialog(self) -> None:
        """Open a bespoke CTkToplevel with Wipe / Cancel buttons."""
        dlg = ctk.CTkToplevel(self)
        dlg.title("Confirm Wipe")
        dlg.resizable(False, False)
        dlg.attributes("-topmost", True)
        dlg.protocol("WM_DELETE_WINDOW", dlg.destroy)

        container = ctk.CTkFrame(dlg, fg_color="transparent")
        container.pack(padx=30, pady=24)

        ctk.CTkLabel(
            container,
            text=(
                "Are you sure you want to wipe all records?\n"
                "This cannot be undone."
            ),
            font=ctk.CTkFont(family="Courier", size=13),
            wraplength=300,
            justify="center",
        ).pack(pady=(0, 20))

        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack()

        def _confirm():
            dlg.destroy()
            jm.wipe_all_records()
            self._reload()

        ctk.CTkButton(
            btn_row,
            text="Wipe",
            font=ctk.CTkFont(family="Courier", size=13, weight="bold"),
            width=100,
            height=self._BTN_HEIGHT,
            fg_color="#c0392b",
            hover_color="#922b21",
            command=_confirm,
        ).grid(row=0, column=0, padx=8)

        ctk.CTkButton(
            btn_row,
            text="Cancel",
            font=ctk.CTkFont(family="Courier", size=13, weight="bold"),
            width=100,
            height=self._BTN_HEIGHT,
            command=dlg.destroy,
        ).grid(row=0, column=1, padx=8)

        # Centre over parent.
        dlg.update_idletasks()
        px = self.winfo_rootx() + self.winfo_width()  // 2
        py = self.winfo_rooty() + self.winfo_height() // 2
        w  = dlg.winfo_width()
        h  = dlg.winfo_height()
        dlg.geometry(f"+{px - w // 2}+{py - h // 2}")

        self._confirm_dialog = dlg   # store reference for testing

    def _on_back(self) -> None:
        self._app.show_main_menu()