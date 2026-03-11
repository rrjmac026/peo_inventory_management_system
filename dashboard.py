# ══════════════════════════════════════════════════════════════════════════════
#  dashboard.py — Dashboard page with stat cards, activity feed, low stock panel
# ══════════════════════════════════════════════════════════════════════════════

import customtkinter as ctk
from theme import (
    BG_CARD, BG_INPUT, ACCENT, ACCENT2, WARN, DANGER, GOLD,
    TEXT_MAIN, TEXT_DIM,
    FONT_TITLE, FONT_HEADING, FONT_BODY, FONT_SMALL, FONT_TINY, FONT_BOLD
)
from database import get_dashboard_stats, get_recent_activity, get_low_stock_products


class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, navigate):
        super().__init__(parent, fg_color="transparent")
        self.navigate = navigate
        self.grid_columnconfigure(0, weight=1)
        self._build()

    # ── Main build ─────────────────────────────────────────────────────────────
    def _build(self):
        self._build_header()
        self._build_stat_cards()
        self._build_bottom_row()

    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        ctk.CTkLabel(hdr, text="Dashboard", font=FONT_TITLE(),
                     text_color=TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(hdr, text="Welcome back! Here's your inventory overview.",
                     font=FONT_BODY(), text_color=TEXT_DIM).pack(anchor="w")

    def _build_stat_cards(self):
        stats = get_dashboard_stats()
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        for i in range(4):
            frame.grid_columnconfigure(i, weight=1)

        card_data = [
            ("Total Products",   stats["total_products"],          "📦", ACCENT),
            ("Items in Stock",   stats["total_items"],             "🗃️", ACCENT2),
            ("Inventory Value",  f"₱{stats['total_value']:,.2f}",  "💰", GOLD),
            ("Low Stock Alerts", stats["low_stock_count"],         "⚠️",  WARN),
        ]
        for i, (label, value, icon, color) in enumerate(card_data):
            _StatCard(frame, label, value, icon, color).grid(
                row=0, column=i, padx=(0 if i == 0 else 8, 0), sticky="ew")

    def _build_bottom_row(self):
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="nsew")
        bottom.grid_columnconfigure(0, weight=2)
        bottom.grid_columnconfigure(1, weight=1)
        bottom.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        _ActivityPanel(bottom).grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        _LowStockPanel(bottom).grid(row=0, column=1, sticky="nsew")


# ── Sub-widgets ────────────────────────────────────────────────────────────────

class _StatCard(ctk.CTkFrame):
    def __init__(self, parent, label, value, icon, color):
        super().__init__(parent, fg_color=BG_CARD, corner_radius=14, height=110)
        self.pack_propagate(False)
        ctk.CTkLabel(self, text=icon, font=("Segoe UI Emoji", 22)).pack(anchor="w", padx=16, pady=(14, 0))
        ctk.CTkLabel(self, text=str(value), font=FONT_BOLD(24),
                     text_color=color).pack(anchor="w", padx=16)
        ctk.CTkLabel(self, text=label, font=FONT_SMALL(),
                     text_color=TEXT_DIM).pack(anchor="w", padx=16, pady=(0, 12))


class _ActivityPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG_CARD, corner_radius=14)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Recent Activity", font=FONT_HEADING(),
                     text_color=TEXT_MAIN).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 8))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 12))

        logs = get_recent_activity(8)
        if not logs:
            ctk.CTkLabel(scroll, text="No activity yet.",
                         text_color=TEXT_DIM, font=FONT_BODY()).pack(pady=20)
            return

        action_colors = {"ADD": ACCENT2, "EDIT": ACCENT, "DELETE": DANGER}
        for log in logs:
            row = ctk.CTkFrame(scroll, fg_color=BG_INPUT, corner_radius=8)
            row.pack(fill="x", pady=3, padx=4)
            color = action_colors.get(log["action"], TEXT_DIM)
            ctk.CTkLabel(row, text=log["action"], font=FONT_BOLD(10),
                         text_color=color, width=50).pack(side="left", padx=(10, 6), pady=8)
            ctk.CTkLabel(row, text=log["details"], font=FONT_BODY(),
                         text_color=TEXT_MAIN).pack(side="left")
            ctk.CTkLabel(row, text=log["timestamp"][:16], font=FONT_TINY(),
                         text_color=TEXT_DIM).pack(side="right", padx=10)


class _LowStockPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG_CARD, corner_radius=14)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="⚠️  Low Stock", font=FONT_HEADING(),
                     text_color=WARN).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 8))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 12))

        low = get_low_stock_products()
        if not low:
            ctk.CTkLabel(scroll, text="All stocked up! ✅",
                         text_color=ACCENT2, font=FONT_BODY()).pack(pady=20)
            return

        for p in low:
            row = ctk.CTkFrame(scroll, fg_color=BG_INPUT, corner_radius=8)
            row.pack(fill="x", pady=3, padx=4)
            ctk.CTkLabel(row, text=p["name"], font=FONT_BODY(),
                         text_color=TEXT_MAIN).pack(side="left", padx=10, pady=8)
            ctk.CTkLabel(row, text=f"{p['quantity']} left", font=FONT_BOLD(11),
                         text_color=DANGER).pack(side="right", padx=10)