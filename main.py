import customtkinter as ctk
from theme import *
from database import initialize_db
from pages.login import LoginPage
from pages.dashboard import DashboardPage
from pages.assets import AssetsPage
from pages.categories import CategoriesPage
from pages.suppliers import SuppliersPage
from pages.lowstock import LowStockPage
from pages.reports import ReportsPage
from pages.users import UsersPage

NAV = [
    ("dashboard",  "🏠", "Dashboard"),
    ("assets",     "📦", "Assets"),
    ("categories", "📁", "Categories"),
    ("suppliers",  "🏭", "Suppliers"),
    ("lowstock",   "⚠️",  "Low Stock"),
    ("reports",    "📊", "Reports"),
    ("users",      "👥", "Users"),
]

PAGE_CLASSES = {
    "dashboard":  DashboardPage,
    "assets":     AssetsPage,
    "categories": CategoriesPage,
    "suppliers":  SuppliersPage,
    "lowstock":   LowStockPage,
    "reports":    ReportsPage,
    "users":      UsersPage,
}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AssetMate — Equipment & Asset Inventory")
        self.geometry("1200x720")
        self.minsize(960, 600)
        self.configure(fg_color=BG_MAIN)
        self.current_user  = None
        self._active_page  = None
        self._nav_buttons  = {}
        self._show_login()

    # ── LOGIN ──────────────────────────────────────────────────────────────────
    def _show_login(self):
        for w in self.winfo_children():
            w.destroy()
        LoginPage(self, on_login_success=self._on_login).pack(fill="both", expand=True)

    def _on_login(self, user):
        self.current_user = user
        self._build_main()
        self.show_page("dashboard")

    # ── MAIN LAYOUT ────────────────────────────────────────────────────────────
    def _build_main(self):
        for w in self.winfo_children():
            w.destroy()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, width=210, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(99, weight=1)

        # App logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(22, 16))
        ctk.CTkLabel(logo_frame, text="🏢", font=("Segoe UI Emoji", 28)).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(logo_frame, text="AssetMate", font=FONT_BOLD(18),
                     text_color=ACCENT).pack(side="left")

        # Divider
        ctk.CTkFrame(self.sidebar, fg_color=BORDER, height=1).grid(
            row=1, column=0, sticky="ew", padx=12, pady=(0, 10))

        # Nav buttons
        self._nav_buttons = {}
        for i, (key, icon, label) in enumerate(NAV):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}   {label}",
                anchor="w",
                height=40,
                corner_radius=8,
                fg_color="transparent",
                hover_color=BG_CARD,
                text_color=TEXT_DIM,
                font=FONT_BODY(),
                command=lambda k=key: self.show_page(k)
            )
            btn.grid(row=i+2, column=0, sticky="ew", padx=10, pady=2)
            self._nav_buttons[key] = btn

        # Bottom: user info + logout
        ctk.CTkFrame(self.sidebar, fg_color=BORDER, height=1).grid(
            row=98, column=0, sticky="ew", padx=12, pady=(0, 8))

        user_frame = ctk.CTkFrame(self.sidebar, fg_color=BG_CARD, corner_radius=10)
        user_frame.grid(row=100, column=0, sticky="ew", padx=10, pady=(0, 8))

        av = ctk.CTkFrame(user_frame, fg_color=ACCENT2, corner_radius=16, width=32, height=32)
        av.pack(side="left", padx=(10, 8), pady=8)
        av.pack_propagate(False)
        initials = (self.current_user["full_name"] or self.current_user["username"])[:1].upper()
        ctk.CTkLabel(av, text=initials, font=FONT_BOLD(13), text_color="white").place(
            relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(user_frame, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(info, text=self.current_user["full_name"] or self.current_user["username"],
                     font=FONT_BOLD(11), text_color=TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(info, text=f"@{self.current_user['username']}",
                     font=FONT_TINY(), text_color=TEXT_DIM).pack(anchor="w")

        ctk.CTkButton(self.sidebar, text="⏏  Logout", height=34, corner_radius=8,
                      fg_color="transparent", hover_color=DANGER, text_color=TEXT_DIM,
                      font=FONT_SMALL(), command=self._logout).grid(
                          row=101, column=0, sticky="ew", padx=10, pady=(0, 16))

        # Content area
        self.content = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

    # ── PAGE ROUTER ────────────────────────────────────────────────────────────
    def show_page(self, key):
        if self._active_page:
            self._active_page.destroy()

        # Update nav highlight
        for k, btn in self._nav_buttons.items():
            btn.configure(
                fg_color=BG_CARD if k == key else "transparent",
                text_color=TEXT_MAIN if k == key else TEXT_DIM
            )

        PageClass = PAGE_CLASSES.get(key)
        if PageClass:
            page = PageClass(self.content, navigate=self.show_page,
                             current_user=self.current_user)
            page.grid(row=0, column=0, sticky="nsew", padx=28, pady=22)
            self._active_page = page

    # ── LOGOUT ─────────────────────────────────────────────────────────────────
    def _logout(self):
        self.current_user = None
        self._active_page = None
        self._show_login()


if __name__ == "__main__":
    initialize_db()
    app = App()
    app.mainloop()