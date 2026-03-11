import customtkinter as ctk
from tkinter import messagebox
from theme import *
from database import login


class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color=BG_MAIN)
        self.on_login_success = on_login_success
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build()

    def _build(self):
        # Center card
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=20, width=420)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.grid_columnconfigure(0, weight=1)

        # Logo & title
        ctk.CTkLabel(card, text="🏢", font=("Segoe UI Emoji", 48)).grid(
            row=0, column=0, pady=(40, 8))
        ctk.CTkLabel(card, text="AssetMate", font=FONT_BOLD(28),
                     text_color=ACCENT).grid(row=1, column=0)
        ctk.CTkLabel(card, text="Equipment & Asset Inventory System",
                     font=FONT_SMALL(), text_color=TEXT_DIM).grid(row=2, column=0, pady=(2, 32))

        # Form
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.grid(row=3, column=0, sticky="ew", padx=40)
        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="Username", font=FONT_SMALL(),
                     text_color=TEXT_DIM).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.e_user = ctk.CTkEntry(form, height=42, fg_color=BG_INPUT,
                                   border_color=BORDER, text_color=TEXT_MAIN,
                                   font=FONT_BODY(), placeholder_text="Enter username")
        self.e_user.grid(row=1, column=0, sticky="ew")

        ctk.CTkLabel(form, text="Password", font=FONT_SMALL(),
                     text_color=TEXT_DIM).grid(row=2, column=0, sticky="w", pady=(16, 4))
        self.e_pass = ctk.CTkEntry(form, height=42, fg_color=BG_INPUT,
                                   border_color=BORDER, text_color=TEXT_MAIN,
                                   font=FONT_BODY(), placeholder_text="Enter password", show="●")
        self.e_pass.grid(row=3, column=0, sticky="ew")

        self.error_label = ctk.CTkLabel(form, text="", font=FONT_SMALL(), text_color=DANGER)
        self.error_label.grid(row=4, column=0, pady=(8, 0))

        ctk.CTkButton(form, text="Login", height=44, corner_radius=10,
                      fg_color=ACCENT, hover_color="#3a7be0",
                      font=FONT_BOLD(14), command=self._attempt_login).grid(
                          row=5, column=0, sticky="ew", pady=(16, 0))

        ctk.CTkLabel(card, text="Default: admin / admin123",
                     font=FONT_TINY(), text_color=TEXT_DIM).grid(row=4, column=0, pady=(16, 40))

        # Bind Enter key
        self.e_pass.bind("<Return>", lambda e: self._attempt_login())
        self.e_user.bind("<Return>", lambda e: self.e_pass.focus())
        self.after(100, self.e_user.focus)

    def _attempt_login(self):
        username = self.e_user.get().strip()
        password = self.e_pass.get()
        if not username or not password:
            self.error_label.configure(text="Please enter username and password.")
            return
        user = login(username, password)
        if user:
            self.error_label.configure(text="")
            self.on_login_success(user)
        else:
            self.error_label.configure(text="❌  Invalid username or password.")
            self.e_pass.delete(0, "end")