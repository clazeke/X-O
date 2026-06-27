"""
exit_frame.py
-------------
ExitFrame — farewell screen shown when the user selects Exit.

Displays a thank-you message and automatically destroys the root
window after a 2-second delay. No user interaction required.

Dependencies: customtkinter only.
"""

import customtkinter as ctk


class ExitFrame(ctk.CTkFrame):
    """Farewell screen.

    Layout (centred):
        ┌─────────────────────────────┐
        │                             │
        │     Thank you for playing   │  ← main label
        │        See you soon!        │  ← sub label
        │                             │
        └─────────────────────────────┘

    Constructor args:
        parent  — the CTk container this frame lives inside (root window)
        app     — the App controller; used to call app.root.destroy()

    Behaviour:
        - on_show() must be called by App immediately after packing this
          frame. It schedules root.destroy() 2000 ms later.
        - The after() handle is stored so it can be cancelled if needed
          (e.g. during testing).
    """

    _DELAY_MS = 2000

    def __init__(self, parent, app) -> None:
        super().__init__(parent, fg_color="transparent")
        self._app          = app
        self._after_handle = None
        self._build_ui()

    # ── UI construction ──────────────────────────────────────────────── #

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)

        # ── Top spacer ────────────────────────────────────────────────── #
        ctk.CTkFrame(self, height=120, fg_color="transparent").grid(row=0, column=0)

        # ── Main label ────────────────────────────────────────────────── #
        ctk.CTkLabel(
            self,
            text="Thank you for playing",
            font=ctk.CTkFont(family="Courier", size=26, weight="bold"),
        ).grid(row=1, column=0, pady=(0, 12))

        # ── Sub label ─────────────────────────────────────────────────── #
        ctk.CTkLabel(
            self,
            text="See you soon!",
            font=ctk.CTkFont(family="Courier", size=13),
        ).grid(row=2, column=0)

    # ── Lifecycle ────────────────────────────────────────────────────── #

    def on_show(self) -> None:
        """Call this immediately after the frame is packed/shown.

        Schedules root.destroy() after _DELAY_MS milliseconds.
        Cancels any previously scheduled destroy (safety guard for
        repeated calls).
        """
        if self._after_handle is not None:
            self.after_cancel(self._after_handle)

        self._after_handle = self.after(
            self._DELAY_MS,
            self._app.root.destroy,
        )

    def cancel_exit(self) -> None:
        """Cancel the pending destroy — useful in tests."""
        if self._after_handle is not None:
            self.after_cancel(self._after_handle)
            self._after_handle = None