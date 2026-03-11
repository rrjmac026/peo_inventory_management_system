import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
from database import (
    initialize_db, get_all_products, add_product, update_product,
    delete_product, search_products, get_low_stock_products,
    get_dashboard_stats, get_recent_activity
)

# ── Theme ──────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Color Palette ──────────────────────────────────────────────────────────────
BG_MAIN     = "#0f1117"
BG_SIDEBAR  = "#161b27"
BG_CARD     = "#1e2535"
BG_INPUT    = "#252d3d"
ACCENT      = "#4f8ef7"
ACCENT2     = "#38d9a9"
WARN        = "#f5a623"
DANGER      = "#e05c5c"
TEXT_MAIN   = "#e8eaf0"
TEXT_DIM    = "#6b7a99"
BORDER      = "#2a3347"


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
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

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = Sidebar(self, self.show_page)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Content area
        self.content = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

    # ── Page Router ───────────────────────────────────────────────────────────
    def show_page(self, name):
        if self.current_page:
            self.current_page.destroy()

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

        # Logo
        logo = ctk.CTkFrame(self, fg_color="transparent", height=80)
        logo.pack(fill="x", padx=20, pady=(24, 8))
        ctk.CTkLabel(logo, text="📦", font=("Segoe UI Emoji", 28)).pack(anchor="w")
        ctk.CTkLabel(logo, text="StockMate", font=ctk.CTkFont("Helvetica", 18, "bold"),
                     text_color=TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(logo, text="Inventory System", font=ctk.CTkFont("Helvetica", 11),
                     text_color=TEXT_DIM).pack(anchor="w")

        # Divider
        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x", padx=16, pady=12)

        # Nav buttons
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", padx=12)

        for key, icon, label in self.NAV:
            btn = ctk.CTkButton(
                nav_frame, text=f"  {icon}  {label}",
                anchor="w", height=44, corner_radius=10,
                font=ctk.CTkFont("Helvetica", 13),
                fg_color="transparent", hover_color=BG_CARD,
                text_color=TEXT_DIM,
                command=lambda k=key: self.on_navigate(k)
            )
            btn.pack(fill="x", pady=2)
            self._buttons[key] = btn

        # Footer
        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x", padx=16, pady=12, side="bottom")
        ctk.CTkLabel(self, text="v1.0.0  •  SQLite", font=ctk.CTkFont("Helvetica", 10),
                     text_color=TEXT_DIM).pack(side="bottom", pady=(0, 16))

    def set_active(self, key):
        for k, btn in self._buttons.items():
            if k == key:
                btn.configure(fg_color=BG_CARD, text_color=ACCENT)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_DIM)


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD PAGE
# ══════════════════════════════════════════════════════════════════════════════
class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, navigate):
        super().__init__(parent, fg_color="transparent")
        self.navigate = navigate
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)

        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        ctk.CTkLabel(hdr, text="Dashboard", font=ctk.CTkFont("Helvetica", 26, "bold"),
                     text_color=TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(hdr, text="Welcome back! Here's your inventory overview.",
                     font=ctk.CTkFont("Helvetica", 13), text_color=TEXT_DIM).pack(anchor="w")

        # Stat cards
        stats = get_dashboard_stats()
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1)

        card_data = [
            ("Total Products",   stats["total_products"],   "📦", ACCENT),
            ("Items in Stock",   stats["total_items"],      "🗃️", ACCENT2),
            ("Inventory Value",  f"₱{stats['total_value']:,.2f}", "💰", "#f7c948"),
            ("Low Stock Alerts", stats["low_stock_count"],  "⚠️",  WARN),
        ]
        for i, (label, value, icon, color) in enumerate(card_data):
            self._stat_card(cards_frame, label, value, icon, color).grid(
                row=0, column=i, padx=(0 if i == 0 else 8, 0), sticky="ew")

        # Bottom row
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="nsew")
        bottom.grid_columnconfigure(0, weight=2)
        bottom.grid_columnconfigure(1, weight=1)
        bottom.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Recent activity
        act_card = ctk.CTkFrame(bottom, fg_color=BG_CARD, corner_radius=14)
        act_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        act_card.grid_rowconfigure(1, weight=1)
        act_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(act_card, text="Recent Activity",
                     font=ctk.CTkFont("Helvetica", 15, "bold"),
                     text_color=TEXT_MAIN).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 8))

        logs = get_recent_activity(8)
        scroll = ctk.CTkScrollableFrame(act_card, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 12))

        if logs:
            for log in logs:
                row = ctk.CTkFrame(scroll, fg_color=BG_INPUT, corner_radius=8)
                row.pack(fill="x", pady=3, padx=4)
                color = {"ADD": ACCENT2, "EDIT": ACCENT, "DELETE": DANGER}.get(log["action"], TEXT_DIM)
                ctk.CTkLabel(row, text=log["action"], font=ctk.CTkFont("Helvetica", 10, "bold"),
                             text_color=color, width=50).pack(side="left", padx=(10, 6), pady=8)
                ctk.CTkLabel(row, text=log["details"], font=ctk.CTkFont("Helvetica", 12),
                             text_color=TEXT_MAIN).pack(side="left")
                ctk.CTkLabel(row, text=log["timestamp"][:16], font=ctk.CTkFont("Helvetica", 10),
                             text_color=TEXT_DIM).pack(side="right", padx=10)
        else:
            ctk.CTkLabel(scroll, text="No activity yet.", text_color=TEXT_DIM,
                         font=ctk.CTkFont("Helvetica", 13)).pack(pady=20)

        # Low stock panel
        ls_card = ctk.CTkFrame(bottom, fg_color=BG_CARD, corner_radius=14)
        ls_card.grid(row=0, column=1, sticky="nsew")
        ls_card.grid_rowconfigure(1, weight=1)
        ls_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(ls_card, text="⚠️  Low Stock",
                     font=ctk.CTkFont("Helvetica", 15, "bold"),
                     text_color=WARN).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 8))

        low = get_low_stock_products()
        ls_scroll = ctk.CTkScrollableFrame(ls_card, fg_color="transparent")
        ls_scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 12))

        if low:
            for p in low:
                row = ctk.CTkFrame(ls_scroll, fg_color=BG_INPUT, corner_radius=8)
                row.pack(fill="x", pady=3, padx=4)
                ctk.CTkLabel(row, text=p["name"], font=ctk.CTkFont("Helvetica", 12),
                             text_color=TEXT_MAIN).pack(side="left", padx=10, pady=8)
                ctk.CTkLabel(row, text=f"{p['quantity']} left",
                             font=ctk.CTkFont("Helvetica", 11, "bold"),
                             text_color=DANGER).pack(side="right", padx=10)
        else:
            ctk.CTkLabel(ls_scroll, text="All stocked up! ✅",
                         text_color=ACCENT2, font=ctk.CTkFont("Helvetica", 13)).pack(pady=20)

    def _stat_card(self, parent, label, value, icon, color):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=14, height=110)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=icon, font=("Segoe UI Emoji", 22)).pack(anchor="w", padx=16, pady=(14, 0))
        ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont("Helvetica", 24, "bold"),
                     text_color=color).pack(anchor="w", padx=16)
        ctk.CTkLabel(card, text=label, font=ctk.CTkFont("Helvetica", 12),
                     text_color=TEXT_DIM).pack(anchor="w", padx=16, pady=(0, 12))
        return card


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
        # Header row
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(hdr, text="Products", font=ctk.CTkFont("Helvetica", 26, "bold"),
                     text_color=TEXT_MAIN).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(hdr, text="＋  Add Product", font=ctk.CTkFont("Helvetica", 13),
                      fg_color=ACCENT, hover_color="#3a7be0", height=38, corner_radius=10,
                      command=self._open_add).grid(row=0, column=1)

        # Search bar
        search_frame = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=10, height=44)
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        search_frame.grid_columnconfigure(1, weight=1)
        search_frame.grid_propagate(False)

        ctk.CTkLabel(search_frame, text="🔍", font=("Segoe UI Emoji", 16)).grid(
            row=0, column=0, padx=(12, 4), pady=8)
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._load_products())
        ctk.CTkEntry(search_frame, textvariable=self.search_var,
                     placeholder_text="Search by name or category...",
                     fg_color="transparent", border_width=0,
                     font=ctk.CTkFont("Helvetica", 13),
                     text_color=TEXT_MAIN).grid(row=0, column=1, sticky="ew", padx=4)

        # Table
        table_frame = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=14)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.grid_rowconfigure(1, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Column headers
        cols = ("ID", "Name", "Category", "Price", "Quantity", "Min Stock", "Status")
        col_widths = (50, 220, 130, 90, 90, 90, 100)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=BG_CARD, fieldbackground=BG_CARD,
                        foreground=TEXT_MAIN, rowheight=38,
                        font=("Helvetica", 12), borderwidth=0)
        style.configure("Treeview.Heading",
                        background=BG_INPUT, foreground=TEXT_DIM,
                        font=("Helvetica", 11, "bold"), relief="flat", borderwidth=0)
        style.map("Treeview", background=[("selected", "#2a3f6e")],
                  foreground=[("selected", TEXT_MAIN)])
        style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        tree_container = ctk.CTkFrame(table_frame, fg_color="transparent")
        tree_container.grid(row=1, column=0, sticky="nsew", padx=12, pady=8)
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_container, columns=cols, show="headings", selectmode="browse")
        for col, w in zip(cols, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, minwidth=w, anchor="center")
        self.tree.column("Name", anchor="w")

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.tag_configure("low", foreground=WARN)
        self.tree.tag_configure("ok",  foreground=ACCENT2)

        # Action buttons
        btn_row = ctk.CTkFrame(table_frame, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", padx=12, pady=(4, 12))

        ctk.CTkButton(btn_row, text="✏️  Edit", width=110, height=34, corner_radius=8,
                      fg_color=BG_INPUT, hover_color=BORDER, text_color=TEXT_MAIN,
                      command=self._open_edit).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_row, text="🗑️  Delete", width=110, height=34, corner_radius=8,
                      fg_color=BG_INPUT, hover_color=DANGER, text_color=TEXT_MAIN,
                      command=self._delete_product).pack(side="left")

        self.count_label = ctk.CTkLabel(btn_row, text="", font=ctk.CTkFont("Helvetica", 11),
                                        text_color=TEXT_DIM)
        self.count_label.pack(side="right")

    def _load_products(self):
        query = self.search_var.get().strip()
        products = search_products(query) if query else get_all_products()
        self.tree.delete(*self.tree.get_children())
        for p in products:
            status = "⚠️ Low" if p["quantity"] <= p["min_stock"] else "✅ OK"
            tag = "low" if p["quantity"] <= p["min_stock"] else "ok"
            self.tree.insert("", "end", iid=str(p["id"]), tags=(tag,),
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

    def _open_add(self):
        ProductForm(self, None, self._load_products)

    def _open_edit(self):
        pid = self._get_selected_id()
        if pid:
            ProductForm(self, pid, self._load_products)

    def _delete_product(self):
        pid = self._get_selected_id()
        if pid:
            name = self.tree.item(str(pid))["values"][1]
            if messagebox.askyesno("Confirm Delete",
                                   f"Delete '{name}'?\nThis cannot be undone.", icon="warning"):
                delete_product(pid)
                self._load_products()


# ══════════════════════════════════════════════════════════════════════════════
#  PRODUCT FORM (Add / Edit)
# ══════════════════════════════════════════════════════════════════════════════
class ProductForm(ctk.CTkToplevel):
    def __init__(self, parent, product_id, on_save):
        super().__init__(parent)
        self.product_id = product_id
        self.on_save = on_save
        self.title("Edit Product" if product_id else "Add Product")
        self.geometry("480x520")
        self.resizable(False, False)
        self.configure(fg_color=BG_MAIN)
        self.grab_set()
        self._build()
        if product_id:
            self._populate()

    def _field(self, parent, label, row, placeholder=""):
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont("Helvetica", 12),
                     text_color=TEXT_DIM).grid(row=row*2, column=0, sticky="w", pady=(10, 2))
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, height=38,
                             fg_color=BG_INPUT, border_color=BORDER,
                             text_color=TEXT_MAIN, font=ctk.CTkFont("Helvetica", 13))
        entry.grid(row=row*2+1, column=0, sticky="ew")
        return entry

    def _build(self):
        self.grid_columnconfigure(0, weight=1)

        title = "Edit Product" if self.product_id else "Add New Product"
        ctk.CTkLabel(self, text=title, font=ctk.CTkFont("Helvetica", 20, "bold"),
                     text_color=TEXT_MAIN).grid(row=0, column=0, sticky="w", padx=28, pady=(24, 4))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.grid(row=1, column=0, sticky="nsew", padx=28, pady=8)
        form.grid_columnconfigure(0, weight=1)

        self.e_name     = self._field(form, "Product Name",  0, "e.g. Apple iPhone 15")
        self.e_category = self._field(form, "Category",      1, "e.g. Electronics")
        self.e_price    = self._field(form, "Price (₱)",     2, "e.g. 55000")
        self.e_qty      = self._field(form, "Quantity",      3, "e.g. 10")
        self.e_min      = self._field(form, "Min Stock Alert", 4, "e.g. 5")

        ctk.CTkLabel(form, text="Description (optional)", font=ctk.CTkFont("Helvetica", 12),
                     text_color=TEXT_DIM).grid(row=10, column=0, sticky="w", pady=(10, 2))
        self.e_desc = ctk.CTkTextbox(form, height=60, fg_color=BG_INPUT, border_color=BORDER,
                                     text_color=TEXT_MAIN, font=ctk.CTkFont("Helvetica", 12))
        self.e_desc.grid(row=11, column=0, sticky="ew")

        # Buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", padx=28, pady=20)
        btn_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_row, text="Cancel", fg_color=BG_INPUT, hover_color=BORDER,
                      text_color=TEXT_MAIN, height=40, corner_radius=10,
                      command=self.destroy).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(btn_row, text="Save Product", fg_color=ACCENT, hover_color="#3a7be0",
                      height=40, corner_radius=10,
                      command=self._save).grid(row=0, column=1, sticky="ew")

    def _populate(self):
        from database import get_product_by_id
        p = get_product_by_id(self.product_id)
        if not p: return
        self.e_name.insert(0, p["name"])
        self.e_category.insert(0, p["category"])
        self.e_price.insert(0, str(p["price"]))
        self.e_qty.insert(0, str(p["quantity"]))
        self.e_min.insert(0, str(p["min_stock"]))
        if p["description"]:
            self.e_desc.insert("1.0", p["description"])

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
            price = float(price_s)
            qty   = int(qty_s)
            min_s = int(min_s)
        except ValueError:
            messagebox.showerror("Invalid Input", "Price must be a number. Quantity and Min Stock must be whole numbers.")
            return

        if self.product_id:
            update_product(self.product_id, name, category, price, qty, min_s, desc)
        else:
            add_product(name, category, price, qty, min_s, desc)

        self.on_save()
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  LOW STOCK PAGE
# ══════════════════════════════════════════════════════════════════════════════
class LowStockPage(ctk.CTkFrame):
    def __init__(self, parent, navigate):
        super().__init__(parent, fg_color="transparent")
        self.navigate = navigate
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        ctk.CTkLabel(hdr, text="⚠️  Low Stock Alerts",
                     font=ctk.CTkFont("Helvetica", 26, "bold"), text_color=WARN).pack(anchor="w")
        ctk.CTkLabel(hdr, text="Products at or below their minimum stock level.",
                     font=ctk.CTkFont("Helvetica", 13), text_color=TEXT_DIM).pack(anchor="w")

        scroll = ctk.CTkScrollableFrame(self, fg_color=BG_CARD, corner_radius=14)
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        products = get_low_stock_products()
        if not products:
            ctk.CTkLabel(scroll, text="🎉  All products are well-stocked!",
                         font=ctk.CTkFont("Helvetica", 16), text_color=ACCENT2).pack(pady=40)
            return

        for p in products:
            card = ctk.CTkFrame(scroll, fg_color=BG_INPUT, corner_radius=10)
            card.pack(fill="x", padx=12, pady=5)
            card.grid_columnconfigure(1, weight=1)

            # Warning badge
            badge = ctk.CTkFrame(card, fg_color=DANGER, corner_radius=8, width=60, height=60)
            badge.grid(row=0, column=0, padx=14, pady=12, rowspan=2)
            badge.grid_propagate(False)
            ctk.CTkLabel(badge, text=str(p["quantity"]),
                         font=ctk.CTkFont("Helvetica", 20, "bold"),
                         text_color="white").place(relx=0.5, rely=0.4, anchor="center")
            ctk.CTkLabel(badge, text="left",
                         font=ctk.CTkFont("Helvetica", 9),
                         text_color="white").place(relx=0.5, rely=0.75, anchor="center")

            ctk.CTkLabel(card, text=p["name"],
                         font=ctk.CTkFont("Helvetica", 14, "bold"),
                         text_color=TEXT_MAIN).grid(row=0, column=1, sticky="w", padx=8, pady=(12, 2))
            ctk.CTkLabel(card, text=f"{p['category']}  •  Min: {p['min_stock']}  •  ₱{p['price']:,.2f}",
                         font=ctk.CTkFont("Helvetica", 11), text_color=TEXT_DIM).grid(
                             row=1, column=1, sticky="w", padx=8, pady=(0, 12))


