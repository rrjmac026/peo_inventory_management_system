import customtkinter as ctk
from tkinter import messagebox, ttk
from theme import *
from database import (
    get_all_assets, search_assets, add_asset, update_asset,
    delete_asset, get_asset_by_id, get_all_categories,
    get_all_suppliers, get_category_names, get_supplier_names,
    log_action
)


class AssetsPage(ctk.CTkFrame):
    def __init__(self, parent, navigate, current_user):
        super().__init__(parent, fg_color="transparent")
        self.navigate = navigate
        self.current_user = current_user
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._category_map = {}   # name → id
        self._build()
        self._load_assets()

    # ── Build ──────────────────────────────────────────────────────────────────
    def _build(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hdr, text="Assets", font=FONT_TITLE(),
                     text_color=TEXT_MAIN).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(hdr, text="＋  Add Asset", font=FONT_BODY(),
                      fg_color=ACCENT, hover_color="#3a7be0", height=38,
                      corner_radius=10, command=self._open_add).grid(row=0, column=1)

        # Search + filter bar
        bar = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=10, height=48)
        bar.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        bar.grid_columnconfigure(1, weight=1)
        bar.grid_propagate(False)

        ctk.CTkLabel(bar, text="🔍", font=("Segoe UI Emoji", 16)).grid(row=0, column=0, padx=(12, 4))
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._load_assets())
        ctk.CTkEntry(bar, textvariable=self.search_var,
                     placeholder_text="Search by name, serial no, location...",
                     fg_color="transparent", border_width=0,
                     font=FONT_BODY(), text_color=TEXT_MAIN).grid(row=0, column=1, sticky="ew", padx=4)

        self.cat_filter = ctk.CTkOptionMenu(
            bar, values=["All Categories"], width=160, height=32,
            fg_color=BG_INPUT, button_color=BG_INPUT, button_hover_color=BORDER,
            text_color=TEXT_MAIN, font=FONT_SMALL(),
            command=lambda _: self._load_assets())
        self.cat_filter.grid(row=0, column=2, padx=(0, 12))
        self._refresh_category_filter()

        # Table
        table_frame = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=14)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.grid_rowconfigure(1, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=BG_CARD, fieldbackground=BG_CARD,
                        foreground=TEXT_MAIN, rowheight=36, font=("Helvetica", 11), borderwidth=0)
        style.configure("Treeview.Heading", background=BG_INPUT, foreground=TEXT_DIM,
                        font=("Helvetica", 10, "bold"), relief="flat", borderwidth=0)
        style.map("Treeview", background=[("selected", "#2a3f6e")],
                  foreground=[("selected", TEXT_MAIN)])
        style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        cols   = ("ID", "Name", "Category", "Supplier", "Qty", "Min", "Value", "Condition", "Location", "Status")
        widths = (40,   200,    120,         120,        50,    50,    90,      90,           110,        80)

        container = ctk.CTkFrame(table_frame, fg_color="transparent")
        container.grid(row=1, column=0, sticky="nsew", padx=10, pady=8)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(container, columns=cols, show="headings", selectmode="browse")
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, minwidth=w, anchor="center")
        self.tree.column("Name", anchor="w")
        self.tree.tag_configure("low", foreground=WARN)
        self.tree.tag_configure("ok",  foreground=ACCENT2)
        self.tree.bind("<Double-1>", lambda e: self._open_edit())

        sb = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")

        # Action buttons
        btn_row = ctk.CTkFrame(table_frame, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", padx=12, pady=(4, 12))
        ctk.CTkButton(btn_row, text="✏️  Edit", width=100, height=32, corner_radius=8,
                      fg_color=BG_INPUT, hover_color=BORDER, text_color=TEXT_MAIN,
                      command=self._open_edit).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_row, text="🗑️  Delete", width=100, height=32, corner_radius=8,
                      fg_color=BG_INPUT, hover_color=DANGER, text_color=TEXT_MAIN,
                      command=self._delete).pack(side="left")
        self.count_lbl = ctk.CTkLabel(btn_row, text="", font=FONT_SMALL(), text_color=TEXT_DIM)
        self.count_lbl.pack(side="right")

    # ── Data ───────────────────────────────────────────────────────────────────
    def _refresh_category_filter(self):
        cats = get_all_categories()
        self._category_map = {c["name"]: c["id"] for c in cats}
        values = ["All Categories"] + [c["name"] for c in cats]
        self.cat_filter.configure(values=values)

    def _load_assets(self):
        query  = self.search_var.get().strip()
        cat_sel = self.cat_filter.get()
        cat_id  = self._category_map.get(cat_sel) if cat_sel != "All Categories" else None
        assets  = search_assets(query, cat_id)
        self.tree.delete(*self.tree.get_children())
        for a in assets:
            low    = a["quantity"] <= a["min_stock"]
            status = "⚠️ Low" if low else "✅ OK"
            self.tree.insert("", "end", iid=str(a["id"]), tags=("low" if low else "ok",),
                             values=(a["id"], a["name"],
                                     a["category_name"] or "—",
                                     a["supplier_name"] or "—",
                                     a["quantity"], a["min_stock"],
                                     f"₱{a['unit_value']:,.2f}",
                                     a["condition"], a["location"] or "—", status))
        self.count_lbl.configure(text=f"{len(assets)} asset(s)")

    def _get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an asset first.")
            return None
        return int(sel[0])

    def _open_add(self):
        AssetForm(self, None, self.current_user, self._on_saved)

    def _open_edit(self):
        aid = self._get_selected_id()
        if aid:
            AssetForm(self, aid, self.current_user, self._on_saved)

    def _delete(self):
        aid = self._get_selected_id()
        if not aid: return
        name = self.tree.item(str(aid))["values"][1]
        if messagebox.askyesno("Confirm Delete", f"Delete asset '{name}'?\nThis cannot be undone.", icon="warning"):
            delete_asset(aid, user=self.current_user["username"])
            self._on_saved()

    def _on_saved(self):
        self._refresh_category_filter()
        self._load_assets()


