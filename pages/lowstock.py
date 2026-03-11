# ══════════════════════════════════════════════════════════════════════════════
#  pages/lowstock.py — Low Stock Alerts page
# ══════════════════════════════════════════════════════════════════════════════

import customtkinter as ctk
from theme import (
    BG_CARD, BG_INPUT, ACCENT2, WARN, DANGER,
    TEXT_MAIN, TEXT_DIM,
    FONT_TITLE, FONT_BODY, FONT_SMALL, FONT_BOLD
)
from database import get_low_stock_products


class LowStockPage(ctk.CTkFrame):
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
        ctk.CTkLabel(hdr, text="⚠️  Low Stock Alerts",
                     font=FONT_TITLE(), text_color=WARN).pack(anchor="w")
        ctk.CTkLabel(hdr, text="Products at or below their minimum stock level.",
                     font=FONT_BODY(), text_color=TEXT_DIM).pack(anchor="w")

        # Scrollable list
        scroll = ctk.CTkScrollableFrame(self, fg_color=BG_CARD, corner_radius=14)
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        products = get_low_stock_products()
        if not products:
            ctk.CTkLabel(scroll, text="🎉  All products are well-stocked!",
                         font=FONT_BODY(), text_color=ACCENT2).pack(pady=40)
            return

        for p in products:
            self._product_card(scroll, p)

    def _product_card(self, parent, p):
        card = ctk.CTkFrame(parent, fg_color=BG_INPUT, corner_radius=10)
        card.pack(fill="x", padx=12, pady=5)
        card.grid_columnconfigure(1, weight=1)

        # Red quantity badge
        badge = ctk.CTkFrame(card, fg_color=DANGER, corner_radius=8, width=60, height=60)
        badge.grid(row=0, column=0, padx=14, pady=12, rowspan=2)
        badge.grid_propagate(False)
        ctk.CTkLabel(badge, text=str(p["quantity"]),
                     font=FONT_BOLD(20), text_color="white").place(relx=0.5, rely=0.4, anchor="center")
        ctk.CTkLabel(badge, text="left",
                     font=FONT_SMALL(), text_color="white").place(relx=0.5, rely=0.75, anchor="center")

        ctk.CTkLabel(card, text=p["name"],
                     font=FONT_BOLD(14), text_color=TEXT_MAIN).grid(
                         row=0, column=1, sticky="w", padx=8, pady=(12, 2))
        ctk.CTkLabel(card, text=f"{p['category']}  •  Min: {p['min_stock']}  •  ₱{p['price']:,.2f}",
                     font=FONT_SMALL(), text_color=TEXT_DIM).grid(
                         row=1, column=1, sticky="w", padx=8, pady=(0, 12))