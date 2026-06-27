"""
select_id_frame.py
------------------
SelectIDFrame — prompts one player to pick an existing ID or create a new one.

Used twice in PvP (once per player) and once in PvC (human player only).
Each use is a **separate instance**; the frame itself is stateless between
instantiations.

Dependencies:
    customtkinter
    tkinter
    jm  (game-logic module — jm.load_records(), jm.create_player(),
                              jm.delete_player())
"""

from __future__ import annotations

import tkinter as tk
from typing import Callable

import customtkinter as ctk

import jm


class SelectIDFrame(ctk.CTkFrame):
    """Player-ID selection screen.

    Layout (top-to-bottom, centred):
        ┌──────────────────────────────────┐
        │           Player 1               │  ← heading (label arg)
        │  ┌──────────────────────────┐    │
        │  │  existing-id-1           │    │  ← Listbox
        │  │  existing-id-2           │    │
        │  └──────────────────────────┘    │
        │  [ entry field ] [ Create New ]  │
        │  [ Delete Player ]               │
        │  [       Confirm              ]  │
        └──────────────────────────────────┘

    Constructor args:
        parent      — the CTk container this frame lives inside
        app         — the App controller
        label       — heading text, e.g. "Player 1" or "Player 2"
        on_confirm  — callback fired with the chosen ID (str) when the
                      user clicks Confirm

    Behaviour:
        • Populates the listbox from jm.load_records(), excluding "Nash's heir".
        • "Create New" calls jm.create_player(name), appends to listbox,
          selects it automatically.
        • "Delete Player" is enabled only when one item is selected.
          Opens a confirmation dialog; if confirmed calls jm.delete_player()
          and removes the entry from the listbox.
        • "Confirm" is disabled until exactly one item is selected.
    """

    _BTN_WIDTH    = 220
    _BTN_HEIGHT   = 38
    _EXCLUDED_IDS = {"Nash's heir"}

    def __init__(
        self,
        parent,
        app,
        label: str,
        on_confirm: Callable[[str], None],
    ) -> None:
        super().__init__(parent, fg_color="transparent")
        self._app        = app
        self._label      = label
        self._on_confirm = on_confirm

        self._build_ui()
        self._populate_listbox()

    # ── UI construction ──────────────────────────────────────────────── #

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        row = 0

        # ── Top spacer ────────────────────────────────────────────────── #
        ctk.CTkFrame(self, height=50, fg_color="transparent").grid(
            row=row, column=0
        )
        row += 1

        # ── Heading ───────────────────────────────────────────────────── #
        ctk.CTkLabel(
            self,
            text=self._label,
            font=ctk.CTkFont(family="Courier", size=28, weight="bold"),
        ).grid(row=row, column=0, pady=(0, 20))
        row += 1

        # ── Listbox ───────────────────────────────────────────────────── #
        list_container = ctk.CTkFrame(self, corner_radius=8)
        list_container.grid(row=row, column=0, padx=40, pady=(0, 12), sticky="ew")
        list_container.columnconfigure(0, weight=1)

        mode_idx   = 0 if ctk.get_appearance_mode() == "Light" else 1
        bg_colour  = ctk.ThemeManager.theme["CTkFrame"]["fg_color"][mode_idx]
        fg_colour  = ctk.ThemeManager.theme["CTkLabel"]["text_color"][mode_idx]
        sel_colour = ctk.ThemeManager.theme["CTkButton"]["fg_color"][mode_idx]

        self._listbox = tk.Listbox(
            list_container,
            selectmode=tk.SINGLE,
            height=6,
            font=("Courier", 13),
            bg=bg_colour,
            fg=fg_colour,
            selectbackground=sel_colour,
            selectforeground="#ffffff",
            relief="flat",
            highlightthickness=0,
            activestyle="none",
            bd=0,
        )
        self._listbox.grid(row=0, column=0, sticky="ew", padx=4, pady=4)
        self._listbox.bind("<<ListboxSelect>>", self._on_selection_changed)
        row += 1

        # ── Create-new row ────────────────────────────────────────────── #
        create_row = ctk.CTkFrame(self, fg_color="transparent")
        create_row.grid(row=row, column=0, padx=40, pady=(0, 8), sticky="ew")
        create_row.columnconfigure(0, weight=1)

        self._entry = ctk.CTkEntry(
            create_row,
            placeholder_text="New player name…",
            font=ctk.CTkFont(family="Courier", size=13),
            height=self._BTN_HEIGHT,
        )
        self._entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkButton(
            create_row,
            text="Create New",
            font=ctk.CTkFont(family="Courier", size=13, weight="bold"),
            width=110,
            height=self._BTN_HEIGHT,
            command=self._on_create_new,
        ).grid(row=0, column=1)
        row += 1

        # ── Delete Player button ──────────────────────────────────────── #
        self._delete_btn = ctk.CTkButton(
            self,
            text="Delete Player",
            font=ctk.CTkFont(family="Courier", size=13, weight="bold"),
            width=self._BTN_WIDTH,
            height=self._BTN_HEIGHT,
            fg_color="#c0392b",
            hover_color="#922b21",
            state="disabled",
            command=self._on_delete_clicked,
        )
        self._delete_btn.grid(row=row, column=0, pady=(0, 8))
        row += 1

        # ── Confirm button ────────────────────────────────────────────── #
        self._confirm_btn = ctk.CTkButton(
            self,
            text="Confirm",
            font=ctk.CTkFont(family="Courier", size=14, weight="bold"),
            width=self._BTN_WIDTH,
            height=self._BTN_HEIGHT + 4,
            state="disabled",
            command=self._on_confirm_clicked,
        )
        self._confirm_btn.grid(row=row, column=0, pady=(0, 4))
        row += 1

        # ── Bottom spacer ─────────────────────────────────────────────── #
        ctk.CTkFrame(self, height=50, fg_color="transparent").grid(
            row=row, column=0
        )

    # ── Data loading ─────────────────────────────────────────────────── #

    def _populate_listbox(self) -> None:
        """Read records.json and fill the listbox, honouring the exclusion list."""
        self._listbox.delete(0, "end")
        records = jm.load_records()
        ids = records.keys() if isinstance(records, dict) else records
        for player_id in ids:
            if player_id not in self._EXCLUDED_IDS:
                self._listbox.insert("end", player_id)

    # ── Event handlers ───────────────────────────────────────────────── #

    def _on_selection_changed(self, _event=None) -> None:
        """Enable/disable Confirm and Delete based on current selection."""
        has_selection = bool(self._listbox.curselection())
        state = "normal" if has_selection else "disabled"
        self._confirm_btn.configure(state=state)
        self._delete_btn.configure(state=state)

    def _on_create_new(self) -> None:
        """Validate entry, write to file, append to listbox, select it."""
        name = self._entry.get().strip()
        if not name:
            return
        if name in self._EXCLUDED_IDS:
            return

        jm.create_player(name)

        self._listbox.insert("end", name)
        new_index = self._listbox.size() - 1
        self._listbox.selection_clear(0, "end")
        self._listbox.selection_set(new_index)
        self._listbox.see(new_index)

        self._entry.delete(0, "end")
        self._on_selection_changed()

    def _on_delete_clicked(self) -> None:
        """Open confirmation dialog before deleting the selected player."""
        selection = self._listbox.curselection()
        if not selection:
            return
        selected_id: str = self._listbox.get(selection[0])
        self._show_delete_confirm_dialog(selected_id)

    def _show_delete_confirm_dialog(self, selected_id: str) -> None:
        """Open a CTkToplevel asking the user to confirm deletion."""
        dlg = ctk.CTkToplevel(self)
        dlg.title("Confirm Delete")
        dlg.resizable(False, False)
        dlg.attributes("-topmost", True)
        dlg.protocol("WM_DELETE_WINDOW", dlg.destroy)

        container = ctk.CTkFrame(dlg, fg_color="transparent")
        container.pack(padx=30, pady=24)

        ctk.CTkLabel(
            container,
            text=(
                f"Are you sure you want to delete {selected_id}?\n"
                "This cannot be undone."
            ),
            font=ctk.CTkFont(family="Courier", size=13),
            wraplength=300,
            justify="center",
        ).pack(pady=(0, 20))

        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack()

        def _confirm_delete():
            dlg.destroy()
            self._do_delete(selected_id)

        ctk.CTkButton(
            btn_row,
            text="Delete",
            font=ctk.CTkFont(family="Courier", size=13, weight="bold"),
            width=100,
            height=self._BTN_HEIGHT,
            fg_color="#c0392b",
            hover_color="#922b21",
            command=_confirm_delete,
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

        self._delete_dialog = dlg   # stored for test access

    def _do_delete(self, player_id: str) -> None:
        """Remove a player from file and from the listbox."""
        jm.delete_player(player_id)

        # Find and remove the entry from the listbox.
        for i in range(self._listbox.size()):
            if self._listbox.get(i) == player_id:
                self._listbox.delete(i)
                break

        # Clear button states — no selection remains.
        self._listbox.selection_clear(0, "end")
        self._on_selection_changed()

    def _on_confirm_clicked(self) -> None:
        """Fire the on_confirm callback with the selected player ID."""
        selection = self._listbox.curselection()
        if not selection:
            return
        chosen_id: str = self._listbox.get(selection[0])
        self._on_confirm(chosen_id)