# ── Asset Form ─────────────────────────────────────────────────────────────────
class AssetForm(ctk.CTkToplevel):
    CONDITIONS = ["Good", "Fair", "Poor", "Under Repair", "Disposed"]

    def __init__(self, parent, asset_id, current_user, on_save):
        super().__init__(parent)
        self.asset_id    = asset_id
        self.current_user = current_user
        self.on_save     = on_save
        self.title("Edit Asset" if asset_id else "Add Asset")
        self.geometry("560x680")
        self.resizable(False, False)
        self.configure(fg_color=BG_MAIN)
        self.grab_set()
        self._build()
        if asset_id:
            self._populate()

    def _field(self, parent, label, row, col=0, placeholder="", colspan=1):
        ctk.CTkLabel(parent, text=label, font=FONT_SMALL(), text_color=TEXT_DIM).grid(
            row=row*2, column=col, columnspan=colspan, sticky="w", pady=(10, 2))
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, height=36,
                             fg_color=BG_INPUT, border_color=BORDER,
                             text_color=TEXT_MAIN, font=FONT_BODY())
        entry.grid(row=row*2+1, column=col, columnspan=colspan, sticky="ew")
        return entry

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text="Edit Asset" if self.asset_id else "Add New Asset",
                     font=FONT_BOLD(18), text_color=TEXT_MAIN).grid(
                         row=0, column=0, sticky="w", padx=28, pady=(22, 4))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.grid(row=1, column=0, sticky="nsew", padx=28, pady=4)
        form.grid_columnconfigure((0, 1), weight=1)

        # Row 0 — Name (full width)
        ctk.CTkLabel(form, text="Asset Name *", font=FONT_SMALL(), text_color=TEXT_DIM).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(8, 2))
        self.e_name = ctk.CTkEntry(form, placeholder_text="e.g. Dell Laptop Pro 15",
                                   height=36, fg_color=BG_INPUT, border_color=BORDER,
                                   text_color=TEXT_MAIN, font=FONT_BODY())
        self.e_name.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Row 1 — Category & Supplier
        ctk.CTkLabel(form, text="Category", font=FONT_SMALL(), text_color=TEXT_DIM).grid(
            row=2, column=0, sticky="w", pady=(10, 2))
        cats = ["— None —"] + get_category_names()
        self.dd_cat = ctk.CTkOptionMenu(form, values=cats, height=36,
                                        fg_color=BG_INPUT, button_color=BG_INPUT,
                                        button_hover_color=BORDER, text_color=TEXT_MAIN,
                                        font=FONT_BODY())
        self.dd_cat.grid(row=3, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(form, text="Supplier", font=FONT_SMALL(), text_color=TEXT_DIM).grid(
            row=2, column=1, sticky="w", pady=(10, 2))
        sups = ["— None —"] + get_supplier_names()
        self.dd_sup = ctk.CTkOptionMenu(form, values=sups, height=36,
                                        fg_color=BG_INPUT, button_color=BG_INPUT,
                                        button_hover_color=BORDER, text_color=TEXT_MAIN,
                                        font=FONT_BODY())
        self.dd_sup.grid(row=3, column=1, sticky="ew", padx=(6, 0))

        # Row 2 — Qty, Min, Value
        ctk.CTkLabel(form, text="Quantity *", font=FONT_SMALL(), text_color=TEXT_DIM).grid(
            row=4, column=0, sticky="w", pady=(10, 2))
        self.e_qty = ctk.CTkEntry(form, placeholder_text="0", height=36,
                                  fg_color=BG_INPUT, border_color=BORDER,
                                  text_color=TEXT_MAIN, font=FONT_BODY())
        self.e_qty.grid(row=5, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(form, text="Min Stock *", font=FONT_SMALL(), text_color=TEXT_DIM).grid(
            row=4, column=1, sticky="w", pady=(10, 2))
        self.e_min = ctk.CTkEntry(form, placeholder_text="1", height=36,
                                  fg_color=BG_INPUT, border_color=BORDER,
                                  text_color=TEXT_MAIN, font=FONT_BODY())
        self.e_min.grid(row=5, column=1, sticky="ew", padx=(6, 0))

        ctk.CTkLabel(form, text="Unit Value (₱) *", font=FONT_SMALL(), text_color=TEXT_DIM).grid(
            row=6, column=0, sticky="w", pady=(10, 2))
        self.e_val = ctk.CTkEntry(form, placeholder_text="0.00", height=36,
                                  fg_color=BG_INPUT, border_color=BORDER,
                                  text_color=TEXT_MAIN, font=FONT_BODY())
        self.e_val.grid(row=7, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(form, text="Condition", font=FONT_SMALL(), text_color=TEXT_DIM).grid(
            row=6, column=1, sticky="w", pady=(10, 2))
        self.dd_cond = ctk.CTkOptionMenu(form, values=self.CONDITIONS, height=36,
                                         fg_color=BG_INPUT, button_color=BG_INPUT,
                                         button_hover_color=BORDER, text_color=TEXT_MAIN,
                                         font=FONT_BODY())
        self.dd_cond.grid(row=7, column=1, sticky="ew", padx=(6, 0))

        # Row 3 — Location, Serial No
        ctk.CTkLabel(form, text="Location", font=FONT_SMALL(), text_color=TEXT_DIM).grid(
            row=8, column=0, sticky="w", pady=(10, 2))
        self.e_loc = ctk.CTkEntry(form, placeholder_text="e.g. Room 201", height=36,
                                  fg_color=BG_INPUT, border_color=BORDER,
                                  text_color=TEXT_MAIN, font=FONT_BODY())
        self.e_loc.grid(row=9, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(form, text="Serial No.", font=FONT_SMALL(), text_color=TEXT_DIM).grid(
            row=8, column=1, sticky="w", pady=(10, 2))
        self.e_serial = ctk.CTkEntry(form, placeholder_text="e.g. SN-12345", height=36,
                                     fg_color=BG_INPUT, border_color=BORDER,
                                     text_color=TEXT_MAIN, font=FONT_BODY())
        self.e_serial.grid(row=9, column=1, sticky="ew", padx=(6, 0))

        # Description
        ctk.CTkLabel(form, text="Description", font=FONT_SMALL(), text_color=TEXT_DIM).grid(
            row=10, column=0, columnspan=2, sticky="w", pady=(10, 2))
        self.e_desc = ctk.CTkTextbox(form, height=56, fg_color=BG_INPUT, border_color=BORDER,
                                     text_color=TEXT_MAIN, font=FONT_BODY())
        self.e_desc.grid(row=11, column=0, columnspan=2, sticky="ew")

        # Buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", padx=28, pady=18)
        btn_row.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(btn_row, text="Cancel", fg_color=BG_INPUT, hover_color=BORDER,
                      text_color=TEXT_MAIN, height=40, corner_radius=10,
                      command=self.destroy).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(btn_row, text="Save Asset", fg_color=ACCENT, hover_color="#3a7be0",
                      height=40, corner_radius=10, command=self._save).grid(row=0, column=1, sticky="ew")

    def _populate(self):
        from database import get_all_categories, get_all_suppliers
        a = get_asset_by_id(self.asset_id)
        if not a: return
        self.e_name.insert(0, a["name"])
        self.e_qty.insert(0, str(a["quantity"]))
        self.e_min.insert(0, str(a["min_stock"]))
        self.e_val.insert(0, str(a["unit_value"]))
        self.dd_cond.set(a["condition"] or "Good")
        if a["location"]:   self.e_loc.insert(0, a["location"])
        if a["serial_no"]:  self.e_serial.insert(0, a["serial_no"])
        if a["description"]: self.e_desc.insert("1.0", a["description"])
        if a["category_name"]: self.dd_cat.set(a["category_name"])
        if a["supplier_name"]: self.dd_sup.set(a["supplier_name"])

    def _save(self):
        name  = self.e_name.get().strip()
        qty_s = self.e_qty.get().strip()
        min_s = self.e_min.get().strip()
        val_s = self.e_val.get().strip()
        if not all([name, qty_s, min_s, val_s]):
            messagebox.showerror("Missing Fields", "Name, Quantity, Min Stock and Unit Value are required.")
            return
        try:
            qty = int(qty_s); mn = int(min_s); val = float(val_s)
        except ValueError:
            messagebox.showerror("Invalid Input", "Quantity and Min Stock must be integers. Value must be a number.")
            return

        from database import get_all_categories, get_all_suppliers
        cats = {c["name"]: c["id"] for c in get_all_categories()}
        sups = {s["name"]: s["id"] for s in get_all_suppliers()}

        cat_sel = self.dd_cat.get()
        sup_sel = self.dd_sup.get()
        cat_id  = cats.get(cat_sel)
        sup_id  = sups.get(sup_sel)
        cond    = self.dd_cond.get()
        loc     = self.e_loc.get().strip()
        serial  = self.e_serial.get().strip()
        desc    = self.e_desc.get("1.0", "end").strip()
        user    = self.current_user["username"]

        if self.asset_id:
            update_asset(self.asset_id, name, cat_id, sup_id, qty, mn, val, cond, loc, serial, desc, user)
        else:
            add_asset(name, cat_id, sup_id, qty, mn, val, cond, loc, serial, desc, user)
        self.on_save()
        self.destroy()