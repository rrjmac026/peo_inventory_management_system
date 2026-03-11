# ══════════════════════════════════════════════════════════════════════════════
#  products.py — Products list page + Add/Edit form popup
# ══════════════════════════════════════════════════════════════════════════════

import customtkinter as ctk
from tkinter import messagebox, ttk
from theme import (
    BG_CARD, BG_INPUT, BG_MAIN, ACCENT, WARN, DANGER,
    TEXT_MAIN, TEXT_DIM, BORDER, ACCENT2,
    FONT_TITLE, FONT_BODY, FONT_SMALL, FONT_TINY, FONT_BOLD
)
from database import (
    get_all_products, search_products, add_product,
    update_product, delete_product, get_product_by_id
)


# ══════════════════════════════════════════════════════════════════════════════
#  PRODUCTS PAGE
# ══════════════════════════════════════════════════════════════════════════════
class ProductsPage(ctk.CTkFrame):
    def __init__(self, parent, navigate):
        super().__init__(parent, fg_color="transparent")
        self.navigate = navigate
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._build()
        self._load_products()

    def _build(self):
        self._build_header()
        self._build_searchbar()
        self._build_table()

    # ── Header ─────────────────────────────────────────────────────────────────
    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hdr, text="Products", font=FONT_TITLE(),
                     text_color=TEXT_MAIN).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(hdr, text="＋  Add Product", font=FONT_BODY(),
                      fg_color=ACCENT, hover_color="#3a7be0",
                      height=38, corner_radius=10,
                      command=self._open_add).grid(row=0, column=1)

    # ── Search bar ─────────────────────────────────────────────────────────────
    def _build_searchbar(self):
        frame = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=10, height=44)
        frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_propagate(False)

        ctk.CTkLabel(frame, text="🔍", font=("Segoe UI Emoji", 16)).grid(
            row=0, column=0, padx=(12, 4), pady=8)
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._load_products())
        ctk.CTkEntry(frame, textvariable=self.search_var,
                     placeholder_text="Search by name or category...",
                     fg_color="transparent", border_width=0,
                     font=FONT_BODY(), text_color=TEXT_MAIN).grid(
                         row=0, column=1, sticky="ew", padx=4)

    # ── Table ──────────────────────────────────────────────────────────────────
    def _build_table(self):
        table_frame = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=14)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.grid_rowconfigure(1, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Style the Treeview to match the dark theme
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=BG_CARD, fieldbackground=BG_CARD,
                        foreground=TEXT_MAIN, rowheight=38,
                        font=("Helvetica", 12), borderwidth=0)
        style.configure("Treeview.Heading",
                        background=BG_INPUT, foreground=TEXT_DIM,
                        font=("Helvetica", 11, "bold"), relief="flat", borderwidth=0)
        style.map("Treeview",
                  background=[("selected", "#2a3f6e")],
                  foreground=[("selected", TEXT_MAIN)])
        style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        cols       = ("ID", "Name", "Category", "Price", "Quantity", "Min Stock", "Status")
        col_widths = (50,   220,    130,         90,      90,         90,          100)

        container = ctk.CTkFrame(table_frame, fg_color="transparent")
        container.grid(row=1, column=0, sticky="nsew", padx=12, pady=8)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(container, columns=cols, show="headings", selectmode="browse")
        for col, w in zip(cols, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, minwidth=w, anchor="center")
        self.tree.column("Name", anchor="w")
        self.tree.tag_configure("low", foreground=WARN)
        self.tree.tag_configure("ok",  foreground=ACCENT2)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Action buttons row
        btn_row = ctk.CTkFrame(table_frame, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", padx=12, pady=(4, 12))

        ctk.CTkButton(btn_row, text="✏️  Edit", width=110, height=34, corner_radius=8,
                      fg_color=BG_INPUT, hover_color=BORDER, text_color=TEXT_MAIN,
                      command=self._open_edit).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_row, text="🗑️  Delete", width=110, height=34, corner_radius=8,
                      fg_color=BG_INPUT, hover_color=DANGER, text_color=TEXT_MAIN,
                      command=self._delete_product).pack(side="left")

        self.count_label = ctk.CTkLabel(btn_row, text="", font=FONT_SMALL(), text_color=TEXT_DIM)
        self.count_label.pack(side="right")

    # ── Data ───────────────────────────────────────────────────────────────────
    def _load_products(self):
        query    = self.search_var.get().strip()
        products = search_products(query) if query else get_all_products()
        self.tree.delete(*self.tree.get_children())
        for p in products:
            low    = p["quantity"] <= p["min_stock"]
            status = "⚠️ Low" if low else "✅ OK"
            self.tree.insert("", "end", iid=str(p["id"]), tags=("low" if low else "ok",),
                             values=(p["id"], p["name"], p["category"],
                                     f"₱{p['price']:,.2f}", p["quantity"],
                                     p["min_stock"], status))
        self.count_label.configure(text=f"{len(products)} product(s)")

    def _get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a product first.")
            return None
        return int(sel[0])

    # ── Actions ────────────────────────────────────────────────────────────────
    def _open_add(self):
        ProductForm(self, None, self._load_products)

    def _open_edit(self):
        pid = self._get_selected_id()
        if pid:
            ProductForm(self, pid, self._load_products)

    def _delete_product(self):
        pid = self._get_selected_id()
        if not pid:
            return
        name = self.tree.item(str(pid))["values"][1]
        if messagebox.askyesno("Confirm Delete",
                               f"Delete '{name}'?\nThis cannot be undone.", icon="warning"):
            delete_product(pid)
            self._load_products()


