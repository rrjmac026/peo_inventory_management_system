import customtkinter as ctk
from theme import *
from database import get_low_stock_assets


class LowStockPage(ctk.CTkFrame):
    def __init__(self, parent, navigate, current_user):
        super().__init__(parent, fg_color="transparent")
        self.navigate = navigate
        self.current_user = current_user
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hdr, text="⚠️  Low Stock Alerts", font=FONT_TITLE(),
                     text_color=WARN).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(hdr, text="Assets at or below their minimum stock level.",
                     font=FONT_BODY(), text_color=TEXT_DIM).grid(row=1, column=0, sticky="w")
        ctk.CTkButton(hdr, text="↗  Go to Assets", height=36, corner_radius=8,
                      fg_color=BG_CARD, hover_color=BORDER, text_color=TEXT_DIM,
                      command=lambda: self.navigate("assets")).grid(row=0, column=1)

        scroll = ctk.CTkScrollableFrame(self, fg_color=BG_CARD, corner_radius=14)
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        assets = get_low_stock_assets()
        if not assets:
            ctk.CTkLabel(scroll, text="🎉  All assets are well-stocked!",
                         font=FONT_HEADING(), text_color=ACCENT2).pack(pady=60)
            return

        for a in assets:
            card = ctk.CTkFrame(scroll, fg_color=BG_INPUT, corner_radius=12)
            card.pack(fill="x", padx=12, pady=5)
            card.grid_columnconfigure(1, weight=1)

            # Red qty badge
            badge = ctk.CTkFrame(card, fg_color=DANGER, corner_radius=10, width=64, height=64)
            badge.grid(row=0, column=0, rowspan=2, padx=14, pady=12)
            badge.grid_propagate(False)
            ctk.CTkLabel(badge, text=str(a["quantity"]), font=FONT_BOLD(22),
                         text_color="white").place(relx=0.5, rely=0.38, anchor="center")
            ctk.CTkLabel(badge, text="left", font=FONT_TINY(),
                         text_color="white").place(relx=0.5, rely=0.72, anchor="center")

            ctk.CTkLabel(card, text=a["name"], font=FONT_BOLD(14),
                         text_color=TEXT_MAIN).grid(row=0, column=1, sticky="w", padx=8, pady=(12, 2))

            detail = f"{a['category_name'] or 'Uncategorized'}  •  Min: {a['min_stock']}  •  ₱{a['unit_value']:,.2f}/unit"
            ctk.CTkLabel(card, text=detail, font=FONT_SMALL(),
                         text_color=TEXT_DIM).grid(row=1, column=1, sticky="w", padx=8, pady=(0, 12))

            # Urgency indicator
            urgency_color = DANGER if a["quantity"] == 0 else WARN
            urgency_text  = "OUT OF STOCK" if a["quantity"] == 0 else "LOW STOCK"
            ctk.CTkLabel(card, text=urgency_text, font=FONT_BOLD(10),
                         text_color=urgency_color).grid(row=0, column=2, padx=14, pady=(12, 0))