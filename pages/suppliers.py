import customtkinter as ctk
from tkinter import messagebox, ttk
from theme import *
from database import get_all_suppliers, add_supplier, update_supplier, delete_supplier, get_supplier_by_id


class SuppliersPage(ctk.CTkFrame):
    def __init__(self, parent, navigate, current_user):
        super().__init__(parent, fg_color="transparent")
        self.navigate = navigate
        self.current_user = current_user
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build()
        self._load()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hdr, text="Suppliers", font=FONT_TITLE(),
                     text_color=TEXT_MAIN).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(hdr, text="Manage your equipment suppliers and vendors.",
                     font=FONT_BODY(), text_color=TEXT_DIM).grid(row=1, column=0, sticky="w")
        ctk.CTkButton(hdr, text="＋  Add Supplier", font=FONT_BODY(),
                      fg_color=ACCENT, hover_color="#3a7be0", height=38, corner_radius=10,
                      command=self._open_add).grid(row=0, column=1, rowspan=2)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color=BG_CARD, corner_radius=14)
        self.scroll.grid(row=1, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

    def _load(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        suppliers = get_all_suppliers()
        if not suppliers:
            ctk.CTkLabel(self.scroll, text="No suppliers yet. Add one to get started.",
                         font=FONT_BODY(), text_color=TEXT_DIM).pack(pady=40)
            return
        for s in suppliers:
            self._supplier_card(s)

    def _supplier_card(self, s):
        card = ctk.CTkFrame(self.scroll, fg_color=BG_INPUT, corner_radius=12)
        card.pack(fill="x", padx=12, pady=5)
        card.grid_columnconfigure(1, weight=1)

        # Icon
        icon_bg = ctk.CTkFrame(card, fg_color=ACCENT, corner_radius=10, width=48, height=48)
        icon_bg.grid(row=0, column=0, rowspan=2, padx=14, pady=12)
        icon_bg.grid_propagate(False)
        ctk.CTkLabel(icon_bg, text="🏭", font=("Segoe UI Emoji", 20)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text=s["name"], font=FONT_BOLD(14),
                     text_color=TEXT_MAIN).grid(row=0, column=1, sticky="w", padx=4, pady=(12, 2))

        info_parts = []
        if s["contact"]: info_parts.append(f"👤 {s['contact']}")
        if s["phone"]:   info_parts.append(f"📞 {s['phone']}")
        if s["email"]:   info_parts.append(f"✉️ {s['email']}")
        if s["address"]: info_parts.append(f"📍 {s['address']}")
        info_text = "   •   ".join(info_parts) if info_parts else "No contact info"
        ctk.CTkLabel(card, text=info_text, font=FONT_SMALL(),
                     text_color=TEXT_DIM).grid(row=1, column=1, sticky="w", padx=4, pady=(0, 12))

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=0, column=2, rowspan=2, padx=(0, 12))
        ctk.CTkButton(btn_frame, text="✏️ Edit", width=80, height=30, corner_radius=6,
                      fg_color=BG_CARD, hover_color=BORDER, text_color=TEXT_DIM,
                      font=FONT_SMALL(),
                      command=lambda sid=s["id"]: self._open_edit(sid)).pack(pady=(0, 4))
        ctk.CTkButton(btn_frame, text="🗑️ Delete", width=80, height=30, corner_radius=6,
                      fg_color=BG_CARD, hover_color=DANGER, text_color=TEXT_DIM,
                      font=FONT_SMALL(),
                      command=lambda sid=s["id"], sname=s["name"]: self._delete(sid, sname)).pack()

    def _open_add(self):
        SupplierForm(self, None, self._load)

    def _open_edit(self, sup_id):
        SupplierForm(self, sup_id, self._load)

    def _delete(self, sup_id, name):
        if messagebox.askyesno("Confirm", f"Delete supplier '{name}'?"):
            delete_supplier(sup_id)
            self._load()


class SupplierForm(ctk.CTkToplevel):
    def __init__(self, parent, sup_id, on_save):
        super().__init__(parent)
        self.sup_id  = sup_id
        self.on_save = on_save
        self.title("Edit Supplier" if sup_id else "Add Supplier")
        self.geometry("460x440")
        self.resizable(False, False)
        self.configure(fg_color=BG_MAIN)
        self.grab_set()
        self._build()
        if sup_id:
            self._populate()

    def _field(self, parent, label, row, placeholder=""):
        ctk.CTkLabel(parent, text=label, font=FONT_SMALL(), text_color=TEXT_DIM).grid(
            row=row*2, column=0, sticky="w", pady=(10, 2))
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, height=36,
                             fg_color=BG_INPUT, border_color=BORDER,
                             text_color=TEXT_MAIN, font=FONT_BODY())
        entry.grid(row=row*2+1, column=0, sticky="ew")
        return entry

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text="Edit Supplier" if self.sup_id else "Add Supplier",
                     font=FONT_BOLD(18), text_color=TEXT_MAIN).grid(
                         row=0, column=0, sticky="w", padx=28, pady=(22, 4))
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.grid(row=1, column=0, sticky="nsew", padx=28)
        form.grid_columnconfigure(0, weight=1)

        self.e_name    = self._field(form, "Supplier Name *", 0, "e.g. Dell Philippines")
        self.e_contact = self._field(form, "Contact Person",  1, "e.g. Juan dela Cruz")
        self.e_phone   = self._field(form, "Phone",           2, "e.g. 09XX XXX XXXX")
        self.e_email   = self._field(form, "Email",           3, "e.g. sales@supplier.com")
        self.e_address = self._field(form, "Address",         4, "e.g. Makati City")

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", padx=28, pady=18)
        btn_row.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(btn_row, text="Cancel", fg_color=BG_INPUT, hover_color=BORDER,
                      text_color=TEXT_MAIN, height=40, corner_radius=10,
                      command=self.destroy).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(btn_row, text="Save Supplier", fg_color=ACCENT, hover_color="#3a7be0",
                      height=40, corner_radius=10, command=self._save).grid(row=0, column=1, sticky="ew")

    def _populate(self):
        s = get_supplier_by_id(self.sup_id)
        if not s: return
        self.e_name.insert(0, s["name"])
        if s["contact"]: self.e_contact.insert(0, s["contact"])
        if s["phone"]:   self.e_phone.insert(0, s["phone"])
        if s["email"]:   self.e_email.insert(0, s["email"])
        if s["address"]: self.e_address.insert(0, s["address"])

    def _save(self):
        name = self.e_name.get().strip()
        if not name:
            messagebox.showerror("Missing", "Supplier name is required.")
            return
        contact = self.e_contact.get().strip()
        phone   = self.e_phone.get().strip()
        email   = self.e_email.get().strip()
        address = self.e_address.get().strip()
        if self.sup_id:
            update_supplier(self.sup_id, name, contact, email, phone, address)
        else:
            add_supplier(name, contact, email, phone, address)
        self.on_save()
        self.destroy()