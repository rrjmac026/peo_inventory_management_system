import customtkinter as ctk
from theme import *
from database import get_dashboard_stats, get_recent_activity, get_low_stock_assets


class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, navigate, current_user):
        super().__init__(parent, fg_color="transparent")
        self.navigate = navigate
        self.current_user = current_user
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hdr, text="Dashboard", font=FONT_TITLE(),
                     text_color=TEXT_MAIN).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(hdr, text=f"Welcome back, {self.current_user['full_name'] or self.current_user['username']}! 👋",
                     font=FONT_BODY(), text_color=TEXT_DIM).grid(row=1, column=0, sticky="w")

        # Stat cards
        stats = get_dashboard_stats()
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        for i in range(6):
            cards_frame.grid_columnconfigure(i, weight=1)

        card_data = [
            ("Total Assets",      stats["total_assets"],          "🏢", ACCENT),
            ("Total Units",       stats["total_units"],           "📦", ACCENT2),
            ("Total Value",       f"₱{stats['total_value']:,.2f}","💰", GOLD),
            ("Low Stock",         stats["low_stock_count"],       "⚠️",  WARN),
            ("Categories",        stats["total_categories"],      "📁", "#a78bfa"),
            ("Suppliers",         stats["total_suppliers"],       "🏭", "#f472b6"),
        ]
        for i, (label, value, icon, color) in enumerate(card_data):
            _StatCard(cards_frame, label, value, icon, color).grid(
                row=0, column=i, padx=(0 if i == 0 else 6, 0), sticky="ew")

        # Bottom panels
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="nsew")
        bottom.grid_columnconfigure(0, weight=2)
        bottom.grid_columnconfigure(1, weight=1)
        bottom.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        _ActivityPanel(bottom).grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        _LowStockPanel(bottom, navigate=self.navigate).grid(row=0, column=1, sticky="nsew")


class _StatCard(ctk.CTkFrame):
    def __init__(self, parent, label, value, icon, color):
        super().__init__(parent, fg_color=BG_CARD, corner_radius=14, height=100)
        self.pack_propagate(False)
        ctk.CTkLabel(self, text=icon, font=("Segoe UI Emoji", 18)).pack(anchor="w", padx=14, pady=(12, 0))
        ctk.CTkLabel(self, text=str(value), font=FONT_BOLD(20),
                     text_color=color).pack(anchor="w", padx=14)
        ctk.CTkLabel(self, text=label, font=FONT_TINY(),
                     text_color=TEXT_DIM).pack(anchor="w", padx=14, pady=(0, 10))


class _ActivityPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG_CARD, corner_radius=14)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Recent Activity", font=FONT_HEADING(),
                     text_color=TEXT_MAIN).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 8))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 12))

        logs = get_recent_activity(12)
        if not logs:
            ctk.CTkLabel(scroll, text="No activity yet.",
                         text_color=TEXT_DIM, font=FONT_BODY()).pack(pady=20)
            return

        colors = {"ADD": ACCENT2, "EDIT": ACCENT, "DELETE": DANGER}
        icons  = {"ADD": "＋", "EDIT": "✎", "DELETE": "✕"}
        for log in logs:
            row = ctk.CTkFrame(scroll, fg_color=BG_INPUT, corner_radius=8)
            row.pack(fill="x", pady=2, padx=4)
            color = colors.get(log["action"], TEXT_DIM)
            badge = ctk.CTkFrame(row, fg_color=color, corner_radius=5, width=26, height=26)
            badge.pack(side="left", padx=(8, 6), pady=8)
            badge.pack_propagate(False)
            ctk.CTkLabel(badge, text=icons.get(log["action"], "•"),
                         font=FONT_BOLD(11), text_color="white").place(relx=0.5, rely=0.5, anchor="center")
            ctk.CTkLabel(row, text=log["details"] or "", font=FONT_SMALL(),
                         text_color=TEXT_MAIN).pack(side="left")
            ctk.CTkLabel(row, text=log["timestamp"][:16], font=FONT_TINY(),
                         text_color=TEXT_DIM).pack(side="right", padx=8)


class _LowStockPanel(ctk.CTkFrame):
    def __init__(self, parent, navigate):
        super().__init__(parent, fg_color=BG_CARD, corner_radius=14)
        self.navigate = navigate
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
        hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hdr, text="⚠️  Low Stock", font=FONT_HEADING(),
                     text_color=WARN).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(hdr, text="View All", width=70, height=26, corner_radius=6,
                      fg_color=BG_INPUT, hover_color=BORDER, text_color=TEXT_DIM,
                      font=FONT_TINY(),
                      command=lambda: self.navigate("lowstock")).grid(row=0, column=1)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 12))

        low = get_low_stock_assets()
        if not low:
            ctk.CTkLabel(scroll, text="All assets stocked up! ✅",
                         text_color=ACCENT2, font=FONT_BODY()).pack(pady=20)
            return

        for a in low:
            row = ctk.CTkFrame(scroll, fg_color=BG_INPUT, corner_radius=8)
            row.pack(fill="x", pady=2, padx=4)
            ctk.CTkLabel(row, text=a["name"], font=FONT_SMALL(),
                         text_color=TEXT_MAIN).pack(side="left", padx=10, pady=8)
            ctk.CTkLabel(row, text=f"{a['quantity']} left",
                         font=FONT_BOLD(11), text_color=DANGER).pack(side="right", padx=10)