# ══════════════════════════════════════════════════════════════════════════════
#  main.py — App entry point. Only handles the window, sidebar, and page routing.
#  Each page lives in its own file — add new pages here without touching others.
# ══════════════════════════════════════════════════════════════════════════════

import customtkinter as ctk
from database import initialize_db
from theme import (
    BG_MAIN, BG_SIDEBAR, BG_CARD, ACCENT,
    TEXT_MAIN, TEXT_DIM, BORDER,
    FONT_BODY, FONT_BOLD
)

# ── Page imports ───────────────────────────────────────────────────────────────
from dashboard        import DashboardPage
from products         import ProductsPage
from pages.lowstock   import LowStockPage
from pages.activity   import ActivityPage


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class InventoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        initialize_db()

        self.title("📦 Inventory Management System")
        self.geometry("1200x720")
        self.minsize(1000, 620)
        self.configure(fg_color=BG_MAIN)

        self.current_page = None
        self._build_layout()
        self.show_page("dashboard")

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, self.show_page)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.content = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

    def show_page(self, name):
        if self.current_page:
            self.current_page.destroy()

        # ── To add a new page: import it above, then add it here ──────────────
        pages = {
            "dashboard": DashboardPage,
            "products":  ProductsPage,
            "lowstock":  LowStockPage,
            "activity":  ActivityPage,
        }

        self.current_page = pages[name](self.content, self.show_page)
        self.current_page.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        self.sidebar.set_active(name)


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
class Sidebar(ctk.CTkFrame):
    # ── Add new nav items here as you create new pages ─────────────────────────
    NAV = [
        ("dashboard", "⬛", "Dashboard"),
        ("products",  "📦", "Products"),
        ("lowstock",  "⚠️",  "Low Stock"),
        ("activity",  "📋", "Activity Log"),
    ]

    def __init__(self, parent, on_navigate):
        super().__init__(parent, fg_color=BG_SIDEBAR, corner_radius=0, width=220)
        self.on_navigate = on_navigate
        self._buttons = {}
        self._build()

    def _build(self):
        self.pack_propagate(False)
        self.grid_propagate(False)

        logo = ctk.CTkFrame(self, fg_color="transparent", height=80)
        logo.pack(fill="x", padx=20, pady=(24, 8))
        ctk.CTkLabel(logo, text="📦", font=("Segoe UI Emoji", 28)).pack(anchor="w")
        ctk.CTkLabel(logo, text="StockMate", font=FONT_BOLD(18),
                     text_color=TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(logo, text="Inventory System", font=FONT_BODY(),
                     text_color=TEXT_DIM).pack(anchor="w")

        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x", padx=16, pady=12)

        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", padx=12)

        for key, icon, label in self.NAV:
            btn = ctk.CTkButton(
                nav_frame, text=f"  {icon}  {label}",
                anchor="w", height=44, corner_radius=10,
                font=FONT_BODY(),
                fg_color="transparent", hover_color=BG_CARD,
                text_color=TEXT_DIM,
                command=lambda k=key: self.on_navigate(k)
            )
            btn.pack(fill="x", pady=2)
            self._buttons[key] = btn

        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(
            fill="x", padx=16, pady=12, side="bottom")
        ctk.CTkLabel(self, text="v1.0.0  •  SQLite", font=FONT_BODY(),
                     text_color=TEXT_DIM).pack(side="bottom", pady=(0, 16))

    def set_active(self, key):
        for k, btn in self._buttons.items():
            if k == key:
                btn.configure(fg_color=BG_CARD, text_color=ACCENT)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_DIM)


if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()