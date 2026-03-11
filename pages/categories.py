import customtkinter as ctk
from tkinter import messagebox, ttk
from theme import *
from database import get_all_categories, add_category, rename_category, delete_category


class CategoriesPage(ctk.CTkFrame):
    def __init__(self, parent, navigate, current_user):
        super().__init__(parent, fg_color="transparent")
        self.navigate = navigate
        self.current_user = current_user
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build()
        self._load()

    def _build(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hdr, text="Categories", font=FONT_TITLE(),
                     text_color=TEXT_MAIN).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(hdr, text="Manage asset categories.", font=FONT_BODY(),
                     text_color=TEXT_DIM).grid(row=1, column=0, sticky="w")

        # Add bar
        add_bar = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12)
        add_bar.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        add_bar.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(add_bar, text="Add New Category", font=FONT_HEADING(),
                     text_color=TEXT_MAIN).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 6))
        inner = ctk.CTkFrame(add_bar, fg_color="transparent")
        inner.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 14))
        inner.grid_columnconfigure(0, weight=1)
        self.e_new = ctk.CTkEntry(inner, placeholder_text="Category name...", height=38,
                                  fg_color=BG_INPUT, border_color=BORDER,
                                  text_color=TEXT_MAIN, font=FONT_BODY())
        self.e_new.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkButton(inner, text="Add", width=90, height=38, corner_radius=8,
                      fg_color=ACCENT, hover_color="#3a7be0",
                      command=self._add_category).grid(row=0, column=1)

        # List
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=BG_CARD, corner_radius=14)
        self.scroll.grid(row=2, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

    def _load(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        cats = get_all_categories()
        if not cats:
            ctk.CTkLabel(self.scroll, text="No categories yet.", font=FONT_BODY(),
                         text_color=TEXT_DIM).pack(pady=30)
            return
        for c in cats:
            self._cat_row(c)

    def _cat_row(self, c):
        row = ctk.CTkFrame(self.scroll, fg_color=BG_INPUT, corner_radius=10)
        row.pack(fill="x", padx=12, pady=4)
        row.grid_columnconfigure(1, weight=1)

        # Color dot
        dot = ctk.CTkFrame(row, fg_color=ACCENT, corner_radius=6, width=10, height=36)
        dot.grid(row=0, column=0, padx=(14, 10), pady=10)
        dot.grid_propagate(False)

        ctk.CTkLabel(row, text=c["name"], font=FONT_BODY(),
                     text_color=TEXT_MAIN).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(row, text=f"{c['asset_count']} asset(s)",
                     font=FONT_SMALL(), text_color=TEXT_DIM).grid(row=0, column=2, padx=12)

        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.grid(row=0, column=3, padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Rename", width=70, height=28, corner_radius=6,
                      fg_color=BG_CARD, hover_color=BORDER, text_color=TEXT_DIM,
                      font=FONT_SMALL(),
                      command=lambda cid=c["id"], cname=c["name"]: self._rename(cid, cname)
                      ).pack(side="left", padx=(0, 4))
        ctk.CTkButton(btn_frame, text="Delete", width=70, height=28, corner_radius=6,
                      fg_color=BG_CARD, hover_color=DANGER, text_color=TEXT_DIM,
                      font=FONT_SMALL(),
                      command=lambda cid=c["id"], cname=c["name"]: self._delete(cid, cname)
                      ).pack(side="left")

    def _add_category(self):
        name = self.e_new.get().strip()
        if not name:
            messagebox.showwarning("Empty", "Please enter a category name.")
            return
        ok, msg = add_category(name)
        if ok:
            self.e_new.delete(0, "end")
            self._load()
        else:
            messagebox.showerror("Error", msg)

    def _rename(self, cat_id, old_name):
        dialog = ctk.CTkInputDialog(text=f"Rename '{old_name}' to:", title="Rename Category")
        new_name = dialog.get_input()
        if new_name and new_name.strip():
            ok, msg = rename_category(cat_id, new_name.strip())
            if ok: self._load()
            else: messagebox.showerror("Error", msg)

    def _delete(self, cat_id, name):
        if messagebox.askyesno("Confirm", f"Delete category '{name}'?\nAssets in this category will become uncategorized."):
            delete_category(cat_id)
            self._load()