"""
main.py — Entry point for the Tic-Tac-Toe GUI application.
"""
import os
import sys

# Add the project directory to sys.path so all modules are importable
# regardless of how or from where Python was launched.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import traceback
import customtkinter as ctk
from app import App

if __name__ == "__main__":
    try:
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        app = App()
        app.root.mainloop()
    except Exception:
        traceback.print_exc()
        input("Press Enter to close...")