# ══════════════════════════════════════════════════════════════════════════════
#  ACTIVITY LOG PAGE
# ══════════════════════════════════════════════════════════════════════════════
class ActivityPage(ctk.CTkFrame):
    def __init__(self, parent, navigate):
        super().__init__(parent, fg_color="transparent")
        self.navigate = navigate
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        ctk.CTkLabel(hdr, text="Activity Log",
                     font=ctk.CTkFont("Helvetica", 26, "bold"), text_color=TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(hdr, text="A full history of all changes made to the inventory.",
                     font=ctk.CTkFont("Helvetica", 13), text_color=TEXT_DIM).pack(anchor="w")

        scroll = ctk.CTkScrollableFrame(self, fg_color=BG_CARD, corner_radius=14)
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        logs = get_recent_activity(100)
        if not logs:
            ctk.CTkLabel(scroll, text="No activity recorded yet.",
                         font=ctk.CTkFont("Helvetica", 14), text_color=TEXT_DIM).pack(pady=40)
            return

        colors = {"ADD": ACCENT2, "EDIT": ACCENT, "DELETE": DANGER}
        icons  = {"ADD": "＋", "EDIT": "✎", "DELETE": "✕"}

        for log in logs:
            row = ctk.CTkFrame(scroll, fg_color=BG_INPUT, corner_radius=8)
            row.pack(fill="x", padx=12, pady=3)
            row.grid_columnconfigure(1, weight=1)

            color = colors.get(log["action"], TEXT_DIM)
            icon  = icons.get(log["action"], "•")

            badge = ctk.CTkFrame(row, fg_color=color, corner_radius=6, width=32, height=32)
            badge.grid(row=0, column=0, padx=12, pady=10)
            badge.grid_propagate(False)
            ctk.CTkLabel(badge, text=icon, font=ctk.CTkFont("Helvetica", 14, "bold"),
                         text_color="white").place(relx=0.5, rely=0.5, anchor="center")

            ctk.CTkLabel(row, text=log["details"],
                         font=ctk.CTkFont("Helvetica", 12), text_color=TEXT_MAIN).grid(
                             row=0, column=1, sticky="w", padx=8)
            ctk.CTkLabel(row, text=log["timestamp"][:16],
                         font=ctk.CTkFont("Helvetica", 10), text_color=TEXT_DIM).grid(
                             row=0, column=2, padx=12)


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()