# ══════════════════════════════════════════════════════════════════════════════
#  PRODUCT FORM — Add / Edit popup window
# ══════════════════════════════════════════════════════════════════════════════
class ProductForm(ctk.CTkToplevel):
    def __init__(self, parent, product_id, on_save):
        super().__init__(parent)
        self.product_id = product_id
        self.on_save    = on_save
        self.title("Edit Product" if product_id else "Add Product")
        self.geometry("480x520")
        self.resizable(False, False)
        self.configure(fg_color=BG_MAIN)
        self.grab_set()   # makes the form modal (blocks main window)
        self._build()
        if product_id:
            self._populate()

    # ── Build the form ─────────────────────────────────────────────────────────
    def _build(self):
        self.grid_columnconfigure(0, weight=1)

        title = "Edit Product" if self.product_id else "Add New Product"
        ctk.CTkLabel(self, text=title, font=FONT_BOLD(20),
                     text_color=TEXT_MAIN).grid(row=0, column=0, sticky="w", padx=28, pady=(24, 4))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.grid(row=1, column=0, sticky="nsew", padx=28, pady=8)
        form.grid_columnconfigure(0, weight=1)

        self.e_name     = self._field(form, "Product Name",    0, "e.g. Apple iPhone 15")
        self.e_category = self._field(form, "Category",        1, "e.g. Electronics")
        self.e_price    = self._field(form, "Price (₱)",       2, "e.g. 55000")
        self.e_qty      = self._field(form, "Quantity",        3, "e.g. 10")
        self.e_min      = self._field(form, "Min Stock Alert", 4, "e.g. 5")

        ctk.CTkLabel(form, text="Description (optional)", font=FONT_SMALL(),
                     text_color=TEXT_DIM).grid(row=10, column=0, sticky="w", pady=(10, 2))
        self.e_desc = ctk.CTkTextbox(form, height=60, fg_color=BG_INPUT, border_color=BORDER,
                                     text_color=TEXT_MAIN, font=FONT_BODY())
        self.e_desc.grid(row=11, column=0, sticky="ew")

        # Save / Cancel buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", padx=28, pady=20)
        btn_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_row, text="Cancel", fg_color=BG_INPUT, hover_color=BORDER,
                      text_color=TEXT_MAIN, height=40, corner_radius=10,
                      command=self.destroy).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(btn_row, text="Save Product", fg_color=ACCENT, hover_color="#3a7be0",
                      height=40, corner_radius=10,
                      command=self._save).grid(row=0, column=1, sticky="ew")

    def _field(self, parent, label, row, placeholder=""):
        """Helper: creates a label + entry pair and returns the entry widget."""
        ctk.CTkLabel(parent, text=label, font=FONT_SMALL(),
                     text_color=TEXT_DIM).grid(row=row * 2, column=0, sticky="w", pady=(10, 2))
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, height=38,
                             fg_color=BG_INPUT, border_color=BORDER,
                             text_color=TEXT_MAIN, font=FONT_BODY())
        entry.grid(row=row * 2 + 1, column=0, sticky="ew")
        return entry

    # ── Populate fields when editing ───────────────────────────────────────────
    def _populate(self):
        p = get_product_by_id(self.product_id)
        if not p:
            return
        self.e_name.insert(0, p["name"])
        self.e_category.insert(0, p["category"])
        self.e_price.insert(0, str(p["price"]))
        self.e_qty.insert(0, str(p["quantity"]))
        self.e_min.insert(0, str(p["min_stock"]))
        if p["description"]:
            self.e_desc.insert("1.0", p["description"])

    # ── Validate & save ────────────────────────────────────────────────────────
    def _save(self):
        name     = self.e_name.get().strip()
        category = self.e_category.get().strip()
        price_s  = self.e_price.get().strip()
        qty_s    = self.e_qty.get().strip()
        min_s    = self.e_min.get().strip()
        desc     = self.e_desc.get("1.0", "end").strip()

        if not all([name, category, price_s, qty_s, min_s]):
            messagebox.showerror("Missing Fields", "Please fill in all required fields.")
            return
        try:
            price   = float(price_s)
            qty     = int(qty_s)
            min_qty = int(min_s)
        except ValueError:
            messagebox.showerror("Invalid Input",
                                 "Price must be a number.\nQuantity and Min Stock must be whole numbers.")
            return

        if self.product_id:
            update_product(self.product_id, name, category, price, qty, min_qty, desc)
        else:
            add_product(name, category, price, qty, min_qty, desc)

        self.on_save()
        self.destroy()