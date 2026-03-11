# ══════════════════════════════════════════════════════════════════════════════
#  pages/activity.py — Activity Log page
# ══════════════════════════════════════════════════════════════════════════════

import customtkinter as ctk
from theme import (
    BG_CARD, BG_INPUT, ACCENT, ACCENT2, DANGER,
    TEXT_MAIN, TEXT_DIM,
    FONT_TITLE, FONT_BODY, FONT_SMALL, FONT_BOLD
)
from database import get_recent_activity


class ActivityPage(ctk.CTkFrame):
    def __init__(self, parent, navigate):
        super().__init__(parent, fg_color="transparent")
        self.navigate = navigate
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build()

    def _build(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        ctk.CTkLabel(hdr, text="Activity Log",
                     font=FONT_TITLE(), text_color=TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(hdr, text="A full history of all changes made to the inventory.",
                     font=FONT_BODY(), text_color=TEXT_DIM).pack(anchor="w")

        # Scrollable log list
        scroll = ctk.CTkScrollableFrame(self, fg_color=BG_CARD, corner_radius=14)
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        logs = get_recent_activity(100)
        if not logs:
            ctk.CTkLabel(scroll, text="No activity recorded yet.",
                         font=FONT_BODY(), text_color=TEXT_DIM).pack(pady=40)
            return

        for log in logs:
            self._log_row(scroll, log)

    def _log_row(self, parent, log):
        ACTION_COLORS = {"ADD": ACCENT2, "EDIT": ACCENT, "DELETE": DANGER}
        ACTION_ICONS  = {"ADD": "＋",   "EDIT": "✎",    "DELETE": "✕"}

        color = ACTION_COLORS.get(log["action"], TEXT_DIM)
        icon  = ACTION_ICONS.get(log["action"], "•")

        row = ctk.CTkFrame(parent, fg_color=BG_INPUT, corner_radius=8)
        row.pack(fill="x", padx=12, pady=3)
        row.grid_columnconfigure(1, weight=1)

        # Colored action badge
        badge = ctk.CTkFrame(row, fg_color=color, corner_radius=6, width=32, height=32)
        badge.grid(row=0, column=0, padx=12, pady=10)
        badge.grid_propagate(False)
        ctk.CTkLabel(badge, text=icon, font=FONT_BOLD(14),
                     text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(row, text=log["details"],
                     font=FONT_BODY(), text_color=TEXT_MAIN).grid(
                         row=0, column=1, sticky="w", padx=8)
        ctk.CTkLabel(row, text=log["timestamp"][:16],
                     font=FONT_SMALL(), text_color=TEXT_DIM).grid(
                         row=0, column=2, padx=12)